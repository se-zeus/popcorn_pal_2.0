import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from . import app, get_smart_recommendations  

class TestRecommendations(unittest.TestCase):
    def test_get_smart_recommendations(self, mock_requests_get, mock_history_find):
        # Mock the user's viewing history from the database
        mock_history_find.return_value = [
            {'genre': 'Action,Adventure'},
            {'genre': 'Drama'}
        ]
        
        # Mock the API response for fetching movies by genre
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            'results': [
                {'title': 'Action Movie 1', 'poster_path': '/path1.jpg'},
                {'title': 'Drama Movie 1', 'poster_path': '/path2.jpg'}
            ]
        }
        
        # Call the function with a test user_id
        recommendations = get_smart_recommendations(user_id='test_user')
        
        # Assertions
        self.assertEqual(len(recommendations), 4)  # 2 genres x 2 movies each
        self.assertIn('Action Movie 1', [movie['title'] for movie in recommendations])
        self.assertIn('Drama Movie 1', [movie['title'] for movie in recommendations])
        self.assertTrue(all('poster' in movie for movie in recommendations))

    def test_recommendations_route(self):
        # Use Flask's test client to simulate a request
        with app.test_client() as client:
            # Mock the function to return a static list
            with patch('app.get_smart_recommendations') as mock_recommendations:
                mock_recommendations.return_value = [
                    {'title': 'Mocked Movie 1', 'poster': 'https://image.tmdb.org/t/path.jpg', 'genre': 'Action'},
                    {'title': 'Mocked Movie 2', 'poster': 'https://image.tmdb.org/t/path2.jpg', 'genre': 'Drama'}
                ]
                
                # Simulate GET request to the recommendations route
                response = client.get('/recommendations/test_user')
                
                # Assertions
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Mocked Movie 1', response.data)
                self.assertIn(b'Mocked Movie 2', response.data)

if __name__ == '__main__':
    unittest.main()
