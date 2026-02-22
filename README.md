# Weather DJ

Weather DJ is an interactive Streamlit web application that personalize Spotify songs based on the current weather in your city.

## Features

Enter your city to fetch real-time weather data and temperatures using the OpenWeather API.
Custom animated CSS weather widgets (pulsing sun, falling snow, rain clouds).
Direct links to play the tracks on Spotify.

## Prerequisites

You will  need to create free accounts to generate API keys for both Spotify and OpenWeather.
In your project's root directory, create a .streamlit folder, and inside it, create a secrets.toml file. 

Add your API keys to the secrets.toml file like this:

OPENWEATHER_API_KEY = "your_openweather_api_key"
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
