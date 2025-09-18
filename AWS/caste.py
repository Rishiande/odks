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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time
# --- Streamlit setup ---
st.set_page_config(page_title="Delta Tracker Ariyalur Master", layout="wide")
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
if 'selected_project' not in st.session_state:
    st.session_state['selected_project'] = "Delta Tracker Ariyalur"
if 'selected_form' not in st.session_state:
    st.session_state['selected_form'] = "149-Ariyalur Tracking Survey 08-2025 ODK XLSForm"
# --- Email configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "rishiande9999@gmail.com"
EMAIL_PASSWORD = "xizdjdbjsjerztbr"
# --- Valid credentials ---
VALID_CREDENTIALS = {
    "rishi": {
        "password": "rishi",
        "email": "rishiande9999@gmail.com"
    },
    "Pramanya": {
        "password": "Pramanya@123",
        "email": "pramanyastrategy@gmail.com"
    },
    "Anil" : {
        "password": "Anil@123",
        "email": "anil@pramanyastrategy.com"
    },
    "Bharath" : {
        "password": "Bharath@123",
        "email": "bharath01psc@gmail.com"
    }
}
# --- Form mappings ---
forms = {
    "Server 1": {
        "Delta Tracker Mayiladuthurai": {
            "160-Sirkazhi (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 10, "form_id": "160-Sirkazhi (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "161-Mayiladuthurai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 10, "form_id": "161-Mayiladuthurai Tracking Survey 08-2025 ODK XLSForm"},
            "162-Poompuhar Tracking Survey 08-2025 ODK XLSForm": {"project_id": 10, "form_id": "162-Poompuhar Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Pudukkottai": {
            "178-Gandharvakottai (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "178-Gandharvakottai (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "179-Viralimalai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "179-Viralimalai Tracking Survey 08-2025 ODK XLSForm"},
            "180-Pudukkottai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "180-Pudukkottai Tracking Survey 08-2025 ODK XLSForm"},
            "181-Thirumayam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "181-Thirumayam Tracking Survey 08-2025 ODK XLSForm"},
            "182-Alangudi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "182-Alangudi Tracking Survey 08-2025 ODK XLSForm"},
            "183-Aranthangi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "183-Aranthangi racking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Ariyalur": {
            "149-Ariyalur Tracking Survey 08-2025 ODK XLSForm": {"project_id": 9, "form_id": "149-Ariyalur Tracking Survey 08-2025 ODK XLSForm"},
            "150-Jayankondam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 9, "form_id": "150-Jayankondam Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Perambalur": {
            "147-Perambalur (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 3, "form_id": "147-Perambalur (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "148-Kunnam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 3, "form_id": "148-Kunnam Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Thiruvarur": {
            "166-Thiruthuraipoondi (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 6, "form_id": "166-Thiruthuraipoondi (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "167-Mannargudi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 6, "form_id": "167-Mannargudi Tracking Survey 08-2025 ODK XLSForm"},
            "168-Thiruvarur Tracking Survey 08-2025 ODK XLSForm": {"project_id": 6, "form_id": "168-Thiruvarur Tracking Survey 08-2025 ODK XLSForm"},
            "169-Nannilam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 6, "form_id": "169-Nannilam Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Nagapattinam": {
            "163-Nagapattinam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 5, "form_id": "163-Nagapattinam Tracking Survey 08-2025 ODK XLSForm"},
            "164-Kilvelur (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 5, "form_id": "164-Kilvelur (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "165-Vedaranyam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 5, "form_id": "165-Vedaranyam Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Cuddalore": {
            "151-Tittakudi (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "151-Tittakudi (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "152-Vriddhachalam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "152-Vriddhachalam Tracking Survey 08-2025 ODK XLSForm"},
            "153-Neyveli Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "153-Neyveli Tracking Survey 08-2025 ODK XLSForm"},
            "154-Panruti Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "154-Panruti Tracking Survey 08-2025 ODK XLSForm"},
            "155-Cuddalore Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "155-Cuddalore Tracking Survey 08-2025 ODK XLSForm"},
            "156-Kurinjipadi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "156-Kurinjipadi Tracking Survey 08-2025 ODK XLSForm"},
            "157-Bhuvanagiri Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "157-Bhuvanagiri Tracking Survey 08-2025 ODK XLSForm"},
            "158-Chidambaram Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "158-Chidambaram Tracking Survey 08-2025 ODK XLSForm"},
            "159-Kattumannarkoil (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 4, "form_id": "159-Kattumannarkoil (SC) Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Thanjavur": {
            "170-Thiruvidaimarudur (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "170-Thiruvidaimarudur (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "171-Kumbakonam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "171-Kumbakonam Tracking Survey 08-2025 ODK XLSForm"},
            "172-Papanasam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "172-Papanasam Tracking Survey 08-2025 ODK XLSForm"},
            "173-Thiruvaiyaru Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "173-Thiruvaiyaru Tracking Survey 08-2025 ODK XLSForm"},
            "174-Thanjavur Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "174-Thanjavur Tracking Survey 08-2025 ODK XLSForm"},
            "175-Orathanadu Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "175-Orathanadu Tracking Survey 08-2025 ODK XLSForm"},
            "176-Pattukkottai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "176-Pattukkottai Tracking Survey 08-2025 ODK XLSForm"},
            "177-Peravurani Tracking Survey 08-2025 ODK XLSForm": {"project_id": 7, "form_id": "177-Peravurani Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracker Thiruchirapalli": {
            "138-Manapparai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "138-Manapparai Tracking Survey 08-2025 ODK XLSForm"},
            "139-Srirangam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "139-Srirangam Tracking Survey 08-2025 ODK XLSForm"},
            "140-Tiruchirappalli (West) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "140-Tiruchirappalli (West) Tracking Survey 08-2025 ODK XLSForm"},
            "141-Tiruchirappalli (East) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "141-Tiruchirappalli (East) Tracking Survey 08-2025 ODK XLSForm"},
            "142-Thiruverumbur Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "142-Thiruverumbur Tracking Survey 08-2025 ODK XLSForm"},
            "143-Lalgudi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "143-Lalgudi Tracking Survey 08-2025 ODK XLSForm"},
            "144-Manachanallur Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "144-Manachanallur Tracking Survey 08-2025 ODK XLSForm"},
            "145-Musiri Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "145-Musiri Tracking Survey 08-2025 ODK XLSForm"},
            "146-Thuraiyur (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 11, "form_id": "146-Thuraiyur (SC) Tracking Survey 08-2025 ODK XLSForm"}
        },
        "South Tracker VirudhuNagar": {
            "202-Rajapalayam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 13, "form_id": "202-Rajapalayam Tracking Survey 08-2025 ODK XLSForm"},
            "203-Srivilliputhur (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 13, "form_id": "203-Srivilliputhur (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "204-Sattur Tracking Survey 08-2025 ODK XLSForm": {"project_id": 13, "form_id": "204-Sattur Tracking Survey 08-2025 ODK XLSForm"},
            "205-Sivakasi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 13, "form_id": "205-Sivakasi Tracking Survey 08-2025 ODK XLSForm"},
            "206-Virudhunagar Tracking Survey 08-2025 ODK XLSForm": {"project_id": 13, "form_id": "206-Virudhunagar Tracking Survey 08-2025 ODK XLSForm"},
            "207-Aruppukkottai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 13, "form_id": "207-Aruppukkottai Tracking Survey 08-2025 ODK XLSForm"},
            "208-Tiruchuli Tracking Survey 08-2025 ODK XLSForm": {"project_id": 13, "form_id": "208-Tiruchuli Tracking Survey 08-2025 ODK XLSForm"}
        },
        "South Tracker Tirunelveli": {
            "224-Tirunelveli Tracking Survey 08-2025 ODK XLSForm": {"project_id": 14, "form_id": "224-Tirunelveli Tracking Survey 08-2025 ODK XLSForm"},
            "225-Ambasamudram Tracking Survey 08-2025 ODK XLSForm": {"project_id": 14, "form_id": "225-Ambasamudram Tracking Survey 08-2025 ODK XLSForm"},
            "226-Palayamkottai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 14, "form_id": "226-Palayamkottai Tracking Survey 08-2025 ODK XLSForm"},
            "227-Nanguneri Tracking Survey 08-2025 ODK XLSForm": {"project_id": 14, "form_id": "227-Nanguneri Tracking Survey 08-2025 ODK XLSForm"},
            "228-Radhapuram Tracking Survey 08-2025 ODK XLSForm": {"project_id": 14, "form_id": "228-Radhapuram Tracking Survey 08-2025 ODK XLSForm"}
        },
        "South Tracker Madurai": {
            "188-Melur Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "188-Melur Tracking Survey 09-2025 ODK XLSForm"},
            "189-Madurai East Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "189-Madurai East Tracking Survey 09-2025 ODK XLSForm"},
            "190-Sholavandan (SC) Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "190-Sholavandan (SC) Tracking Survey 09-2025 ODK XLSForm"},
            "191-Madurai North Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "191-Madurai North Tracking Survey 09-2025 ODK XLSForm"},
            "192-Madurai South Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "192-Madurai South Tracking Survey 09-2025 ODK XLSForm"},
            "193-Madurai Central Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "193-Madurai Central Tracking Survey 09-2025 ODK XLSForm"},
            "194-Madurai West Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "194-Madurai West Tracking Survey 09-2025 ODK XLSForm"},
            "195-Thiruparankundram Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "195-Thiruparankundram Tracking Survey 09-2025 ODK XLSForm"},
            "196-Thirumangalam Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "196-Thirumangalam Tracking Survey 09-2025 ODK XLSForm"},
            "197-Usilampatti Tracking Survey 09-2025 ODK XLSForm": {"project_id": 19, "form_id": "197-Usilampatti Tracking Survey 09-2025 ODK XLSForm"}
        },
        "South Tracker Ramanathapuram": {
            "209-Paramakudi (SC) Tracking Survey 09-2025 ODK XLSForm": {"project_id": 16, "form_id": "209-Paramakudi (SC) Tracking Survey 09-2025 ODK XLSForm"},
            "210-Tiruvadanai Tracking Survey 09-2025 ODK XLSForm": {"project_id": 16, "form_id": "210-Tiruvadanai Tracking Survey 09-2025 ODK XLSForm"},
            "211-Ramanathapuram Tracking Survey 09-2025 ODK XLSForm": {"project_id": 16, "form_id": "211-Ramanathapuram Tracking Survey 09-2025 ODK XLSForm"},
            "212-Mudhukulathur Tracking Survey 09-2025 ODK XLSForm": {"project_id": 16, "form_id": "212-Mudhukulathur Tracking Survey 09-2025 ODK XLSForm"}
        },
        "South Tracker Sivaganga": {
            "184-Karaikudi Tracking Survey 09-2025 ODK XLSForm": {"project_id": 17, "form_id": "184-Karaikudi Tracking Survey 09-2025 ODK XLSForm"},
            "185-Tiruppattur Tracking Survey 09-2025 ODK XLSForm": {"project_id": 17, "form_id": "185-Tiruppattur Tracking Survey 09-2025 ODK XLSForm"},
            "186-Sivaganga Tracking Survey 09-2025 ODK XLSForm": {"project_id": 17, "form_id": "186-Sivaganga Tracking Survey 09-2025 ODK XLSForm"},
            "187-Manamadurai (SC) Tracking Survey 09-2025 ODK XLSForm": {"project_id": 17, "form_id": "187-Manamadurai (SC) Tracking Survey 09-2025 ODK XLSForm"}
        },
        "South Tracker Tenkasi": {
            "219-Sankarankovil (SC) Tracking Survey 09-2025 ODK XLSForm": {"project_id": 15, "form_id": "219-Sankarankovil (SC) Tracking Survey 09-2025 ODK XLSForm"},
            "220-Vasudevanallur (SC) Tracking Survey 09-2025 ODK XLSForm": {"project_id": 15, "form_id": "220-Vasudevanallur (SC) Tracking Survey 09-2025 ODK XLSForm"},
            "221-Kadayanallur Tracking Survey 09-2025 ODK XLSForm": {"project_id": 15, "form_id": "221-Kadayanallur Tracking Survey 09-2025 ODK XLSForm"},
            "222-Tenkasi Tracking Survey 09-2025 ODK XLSForm": {"project_id": 15, "form_id": "222-Tenkasi Tracking Survey 09-2025 ODK XLSForm"},
            "223-Alangulam Tracking Survey 09-2025 ODK XLSForm": {"project_id": 15, "form_id": "223-Alangulam Tracking Survey 09-2025 ODK XLSForm"}
        },
        "South Tracker Thoothukudi": {
            "213-Vilathikulam Tracking Survey 09-2025 ODK XLSForm": {"project_id": 18, "form_id": "213-Vilathikulam Tracking Survey 09-2025 ODK XLSForm"},
            "214-Thoothukkudi Tracking Survey 09-2025 ODK XLSForm": {"project_id": 18, "form_id": "214-Thoothukkudi Tracking Survey 09-2025 ODK XLSForm"},
            "215-Tiruchendur Tracking Survey 09-2025 ODK XLSForm": {"project_id": 18, "form_id": "215-Tiruchendur Tracking Survey 09-2025 ODK XLSForm"},
            "216-Srivaikuntam Tracking Survey 09-2025 ODK XLSForm": {"project_id": 18, "form_id": "216-Srivaikuntam Tracking Survey 09-2025 ODK XLSForm"},
            "217-Ottapidaram (SC) Tracking Survey 09-2025 ODK XLSForm": {"project_id": 18, "form_id": "217-Ottapidaram (SC) Tracking Survey 09-2025 ODK XLSForm"},
            "218-Kovilpatti Tracking Survey 09-2025 ODK XLSForm": {"project_id": 18, "form_id": "218-Kovilpatti Tracking Survey 09-2025 ODK XLSForm"}
        },
        "South Tracker Theni": {
            "198-Andipatti Tracking Survey 09-2025 ODK XLSForm": {"project_id": 20, "form_id": "198-Andipatti Tracking Survey 09-2025 ODK XLSForm"},
            "199-Periyakulam (SC) Tracking Survey 09-2025 ODK XLSForm": {"project_id": 20, "form_id": "199-Periyakulam (SC) Tracking Survey 09-2025 ODK XLSForm"},
            "200-Bodinayakanur Tracking Survey 09-2025 ODK XLSForm": {"project_id": 20, "form_id": "200-Bodinayakanur Tracking Survey 09-2025 ODK XLSForm"},
            "201-Cumbum Tracking Survey 09-2025 ODK XLSForm": {"project_id": 20, "form_id": "201-Cumbum Tracking Survey 09-2025 ODK XLSForm"}
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
    st.title("🔒 Delta Tracker Ariyalur Master Login")
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
            df['submission_datetime'] = pd.to_datetime(df['start'], errors='coerce')
            df['end_datetime'] = pd.to_datetime(df['end'], errors='coerce')
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
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lon}",
            "key": key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK' and data['results']:
                return data['results'][0]['formatted_address']
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
    for project in forms["Server 1"]:
        for form_name, form_info in forms["Server 1"][project].items():
            project_id = form_info['project_id']
            form_id = form_info['form_id']
            collection_name = f"submissions_Server_1_{project_id}_{form_id.replace(' ', '_').replace('-', '_').replace('.', '_').replace('(', '').replace(')', '')}"
            collection = db[collection_name]
            df = load_from_mongodb(collection)
            if df is not None:
                df['Form_Name'] = form_name
                df['Project'] = project
                df['Server'] = "Server 1"
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
    base_url_prefix = "https://tnodk04.indiaintentions.com"
    for project in forms["Server 1"]:
        for form_name, form_info in forms["Server 1"][project].items():
            project_id = form_info['project_id']
            form_id = form_info['form_id']
            collection_name = f"submissions_Server_1_{project_id}_{form_id.replace(' ', '_').replace('-', '_').replace('.', '_').replace('(', '').replace(')', '')}"
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
    GOOGLE_MAPS_API_KEY = "AIzaSyD3lO5STzGksBLVkH8LHViyzx0HjB-wLHQ"
    st.title("Delta Tracker Ariyalur Dashboard")
    st.write(f"Welcome, {st.session_state['username']}!")
    # Sidebar navigation
    st.sidebar.header("Navigation")
    dashboard_option = st.sidebar.radio(
        "Select Dashboard:",
        ["Form-wise Dashboard", "Overall Dashboard"],
        index=0,
        key="dashboard_selector_main"
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
    st.title("📊 Delta Tracker Ariyalur: Ariyalur Landscape Survey Dashboard (August 2025)")
    # Form selection sidebar
    st.sidebar.header("Data Selection")
    selected_project = st.sidebar.selectbox(
        "Select Project:",
        list(forms["Server 1"].keys()),
        index=list(forms["Server 1"].keys()).index(st.session_state['selected_project']),
        key="project_selector"
    )
    form_options = list(forms["Server 1"][selected_project].keys())
    selected_form = st.sidebar.selectbox(
        "Select Form:",
        form_options,
        index=form_options.index(st.session_state['selected_form']) if st.session_state['selected_form'] in form_options else 0,
        key="form_selector"
    )
    # Update session state
    st.session_state['selected_project'] = selected_project
    st.session_state['selected_form'] = selected_form
    # Get project and form ID
    selected_project_id = forms["Server 1"][selected_project][selected_form]["project_id"]
    selected_form_id = forms["Server 1"][selected_project][selected_form]["form_id"]
    base_url_prefix = "https://tnodk04.indiaintentions.com"
    BASE_URL = f"{base_url_prefix}/v1/projects/{selected_project_id}/forms/{urllib.parse.quote(selected_form_id)}.svc/Submissions"
    # Collection name
    form_collection_name = f"submissions_Server_1_{selected_project_id}_{selected_form_id.replace(' ', '_').replace('-', '_').replace('.', '_').replace('(', '').replace(')', '')}"
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
                    min_date = pd.to_datetime(min(unique_dates)).date()
                    max_date = pd.to_datetime(max(unique_dates)).date()
                    default_date = min_date
                    selected_date = st.sidebar.date_input(
                        "Select Date:", value=default_date, min_value=min_date, max_value=max_date, format="YYYY-MM-DD"
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
    if selected_project in ["Delta Tracker Ariyalur"]:
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
            caste_counts['Percentage'] = (caste_counts['Count'] / total_submissions * 100).round(1)
            st.metric(label="Total Respondents", value=total_submissions)
            fig_caste = px.bar(caste_counts, x='Caste', y='Percentage',
                               title=f'Caste Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                               labels={'Caste': 'Caste', 'Percentage': 'Percentage'})
            fig_caste.update_traces(text=caste_counts['Percentage'].astype(str) + '%', textposition='outside')
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
                    caste_counts_user['Percentage'] = (caste_counts_user['Count'] / total_caste_user * 100).round(1)
                    trace = dict(
                        type='bar', x=caste_counts_user['Caste'], y=caste_counts_user['Percentage'],
                        text=caste_counts_user['Percentage'].astype(str) + '%', textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_caste_user], hovertemplate='%{x}<br>Percentage: %{y}%<extra></extra>'
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
                        xaxis=dict(title="Caste", tickangle=45), yaxis=dict(title="Percentage"), showlegend=False
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
            Delta Tracker Ariyalur Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data source: MongoDB (ODK Central) | Current Form: {form_title}
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
    ODK_USERNAME = os.getenv("ODK_USERNAME")
    ODK_PASSWORD = os.getenv("ODK_PASSWORD")
    MONGO_URI = os.getenv("MONGO_URI")
    GOOGLE_MAPS_API_KEY = "AIzaSyCkL2eWj4f_LX_ORf-Cf3Hwc-HhZafbcoc"
    st.title("📊 Delta Tracker Ariyalur: Overall Ariyalur Landscape Survey Dashboard (August 2025)")
    st.write(f"Welcome, {st.session_state['username']}! This dashboard summarizes data across all forms.")
    # Sidebar navigation
    st.sidebar.header("Navigation")
    dashboard_option = st.sidebar.radio(
        "Select Dashboard:",
        ["Form-wise Dashboard", "Overall Dashboard"],
        index=1,
        key="dashboard_selector_overall"
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
        if not show_all_dates:
            unique_dates = sorted(aggregated_df['submission_date'].dropna().unique())
            if unique_dates:
                try:
                    min_date = pd.to_datetime(min(unique_dates)).date()
                    max_date = pd.to_datetime(max(unique_dates)).date()
                    default_date = min_date
                    selected_date = st.sidebar.date_input(
                        "Select Date:",
                        value=default_date,
                        min_value=min_date,
                        max_value=max_date,
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
    # Display total submissions
    total_submissions = len(filtered_df)
    st.markdown(f"**Total Submissions Across All Forms**: {total_submissions}")
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
            caste_counts['Percentage'] = (caste_counts['Count'] / total_submissions * 100).round(1)
            st.metric(label="Total Respondents", value=total_submissions)
            fig_caste = px.bar(caste_counts, x='Caste', y='Percentage',
                               title=f'Caste Distribution' + (f' on {selected_date}' if selected_date != 'All' else ' (Overall)'),
                               labels={'Caste': 'Caste', 'Percentage': 'Percentage'})
            fig_caste.update_traces(text=caste_counts['Percentage'].astype(str) + '%', textposition='outside')
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
                    caste_counts_user['Percentage'] = (caste_counts_user['Count'] / total_caste_user * 100).round(1)
                    trace = dict(
                        type='bar', x=caste_counts_user['Caste'], y=caste_counts_user['Percentage'],
                        text=caste_counts_user['Percentage'].astype(str) + '%', textposition='outside', name=submitter, visible=(submitter == 'All'),
                        customdata=[total_caste_user], hovertemplate='%{x}<br>Percentage: %{y}%<extra></extra>'
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
                        xaxis=dict(title="Caste", tickangle=45), yaxis=dict(title="Percentage"), showlegend=False
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
    # Download Aggregated Data
    st.subheader("Download Aggregated Data")
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Aggregated Data as CSV",
            data=csv,
            file_name=f"Aggregated_Delta Tracker Ariyalur_data{'_' + str(selected_date) if selected_date != 'All' else ''}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data to download.")
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: gray; font-size: 12px;">
            Delta Tracker Ariyalur Overall Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data source: MongoDB (ODK Central) | Aggregated across all forms
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