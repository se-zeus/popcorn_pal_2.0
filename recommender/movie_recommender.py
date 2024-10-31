"""
Content-Based Movie Recommendation System using Sentence Transformer Embeddings
-------------------------------------------------------------------------------
This script uses sentence embeddings generated with a Sentence Transformer model to build a content-based movie recommendation system.
The recommendation is based on cosine similarity between movie overview embeddings.

Requirements:
    - pandas
    - sentence-transformers
    - torch
    - sklearn

Dataset:
    TMDB 5000 Movie Dataset (assumed to be in the same directory as 'tmdb_5000_movies.csv')
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json


class MovieRecommender:
    """
    A content-based movie recommender system that utilizes embeddings to find similar movies based on overviews.

    Attributes:
        data_path (str): Path to the movies dataset.
        model (SentenceTransformer): Pre-trained sentence transformer model for embeddings.
        movies_df (pd.DataFrame): DataFrame containing movie information.
        cosine_sim (np.ndarray): Cosine similarity matrix for movie embeddings.
    """

    def __init__(self, data_path="tmdb_5000_movies.csv", model_name="all-MiniLM-L6-v2"):
        """
        Initializes the MovieRecommender with specified dataset and model.

        Args:
            data_path (str): Path to the CSV file containing movie data.
            model_name (str): Sentence Transformer model name for embedding generation.
        """
        self.data_path = data_path
        self.embeddings_path = data_path.replace(".csv", "_embeddings.json")
        self.model = SentenceTransformer(model_name)
        self.movies_df = self._load_data()
        self._generate_embeddings_if_needed()
        self.cosine_sim = self._calculate_similarity_matrix()

    def _load_data(self):
        """
        Loads and preprocesses the movies dataset by filling NaN values in the 'overview' column.

        Returns:
            pd.DataFrame: DataFrame with preprocessed movie data.
        """
        movies_df = pd.read_csv(self.data_path)
        movies_df['overview'] = movies_df['overview'].fillna('')
        return movies_df

    def _generate_embeddings_if_needed(self):
        """
        Checks if embeddings exist in a JSON file; if not, computes embeddings for each movie overview.
        """
        if not self._load_embeddings_from_file():
            print("Generating embeddings for movie overviews...")
            self.movies_df['embedding'] = self.movies_df['overview'].apply(lambda x: self.model.encode(x).tolist())
            # Save embeddings to JSON file
            with open(self.embeddings_path, "w") as f:
                json.dump(self.movies_df['embedding'].tolist(), f)
        else:
            print("Embeddings successfully loaded from file.")

    def _load_embeddings_from_file(self):
        """
        Loads embeddings from a JSON file if it exists.

        Returns:
            bool: True if embeddings were loaded successfully, False otherwise.
        """
        try:
            with open(self.embeddings_path, "r") as f:
                embeddings = json.load(f)
            # Convert loaded embeddings to arrays
            self.movies_df['embedding'] = [np.array(embed) for embed in embeddings]
            return True
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return False

    def get_recommendations_by_id(self, movie_id, top_n=10):
        # Find the index of the movie by ID
        idx = self.movies_df.index[self.movies_df['id'] == int(movie_id)].tolist()[0]

        # Get similar movies based on the cosine similarity matrix
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]

        # Get movie details for recommendations
        movie_indices = [i[0] for i in sim_scores]
        return self.movies_df.loc[movie_indices, ['id', 'title', 'overview', 'genres', 'release_date']].to_dict(orient='records')

    def _calculate_similarity_matrix(self):
        """
        Calculates the cosine similarity matrix for all movie embeddings.

        Returns:
            np.ndarray: A square matrix containing cosine similarity scores.
        """
        embeddings_matrix = np.vstack(self.movies_df['embedding'].values)
        return cosine_similarity(embeddings_matrix, embeddings_matrix)

    def get_recommendations(self, title, top_n=10):
        """
        Recommends top N similar movies for a given movie title based on the cosine similarity.

        Args:
            title (str): The title of the movie to get recommendations for.
            top_n (int): The number of recommendations to return.

        Returns:
            list: List of dictionaries with detailed information for each recommended movie.
        """
        try:
            idx = self.movies_df[self.movies_df['title'].str.lower() == title.lower()].index[0]
        except IndexError:
            raise ValueError(f"Movie titled '{title}' not found in the dataset.")

        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]
        movie_indices = [i[0] for i in sim_scores]

        # Return detailed information for each recommended movie
        return self.movies_df.loc[movie_indices, ['id', 'title', 'overview', 'genres', 'release_date']].to_dict(orient='records')


if __name__ == "__main__":
    # Example usage
    recommender = MovieRecommender(data_path="/Users/buddarvx/Desktop/data/tmdb_5000_movies.csv")
    movie_title = "The Dark Knight"
    print(f"Top recommendations for '{movie_title}':")
    recommendations = recommender.get_recommendations(movie_title)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. ID: {rec['id']}, Title: {rec['title']}, Release Date: {rec['release_date']}")
        print(f"   Overview: {rec['overview']}")
        print(f"   Genres: {rec['genres']}")
        print()
