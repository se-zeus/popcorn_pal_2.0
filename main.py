import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
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

# Loading the trained machine learning models (nlp_model.pkl and tranform.pkl) using pickle.load and tfidf vectorizer from disk for sentiment analysis of the movie reviews
try:
    filename = 'nlp_model.pkl'
    clf = pickle.load(open(filename, 'rb'))
    vectorizer = pickle.load(open('tranform.pkl','rb'))
    logging.info("Models loaded successfully.")
except Exception as e:
    logging.error(f"Error loading models: {e}")
    logging.error(traceback.format_exc())

# Below functions are defined to convert strings to lists, generate a TF-IDF matrix, and get movie suggestions from a CSV file (main_data.csv)
def convert_to_list(my_list):
    try:
        my_list = my_list.split('","')
        my_list[0] = my_list[0].replace('["','')
        my_list[-1] = my_list[-1].replace('"]','')
        return my_list
    except Exception as e:
        logging.error(f"Error in convert_to_list: {e}")
        logging.error(traceback.format_exc())
        return []

def convert_to_list_num(my_list):
    try:
        my_list = my_list.split(',')
        my_list[0] = my_list[0].replace("[","")
        my_list[-1] = my_list[-1].replace("]","")
        return my_list
    except Exception as e:
        logging.error(f"Error in convert_to_list_num: {e}")
        logging.error(traceback.format_exc())
        return []

def generate_tfidf_matrix(metadata):
    try:
        tfidf = TfidfVectorizer(stop_words="english")
        metadata["overview"] = metadata["overview"].fillna("")
        tfidf_matrix = tfidf.fit_transform(metadata["overview"])
        cosine_similarity = linear_kernel(tfidf_matrix, tfidf_matrix)
        np.savez("cosine_similarity_10k", matrix=cosine_similarity)
        logging.info("TF-IDF matrix generated and saved successfully.")
    except Exception as e:
        logging.error(f"Error in generate_tfidf_matrix: {e}")
        logging.error(traceback.format_exc())

def get_suggestions():
    try:
        data = pd.read_csv('main_data.csv')
        return list(data['movie_title'].str.capitalize())
    except Exception as e:
        logging.error(f"Error in get_suggestions: {e}")
        logging.error(traceback.format_exc())
        return []

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    try:
        suggestions = get_suggestions()
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
        movie_cards = {"https://image.tmdb.org/t/p/original"+movies_list[i]['poster_path'] if movies_list[i]['poster_path'] else "/static/movie_placeholder.jpeg": [movies_list[i]['title'],movies_list[i]['original_title'],movies_list[i]['vote_average'],datetime.strptime(movies_list[i]['release_date'], '%Y-%m-%d').year if movies_list[i]['release_date'] else "N/A", movies_list[i]['id']] for i in range(len(movies_list))}
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
        title = request.form['title']
        cast_ids = request.form['cast_ids']
        cast_names = request.form['cast_names']
        cast_chars = request.form['cast_chars']
        cast_bdays = request.form['cast_bdays']
        cast_bios = request.form['cast_bios']
        cast_places = request.form['cast_places']
        cast_profiles = request.form['cast_profiles']
        imdb_id = request.form['imdb_id']
        poster = request.form['poster']
        genres = request.form['genres']
        overview = request.form['overview']
        vote_average = request.form['rating']
        vote_count = request.form['vote_count']
        rel_date = request.form['rel_date']
        release_date = request.form['release_date']
        runtime = request.form['runtime']
        status = request.form['status']
        rec_movies = request.form['rec_movies']
        rec_posters = request.form['rec_posters']
        rec_movies_org = request.form['rec_movies_org']
        rec_year = request.form['rec_year']
        rec_vote = request.form['rec_vote']
        rec_ids = request.form['rec_ids']

        suggestions = get_suggestions()

        rec_movies_org = convert_to_list(rec_movies_org)
        rec_movies = convert_to_list(rec_movies)
        rec_posters = convert_to_list(rec_posters)
        cast_names = convert_to_list(cast_names)
        cast_chars = convert_to_list(cast_chars)
        cast_profiles = convert_to_list(cast_profiles)
        cast_bdays = convert_to_list(cast_bdays)
        cast_bios = convert_to_list(cast_bios)
        cast_places = convert_to_list(cast_places)
        cast_ids = convert_to_list_num(cast_ids)
        rec_vote = convert_to_list_num(rec_vote)
        rec_year = convert_to_list_num(rec_year)
        rec_ids = convert_to_list_num(rec_ids)

        for i in range(len(cast_bios)):
            cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"','\"')

        for i in range(len(cast_chars)):
            cast_chars[i] = cast_chars[i].replace(r'\n', '\n').replace(r'\"','\"') 

        movie_cards = {rec_posters[i]: [rec_movies[i],rec_movies_org[i],rec_vote[i],rec_year[i],rec_ids[i]] for i in range(len(rec_posters))}
        casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}
        cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}
        
        if(imdb_id != ""):

            # sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
            url = 'https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)
            sauce = urllib.request.urlopen(url).read()
            soup = bs.BeautifulSoup(sauce,'lxml')
            soup_result = soup.find_all("div",{"class":"text show-more__control"})

            reviews_list = []
            reviews_status = []
            for reviews in soup_result:
                if reviews.string:
                    reviews_list.append(reviews.string)
                    movie_review_list = np.array([reviews.string])
                    movie_vector = vectorizer.transform(movie_review_list)
                    pred = clf.predict(movie_vector)
                    reviews_status.append('Positive' if pred else 'Negative')

            movie_rel_date = ""
            curr_date = ""
            if(rel_date):
                today = str(date.today())
                curr_date = datetime.strptime(today,'%Y-%m-%d')
                movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d')

            movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}     

            return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
                vote_count=vote_count,release_date=release_date,movie_rel_date=movie_rel_date,curr_date=curr_date,runtime=runtime,status=status,genres=genres,movie_cards=movie_cards,reviews=movie_reviews,casts=casts,cast_details=cast_details)

        else:
            return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
                vote_count=vote_count,release_date=release_date,movie_rel_date="",curr_date="",runtime=runtime,status=status,genres=genres,movie_cards=movie_cards,reviews="",casts=casts,cast_details=cast_details)
    except Exception as e:
        logging.error(f"Error in recommend route: {e}")
        logging.error(f"URL: {request.url}")
        logging.error(f"Body: {request.get_data()}")
        logging.error(traceback.format_exc())
        return "An error occurred."

if __name__ == '__main__':
    app.run(debug=True)