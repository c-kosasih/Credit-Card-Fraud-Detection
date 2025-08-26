import streamlit as st
import requests
import time
from datetime import datetime

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Fraud Dashboard", layout="wide")
st.title("📊 Fraud Detection Live Dashboard")

# CSS
st.markdown("""
<style>
    .fraud-alert {
        background-color: #ff4b4b;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .not-fraud {
        background-color: #4caf50;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        color: black;
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

placeholder = st.empty()

# Refresh every 10 seconds
while True:
    # Try to trigger new prediction
    try:
        response = requests.post(f"{API}/predict-latest", timeout=10)
    except Exception as e:
        placeholder.error(f"🔌 API connection error: {e}")
        time.sleep(5)
        continue

    # Get latest prediction
    try:
        res = requests.get(f"{API}/latest-prediction", timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data and data.get("prediction") is not None:
                prediction = data.get("prediction", "-")
                
                with placeholder.container():
                    # Header with colored alert
                    if prediction == 1:
                        st.markdown('<div class="fraud-alert"><h2>🚨 FRAUD DETECTED 🚨</h2></div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="not-fraud"><h2>✅ TRANSACTION LEGITIMATE</h2></div>', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.subheader("📋 Transaction Details")
                        st.markdown(f'<div class="metric-card">'
                                    f'<b>Merchant:</b> {data.get("merchant", "N/A")}<br>'
                                    f'<b>Category:</b> {data.get("category", "N/A")}<br>'
                                    f'<b>Amount:</b> ${data.get("amt", 0):.2f}<br>'
                                    f'<b>Transaction ID:</b> {data.get("trans_num", "N/A")}'
                                    f'</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("📍 Location")
                        st.markdown(f'<div class="metric-card">'
                                    f'<b>City:</b> {data.get("city", "N/A")}<br>'
                                    f'<b>State:</b> {data.get("state", "N/A")}<br>'
                                    f'<b>ZIP:</b> {data.get("zip", "N/A")}<br>'
                                    f'<b>Coordinates:</b> {data.get("lat", "N/A")}, {data.get("long", "N/A")}'
                                    f'</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.subheader("👤 Customer Info")
                        st.markdown(f'<div class="metric-card">'
                                    f'<b>Name:</b> {data.get("first", "N/A")} {data.get("last", "N/A")}<br>'
                                    f'<b>Gender:</b> {data.get("gender", "N/A")}<br>'
                                    f'<b>Occupation:</b> {data.get("job", "N/A")}<br>'
                                    f'<b>Prediction ID:</b> {data.get("id", "N/A")}'
                                    f'</div>', unsafe_allow_html=True)
                    
                    # Prediction confidence (if available)
                    if prediction == 1:
                        st.warning("⚠️ This transaction has been flagged as potentially fraudulent. Please review immediately.")
                    else:
                        st.success("✓ This transaction appears to be legitimate.")
                    
                    # Timestamp
                    if data.get("created_at"):
                        st.caption(f"🕒 Last prediction: {data.get('created_at')}")
                        
            else:
                placeholder.info("⏳ Waiting for new transactions... Insert data into MySQL database to see predictions.")
        else:
            placeholder.warning("⚠️ API temporarily unavailable. Checking again in 10 seconds...")
    except Exception as e:
        placeholder.error(f"❌ Error fetching prediction: {e}")

    time.sleep(10)

# streamlit run dashboard.py