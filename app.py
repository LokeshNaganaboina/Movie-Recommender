import pickle
import streamlit as st
import requests
import pandas as pd
import boto3
from PIL import Image



aws_credentials = st.secrets["aws"]
aws_access_key_id = aws_credentials["aws_access_key_id"]
aws_secret_access_key = aws_credentials["aws_secret_access_key"]

s3 = boto3.client('s3',aws_access_key_id=aws_access_key_id, 
                  aws_secret_access_key=aws_secret_access_key)



bucket_name = "movie-recommender-st"

tmdb_credentials = st.secrets["tmdb"]
api_key = tmdb_credentials["api_key"]

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

def resizeImage(image,size):
    img = Image.open(image)
    img = img.resize(size)
    return img
    
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

st.header('CineSelect : Movie Recommender')

movies_data_key = 'movies_data_dict.pkl'
movies_data_file = s3.get_object(Bucket=bucket_name, Key=movies_data_key)
moviesDict = pickle.loads(movies_data_file['Body'].read())
data = pd.DataFrame(moviesDict)


similarity_key = 'similarity.pkl'
similarity_file = s3.get_object(Bucket=bucket_name, Key=similarity_key)
similarity_matrix = pickle.loads(similarity_file['Body'].read())


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
    
    try:
        poster = res["poster_path"]
        title = res["title"]
        overview = res["overview"]
        runtime = res["runtime"]
        movie_language = res["spoken_languages"][0]["english_name"]
        release_date = res["release_date"]
        budget = res["budget"]
        revenue = res["revenue"]
    except:
        poster = 'Not Available'
        title = 'Not Available'
        overview = 'Not Available'
        runtime = 'Not Available'
        movie_language = 'Not Available'
        release_date = 'Not Available'
        budget = 'Not Available'
        revenue = 'Not Available'
    
    #resized_image = resizeImage("https://image.tmdb.org/t/p/w500/"+poster,(300,300))
    
    #image = Image.open("https://image.tmdb.org/t/p/w500"+poster)
    column1,column2 = st.columns(2)
    with column1:
        st.image( "https://image.tmdb.org/t/p/w500"+poster , width = 200, caption=selected_movie)
    with column2:
        st.write('Movie Title : ',title)
        st.write('Movie Overview : ',overview)
        st.write('Movie Runtime :',runtime,' minutes')
        st.write('Movie Language :',movie_language)
        st.write('Movie Release Date :',release_date)
        st.write('Movie Budget :',budget,' crores')
        st.write('Movie Collection :',revenue,' crores')
    
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
    
        
