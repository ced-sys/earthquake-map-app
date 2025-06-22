import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Earthquakes this Month")

@st.cache_data(ttl=3600)
def scrape_earthquake_data():
    url='https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
    response=requests.get(url)
    if response.status_code==200:
        df=pd.read_csv(url)
        df['time']=pd.to_datetime(df['time'])
        return df
    else:
        st.error("Failed to fetch earthquake data.")
        return pd.DataFrame()

df=scrape_earthquake_data()

now=datetime.now(timezone.utc)
df_month=df[(df['time'].dt.month==now.month) & (df['time'].dt.year==now.year)]

if df_month.empty:
    st.warning("No Earthquake data available for this month yet")
else:
    st.success(f"Showing {len(df_month)} earthquakes from {now.strftime('%B %Y')}")

    m=folium.Map(location=[df_month['latitude'].mean(), df_month['longitude'].mean()], zoom_start=2)
    marker_cluster=MarkerCluster().add_to(m)

    for _, row in df_month.iterrows():
        popup_info=(
                f"<b>Magnitude:</b> {row['mag']}<br>"
                f"<b>Location:</b> {row['place']}<br>"
                f"<b>Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S')}"
                )
        folium.Marker(
                location=[row['latitude'], row['longitude']], 
                popup=popup_info,
                icon=folium.Icon(color='red' if row['mag'] >= 5 else 'blue')
        ).add_to(marker_cluster)

    st_folium(m, width=1000, height=600)
