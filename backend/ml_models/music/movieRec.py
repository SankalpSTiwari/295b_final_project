import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
pd.options.mode.chained_assignment = None  # default='warn'


def parse_genres(genres_str):
    return genres_str.split(', ') if genres_str else []


def recommend_movies(user_data, movies, current_mood, top_n):
    # Bail out early if we are missing data
    if not user_data:
        return []
    mood_key = f'{current_mood.lower()}_movie'
    user_pref_genres = parse_genres(user_data.get(mood_key, ''))
    if not user_pref_genres:
        return []

    # movies['Genres'] = movies['Genres'].apply(parse_genres)
    movies['Genres'] = movies['Genres'].str.lower()
    movie_genres_df = movies[movies['Genres'].apply(
        lambda genres: any(genre in genres for genre in user_pref_genres))]
    if movie_genres_df.empty:
        # Fallback: return top popular movies if no genre match
        movie_genres_df = movies.sort_values(by='popularity', ascending=False).head(top_n)

    mlb = MultiLabelBinarizer()
    movie_genres_encoded = mlb.fit_transform(movie_genres_df['Genres'])
    if movie_genres_encoded.size == 0:
        return []
    genre_prefs_encoded = mlb.transform([user_pref_genres])
    if genre_prefs_encoded.size == 0:
        return []
    similarity_scores = cosine_similarity(
        genre_prefs_encoded, movie_genres_encoded)[0]

    scaler = MinMaxScaler()
    normalized_popularity = scaler.fit_transform(
        movie_genres_df[['popularity']])
    normalized_vote_average = scaler.fit_transform(
        movie_genres_df[['vote_average']])

    final_scores = similarity_scores + normalized_popularity.flatten() + \
        normalized_vote_average.flatten()
    top_indices = np.argsort(final_scores)[-top_n:][::-1]
    recommended_movies_info = movie_genres_df.iloc[top_indices]

    # return recommended_movies_info[['id']].to_dict(orient='records')
    return recommended_movies_info[['id']].values.tolist()
