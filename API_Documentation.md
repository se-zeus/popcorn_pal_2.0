# **Movie Recommendation API Documentation**

## **Introduction**

The **Movie Recommendation API** provides endpoints to deliver movie recommendations based on user input. It leverages machine learning models to suggest personalized recommendations and includes features like autocomplete for movie titles and detailed movie metadata.

---

## **Base URL**

The API runs locally and can be accessed via:  
`http://localhost:5000/`

---

## **Endpoints**

### **1. Home Page - Get Autocomplete Suggestions**

- **Endpoint:** `GET /home`  
- **Description:** Provides a list of movie title suggestions for autocomplete functionality.  
- **Request Example:**  
  ```http
  GET /home
  ```
- **Response Example:**  
  ```json
  {
    "suggestions": ["Inception", "Interstellar", "Iron Man"]
  }
  ```

---

### **2. Populate Movie Matches**

- **Endpoint:** `POST /populate-matches`  
- **Description:** Populates a set of movie matches based on a list of user-provided movie details.  
- **Request Example:**  
  ```json
  {
    "movies_list": [
      {
        "poster_path": "/path/to/poster.jpg",
        "title": "Inception",
        "original_title": "Inception",
        "vote_average": 8.8,
        "release_date": "2010-07-16",
        "id": 27205
      }
    ]
  }
  ```
- **Response:**  
  - **Status Code:** `200 OK`  
  - **Content Type:** `text/html`

---

### **3. Get Movie Recommendations**

- **Endpoint:** `POST /recommend`  
- **Description:** Generates personalized movie recommendations based on the user's preferences and provided input.  
- **Request Example:**  
  ```http
  POST /recommend
  ```
  **Form Data:**  
  ```plaintext
  title=Inception
  cast_ids=123,456
  cast_names=Leonardo DiCaprio, Joseph Gordon-Levitt
  cast_chars=Dom Cobb, Arthur
  ...
  ```
- **Response:**  
  - **Status Code:** `200 OK`  
  - **Content Type:** `text/html`

---

## **`search.py` Code Documentation**

The `search.py` file contains the **`Search`** class, which implements the logic for movie search and autocomplete functionality.

### **Class: `Search`**

#### **1. `startsWith(self, word)`**
- **Input:**  
  - `word`: A string containing the initial part of the movie title.  
- **Output:**  
  - Returns a list of movies whose titles start with the input word.  

#### **2. `anywhere(self, word, visitedWords)`**
- **Input:**  
  - `word`: A string containing any part of the movie title.  
  - `visitedWords`: A set of movie titles to exclude from the output.  
- **Output:**  
  - Returns a list of movies where the input word appears anywhere in the title (excluding those in `visitedWords`).  

#### **3. `results(self, word)`**
- **Input:**  
  - `word`: A string containing any part of the movie title.  
- **Output:**  
  - Combines results from `startsWith` and `anywhere` methods. Returns a prioritized list with movies starting with the input word appearing first.  

#### **4. `resultsTop10(self, word)`**
- **Input:**  
  - `word`: A string containing any part of the movie title.  
- **Output:**  
  - Retrieves the top 10 results from the `results` method.  

---

## **Additional Notes**

- **Dependencies:**  
  Ensure you have the required dependencies installed, and use **Python 3.10** to avoid compatibility issues with older dependencies (e.g., `transformers`, `tokenizers`).

- **Anaconda Setup:**  
  The project requires Anaconda for environment management. Refer to the [Contributing Guidelines](https://github.com/se-zeus/popcorn_pal_2.0/blob/master/CONTRIBUTING.md) for detailed setup instructions.