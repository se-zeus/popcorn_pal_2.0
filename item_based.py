import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)

# Load the data
ratings = pd.read_csv(project_dir + "/data/ratings.csv")
movies = pd.read_csv(project_dir + "/data/movies.csv")

# Function to compute user-based recommendations
def recommendForNewUser(user_rating):
    # Convert user ratings into a dataframe
    user = pd.DataFrame(user_rating)
    
    # Create a matrix where rows are users and columns are movies
    user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating')

    # Fill missing values with zeros (users who haven't rated a movie)
    user_movie_matrix = user_movie_matrix.fillna(0)

    # Calculate the cosine similarity between users
    user_similarity = cosine_similarity(user_movie_matrix)

    # Create a dataframe for user similarities
    user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)

    # For the new user, find the most similar users
    user_ratings = user_movie_matrix.loc[user_movie_matrix.index.isin(user['userId'])]
    
    similar_users = user_similarity_df[user_ratings.index[0]].sort_values(ascending=False)[1:11]  # Top 10 similar users
    
    # Get the movies rated highly by similar users that the new user has not yet rated
    similar_users_movies = ratings[ratings['userId'].isin(similar_users.index)]
    similar_users_movies = similar_users_movies[~similar_users_movies['movieId'].isin(user['movieId'])]

    # Sort movies based on the average rating of similar users
    recommendations = similar_users_movies.groupby('movieId')['rating'].mean().sort_values(ascending=False).head(10)
    
    # Get movie titles for the top recommended movie IDs
    recommended_movie_titles = movies[movies['movieId'].isin(recommendations.index)]['title']
    return recommended_movie_titles.tolist()
