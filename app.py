import pickle
import streamlit as st
import requests
import pandas as pd

api_key = 'a1c7c41d7acd5a3c303c90d19b72ebe4'

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id,api_key)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def fetch_data(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id,api_key)
    data = requests.get(url)
    data = data.json()
    return data
    
def recommend(movie):
    #Get the movie index
    movie_index = data[movie==data['title']].index[0]
    similarity_movie_dist = similarity_matrix[movie_index]
    recommended = sorted(list(enumerate(similarity_movie_dist)),reverse = True,key = lambda x:x[1])[1:6]
    
    movie_titles = []
    movie_posters = []
    
    for movie in recommended:
        movie_id = data.iloc[movie[0]].movie_id
        movie_posters.append(fetch_poster(movie_id))
        movie_titles.append(data.iloc[movie[0]].title)
        
    return movie_titles,movie_posters

st.header('Movie Recommender')

with open('movies_data_dict.pkl','rb') as file:
    moviesDict = pickle.load(file)
data = pd.DataFrame(moviesDict)

with open('similarity.pkl','rb') as file:
    similarity_matrix = pickle.load(file)

movie_list = data['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list)

if st.button('Show Recommendation'):
    #movie_index = data[selected_movie==data['title']].movie_id
    movie_id = data.loc[data['title'] == selected_movie, 'movie_id'].values[0]
    url = "https://api.themoviedb.org/3/movie/{}?api_key=a1c7c41d7acd5a3c303c90d19b72ebe4".format(movie_id)

    res = requests.get(url)
    res = res.json()
    
    st.image( "https://image.tmdb.org/t/p/w500/"+res["poster_path"], caption=selected_movie, use_column_width=True)
    st.write('Movie Title : ',res["title"])
    st.write('Movie Overview : ',res["overview"])
    st.write('Movie Runtime :',res["runtime"])
    st.write('Movie Language :',res["spoken_languages"][0]["english_name"])
    st.write('Movie Release Date :',res["release_date"])
    st.write('Movie Budget :',res["budget"])
    st.write('Movie Collection :',res["revenue"])
    
    st.header('Movies you might also like :')
    
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Display images in each column
    with col1:
        st.image(recommended_movie_posters[0], caption=recommended_movie_names[0], use_column_width=True)
 
    with col2:
        st.image(recommended_movie_posters[1], caption=recommended_movie_names[1], use_column_width=True)
        
    with col3:
        st.image(recommended_movie_posters[2], caption=recommended_movie_names[2], use_column_width=True)
        
    with col4:
        st.image(recommended_movie_posters[3], caption=recommended_movie_names[3], use_column_width=True)

    with col5:
        st.image(recommended_movie_posters[4], caption=recommended_movie_names[4], use_column_width=True)
    
        
