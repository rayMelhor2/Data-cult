import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

EMBEDDINGS_FILE = "movie_embeddings.npy"
DATA_FILE = "dataset2.csv"

if os.path.exists(EMBEDDINGS_FILE):

    embeddings = np.load(EMBEDDINGS_FILE)
else:
    # Если файла нет, вычисляем вектора и сохраняем их
    df = pd.read_csv(DATA_FILE)
    descriptions = df['Description'].tolist()
    embeddings = model.encode(descriptions)
    np.save(EMBEDDINGS_FILE, embeddings)
    descriptions = df['Description'].tolist()
    embeddings = model.encode(descriptions)
df = pd.read_csv('dataset.csv')

def semantic_search(query: str, top_k: int = 3) -> pd.DataFrame:
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)
    top_indices = similarities.argsort()[0][-top_k:][::-1]
    return df.iloc[top_indices]


if __name__ == "__main__":
    while True:
        query = input("Введите поисковый запрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break
        results = semantic_search(query)
        print(results[['Name', 'Description']])
        print("\n" + "="*50 + "\n")