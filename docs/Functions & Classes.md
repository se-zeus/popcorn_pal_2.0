# Movie Recommendation Classes and Functions

## `main.py` Code Documentation

### Class: Main

#### Method: `get_suggestions()`

**Output:**
- Returns a list of movie title suggestions for autocomplete.

#### Method: `convert_to_list(input_string)`

**Input:**
- input_string (string): Input string to be converted to a list.

**Output:**
- Returns a list based on the input string.

#### Method: `convert_to_list_num(input_string)`

**Input:**
- input_string (string): Input string containing numbers separated by commas.

**Output:**
- Returns a list of numbers based on the input string.

#### Method: `populate_matches(movies_list)`

**Input:**
- movies_list (list): List of movie details to populate matches.

**Output:**
- Returns a dictionary of movie cards.

#### Method: `recommend()`

**Input:**
- Various form data fields (e.g., title, cast_ids, cast_names, etc.).

**Output:**
- Renders a recommendation HTML page with movie details.

## `search.py` Code Documentation

### Class: Search

#### Method: `startsWith(self, word)`

**Input:**
- word (string): The name of the movie.

**Output:**
- Returns a list of movies that start with the given word.

#### Method: `anywhere(self, word, visitedWords)`

**Input:**
- word (string): The name of the movie.
- visitedWords (set): A set of movies that should not be part of the output.

**Output:**
- Returns a list of movies that have the input word anywhere in their title.

#### Method: `results(self, word)`

**Input:**
- word (string): The name of the movie.

**Output:**
- Returns a list of movies where the first few movies start with the input word, followed by movies that have the input word anywhere in their title.

#### Method: `resultsTop10(self, word)`

**Input:**
- word (string): The name of the movie.

**Output:**
- Returns the first 10 results from the `results` method.


