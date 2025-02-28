from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
EMBEDDINGS_FILE = "movie_embeddings.npy"
DATA_FILE = "dataset2.csv"

if os.path.exists(EMBEDDINGS_FILE):
    embeddings = np.load(EMBEDDINGS_FILE)
else:
    df = pd.read_csv(DATA_FILE)
    descriptions = df['Description'].tolist()
    embeddings = model.encode(descriptions)
    np.save(EMBEDDINGS_FILE, embeddings)

df = pd.read_csv('dataset2.csv')

app = Flask(__name__)

MOVIES_PER_PAGE = 8


def semantic_search(query: str, top_k: int = 8) -> pd.DataFrame:
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)
    top_indices = similarities.argsort()[0][-top_k:][::-1]
    return df.iloc[top_indices]


def get_paginated_movies(page: int, per_page: int = MOVIES_PER_PAGE) -> pd.DataFrame:
    start = (page - 1) * per_page
    end = start + per_page
    return df.iloc[start:end]


def get_total_pages(total_movies: int, per_page: int = MOVIES_PER_PAGE) -> int:
    return (total_movies + per_page - 1) // per_page


def get_recommended_movies(found_genres: list = None, exclude_indices: list = None, top_k: int = 4) -> pd.DataFrame:
    if found_genres:
        recommended_movies = df[df['Theme'].apply(lambda x: any(genre in x for genre in found_genres))]
        recommended_movies = recommended_movies[~recommended_movies.index.isin(exclude_indices)]
    else:
        recommended_movies = df.sample(n=top_k)

    if len(recommended_movies) > top_k:
        recommended_movies = recommended_movies.sample(n=top_k)

    return recommended_movies


def clean_genre(genre: str) -> str:
    if isinstance(genre, str):
        genre = re.sub(r"[[\]'\"\s]", "", genre)
    return genre


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        search_query = str(request.form.get('search_input'))
        print(f"Search query: {search_query}")

        results = semantic_search(search_query)
        print(f"Search results: {results}")

        items = []
        found_genres = []
        for _, row in results.iterrows():
            items.append({
                'name': row['Name'],
                'description': row['Description'],
                'banner': row.get('photo', ''),
                'imdb_rating': row.get('IMDb rate', 'N/A'),
                'theme': clean_genre(row.get('Theme', 'N/A')),
                'age_rating': row.get('years old', 'N/A'),
                'published': row.get('Published', 'N/A'),
                'url': row.get('Url', '#')
            })
            if row.get('Theme'):
                found_genres.extend(clean_genre(row['Theme']).split(','))

        found_genres = list(set(found_genres))

        recommended_movies = get_recommended_movies(found_genres, results.index.tolist())
    else:
        items = []
        recommended_movies = get_recommended_movies()

    recommended_items = []
    for _, row in recommended_movies.iterrows():
        recommended_items.append({
            'name': row['Name'],
            'description': row['Description'],
            'banner': row.get('photo', ''),
            'imdb_rating': row.get('IMDb rate', 'N/A'),
            'theme': clean_genre(row.get('Theme', 'N/A')),
            'age_rating': row.get('years old', 'N/A'),
            'published': row.get('Published', 'N/A'),
            'url': row.get('Url', '#')
        })

    page = request.args.get('page', 1, type=int)
    paginated_movies = get_paginated_movies(page)

    movies = []
    seen_movies = set()
    for _, row in paginated_movies.iterrows():
        movie_id = row['Name']
        if movie_id not in seen_movies:
            seen_movies.add(movie_id)
            movies.append({
                'name': row['Name'],
                'description': row['Description'],
                'banner': row.get('photo', ''),
                'imdb_rating': row.get('IMDb rate', 'N/A'),
                'theme': clean_genre(row.get('Theme', 'N/A')),
                'age_rating': row.get('years old', 'N/A'),
                'published': row.get('Published', 'N/A'),
                'url': row.get('Url', '#')
            })

    total_pages = get_total_pages(len(df))

    return render_template('base.html', items=items, recommended_items=recommended_items,
                           search_query=request.form.get('search_input', ''), movies=movies, page=page,
                           total_pages=total_pages)


@app.route('/like', methods=['POST'])
def like():
    data = request.get_json()
    movie_index = data.get('movie_index')
    genres = data.get('genres', [])
    exclude_indices = data.get('exclude_indices', [])

    liked_movie_genres = df.iloc[movie_index]['Theme']
    if isinstance(liked_movie_genres, str):
        liked_movie_genres = clean_genre(liked_movie_genres).split(',')
    else:
        liked_movie_genres = []

    genres.extend(liked_movie_genres)
    genres = list(set(genres))

    recommended_movies = get_recommended_movies(genres, exclude_indices)

    recommended_items = []
    for _, row in recommended_movies.iterrows():
        recommended_items.append({
            'name': row['Name'],
            'description': row['Description'],
            'banner': row.get('photo', ''),
            'imdb_rating': row.get('IMDb rate', 'N/A'),
            'theme': clean_genre(row.get('Theme', 'N/A')),
            'age_rating': row.get('years old', 'N/A'),
            'published': row.get('Published', 'N/A'),
            'url': row.get('Url', '#')
        })

    return jsonify(recommended_items)


if __name__ == '__main__':
    app.run(debug=False)