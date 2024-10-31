import unittest
import pandas as pd
import numpy as np
from recommender import MovieRecommender  # Assuming the class is saved in recommender.py

class TestMovieRecommender(unittest.TestCase):

    def setUp(self):
        # Create a small dataset for testing
        self.mock_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'title': ["Movie A", "Movie B", "Movie C", "Movie D", "Movie E"],
            'overview': ["This is an adventure movie", "A romantic movie about love",
                         "Action-packed and thrilling", "A science fiction epic",
                         "A journey through space and time"],
            'genres': ["Adventure", "Romance", "Action", "Sci-Fi", "Sci-Fi"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01", "2003-01-01", "2004-01-01"]
        })

        # Initialize the recommender with real data and model
        self.recommender = MovieRecommender(data_path="./data/tmdb_5000_movies_sample.csv")
        self.recommender.movies_df = self.mock_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()

    def test_init_loads_data_correctly(self):
        self.assertEqual(len(self.recommender.movies_df), 5)

    def test_generate_embeddings_if_needed_creates_embeddings(self):
        self.assertIn("embedding", self.recommender.movies_df.columns)
        self.assertEqual(len(self.recommender.movies_df["embedding"].iloc[0]), 384)  # Check embedding size

    def test_calculate_similarity_matrix_shape(self):
        self.assertEqual(self.recommender.cosine_sim.shape, (5, 5))

    def test_get_recommendations_by_id_valid_id(self):
        recommendations = self.recommender.get_recommendations_by_id(1, top_n=3)
        self.assertEqual(len(recommendations), 3)
        self.assertNotEqual(recommendations[0]['id'], 1)  # Ensure it's not recommending itself

    def test_get_recommendations_by_id_invalid_id(self):
        with self.assertRaises(IndexError):
            self.recommender.get_recommendations_by_id(999)

    def test_get_recommendations_by_title_valid_title(self):
        recommendations = self.recommender.get_recommendations("Movie A", top_n=3)
        self.assertEqual(len(recommendations), 3)

    def test_get_recommendations_by_title_invalid_title(self):
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations("Nonexistent Movie")

    def test_get_recommendations_by_title_case_insensitive(self):
        recommendations = self.recommender.get_recommendations("movie a", top_n=3)
        self.assertEqual(len(recommendations), 3)

    def test_top_n_larger_than_available_movies(self):
        recommendations = self.recommender.get_recommendations("Movie A", top_n=10)
        self.assertLessEqual(len(recommendations), len(self.mock_data) - 1)  # Minus 1 for the input movie itself

    def test_results_with_empty_overview(self):
        self.recommender.movies_df.loc[0, "overview"] = None
        self.recommender._generate_embeddings_if_needed()
        self.assertEqual(len(self.recommender.movies_df['embedding'].iloc[0]), 384)  # Embedding for empty should be valid


    def test_similarity_matrix_values(self):
        sim_score = self.recommender.cosine_sim[0, 1]  # Check similarity between two movies
        self.assertGreaterEqual(sim_score, 0)
        self.assertLessEqual(sim_score, 1)

    def test_similarity_matrix_values_exact(self):
        sim_score = self.recommender.cosine_sim[0, 1]  # Check similarity between two movies
        self.assertLessEqual(sim_score, 0.5)
        self.assertLessEqual(sim_score, 1)



    def test_all_movie_titles_returned_in_recommendations_B(self):
        recommendations = self.recommender.get_recommendations("Movie A", top_n=4)
        recommended_titles = [rec['title'] for rec in recommendations]
        self.assertIn("Movie B", recommended_titles)

    def test_all_movie_titles_returned_in_recommendations_C(self):
        recommendations = self.recommender.get_recommendations("Movie A", top_n=4)
        recommended_titles = [rec['title'] for rec in recommendations]
        self.assertIn("Movie C", recommended_titles)

    def test_single_movie_no_recommendation(self):
        single_movie_df = pd.DataFrame({
            'id': [1],
            'title': ["Single Movie"],
            'overview': ["A unique and stand-alone movie"],
            'genres': ["Drama"],
            'release_date': ["2020-01-01"]
        })
        self.recommender.movies_df = single_movie_df
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Single Movie", top_n=3)
        self.assertEqual(len(recommendations), 0)


    def test_load_data_handles_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            MovieRecommender(data_path="./data/nonexistent_file.csv")

    def test_generate_embeddings_for_non_string_overview(self):
        self.recommender.movies_df.loc[0, "overview"] = 12345
        self.recommender._generate_embeddings_if_needed()
        self.assertEqual(len(self.recommender.movies_df['embedding'].iloc[0]), 384)

    def test_top_n_is_zero_returns_empty(self):
        recommendations = self.recommender.get_recommendations("Movie A", top_n=0)
        self.assertEqual(len(recommendations), 0)

    def test_top_n_is_negative_returns_empty(self):
        recommendations = self.recommender.get_recommendations("Movie A", top_n=-1)
        self.assertEqual(len(recommendations), 0)

    def test_top_n_exceeds_number_of_movies(self):
        # Test top_n exceeding the number of available movies minus the input movie itself
        recommendations = self.recommender.get_recommendations("Movie A", top_n=10)
        self.assertEqual(len(recommendations), 4)  # Only 2 other movies in the dataset

    def test_nonexistent_movie_title_returns_error(self):
        # Test with a movie title that doesn't exist in the dataset
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations("Nonexistent Movie", top_n=5)

    def test_whitespace_in_movie_title_raises_error(self):
        # Test with extra whitespace around the movie title
        with self.assertRaises(ValueError) as context:
            self.recommender.get_recommendations("  Movie A  ", top_n=2)
        self.assertIn("Movie titled '  Movie A  ' not found in the dataset.", str(context.exception))

    def test_empty_string_movie_title_returns_error(self):
        # Test with an empty string for the movie title
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations("", top_n=5)
    def test_similarity_matrix_is_symmetric(self):
        for i in range(len(self.recommender.cosine_sim)):
            for j in range(i, len(self.recommender.cosine_sim)):
                self.assertEqual(self.recommender.cosine_sim[i, j], self.recommender.cosine_sim[j, i])

    def test_get_recommendations_top_n_with_all_same_titles(self):
        duplicate_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie A", "Movie A"],
            'overview': ["Overview A", "Overview B", "Overview C"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = duplicate_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_with_all_unique_titles(self):
        unique_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Unique A", "Unique B", "Unique C"],
            'overview': ["Overview A", "Overview B", "Overview C"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = unique_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Unique A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_similar_overviews(self):
        similar_overviews_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["Adventure movie", "Adventure film", "Adventure saga"],
            'genres': ["Adventure", "Adventure", "Adventure"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = similar_overviews_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_mixed_case_titles(self):
        mixed_case_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["movie a", "Movie A", "MOVIE A"],
            'overview': ["Overview A", "Overview B", "Overview C"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = mixed_case_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("movie a", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_duplicate_overviews(self):
        duplicate_overviews_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["Same overview", "Same overview", "Same overview"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = duplicate_overviews_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_mixed_genres(self):
        mixed_genres_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["Overview A", "Overview B", "Overview C"],
            'genres': ["Action", "Comedy", "Drama"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = mixed_genres_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_all_same_genre(self):
        same_genre_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["Overview A", "Overview B", "Overview C"],
            'genres': ["Action", "Action", "Action"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = same_genre_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_same_release_date(self):
        same_release_date_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["Overview A", "Overview B", "Overview C"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["2000-01-01", "2000-01-01", "2000-01-01"]
        })
        self.recommender.movies_df = same_release_date_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_different_release_dates(self):
        different_release_dates_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["Overview A", "Overview B", "Overview C"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["1999-01-01", "2000-01-01", "2001-01-01"]
        })
        self.recommender.movies_df = different_release_dates_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_with_blank_overview(self):
        blank_overview_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["", "Overview B", "Overview C"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = blank_overview_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_get_recommendations_with_numeric_overview(self):
        numeric_overview_data = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ["Movie A", "Movie B", "Movie C"],
            'overview': ["12345", "67890", "54321"],
            'genres': ["Genre A", "Genre B", "Genre C"],
            'release_date': ["2000-01-01", "2001-01-01", "2002-01-01"]
        })
        self.recommender.movies_df = numeric_overview_data
        self.recommender._generate_embeddings_if_needed()
        self.recommender.cosine_sim = self.recommender._calculate_similarity_matrix()
        recommendations = self.recommender.get_recommendations("Movie A", top_n=2)
        self.assertEqual(len(recommendations), 2)

if __name__ == '__main__':
    unittest.main()
