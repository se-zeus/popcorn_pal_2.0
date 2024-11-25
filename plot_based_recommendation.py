import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load movie metadata
def get_data(movie_length):
    metadata = pd.read_csv("movies_metadata.csv", low_memory=False)
    return metadata[:movie_length]

# Calculate the cosine similarity matrix
def compute_tfidfmatrix(metadata):
    tfidf = TfidfVectorizer(stop_words="english")
    metadata["overview"] = metadata["overview"].fillna("")  # Replace NaN with empty strings
    tfidf_matrix = tfidf.fit_transform(metadata["overview"])
    cosine_similarity = linear_kernel(tfidf_matrix, tfidf_matrix)
    np.savez("cosine_similarity_5k.npz", matrix=cosine_similarity)

# Get movie recommendations based on similarity
def get_recommendations(title, indices, cosine_sim):
    if title not in indices:
        return None
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))  # Get similarity scores for all movies
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]  # Sort and take top 10
    movie_indices = [i[0] for i in sim_scores]
    return metadata["title"].iloc[movie_indices]

# Main program
if __name__ == "__main__":
    metadata = get_data(movie_length=5000)
    data = np.load("cosine_similarity_5k.npz", allow_pickle=True)
    cosine_similarity = data["matrix"]
    indices = pd.Series(metadata.index, index=metadata["title"]).drop_duplicates()

    movie = "Toy Story"  # Example movie title
    recommendations = get_recommendations(movie, indices, cosine_similarity)
    print("Recommendations for", movie, ":", recommendations)
