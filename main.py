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
from recommender import MovieRecommender
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import bcrypt
from flask import jsonify
from flask import session

app = Flask(__name__)

# Replace with your MongoDB connection string
uri = "REPLACE WITH YOUR MongoDB"
client = MongoClient(uri)
db = client['REPLACE WITH YOUR MongoDB']  # Use your database name
users_collection = db['REPLACE WITH YOUR MongoDB']  # Use your collection name

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        suggestions = Utility.get_suggestions()
        return render_template('home.html', suggestions=suggestions)
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

@app.route("/recommend", methods=["POST"])
def recommend():
    movie_id = request.form.get('movie_id')
    try:
        # Fetch recommendations based on the movie_id
        recommendations = movie_recommender.get_recommendations_by_id(movie_id, top_n=10)
        return render_template("recommendations.html", recommendations=recommendations)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.error(f"Error fetching recommendations: {error_traceback}")
        return render_template("error.html", error_message="An error occurred while fetching recommendations.", traceback=error_traceback)

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


@app.route('/myprofile')
def my_profile():
    if 'username' in session:
        username = session['username']
        user = users_collection.find_one({'username': username})
        return render_template('myprofile.html', user=user)
    return render_template('signin.html')

if __name__ == "__main__":
    app.secret_key = "super secret key"
    app.run(debug=True)
