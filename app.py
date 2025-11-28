import streamlit as st
import ee
import os

st.set_page_config(page_title="Smog Debugger", layout="wide")
st.title("🕵️ Smog Assassin: Debug Mode")

# 1. Debugging Secrets
st.subheader("Step 1: Checking Secrets")
if "earth_engine" in st.secrets and "token" in st.secrets["earth_engine"]:
    token = st.secrets["earth_engine"]["token"]
    st.success("✅ Token found in Secrets!")
    st.write(f"Token length: {len(token)} characters")
    st.write(f"Token preview: `{token[:20]}...`")
    
    # Check for newlines which break things
    if "\n" in token:
        st.warning("⚠️ Warning: Your token has hidden 'Enter' (newline) characters. This might break it.")
else:
    st.error("❌ Token NOT found in Secrets. Check your spelling.")
    st.stop()

# 2. Writing the File
st.subheader("Step 2: Writing Credentials File")
try:
    # Force the path to the home directory
    home_dir = os.path.expanduser("~")
    cred_path = os.path.join(home_dir, ".config", "earthengine", "credentials")
    
    st.write(f"Target Path: `{cred_path}`")
    
    # Create directory
    os.makedirs(os.path.dirname(cred_path), exist_ok=True)
    
    # Write file
    with open(cred_path, "w") as f:
        f.write(token)
        
    st.success("✅ File written successfully.")
    
    # Verify file exists
    if os.path.exists(cred_path):
        st.info(f"File verified on disk. Size: {os.path.getsize(cred_path)} bytes")
    else:
        st.error("❌ File write failed silently.")
        
except Exception as e:
    st.error(f"❌ File Error: {e}")
    st.stop()

# 3. Initializing Earth Engine
st.subheader("Step 3: Waking up Satellite")
try:
    ee.Initialize()
    st.success("🎉 SUCCESS! Connected to Earth Engine.")
    st.balloons()
except Exception as e:
    st.error(f"❌ Connection Failed: {e}")
    st.write("---")
    st.write("### How to fix:")
    st.write("If the token preview above looks wrong, go back to Secrets and fix it.")
    st.write("Try using triple quotes in Secrets like this:")
    st.code("[earth_engine]\ntoken = '''PASTE_TOKEN_HERE'''")
