import streamlit as st
import pandas as pd
import requests
import time
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

# Filter for this month
now = datetime.now(timezone.utc)
df_month = df[
    (df['time'].dt.month == now.month) & 
    (df['time'].dt.year == now.year)
]

# Keep only necessary columns
df_month = df_month[['latitude', 'longitude', 'mag', 'place', 'time']]

# Optional: filter to show only relevant events (e.g., mag ≥ 3) and limit to 300 for performance
df_month = df_month[df_month['mag'] >= 3.0]
df_month = df_month.head(300)

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
#Render the map unconditionally wit loading UI
with st.spinner("Generating map...please wait"):
    progress=st.progress(0)
    for i in range(1, 6):
        time.sleep(0.1)
        progress.progress(i*20)
    m=generate_map(df_month)
    progress.empty()

st_folium(m, width=1000, height=600)


