import streamlit as st
import geemap.foliumap as geemap
import ee
import os

# 1. Page Setup (Must be the first command)
st.set_page_config(page_title="Smog Assassin", layout="wide")
st.title("🛰️ Sentinel-5P Smog Monitor")

# 2. Authentication (The Fix)
try:
    # Check if secrets exist
    if "earth_engine" not in st.secrets:
        st.error("❌ Error: Secrets not found. Please add [earth_engine] to Secrets.")
        st.stop()
        
    # Get the token
    ee_token = st.secrets["earth_engine"]["token"]
    
    # Write it to the location Earth Engine expects
    # We use os.path.expanduser to ensure it works on Linux servers
    credentials_path = os.path.expanduser("~/.config/earthengine/")
    os.makedirs(credentials_path, exist_ok=True)
    with open(os.path.join(credentials_path, "credentials"), "w") as f:
        f.write(ee_token)
    
    # Initialize without a specific project name
    # The token itself contains the project info ("project": "3396...")
    ee.Initialize()
    
except Exception as e:
    st.error(f"❌ Authentication Failed: {e}")
    st.info("Tip: If the error says 'project not found', your token might be invalid.")
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

# Get Data (Last 30 Days)
# We use a try-except block here too, just in case the satellite data fails
try:
    col = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2') \
        .select('tropospheric_NO2_column_number_density') \
        .filterDate('2025-11-01', '2025-11-25') \
        .mean()

    vis = {
        'min': 0, 
        'max': 0.0002, 
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
    }
    
    m.addLayer(col, vis, "NO2 Levels")
    m.to_streamlit(height=600)

except Exception as e:
    st.error(f"Failed to load map data: {e}")
