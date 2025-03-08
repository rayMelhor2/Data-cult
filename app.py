from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')



EMBEDDINGS_FILE = 'movie_embeddings.npy'
DATA_FILE = 'dataset.csv'
MOVIES_PER_PAGE = 12



if os.path.exists(EMBEDDINGS_FILE):
    embeddings = np.load(EMBEDDINGS_FILE)
    df2 = pd.read_csv(DATA_FILE)
    df2.pop('Unnamed: 0')
else:
    df = pd.read_csv(DATA_FILE)
    for i in range(len(df['Description'])):
        time = df['Description'][i]
        time = re.sub(r'[^a-zA-Zа-яА-Я0-9]', ' ', str(time))
        time = time.lower()
        time = ' '.join(time.split())
        if time == 'false' or time == 'NaN':
            df.drop(i,inplace=True)
        else:
            df.at[i,'Description'] = time
            print(i, type(df['Description'][i]), time)
    df.pop('Unnamed: 0')
    df = df.drop_duplicates()
    df.to_csv(DATA_FILE)
    df2 = pd.read_csv(DATA_FILE)
    df2.pop('Unnamed: 0')
    descriptions = df2['Description'].tolist()
    embeddings = model.encode(descriptions)
    np.save(EMBEDDINGS_FILE, embeddings)

app = Flask(__name__, static_folder='static')



def search(query: str, top_k: int = 8) -> pd.DataFrame:
    qur = df2[df2['Name'].str.contains(str(query), case=False, na=False)]
    if not len(qur)!=0:
        result = pd.DataFrame()
    else:
        result = qur
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)
    top_indices = np.argsort(similarities[0])[::-1]
    b = df2.iloc[top_indices]
    results = pd.concat([result,b])
    return results.iloc[0:top_k]

def get_paginated_movies(page: int, per_page: int = MOVIES_PER_PAGE) -> pd.DataFrame:
    first_page_index = (page - 1) * per_page
    last_page_index = first_page_index + per_page
    return df2.iloc[first_page_index:last_page_index]

def clean_genre(genre: str) -> str:
    if isinstance(genre, str):
        genre = re.sub(r"[[\]'\"\s]", "", genre)
    return genre

@app.route('/', methods=['GET', 'POST'])
def main():
    search_query = request.form.get('search_input') if request.method == 'POST' else ''
    page = request.args.get('page', 1, type=int)

    if search_query:
        results = search(search_query)
    else:
        results = get_paginated_movies(page)

    items = [
        {
            'name': row['Name'],
            'description': row['Description'],
            'banner': row.get('photo', ''),
            'imdb_rating': row.get('IMDb rate', 'N/A'),
            'theme': row.get('Theme', 'N/A'),
            'age_rating': row.get('years old', 'N/A'),
            'published': row.get('Published', 'N/A'),
            'url': row.get('Url', '#')
        }
        for _, row in results.iterrows()
    ]

    total_pages = (len(df2) + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE

    return render_template('base.html', items=items, search_query=search_query, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=False)
