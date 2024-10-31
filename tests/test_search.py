import unittest
import pandas as pd
from search import Search  # Make sure this path is correct

class TestSearch(unittest.TestCase):
    def setUp(self):
        # Sample DataFrame for testing
        data = {
            'title': [
                'Star Wars: Episode IV - A New Hope (1977)',
                'Star Wars: Episode V - The Empire Strikes Back (1980)',
                'Star Wars: Episode VI - Return of the Jedi (1983)',
                'Star Trek (2009)',
                'The Godfather (1972)',
                'Gone with the Wind (1939)'
            ]
        }
        self.df = pd.DataFrame(data)
        self.search = Search(self.df)

    def test_anywhere(self):
        visited_words = set()
        result = self.search.anywhere("Star", visited_words)
        expected = [
            'Star Wars: Episode IV - A New Hope (1977)',
            'Star Wars: Episode V - The Empire Strikes Back (1980)',
            'Star Wars: Episode VI - Return of the Jedi (1983)',
            'Star Trek (2009)'
        ]
        self.assertEqual(result, expected)

    def test_results(self):
        result = self.search.results("Star")
        expected = [
            'Star Wars: Episode IV - A New Hope (1977)',
            'Star Wars: Episode V - The Empire Strikes Back (1980)',
            'Star Wars: Episode VI - Return of the Jedi (1983)',
            'Star Trek (2009)'
        ]
        self.assertEqual(result, expected)

    def test_resultsTop10(self):
        result = self.search.resultsTop10("Star")
        expected = [
            'Star Wars: Episode IV - A New Hope (1977)',
            'Star Wars: Episode V - The Empire Strikes Back (1980)',
            'Star Wars: Episode VI - Return of the Jedi (1983)',
            'Star Trek (2009)'
        ]
        self.assertEqual(result, expected[:10])

if __name__ == '__main__':
    unittest.main()
