
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
def fetch_earthquake_data():
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
    try:
        df = pd.read_csv(url, parse_dates=['time'])
        return df
    except Exception as e:
        st.error(f"Data load failed: {e}")
        return pd.DataFrame()

def build_map(data):
    center = [data['latitude'].mean(), data['longitude'].mean()]
    m = folium.Map(location=center, zoom_start=2)
    cluster = MarkerCluster().add_to(m)

    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color='red' if row['mag'] >= 5 else 'blue',
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"<b>Location:</b> {row['place']}<br>"
                f"<b>Magnitude:</b> {row['mag']}<br>"
                f"<b>Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S')}",
                max_width=300
            )
        ).add_to(cluster)

    return m

df_all = fetch_earthquake_data()
now = datetime.now(timezone.utc)

# Lowered threshold to 2.0
df_filtered = df_all[
    (df_all['time'].dt.year == now.year) &
    (df_all['time'].dt.month == now.month) &
    (df_all['mag'] >= 2.0)
].loc[:, ['latitude', 'longitude', 'mag', 'place', 'time']].head(300)

st.info(
    f"This map shows earthquakes (magnitude ≥ 2.0) recorded by the USGS "
    f"during **{now.strftime('%B %Y')}**. Displaying **{len(df_filtered)} events**."
)

with st.spinner("Loading map..."):
    quake_map = build_map(df_filtered)

st_folium(quake_map, width=1000, height=600)
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
def fetch_earthquake_data():
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
    try:
        df = pd.read_csv(url, parse_dates=['time'])
        return df
    except Exception as e:
        st.error(f"Data load failed: {e}")
        return pd.DataFrame()

def build_map(data):
    center = [data['latitude'].mean(), data['longitude'].mean()]
    m = folium.Map(location=center, zoom_start=2)
    cluster = MarkerCluster().add_to(m)

    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color='red' if row['mag'] >= 5 else 'blue',
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"<b>Location:</b> {row['place']}<br>"
                f"<b>Magnitude:</b> {row['mag']}<br>"
                f"<b>Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S')}",
                max_width=300
            )
        ).add_to(cluster)

    return m

df_all = fetch_earthquake_data()
now = datetime.now(timezone.utc)

# Lowered threshold to 2.0
df_filtered = df_all[
    (df_all['time'].dt.year == now.year) &
    (df_all['time'].dt.month == now.month) &
    (df_all['mag'] >= 2.0)
].loc[:, ['latitude', 'longitude', 'mag', 'place', 'time']].head(300)

st.info(
    f"This map shows earthquakes (magnitude ≥ 2.0) recorded by the USGS "
    f"during **{now.strftime('%B %Y')}**. Displaying **{len(df_filtered)} events**."
)

with st.spinner("Loading map..."):
    quake_map = build_map(df_filtered)

st_folium(quake_map, width=1000, height=600)

