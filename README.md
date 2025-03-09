# Movie Recommendation System

A Flask-based movie recommendation system that leverages deep overview embeddings, similarity functions, and a local Llama 3.2 reasoning model to provide personalized movie suggestions with natural language explanations.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Examples](#examples)
- [File Structure](#file-structure)

## Introduction

This project is a complete movie recommendation system that:
- Loads and preprocesses movie data from a CSV file.
- Computes deep embeddings for movie overviews using the `SentenceTransformer`.
- Uses various similarity measures (e.g., cosine similarity, Jaccard similarity) to calculate how similar movies are.
- Generates natural language reasoning for recommendations with a local Llama 3.2 model using the Ollama library.
- Provides a user-friendly interface via a Flask web application with dynamic autocomplete and interactive movie cards.

## Features

- **Deep Overview Embeddings:** Compute or load precomputed embeddings for movie overviews.
- **Similarity Metrics:** Utilize multiple similarity functions, including binary franchise match, Jaccard similarity, and list overlap score.
- **Natural Language Reasoning:** Generate detailed reasoning for recommendations using the Llama 3.2 model.
- **Dynamic Styling:** Extract dominant colors from movie posters to style the recommendation cards dynamically.
- **Modular Codebase:** Well-organized code separated into different modules for maintainability.
- **Responsive UI:** A clean, responsive web interface with autocomplete suggestions and animated loading skeletons.

## Examples

![Results 1](assets/screencapture-127-0-0-1-5000-results-2025-03-09-10_33_10.png)
![Results 1](assets/screencapture-127-0-0-1-5000-results-2025-03-09-10_34_36.png)


## File Structure

```plaintext
project/
├── app.py                    # Main Flask application with route definitions
├── recommendation.py         # Recommendation logic and Llama 3.2 integration
├── utils.py                  # Helper functions (e.g., poster retrieval, color extraction)
├── templates/
│   ├── home.html             # Homepage with search functionality and autocomplete
│   └── results.html          # Results page to display target and recommended movies
├── static/
│   ├── css/
│   │   └── style.css         # (Optional) Custom styles (can be included in HTML files)
│   └── posters/
│       └── default.jpg       # Default movie poster image
├── data/
│   ├── 2.csv                 # Movie data CSV file
│   └── overview_embeddings.npy  # Saved overview embeddings (auto-generated)
└── requirements.txt          # List of Python dependencies
