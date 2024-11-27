# Movie Recommendation API URLs

## Base URL
The base URL for the API is: `http://localhost:5000/`

## Endpoints

### 1. Home Page - Get Autocomplete Suggestions
- **Endpoint:** `GET /home`
- **Description:** Returns a list of movie title suggestions for autocomplete.
- **Request:** `GET /home`
- **Response:**
  ```json
  {
    "suggestions": ["Movie 1", "Movie 2", "Movie 3"]
  } 

### 2. Populate Movie Matches
 - **Endpoint:** POST /populate-matches
 - **Description:** Populates movie matches based on user-provided movie details.
 - **Request:** POST /populate-matches

```json
{
  "movies_list": [
    {
      "genre": "Animation",
      "title": "Movie Title",
      "original_title": "Movie Title",
      "rating": 8.5,
      "release_date": "2022-01-01",
      "id": 123,
      "status": "Released"
    }
  ]
} 
```

### Response
 - **Status Code:** 200 OK
 - **Content Type:** text/html

### 3. Get Movie Recommendations
 - **Endpoint:** POST /recommend
 - **Description:** Generates movie recommendations based on user input and provides detailed movie information.
 - **Request:** POST /recommend
 - **Form Data:**
    - **title:** Movie title
    - **cast_ids:** Comma-separated list of cast IDs
    - **cast_names:** Comma-separated list of cast names
    - **cast_chars:** Comma-separated list of cast characters
    
### Response:
 - **Status Code:** 200 OK
 - **Content Type:** text/html 
