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
            st.markdown(f'<style>{keyframes}</style>'f'<a href="{spotify_url}" target="_blank" style="{link_style}"> <img src="https://cdn3.emoji.gg/emojis/SpotifyLogo.png" width="64px" height="64px" alt="SpotifyLogo"> 🎵 Listen on Spotify 🎵</a></br>',unsafe_allow_html=True)
            
    
    
    logging.info("Successfully show user enter movie with information")
    
    #Recommended Songs
st.markdown(f'<h1 style="{title_style}">Recommended Songs</h1></br>', unsafe_allow_html=True)

# Display recommended songs with hover buttons
for i in range(1, 11):
    with st.expander(names[i]):
        # Add hover effect with button
        st.markdown(
            f'<div class="hover-container" style="position: relative;">'
            f'<img src="{posters[i]}" style="border-radius: 10px; width:250px;box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.2);">'
            f'<button class="hover-button" onclick="showModal(\'{names[i]}\')">Show Info</button>'
            f'</div>',
            unsafe_allow_html=True
        )

# JavaScript for hover effect and modal
st.markdown("""
    <style>
        .hover-button {
            opacity: 0;
            transition: opacity 0.3s ease;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .hover-container:hover .hover-button {
            opacity: 1;
        }
    </style>
    <script>
        function showModal(songName) {
            alert("Display modal for " + songName); // Replace this with your modal implementation
        }
    </script>
""", unsafe_allow_html=True)




##Team Name 
st.write('</br></br><div class="footer" style="text-align:center;padding-top: 25px; font-size: 15px;"><span style="font-size: 25px;color:red;"> </span><span class="ok-text">Made With <span style="color:red;"> &hearts; </span> By Team 200 Ok </span></div>', unsafe_allow_html=True)
st.markdown(team_style, unsafe_allow_html=True)
