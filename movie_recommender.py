import streamlit as st
import kagglehub
import pandas as pd
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import process # thefuzz can handle typos

# os.environ['KAGGLEHUB_CACHE'] = "C:/Users/aamna/Documents/Movie Recommendation System"
# path = kagglehub.dataset_download("muqarrishzaib/tmdb-10000-movies-dataset")

dataset = pd.read_csv(r"datasets\muqarrishzaib\tmdb-10000-movies-dataset\versions\1\TMDB 10000 Movies Dataset.csv")
dataset['overview'] = dataset['overview'].fillna('')

#print("Path to dataset files:", path)

st.write("## FlickFinder - Helping you find good movies!")
movie_name = st.text_input("Enter Movie Title")

if movie_name:
    # List of all movie titles
    titles = dataset['title'].dropna().tolist()

    # Get top 3 closest matches
    matches = process.extract(movie_name, titles, limit=3)
    options = [title for title, score in matches]

    # Show dropdown to select the closest match
    best_match = st.selectbox("Choose the closest match:", options)

    # Let user choose sorting option
    sort_option = st.selectbox("Sort recommendations by:", ['Popularity', 'User Rating','Release Date'])

    if best_match:
        match_index = dataset.index[dataset['title'] == best_match]
        # st.write(match_index)
        match_overview = dataset.iloc[match_index]['overview']

        # TF-IDF on all overviews
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(dataset['overview'])

        # Cosine similarity between the best match and all movies
        cosine_sim = cosine_similarity(tfidf_matrix[match_index], tfidf_matrix).flatten()

        # Get top k similar movies (excluding the original match)
        k = 7
        similar_indices = cosine_sim.argsort()[::-1][1:k]

        # Sort by user choice
        if sort_option == 'Release Date':
            sorted_indices = sorted(similar_indices, key=lambda i: dataset.iloc[i]['release_date'], reverse=True)
        elif sort_option == 'User Rating':
            sorted_indices = sorted(
                similar_indices,
                key=lambda i: dataset.iloc[i]['vote_average'] * dataset.iloc[i]['vote_count'], reverse=True)
        else:
            sorted_indices = sorted(similar_indices, key=lambda i: dataset.iloc[i]['popularity'], reverse=True)

        st.write(f"### 🎥 Movies similar to {best_match}")
        for i in sorted_indices:
            st.write(f"- {dataset.iloc[i]['title']}")
        # else:
        #     st.warning("No close matches found.")

else:
    st.info("Type a movie title to get recommendations.")