import os

import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
from datetime import date, datetime
import logging
import traceback
import urllib.error
from movie_recommender import MovieRecommender
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import bcrypt
from flask import jsonify
from flask import session

app = Flask(__name__)

# Replace with your MongoDB connection string
uri = "mongodb+srv://seyoubin:seyoubin@csc510.pdrzq.mongodb.net/?retryWrites=true&w=majority&appName=csc510"
client = MongoClient(uri)
db = client['test']  
users_collection = db['users']  # Use your collection name
API_KEY = '66813434ee0cef76f2119aadee082ae5'  
MOVIE_API_URL = 'https://www.themoviedb.org/movie' 
history_collection = db['viewing_history']

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Loading the trained machine learning models (nlp_model.pkl and tranform.pkl) using pickle.load and tfidf vectorizer from disk for sentiment analysis of the movie reviews
try:
    filename = 'nlp_model.pkl'
    clf = pickle.load(open(filename, 'rb'))
    vectorizer = pickle.load(open('tranform.pkl','rb'))
    logging.info("Models loaded successfully.")
except Exception as e:
    logging.error(f"Error loading models: {e}")
    logging.error(traceback.format_exc())


movie_recommender = MovieRecommender()
class ConfigManager:
    _instance = None

    def __new__(cls, config_file):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.config_file = config_file
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        # Load configuration from the file
        self.config = {
            'api_key': ''  # Replace with actual API key
        }

    @property
    def api_key(self):
        return self.config['api_key']


class Utility:
    @staticmethod
    def convert_to_list(my_list):
        try:
            my_list = my_list.split('","')
            my_list[0] = my_list[0].replace('["', '')
            my_list[-1] = my_list[-1].replace('"]', '')
            return my_list
        except Exception as e:
            logging.error(f"Error in convert_to_list: {e}")
            logging.error(traceback.format_exc())
            return []

    @staticmethod
    def convert_to_list_num(my_list):
        try:
            my_list = my_list.split(',')
            my_list[0] = my_list[0].replace("[", "")
            my_list[-1] = my_list[-1].replace("]", "")
            return my_list
        except Exception as e:
            logging.error(f"Error in convert_to_list_num: {e}")
            logging.error(traceback.format_exc())
            return []

    @staticmethod
    def generate_tfidf_matrix(metadata):
        try:
            tfidf = TfidfVectorizer(stop_words="english")
            metadata["overview"] = metadata["overview"].fillna("")
            tfidf_matrix = tfidf.fit_transform(metadata["overview"])
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            np.savez("cosine_similarity_10k", matrix=cosine_sim)
            logging.info("TF-IDF matrix generated and saved successfully.")
        except Exception as e:
            logging.error(f"Error in generate_tfidf_matrix: {e}")
            logging.error(traceback.format_exc())

    @staticmethod
    def get_suggestions():
        try:
            print(os.getcwd())
            data = pd.read_csv('/data/tmdb_5000_movies_sample.csv')
            return list(data['movie_title'].str.capitalize())
        except Exception as e:
            logging.error(f"Error in get_suggestions: {e}")
            logging.error(traceback.format_exc())
            return []

class MovieRecommender:
    def __init__(self, clf, vectorizer):
        self.clf = clf
        self.vectorizer = vectorizer

    def fetch_movie_reviews(self, imdb_id):
        try:
            url = f'https://www.imdb.com/title/{imdb_id}/reviews?ref_=tt_ov_rt'
            headers = {'Authorization': f'Bearer {ConfigManager("config.ini").api_key}'}
            req = urllib.request.Request(url, headers=headers)
            sauce = urllib.request.urlopen(req).read()
            soup = bs.BeautifulSoup(sauce, 'lxml')
            soup_result = soup.find_all("div", {"class": "text show-more__control"})

            reviews_list = []
            reviews_status = []
            for reviews in soup_result:
                if reviews.string:
                    reviews_list.append(reviews.string)
                    movie_review_list = np.array([reviews.string])
                    movie_vector = self.vectorizer.transform(movie_review_list)
                    pred = self.clf.predict(movie_vector)
                    reviews_status.append('Positive' if pred else 'Negative')

            return {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}
        except Exception as e:
            logging.error(f"Error fetching movie reviews: {e}")
            logging.error(traceback.format_exc())
            return {}

    def get_release_dates(self, rel_date):
        try:
            today = str(date.today())
            curr_date = datetime.strptime(today, '%Y-%m-%d')
            movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d') if rel_date else ""
            return movie_rel_date, curr_date
        except Exception as e:
            logging.error(f"Error in get_release_dates: {e}")
            logging.error(traceback.format_exc())
            return "", ""

@app.route("/")

@app.route("/home")
def home():
    try:
        # Check if the user is signed in
        username = session.get('username')
        
        # Fetch personalized recommendations if the user is signed in
        if username:
            # Get user from MongoDB (or another source)
            user = users_collection.find_one({'username': username})

            # Fetch user's viewing history from MongoDB
            viewing_history = history_collection.find({'username': username})

            # Assuming the history contains a list of movie IDs or titles
            watched_movies = [history['id'] for history in viewing_history]

            # Assuming preferred_genres is a list
            preferred_genres = user.get('preferred_genres', [])

            # Fetch movie data from a CSV based on preferred genres and viewing history
            data = pd.read_csv('./data/movies.csv')
            recommendations = data[data['genre'].isin(preferred_genres)]

            # Filter out movies that the user has already watched
            recommendations = recommendations[~recommendations['id'].isin(watched_movies)]
            
            # Now, create a list of movie recommendations (excluding those already watched)
            movie_list = []
            for _, row in recommendations.iterrows():
                movie = {
                    'title': row['title'],
                    'poster': row.get('poster', ''),
                    'movie_id': row.get('id', '')
                }
                movie_list.append(movie)

            personalized_recommendations = movie_list
        else:
            personalized_recommendations = []

        # Log the recommendations to see if anything is problematic
        print(json.dumps(personalized_recommendations, indent=2))

        # Render the home page with personalized recommendations
        suggestions = Utility.get_suggestions()
        return render_template('home.html', personalized_recommendations=personalized_recommendations,suggestions=suggestions)

    except Exception as e:
        logging.error(f"Error in home route: {e}")
        logging.error(traceback.format_exc())
        return "An error occurred."




@app.route("/populate-matches", methods=["POST"])
def populate_matches():
    try:
        res = json.loads(request.get_data("data"))
        movies_list = res['movies_list']
        movie_cards = {
            "https://image.tmdb.org/t/p/original" + movies_list[i]['poster_path'] if movies_list[i]['poster_path'] else "/static/movie_placeholder.jpeg": [
                movies_list[i]['title'], movies_list[i]['original_title'], movies_list[i]['vote_average'],
                datetime.strptime(movies_list[i]['release_date'], '%Y-%m-%d').year if movies_list[i]['release_date'] else "N/A",
                movies_list[i]['id']
            ] for i in range(len(movies_list))
        }
        return render_template('recommend.html', movie_cards=movie_cards)
    except Exception as e:
        logging.error(f"Error in populate_matches route: {e}")
        logging.error(f"URL: {request.url}")
        logging.error(f"Body: {request.get_data()}")
        logging.error(traceback.format_exc())
        return "An error occurred."

@app.route("/recommend", methods=["GET"])  # Change POST to GET
def recommend():
    movie_id = request.args.get('movie_id')  # Use request.args to get query parameters
    try:
        # Fetch recommendations based on the movie_id
        recommendations = movie_recommender.get_recommendations_by_id(id, top_n=10)
        return render_template("./movie_recommender/recommendations.html", recommendations=recommendations)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.error(f"Error fetching recommendations: {error_traceback}")
        return render_template("./movie_recommender/error.html", error_message="An error occurred while fetching recommendations.", traceback=error_traceback)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        genres = request.form.getlist('genre')

        if password != confirm_password:
            return jsonify({'status': 'error', 'message': 'Passwords do not match!'}), 400

        # Check if user already exists
        if users_collection.find_one({'username': username}):
            return jsonify({'status': 'error', 'message': 'User already exists!'}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create a new user
        users_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'preferred_genres': genres
        })

        return jsonify({'status': 'success', 'message': 'Your account has been created!'}), 201

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Username: {username}, Password: {password}")

        user = users_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username  # Store username in session
            return jsonify({'status': 'success', 'message': 'You are signed in!'}), 200
        
        return jsonify({'status': 'error', 'message': 'Check your username or password.'}), 400

    return render_template('signin.html')

@app.route('/signout')
def signout():
    session.clear()  # Clear the session
    try:
        suggestions = Utility.get_suggestions()
        return render_template('home.html', suggestions=suggestions)
    except Exception as e:
        logging.error(f"Error in home route: {e}")
        logging.error(traceback.format_exc())
        return "An error occurred."


@app.route('/myprofile', methods=['GET', 'POST'])
def my_profile():
    if 'username' in session:
        username = session['username']
        user = users_collection.find_one({'username': username})

        # Follow user functionality
        if request.method == 'POST':
            follow_user = request.form['follow_user']
            if follow_user:
                # Fetch the user to follow
                user_to_follow = users_collection.find_one({'username': follow_user})
                
                if user_to_follow:
                    # Add to current user's following list (if not already followed)
                    if follow_user not in user.get('following', []):
                        users_collection.update_one(
                            {'username': username},
                            {'$push': {'following': follow_user}}
                        )
                        # Add the current user to the followed user's followers list (optional)
                        users_collection.update_one(
                            {'username': follow_user},
                            {'$push': {'followers': username}}
                        )
                    else:
                        pass
                else:
                    flash('User not found! Please try again with a valid username.', 'error')

        # After follow, reload the profile page with updated user info
        user = users_collection.find_one({'username': username})  # Refetch to get updated data
        return render_template('myprofile.html', user=user)

    return redirect(url_for('signin'))


# New route to handle user search dynamically
@app.route('/search_user', methods=['GET'])
def search_user():
    search_query = request.args.get('query', '').lower()

    if search_query:
        # Perform case-insensitive search for usernames matching the query
        matched_users = users_collection.find({'username': {'$regex': search_query, '$options': 'i'}})
        users_list = [{'username': user['username']} for user in matched_users]
        return jsonify(users_list)
    return jsonify([])  # Return an empty list if no query is provided




# Function to get movie recommendations based on user's viewing history
def get_smart_recommendations(user_id):
    # Retrieve the user's viewing history from the MongoDB collection
    user_history = history_collection.find({'username': user_id})
    
    # Example logic: Collect all genres from the viewing history
    genres = set()
    for movie in user_history:
        genres.update(movie['genre'].split(','))  # Assuming genre is stored as a comma-separated string
    
    # Now find movies with similar genres (for demo purposes, we use popular movies API)
    recommended_movies = []
    for genre in genres:
        response = requests.get(MOVIE_API_URL, params={
            'api_key': API_KEY,
            'with_genres': genre,
            'page': 1  # For example, get the first page of results
        })
        
        if response.status_code == 200:
            data = response.json()
            for movie in data['results']:
                recommended_movies.append({
                    'title': movie['title'],
                    'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else '',
                    'genre': genre
                })
    
    # Return a list of recommended movies
    return recommended_movies

# Route to render personalized recommendations
@app.route('/recommendations/<user_id>')
def recommendations(user_id):
    # Get recommendations for the given user ID
    personalized_recommendations = get_smart_recommendations(user_id)
    
    # Render the recommendations template
    return render_template('./movie_recommender/recommendations.html', personalized_recommendations=personalized_recommendations)




# Function to fetch trending movies from TMDb
def get_trending_movies():
    try:
        # TMDb API configuration
        TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
        API_KEY = '66813434ee0cef76f2119aadee082ae5'  # Using your existing API key

        # Make API request to get trending movies
        response = requests.get(
            f"https://api.themoviedb.org/3/trending/movie/day",
            params={
                "api_key": API_KEY,
                "language": "en-US"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            movies_data = data['results']
            
            # Process each movie to add complete poster URLs and other details
            trending_movies = []
            for movie in movies_data:
                movie_info = {
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'vote_average': movie.get('vote_average'),
                    'overview': movie.get('overview'),
                    'release_date': movie.get('release_date'),
                    'poster_path': f"{TMDB_IMAGE_BASE_URL}{movie.get('poster_path')}" if movie.get('poster_path') else url_for('static', filename='R.jpg', _external=True)
                }
                trending_movies.append(movie_info)
            
            return trending_movies
        else:
            logging.error(f"Error fetching trending movies: {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error in get_trending_movies: {e}")
        return []
    except Exception as e:
        logging.error(f"Error in get_trending_movies: {e}")
        return []

@app.route('/trending')
def trending():
    # Get trending movies
    trending_movies = get_trending_movies()
    
    # If no movies are returned or there's an error, flash a message
    if not trending_movies:
        flash("Sorry, we couldn't fetch the trending movies. Please try again later.", 'error')

    return render_template('trending.html', trending_movies=trending_movies)


# Your TMDb API Key
TMDB_API_KEY = '9142aba24c1ffa938aae70421c9ee637'
TMDB_BASE_URL = 'https://api.themoviedb.org/3/'

# Function to fetch streaming availability from TMDb
def get_streaming_availability(movie_id):
    url = f"{TMDB_BASE_URL}movie/{movie_id}/watch/providers"
    params = {'api_key': TMDB_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return {}

# Flask route to render movie details and streaming platforms
@app.route('/movies/<int:movie_id>/details')
def movie_details(movie_id):
    # Simulated movie details
    movie = {
        "id": movie_id,
        "title": "Inception",
        "description": "A skilled thief is given a chance at redemption if he can successfully perform an inception."
    }

    # Fetch streaming platform availability
    streaming_data = get_streaming_availability(movie_id)
    streaming_platforms = streaming_data.get('results', {}).get('US', {}).get('flatrate', [])

    return render_template('movie_details.html', movie=movie, streaming_platforms=streaming_platforms)


if __name__ == "__main__":
    app.secret_key = "super secret key"
    app.run(debug=True)