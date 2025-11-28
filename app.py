import streamlit as st
import geemap.foliumap as geemap
import ee
import json
from google.oauth2.credentials import Credentials

# 1. Page Setup
st.set_page_config(page_title="Smog Assassin", layout="wide")
st.title("🛰️ Sentinel-5P Smog Monitor")

# 2. Authentication (Surgical Scope Fix)
try:
    if "earth_engine" in st.secrets:
        token_str = st.secrets["earth_engine"]["token"]
    else:
        st.error("❌ Secrets not found.")
        st.stop()
    
    # Parse the token
    token_info = json.loads(token_str)
    
    # --- SURGERY START ---
    # We force the scopes to be ONLY Earth Engine.
    # This fixes the "Invalid Scope" error by removing Drive/Cloud storage junk.
    token_info['scopes'] = ['https://www.googleapis.com/auth/earthengine.readonly']
    # --- SURGERY END ---
    
    # Create Credentials
    creds = Credentials.from_authorized_user_info(token_info)
    
    # Initialize
    ee.Initialize(credentials=creds)
    
except Exception as e:
    st.error(f"❌ Authentication Failed: {e}")
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

try:
    m = geemap.Map(center=coords, zoom=zoom)
    
    # Get Data (Last 30 Days)
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
    st.error(f"Map Error: {e}")
    
    m.addLayer(col, vis, "NO2 Levels")
    m.to_streamlit(height=600)
    
except Exception as e:
    st.error(f"Map Error: {e}")
