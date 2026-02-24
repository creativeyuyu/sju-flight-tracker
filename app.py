import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="SJU Live Tracker", layout="wide")

st.title("✈️ San Juan Live Air Traffic")
st.write("Tracking Luis Muñoz Marín (SJU) and Isla Grande (SIG)")

# Sidebar for Filters
st.sidebar.header("Filter Traffic")
show_jetblue = st.sidebar.checkbox("Highlight JetBlue (B6/JBU)", value=True)

# 1. Fetch Data
SJU_BBOX = {'lamin': 18.0, 'lomin': -67.0, 'lamax': 18.8, 'lomax': -65.5}
url = 'https://opensky-network.org/api/states/all'
res = requests.get(url, params=SJU_BBOX).json()

# 2. Process into a DataFrame
columns = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 
           'long', 'lat', 'baro_altitude', 'on_ground', 'velocity', 'true_track']
df = pd.DataFrame(res['states'], columns=columns + [None]*(len(res['states'][0])-len(columns)))
df['callsign'] = df['callsign'].str.strip()

# 3. Create the Map
m = folium.Map(location=[18.45, -66.1], zoom_start=9, tiles="CartoDB dark_matter")

for _, row in df.iterrows():
    color = "blue" if "JBU" in row['callsign'] else "white"
    if show_jetblue and "JBU" not in row['callsign']:
        continue
        
    folium.Marker(
        [row['lat'], row['long']],
        popup=f"Flight: {row['callsign']}\nAlt: {row['baro_altitude']}m",
        icon=folium.Icon(color=color, icon="plane")
    ).add_to(m)

# 4. Display Dashboard
col1, col2 = st.columns([3, 1])

with col1:
    st_folium(m, width=900, height=500)

with col2:
    st.subheader("Active Flights")
    st.dataframe(df[['callsign', 'baro_altitude', 'velocity']].dropna())

st.info("Data provided by OpenSky Network. Refresh page to update positions.")
