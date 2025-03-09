from flask import Flask, render_template, request, jsonify
from recommendation import recommend_movies_by_title
from utils import get_poster, get_dominant_color
import pandas as pd

app = Flask(__name__)

# Load movie data (this can also be moved to a separate module if desired)
CSV_FILE = "data/2.csv"
df = pd.read_csv(CSV_FILE)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("query", "").lower()
    movies = df[["title", "poster_path"]].dropna(subset=["title"]).drop_duplicates().to_dict("records")
    suggestions = []
    if query:
        prefix_matches = [movie for movie in movies if movie["title"].lower().startswith(query)]
        non_prefix_matches = [movie for movie in movies if query in movie["title"].lower() and not movie["title"].lower().startswith(query)]
        suggestions = (prefix_matches + non_prefix_matches)[:5]
    return jsonify({"suggestions": suggestions})

@app.route("/recommend")
def recommend():
    movie_title = request.args.get("title", "")
    if not movie_title:
        return jsonify({"error": "Please provide a movie title."})
    try:
        recommendations, target_movie = recommend_movies_by_title(df, movie_title)
        # Process target movie
        target = {
            "title": target_movie["title"],
            "date": target_movie.get("release_date", ""),
            "genres": target_movie["genres"].split(", ") if pd.notna(target_movie["genres"]) else [],
            "cast": target_movie["cast"].split(", ")[:5] if pd.notna(target_movie["cast"]) else [],
            "crew": target_movie["crew"].split(", ")[:3] if pd.notna(target_movie["crew"]) else [],
            "overview": target_movie["overview"] if pd.notnull(target_movie["overview"]) else "No overview available.",
            "poster_path": get_poster(target_movie)
        }
        (target["bg_color"], target["text_color"], target["border_color"],
         target["pill_bg"], target["pill_bg_hover"], target["pill_text"]) = get_dominant_color(target["poster_path"])

        recs = []
        for rec in recommendations:
            rec_movie = rec[3]
            movie_info = {
                "title": rec_movie["title"],
                "date": rec_movie.get("release_date", ""),
                "genres": rec_movie["genres"].split(", ") if pd.notna(rec_movie["genres"]) else [],
                "cast": rec_movie["cast"].split(", ")[:5] if pd.notna(rec_movie["cast"]) else [],
                "crew": rec_movie["crew"].split(", ")[:3] if pd.notna(rec_movie["crew"]) else [],
                "overview": rec_movie["overview"] if pd.notnull(rec_movie["overview"]) else "No overview available.",
                "poster_path": get_poster(rec_movie),
                "reasoning": rec_movie.get("reasoning", "")
            }
            (movie_info["bg_color"], movie_info["text_color"], movie_info["border_color"],
             movie_info["pill_bg"], movie_info["pill_bg_hover"], movie_info["pill_text"]) = get_dominant_color(movie_info["poster_path"])
            recs.append(movie_info)
        
        result = {
            "target_movie": target,
            "recommendations": recs
        }
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An unexpected error occurred. Please try again later."})

@app.route("/results")
def results():
    return render_template("results.html")

if __name__ == "__main__":
    print("Starting Movie Recommendation Server...")
    app.run(debug=False, host='0.0.0.0', port=5000)
