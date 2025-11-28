import streamlit as st
import os
import json

# 1. Page Setup
st.set_page_config(page_title="Smog Assassin", layout="wide")
st.title("🛰️ Sentinel-5P Smog Monitor")

# 2. Authentication (The Priority Task)
# We do this BEFORE importing geemap to prevent early connection errors
try:
    # Get token from secrets
    if "earth_engine" in st.secrets:
        ee_token = st.secrets["earth_engine"]["token"]
    else:
        st.error("❌ Secrets not found.")
        st.stop()
    
    # Write the token to the disk
    # GEE looks for this specific path
    credentials_path = os.path.expanduser("~/.config/earthengine/")
    os.makedirs(credentials_path, exist_ok=True)
    json_token = json.loads(ee_token) # Parse to ensure valid JSON
    
    # Write the file
    with open(os.path.join(credentials_path, "credentials"), "w") as f:
        f.write(json.dumps(json_token)) # Write clean JSON
    
    # NOW we import Earth Engine and Initialize
    import ee
    
    # Initialize with the specific project ID found in your token
    # This prevents the "Project not found" error
    project_id = json_token.get("project", "ist-research-2025")
    ee.Initialize(project=project_id)
    
except Exception as e:
    st.error(f"❌ Authentication Error: {e}")
    st.stop()

# 3. Import Geemap (ONLY AFTER AUTH IS DONE)
import geemap.foliumap as geemap

# 4. The Controls
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

# 5. The Map
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
    st.write("---")
    st.write("### How to fix:")
    st.write("If the token preview above looks wrong, go back to Secrets and fix it.")
    st.write("Try using triple quotes in Secrets like this:")
    st.code("[earth_engine]\ntoken = '''PASTE_TOKEN_HERE'''")
