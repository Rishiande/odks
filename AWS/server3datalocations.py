import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
from datetime import datetime
from dateutil import parser
from io import BytesIO
import logging
import os
from dotenv import load_dotenv
import urllib.parse
from pydub import AudioSegment
import math

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ODK Configuration
ODK_CONFIG = {
    "BASE_URL": "https://tnodk03.indiaintentions.com",
    "USERNAME": os.getenv("ODK_USERNAME", "rushi@tnodk01.ii.com"),
    "PASSWORD": os.getenv("ODK_PASSWORD", "rushi2025&")
}

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyB2RC76X859_0UQKBwqTBwRc6eVnfdQN88"

# Project configurations
PROJECTS = {
    "01 Bhaskar Srinivas TN Landscape Survey": {
        "project_id": 4,
        "excel_base_path": r"01 Bhaskar Srinivas TN Landscape Survey",
        "forms": {
            "60-Pappireddippatti": {
                "form_id": "60-Pappireddippatti Landscape Survey 04-2025",
                "excel_file": "60. PAPPIREDDIPPATTI.xlsx",
                "sheet_name": "60. PAPPIREDDIPPATTI",
                "geocode_city": "Pappireddippatti, Tamil Nadu, India"
            },
            "77-Ulundurpettai": {
                "form_id": "77-Ulundurpettai Landscape Survey 04-2025",
                "excel_file": "77-Ulundurpettai.xlsx",
                "sheet_name": "77-Ulundurpettai",
                "geocode_city": "Ulundurpettai, Tamil Nadu, India"
            },
            "79-Sankarapuram": {
                "form_id": "79-Sankarapuram Landscape Survey 04-2025",
                "excel_file": "79. Sankarapuram.xlsx",
                "sheet_name": "79. Sankarapuram",
                "geocode_city": "Sankarapuram, Tamil Nadu, India"
            },
            "84-Omalur": {
                "form_id": "84-Omalur Landscape Survey 04-2025",
                "excel_file": "84. Omalur.xlsx",
                "sheet_name": "84. Omalur",
                "geocode_city": "Omalur, Tamil Nadu, India"
            },
            "160-Sirkazhi": {
                "form_id": "160-Sirkazhi (SC) Landscape Survey 04-2025",
                "excel_file": "160.Sirkazhi.xlsx",  # Fixed typo: Sizkazhi -> Sirkazhi
                "sheet_name": "160.Sirkazhi",
                "geocode_city": "Sirkazhi, Tamil Nadu, India"
            },
            "165-Vedaranyam": {
                "form_id": "165-Vedaranyam Landscape Survey 04-2025",
                "excel_file": "165. Vedharanyam.xlsx",
                "sheet_name": "165. Vedharanyam",
                "geocode_city": "Vedaranyam, Tamil Nadu, India"
            },
            "166-Thiruthuraipoondi": {
                "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025",
                "excel_file": "166. Thiruthuraipoondi.xlsx",
                "sheet_name": "166. Thiruthuraipoondi",
                "geocode_city": "Thiruthuraipoondi, Tamil Nadu, India"
            },
            "167-Mannargudi": {
                "form_id": "167-Mannargudi Landscape Survey 04-2025",
                "excel_file": "167. Mannargudi.xlsx",
                "sheet_name": "167. Mannargudi",
                "geocode_city": "Mannargudi, Tamil Nadu, India"
            },
            "168-Thiruvarur": {
                "form_id": "168-Thiruvarur Landscape Survey 04-2025",
                "excel_file": "168. Thiruvarur.xlsx",
                "sheet_name": "168. Thiruvarur",
                "geocode_city": "Thiruvarur, Tamil Nadu, India"
            },
            "169-Nannilam": {
                "form_id": "169-Nannilam Landscape Survey 04-2025",
                "excel_file": "169. Nannilam.xlsx",
                "sheet_name": "169. Nannilam",
                "geocode_city": "Nannilam, Tamil Nadu, India"
            },
            "177-Peravurani": {
                "form_id": "177-Peravurani Landscape Survey 04-2025",
                "excel_file": "177. Peravurani.xlsx",
                "sheet_name": "177. Peravurani",
                "geocode_city": "Peravurani, Tamil Nadu, India"
            },
            "178-Gandharvakottai": {
                "form_id": "178-Gandharvakottai (SC) Landscape Survey 04-2025",
                "excel_file": "178. Gandharvakottai.xlsx",
                "sheet_name": "178. Gandharvakottai",
                "geocode_city": "Gandharvakottai, Tamil Nadu, India"
            },
            "200-Bodinayakanur": {
                "form_id": "200-Bodinayakanur Landscape Survey 04-2025",
                "excel_file": "200. Bodinayakanur.xlsx",
                "sheet_name": "200. Bodinayakanur",
                "geocode_city": "Bodinayakanur, Tamil Nadu, India"
            },
            "Test TN Landscape Survey 05-2025": {
                "form_id": "Test TN Landscape Survey 05-2025",
                "excel_file": "Test TN Landscape Survey 05-2025.xlsx",
                "sheet_name": "Test TN Landscape Survey 05-2025",
                "geocode_city": "Tamil Nadu, India"
            }
        }
    },
    "01 Laxmi Narayana TN Landscape": {
        "project_id": 5,
        "excel_base_path": r"01 Laxmi Narayana TN Landscape",
        "forms": {
            "78-Rishivandiyam": {
                "form_id": "78-Rishivandiyam Landscape Survey 04-2025 copy 42",
                "excel_file": "78. Rishivandiyam.xlsx",
                "sheet_name": "78. Rishivandiyam",
                "geocode_city": "Rishivandiyam, Tamil Nadu, India"
            },
            "80-Kallakurichi": {
                "form_id": "80-Kallakurichi (SC) Landscape Survey 04-2025",
                "excel_file": "80. Kallakurichi.xlsx",
                "sheet_name": "80. Kallakurichi",
                "geocode_city": "Kallakurichi, Tamil Nadu, India"
            },
            "127-Palani": {
                "form_id": "127-Palani Landscape Survey 04-2025",
                "excel_file": "127. Palani.xlsx",
                "sheet_name": "127. Palani",
                "geocode_city": "Palani, Tamil Nadu, India"
            },
            "148-Kunnam": {
                "form_id": "148-Kunnam Landscape Survey 04-2025",
                "excel_file": "148. Kunnam.xlsx",
                "sheet_name": "148. Kunnam",
                "geocode_city": "Kunnam, Tamil Nadu, India"
            }
        }
    },
    "01 Ravi Sai TN Landscape": {
        "project_id": 6,
        "excel_base_path": r"01 Ravi Sai TN Landscape",
        "forms": {
            "4-Tiruvallur": {
                "form_id": "4-Tiruvallur Landscape Survey 04-2025 copy 2",
                "excel_file": "4. Tiruvallur.xlsx",
                "sheet_name": "4. Tiruvallur",
                "geocode_city": "Tiruvallur, Tamil Nadu, India"
            },
            "17-Royapuram": {
                "form_id": "17-Royapuram Landscape Survey 04-2025",
                "excel_file": "17. Royapuram.xlsx",
                "sheet_name": "17. Royapuram",
                "geocode_city": "Royapuram, Tamil Nadu, India"
            },
            "25-Mylapore": {
                "form_id": "25-Mylapore Landscape Survey 05-2025",
                "excel_file": "25. Mylapore.xlsx",
                "sheet_name": "25. Mylapore",
                "geocode_city": "Mylapore, Tamil Nadu, India"
            },
            "26-Velachery": {
                "form_id": "26-Velachery Landscape Survey 04-2025",
                "excel_file": "26. Velachery.xlsx",
                "sheet_name": "26. Velachery",
                "geocode_city": "Velachery, Tamil Nadu, India"
            },
            "28-Alandur": {
                "form_id": "28-Alandur Landscape Survey 04-2025",
                "excel_file": "28. Alandur.xlsx",
                "sheet_name": "28. Alandur",
                "geocode_city": "Alandur, Tamil Nadu, India"
            },
            "98-Erode (East)": {
                "form_id": "98-Erode (East) Landscape Survey 04-2025",
                "excel_file": "98. Erode (East).xlsx",
                "sheet_name": "98. Erode (East)",
                "geocode_city": "Erode (East), Tamil Nadu, India"
            },
            "99-Erode (West)": {
                "form_id": "99-Erode (West) Landscape Survey 04-2025",
                "excel_file": "99. Erode (West).xlsx",
                "sheet_name": "99. Erode (West)",
                "geocode_city": "Erode (West), Tamil Nadu, India"
            },
            "162-Poompuhar": {
                "form_id": "162-Poompuhar Landscape Survey 04-2025",
                "excel_file": "162. Poompuhar.xlsx",
                "sheet_name": "162. Poompuhar",
                "geocode_city": "Poompuhar, Tamil Nadu, India"
            },
            "164-Kilvelur": {
                "form_id": "164-Kilvelur (SC) Landscape Survey 04-2025",
                "excel_file": "164. Kilvelur.xlsx",
                "sheet_name": "164. Kilvelur",
                "geocode_city": "Kilvelur, Tamil Nadu, India"
            },
            "176-Pattukkottai": {
                "form_id": "176-Pattukkottai Landscape Survey 04-2025",
                "excel_file": "176. Pattukkottai.xlsx",
                "sheet_name": "176. Pattukkottai",
                "geocode_city": "Pattukkottai, Tamil Nadu, India"
            },
            "206-Virudhunagar": {
                "form_id": "206-Virudhunagar Landscape Survey 04-2025",
                "excel_file": "206. Virudhunagar.xlsx",
                "sheet_name": "206. Virudhunagar",
                "geocode_city": "Virudhunagar, Tamil Nadu, India"
            }
        }
    },
    "01 Vasu Srinivas TN Landscape": {
        "project_id": 3,
        "excel_base_path": r"01 Vasu Srinivas TN Landscape",
        "forms": {
            "4-Tiruvallur": {
                "form_id": "4-Tiruvallur Landscape Survey 04-2025 copy 2",
                "excel_file": "4. Tiruvallur.xlsx",
                "sheet_name": "4. Tiruvallur",
                "geocode_city": "Tiruvallur, Tamil Nadu, India"
            },
            "6-Avadi": {
                "form_id": "6-Avadi Landscape Survey 04-2025",
                "excel_file": "6. Avadi.xlsx",
                "sheet_name": "6. Avadi",
                "geocode_city": "Avadi, Tamil Nadu, India"
            },
            "7-Maduravoyal": {
                "form_id": "7-Maduravoyal Landscape Survey 04-2025",
                "excel_file": "7. Maduravoyal.xlsx",
                "sheet_name": "7. Maduravoyal",
                "geocode_city": "Maduravoyal, Tamil Nadu, India"
            },
            "13-Kolathur": {
                "form_id": "13-Kolathur Landscape Survey 04-2025",
                "excel_file": "13. Kolathur.xlsx",
                "sheet_name": "13. Kolathur",
                "geocode_city": "Kolathur, Tamil Nadu, India"
            },
            "15-Thiru-Vi-Ka-Nagar": {
                "form_id": "15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 04-2025",
                "excel_file": "15. Thiru-Vi-Ka-Nagar.xlsx",
                "sheet_name": "15. Thiru-Vi-Ka-Nagar",
                "geocode_city": "Thiru-Vi-Ka-Nagar, Tamil Nadu, India"
            },
            "23-Saidapet": {
                "form_id": "23-Saidapet Landscape Survey 04-2025",
                "excel_file": "23. Saidapet.xlsx",
                "sheet_name": "23. Saidapet",
                "geocode_city": "Saidapet, Tamil Nadu, India"
            },
            "26-Velachery": {
                "form_id": "26-Velachery Landscape Survey 04-2025",
                "excel_file": "26. Velachery.xlsx",
                "sheet_name": "26. Velachery",
                "geocode_city": "Velachery, Tamil Nadu, India"
            },
            "28-Alandur": {
                "form_id": "28-Alandur Landscape Survey 04-2025",
                "excel_file": "28. Alandur.xlsx",
                "sheet_name": "28. Alandur",
                "geocode_city": "Alandur, Tamil Nadu, India"
            },
            "31-Tambaram": {
                "form_id": "31-Tambaram Landscape Survey 04-2025",
                "excel_file": "31. Tambaram.xlsx",
                "sheet_name": "31. Tambaram",
                "geocode_city": "Tambaram, Tamil Nadu, India"
            },
            "40-Katpadi": {
                "form_id": "40-Katpadi Landscape Survey 04-2025",
                "excel_file": "40. Katpadi.xlsx",
                "sheet_name": "40. Katpadi",
                "geocode_city": "Katpadi, Tamil Nadu, India"
            },
            "41-Ranipet": {
                "form_id": "41-Ranipet Landscape Survey 04-2025",
                "excel_file": "41. Ranipet.xlsx",
                "sheet_name": "41. Ranipet",
                "geocode_city": "Ranipet, Tamil Nadu, India"
            },
            "42-Arcot": {
                "form_id": "42-Arcot Landscape Survey 04-2025",
                "excel_file": "42. Arcot.xlsx",
                "sheet_name": "42. Arcot",
                "geocode_city": "Arcot, Tamil Nadu, India"
            },
            "43-Vellore": {
                "form_id": "43-Vellore Landscape Survey 04-2025",
                "excel_file": "43. Vellore.xlsx",
                "sheet_name": "43. Vellore",
                "geocode_city": "Vellore, Tamil Nadu, India"
            },
            "52-Bargur": {
                "form_id": "52-Bargur Landscape Survey 04-2025",
                "excel_file": "52. Bargur.xlsx",
                "sheet_name": "52. Bargur",
                "geocode_city": "Bargur, Tamil Nadu, India"
            },
            "53-Krishnagiri": {
                "form_id": "53-Krishnagiri Landscape Survey 04-2025",
                "excel_file": "53. Krishnagiri.xlsx",
                "sheet_name": "53. Krishnagiri",
                "geocode_city": "Krishnagiri, Tamil Nadu, India"
            },
            "59-Dharmapuri": {
                "form_id": "59-Dharmapuri Landscape Survey 04-2025",
                "excel_file": "59. Dharmapuri.xlsx",
                "sheet_name": "59. Dharmapuri",
                "geocode_city": "Dharmapuri, Tamil Nadu, India"
            },
            "70-Gingee": {
                "form_id": "70-Gingee Landscape Survey 04-2025",
                "excel_file": "70. Gingee.xlsx",
                "sheet_name": "70. Gingee",
                "geocode_city": "Gingee, Tamil Nadu, India"
            },
            "71-Mailam": {
                "form_id": "71-Mailam Landscape Survey 04-2025",
                "excel_file": "71. Mailam.xlsx",
                "sheet_name": "71. Mailam",
                "geocode_city": "Mailam, Tamil Nadu, India"
            },
            "72-Tindivanam": {
                "form_id": "72-Tindivanam (SC) Landscape Survey 04-2025",
                "excel_file": "72. Tindivanam.xlsx",
                "sheet_name": "72. Tindivanam",
                "geocode_city": "Tindivanam, Tamil Nadu, India"
            },
            "75-Vikravandi": {
                "form_id": "75-Vikravandi Landscape Survey 04-2025",
                "excel_file": "75. Vikravandi.xlsx",
                "sheet_name": "75. Vikravandi",
                "geocode_city": "Vikravandi, Tamil Nadu, India"
            },
            "76-Tirukkoyilur": {
                "form_id": "76-Tirukkoyilur Landscape Survey 04-2025",
                "excel_file": "76. Tirukkoyilur.xlsx",
                "sheet_name": "76. Tirukkoyilur",
                "geocode_city": "Tirukkoyilur, Tamil Nadu, India"
            },
            "98-Erode (East)": {
                "form_id": "98-Erode (East) Landscape Survey 04-2025",
                "excel_file": "98. Erode (East).xlsx",
                "sheet_name": "98. Erode (East)",
                "geocode_city": "Erode (East), Tamil Nadu, India"
            },
            "99-Erode (West)": {
                "form_id": "99-Erode (West) Landscape Survey 04-2025",
                "excel_file": "99. Erode (West).xlsx",
                "sheet_name": "99. Erode (West)",
                "geocode_city": "Erode (West), Tamil Nadu, India"
            },
            "117-Kavundampalayam": {
                "form_id": "117-Kavundampalayam Landscape Survey 04-2025",
                "excel_file": "117. Kavundampalayam.xlsx",
                "sheet_name": "117. Kavundampalayam",
                "geocode_city": "Kavundampalayam, Tamil Nadu, India"
            },
            "119-Thondamuthur": {
                "form_id": "119-Thondamuthur Landscape Survey 04-2025",
                "excel_file": "119. Thondamuthur.xlsx",
                "sheet_name": "119. Thondamuthur",
                "geocode_city": "Thondamuthur, Tamil Nadu, India"
            },
            "120-Coimbatore (South)": {
                "form_id": "120-Coimbatore (South) Landscape Survey 04-2025",
                "excel_file": "120. Coimbatore (South).xlsx",
                "sheet_name": "120. Coimbatore (South)",
                "geocode_city": "Coimbatore (South), Tamil Nadu, India"
            },
            "121-Singanallur": {
                "form_id": "121-Singanallur Landscape Survey 04-2025",
                "excel_file": "121. Singanallur.xlsx",
                "sheet_name": "121. Singanallur",
                "geocode_city": "Singanallur, Tamil Nadu, India"
            },
            "151-Tittakudi": {
                "form_id": "151-Tittakudi (SC) Landscape Survey 04-2025",
                "excel_file": "151. Tittakudi.xlsx",
                "sheet_name": "151. Tittakudi",
                "geocode_city": "Tittakudi, Tamil Nadu, India"
            },
            "154-Panruti": {
                "form_id": "154-Panruti Landscape Survey 04-2025",
                "excel_file": "154. Panruti.xlsx",
                "sheet_name": "154. Panruti",
                "geocode_city": "Panruti, Tamil Nadu, India"
            },
            "162-Poompuhar": {
                "form_id": "162-Poompuhar Landscape Survey 04-2025",
                "excel_file": "162. Poompuhar.xlsx",
                "sheet_name": "162. Poompuhar",
                "geocode_city": "Poompuhar, Tamil Nadu, India"
            },
            "164-Kilvelur": {
                "form_id": "164-Kilvelur (SC) Landscape Survey 04-2025",
                "excel_file": "164. Kilvelur.xlsx",
                "sheet_name": "164. Kilvelur",
                "geocode_city": "Kilvelur, Tamil Nadu, India"
            },
            "170-Thiruvidaimarudur": {
                "form_id": "170-Thiruvidaimarudur (SC) Landscape Survey 04-2025",
                "excel_file": "170. Thiruvidaimarudur.xlsx",
                "sheet_name": "170. Thiruvidaimarudur",
                "geocode_city": "Thiruvidaimarudur, Tamil Nadu, India"
            },
            "175-Orathanadu": {
                "form_id": "175-Orathanadu Landscape Survey 04-2025",
                "excel_file": "175. Orathanadu.xlsx",
                "sheet_name": "175. Orathanadu",
                "geocode_city": "Orathanadu, Tamil Nadu, India"
            },
            "176-Pattukkottai": {
                "form_id": "176-Pattukkottai Landscape Survey 04-2025",
                "excel_file": "176. Pattukkottai.xlsx",
                "sheet_name": "176. Pattukkottai",
                "geocode_city": "Pattukkottai, Tamil Nadu, India"
            },
            "185-Tiruppattur": {
                "form_id": "185-Tiruppattur Landscape Survey 04-2025 copy 37",
                "excel_file": "185. Tiruppattur.xlsx",
                "sheet_name": "185. Tiruppattur",
                "geocode_city": "Tiruppattur, Tamil Nadu, India"
            },
            "206-Virudhunagar": {
                "form_id": "206-Virudhunagar Landscape Survey 04-2025",
                "excel_file": "206. Virudhunagar.xlsx",
                "sheet_name": "206. Virudhunagar",
                "geocode_city": "Virudhunagar, Tamil Nadu, India"
            },
            "Test TN Landscape Survey 05-2025": {
                "form_id": "Test TN Landscape Survey 05-2025",
                "excel_file": "Test TN Landscape Survey 05-2025.xlsx",
                "sheet_name": "Test TN Landscape Survey 05-2025",
                "geocode_city": "Tamil Nadu, India"
            }
        }
    }
}

# Forms structure - Sorted in ascending order
FORMS = {
    "Server 3": {
        "01 Bhaskar Srinivas TN Landscape Survey": {
            "60-Pappireddippatti Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "60-Pappireddippatti Landscape Survey 04-2025"
            },
            "77-Ulundurpettai Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "77-Ulundurpettai Landscape Survey 04-2025"
            },
            "79-Sankarapuram Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "79-Sankarapuram Landscape Survey 04-2025"
            },
            "84-Omalur Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "84-Omalur Landscape Survey 04-2025"
            },
            "160-Sirkazhi (SC) Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "160-Sirkazhi (SC) Landscape Survey 04-2025"
            },
            "165-Vedaranyam Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "165-Vedaranyam Landscape Survey 04-2025"
            },
            "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025"
            },
            "167-Mannargudi Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "167-Mannargudi Landscape Survey 04-2025"
            },
            "168-Thiruvarur Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "168-Thiruvarur Landscape Survey 04-2025"
            },
            "169-Nannilam Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "169-Nannilam Landscape Survey 04-2025"
            },
            "177-Peravurani Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "177-Peravurani Landscape Survey 04-2025"
            },
            "178-Gandharvakottai (SC) Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "178-Gandharvakottai (SC) Landscape Survey 04-2025"
            },
            "200-Bodinayakanur Landscape Survey 04-2025": {
                "project_id": 4,
                "form_id": "200-Bodinayakanur Landscape Survey 04-2025"
            },
            "Test TN Landscape Survey 05-2025": {
                "project_id": 4,
                "form_id": "Test TN Landscape Survey 05-2025"
            }
        },
        "01 Laxmi Narayana TN Landscape": {
            "78-Rishivandiyam Landscape Survey 04-2025 copy 42": {
                "project_id": 5,
                "form_id": "78-Rishivandiyam Landscape Survey 04-2025 copy 42"
            },
            "80-Kallakurichi (SC) Landscape Survey 04-2025": {
                "project_id": 5,
                "form_id": "80-Kallakurichi (SC) Landscape Survey 04-2025"
            },
            "127-Palani Landscape Survey 04-2025": {
                "project_id": 5,
                "form_id": "127-Palani Landscape Survey 04-2025"
            },
            "148-Kunnam Landscape Survey 04-2025": {
                "project_id": 5,
                "form_id": "148-Kunnam Landscape Survey 04-2025"
            }
        },
        "01 Ravi Sai TN Landscape": {
            "4-Tiruvallur Landscape Survey 04-2025 copy 2": {
                "project_id": 6,
                "form_id": "4-Tiruvallur Landscape Survey 04-2025 copy 2"
            },
            "17-Royapuram Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "17-Royapuram Landscape Survey 04-2025"
            },
            "25-Mylapore Landscape Survey 05-2025": {
                "project_id": 6,
                "form_id": "25-Mylapore Landscape Survey 05-2025"
            },
            "26-Velachery Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "26-Velachery Landscape Survey 04-2025"
            },
            "28-Alandur Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "28-Alandur Landscape Survey 04-2025"
            },
            "98-Erode (East) Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "98-Erode (East) Landscape Survey 04-2025"
            },
            "99-Erode (West) Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "99-Erode (West) Landscape Survey 04-2025"
            },
            "162-Poompuhar Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "162-Poompuhar Landscape Survey 04-2025"
            },
            "164-Kilvelur (SC) Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "164-Kilvelur (SC) Landscape Survey 04-2025"
            },
            "176-Pattukkottai Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "176-Pattukkottai Landscape Survey 04-2025"
            },
            "206-Virudhunagar Landscape Survey 04-2025": {
                "project_id": 6,
                "form_id": "206-Virudhunagar Landscape Survey 04-2025"
            }
        },
        "01 Vasu Srinivas TN Landscape": {
            "4-Tiruvallur Landscape Survey 04-2025 copy 2": {
                "project_id": 3,
                "form_id": "4-Tiruvallur Landscape Survey 04-2025 copy 2"
            },
            "6-Avadi Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "6-Avadi Landscape Survey 04-2025"
            },
            "7-Maduravoyal Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "7-Maduravoyal Landscape Survey 04-2025"
            },
            "13-Kolathur Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "13-Kolathur Landscape Survey 04-2025"
            },
            "15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 04-2025"
            },
            "23-Saidapet Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "23-Saidapet Landscape Survey 04-2025"
            },
            "26-Velachery Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "26-Velachery Landscape Survey 04-2025"
            },
            "28-Alandur Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "28-Alandur Landscape Survey 04-2025"
            },
            "31-Tambaram Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "31-Tambaram Landscape Survey 04-2025"
            },
            "40-Katpadi Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "40-Katpadi Landscape Survey 04-2025"
            },
            "41-Ranipet Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "41-Ranipet Landscape Survey 04-2025"
            },
            "42-Arcot Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "42-Arcot Landscape Survey 04-2025"
            },
            "43-Vellore Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "43-Vellore Landscape Survey 04-2025"
            },
            "52-Bargur Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "52-Bargur Landscape Survey 04-2025"
            },
            "53-Krishnagiri Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "53-Krishnagiri Landscape Survey 04-2025"
            },
            "59-Dharmapuri Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "59-Dharmapuri Landscape Survey 04-2025"
            },
            "70-Gingee Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "70-Gingee Landscape Survey 04-2025"
            },
            "71-Mailam Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "71-Mailam Landscape Survey 04-2025"
            },
            "72-Tindivanam (SC) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "72-Tindivanam (SC) Landscape Survey 04-2025"
            },
            "75-Vikravandi Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "75-Vikravandi Landscape Survey 04-2025"
            },
            "76-Tirukkoyilur Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "76-Tirukkoyilur Landscape Survey 04-2025"
            },
            "98-Erode (East) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "98-Erode (East) Landscape Survey 04-2025"
            },
            "99-Erode (West) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "99-Erode (West) Landscape Survey 04-2025"
            },
            "117-Kavundampalayam Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "117-Kavundampalayam Landscape Survey 04-2025"
            },
            "119-Thondamuthur Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "119-Thondamuthur Landscape Survey 04-2025"
            },
            "120-Coimbatore (South) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "120-Coimbatore (South) Landscape Survey 04-2025"
            },
            "121-Singanallur Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "121-Singanallur Landscape Survey 04-2025"
            },
            "151-Tittakudi (SC) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "151-Tittakudi (SC) Landscape Survey 04-2025"
            },
            "154-Panruti Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "154-Panruti Landscape Survey 04-2025"
            },
            "162-Poompuhar Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "162-Poompuhar Landscape Survey 04-2025"
            },
            "164-Kilvelur (SC) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "164-Kilvelur (SC) Landscape Survey 04-2025"
            },
            "170-Thiruvidaimarudur (SC) Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "170-Thiruvidaimarudur (SC) Landscape Survey 04-2025"
            },
            "175-Orathanadu Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "175-Orathanadu Landscape Survey 04-2025"
            },
            "176-Pattukkottai Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "176-Pattukkottai Landscape Survey 04-2025"
            },
            "185-Tiruppattur Landscape Survey 04-2025 copy 37": {
                "project_id": 3,
                "form_id": "185-Tiruppattur Landscape Survey 04-2025 copy 37"
            },
            "206-Virudhunagar Landscape Survey 04-2025": {
                "project_id": 3,
                "form_id": "206-Virudhunagar Landscape Survey 04-2025"
            },
            "Test TN Landscape Survey 05-2025": {
                "project_id": 3,
                "form_id": "Test TN Landscape Survey 05-2025"
            }
        }
    }
}

# Mapping of full form names to PROJECTS form keys
FORM_NAME_MAPPING = {
    "60-Pappireddippatti Landscape Survey 04-2025": "60-Pappireddippatti",
    "77-Ulundurpettai Landscape Survey 04-2025": "77-Ulundurpettai",
    "79-Sankarapuram Landscape Survey 04-2025": "79-Sankarapuram",
    "84-Omalur Landscape Survey 04-2025": "84-Omalur",
    "160-Sirkazhi (SC) Landscape Survey 04-2025": "160-Sirkazhi",
    "165-Vedaranyam Landscape Survey 04-2025": "165-Vedaranyam",
    "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025": "166-Thiruthuraipoondi",
    "167-Mannargudi Landscape Survey 04-2025": "167-Mannargudi",
    "168-Thiruvarur Landscape Survey 04-2025": "168-Thiruvarur",
    "169-Nannilam Landscape Survey 04-2025": "169-Nannilam",
    "177-Peravurani Landscape Survey 04-2025": "177-Peravurani",
    "178-Gandharvakottai (SC) Landscape Survey 04-2025": "178-Gandharvakottai",
    "200-Bodinayakanur Landscape Survey 04-2025": "200-Bodinayakanur",
    "Test TN Landscape Survey 05-2025": "Test TN Landscape Survey 05-2025",
    "78-Rishivandiyam Landscape Survey 04-2025 copy 42": "78-Rishivandiyam",
    "80-Kallakurichi (SC) Landscape Survey 04-2025": "80-Kallakurichi",
    "127-Palani Landscape Survey 04-2025": "127-Palani",
    "148-Kunnam Landscape Survey 04-2025": "148-Kunnam",
    "4-Tiruvallur Landscape Survey 04-2025 copy 2": "4-Tiruvallur",
    "17-Royapuram Landscape Survey 04-2025": "17-Royapuram",
    "25-Mylapore Landscape Survey 05-2025": "25-Mylapore",
    "26-Velachery Landscape Survey 04-2025": "26-Velachery",
    "28-Alandur Landscape Survey 04-2025": "28-Alandur",
    "98-Erode (East) Landscape Survey 04-2025": "98-Erode (East)",
    "99-Erode (West) Landscape Survey 04-2025": "99-Erode (West)",
    "162-Poompuhar Landscape Survey 04-2025": "162-Poompuhar",
    "164-Kilvelur (SC) Landscape Survey 04-2025": "164-Kilvelur",
    "176-Pattukkottai Landscape Survey 04-2025": "176-Pattukkottai",
    "206-Virudhunagar Landscape Survey 04-2025": "206-Virudhunagar",
    "6-Avadi Landscape Survey 04-2025": "6-Avadi",
    "7-Maduravoyal Landscape Survey 04-2025": "7-Maduravoyal",
    "13-Kolathur Landscape Survey 04-2025": "13-Kolathur",
    "15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 04-2025": "15-Thiru-Vi-Ka-Nagar",
    "23-Saidapet Landscape Survey 04-2025": "23-Saidapet",
    "31-Tambaram Landscape Survey 04-2025": "31-Tambaram",
    "40-Katpadi Landscape Survey 04-2025": "40-Katpadi",
    "41-Ranipet Landscape Survey 04-2025": "41-Ranipet",
    "42-Arcot Landscape Survey 04-2025": "42-Arcot",
    "43-Vellore Landscape Survey 04-2025": "43-Vellore",
    "52-Bargur Landscape Survey 04-2025": "52-Bargur",
    "53-Krishnagiri Landscape Survey 04-2025": "53-Krishnagiri",
    "59-Dharmapuri Landscape Survey 04-2025": "59-Dharmapuri",
    "70-Gingee Landscape Survey 04-2025": "70-Gingee",
    "71-Mailam Landscape Survey 04-2025": "71-Mailam",
    "72-Tindivanam (SC) Landscape Survey 04-2025": "72-Tindivanam",
    "75-Vikravandi Landscape Survey 04-2025": "75-Vikravandi",
    "76-Tirukkoyilur Landscape Survey 04-2025": "76-Tirukkoyilur",
    "117-Kavundampalayam Landscape Survey 04-2025": "117-Kavundampalayam",
    "119-Thondamuthur Landscape Survey 04-2025": "119-Thondamuthur",
    "120-Coimbatore (South) Landscape Survey 04-2025": "120-Coimbatore (South)",
    "121-Singanallur Landscape Survey 04-2025": "121-Singanallur",
    "151-Tittakudi (SC) Landscape Survey 04-2025": "151-Tittakudi",
    "154-Panruti Landscape Survey 04-2025": "154-Panruti",
    "170-Thiruvidaimarudur (SC) Landscape Survey 04-2025": "170-Thiruvidaimarudur",
    "175-Orathanadu Landscape Survey 04-2025": "175-Orathanadu",
    "185-Tiruppattur Landscape Survey 04-2025 copy 37": "185-Tiruppattur"
}

# Haversine formula for distance (in kilometers)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Cache geocoding results
@st.cache_data
def geocode_location(location, city):
    address = f"{location}, {city}"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={GOOGLE_MAPS_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["status"] == "OK" and data["results"]:
            result = data["results"][0]
            lat = result["geometry"]["location"]["lat"]
            lon = result["geometry"]["location"]["lng"]
            return {"lat": lat, "lon": lon, "status": "OK"}
        else:
            logger.warning(f"Geocoding failed for {address}. Status: {data['status']}")
            return {"lat": None, "lon": None, "status": data["status"]}
    except Exception as e:
        logger.warning(f"Geocoding error for {address}: {str(e)}")
        return {"lat": None, "lon": None, "status": str(e)}

def fetch_all_submissions(project_id, form_id):
    """Fetch all submissions without date filtering"""
    # Ensure form_id is properly encoded
    encoded_form_id = urllib.parse.quote(form_id, safe='')
    url = f"{ODK_CONFIG['BASE_URL']}/v1/projects/{project_id}/forms/{encoded_form_id}.svc/Submissions"
    all_data = []
    skip = 0
    batch_size = 500

    try:
        while True:
            params = {"$top": batch_size, "$skip": skip}
            response = requests.get(
                url,
                auth=HTTPBasicAuth(ODK_CONFIG['USERNAME'], ODK_CONFIG['PASSWORD']),
                params=params,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            submissions = data.get('value', [])
            
            if not submissions:
                break
                
            all_data.extend(submissions)
            skip += len(submissions)
            
            if len(submissions) < batch_size:
                break

    except requests.exceptions.HTTPError as e:
        logger.error(f"Error fetching submissions: {str(e)}")
        st.error(f"Failed to fetch data: {str(e)}. Please verify the project ID and form ID.")
        return []
    except Exception as e:
        logger.error(f"Error fetching submissions: {str(e)}")
        st.error(f"Failed to fetch data: {str(e)}")
        return []

    return all_data

def validate_audio(audio_url):
    """Validate audio duration (8+ minutes = valid)"""
    try:
        response = requests.get(
            audio_url,
            auth=HTTPBasicAuth(ODK_CONFIG['USERNAME'], ODK_CONFIG['PASSWORD']),
            timeout=30
        )
        response.raise_for_status()
        
        audio = AudioSegment.from_file(BytesIO(response.content))
        duration_sec = len(audio) / 1000
        duration_str = f"{int(duration_sec//60)}:{int(duration_sec%60):02d}"
        is_valid = duration_sec >= 480  # 8 minutes in seconds
        
        return duration_str, is_valid
    except Exception as e:
        logger.error(f"Audio validation failed: {str(e)}")
        return "Error", False

def process_submissions(submissions, form_name, project_id, form_id, server_path, project_name, survey_name, distance_threshold):
    """Process submissions with all required fields"""
    if not submissions:
        return None
    
    df = pd.DataFrame(submissions)
    
    # Handle submission IDs
    id_col = 'instanceID' if 'instanceID' in df.columns else '__id'
    df['Submission_Order'] = range(1, len(df)+1)
    
    # Basic info
    df['Form Name'] = form_name
    df['instanceID'] = df[id_col]
    df['Date'] = df['__system'].apply(
        lambda x: parser.parse(x['submissionDate']).date() if isinstance(x, dict) else None
    )
    
    # Extract fields from group_six
    def extract_field(row, field):
        g6 = row.get('group_six', {})
        if isinstance(g6, str):
            try:
                g6 = json.loads(g6)
            except:
                g6 = {}
        return str(g6.get(field, '')).strip()
    
    # Standard fields
    df['Submitted By'] = df.apply(lambda r: extract_field(r, 'submittedBy'), axis=1)
    df['Name'] = df.apply(lambda r: extract_field(r, 'D7_Name'), axis=1)
    df['Gender'] = df.apply(lambda r: extract_field(r, 'D3_Gender').replace('gender.', ''), axis=1)
    df['Age'] = df.apply(lambda r: extract_field(r, 'D4_Age').replace('age.', ''), axis=1)
    df['Caste'] = df.apply(lambda r: extract_field(r, 'D5_Caste').replace('caste.', ''), axis=1)
    df['Block'] = df.apply(lambda r: extract_field(r, 'D1_Block'), axis=1)
    df['Village'] = df.apply(lambda r: extract_field(r, 'D2_Village_GP'), axis=1)
    df['Phone Number'] = df.apply(lambda r: extract_field(r, 'D8_PhoneNumber'), axis=1)
    
    # Audio files
    df['Audio File'] = df.get('bg_audio', 'Unknown')
    df['Audio Present'] = df['Audio File'].apply(lambda x: "✅" if x and x != "Unknown" else "❌")
    
    # Initialize audio validation columns
    df['Audio Duration (MM:SS)'] = "Pending"
    df['Audio Validity'] = "Pending"
    
    # Add concatenated fields
    df['SubmittedBy_AudioFile'] = df.apply(
        lambda r: f"{r['Submitted By']}_{r['Audio File']}".replace(" ", "_").replace("/", "_") if r['Audio Present'] == "✅" else "N/A",
        axis=1
    )
    df['Custom_Concatenated'] = df['SubmittedBy_AudioFile']
    
    # Location data
    def extract_location(row):
        try:
            g6 = row.get('group_six', {})
            if isinstance(g6, str):
                try:
                    g6 = json.loads(g6)
                except:
                    g6 = {}
            
            geo = g6.get('geopoint_widget', {}) if isinstance(g6, dict) else {}
            
            if isinstance(geo, dict):
                coords = geo.get('coordinates', [None, None])
            else:
                coords = [None, None]
            
            if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                return float(coords[1]) if coords[1] is not None else None, \
                       float(coords[0]) if coords[0] is not None else None
            return None, None
        except Exception as e:
            logger.warning(f"Error extracting location: {str(e)}")
            return None, None
    
    df['Latitude'], df['Longitude'] = zip(*df.apply(extract_location, axis=1))
    df['Location Present'] = df.apply(
        lambda r: "✅" if pd.notna(r['Latitude']) and pd.notna(r['Longitude']) else "❌", 
        axis=1
    )
    
    # Interview duration
    if 'start' in df.columns and 'end' in df.columns:
        try:
            df['Interview Length (min)'] = (
                pd.to_datetime(df['end']) - pd.to_datetime(df['start'])
            ).dt.total_seconds() / 60
        except:
            df['Interview Length (min)'] = 0
    
    # Age groups
    age_bins = [18, 25, 35, 45, 55, 100]
    age_labels = ['18-25', '26-35', '36-45', '46-55', '56+']
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df['Age Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels)
    
    # Duration groups
    dur_bins = [0, 5, 10, 15, 20, 1000]
    dur_labels = ['0-5', '5-10', '10-15', '15-20', '20+']
    df['Duration Group'] = pd.cut(df['Interview Length (min)'], bins=dur_bins, labels=dur_labels)
    
    # Load and geocode polling station locations
    column_name = "Location and name of building in which Polling Station located"
    try:
        project_config = PROJECTS[project_name]
        # Map the full form name to the PROJECTS form key
        form_key = FORM_NAME_MAPPING.get(survey_name, survey_name)
        excel_base_path = os.path.join(server_path, project_config['excel_base_path'])
        survey_config = project_config["forms"][form_key]
        excel_file = os.path.join(excel_base_path, survey_config['excel_file'])
        sheet_name = survey_config["sheet_name"]
        geocode_city = survey_config["geocode_city"]
        
        locations_df = pd.read_excel(excel_file, sheet_name=sheet_name)
        locations = locations_df[column_name].dropna().tolist()
        
        geocoded_locations = []
        for loc in locations:
            result = geocode_location(loc, geocode_city)
            geocoded_locations.append({
                "location": loc,
                "lat": result["lat"],
                "lon": result["lon"],
                "status": result["status"]
            })
    except FileNotFoundError:
        logger.error(f"Excel file not found at {excel_file}")
        st.error(f"Excel file not found at {excel_file}. Please check the path.")
        geocoded_locations = []
    except KeyError as e:
        logger.error(f"Form configuration not found for {survey_name}: {str(e)}")
        st.error(f"Form configuration not found for {survey_name}. Please check the form name.")
        geocoded_locations = []
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        st.error(f"Error reading Excel file: {str(e)}")
        geocoded_locations = []
    
    # Calculate distance to nearest polling station and identify matches for each radius
    radius_thresholds = [2, 5, 10, 15, 20, 25]  # in kilometers
    def check_location_range(row, threshold):
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']) or not geocoded_locations:
            return ["❌ No Location Data"], None, "No Match", ["❌ No Match"] * len(radius_thresholds)
        
        min_distance = float('inf')
        matched_location = "No Match"
        radius_matches = ["❌ No Match"] * len(radius_thresholds)
        
        for geocoded in geocoded_locations:
            if geocoded["lat"] is not None and geocoded["lon"] is not None:
                distance = haversine_distance(row['Latitude'], row['Longitude'], geocoded["lat"], geocoded["lon"])
                if distance < min_distance:
                    min_distance = distance
                    if distance <= threshold:
                        matched_location = geocoded["location"]
        
        # Check exclusive radius matching
        for i, radius in enumerate(radius_thresholds):
            if min_distance <= radius:
                radius_matches[i] = "✅ Matched"
                break  # Ensure only the smallest radius is marked
        
        status = ["✅ Within Range" if min_distance <= threshold else "❌ Out of Range"]
        return status, min_distance, matched_location, radius_matches
    
    # Apply distance calculation and matching
    df[['Location Within Range', 'Distance to Nearest Polling Station (km)', 'Matched Polling Station', 'Radius Matches']] = df.apply(
        lambda row: pd.Series(check_location_range(row, distance_threshold)), axis=1
    )
    
    # Expand radius matches into separate columns
    for i, radius in enumerate(radius_thresholds):
        df[f'Match Within {radius}km'] = df['Radius Matches'].apply(lambda x: x[i])
    
    # Drop temporary Radius Matches column
    df = df.drop('Radius Matches', axis=1)
    
    # Required columns
    required_columns = [
        'Form Name', 'Date', 'Audio File', 'Audio Present', 'Location Present',
        'Name', 'Gender', 'Age', 'Age Group', 'Caste', 'Block', 'Village',
        'Submitted By', 'Phone Number', 'Interview Length (min)', 'Duration Group',
        'Latitude', 'Longitude', 'instanceID', 'SubmittedBy_AudioFile', 'Custom_Concatenated',
        'Audio Duration (MM:SS)', 'Audio Validity', 'Submission_Order', 'Location Within Range',
        'Distance to Nearest Polling Station (km)', 'Matched Polling Station',
        'Match Within 2km', 'Match Within 5km', 'Match Within 10km', 'Match Within 15km',
        'Match Within 20km', 'Match Within 25km'
    ]
    
    # Ensure all columns exist
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    return df[required_columns]

def main():
    st.set_page_config(page_title="ODK Data Processor", layout="wide")
    st.title("📊 ODK Form Data Processor")
    
    # Sidebar controls
    st.sidebar.header("Filters")
    server_path = st.sidebar.text_input("Server Path", value="server3", key="server_path")
    selected_server = st.sidebar.selectbox("Server", list(FORMS.keys()))
    selected_project = st.sidebar.selectbox("Project", list(FORMS[selected_server].keys()))
    selected_form = st.sidebar.selectbox("Form", list(FORMS[selected_server][selected_project].keys()))
    distance_threshold = st.sidebar.slider(
        "Distance Threshold (kilometers)",
        min_value=0.1,
        max_value=50.0,
        value=0.1,
        step=0.1,
        help="Maximum distance in kilometers for a coordinate to be considered within range",
        key="distance_threshold"
    )
    
    form_info = FORMS[selected_server][selected_project][selected_form]
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'audio_validated' not in st.session_state:
        st.session_state.audio_validated = False
    
    # Main content
    if st.button("Load All Submissions"):
        with st.spinner(f"Fetching all submissions for {selected_form}..."):
            submissions = fetch_all_submissions(
                form_info['project_id'],
                form_info['form_id']
            )
        
        if submissions:
            df = process_submissions(
                submissions,
                selected_form,
                form_info['project_id'],
                form_info['form_id'],
                server_path,
                selected_project,
                selected_form,
                distance_threshold
            )
            
            if df is not None:
                st.session_state.df = df
                st.session_state.audio_validated = False
                st.success(f"Loaded {len(df)} submissions")
            else:
                st.error("Failed to process submissions")
        else:
            st.warning("No submissions found for this form")
    
    # Audio validation section
    if st.session_state.df is not None:
        st.subheader("Audio Validation")
        
        # Show validation status
        if st.session_state.audio_validated:
            st.success("✓ All audio files validated")
        else:
            st.warning("Audio files not yet validated")
        
        # Validation button
        if st.button("🔍 Validate All Audio Files") and not st.session_state.audio_validated:
            audio_subset = st.session_state.df[st.session_state.df['Audio Present'] == "✅"]
            if not audio_subset.empty:
                progress_bar = st.progress(0)
                status_text = st.empty()
                total_files = len(audio_subset)
                
                for i, (idx, row) in enumerate(audio_subset.iterrows()):
                    status_text.text(f"Validating {i+1}/{total_files}: {row['Audio File']}")
                    progress_bar.progress((i + 1) / total_files)
                    
                    audio_url = (
                        f"{ODK_CONFIG['BASE_URL']}/v1/projects/{form_info['project_id']}/"
                        f"forms/{urllib.parse.quote(form_info['form_id'])}/submissions/{row['instanceID']}/"
                        f"attachments/{row['Audio File']}"
                    )
                    duration, valid = validate_audio(audio_url)
                    st.session_state.df.at[idx, 'Audio Duration (MM:SS)'] = duration
                    st.session_state.df.at[idx, 'Audio Validity'] = "✅ Valid (≥8 min)" if valid else "❌ Invalid (<8 min)"
                
                progress_bar.empty()
                status_text.empty()
                st.session_state.audio_validated = True
                st.success(f"Validated {total_files} audio files")
            else:
                st.warning("No audio files to validate")
        
        # Display data
        st.subheader("All Submission Data")
        st.dataframe(st.session_state.df)
        
        # Export
        st.subheader("Data Export")
        
        # Create two columns for download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV Download
            csv = st.session_state.df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Full CSV",
                csv,
                f"{selected_form}_all_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key='csv-download'
            )
        
        with col2:
            # Excel Download
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                st.session_state.df.to_excel(writer, index=False, sheet_name='Submissions')
                writer.close()
                
                st.download_button(
                    "📥 Download Full Excel (XLSX)",
                    excel_buffer.getvalue(),
                    f"{selected_form}_all_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key='excel-download'
                )

if __name__ == "__main__":
    main()
