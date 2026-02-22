import streamlit as st
import requests
import base64
import random
 
try:
    OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
    SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
except FileNotFoundError:
    st.error("Secrets file not found. Please set up your API keys.")
    st.stop()
    
#  Authentication
@st.cache_resource(ttl=3500)
def get_spotify_token():
    if "YOUR_SPOTIFY" in SPOTIFY_CLIENT_ID: return None
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, headers=headers, data={"grant_type": "client_credentials"}, timeout=10)
        return response.json().get('access_token') if response.status_code == 200 else None
    except: return None

# Functions
def get_weather_data(city_name):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            cond = data['weather'][0]['main']
            conditions = {
                "Rain": "Rainy", "Drizzle": "Rainy", "Thunderstorm": "Rainy",
                "Snow": "Snowy", "Clear": "Sunny"
            }
            return temp, conditions.get(cond, "Cloudy")
        return None, None
    except: return None, None

def get_genres_for_weather(weather_condition):
    map = {
        "Sunny": ["pop", "dance", "reggae","acoustic"],
        "Rainy": ["acoustic", "piano", "chill", "sleep"],
        "Snowy": ["jazz", "classical", "chill", "sleep"],
        "Cloudy": ["indie", "pop", "study", "lo-fi"]
    }
    return map.get(weather_condition, ["pop", "rock", "indie"])

def fetch_tracks(token, genre):
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = "https://api.spotify.com/v1/search"
    params = {"q": f"genre:{genre}", "type": "track", "limit": 20, "market": "US"}
    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            raw_tracks = response.json().get("tracks", {}).get("items", [])
            parsed_tracks = []
            for t in raw_tracks:
                album = t.get("album", {})
                parsed_tracks.append({
                    "id": t.get("id"),
                    "Genre": genre, 
                    "Track": t.get("name"),
                    "Artist": t.get("artists", [{}])[0].get("name", "Unknown"),
                    "Cover": album.get("images", [{}])[0].get("url"),
                    "Link": t.get("external_urls", {}).get("spotify")
                })
            return parsed_tracks
    except:
        return []
    return []

# UI
def display_scrolling_ticker(genres):
    unique_genres = list(set(genres)) 
    if not unique_genres: unique_genres = ["Music", "Vibes"]
    genre_str = "   •   ".join([str(g).upper() for g in unique_genres] * 5)
    
    html_code = f"""
    <style>
    .ticker-wrap {{
        width: 100%; overflow: hidden; background-color: #1DB954; color: white;
        padding: 8px 0; margin-bottom: 15px; border-radius: 8px; white-space: nowrap;
    }}
    .ticker {{ display: inline-block; animation: ticker 30s linear infinite; }}
    @keyframes ticker {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-50%, 0, 0); }} }}
    .ticker-item {{ display: inline-block; padding: 0 2rem; font-family: sans-serif; font-weight: bold; }}
    </style>
    <div class="ticker-wrap"><div class="ticker"><div class="ticker-item">{genre_str}</div><div class="ticker-item">{genre_str}</div><div class="ticker-item">{genre_str}</div><div class="ticker-item">{genre_str}</div></div></div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

def display_weather_widget(weather_condition):
    css_styles = """
    <style>
        /* Container Style */
        .weather-widget-container {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            color: #333;
            font-family: sans-serif;
        }

        /* SUNNY ICON */
        .sun {
            width: 80px; height: 80px;
            background: #FFD700;
            border-radius: 50%;
            box-shadow: 0 0 40px #FFD700;
            margin: 0 auto 10px auto;
            animation: sun-pulse 2s infinite alternate;
        }
        @keyframes sun-pulse { 0% { transform: scale(1); } 100% { transform: scale(1.1); } }

        /* CLOUDY ICON */
        .cloud-container { position: relative; height: 80px; width: 100px; margin: 0 auto; }
        .cloud {
            width: 100px; height: 40px;
            background: #fff;
            border-radius: 20px;
            position: absolute; top: 40px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .cloud::after {
            content: ""; position: absolute;
            width: 50px; height: 50px;
            background: #fff; border-radius: 50%;
            top: -25px; left: 15px;
        }
        .cloud::before {
            content: ""; position: absolute;
            width: 40px; height: 40px;
            background: #fff; border-radius: 50%;
            top: -15px; left: 50px;
        }

        /* RAINY ICON */
        .rain-container { position: relative; height: 80px; width: 100px; margin: 0 auto; }
        .rain-cloud {
            width: 100px; height: 40px;
            background: #7f8c8d;
            border-radius: 20px;
            position: absolute; top: 30px;
        }
        .rain-cloud::after {
            content: ""; position: absolute;
            width: 50px; height: 50px;
            background: #7f8c8d; border-radius: 50%;
            top: -25px; left: 15px;
        }
        .drop {
            width: 4px; height: 10px;
            background: #3498db;
            position: absolute;
            bottom: -20px;
            animation: rain-drop 1s infinite linear;
        }
        @keyframes rain-drop { 0% { transform: translateY(0); opacity: 1; } 100% { transform: translateY(20px); opacity: 0; } }

        /* SNOWY ICON */
        .snow-container { position: relative; height: 80px; width: 100px; margin: 0 auto; }
        .flake {
            color: white; font-size: 20px; position: absolute; top: 50px;
            animation: snow-fall 3s infinite linear;
        }
        @keyframes snow-fall { 0% { transform: translateY(0); opacity: 1; } 100% { transform: translateY(30px); opacity: 0; } }
    </style>
    """

    icons = {
        "Sunny": """
            <div class="sun"></div>
            <h3>Sunny</h3>
        """,
        "Cloudy": """
            <div class="cloud-container"><div class="cloud"></div></div>
            <h3>Cloudy</h3>
        """,
        "Rainy": """
            <div class="rain-container">
                <div class="rain-cloud"></div>
                <div class="drop" style="left: 20px; animation-delay: 0s;"></div>
                <div class="drop" style="left: 50px; animation-delay: 0.5s;"></div>
                <div class="drop" style="left: 80px; animation-delay: 0.2s;"></div>
            </div>
            <h3>Rainy</h3>
        """,
        "Snowy": """
            <div class="snow-container">
                <div class="rain-cloud" style="background: #bdc3c7;"></div>
                <div class="flake" style="left: 20px; animation-delay: 0s;">❄</div>
                <div class="flake" style="left: 50px; animation-delay: 1.5s;">❄</div>
                <div class="flake" style="left: 80px; animation-delay: 0.8s;">❄</div>
            </div>
            <h3>Snowy</h3>
        """
    }


    content = icons.get(weather_condition, icons["Cloudy"])
    

    st.markdown(f"{css_styles}<div class='weather-widget-container'>{content}</div>", unsafe_allow_html=True)

# App
st.set_page_config(page_title="Weather DJ", page_icon="🎧", layout="wide")


if 'city_name' not in st.session_state:
    st.session_state['city_name'] = "Simulator Mode"


if st.session_state.get("source_mode") == "Simulator":
    display_title = "🎧 Weather DJ • Simulator Mode"
elif "city_name" in st.session_state:
    display_title = f"🎧 Weather DJ • {st.session_state['city_name']}"
else:
    display_title = "🎧 Weather DJ"

st.title(display_title)

# Sidebar
with st.sidebar:
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg", width=50)
    
    st.header("🎛️ Control Center")

    mode = st.radio("Source", ["Simulator", "Live Weather"], horizontal=True, key="source_mode")
    
    if mode == "Live Weather":
        city = st.text_input("City", "Barcelona")
        if st.button("Weather Scan"):
            with st.spinner("Triangulating satellites..."):
                t, c = get_weather_data(city)
                if c: 
                    st.session_state['weather'] = (t, c)
                    st.session_state['city_name'] = city.title()
                    
                    keys_to_clear = ['active_playlist', 'reserve_playlist', 'current_genre']
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun() 
                  
    
    else: 
        st.session_state['city_name'] = "Simulator Mode"
        sky = st.selectbox("Sky", ["Sunny", "Cloudy", "Rainy", "Snowy"])
        temp = st.slider("Temp", -10, 40, 22)
        
        new_weather = (temp, sky)
        if 'weather' in st.session_state and st.session_state['weather'] != new_weather:
             
             if 'active_playlist' in st.session_state: del st.session_state['active_playlist']
             if 'current_genre' in st.session_state: del st.session_state['current_genre']
        
        st.session_state['weather'] = new_weather

# Main Logic
if 'weather' in st.session_state:
    temp, sky = st.session_state['weather']
    available_genres = get_genres_for_weather(sky)
    
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
       
        display_weather_widget(sky)
        
        st.markdown(f"<h1 style='text-align: center; margin-top: -10px;'>{round(temp)}°C</h1>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("🎵 Select Vibe")
        
        if 'current_genre' not in st.session_state:
            st.session_state['current_genre'] = available_genres[0]
            
        selected_genre = st.radio(
            "Change Genre:", 
            available_genres, 
            index=available_genres.index(st.session_state['current_genre']) if st.session_state['current_genre'] in available_genres else 0
        )
        
        if selected_genre != st.session_state['current_genre']:
            st.session_state['current_genre'] = selected_genre
            if 'active_playlist' in st.session_state: del st.session_state['active_playlist']
            st.rerun()

    with col_right:
        token = get_spotify_token()
        
  
        if 'active_playlist' not in st.session_state and token:
            with st.spinner(f"Mixing {selected_genre} tracks for {sky} weather..."):
                tracks = fetch_tracks(token, selected_genre)
                st.session_state['active_playlist'] = tracks[:5]
                st.session_state['reserve_playlist'] = tracks[5:]
        
        if 'active_playlist' in st.session_state:
            active = st.session_state['active_playlist']
            display_scrolling_ticker([selected_genre])
            
            for i, track in enumerate(active):
                with st.container(border=True):
                    c_img, c_info, c_btn = st.columns([1, 4, 1.5])
                    with c_img: st.image(track['Cover'], width=80)
                    with c_info:
                        st.subheader(track['Track'])
                        st.caption(f"{track['Artist']} • {track['Genre'].title()}")
                        st.markdown(f"[Play on Spotify]({track['Link']})")
                    with c_btn:
                        if st.button("Next 🚫", key=f"swap_{track['id']}"):
                            if st.session_state['reserve_playlist']:
                                new_track = st.session_state['reserve_playlist'].pop(0)
                                st.session_state['active_playlist'][i] = new_track
                                st.rerun()
                            else:
                                st.warning("No more songs in reserve!")
        else:
             st.info("Waiting for Spotify connection...")

else:
    st.info("👈 Set weather to begin.")