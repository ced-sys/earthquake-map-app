import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Earthquake Tracker",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Earthquake Tracker")
st.markdown("Real-time earthquake data from the USGS Earthquake Hazards Program")

@st.cache_data(ttl=3600)
def fetch_earthquake_data():
    """Fetch earthquake data from USGS API"""
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
    try:
        df = pd.read_csv(url, parse_dates=['time'])
        return df
    except Exception as e:
        st.error(f"Failed to load earthquake data: {e}")
        return pd.DataFrame()

def get_magnitude_color(magnitude):
    """Return color based on earthquake magnitude"""
    if magnitude >= 7.0:
        return 'darkred'
    elif magnitude >= 6.0:
        return 'red'
    elif magnitude >= 5.0:
        return 'orange'
    elif magnitude >= 4.0:
        return 'yellow'
    elif magnitude >= 3.0:
        return 'green'
    else:
        return 'lightblue'

def get_magnitude_size(magnitude):
    """Return marker size based on earthquake magnitude"""
    return max(3, min(20, magnitude * 3))

def build_map(data, map_type="cluster"):
    """Build earthquake map with different visualization options"""
    if data.empty:
        return folium.Map(location=[0, 0], zoom_start=2)
    
    center = [data['latitude'].mean(), data['longitude'].mean()]
    m = folium.Map(location=center, zoom_start=2, tiles='OpenStreetMap')
    
    if map_type == "cluster":
        cluster = MarkerCluster().add_to(m)
        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=get_magnitude_size(row['mag']),
                color=get_magnitude_color(row['mag']),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"<b>Location:</b> {row['place']}<br>"
                    f"<b>Magnitude:</b> {row['mag']}<br>"
                    f"<b>Depth:</b> {row.get('depth', 'N/A')} km<br>"
                    f"<b>Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S UTC')}",
                    max_width=300
                )
            ).add_to(cluster)
    
    elif map_type == "heatmap":
        heat_data = [[row['latitude'], row['longitude'], row['mag']] for _, row in data.iterrows()]
        HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
    
    else:  # individual markers
        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=get_magnitude_size(row['mag']),
                color=get_magnitude_color(row['mag']),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"<b>Location:</b> {row['place']}<br>"
                    f"<b>Magnitude:</b> {row['mag']}<br>"
                    f"<b>Depth:</b> {row.get('depth', 'N/A')} km<br>"
                    f"<b>Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S UTC')}",
                    max_width=300
                )
            ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Magnitude Scale</b></p>
    <p><i class="fa fa-circle" style="color:darkred"></i> ≥ 7.0 Major</p>
    <p><i class="fa fa-circle" style="color:red"></i> 6.0-6.9 Strong</p>
    <p><i class="fa fa-circle" style="color:orange"></i> 5.0-5.9 Moderate</p>
    <p><i class="fa fa-circle" style="color:yellow"></i> 4.0-4.9 Light</p>
    <p><i class="fa fa-circle" style="color:green"></i> 3.0-3.9 Minor</p>
    <p><i class="fa fa-circle" style="color:lightblue"></i> < 3.0 Micro</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_magnitude_histogram(data):
    """Create histogram of earthquake magnitudes"""
    fig = px.histogram(
        data, 
        x='mag', 
        nbins=30,
        title='Distribution of Earthquake Magnitudes',
        labels={'mag': 'Magnitude', 'count': 'Number of Earthquakes'},
        color_discrete_sequence=['#FF6B6B']
    )
    fig.update_layout(height=400)
    return fig

def create_timeline_chart(data):
    """Create timeline of earthquakes"""
    daily_counts = data.groupby(data['time'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']
    
    fig = px.line(
        daily_counts, 
        x='date', 
        y='count',
        title='Daily Earthquake Activity',
        labels={'date': 'Date', 'count': 'Number of Earthquakes'}
    )
    fig.update_layout(height=400)
    return fig

# Main app
df_all = fetch_earthquake_data()

if not df_all.empty:
    now = datetime.now(timezone.utc)
    
    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    
    min_magnitude = st.sidebar.slider(
        "Minimum Magnitude", 
        min_value=0.0, 
        max_value=9.0, 
        value=2.0, 
        step=0.1,
        key="slider_min_mag"
    )
    
    max_events = st.sidebar.slider(
        "Maximum Events to Display", 
        min_value=50, 
        max_value=1000, 
        value=300, 
        step=50,
        key="slider_max_events"
    )
    
    map_type = st.sidebar.selectbox(
        "Map Visualization",
        ["cluster", "heatmap", "individual"],
        index=0,
        key="map_type_selector"
    )
    
    # Filter data
    df_filtered = df_all[
        (df_all['time'].dt.year == now.year) &
        (df_all['time'].dt.month == now.month) &
        (df_all['mag'] >= min_magnitude)
    ].head(max_events)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Earthquakes", len(df_filtered))
    
    with col2:
        max_mag = df_filtered['mag'].max() if not df_filtered.empty else 0
        st.metric("Largest Magnitude", f"{max_mag:.1f}")
    
    with col3:
        major_count = len(df_filtered[df_filtered['mag'] >= 5.0])
        st.metric("Major Earthquakes (≥5.0)", major_count)
    
    with col4:
        if not df_filtered.empty:
            avg_depth = df_filtered['depth'].mean() if 'depth' in df_filtered.columns else 0
            st.metric("Avg Depth", f"{avg_depth:.1f} km")
        else:
            st.metric("Avg Depth", "N/A")
    
    # Info message
    st.info(
        f"📊 Showing earthquakes (magnitude ≥ {min_magnitude}) recorded during "
        f"**{now.strftime('%B %Y')}**. Displaying **{len(df_filtered)}** events."
    )
    
    # Main map
    with st.spinner("🗺️ Loading earthquake map..."):
        quake_map = build_map(df_filtered, map_type)
    
    st_folium(quake_map, width=1000, height=600)
    
    # Charts section
    if not df_filtered.empty:
        st.header("📈 Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hist_fig = create_magnitude_histogram(df_filtered)
            st.plotly_chart(hist_fig, use_container_width=True)
        
        with col2:
            timeline_fig = create_timeline_chart(df_filtered)
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        # Recent earthquakes table
        st.header("🕐 Recent Earthquakes")
        recent_quakes = df_filtered.nlargest(10, 'time')[
            ['time', 'place', 'mag', 'depth']
        ].copy()
        recent_quakes['time'] = recent_quakes['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(recent_quakes, use_container_width=True)

else:
    st.error("Unable to load earthquake data. Please try again later.")

# Footer
st.markdown("---")
st.markdown(
    "**Data Source:** [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/) | "
    "**Updates:** Every hour | **Time Zone:** UTC"
)
