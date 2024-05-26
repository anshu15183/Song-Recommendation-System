import streamlit as st
import pickle
import pandas as pd
import requests
import spotipy
import requests
import base64
from spotipy.oauth2 import SpotifyClientCredentials
import warnings
from logger import logging
from exception import CustomException
import sys
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Musicify || Music Recommendation System",  # Set custom page title
    page_icon="favicon.ico",  # Set URL of the favicon
    layout="wide"  # Set layout to wide mode if desired
)

CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

##Songs data
music_dict = pickle.load(open(r'artifacts/musicrec.pkl', 'rb'))
music = pd.DataFrame(music_dict)

## Similarity distance between songs
similarity = pickle.load(open(r'artifacts/similarity.pkl', 'rb'))


text_style = (
    "font-weight: normal; "
    "font-size: 18px; "
    "color: #7B3F00;"
    "font-weight: bold;"
)
link_style = (
    "text-decoration: none; "
    "color: #007bff; "
    "font-weight: bold; "
    "font-size: 1.5rem; "
    "padding-top : 20px; " # Add padding to the top
    "animation: pulse 1s infinite; "  # Add animation
)

# Define CSS keyframes for animation
keyframes = (
    "@keyframes pulse { "
    "0% { transform: scale(1); } "
    "50% { transform: scale(1.1); } "
    "100% { transform: scale(1); } "
    "} "
)
center_style = (
    "text-align: center; "  # Center the text horizontally
    "padding: 7px; "  # Add 10 pixels of padding
    "font-size: 75px;"
)
title_style = (
    "color: #007bff; "  
    "font-size: 32px; "  
    "font-weight: bold; "  
    "text-align: center; "  
)
team_style = """
<style>
.ok-text { 
    color:#D4AF37;
    font-weight:bold;
    display: inline-block;
    font-size:2rem;
}
}
</style>
"""


# Function to fetch track information from Spotify API
def fetch_track_info(track_name):

    """
    This function is used for fetch the poster url of the enter song
    
    Args:
        Song Name

    return:
           Poster Url 
    """


    logging.info("I am Enter In Fetch Track Info Function")
    try:
        url = "https://api.spotify.com/v1/search"
        
        params = {
            "q": f"track:{track_name}",
            "type": "track"
        }
        
        client_id = CLIENT_ID
        client_secret = CLIENT_SECRET
        
        client_credentials = f"{client_id}:{client_secret}"
        encoded_client_credentials = base64.b64encode(client_credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_client_credentials}"
        }
        
        token_url = "https://accounts.spotify.com/api/token"
        token_params = {
            "grant_type": "client_credentials"
        }
        token_response = requests.post(token_url, data=token_params, headers=headers)
        
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            headers["Authorization"] = f"Bearer {access_token}"
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "tracks" in data and "items" in data["tracks"] and len(data["tracks"]["items"]) > 0:
                    track = data["tracks"]["items"][0]
                    album_cover_url = track["album"]["images"][0]["url"]
                    return album_cover_url
                else:
                    return "https://i.postimg.cc/0QNxYz4V/social.png"
            else:
                return "https://i.postimg.cc/0QNxYz4V/social.png"
        else:
            return "https://i.postimg.cc/0QNxYz4V/social.png"
        
    except Exception as e:

        logging.info("Error Occure {}".format(e))
        raise CustomException(e, sys)


#This function is used to given recommend songs to users
def recommend(song):

    """
    This function is used for recommended movie base on user experience 
    
    Args:
        Song Name

    return:
           Poster List And Movies Name List 
    """
    try:
        logging.info("I am Enter Recommend Fun")
        index = music[music['title'] == song].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_music_names = []
        recommended_music_posters = []
        for i in distances[0:11]:
            recommended_music_posters.append(fetch_track_info(music.iloc[i[0]].title))
            recommended_music_names.append(music.iloc[i[0]].title)

        return recommended_music_names, recommended_music_posters
    
    except Exception as e:

        logging.info("Error Occure {}".format(e))
        raise CustomException(e, sys)


#This function is used to fetch song information
def fetch_song_info(track_name):

    """
    This function is used for fetch song information like name,release date, ranking and more.
    
    Args:
        Song Name

    return:
           track_name, artist_name, album_name, release_date, popularity, spotify_url
    """

    logging.info("I am enter fetch song info function")
    try:
        url = "https://api.spotify.com/v1/search"
        
        # Parameters for the query
        params = {
            "q": f"track:{track_name}",
            "type": "track"
        }
        
        # Spotify API credentials
        client_id = "70a9fb89662f4dac8d07321b259eaad7"
        client_secret = "4d6710460d764fbbb8d8753dc094d131"
        
        # Encode client ID and client secret
        client_credentials = f"{client_id}:{client_secret}"
        encoded_client_credentials = base64.b64encode(client_credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_client_credentials}"
        }
        
        token_url = "https://accounts.spotify.com/api/token"
        token_params = {
            "grant_type": "client_credentials"
        }
        token_response = requests.post(token_url, data=token_params, headers=headers)
        
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            headers["Authorization"] = f"Bearer {access_token}"
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "tracks" in data and "items" in data["tracks"] and len(data["tracks"]["items"]) > 0:
                    track = data["tracks"]["items"][0]  
                    track_name = track["name"]
                    artist_name = track["artists"][0]["name"]
                    album_name = track["album"]["name"]
                    release_date = track["album"]["release_date"]
                    popularity = track["popularity"]
                    spotify_url = track["external_urls"]["spotify"]
                    
                    return track_name, artist_name, album_name, release_date, popularity, spotify_url
                else:
                    return "None"
            else:
                return "None"
        else:
            return "None"
    except Exception as e:

        logging.info("Error Occure {}".format(e))
        raise CustomException(e, sys)


st.markdown(
    """
    <style>
    .title {
        text-align: center;
        color: #D4AF37; /* Set the color to the desired hex value */
        font-weight: bold; /* Make the text bold */
    }
    </style>
    """,
    unsafe_allow_html=True
)

#Project title
st.markdown("<h1 class='title'>Music Recommendation System</h1>", unsafe_allow_html=True)
selected_music_name = st.selectbox('Select a music you like', music['title'].values)


if st.button('Recommend',):
    st.write(f'</br></br>', unsafe_allow_html=True)
    
    #Fetch All Data from api
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(selected_music_name)
        name,artist_name,album_name,release_date,popularity,spotify_url = fetch_song_info(selected_music_name)
    
    #User Enter movie
    col1, col2,col3 = st.columns(3)

    with col1:
        st.write(f'<div style="font-weight: bold;font-size: 22px;color: #007bff;">{name}</div>', unsafe_allow_html=True)
        st.image(posters[0], width=300)  
    with col2:
        st.write(f'<div style="{text_style} padding-top: 25px;">Song Name   : {name}</div></br>', unsafe_allow_html=True)
        st.write(f'<div style="{text_style}">Artist Name : {artist_name}</div></br>', unsafe_allow_html=True)
        st.write(f'<div style="{text_style}">Album Name  : {album_name}</div></br>', unsafe_allow_html=True)
        st.write(f'<div style="{text_style}">Release Date: {release_date}</div></br>', unsafe_allow_html=True)
        st.write(f'<div style="{text_style}">Popularity  : {popularity}</div></br>', unsafe_allow_html=True)
    with col3:
         if spotify_url:
            st.markdown(f'<style>{keyframes}</style>'f'<a href="{spotify_url}" target="_blank" style="{link_style}"><svg viewBox="0 0 48 48" width="24" height="24" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" fill="#000000">
    <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
    <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
    <g id="SVGRepo_iconCarrier">
        <title>Spotify-color</title>
        <desc>Created with Sketch.</desc>
        <defs></defs>
        <g id="Icons" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
            <g id="Color-" transform="translate(-200.000000, -460.000000)" fill="#00DA5A">
                <path d="M238.16,481.36 C230.48,476.8 217.64,476.32 210.32,478.6 C209.12,478.96 207.92,478.24 207.56,477.16 C207.2,475.96 207.92,474.76 209,474.4 C217.52,471.88 231.56,472.36 240.44,477.64 C241.52,478.24 241.88,479.68 241.28,480.76 C240.68,481.6 239.24,481.96 238.16,481.36 M237.92,488.08 C237.32,488.92 236.24,489.28 235.4,488.68 C228.92,484.72 219.08,483.52 211.52,485.92 C210.56,486.16 209.48,485.68 209.24,484.72 C209,483.76 209.48,482.68 210.44,482.44 C219.2,479.8 230,481.12 237.44,485.68 C238.16,486.04 238.52,487.24 237.92,488.08 M235.04,494.68 C234.56,495.4 233.72,495.64 233,495.16 C227.36,491.68 220.28,490.96 211.88,492.88 C211.04,493.12 210.32,492.52 210.08,491.8 C209.84,490.96 210.44,490.24 211.16,490 C220.28,487.96 228.2,488.8 234.44,492.64 C235.28,493 235.4,493.96 235.04,494.68 M224,460 C210.8,460 200,470.8 200,484 C200,497.2 210.8,508 224,508 C237.2,508 248,497.2 248,484 C248,470.8 237.32,460 224,460" id="Spotify"> </path>
            </g>
        </g>
    </g>
</svg> 🎵 Listen on Spotify 🎵</a></br>',unsafe_allow_html=True)
            
    
    
    logging.info("Successfully show user enter movie with information")
    
    #Recommended Movies
    st.markdown(f'<h1 style="{title_style}">Recommended Songs</h1></br>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    for i in range(1, 6):
        with columns[i - 1]:
            st.write(f"<div style='color: hotpink;font-size:18px;font-weight:bold; text-align:center'>{names[i]}</div>", unsafe_allow_html=True)
            st.image(posters[i])
            
    st.write(f'</br></br>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    for i, col in enumerate(columns):  
        with col:
            st.write(f"<div style='color: hotpink;font-size:18px;font-weight:bold;text-align:center'>{names[i+6]}</div>", unsafe_allow_html=True)
            st.image(posters[i + 6])

    logging.info("Successfully show all resommended movies")


##Team Name 
st.write('</br></br><div class="footer" style="text-align:center;padding-top: 25px; font-size: 15px;"><span style="font-size: 25px;color:red;"> </span><span class="ok-text">Made With <span style="color:red;"> &hearts; </span> By Team 200 Ok </span></div>', unsafe_allow_html=True)
st.markdown(team_style, unsafe_allow_html=True)
