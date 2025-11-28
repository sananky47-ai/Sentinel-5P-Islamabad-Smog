import streamlit as st
import geemap.foliumap as geemap
import ee
import os

# 1. Page Setup
st.set_page_config(page_title="Smog Assassin", layout="wide")
st.title("🛰️ Sentinel-5P Smog Monitor")

# 2. Authentication (Loud Debugging Version)
try:
    # Check if secrets exist
    if "earth_engine" not in st.secrets:
        st.error("❌ Error: The '[earth_engine]' section is missing from Secrets.")
        st.stop()
        
    if "token" not in st.secrets["earth_engine"]:
        st.error("❌ Error: The 'token' key is missing. Did you misspell it?")
        st.stop()
    
    # Get the token
    ee_token = st.secrets["earth_engine"]["token"]
    
    # Write it to disk
    credentials_path = os.path.expanduser("~/.config/earthengine/")
    os.makedirs(credentials_path, exist_ok=True)
    with open(os.path.join(credentials_path, "credentials"), "w") as f:
        f.write(ee_token)
        
    # Initialize
    ee.Initialize(project='ist-research-2025')
    
except Exception as e:
    # THIS is what we need to see
    st.error(f"❌ CRITICAL FAILURE: {e}")
    st.stop()
# 3. The Controls
with st.sidebar:
    st.header("Control Panel")
    city = st.selectbox("Choose Target:", ["Islamabad (IST)", "Lahore", "Karachi"])
    
    if city == "Islamabad (IST)":
        coords = [33.5194, 73.1709]
        zoom = 10
    elif city == "Lahore":
        coords = [31.5204, 74.3587]
        zoom = 10
    elif city == "Karachi":
        coords = [24.8607, 67.0011]
        zoom = 10

# 4. The Map
st.subheader(f"Live Pollution Map: {city}")
m = geemap.Map(center=coords, zoom=zoom)
col = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2') \
    .select('tropospheric_NO2_column_number_density') \
    .filterDate('2025-11-01', '2025-11-24') \
    .mean()

vis = {'min': 0, 'max': 0.0002, 'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']}
m.addLayer(col, vis, "NO2 Levels")
m.to_streamlit(height=500)
