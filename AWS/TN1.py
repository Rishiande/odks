import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json
import re
import plotly.graph_objects as go
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import urllib.parse
import pydeck as pdk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time

# --- Streamlit setup ---
st.set_page_config(page_title="TN Master", layout="wide")

# --- Initialize session state ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'otp_sent' not in st.session_state:
    st.session_state['otp_sent'] = False
if 'otp' not in st.session_state:
    st.session_state['otp'] = None
if 'otp_time' not in st.session_state:
    st.session_state['otp_time'] = 0
if 'email' not in st.session_state:
    st.session_state['email'] = ""
if 'attempts' not in st.session_state:
    st.session_state['attempts'] = 0
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"
# Add defaults for dashboard selections
if 'selected_server' not in st.session_state:
    st.session_state['selected_server'] = "Server 1"
if 'selected_project' not in st.session_state:
    st.session_state['selected_project'] = "TN Master"
if 'selected_form' not in st.session_state:
    st.session_state['selected_form'] = "Master Landscape Survey 04-2025 ODK XLSForm"

# --- Email configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "rishiande9999@gmail.com"
EMAIL_PASSWORD = "coveaqwzdhzoqbnw"

# --- Valid credentials ---
VALID_CREDENTIALS = {
    "rishi": {
        "password": "rishi",
        "email": "rishiande9999@gmail.com"
    },
    "Sanjay": {
        "password": "Sanjaysrivastava@123",
        "email": "srisanjay2@gmail.com"
    },
    "Pramanya": {
        "password": "Pramanya@123",
        "email": "pramanyastrategy@gmail.com"
    }
}

# --- Form mappings ---
forms = {
    "Server 1": {
        "TN Master": {
            "Master Landscape Survey 04-2025 ODK XLSForm": {
                "project_id": 3,
                "form_id": "Master Landscape Survey 04-2025 ODK XLSForm"
            }
        },
        "BK TN AC Landscape": {
            "201-Cumbum": {"project_id": 4, "form_id": "201-Cumbum Landscape Survey 04-2025"},
            "39-Sholingur": {"project_id": 4, "form_id": "39-Sholingur Landscape Survey 04-2025"},
            "155-Cuddalore": {"project_id": 4, "form_id": "155-Cuddalore Landscape Survey 04-2025"},
            "66-Polur": {"project_id": 4, "form_id": "66-Polur Landscape Survey 04-2025"},
            "144-Manachanallur": {"project_id": 4, "form_id": "144-Manachanallur Landscape Survey 04-2025"},
            "145-Musiri": {"project_id": 4, "form_id": "145-Musiri Landscape Survey 04-2025"},
            "56-Thalli": {"project_id": 4, "form_id": "56-Thalli Landscape Survey 04-2025"},
            "3-Thirutthani": {"project_id": 4, "form_id": "3-Thirutthani Landscape Survey 04-2025"},
            "146-Thuraiyur": {"project_id": 4, "form_id": "146. Thuraiyur (SC) Landscape Survey 04-2025"},
            "182-Alangudi": {"project_id": 4, "form_id": "182-Alangudi Landscape Survey 04-2025"},
            "137-Kulithalai": {"project_id": 4, "form_id": "137-Kulithalai Landscape Survey 04-2025"},
            "12-Perambur": {"project_id": 4, "form_id": "12-Perambur Landscape Survey 04-2025"},
            "171-Kumbakonam": {"project_id": 4, "form_id": "171-Kumbakonam Landscape Survey 04-2025"},
            "150-Jayankondam": {"project_id": 4, "form_id": "150-Jayankondam Landscape Survey 04-2025"},
            "132-Dindigul": {"project_id": 4, "form_id": "132 Dindigul Landscape Survey 04-2025"},
            "20-Thousand Lights": {"project_id": 4, "form_id": "20-Thousand Lights Landscape Survey 04-2025"},
            "37-Kancheepuram": {"project_id": 4, "form_id": "37-Kancheepuram Landscape Survey 04-2025"},
            "136-Krishnarayapuram": {"project_id": 4, "form_id": "136-Krishnarayapuram (SC) Landscape Survey 04-2025"},
            "38-Arakkonam": {"project_id": 4, "form_id": "38-Arakkonam (SC) Landscape Survey 04-2025"},
            "200-Bodinayakanur": {"project_id": 4, "form_id": "200-Bodinayakanur Landscape Survey 04-2025"},
            "118-Coimbatore North": {"project_id": 4, "form_id": "118-Coimbatore North Landscape Survey 04-2025"},
            "189-Madurai East": {"project_id": 4, "form_id": "189-Madurai East Landscape Survey 04-2025"},
            "103-Perundurai": {"project_id": 4, "form_id": "103-Perundurai Landscape Survey 04-2025"},
            "199-Periyakulam": {"project_id": 4, "form_id": "199. Periyakulam (SC) Landscape Survey 04-2025"},
            "149-Ariyalur": {"project_id": 4, "form_id": "149-Ariyalur Landscape Survey 04-2025"},
            "135-Karur": {"project_id": 4, "form_id": "135-Karur Landscape Survey 04-2025"},
            "138-Manapparai": {"project_id": 4, "form_id": "138-Manapparai Landscape Survey 04-2025"},
            "152-Vriddhachalam": {"project_id": 4, "form_id": "152-Vriddhachalam Landscape Survey 04-2025"},
            "153-Neyveli": {"project_id": 4, "form_id": "153-Neyveli Landscape Survey 04-2025"},
            "156-Kurinjipadi": {"project_id": 4, "form_id": "156-Kurinjipadi Landscape Survey 04-2025"},
            "161-Mayiladuthurai": {"project_id": 4, "form_id": "161-Mayiladuthurai Landscape Survey 04-2025"},
            "166-Thiruthuraipoondi": {"project_id": 4, "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025"},
            "178-Gandharvakottai": {"project_id": 4, "form_id": "178-Gandharvakottai (SC) Landscape Survey 04-2025 copy 3"},
            "198-Andipatti": {"project_id": 4, "form_id": "198-Andipatti Landscape Survey 04-2025"},
            "51-Uthangarai": {"project_id": 4, "form_id": "51-Uthangarai (SC) Landscape Survey 04-2025"},
            "60-Pappireddippatti": {"project_id": 4, "form_id": "60-Pappireddippatti Landscape Survey 04-2025"},
            "61-Harur": {"project_id": 4, "form_id": "61-Harur (SC) Landscape Survey 04-2025"},
            "180-Pudukkottai": {"project_id": 4, "form_id": "180-Pudukkottai Landscape Survey 04-2025"},
            "158-Chidambaram": {"project_id": 4, "form_id": "158-Chidambaram Landscape Survey 04-2025"},
            "216-Srivaikuntam Landscape Survey 04-2025": {"project_id": 4, "form_id": "216-Srivaikuntam Landscape Survey 04-2025"},
            "133-Vedasandur Landscape Survey 04-2025": {"project_id": 4, "form_id": "133-Vedasandur Landscape Survey 04-2025"},
            "110-Coonoor Landscape Survey 04-2025": {"project_id": 4, "form_id": "110-Coonoor Landscape Survey 04-2025"},
            "109-Gudalur (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "109-Gudalur (SC) Landscape Survey 04-2025"}
        },
        "03 TN AC Landscape": {
            "110-Coonoor": {"project_id": 5, "form_id": "110-Coonoor Landscape Survey 04-2025"},
            "222-Tenkasi": {"project_id": 5, "form_id": "222-Tenkasi Landscape Survey 04-2025"},
            "223-Alangulam": {"project_id": 5, "form_id": "223-Alangulam Landscape Survey 04-2025"},
            "48-Ambur": {"project_id": 5, "form_id": "48-AmburLandscape Survey 04-2025"},
            "49-Jolarpet": {"project_id": 5, "form_id": "49-Jolarpet Landscape Survey 04-2025"},
            "63-Tiruvannamalai": {"project_id": 5, "form_id": "63-Tiruvannamalai Landscape Survey 04-2025"},
            "64-Kilpennathur": {"project_id": 5, "form_id": "64-KilpennathurLandscape Survey 04-2025"},
            "65-Kalasapakkam": {"project_id": 5, "form_id": "65-Kalasapakkam Landscape Survey 04-2025"},
            "67-Arani": {"project_id": 5, "form_id": "67-Arani Landscape Survey 04-2025"},
            "68-Cheyyar": {"project_id": 5, "form_id": "68-Cheyyar Landscape Survey 04-2025"}
        }
    },
    "Server 2": {
        "02 TN Landscape Survey": {
            "139-Srirangam": {"project_id": 3, "form_id": "139-SrirangamLandscape Survey 04-2025"},
            "141-Tiruchirappalli (East)": {"project_id": 3, "form_id": "141-Tiruchirappalli (East) Landscape Survey 04-2025"},
            "163-Nagapattinam": {"project_id": 3, "form_id": "163-Nagapattinam Landscape Survey 04-2025"},
            "172-Papanasam": {"project_id": 3, "form_id": "172-Papanasam Landscape Survey 04-2025"},
            "174-Thanjavur": {"project_id": 3, "form_id": "174-Thanjavur Landscape Survey 04-2025"},
            "177-Peravurani": {"project_id": 3, "form_id": "177-Peravurani Landscape Survey 04-2025"},
            "205-Sivakasi": {"project_id": 3, "form_id": "205-Sivakasi Landscape Survey 04-2025"},
            "209-Paramakudi (SC)": {"project_id": 3, "form_id": "209-Paramakudi (SC) Landscape Survey 04-2025"},
            "213-Vilathikulam": {"project_id": 3, "form_id": "213-Vilathikulam Landscape Survey 04-2025"},
            "216-Srivaikuntam": {"project_id": 3, "form_id": "216-Srivaikuntam Landscape Survey 04-2025"},
            "217-Ottapidaram (SC)": {"project_id": 3, "form_id": "217 - Ottapidaram (SC) Landscape Survey 04-2025"},
            "65-Kalasapakkam": {"project_id": 3, "form_id": "65-Kalasapakkam Landscape Survey 04-2025"},
            "68-Cheyyar": {"project_id": 3, "form_id": "68-Cheyyar Landscape Survey 04-2025"},
            "77-Ulundurpettai": {"project_id": 3, "form_id": "77-Ulundurpettai Landscape Survey 04-2025"},
            "8-Ambattur": {"project_id": 3, "form_id": "8-Ambattur Landscape Survey 04-2025"},
            "Test Landscape Survey 04-2025 copy": {"project_id": 3, "form_id": "Test Landscape Survey 04-2025 copy"},
            "V3 Master Landscape Survey 04-2025 ODK XLSForm": {"project_id": 3, "form_id": "V3 Master Landscape Survey 04-2025 ODK XLSForm"}
        }
    }
}

# --- MongoDB Functions ---
def get_mongo_client():
    try:
        load_dotenv()
        MONGO_URI = os.getenv("MONGO_URI")
        if not MONGO_URI:
            MONGO_URI = "mongodb://localhost:27017/"
        client = MongoClient(MONGO_URI)
        return client
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {str(e)}")
        return None

def save_login_details(username, email):
    try:
        client = get_mongo_client()
        if client:
            db = client["tnmaster_db"]
            login_collection = db["login_history"]
            login_data = {
                "username": username,
                "email": email,
                "login_time": datetime.now(),
                "login_date": date.today().isoformat(),
                "user_agent": st.session_state.get("_client", {}).get("user_agent", "Unknown"),
                "ip_address": st.session_state.get("_client", {}).get("ip", "Unknown")
            }
            login_collection.insert_one(login_data)
            client.close()
            return True
        return False
    except Exception as e:
        st.error(f"Error saving login details: {str(e)}")
        return False

# --- OTP Functions ---
def send_otp_email(receiver_email, otp, username):
    try:
        msg = MIMEMultipart()
        msg['From'] = "TNMaster Analytics <analytics@tnmaster.com>"
        msg['To'] = receiver_email
        msg['Subject'] = "TNMaster Authentication: Your Secure Login OTP"
        current_date = datetime.now().strftime("%B %d, %Y")
        body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.7; color: #333;">
                <div style="max-width: 650px; margin: 0 auto;">
                    <div style="background-color: #1a73e8; padding: 20px 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-weight: 300;">TNMaster Analytics Platform</h1>
                    </div>
                    <div style="background-color: #ffffff; padding: 30px 40px; border-left: 1px solid #e0e0e0; border-right: 1px solid #e0e0e0;">
                        <p style="margin-top: 0;">Dear <strong>{username}</strong>,</p>
                        <p>Thank you for accessing the TNMaster Analytics Dashboard. To ensure the security of your account, we require two-factor authentication.</p>
                        <div style="background-color: #f8f9fb; border-left: 4px solid #1a73e8; padding: 20px 25px; margin: 30px 0; text-align: center;">
                            <p style="font-size: 15px; margin: 0 0 10px 0;">Your One-Time Password (OTP) is:</p>
                            <div style="font-size: 26px; font-weight: bold; letter-spacing: 3px; color: #1a73e8; padding: 10px 0;">
                                {otp}
                            </div>
                            <p style="font-size: 13px; margin: 10px 0 0 0; color: #666;">
                                Valid for <strong>5 minutes</strong>
                            </p>
                        </div>
                        <p>After authentication, you'll access the TNMaster dashboard featuring:</p>
                        <ul style="padding-left: 20px; margin-bottom: 25px;">
                            <li><strong>Real-time Data Visualization</strong></li>
                            <li><strong>Comprehensive Analytics</strong></li>
                            <li><strong>Geographic Information System</strong></li>
                            <li><strong>Custom Report Generation</strong></li>
                        </ul>
                        <div style="background-color: #fbf8e3; padding: 15px; border-left: 4px solid #f5c518; margin: 25px 0;">
                            <p style="margin: 0; font-size: 14px;">
                                <strong>Security Note:</strong> This OTP is unique to your session. TNMaster will never ask for your password or OTP via phone or other channels.
                            </p>
                        </div>
                    </div>
                    <div style="background-color: #f5f5f7; padding: 20px 30px; text-align: center; font-size: 12px; color: #666; border: 1px solid #e0e0e0; border-top: none;">
                        <p>This is an automated message. Please do not reply.</p>
                        <p style="margin-bottom: 5px;">© {datetime.now().year} TNMaster. All rights reserved.</p>
                        <p style="margin-top: 0;">Sent on {current_date}</p>
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending OTP: {str(e)}")
        return False

def generate_otp():
    return str(random.randint(100000, 999999))

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

# --- Login Page ---
def login_page():
    st.title("🔒 TNMaster Login")
    st.markdown("Please enter your credentials to access the dashboard.")
    with st.form(key='login_form'):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        if not st.session_state['otp_sent']:
            submit_button = st.form_submit_button("Login")
            if submit_button:
                if username in VALID_CREDENTIALS and password == VALID_CREDENTIALS[username]["password"]:
                    user_email = VALID_CREDENTIALS[username]["email"]
                    st.session_state['email'] = user_email
                    st.session_state['username'] = username
                    otp = generate_otp()
                    st.session_state['otp'] = otp
                    st.session_state['otp_time'] = time.time()
                    if send_otp_email(user_email, otp, username):
                        st.session_state['otp_sent'] = True
                        st.success(f"OTP sent to {user_email[:2]}****{user_email.split('@')[1]}")
                    else:
                        st.error("Failed to send OTP. Please try again.")
                else:
                    st.session_state['attempts'] += 1
                    if st.session_state['attempts'] >= 3:
                        st.error("Too many failed attempts. Please try again later.")
                        st.stop()
                    else:
                        st.error("Invalid username or password.")
        if st.session_state['otp_sent']:
            st.markdown("---")
            st.subheader("OTP Verification")
            entered_otp = st.text_input("Enter 6-digit OTP", placeholder="XXXXXX", max_chars=6, type="password")
            if st.form_submit_button("Verify OTP"):
                current_time = time.time()
                otp_expired = (current_time - st.session_state['otp_time']) > 300
                if otp_expired:
                    st.error("OTP has expired. Please request a new one.")
                    st.session_state['otp_sent'] = False
                elif entered_otp == st.session_state['otp']:
                    save_result = save_login_details(st.session_state['username'], st.session_state['email'])
                    st.session_state['logged_in'] = True
                    st.session_state['page'] = "Main Dashboard"
                    st.success("Authentication successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid OTP. Please try again.")

# --- Data Processing Functions ---
@st.cache_data(ttl=3600)
def get_submissions(url, username, password):
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        data = response.json().get("value", [])
        if not data:
            st.warning("No submissions found in ODK for this form.")
        return data
    except Exception as e:
        st.error(f"Failed to fetch submissions from ODK: {e}")
        return []

def process_submissions(submissions):
    if not submissions:
        return None
    df = pd.DataFrame(submissions)

    def extract_group_six_field(row, field_name):
        value = None
        group_six = row.get('group_six')
        if isinstance(group_six, str):
            try:
                group_six_data = json.loads(group_six)
                value = group_six_data.get(field_name)
            except json.JSONDecodeError:
                pass
        elif isinstance(group_six, dict):
            value = group_six.get(field_name)
        if value:
            value = str(value).lower().replace(' ', '')
            if field_name == 'D3_Gender':
                value = value.replace('gender.', '')
            elif field_name == 'D4_Age':
                value = value.replace('age.', '')
            elif field_name == 'D5_Caste':
                value = value.replace('caste.', '')
        return value

    def extract_geopoint_data(row):
        group_six = row.get('group_six')
        lat, lon = None, None
        error_reason = None
        try:
            if isinstance(group_six, str):
                group_six_data = json.loads(group_six)
            elif isinstance(group_six, dict):
                group_six_data = group_six
            else:
                return None, None, "No group_six data"
            geopoint = group_six_data.get('geopoint_widget')
            if not geopoint or not isinstance(geopoint, dict):
                return None, None, "Invalid geopoint_widget"
            coordinates = geopoint.get('coordinates')
            if not coordinates or len(coordinates) < 2:
                return None, None, "Missing coordinates"
            lon, lat = coordinates[0], coordinates[1]
            if lat is None or lon is None:
                return None, None, "Null coordinates"
            lat = float(lat)
            lon = float(lon)
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return None, None, f"Out-of-range: lat={lat}, lon={lon}"
            return lat, lon, None
        except Exception as e:
            return None, None, f"Error: {str(e)}"

    df['submittedBy'] = df.apply(lambda row: extract_group_six_field(row, 'submittedBy'), axis=1)
    df['Gender'] = df.apply(lambda row: extract_group_six_field(row, 'D3_Gender'), axis=1)
    df['Age'] = df.apply(lambda row: extract_group_six_field(row, 'D4_Age'), axis=1)
    df['Caste'] = df.apply(lambda row: extract_group_six_field(row, 'D5_Caste'), axis=1)
    df['Block'] = df.apply(lambda row: extract_group_six_field(row, 'D1_Block'), axis=1)
    df['Village'] = df.apply(lambda row: extract_group_six_field(row, 'D2_Village_GP'), axis=1)
    df['Latitude'], df['Longitude'], df['GeoError'] = zip(*df.apply(extract_geopoint_data, axis=1))

    if 'start' in df.columns and 'end' in df.columns:
        try:
            df['submission_datetime'] = pd.to_datetime(df['start'])
            df['end_datetime'] = pd.to_datetime(df['end'])
            df['submission_hour'] = df['submission_datetime'].dt.hour
            df['submission_date'] = df['submission_datetime'].dt.strftime('%Y-%m-%d')
            df['Duration'] = (df['end_datetime'] - df['submission_datetime']).dt.total_seconds() / 60.0
        except Exception as e:
            st.error(f"Error processing dates: {e}")
            return None
    else:
        st.error("Missing 'start' or 'end' columns.")
        return None

    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    if df['Age'].notna().any():
        age_bins = [18, 25, 35, 45, 55, float('inf')]
        age_labels = ['18-25', '26-35', '36-45', '46-55', '56+']
        df['Age_Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, include_lowest=True, right=False)
    else:
        df['Age_Group'] = None

    duration_bins = [0, 5, 10, 15, 20, float('inf')]
    duration_labels = ['0-5 min', '5-10 min', '10-15 min', '15-20 min', '20+ min']
    df['Duration_Group'] = pd.cut(df['Duration'], bins=duration_bins, labels=duration_labels, include_lowest=True, right=False)

    return df

def store_in_mongodb(df, collection):
    try:
        records = df.to_dict('records')
        collection.delete_many({})
        collection.insert_many(records)
        st.success(f"Stored {len(records)} submissions in MongoDB!")
    except Exception as e:
        st.error(f"Failed to store in MongoDB: {e}")

def load_from_mongodb(collection):
    try:
        records = list(collection.find())
        if not records:
            return None
        df = pd.DataFrame(records)
        if 'submission_datetime' in df.columns:
            df['submission_datetime'] = pd.to_datetime(df['submission_datetime'], errors='coerce')
        if 'end_datetime' in df.columns:
            df['end_datetime'] = pd.to_datetime(df['end_datetime'], errors='coerce')
        if 'submission_datetime' in df.columns:
            df['submission_hour'] = df['submission_datetime'].dt.hour
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
        return df
    except Exception as e:
        st.error(f"Failed to load from MongoDB: {e}")
        return None

@st.cache_data(ttl=3600)
def get_address(lat, lon, key):
    try:
        url = f"https://atlas.microsoft.com/search/address/reverse/json"
        params = {
            "api-version": "1.0",
            "subscription-key": key,
            "query": f"{lat},{lon}"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            address_info = data.get("addresses", [])
            if address_info:
                return address_info[0].get("address", {}).get("freeformAddress", "Address not found")
            return "Address not found"
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Aggregate All Form Data ---
def aggregate_all_forms():
    client = get_mongo_client()
    if not client:
        return None
    db = client['test']
    all_dfs = []
    for server in forms:
        for project in forms[server]:
            for form_name, form_info in forms[server][project].items():
                project_id = form_info['project_id']
                form_id = form_info['form_id']
                collection_name = f"submissions_{server.replace(' ', '_')}_{project_id}_{form_id.replace(' ', '_').replace('-', '_').replace('.', '_').replace('(', '').replace(')', '')}"
                collection = db[collection_name]
                df = load_from_mongodb(collection)
                if df is not None:
                    df['Form_Name'] = form_name
                    df['Project'] = project
                    df['Server'] = server
                    all_dfs.append(df)
    client.close()
    if not all_dfs:
        return None
    aggregated_df = pd.concat(all_dfs, ignore_index=True)
    return aggregated_df

# --- Refresh All Forms ---
def refresh_all_forms():
    load_dotenv()
    ODK_USERNAME = os.getenv("ODK_USERNAME")
    ODK_PASSWORD = os.getenv("ODK_PASSWORD")
    client = get_mongo_client()
    if not client:
        return
    db = client['test']
    for server in forms:
        base_url_prefix = "https://tnodk01.indiaintentions.com" if server == "Server 1" else "https://tnodk02.indiaintentions.com"
        for project in forms[server]:
            for form_name, form_info in forms[server][project].items():
                project_id = form_info['project_id']
                form_id = form_info['form_id']
                collection_name = f"submissions_{server.replace(' ', '_')}_{project_id}_{form_id.replace(' ', '_').replace('-', '_').replace('.', '_').replace('(', '').replace(')', '')}"
                collection = db[collection_name]
                base_url = f"{base_url_prefix}/v1/projects/{project_id}/forms/{urllib.parse.quote(form_id)}.svc/Submissions"
                submissions = get_submissions(base_url, ODK_USERNAME, ODK_PASSWORD)
                df = process_submissions(submissions)
                if df is not None:
                    store_in_mongodb(df, collection)
                    st.session_state[f'data_{collection_name}'] = df
    client.close()
    st.success("All form data refreshed successfully!")

# --- Main Dashboard ---
def main_dashboard():
    load_dotenv()
    ODK_USERNAME = os.getenv("ODK_USERNAME")
    ODK_PASSWORD = os.getenv("ODK_PASSWORD")
    MONGO_URI = os.getenv("MONGO_URI")
    AZURE_MAPS_API_KEY = "944BjlSA5zZyX94AAvM2mM4gIRV005pWgXAOpFbvVNEWSGmFMEm7JQQJ99BDACYeBjFgSQNNAAAgAZMP3Cok"

    st.title("TNMaster Dashboard")
    st.write(f"Welcome, {st.session_state['username']}!")

    # Sidebar navigation
    st.sidebar.header("Navigation")
    dashboard_option = st.sidebar.radio(
        "Select Dashboard:", 
        ["Form-wise Dashboard", "Overall Dashboard"], 
        index=0, 
        key="dashboard_selector"
    )

    # Update session state based on selection
    if dashboard_option == "Overall Dashboard":
        st.session_state['page'] = "Overall Dashboard"
        overall_dashboard()
        return
    else:
        st.session_state['page'] = "Main Dashboard"

    # MongoDB setup
    try:
        client = MongoClient(MONGO_URI)
        db = client['test']
        st.success("Connected to MongoDB successfully!")
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        st.stop()

    st.markdown("<style> .css-1aumxhk { padding-top: 50px; } </style>", unsafe_allow_html=True)
    st.title("📊 TNMaster: Tamil Nadu Landscape Survey Dashboard (April 2025)")

    # Form selection sidebar
    st.sidebar.header("Data Selection")
    selected_server = st.sidebar.selectbox(
        "Select Server:", 
        list(forms.keys()), 
        index=list(forms.keys()).index(st.session_state['selected_server']), 
        key="server_selector"
    )
    project_options = list(forms[selected_server].keys())
    selected_project = st.sidebar.selectbox(
        "Select Project:", 
        project_options, 
        index=project_options.index(st.session_state['selected_project']) if st.session_state['selected_project'] in project_options else 0, 
        key="project_selector"
    )
    form_options = list(forms[selected_server][selected_project].keys())
    selected_form = st.sidebar.selectbox(
        "Select Form:", 
        form_options, 
        index=form_options.index(st.session_state['selected_form']) if st.session_state['selected_form'] in form_options else 0, 
        key="form_selector"
    )

    # Update session state
    st.session_state['selected_server'] = selected_server
    st.session_state['selected_project'] = selected_project
    st.session_state['selected_form'] = selected_form

    # Get project and form ID
    selected_project_id = forms[selected_server][selected_project][selected_form]["project_id"]
    selected_form_id = forms[selected_server][selected_project][selected_form]["form_id"]
    base_url_prefix = "https://tnodk01.indiaintentions.com" if selected_server == "Server 1" else "https://tnodk02.indiaintentions.com"
    BASE_URL = f"{base_url_prefix}/v1/projects/{selected_project_id}/forms/{urllib.parse.quote(selected_form_id)}.svc/Submissions"

    # Collection name
    form_collection_name = f"submissions_{selected_server.replace(' ', '_')}_{selected_project_id}_{selected_form_id.replace(' ', '_').replace('-', '_').replace('.', '_').replace('(', '').replace(')', '')}"
    collection = db[form_collection_name]
    st.success(f"Using collection: {form_collection_name}")

    # Data loading logic
    refresh_data = st.sidebar.button("Refresh Data from ODK")
    form_title = f"{selected_form} ({selected_project})"
    st.subheader(f"Analyzing data for: {form_title}")

    if refresh_data:
        submissions = get_submissions(BASE_URL, ODK_USERNAME, ODK_PASSWORD)
        df = process_submissions(submissions)
        if df is not None:
            store_in_mongodb(df, collection)
            st.session_state['data'] = df
        else:
            st.error(f"No valid data processed from ODK for {form_title}.")
            st.stop()
    else:
        df = load_from_mongodb(collection)
        if df is None:
            st.info(f"No data in MongoDB for {form_title}. Fetching from ODK...")
            submissions = get_submissions(BASE_URL, ODK_USERNAME, ODK_PASSWORD)
            df = process_submissions(submissions)
            if df is not None:
                store_in_mongodb(df, collection)
                st.session_state['data'] = df
            else:
                st.error(f"No data available from ODK for {form_title}.")
                st.stop()
        else:
            st.session_state['data'] = df

    filtered_df = st.session_state.get('data', pd.DataFrame())
    if filtered_df.empty:
        st.error("No data to display.")
        st.stop()

    # Date filter
    st.sidebar.header("📅 Filter by Date")
    if 'submission_date' in filtered_df.columns:
        show_all_dates = st.sidebar.checkbox("Show All Dates", value=True)
        if not show_all_dates:
            unique_dates = sorted(filtered_df['submission_date'].dropna().unique())
            if unique_dates:
                try:
                    if selected_project == "TN Master":
                        allowed_dates = ['2025-04-14', '2025-04-15']
                        valid_dates = [d for d in unique_dates if d in allowed_dates]
                        if not valid_dates:
                            st.sidebar.warning("No data for April 14 or 15, 2025.")
                            selected_date = '2025-04-14'
                        else:
                            min_date = pd.to_datetime('2025-04-14').date()
                            max_date = pd.to_datetime('2025-04-15').date()
                            default_date = pd.to_datetime(min(valid_dates)).date()
                            selected_date = st.sidebar.date_input(
                                "Select Date:", value=default_date, min_value=min_date, max_value=max_date, format="YYYY-MM-DD"
                            )
                            selected_date = selected_date.strftime('%Y-%m-%d')
                    else:
                        min_allowed_date = pd.to_datetime('2025-04-14').date()
                        max_allowed_date = datetime.now().date()
                        valid_dates = [d for d in unique_dates if pd.to_datetime(d).date() >= min_allowed_date]
                        if not valid_dates:
                            st.sidebar.warning("No data from April 14, 2025 onwards.")
                            default_date = min_allowed_date
                        else:
                            default_date = pd.to_datetime(min(valid_dates)).date()
                        selected_date = st.sidebar.date_input(
                            "Select Date:", value=default_date, min_value=min_allowed_date, max_value=max_allowed_date, format="YYYY-MM-DD"
                        )
                        selected_date = selected_date.strftime('%Y-%m-%d')
                except Exception as e:
                    st.sidebar.error(f"Error processing dates: {e}")
                    selected_date = 'All'
            else:
                selected_date = 'All'
                st.sidebar.warning("No valid dates available.")
        else:
            selected_date = 'All'
    else:
        selected_date = 'All'
        st.sidebar.info("Date filtering unavailable.")

    # Filter data
    if selected_date != 'All' and 'submission_date' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['submission_date'] == selected_date]
        if filtered_df.empty:
            st.warning(f"No data for selected date: {selected_date}")

    if 'submission_date' in filtered_df.columns:
        if selected_project == "TN Master":
            allowed_dates = ['2025-04-14', '2025-04-15']
            filtered_df = filtered_df[filtered_df['submission_date'].isin(allowed_dates)]
            if filtered_df.empty and selected_date == 'All':
                st.warning("No data for April 14 or 15, 2025.")
        else:
            min_allowed_date = pd.to_datetime('2025-04-14').date()
            filtered_df = filtered_df[pd.to_datetime(filtered_df['submission_date']).dt.date >= min_allowed_date]
            if filtered_df.empty and selected_date == 'All':
                st.warning("No data from April 14, 2025 onwards.")

    if selected_project in ["BK TN AC Landscape", "03 TN AC Landscape", "02 TN Landscape Survey"]:
        today_date = datetime.now().strftime('%Y-%m-%d')
        if 'submission_date' in filtered_df.columns:
            today_data = filtered_df[filtered_df['submission_date'] == today_date]
            if today_data.empty:
                st.warning(f"No data for today ({today_date}) in form {form_title}. Showing available data.")
            else:
                st.info(f"Found {len(today_data)} submissions for today ({today_date}) in form {form_title}.")
        else:
            st.warning("No submission date info available.")

    total_submissions = len(filtered_df)
    st.markdown(f"**Total Submissions for {form_title}**: {total_submissions}")

    # Visualizations
    st.subheader("Submissions per Hour Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'submission_hour' in filtered_df.columns and not filtered_df.empty:
            hourly_counts = filtered_df['submission_hour'].value_counts().sort_index().reset_index(name='Count')
            hourly_counts['Time'] = hourly_counts['submission_hour'].astype(str).str.zfill(2) + ":00"
            missing_hours = filtered_df['submission_hour'].isna().sum()
            if missing_hours > 0:
                hourly_counts = pd.concat([hourly_counts, pd.DataFrame({'submission_hour': [None], 'Count': [missing_hours], 'Time': ['Missing']})])
            total_submissions = hourly_counts['Count'].sum()
            st.metric(label="Total Submissions", value=total_submissions)
            fig = px.bar(hourly_counts, x='Time', y='Count',
                         title=f'Submissions per Hour' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                         labels={'Time': 'Hour (IST)', 'Count': 'Submissions'})
            fig.update_traces(text=hourly_counts['Count'], textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'submission_hour' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    hourly_counts_user = user_df['submission_hour'].value_counts().sort_index().reset_index(name='Count')
                    hourly_counts_user['Time'] = hourly_counts_user['submission_hour'].astype(str).str.zfill(2) + ":00"
                    missing_hours_user = user_df['submission_hour'].isna().sum()
                    if missing_hours_user > 0:
                        hourly_counts_user = pd.concat([hourly_counts_user, pd.DataFrame({'submission_hour': [None], 'Count': [missing_hours_user], 'Time': ['Missing']})])
                    total_user = hourly_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=hourly_counts_user['Time'], y=hourly_counts_user['Count'],
                        text=hourly_counts_user['Count'], textposition='outside', name=submitter,
                        visible=(submitter == 'All'), customdata=[total_user] * len(hourly_counts_user),
                        hovertemplate='%{x}<br>Submissions: %{y}<extra></extra>'
                    )
                    traces.append(trace)
            if traces:
                updatemenus = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Submissions per Hour ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_user = dict(
                    data=traces, layout=dict(
                        updatemenus=updatemenus,
                        title=f"Submissions per Hour (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Hour (IST)"), yaxis=dict(title="Submissions"), showlegend=False
                    )
                )
                total_initial = traces[0]['customdata'][0]
                total_metric = st.metric(label="Total Submissions (All Users)", value=total_initial)
                st.plotly_chart(fig_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Submissions (All Users)" : "Total Submissions by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific hourly data.")
        else:
            st.info("No submitter data available.")

    # Gender Distribution
    st.subheader("Gender Distribution Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Gender' in filtered_df.columns:
            gender_counts = filtered_df['Gender'].value_counts().reset_index(name='Count')
            gender_counts.columns = ['Gender', 'Count']
            missing_gender = filtered_df['Gender'].isna().sum()
            if missing_gender > 0:
                gender_counts = pd.concat([gender_counts, pd.DataFrame({'Gender': ['Missing'], 'Count': [missing_gender]})])
            total_submissions = gender_counts['Count'].sum()
            st.metric(label="Total Respondents", value=total_submissions)
            fig_gender = px.pie(gender_counts, names='Gender', values='Count',
                                title=f'Gender Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'))
            fig_gender.update_traces(textinfo='value+percent', textposition='inside')
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.info("No gender data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Gender' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_gender = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    gender_counts_user = user_df['Gender'].value_counts().reset_index(name='Count')
                    gender_counts_user.columns = ['Gender', 'Count']
                    missing_gender_user = user_df['Gender'].isna().sum()
                    if missing_gender_user > 0:
                        gender_counts_user = pd.concat([gender_counts_user, pd.DataFrame({'Gender': ['Missing'], 'Count': [missing_gender_user]})])
                    total_gender_user = gender_counts_user['Count'].sum()
                    trace = dict(
                        type='pie', labels=gender_counts_user['Gender'], values=gender_counts_user['Count'],
                        textinfo='value+percent', textposition='inside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_gender_user], hovertemplate='%{label}<br>Count: %{value} (%{percent})<extra></extra>'
                    )
                    traces_gender.append(trace)
            if traces_gender:
                updatemenus_gender = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Gender Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_gender_user = dict(
                    data=traces_gender, layout=dict(
                        updatemenus=updatemenus_gender,
                        title=f"Gender Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        showlegend=True
                    )
                )
                total_gender_initial = traces_gender[0]['customdata'][0]
                total_metric_gender = st.metric(label="Total Respondents (Gender)", value=total_gender_initial)
                st.plotly_chart(fig_gender_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Respondents (Gender)" : "Total Respondents (Gender) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific gender data.")
        else:
            st.info("No gender or submitter data.")

    # Age Distribution
    st.subheader("Age Distribution Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Age_Group' in filtered_df.columns:
            age_counts = filtered_df['Age_Group'].value_counts().reset_index(name='Count')
            age_counts.columns = ['Age Group', 'Count']
            missing_age = filtered_df['Age'].isna().sum()
            if missing_age > 0:
                age_counts = pd.concat([age_counts, pd.DataFrame({'Age Group': ['Missing'], 'Count': [missing_age]})])
            total_submissions = age_counts['Count'].sum()
            st.metric(label="Total Respondents", value=total_submissions)
            fig_age = px.bar(age_counts, x='Age Group', y='Count',
                             title=f'Age Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'))
            fig_age.update_traces(text=age_counts['Count'], textposition='outside')
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("No age data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Age_Group' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_age = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    age_counts_user = user_df['Age_Group'].value_counts().reset_index(name='Count')
                    age_counts_user.columns = ['Age Group', 'Count']
                    missing_age_user = user_df['Age'].isna().sum()
                    if missing_age_user > 0:
                        age_counts_user = pd.concat([age_counts_user, pd.DataFrame({'Age Group': ['Missing'], 'Count': [missing_age_user]})])
                    total_age_user = age_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=age_counts_user['Age Group'], y=age_counts_user['Count'],
                        text=age_counts_user['Count'], textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_age_user], hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
                    )
                    traces_age.append(trace)
            if traces_age:
                updatemenus_age = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Age Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_age_user = dict(
                    data=traces_age, layout=dict(
                        updatemenus=updatemenus_age,
                        title=f"Age Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Age Group"), yaxis=dict(title="Respondents"), showlegend=False
                    )
                )
                total_age_initial = traces_age[0]['customdata'][0]
                total_metric_age = st.metric(label="Total Respondents (Age)", value=total_age_initial)
                st.plotly_chart(fig_age_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Respondents (Age)" : "Total Respondents (Age) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific age data.")
        else:
            st.info("No age or submitter data.")

    # Caste Distribution
    st.subheader("Caste Distribution Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Caste' in filtered_df.columns:
            caste_counts = filtered_df['Caste'].value_counts().reset_index(name='Count')
            caste_counts.columns = ['Caste', 'Count']
            missing_caste = filtered_df['Caste'].isna().sum()
            if missing_caste > 0:
                caste_counts = pd.concat([caste_counts, pd.DataFrame({'Caste': ['Missing'], 'Count': [missing_caste]})])
            total_submissions = caste_counts['Count'].sum()
            st.metric(label="Total Respondents", value=total_submissions)
            fig_caste = px.bar(caste_counts, x='Caste', y='Count',
                               title=f'Caste Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                               labels={'Caste': 'Caste', 'Count': 'Count'})
            fig_caste.update_traces(text=caste_counts['Count'], textposition='outside')
            fig_caste.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_caste, use_container_width=True)
        else:
            st.info("No caste data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Caste' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_caste = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    caste_counts_user = user_df['Caste'].value_counts().reset_index(name='Count')
                    caste_counts_user.columns = ['Caste', 'Count']
                    missing_caste_user = user_df['Caste'].isna().sum()
                    if missing_caste_user > 0:
                        caste_counts_user = pd.concat([caste_counts_user, pd.DataFrame({'Caste': ['Missing'], 'Count': [missing_caste_user]})])
                    total_caste_user = caste_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=caste_counts_user['Caste'], y=caste_counts_user['Count'],
                        text=caste_counts_user['Count'], textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_caste_user], hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
                    )
                    traces_caste.append(trace)
            if traces_caste:
                updatemenus_caste = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Caste Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_caste_user = dict(
                    data=traces_caste, layout=dict(
                        updatemenus=updatemenus_caste,
                        title=f"Caste Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Caste", tickangle=45), yaxis=dict(title="Count"), showlegend=False
                    )
                )
                total_caste_initial = traces_caste[0]['customdata'][0]
                total_metric_caste = st.metric(label="Total Respondents (Caste)", value=total_caste_initial)
                st.plotly_chart(fig_caste_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Respondents (Caste)" : "Total Respondents (Caste) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific caste data.")
        else:
            st.info("No caste or submitter data.")

    # Survey Duration
    st.subheader("Survey Duration Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Duration_Group' in filtered_df.columns:
            duration_counts = filtered_df['Duration_Group'].value_counts().reset_index(name='Count')
            duration_counts.columns = ['Duration', 'Count']
            missing_duration = filtered_df['Duration'].isna().sum()
            if missing_duration > 0:
                duration_counts = pd.concat([duration_counts, pd.DataFrame({'Duration': ['Missing'], 'Count': [missing_duration]})])
            total_submissions = duration_counts['Count'].sum()
            st.metric(label="Total Submissions", value=total_submissions)
            fig_duration = px.bar(duration_counts, x='Duration', y='Count',
                                  title=f'Survey Duration Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'))
            fig_duration.update_traces(text=duration_counts['Count'], textposition='outside')
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No duration data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Duration_Group' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_duration = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    duration_counts_user = user_df['Duration_Group'].value_counts().reset_index(name='Count')
                    duration_counts_user.columns = ['Duration', 'Count']
                    missing_duration_user = user_df['Duration'].isna().sum()
                    if missing_duration_user > 0:
                        duration_counts_user = pd.concat([duration_counts_user, pd.DataFrame({'Duration': ['Missing'], 'Count': [missing_duration_user]})])
                    total_duration_user = duration_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=duration_counts_user['Duration'], y=duration_counts_user['Count'],
                        text=duration_counts_user['Count'], textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_duration_user], hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
                    )
                    traces_duration.append(trace)
            if traces_duration:
                updatemenus_duration = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Survey Duration Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_duration_user = dict(
                    data=traces_duration, layout=dict(
                        updatemenus=updatemenus_duration,
                        title=f"Survey Duration Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Duration"), yaxis=dict(title="Submissions"), showlegend=False
                    )
                )
                total_duration_initial = traces_duration[0]['customdata'][0]
                total_metric_duration = st.metric(label="Total Submissions (Duration)", value=total_duration_initial)
                st.plotly_chart(fig_duration_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Submissions (Duration)" : "Total Submissions (Duration) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific duration data.")
        else:
            st.info("No duration or submitter data.")

    # Geographic Distribution
    st.subheader("Geographic Distribution")
    if 'Latitude' in filtered_df.columns and 'Longitude' in filtered_df.columns:
        map_df = filtered_df[filtered_df['Latitude'].notna() & filtered_df['Longitude'].notna() & (filtered_df['GeoError'].isna())]
        invalid_df = filtered_df[filtered_df['Latitude'].isna() | filtered_df['Longitude'].isna() | filtered_df['GeoError'].notna()]
        st.markdown("**Geographic Data Summary**")
        total_submissions = len(filtered_df)
        valid_coords = len(map_df)
        invalid_coords = len(invalid_df)
        st.write(f"Total Submissions: {total_submissions}")
        st.write(f"Valid Coordinates: {valid_coords}")
        st.write(f"Missing/Invalid Coordinates: {invalid_coords}")

        if not invalid_df.empty:
            st.markdown("**Invalid Coordinates Analysis**")
            error_counts = invalid_df['GeoError'].value_counts().reset_index(name='Count')
            error_counts.columns = ['Error Reason', 'Count']
            st.write("Reasons for Invalid Coordinates:")
            st.dataframe(error_counts)
            with st.expander("View Invalid Coordinates Sample"):
                st.dataframe(invalid_df[['submittedBy', 'Block', 'Village', 'GeoError']].head(10))

        if not map_df.empty:
            with st.expander("View Valid Coordinates Sample"):
                st.dataframe(map_df[['submittedBy', 'Latitude', 'Longitude', 'Block', 'Village']].head(10))

            map_df = map_df.copy()
            map_df['Address'] = map_df.apply(
                lambda row: get_address(row['Latitude'], row['Longitude'], AZURE_MAPS_API_KEY),
                axis=1
            )

            map_data = pd.DataFrame({
                "lat": map_df['Latitude'],
                "lon": map_df['Longitude'],
                "tooltip": map_df.apply(
                    lambda row: f"Address: {row['Address']}\nSubmitted By: {row['submittedBy'] or 'Unknown'}\nBlock: {row['Block'] or 'Unknown'}\nVillage: {row['Village'] or 'Unknown'}",
                    axis=1
                ),
                "submitter": map_df['submittedBy'].fillna('Unknown'),
                "block": map_df['Block'].fillna('Unknown'),
                "village": map_df['Village'].fillna('Unknown'),
                "address": map_df['Address']
            })

            icon_data = {
                "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
                "width": 128,
                "height": 128,
                "anchorY": 128
            }
            map_data["icon_data"] = [icon_data] * len(map_data)

            lat_mean = map_data['lat'].mean() if not map_data['lat'].empty else 10.5
            lon_mean = map_data['lon'].mean() if not map_data['lon'].empty else 78
            zoom_level = min(10, max(5, 10 - len(map_data) // 1000))

            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/streets-v11",
                initial_view_state=pdk.ViewState(
                    latitude=lat_mean,
                    longitude=lon_mean,
                    zoom=zoom_level,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        "IconLayer",
                        data=map_data,
                        get_icon="icon_data",
                        get_size=4,
                        size_scale=15,
                        get_position=["lon", "lat"],
                        pickable=True
                    )
                ],
                tooltip={"text": "{tooltip}"}
            ))

            st.metric(label="Total Geotagged Submissions", value=valid_coords)

            if 'block' in map_data.columns and map_data['block'].notna().any():
                block_counts = map_data['block'].value_counts()
                st.markdown("**Block-wise Distribution:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(block_counts.reset_index().rename(columns={'index': 'Block', 'block': 'Count'}))
                with col2:
                    fig_block = px.pie(names=block_counts.index, values=block_counts.values, title='Block-wise Distribution')
                    st.plotly_chart(fig_block, use_container_width=True)
    else:
        st.info("No geographic data available.")

    # Data Quality
    st.subheader("Data Quality Information")
    total_submissions = len(filtered_df)
    missing_gender = filtered_df['Gender'].isna().sum() if 'Gender' in filtered_df.columns else 0
    missing_age = filtered_df['Age'].isna().sum() if 'Age' in filtered_df.columns else 0
    missing_caste = filtered_df['Caste'].isna().sum() if 'Caste' in filtered_df.columns else 0
    missing_coords = filtered_df[filtered_df['Latitude'].isna() | filtered_df['Longitude'].isna()].shape[0] if 'Latitude' in filtered_df.columns else 0
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Missing Gender", value=missing_gender, delta=f"{round(missing_gender/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")
    with col2:
        st.metric(label="Missing Age", value=missing_age, delta=f"{round(missing_age/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")
    with col3:
        st.metric(label="Missing Caste", value=missing_caste, delta=f"{round(missing_caste/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")
    with col4:
        st.metric(label="Missing Coordinates", value=missing_coords, delta=f"{round(missing_coords/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")

    # Download Data
    st.subheader("Download Data")
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name=f"{form_title.replace(' ', '_')}_data{'_' + str(selected_date) if selected_date != 'All' else ''}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data to download.")

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: gray; font-size: 12px;">
            TNMaster Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data source: MongoDB (ODK Central) | Current Form: {form_title}
        </div>
        """, unsafe_allow_html=True)

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['otp_sent'] = False
        st.session_state['otp'] = None
        st.session_state['email'] = ""
        st.session_state['attempts'] = 0
        st.session_state['page'] = "Login"
        st.success("Logged out successfully!")
        st.rerun()

# --- Overall Dashboard ---
def overall_dashboard():
    load_dotenv()
    AZURE_MAPS_API_KEY = "944BjlSA5zZyX94AAvM2mM4gIRV005pWgXAOpFbvVNEWSGmFMEm7JQQJ99BDACYeBjFgSQNNAAAgAZMP3Cok"

    st.title("📊 TNMaster: Overall Tamil Nadu Landscape Survey Dashboard (April 2025)")
    st.write(f"Welcome, {st.session_state['username']}! This dashboard summarizes data across all forms.")

    # Sidebar navigation
    st.sidebar.header("Navigation")
    dashboard_option = st.sidebar.radio(
        "Select Dashboard:", 
        ["Form-wise Dashboard", "Overall Dashboard"], 
        index=1, 
        key="dashboard_selector"
    )

    # Handle navigation
    if dashboard_option == "Form-wise Dashboard":
        st.session_state['page'] = "Main Dashboard"
        st.rerun()
        return

    # Add a Back button
    if st.sidebar.button("Back to Form-wise Dashboard"):
        st.session_state['page'] = "Main Dashboard"
        st.rerun()

    # Sidebar data refresh
    st.sidebar.header("Data Refresh")
    if st.sidebar.button("Refresh All Form Data"):
        refresh_all_forms()
        st.session_state['overall_data'] = None

    # Load aggregated data
    if 'overall_data' not in st.session_state or st.session_state['overall_data'] is None:
        aggregated_df = aggregate_all_forms()
        st.session_state['overall_data'] = aggregated_df
    else:
        aggregated_df = st.session_state['overall_data']

    if aggregated_df is None or aggregated_df.empty:
        st.error("No aggregated data available. Please refresh the data or check MongoDB collections.")
        st.stop()

    # Date filter
    st.sidebar.header("📅 Filter by Date")
    if 'submission_date' in aggregated_df.columns:
        show_all_dates = st.sidebar.checkbox("Show All Dates", value=True)
        if        not show_all_dates:
            unique_dates = sorted(aggregated_df['submission_date'].dropna().unique())
            if unique_dates:
                try:
                    # Define allowed dates based on project context
                    min_allowed_date = pd.to_datetime('2025-04-14').date()
                    max_allowed_date = datetime.now().date()
                    valid_dates = [d for d in unique_dates if pd.to_datetime(d).date() >= min_allowed_date]
                    if not valid_dates:
                        st.sidebar.warning("No data from April 14, 2025 onwards.")
                        selected_date = 'All'
                    else:
                        default_date = pd.to_datetime(min(valid_dates)).date()
                        selected_date = st.sidebar.date_input(
                            "Select Date:", 
                            value=default_date, 
                            min_value=min_allowed_date, 
                            max_value=max_allowed_date, 
                            format="YYYY-MM-DD"
                        )
                        selected_date = selected_date.strftime('%Y-%m-%d')
                except Exception as e:
                    st.sidebar.error(f"Error processing dates: {e}")
                    selected_date = 'All'
            else:
                selected_date = 'All'
                st.sidebar.warning("No valid dates available.")
        else:
            selected_date = 'All'
    else:
        selected_date = 'All'
        st.sidebar.info("Date filtering unavailable.")

    # Filter data by date
    filtered_df = aggregated_df.copy()
    if selected_date != 'All' and 'submission_date' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['submission_date'] == selected_date]
        if filtered_df.empty:
            st.warning(f"No data for selected date: {selected_date}")

    # Apply date restrictions
    if 'submission_date' in filtered_df.columns:
        min_allowed_date = pd.to_datetime('2025-04-14').date()
        filtered_df = filtered_df[pd.to_datetime(filtered_df['submission_date']).dt.date >= min_allowed_date]
        if filtered_df.empty and selected_date == 'All':
            st.warning("No data from April 14, 2025 onwards.")

    # Display total submissions
    total_submissions = len(filtered_df)
    st.markdown(f"**Total Submissions Across All Forms**: {total_submissions}")

    # Visualizations
    st.subheader("Submissions per Hour Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'submission_hour' in filtered_df.columns and not filtered_df.empty:
            hourly_counts = filtered_df['submission_hour'].value_counts().sort_index().reset_index(name='Count')
            hourly_counts['Time'] = hourly_counts['submission_hour'].astype(str).str.zfill(2) + ":00"
            missing_hours = filtered_df['submission_hour'].isna().sum()
            if missing_hours > 0:
                hourly_counts = pd.concat([hourly_counts, pd.DataFrame({'submission_hour': [None], 'Count': [missing_hours], 'Time': ['Missing']})])
            total_submissions = hourly_counts['Count'].sum()
            st.metric(label="Total Submissions", value=total_submissions)
            fig = px.bar(hourly_counts, x='Time', y='Count',
                         title=f'Submissions per Hour' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                         labels={'Time': 'Hour (IST)', 'Count': 'Submissions'})
            fig.update_traces(text=hourly_counts['Count'], textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'submission_hour' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    hourly_counts_user = user_df['submission_hour'].value_counts().sort_index().reset_index(name='Count')
                    hourly_counts_user['Time'] = hourly_counts_user['submission_hour'].astype(str).str.zfill(2) + ":00"
                    missing_hours_user = user_df['submission_hour'].isna().sum()
                    if missing_hours_user > 0:
                        hourly_counts_user = pd.concat([hourly_counts_user, pd.DataFrame({'submission_hour': [None], 'Count': [missing_hours_user], 'Time': ['Missing']})])
                    total_user = hourly_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=hourly_counts_user['Time'], y=hourly_counts_user['Count'],
                        text=hourly_counts_user['Count'], textposition='outside', name=submitter,
                        visible=(submitter == 'All'), customdata=[total_user] * len(hourly_counts_user),
                        hovertemplate='%{x}<br>Submissions: %{y}<extra></extra>'
                    )
                    traces.append(trace)
            if traces:
                updatemenus = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Submissions per Hour ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_user = dict(
                    data=traces, layout=dict(
                        updatemenus=updatemenus,
                        title=f"Submissions per Hour (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Hour (IST)"), yaxis=dict(title="Submissions"), showlegend=False
                    )
                )
                total_initial = traces[0]['customdata'][0]
                total_metric = st.metric(label="Total Submissions (All Users)", value=total_initial)
                st.plotly_chart(fig_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Submissions (All Users)" : "Total Submissions by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific hourly data.")
        else:
            st.info("No submitter data available.")

    # Gender Distribution
    st.subheader("Gender Distribution Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Gender' in filtered_df.columns:
            gender_counts = filtered_df['Gender'].value_counts().reset_index(name='Count')
            gender_counts.columns = ['Gender', 'Count']
            missing_gender = filtered_df['Gender'].isna().sum()
            if missing_gender > 0:
                gender_counts = pd.concat([gender_counts, pd.DataFrame({'Gender': ['Missing'], 'Count': [missing_gender]})])
            total_submissions = gender_counts['Count'].sum()
            st.metric(label="Total Respondents", value=total_submissions)
            fig_gender = px.pie(gender_counts, names='Gender', values='Count',
                                title=f'Gender Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'))
            fig_gender.update_traces(textinfo='value+percent', textposition='inside')
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.info("No gender data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Gender' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_gender = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    gender_counts_user = user_df['Gender'].value_counts().reset_index(name='Count')
                    gender_counts_user.columns = ['Gender', 'Count']
                    missing_gender_user = user_df['Gender'].isna().sum()
                    if missing_gender_user > 0:
                        gender_counts_user = pd.concat([gender_counts_user, pd.DataFrame({'Gender': ['Missing'], 'Count': [missing_gender_user]})])
                    total_gender_user = gender_counts_user['Count'].sum()
                    trace = dict(
                        type='pie', labels=gender_counts_user['Gender'], values=gender_counts_user['Count'],
                        textinfo='value+percent', textposition='inside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_gender_user], hovertemplate='%{label}<br>Count: %{value} (%{percent})<extra></extra>'
                    )
                    traces_gender.append(trace)
            if traces_gender:
                updatemenus_gender = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Gender Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_gender_user = dict(
                    data=traces_gender, layout=dict(
                        updatemenus=updatemenus_gender,
                        title=f"Gender Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        showlegend=True
                    )
                )
                total_gender_initial = traces_gender[0]['customdata'][0]
                total_metric_gender = st.metric(label="Total Respondents (Gender)", value=total_gender_initial)
                st.plotly_chart(fig_gender_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Respondents (Gender)" : "Total Respondents (Gender) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific gender data.")
        else:
            st.info("No gender or submitter data.")

    # Age Distribution
    st.subheader("Age Distribution Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Age_Group' in filtered_df.columns:
            age_counts = filtered_df['Age_Group'].value_counts().reset_index(name='Count')
            age_counts.columns = ['Age Group', 'Count']
            missing_age = filtered_df['Age'].isna().sum()
            if missing_age > 0:
                age_counts = pd.concat([age_counts, pd.DataFrame({'Age Group': ['Missing'], 'Count': [missing_age]})])
            total_submissions = age_counts['Count'].sum()
            st.metric(label="Total Respondents", value=total_submissions)
            fig_age = px.bar(age_counts, x='Age Group', y='Count',
                             title=f'Age Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'))
            fig_age.update_traces(text=age_counts['Count'], textposition='outside')
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("No age data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Age_Group' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_age = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    age_counts_user = user_df['Age_Group'].value_counts().reset_index(name='Count')
                    age_counts_user.columns = ['Age Group', 'Count']
                    missing_age_user = user_df['Age'].isna().sum()
                    if missing_age_user > 0:
                        age_counts_user = pd.concat([age_counts_user, pd.DataFrame({'Age Group': ['Missing'], 'Count': [missing_age_user]})])
                    total_age_user = age_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=age_counts_user['Age Group'], y=age_counts_user['Count'],
                        text=age_counts_user['Count'], textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_age_user], hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
                    )
                    traces_age.append(trace)
            if traces_age:
                updatemenus_age = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Age Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_age_user = dict(
                    data=traces_age, layout=dict(
                        updatemenus=updatemenus_age,
                        title=f"Age Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Age Group"), yaxis=dict(title="Respondents"), showlegend=False
                    )
                )
                total_age_initial = traces_age[0]['customdata'][0]
                total_metric_age = st.metric(label="Total Respondents (Age)", value=total_age_initial)
                st.plotly_chart(fig_age_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Respondents (Age)" : "Total Respondents (Age) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific age data.")
        else:
            st.info("No age or submitter data.")

    # Caste Distribution
    st.subheader("Caste Distribution Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Caste' in filtered_df.columns:
            caste_counts = filtered_df['Caste'].value_counts().reset_index(name='Count')
            caste_counts.columns = ['Caste', 'Count']
            missing_caste = filtered_df['Caste'].isna().sum()
            if missing_caste > 0:
                caste_counts = pd.concat([caste_counts, pd.DataFrame({'Caste': ['Missing'], 'Count': [missing_caste]})])
            total_submissions = caste_counts['Count'].sum()
            st.metric(label="Total Respondents", value=total_submissions)
            fig_caste = px.bar(caste_counts, x='Caste', y='Count',
                               title=f'Caste Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                               labels={'Caste': 'Caste', 'Count': 'Count'})
            fig_caste.update_traces(text=caste_counts['Count'], textposition='outside')
            fig_caste.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_caste, use_container_width=True)
        else:
            st.info("No caste data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Caste' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_caste = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    caste_counts_user = user_df['Caste'].value_counts().reset_index(name='Count')
                    caste_counts_user.columns = ['Caste', 'Count']
                    missing_caste_user = user_df['Caste'].isna().sum()
                    if missing_caste_user > 0:
                        caste_counts_user = pd.concat([caste_counts_user, pd.DataFrame({'Caste': ['Missing'], 'Count': [missing_caste_user]})])
                    total_caste_user = caste_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=caste_counts_user['Caste'], y=caste_counts_user['Count'],
                        text=caste_counts_user['Count'], textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_caste_user], hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
                    )
                    traces_caste.append(trace)
            if traces_caste:
                updatemenus_caste = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Caste Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_caste_user = dict(
                    data=traces_caste, layout=dict(
                        updatemenus=updatemenus_caste,
                        title=f"Caste Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Caste", tickangle=45), yaxis=dict(title="Count"), showlegend=False
                    )
                )
                total_caste_initial = traces_caste[0]['customdata'][0]
                total_metric_caste = st.metric(label="Total Respondents (Caste)", value=total_caste_initial)
                st.plotly_chart(fig_caste_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Respondents (Caste)" : "Total Respondents (Caste) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific caste data.")
        else:
            st.info("No caste or submitter data.")

    # Survey Duration
    st.subheader("Survey Duration Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**All Users**")
        if 'Duration_Group' in filtered_df.columns:
            duration_counts = filtered_df['Duration_Group'].value_counts().reset_index(name='Count')
            duration_counts.columns = ['Duration', 'Count']
            missing_duration = filtered_df['Duration'].isna().sum()
            if missing_duration > 0:
                duration_counts = pd.concat([duration_counts, pd.DataFrame({'Duration': ['Missing'], 'Count': [missing_duration]})])
            total_submissions = duration_counts['Count'].sum()
            st.metric(label="Total Submissions", value=total_submissions)
            fig_duration = px.bar(duration_counts, x='Duration', y='Count',
                                  title=f'Survey Duration Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'))
            fig_duration.update_traces(text=duration_counts['Count'], textposition='outside')
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No duration data available.")
    with col2:
        st.markdown("**By User**")
        if 'submittedBy' in filtered_df.columns and filtered_df['submittedBy'].notna().any() and 'Duration_Group' in filtered_df.columns:
            unique_submitters = sorted(set(filtered_df['submittedBy'].dropna()))
            submitter_options = ['All'] + unique_submitters
            traces_duration = []
            for submitter in submitter_options:
                user_df = filtered_df if submitter == 'All' else filtered_df[filtered_df['submittedBy'] == submitter]
                if not user_df.empty:
                    duration_counts_user = user_df['Duration_Group'].value_counts().reset_index(name='Count')
                    duration_counts_user.columns = ['Duration', 'Count']
                    missing_duration_user = user_df['Duration'].isna().sum()
                    if missing_duration_user > 0:
                        duration_counts_user = pd.concat([duration_counts_user, pd.DataFrame({'Duration': ['Missing'], 'Count': [missing_duration_user]})])
                    total_duration_user = duration_counts_user['Count'].sum()
                    trace = dict(
                        type='bar', x=duration_counts_user['Duration'], y=duration_counts_user['Count'],
                        text=duration_counts_user['Count'], textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_duration_user], hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
                    )
                    traces_duration.append(trace)
            if traces_duration:
                updatemenus_duration = [dict(
                    buttons=[dict(
                        label=s, method='update',
                        args=[{'visible': [s == opt for opt in submitter_options]},
                              {'title': f"Survey Duration Distribution ({s if s == 'All' else f'by {s}'})" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)')}]
                    ) for s in submitter_options],
                    direction='down', showactive=True, x=1.15, xanchor='right', y=1.2, yanchor='top'
                )]
                fig_duration_user = dict(
                    data=traces_duration, layout=dict(
                        updatemenus=updatemenus_duration,
                        title=f"Survey Duration Distribution (All Users)" + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                        xaxis=dict(title="Duration"), yaxis=dict(title="Submissions"), showlegend=False
                    )
                )
                total_duration_initial = traces_duration[0]['customdata'][0]
                total_metric_duration = st.metric(label="Total Submissions (Duration)", value=total_duration_initial)
                st.plotly_chart(fig_duration_user, use_container_width=True)
                st.markdown("""
                    <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.addEventListener('plotly_restyle', function(event) {
                            var plotlyData = event.detail[0];
                            var visibleTraceIndex = plotlyData.visible.indexOf(true);
                            var total = plotlyData.data[visibleTraceIndex].customdata[0];
                            var label = visibleTraceIndex === 0 ? "Total Submissions (Duration)" : "Total Submissions (Duration) by " + plotlyData.data[visibleTraceIndex].name;
                            var metricElement = document.querySelector('div[data-testid="stMetricLabel"]');
                            var valueElement = document.querySelector('div[data-testid="stMetricValue"]');
                            if (metricElement && valueElement) {
                                metricElement.innerText = label;
                                valueElement.innerText = total;
                            }
                        });
                    });
                    </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No user-specific duration data.")
        else:
            st.info("No duration or submitter data.")

    # Geographic Distribution
    st.subheader("Geographic Distribution")
    if 'Latitude' in filtered_df.columns and 'Longitude' in filtered_df.columns:
        map_df = filtered_df[filtered_df['Latitude'].notna() & filtered_df['Longitude'].notna() & (filtered_df['GeoError'].isna())]
        invalid_df = filtered_df[filtered_df['Latitude'].isna() | filtered_df['Longitude'].isna() | filtered_df['GeoError'].notna()]
        st.markdown("**Geographic Data Summary**")
        total_submissions = len(filtered_df)
        valid_coords = len(map_df)
        invalid_coords = len(invalid_df)
        st.write(f"Total Submissions: {total_submissions}")
        st.write(f"Valid Coordinates: {valid_coords}")
        st.write(f"Missing/Invalid Coordinates: {invalid_coords}")

        if not invalid_df.empty:
            st.markdown("**Invalid Coordinates Analysis**")
            error_counts = invalid_df['GeoError'].value_counts().reset_index(name='Count')
            error_counts.columns = ['Error Reason', 'Count']
            st.write("Reasons for Invalid Coordinates:")
            st.dataframe(error_counts)
            with st.expander("View Invalid Coordinates Sample"):
                st.dataframe(invalid_df[['submittedBy', 'Block', 'Village', 'GeoError', 'Form_Name']].head(10))

        if not map_df.empty:
            with st.expander("View Valid Coordinates Sample"):
                st.dataframe(map_df[['submittedBy', 'Latitude', 'Longitude', 'Block', 'Village', 'Form_Name']].head(10))

            map_df = map_df.copy()
            map_df['Address'] = map_df.apply(
                lambda row: get_address(row['Latitude'], row['Longitude'], AZURE_MAPS_API_KEY),
                axis=1
            )

            map_data = pd.DataFrame({
                "lat": map_df['Latitude'],
                "lon": map_df['Longitude'],
                "tooltip": map_df.apply(
                    lambda row: f"Address: {row['Address']}\nSubmitted By: {row['submittedBy'] or 'Unknown'}\nBlock: {row['Block'] or 'Unknown'}\nVillage: {row['Village'] or 'Unknown'}\nForm: {row['Form_Name']}",
                    axis=1
                ),
                "submitter": map_df['submittedBy'].fillna('Unknown'),
                "block": map_df['Block'].fillna('Unknown'),
                "village": map_df['Village'].fillna('Unknown'),
                "address": map_df['Address'],
                "form_name": map_df['Form_Name']
            })

            icon_data = {
                "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
                "width": 128,
                "height": 128,
                "anchorY": 128
            }
            map_data["icon_data"] = [icon_data] * len(map_data)

            lat_mean = map_data['lat'].mean() if not map_data['lat'].empty else 10.5
            lon_mean = map_data['lon'].mean() if not map_data['lon'].empty else 78
            zoom_level = min(10, max(5, 10 - len(map_data) // 1000))

            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/streets-v11",
                initial_view_state=pdk.ViewState(
                    latitude=lat_mean,
                    longitude=lon_mean,
                    zoom=zoom_level,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        "IconLayer",
                        data=map_data,
                        get_icon="icon_data",
                        get_size=4,
                        size_scale=15,
                        get_position=["lon", "lat"],
                        pickable=True
                    )
                ],
                tooltip={"text": "{tooltip}"}
            ))

            st.metric(label="Total Geotagged Submissions", value=valid_coords)

            if 'block' in map_data.columns and map_data['block'].notna().any():
                block_counts = map_data['block'].value_counts()
                st.markdown("**Block-wise Distribution:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(block_counts.reset_index().rename(columns={'index': 'Block', 'block': 'Count'}))
                with col2:
                    fig_block = px.pie(names=block_counts.index, values=block_counts.values, title='Block-wise Distribution')
                    st.plotly_chart(fig_block, use_container_width=True)
    else:
        st.info("No geographic data available.")

    # Data Quality
    st.subheader("Data Quality Information")
    total_submissions = len(filtered_df)
    missing_gender = filtered_df['Gender'].isna().sum() if 'Gender' in filtered_df.columns else 0
    missing_age = filtered_df['Age'].isna().sum() if 'Age' in filtered_df.columns else 0
    missing_caste = filtered_df['Caste'].isna().sum() if 'Caste' in filtered_df.columns else 0
    missing_coords = filtered_df[filtered_df['Latitude'].isna() | filtered_df['Longitude'].isna()].shape[0] if 'Latitude' in filtered_df.columns else 0
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Missing Gender", value=missing_gender, delta=f"{round(missing_gender/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")
    with col2:
        st.metric(label="Missing Age", value=missing_age, delta=f"{round(missing_age/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")
    with col3:
        st.metric(label="Missing Caste", value=missing_caste, delta=f"{round(missing_caste/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")
    with col4:
        st.metric(label="Missing Coordinates", value=missing_coords, delta=f"{round(missing_coords/total_submissions*100, 1)}%" if total_submissions > 0 else "N/A")

    # Download Data
    st.subheader("Download Aggregated Data")
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Aggregated Data as CSV",
            data=csv,
            file_name=f"Aggregated_TNMaster_data{'_' + str(selected_date) if selected_date != 'All' else ''}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data to download.")

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: gray; font-size: 12px;">
            TNMaster Overall Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data source: MongoDB (ODK Central) | Aggregated across all forms
        </div>
        """, unsafe_allow_html=True)

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['otp_sent'] = False
        st.session_state['otp'] = None
        st.session_state['email'] = ""
        st.session_state['attempts'] = 0
        st.session_state['page'] = "Login"
        st.success("Logged out successfully!")
        st.rerun()

# --- Main Function ---
def main():
    if st.session_state['page'] == "Login":
        login_page()
    elif st.session_state['page'] == "Main Dashboard":
        main_dashboard()
    elif st.session_state['page'] == "Overall Dashboard":
        overall_dashboard()

if __name__ == "__main__":
    main()