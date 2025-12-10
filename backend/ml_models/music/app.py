from movieRec import recommend_movies
from flask import Flask, render_template, request, jsonify
import os
from flask_cors import CORS
import pandas as pd
import mysql.connector
import pickle

app = Flask(__name__)
CORS(app)

##################### Database Conn & MySQL APIs ########################


def mysql_connect():
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'dbfinalproject.cpcem4w6a78y.us-east-1.rds.amazonaws.com'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', '295bfinalproject'),
        database=os.environ.get('DB_NAME', 'finaldb'),
        port=os.environ.get('DB_PORT', '3306'),
    )
    return conn


# api to get values for signup questionairre
# output format: {'happy_movie': 'Action, Horror', 'sad_movie': 'Comedy, Family', 'neutral_movie': 'Drama, Romance', 'user_id': 7}
def get_user_movie_data(user_id):
    conn = mysql_connect()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM genre_preferences WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


# api to get values for signin questionairre
# output format: {'user_id': 4, 'mood': 'happy', 'time_preference': 'latest'}
def get_signin_ques_data(user_id):
    conn = mysql_connect()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT user_id, mood, time_preference FROM questionnaire_responses WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


########################################################################


############################# Music Model APIs ##################################

# Load the scaler
with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Load the multi-output model
with open('multi_target_rf_model.pkl', 'rb') as model_file:
    multi_target_rf = pickle.load(model_file)

# Load your dataset
df = pd.read_csv("./playlist_features.csv", index_col=0)
# Make sure to preprocess your dataframe here as per your model's requirement

df['Release_Year'] = pd.to_datetime(df['Release_Date']).dt.year


def label_mood(row):
    if row['Valence'] >= 0.7:
        return 'happy'
    elif row['Valence'] <= 0.39:
        return 'sad'
    else:
        return 'neutral'


df['Mood'] = df.apply(lambda row: label_mood(row), axis=1)

# Categorize songs by release year


def categorize_release_year(year):
    if year >= 2023:
        return 'latest'
    elif 2010 <= year <= 2022:
        return 'mid'
    else:
        return 'old'


df['Release_Era'] = df['Release_Year'].apply(categorize_release_year)


def recommend_songs_for_user_preferences(model, df, scaler, user_mood, user_era, num_recommendations):
    print("Starting recommendations...")  # Debugging statement

    # Assuming df is your original dataset and it has been processed as per the model's requirements

    # Extract features and scale
    features = df[['Valence', 'Danceability', 'Energy',
                   'Release_Year', 'Acousticness', 'Loudness', 'Tempo']]
    scaled_features = scaler.transform(features)

    # Make predictions for the entire dataset
    predictions = model.predict(scaled_features)

    # Convert predictions to a DataFrame for easier handling
    predictions_df = pd.DataFrame(
        predictions, columns=['Mood', 'Release_Era'], index=df.index)

    print("Predictions DataFrame created.")  # Debugging statement

    # Add predictions back to the original dataset to filter
    df_with_predictions = df.assign(
        Predicted_Mood=predictions_df['Mood'], Predicted_Era=predictions_df['Release_Era'])

    print("Filtering songs based on user preferences...")  # Debugging statement
    # It's helpful to inspect the DataFrame shapes to ensure that the filtering hasn't introduced issues.
    print(
        f"df_with_predictions shape before filtering: {df_with_predictions.shape}")

    # Filter based on user preferences
    filtered_songs = df_with_predictions[
        (df_with_predictions['Predicted_Mood'] == user_mood) &
        (df_with_predictions['Predicted_Era'] == user_era)
    ]

    # Debugging statement
    print(f"Filtered songs shape: {filtered_songs.shape}")

    # Ensure the filtering operation is working as intended
    if filtered_songs.empty:
        print("No songs match the user preferences.")  # Debugging statement
        return pd.DataFrame()  # Return an empty DataFrame if no songs match

    # Sort and return top N recommendations
    top_recommendations = filtered_songs.sort_values(
        by=['Popularity'], ascending=False).head(num_recommendations)

    # Debugging statement
    print(f"Top recommendations shape: {top_recommendations.shape}")

    return top_recommendations[['Track_id']]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_mood = request.form.get('mood')
        print(user_mood)
        user_era = request.form.get('era')

        recommendations = recommend_songs_for_user_preferences(
            multi_target_rf, df, scaler, user_mood, user_era, 10)
        print(recommendations['Track_id'])
        if not recommendations.empty:
            # Convert DataFrame column to list
            recomm = recommendations['Track_id'].tolist()
        else:
            recomm = []
        return render_template('music.html', recommendations=recomm)
    return render_template('music.html', recommendations=None)


@app.route('/predict', methods=['GET'])
def predict():
    # user_mood = "happy"
    # user_era = "latest"

    # Retrieve the user_id from query parameters
    # 'default_user_id' is a fallback if no userid is provided
    user_id = request.args.get('userid', 'default_user_id')
    print(f"User ID: {user_id}")

    signin_res = get_signin_ques_data(user_id)
    print(signin_res['mood'])

    user_mood = signin_res['mood']
    user_era = signin_res['time_preference']
    print(user_era)

    recommendations = recommend_songs_for_user_preferences(
        multi_target_rf, df, scaler, user_mood, user_era, 5)
    print(recommendations['Track_id'].tolist())
    if not recommendations.empty:
        # Convert DataFrame column to list
        recomm = recommendations['Track_id'].tolist()
        recomm_url = [
            f"https://open.spotify.com/embed/track/{track_id}?utm_source=oembed" for track_id in recomm]
    else:
        recomm_url = []
    return jsonify(recomm_url)


########################################################################


############################# Movie Model APIs ##################################
# Tmdb API key: de8a7853bbd000984d6455656338eb6d
# https://api.themoviedb.org/3/movie/278?api_key=de8a7853bbd000984d6455656338eb6d

@app.route('/recommend/movie', methods=['GET'])
def recommend():

    user_id = 7
    pref_era = "mid"
    curr_mood = "sad"

    user_id = request.args.get('userid', 'default_user_id')
    print(f"From Movie Side User ID: {user_id}")

    signin_res = get_signin_ques_data(user_id)

    curr_mood = signin_res['mood']
    pref_era = signin_res['time_preference']
    print(pref_era)

    user_data = get_user_movie_data(user_id)
    print(user_data)
    movies = pd.read_csv('./tmdb2024_new.csv')
    filtered_movies = movies[movies['Release_Era'] == pref_era]
    recommendations = recommend_movies(
        user_data, filtered_movies, curr_mood, 5)
    print(recommendations)
    movie_tmdb = [
        f"https://api.themoviedb.org/3/movie/{movie_id[0]}?api_key=de8a7853bbd000984d6455656338eb6d" for movie_id in recommendations]
    return jsonify(movie_tmdb)


#################################################################################

if __name__ == '__main__':
    app.run(debug=True)
