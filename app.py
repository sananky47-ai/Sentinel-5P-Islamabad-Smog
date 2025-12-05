import streamlit as st
import geemap.foliumap as geemap
import ee
import json
import os
from google.oauth2.credentials import Credentials

st.set_page_config(page_title="Smog Assassin: AI Sentinel", layout="wide")

# --- THE PITCH ---
st.title("🛰️ Sentinel-5P: Autonomous Smog Warning System")
st.markdown("**Phase 1 Prototype:** Simulating On-board Satellite Logic for Real-time Alerts.")

# --- AUTHENTICATION (The Exorcism Fix) ---
try:
    # 1. Reset any previous connections
    ee.Reset()
    
    # 2. Force Environment Variables
    os.environ['GOOGLE_CLOUD_PROJECT'] = '339680349370'
    os.environ['EARTHENGINE_PROJECT'] = '339680349370'
    
    if "earth_engine" in st.secrets:
        token_str = st.secrets["earth_engine"]["token"]
    else:
        st.error("❌ Secrets not found.")
        st.stop()
    
    # 3. Parse and SURGICALLY MODIFY the Token
    token_info = json.loads(token_str)
    
    # Force the Project ID inside the token data
    # This overwrites 'ee-sananky47' if it exists in the hidden metadata
    token_info['project_id'] = '339680349370'
    token_info['project'] = '339680349370'
    token_info['quota_project_id'] = '339680349370'
    
    # Fix scopes
    token_info['scopes'] = ['https://www.googleapis.com/auth/earthengine.readonly']
    
    # 4. Create Credentials from the Cleaned Data
    creds = Credentials.from_authorized_user_info(token_info)
    
    # 5. Initialize
    ee.Initialize(credentials=creds, project='339680349370')
    
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.write("Tip: If this persists, your Token might need to be regenerated in Colab.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Mission Control")
    city = st.selectbox("Target Sector:", ["Islamabad (IST)", "Lahore", "Karachi"])
    
    if city == "Islamabad (IST)":
        coords = [33.5194, 73.1709]
        zoom = 11
    elif city == "Lahore":
        coords = [31.5204, 74.3587]
        zoom = 11
    elif city == "Karachi":
        coords = [24.8607, 67.0011]
        zoom = 11

# --- THE SMART LOGIC ---
try:
    col = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2') \
        .select('tropospheric_NO2_column_number_density') \
        .filterDate('2025-11-01', '2025-11-25')

    point = ee.Geometry.Point([coords[1], coords[0]])
    roi = point.buffer(10000) 

    mean_img = col.mean()
    
    # We use a try-catch for the calculation to prevent full crash on empty data
    try:
        stats = mean_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=1000
        ).getInfo()
        no2_value = stats.get('tropospheric_NO2_column_number_density')
    except:
        no2_value = None

    # --- DASHBOARD ---
    col1, col2, col3 = st.columns(3)

    if no2_value:
        val = float(no2_value)
        col1.metric("NO2 Concentration", f"{val:.5f} mol/m²")
        
        limit = 0.00010 
        
        if val > limit:
            col2.error("🚨 STATUS: CRITICAL SMOG")
            col3.markdown("⚠️ **Action Required:** \nRecommend Mask Mandate & Traffic Reduction.")
        else:
            col2.success("✅ STATUS: SAFE")
            col3.markdown("No restrictions needed.")
    else:
        col1.metric("NO2 Concentration", "No Data")
        col2.warning("Status: Unknown")

    # --- MAP ---
    m = geemap.Map(center=coords, zoom=zoom)
    vis = {'min': 0, 'max': 0.0002, 'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']}
    m.addLayer(mean_img, vis, "NO2 Heatmap")
    m.addLayer(roi, {'color': 'white'}, "Monitoring Zone")
    m.to_streamlit(height=500)

except Exception as e:
    st.error(f"Map Error: {e}")
