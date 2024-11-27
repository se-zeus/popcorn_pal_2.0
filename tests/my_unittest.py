import unittest
import warnings
import sys
from datetime import datetime

sys.path.append("../")
from main import get_suggestions, convert_to_list, convert_to_list_num, app, get_similar_user_recommendations, hybrid_recommendation

warnings.filterwarnings("ignore")

class TestMain(unittest.TestCase):

    def test_get_suggestions(self):
        # Assuming get_suggestions now uses collaborative filtering
        suggestions = get_suggestions(user_id=10)  # Assuming this takes a user_id
        self.assertTrue(isinstance(suggestions, list))
        self.assertGreater(len(suggestions), 0, "No suggestions were returned.")

    def test_get_similar_user_recommendations(self):
        # Assuming get_similar_user_recommendations takes a user_id and returns movie recommendations based on similar users
        recommendations = get_similar_user_recommendations(user_id=10, top_n=5)
        
        self.assertTrue(isinstance(recommendations, list))
        self.assertGreater(len(recommendations), 0, "No recommendations were returned.")
        self.assertTrue(all(isinstance(rec, tuple) and len(rec) == 2 for rec in recommendations),
                        "Recommendations should be a list of tuples with (movie_id, score).")

    def test_hybrid_recommendation(self):
        # Assuming hybrid_recommendation combines content-based and user-based recommendations
        hybrid_recs = hybrid_recommendation(user_id=10, movie_id=1, top_n=5, alpha=0.7)
        
        self.assertTrue(isinstance(hybrid_recs, list))
        self.assertGreater(len(hybrid_recs), 0, "No hybrid recommendations were returned.")
        self.assertTrue(all(isinstance(rec, tuple) and len(rec) == 2 for rec in hybrid_recs),
                        "Hybrid recommendations should be a list of tuples with (movie_id, combined_score).")

    def test_convert_to_list(self):
        result = convert_to_list('["abc", "def"]')
        self.assertEqual(result, ["abc", "def"])
    
    def test_convert_to_list_num(self):
        result = convert_to_list_num("[1, 2, 3]")
        self.assertEqual(result, [1, 2, 3])

    def test_home_route(self):
        with app.test_client() as client:
            response = client.get("/home")
            self.assertEqual(response.status_code, 200)

    def test_recommend_route(self):
        with app.test_client() as client:
            response = client.post(
                "/recommend",
                data={
                    "title": "Test Movie",
                    "poster": "test_poster.jpg",
                    "overview": "Test overview",
                    "vote_average": "8.0",
                    "vote_count": "100",
                    "release_date": "2022-01-01",
                    "runtime": "120",
                    "status": "Released",
                    "genres": "Action, Adventure",
                    "rec_movies": '["Movie 1", "Movie 2"]',
                    "rec_posters": '["poster1.jpg", "poster2.jpg"]',
                    "rec_movies_org": '["Movie 1", "Movie 2"]',
                    "rec_year": "[2020, 2021]",
                    "rec_vote": "[8.5, 9.0]",
                    "rec_ids": "[1, 2]",
                },
            )
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
