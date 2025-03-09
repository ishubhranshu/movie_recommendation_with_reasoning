import os
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import ollama  # Local Ollama library for Llama 3.2 calls

# Global Configuration
K = 11
EMBEDDING_FILE = "data/overview_embeddings.npy"
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# Load or Compute Overview Embeddings
def load_overview_embeddings(df):
    if os.path.exists(EMBEDDING_FILE):
        print("Loading saved overview embeddings...")
        return np.load(EMBEDDING_FILE)
    else:
        print("Computing overview embeddings...")
        overview_texts = df["overview"].fillna("").tolist()
        embeddings = model.encode(overview_texts, convert_to_tensor=True).cpu().numpy()
        np.save(EMBEDDING_FILE, embeddings)
        print("Embeddings computed and saved.")
        return embeddings

# Similarity Functions
def binary_franchise_match(val1, val2):
    if pd.notnull(val1) and pd.notnull(val2) and val1.strip() and val2.strip() and val1.strip().lower() == val2.strip().lower():
        return 1
    return 0

def jaccard_similarity(str1, str2):
    set1 = set([x.strip().lower() for x in str(str1).split(",") if x.strip()])
    set2 = set([x.strip().lower() for x in str(str2).split(",") if x.strip()])
    if not set1 or not set2:
        return 0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def list_overlap_score(str1, str2):
    set1 = set([x.strip().lower() for x in str(str1).split(",") if x.strip()])
    set2 = set([x.strip().lower() for x in str(str2).split(",") if x.strip()])
    if not set1:
        return 0
    return len(set1.intersection(set2)) / len(set1)

def get_deep_overview_similarity(overview_embeddings, idx1, idx2):
    vec1 = overview_embeddings[idx1].reshape(1, -1)
    vec2 = overview_embeddings[idx2].reshape(1, -1)
    sim = cosine_similarity(vec1, vec2)
    return sim[0][0]

# Weights for similarity factors
weights = {
    "franchise": 0.15,
    "overview": 0.25,
    "genre": 0.20,
    "keywords": 0.15,
    "cast": 0.15,
    "crew": 0.10
}

# Llama 3.2 Reasoning Function
def llama_reasoning(prompt):
    messages = [{"role": "user", "content": prompt}]
    result = ollama.chat(model="llama3.2", messages=messages)
    return result["message"]["content"]

# Main Recommendation Function
def recommend_movies_by_title(df, movie_name, top_n=K):
    overview_embeddings = load_overview_embeddings(df)
    
    matches = df[df["title"].fillna("").str.lower() == movie_name.lower()]
    if matches.empty:
        matches = df[df["title"].fillna("").str.lower().str.contains(movie_name.lower())]
        if matches.empty:
            raise ValueError(f"Movie '{movie_name}' not found.")
    target_idx = matches.index[0]
    target_movie = df.iloc[target_idx]
    
    scores = []
    for idx, row in df.iterrows():
        if idx == target_idx:
            continue
        franchise_score = binary_franchise_match(target_movie.get("belongs_to_collection", ""), row.get("belongs_to_collection", ""))
        overview_score = get_deep_overview_similarity(overview_embeddings, target_idx, idx)
        genre_score = jaccard_similarity(target_movie.get("genres", ""), row.get("genres", ""))
        keywords_score = jaccard_similarity(target_movie.get("keywords", ""), row.get("keywords", ""))
        cast_score = list_overlap_score(target_movie.get("cast", ""), row.get("cast", ""))
        crew_score = list_overlap_score(target_movie.get("crew", ""), row.get("crew", ""))
        
        total_score = (
            weights["franchise"] * franchise_score +
            weights["overview"] * overview_score +
            weights["genre"] * genre_score +
            weights["keywords"] * keywords_score +
            weights["cast"] * cast_score +
            weights["crew"] * crew_score
        )
        scores.append((row["id"], row["title"], total_score, row))
    
    recommendations = sorted(scores, key=lambda x: x[2], reverse=True)[:top_n]

    # Optionally, add reasoning using Llama 3.2 for each recommended movie
    for rec in recommendations:
        rec_movie = rec[3]
        prompt = (
            f"Explain why '{rec_movie['title']}' is recommended for fans of '{target_movie['title']}'.\n"
            "Consider shared genre themes, storytelling, director influence, and character journeys.\n"
            "Keep your explanation under 200 words."
        )
        reasoning = llama_reasoning(prompt)
        rec_movie["reasoning"] = reasoning

    return recommendations, target_movie
