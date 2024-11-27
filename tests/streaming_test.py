import unittest
from unittest.mock import patch
from flask import Flask
from your_flask_app import app, get_streaming_availability  # Replace with the actual filename

class TestMovieDetails(unittest.TestCase):


    def test_get_streaming_availability_success(self, mock_get):
        # Mock a successful response from TMDb API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'results': {
                'US': {
                    'flatrate': [
                        {'provider_name': 'Netflix'},
                        {'provider_name': 'Hulu'}
                    ]
                }
            }
        }
        
        result = get_streaming_availability(movie_id=12345)
        self.assertIn('results', result)
        self.assertEqual(result['results']['US']['flatrate'][0]['provider_name'], 'Netflix')

    def test_get_streaming_availability_failure(self, mock_get):
        # Mock an API failure (non-200 response)
        mock_get.return_value.status_code = 500
        result = get_streaming_availability(movie_id=12345)
        self.assertEqual(result, {})  # Should return an empty dictionary

    def test_movie_details_route(self):
        with app.test_client() as client:
            # Mock the get_streaming_availability function
            with patch('your_flask_app.get_streaming_availability') as mock_get_streaming_availability:
                mock_get_streaming_availability.return_value = {
                    'results': {
                        'US': {
                            'flatrate': [
                                {'provider_name': 'Netflix', 'logo_path': '/netflix_logo.png'},
                                {'provider_name': 'Hulu', 'logo_path': '/hulu_logo.png'}
                            ]
                        }
                    }
                }

                response = client.get('/movies/12345/details')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Inception', response.data)  # Check if movie title is in the response
                self.assertIn(b'Netflix', response.data)  # Check if Netflix is listed
                self.assertIn(b'Hulu', response.data)  # Check if Hulu is listed

if __name__ == '__main__':
    unittest.main()
