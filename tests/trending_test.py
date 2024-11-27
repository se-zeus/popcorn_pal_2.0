import unittest
from unittest.mock import patch
from flask import Flask
from flask import app, get_trending_movies  # Replace with the actual filename

class TestTrendingMovies(unittest.TestCase):

    @patch('app.requests.get')
    def test_get_trending_movies_success(self, mock_get):
        # Mock a successful API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'results': [{'title': 'Movie 1'}, {'title': 'Movie 2'}]
        }
        trending_movies = get_trending_movies()
        self.assertEqual(len(trending_movies), 2)
        self.assertEqual(trending_movies[0]['title'], 'Movie 1')

    @patch('app.requests.get')
    def test_get_trending_movies_error(self, mock_get):
        # Mock an API error
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        trending_movies = get_trending_movies()
        self.assertEqual(trending_movies, [])  # Should return an empty list

    def test_trending_route(self):
        with app.test_client() as client:
            # Mock the function
            with patch('app.get_trending_movies') as mock_get_trending_movies:
                mock_get_trending_movies.return_value = [
                    {'title': 'Mocked Movie 1'}, {'title': 'Mocked Movie 2'}
                ]

                response = client.get('/trending')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Mocked Movie 1', response.data)
                self.assertIn(b'Mocked Movie 2', response.data)

            # Test error scenario
            with patch('app.get_trending_movies') as mock_get_trending_movies:
                mock_get_trending_movies.return_value = []
                response = client.get('/trending')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Sorry, we couldn't fetch the trending movies.", response.data)

if __name__ == '__main__':
    unittest.main()
