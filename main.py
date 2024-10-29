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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            'api_key': 'bab2b00a4e94bbaac96b9d7a2c3716b3'  # Replace with actual API key
        }

    @property
    def api_key(self):
        return self.config['api_key']

class ModelLoader:
    @staticmethod
    def load_models():
        try:
            clf = pickle.load(open('nlp_model.pkl', 'rb'))
            vectorizer = pickle.load(open('tranform.pkl', 'rb'))
            logging.info("Models loaded successfully.")
            return clf, vectorizer
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            logging.error(traceback.format_exc())
            return None, None

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
            data = pd.read_csv('main_data.csv')
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

app = Flask(__name__)

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
    try:
        form_data = request.form
        title = form_data['title']
        cast_ids = Utility.convert_to_list_num(form_data['cast_ids'])
        cast_names = Utility.convert_to_list(form_data['cast_names'])
        cast_chars = Utility.convert_to_list(form_data['cast_chars'])
        cast_bdays = Utility.convert_to_list(form_data['cast_bdays'])
        cast_bios = Utility.convert_to_list(form_data['cast_bios'])
        cast_places = Utility.convert_to_list(form_data['cast_places'])
        cast_profiles = Utility.convert_to_list(form_data['cast_profiles'])
        imdb_id = form_data['imdb_id']
        poster = form_data['poster']
        genres = form_data['genres']
        overview = form_data['overview']
        vote_average = form_data['rating']
        vote_count = form_data['vote_count']
        rel_date = form_data['rel_date']
        release_date = form_data['release_date']
        runtime = form_data['runtime']
        status = form_data['status']
        rec_movies = Utility.convert_to_list(form_data['rec_movies'])
        rec_posters = Utility.convert_to_list(form_data['rec_posters'])
        rec_movies_org = Utility.convert_to_list(form_data['rec_movies_org'])
        rec_year = Utility.convert_to_list_num(form_data['rec_year'])
        rec_vote = Utility.convert_to_list_num(form_data['rec_vote'])
        rec_ids = Utility.convert_to_list_num(form_data['rec_ids'])

        for i in range(len(cast_bios)):
            cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')

        for i in range(len(cast_chars)):
            cast_chars[i] = cast_chars[i].replace(r'\n', '\n').replace(r'\"', '\"')

        movie_cards = {rec_posters[i]: [rec_movies[i], rec_movies_org[i], rec_vote[i], rec_year[i], rec_ids[i]] for i in range(len(rec_posters))}
        casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}
        cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

        recommender = MovieRecommender(clf, vectorizer)

        if imdb_id:
            movie_reviews = recommender.fetch_movie_reviews(imdb_id)
            movie_rel_date, curr_date = recommender.get_release_dates(rel_date)
            return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                                   vote_count=vote_count, release_date=release_date, movie_rel_date=movie_rel_date,
                                   curr_date=curr_date, runtime=runtime, status=status, genres=genres,
                                   movie_cards=movie_cards, reviews=movie_reviews, casts=casts, cast_details=cast_details)
        else:
            return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                                   vote_count=vote_count, release_date=release_date, movie_rel_date="", curr_date="",
                                   runtime=runtime, status=status, genres=genres, movie_cards=movie_cards, reviews="",
                                   casts=casts, cast_details=cast_details)
    except Exception as e:
        logging.error(f"Error in recommend route: {e}")
        logging.error(f"URL: {request.url}")
        logging.error(f"Body: {request.get_data()}")
        logging.error(traceback.format_exc())
        return "An error occurred."

if __name__ == "__main__":
    app.run(debug=True)