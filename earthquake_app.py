import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🌍 Earthquakes This Month")

@st.cache_data(ttl=3600)
def scrape_earthquake_data():
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_csv(url)
        df['time'] = pd.to_datetime(df['time'])
        return df
    else:
        st.error("Failed to fetch earthquake data.")
        return pd.DataFrame()

df = scrape_earthquake_data()

# Filter earthquakes for the current month
now = datetime.now(timezone.utc)
df_month = df[
    (df['time'].dt.month == now.month) & 
    (df['time'].dt.year == now.year)
]

# Select relevant columns only
df_month = df_month[['latitude', 'longitude', 'mag', 'place', 'time']]

# Optional filtering
min_magnitude = st.slider("Minimum magnitude to display", 0.0, 10.0, 3.0, 0.1)
max_points = st.slider("Maximum number of earthquakes to display", 50, 1000, 300)

df_month = df_month[df_month['mag'] >= min_magnitude]
df_month = df_month.head(max_points)

@st.cache_resource(ttl=3600)
def generate_map(df):
    if df.empty:
        return None

    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=2)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup = (
            f"<b>Magnitude:</b> {row['mag']}<br>"
            f"<b>Location:</b> {row['place']}<br>"
            f"<b>Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S')}"
        )
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color='red' if row['mag'] >= 5 else 'blue',
            fill=True,
            fill_opacity=0.6,
            popup=popup
        ).add_to(marker_cluster)

    return m

