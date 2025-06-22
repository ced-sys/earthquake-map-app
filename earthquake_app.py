

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Earthquakes This Month")

@st.cache_data(ttl=3600)
def load_earthquake_data():
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
    try:
        df = pd.read_csv(url)
        df['time'] = pd.to_datetime(df['time'])
        return df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

def generate_map(df):
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=2)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup_html = folium.Popup(
            html=f"""
                <b>Location:</b> {row['place']}<br>
                <b>Magnitude:</b> {row['mag']}<br>
                <b>Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S')}
            """,
            max_width=300
        )
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color='red' if row['mag'] >= 5 else 'blue',
            fill=True,
            fill_opacity=0.7,
            popup=popup_html
        ).add_to(marker_cluster)

    return m

# Load and filter data
df = load_earthquake_data()

now = datetime.now(timezone.utc)
df_month = df[
    (df['time'].dt.month == now.month) &
    (df['time'].dt.year == now.year)
]

df_month = df_month[['latitude', 'longitude', 'mag', 'place', 'time']]
df_month = df_month[df_month['mag'] >= 3.0].head(300)

# Show info box — this gives context for "why" the app exists
st.info(
    f"This map shows earthquakes with magnitude ≥ 3.0 recorded by the USGS "
    f"during **{now.strftime('%B %Y')}**. Currently displaying **{len(df_month)} earthquakes**."
)

# Loading message
with st.spinner("Loading interactive map..."):
    m = generate_map(df_month)

# Display the map always
st_folium(m, width=1000, height=600)

