import requests
from requests.auth import HTTPBasicAuth
import streamlit as st
import pandas as pd
import io
import zipfile
from datetime import datetime

# Streamlit Setup
st.set_page_config(page_title="ODK Audio Test Downloader", layout="centered")
st.title("🔊 ODK Audio Test Download (All Files from Each Form)")

# ODK Configurations for each server
ODK_CONFIGS = {
    "Server 1": {
        "ODK_USERNAME": "rushi@tnodk01.ii.com",
        "ODK_PASSWORD": "rushi2025&",
        "BASE_URL": "https://tnodk01.indiaintentions.com"
    },
    "Server 2": {
        "ODK_USERNAME": "rushi@tnodk01.ii.com",
        "ODK_PASSWORD": "rushi2025&",
        "BASE_URL": "https://tnodk02.indiaintentions.com"
    },
    "Server 3": {
        "ODK_USERNAME": "rushi@tnodk01.ii.com",
        "ODK_PASSWORD": "rushi2025&",
        "BASE_URL": "https://tnodk03.indiaintentions.com"
    }
}

forms = {
    "Server 1": {
        "Krishnagiri APP": {
            "52-Bargur Landscape Survey 05-2025": {"project_id": 7, "form_id": "52-Bargur Landscape Survey 05-2025"},
            "53-Krishnagiri Landscape Survey 05-2025": {"project_id": 7, "form_id": "53-Krishnagiri Landscape Survey 05-2025"}
        },
        "Bikas Tirunelveli APP": {
            "225-Ambasamudram Landscape Survey 05-2025": {"project_id": 14, "form_id": "225-Ambasamudram Landscape Survey 05-2025"},
            "227-Nanguneri Landscape Survey 05-2025": {"project_id": 14, "form_id": "227-Nanguneri Landscape Survey 05-2025"},
            "228-Radhapuram Landscape Survey 05-2025": {"project_id": 14, "form_id": "228-Radhapuram Landscape Survey 05-2025"}
        },
        "Gopal Misc APP": {
            "148-Kunnam Landscape Survey 05-2025": {"project_id": 16, "form_id": "148-Kunnam Landscape Survey 05-2025"}
        },
        "Mahesh Ramanathapuram APP": {
            "210-Tiruvadanai Landscape Survey 05-2025": {"project_id": 11, "form_id": "210-Tiruvadanai Landscape Survey 05-2025"},
            "211-Ramanathapuram Landscape Survey 05-2025": {"project_id": 11, "form_id": "211-Ramanathapuram Landscape Survey 05-2025"},
            "212-Mudhukulathur Landscape Survey 05-2025": {"project_id": 11, "form_id": "212-Mudhukulathur Landscape Survey 05-2025"}
        },
        "BK TN AC Landscape": {
            "103-Perundurai Landscape Survey 04-2025": {"project_id": 4, "form_id": "103-Perundurai Landscape Survey 04-2025"},
            "132 Dindigul Landscape Survey 04-2025": {"project_id": 4, "form_id": "132 Dindigul Landscape Survey 04-2025"},
            "35-Karur Landscape Survey 04-2025": {"project_id": 4, "form_id": "35-Karur Landscape Survey 04-2025"},
            "146. Thuraiyur (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "146. Thuraiyur (SC) Landscape Survey 04-2025"},
            "150-Jayankondam Landscape Survey 04-2025": {"project_id": 4, "form_id": "150-Jayankondam Landscape Survey 04-2025"},
            "155-Cuddalore Landscape Survey 04-2025": {"project_id": 4, "form_id": "155-Cuddalore Landscape Survey 04-2025"},
            "171-Kumbakonam Landscape Survey 04-2025": {"project_id": 4, "form_id": "171-Kumbakonam Landscape Survey 04-2025"},
            "189-Madurai East Landscape Survey 04-2025": {"project_id": 4, "form_id": "189-Madurai East Landscape Survey 04-2025"}
        },
        "Closed Forms - BK TN AC Landscape": {
            "66-Polur Landscape Survey 04-2025": {"project_id": 4, "form_id": "66-Polur Landscape Survey 04-2025"},
            "56-Thalli Landscape Survey 04-2025": {"project_id": 4, "form_id": "56-Thalli Landscape Survey 04-2025"},
            "39-Sholingur Landscape Survey 04-2025": {"project_id": 4, "form_id": "39-Sholingur Landscape Survey 04-2025"},
            "38-Arakkonam (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "38-Arakkonam (SC) Landscape Survey 04-2025"},
            "3-Thirutthani Landscape Survey 04-2025": {"project_id": 4, "form_id": "3-Thirutthani Landscape Survey 04-2025"},
            "201-Cumbum Landscape Survey 04-2025": {"project_id": 4, "form_id": "201-Cumbum Landscape Survey 04-2025"},
            "199. Periyakulam (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "199. Periyakulam (SC) Landscape Survey 04-2025"},
            "198-Andipatti Landscape Survey 04-2025": {"project_id": 4, "form_id": "198-Andipatti Landscape Survey 04-2025"},
            "180-Pudukkottai Landscape Survey 04-2025": {"project_id": 4, "form_id": "180-Pudukkottai Landscape Survey 04-2025"},
            "158-Chidambaram Landscape Survey 04-2025": {"project_id": 4, "form_id": "158-Chidambaram Landscape Survey 04-2025"},
            "145-Musiri Landscape Survey 04-2025": {"project_id": 4, "form_id": "145-Musiri Landscape Survey 04-2025"},
            "137-Kulithalai Landscape Survey 04-2025": {"project_id": 4, "form_id": "137-Kulithalai Landscape Survey 04-2025"},
            "136-Krishnarayapuram (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "136-Krishnarayapuram (SC) Landscape Survey 04-2025"},
            "12-Perambur Landscape Survey 04-2025": {"project_id": 4, "form_id": "12-Perambur Landscape Survey 04-2025"},
            "109-Gudalur (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "109-Gudalur (SC) Landscape Survey 04-2025"}
        },
        "03 BK TN AC Landscape": {
            "100-Modakkurichi Landscape Survey 04-2025": {"project_id": 5, "form_id": "100-Modakkurichi Landscape Survey 04-2025"},
            "153-Neyveli Landscape Survey 05-2025": {"project_id": 5, "form_id": "153-Neyveli Landscape Survey 05-2025"},
            "197-Usilampatti Landscape Survey 04-2025": {"project_id": 5, "form_id": "197-Usilampatti Landscape Survey 04-2025"},
            "62-Chengam (SC) Landscape Survey 05-2025": {"project_id": 5, "form_id": "62-Chengam (SC) Landscape Survey 05-2025"},
            "63-Tiruvannamalai Landscape Survey 04-2025": {"project_id": 5, "form_id": "63-Tiruvannamalai Landscape Survey 04-2025"},
            "95-Paramathi-Velur Landscape Survey 05-2025": {"project_id": 5, "form_id": "95-Paramathi-Velur Landscape Survey 05-2025"}
        },
        "Closed Forms - 03 BK TN AC Landscape": {
            "55-Hosur Landscape Survey 04-2025": {"project_id": 5, "form_id": "55-Hosur Landscape Survey 04-2025"}
        },
        "Gopal Ranipet Vellore APP": {
            "41-Ranipet Landscape Survey 05-2025": {"project_id": 15, "form_id": "41-Ranipet Landscape Survey 05-2025"},
            "42-Arcot Landscape Survey 05-2025": {"project_id": 15, "form_id": "42-Arcot Landscape Survey 05-2025"},
            "43-Vellore Landscape Survey 05-2025": {"project_id": 15, "form_id": "43-Vellore Landscape Survey 05-2025"},
            "44-Anaikattu Landscape Survey 05-2025": {"project_id": 15, "form_id": "44-Anaikattu Landscape Survey 05-2025"}
        },
        "Virudhunagar APP": {
            "202-Rajapalayam Landscape Survey 05-2025": {"project_id": 8, "form_id": "202-Rajapalayam Landscape Survey 05-2025"},
            "203-Srivilliputhur (SC) Landscape Survey 05-2025": {"project_id": 8, "form_id": "203-Srivilliputhur (SC) Landscape Survey 05-2025"},
            "205-Sivakasi Landscape Survey 05-2025": {"project_id": 8, "form_id": "205-Sivakasi Landscape Survey 05-2025"},
            "206-Virudhunagar Landscape Survey 05-2025": {"project_id": 8, "form_id": "206-Virudhunagar Landscape Survey 05-2025"},
            "208-Tiruchuli Landscape Survey 05-2025": {"project_id": 8, "form_id": "208-Tiruchuli Landscape Survey 05-2025"}
        },
        "Tanjavore APP": {
            "176-Pattukkottai Landscape Survey 05-2025": {"project_id": 9, "form_id": "176-Pattukkottai Landscape Survey 05-2025"}
        },
        "Bikas Tenkasi APP": {
            "220-Vasudevanallur (SC) Landscape Survey 05-2025": {"project_id": 13, "form_id": "220-Vasudevanallur (SC) Landscape Survey 05-2025"},
            "221-Kadayanallur Landscape Survey 05-2025": {"project_id": 13, "form_id": "221-Kadayanallur Landscape Survey 05-2025"},
            "222-Tenkasi Landscape Survey 05-2025": {"project_id": 13, "form_id": "222-Tenkasi Landscape Survey 05-2025"},
            "223-Alangulam Landscape Survey 05-2025": {"project_id": 13, "form_id": "223-Alangulam Landscape Survey 05-2025"}
        },
        "Sai Sivaganga APP": {
            "184-Karaikudi Landscape Survey 05-2025": {"project_id": 12, "form_id": "184-Karaikudi Landscape Survey 05-2025"},
            "185-Tiruppattur Landscape Survey 05-2025": {"project_id": 12, "form_id": "185-Tiruppattur Landscape Survey 05-2025"},
            "186-Sivaganga Landscape Survey 05-2025": {"project_id": 12, "form_id": "186-Sivaganga Landscape Survey 05-2025"},
            "187-Manamadurai (SC) Landscape Survey 05-2025": {"project_id": 12, "form_id": "187-Manamadurai (SC) Landscape Survey 05-2025"}
        },
        "04 TN AC Landscape": {
            "151-Tittakudi (SC) Landscape Survey 05-2025": {"project_id": 6, "form_id": "151-Tittakudi (SC) Landscape Survey 05-2025"},
            "156-Kurinjipadi Landscape Survey 05-2025": {"project_id": 6, "form_id": "156-Kurinjipadi Landscape Survey 05-2025"},
            "159-Kattumannarkoil (SC) Landscape Survey 04-2025": {"project_id": 6, "form_id": "159-Kattumannarkoil (SC) Landscape Survey 04-2025"},
            "181-Thirumayam Landscape Survey 04-2025": {"project_id": 6, "form_id": "181-Thirumayam Landscape Survey 04-2025"},
            "204-Sattur Landscape Survey 05-2025": {"project_id": 6, "form_id": "204-Sattur Landscape Survey 05-2025"},
            "183-Aranthangi Landscape Survey 04-2025": {"project_id": 6, "form_id": "183-Aranthangi Landscape Survey 04-2025"}
        },
        "Closed Forms - 04 TN AC Landscape": {
            "183-Aranthangi Landscape Survey 04-2025": {"project_id": 6, "form_id": "183-Aranthangi Landscape Survey 04-2025"}
        },
        "Thoothukudi APP": {
            "214-Thoothukkudi Landscape Survey 05-2025": {"project_id": 10, "form_id": "214-Thoothukkudi Landscape Survey 05-2025"},
            "215-Tiruchendur Landscape Survey 05-2025": {"project_id": 10, "form_id": "215-Tiruchendur Landscape Survey 05-2025"},
            "216-Srivaikuntam Landscape Survey 05-2025": {"project_id": 10, "form_id": "216-Srivaikuntam Landscape Survey 05-2025"},
            "218-Kovilpatti Landscape Survey 05-2025": {"project_id": 10, "form_id": "218-Kovilpatti Landscape Survey 05-2025"}
        }
    },
    "Server 2": {
        "01 Shankar Subramaniam TN Landscape Survey": {
            "108-Udhagamandalam Landscape Survey 04-2025": {"project_id": 10, "form_id": "108-Udhagamandalam Landscape Survey 04-2025"},
            "142-Thiruverumbur Landscape Survey 04-2025": {"project_id": 10, "form_id": "142-Thiruverumbur Landscape Survey 04-2025"},
            "143-Lalgudi Landscape Survey 05-2025": {"project_id": 10, "form_id": "143-Lalgudi Landscape Survey 05-2025"},
            "144-Manachanallur Landscape Survey 04-2025": {"project_id": 10, "form_id": "144-Manachanallur Landscape Survey 04-2025"},
            "175-Orathanadu Landscape Survey 05-2025": {"project_id": 10, "form_id": "175-Orathanadu Landscape Survey 05-2025"},
            "219-Sankarankovil (SC) Landscape Survey 04-2025": {"project_id": 10, "form_id": "219-Sankarankovil (SC) Landscape Survey 04-2025"},
            "54-Veppanahalli Landscape Survey 04-2025": {"project_id": 10, "form_id": "54-Veppanahalli Landscape Survey 04-2025"}
        },
        "03 Bikas V6": {
            "182-Alangudi Landscape Survey 05-2025": {"project_id": 12, "form_id": "182-Alangudi Landscape Survey 05-2025"},
            "207-Aruppukkottai Landscape Survey 05-2025": {"project_id": 12, "form_id": "207-Aruppukkottai Landscape Survey 05-2025"},
            "41-Ranipet Landscape Survey 05-2025": {"project_id": 12, "form_id": "41-Ranipet Landscape Survey 05-2025"},
            "42-Arcot Landscape Survey 05-2025": {"project_id": 12, "form_id": "42-Arcot Landscape Survey 05-2025"},
            "50-Tirupattur Landscape Survey 05-2025": {"project_id": 12, "form_id": "50-Tirupattur Landscape Survey 05-2025"},
            "72-Tindivanam (SC) Landscape Survey 05-2025": {"project_id": 12, "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025"}
        },
        "Nanda TN Landscape": {
            "128-Oddanchatram Landscape Survey 05-2025": {"project_id": 11, "form_id": "128-Oddanchatram Landscape Survey 05-2025"},
            "154-Panruti Landscape Survey 05-2025": {"project_id": 11, "form_id": "154-Panruti Landscape Survey 05-2025"},
            "155-Cuddalore Landscape Survey 05-2025": {"project_id": 11, "form_id": "155-Cuddalore Landscape Survey 05-2025"},
            "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025": {"project_id": 11, "form_id": "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025"},
            "162-Poompuhar Landscape Survey 05-2025": {"project_id": 11, "form_id": "162-Poompuhar Landscape Survey 05-2025"},
            "164-Kilvelur (SC) Landscape Survey 05-2025": {"project_id": 11, "form_id": "164-Kilvelur (SC) Landscape Survey 05-2025"}
        },
        "Closed Forms - Nanda TN Landscape": {
            "229-Kanniyakumari Landscape Survey 05-2025": {"project_id": 11, "form_id": "229-Kanniyakumari Landscape Survey 05-2025"},
            "230-Nagercoil Landscape Survey 05-2025": {"project_id": 11, "form_id": "230-Nagercoil Landscape Survey 05-2025"}
        },
        "Nanda Kanniyakumari APP": {
            "229-Kanniyakumari Landscape Survey 05-2025": {"project_id": 14, "form_id": "229-Kanniyakumari Landscape Survey 05-2025"},
            "230-Nagercoil Landscape Survey 05-2025": {"project_id": 14, "form_id": "230-Nagercoil Landscape Survey 05-2025"},
            "231-Colachal Landscape Survey 05-2025": {"project_id": 14, "form_id": "231-Colachal Landscape Survey 05-2025"},
            "232-Padmanabhapuram Landscape Survey 05-2025": {"project_id": 14, "form_id": "232-Padmanabhapuram Landscape Survey 05-2025"},
            "233-Vilavancode Landscape Survey 05-2025": {"project_id": 14, "form_id": "233-Vilavancode Landscape Survey 05-2025"},
            "234-Killiyoor Landscape Survey 05-2025": {"project_id": 14, "form_id": "234-Killiyoor Landscape Survey 05-2025"}
        },
        "Shankar Tenkasi": {
            "220-Vasudevanallur (SC) Landscape Survey 05-2025": {"project_id": 13, "form_id": "220-Vasudevanallur (SC) Landscape Survey 05-2025"}
        },
        "02 FMRS TN Landscape Survey": {
            "188-Melur Landscape Survey 04-2025": {"project_id": 7, "form_id": "188-Melur Landscape Survey 04-2025"},
            "190-Sholavandan (SC) Landscape Survey 04-2025": {"project_id": 7, "form_id": "190-Sholavandan (SC) Landscape Survey 04-2025"},
            "191-Madurai North Landscape Survey 04-2025": {"project_id": 7, "form_id": "191-Madurai North Landscape Survey 04-2025"},
            "192-Madurai South Landscape Survey 04-2025": {"project_id": 7, "form_id": "192-Madurai South Landscape Survey 04-2025"},
            "193-Madurai Central Landscape Survey 04-2025": {"project_id": 7, "form_id": "193-Madurai Central Landscape Survey 04-2025"},
            "194-Madurai West Landscape Survey 04-2025": {"project_id": 7, "form_id": "194-Madurai West Landscape Survey 04-2025"},
            "196-Thirumangalam Landscape Survey 04-2025": {"project_id": 7, "form_id": "196-Thirumangalam Landscape Survey 04-2025"}
        },
        "Closed Forms - 02 FMRS TN Landscape Survey": {
            "195-Thiruparankundram Landscape Survey 04-2025": {"project_id": 7, "form_id": "195-Thiruparankundram Landscape Survey 04-2025"}
        },
        "Closed Forms - 01 FMRS TN Landscape Survey": {
            "139-Srirangam Landscape Survey 04-2025": {"project_id": 3, "form_id": "139-Srirangam Landscape Survey 04-2025"},
            "141-Tiruchirappalli (East) Landscape Survey 04-2025": {"project_id": 3, "form_id": "141-Tiruchirappalli (East) Landscape Survey 04-2025"},
            "163-Nagapattinam Landscape Survey 04-2025": {"project_id": 3, "form_id": "163-Nagapattinam Landscape Survey 04-2025"},
            "172-Papanasam Landscape Survey 04-2025": {"project_id": 3, "form_id": "172-Papanasam Landscape Survey 04-2025"},
            "174-Thanjavur Landscape Survey 04-2025": {"project_id": 3, "form_id": "174-Thanjavur Landscape Survey 04-2025"},
            "177-Peravurani Landscape Survey 04-2025": {"project_id": 3, "form_id": "177-Peravurani Landscape Survey 04-2025"},
            "209-Paramakudi (SC) Landscape Survey 04-2025": {"project_id": 3, "form_id": "209-Paramakudi (SC) Landscape Survey 04-2025"},
            "213-Vilathikulam Landscape Survey 04-2025": {"project_id": 3, "form_id": "213-Vilathikulam Landscape Survey 04-2025"},
            "217-Ottapidaram (SC) Landscape Survey 04-2025": {"project_id": 3, "form_id": "217-Ottapidaram (SC) Landscape Survey 04-2025"},
            "65-Kalasapakkam Landscape Survey 04-2025": {"project_id": 3, "form_id": "65-Kalasapakkam Landscape Survey 04-2025"},
            "8-Ambattur Landscape Survey 04-2025": {"project_id": 3, "form_id": "8-Ambattur Landscape Survey 04-2025"}
        },
        "01 Bikas TN Landscape Survey": {
            "127-Palani Landscape Survey 05-2025": {"project_id": 4, "form_id": "127-Palani Landscape Survey 05-2025"},
            "128-Oddanchatram Landscape Survey 05-2025": {"project_id": 4, "form_id": "128-Oddanchatram Landscape Survey 05-2025"},
            "129-Athoor Landscape Survey 05-2025": {"project_id": 4, "form_id": "129-Athoor Landscape Survey 05-2025"},
            "130-Nilakkottai (SC) Landscape Survey 05-2025": {"project_id": 4, "form_id": "130-Nilakkottai (SC) Landscape Survey 05-2025"},
            "143-Lalgudi Landscape Survey 05-2025": {"project_id": 4, "form_id": "143-Lalgudi Landscape Survey 05-2025"},
            "147-Perambalur (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "147-Perambalur (SC) Landscape Survey 04-2025"},
            "45-Kilvaithinankuppam (SC) Landscape Survey 05-2025": {"project_id": 4, "form_id": "45-Kilvaithinankuppam (SC) Landscape Survey 05-2025"},
            "47-Vaniyambadi Landscape Survey 05-2025": {"project_id": 4, "form_id": "47-Vaniyambadi Landscape Survey 05-2025"},
            "49-Jolarpet Landscape Survey 04-2025": {"project_id": 4, "form_id": "49-Jolarpet Landscape Survey 04-2025"},
            "69-Vandavasi (SC) Landscape Survey 05-2025": {"project_id": 4, "form_id": "69-Vandavasi (SC) Landscape Survey 05-2025"},
            "81-Gangavalli (SC) Landscape Survey 05-2025": {"project_id": 4, "form_id": "81-Gangavalli (SC) Landscape Survey 05-2025"}
        },
        "Closed Forms - 01 Bikas TN Landscape Survey": {
            "14-Villivakkam Landscape Survey 04-2025": {"project_id": 4, "form_id": "14-Villivakkam Landscape Survey 04-2025"},
            "150-Jayankondam Landscape Survey 04-2025": {"project_id": 4, "form_id": "150-Jayankondam Landscape Survey 04-2025"},
            "159-Kattumannarkoil (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "159-Kattumannarkoil (SC) Landscape Survey 04-2025"},
            "173-Thiruvaiyaru Landscape Survey 04-2025": {"project_id": 4, "form_id": "173-Thiruvaiyaru Landscape Survey 04-2025"},
            "179-Viralimalai Landscape Survey 04-2025": {"project_id": 4, "form_id": "179-Viralimalai Landscape Survey 04-2025"},
            "223-Alangulam Landscape Survey 04-2025": {"project_id": 4, "form_id": "223-Alangulam Landscape Survey 04-2025"},
            "24-Thiyagarayanagar Landscape Survey 04-2025": {"project_id": 4, "form_id": "24-Thiyagarayanagar Landscape Survey 04-2025"},
            "44-Anaikattu Landscape Survey 05-2025": {"project_id": 4, "form_id": "44-Anaikattu Landscape Survey 05-2025"},
            "46-Gudiyattam (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "46-Gudiyattam (SC) Landscape Survey 04-2025"},
            "48-Ambur Landscape Survey 04-2025": {"project_id": 4, "form_id": "48-Ambur Landscape Survey 04-2025"}
        },
        "02 Shashi TN Landscape": {
            "25-Mylapore Landscape Survey 04-2025": {"project_id": 8, "form_id": "25-Mylapore Landscape Survey 04-2025"}
        },
        "02 Bikas TN Landscape Survey": {
            "155-Cuddalore Landscape Survey 04-2025": {"project_id": 5, "form_id": "155-Cuddalore Landscape Survey 04-2025"},
            "64-Kilpennathur Landscape Survey 04-2025": {"project_id": 5, "form_id": "64-Kilpennathur Landscape Survey 04-2025"}
        },
        "Closed Forms - 02 Bikas TN Landscape Survey": {
            "12-Perambur Landscape Survey 04-2025": {"project_id": 5, "form_id": "12-Perambur Landscape Survey 04-2025"},
            "131-Natham Landscape Survey 04-2025": {"project_id": 5, "form_id": "131-Natham Landscape Survey 04-2025"},
            "132-Dindigul Landscape Survey 04-2025": {"project_id": 5, "form_id": "132-Dindigul Landscape Survey 04-2025"},
            "134-Aravakurichi Landscape Survey 04-2025": {"project_id": 5, "form_id": "134-Aravakurichi Landscape Survey 04-2025"},
            "135-Karur Landscape Survey 04-2025": {"project_id": 5, "form_id": "135-Karur Landscape Survey 04-2025"},
            "157-Bhuvanagiri Landscape Survey 04-2025": {"project_id": 5, "form_id": "157-Bhuvanagiri Landscape Survey 04-2025"},
            "171-Kumbakonam Landscape Survey 04-2025": {"project_id": 5, "form_id": "171-Kumbakonam Landscape Survey 04-2025"},
            "66-Polur Landscape Survey 04-2025": {"project_id": 5, "form_id": "66-Polur Landscape Survey 04-2025"},
            "67-Arani Landscape Survey 04-2025": {"project_id": 5, "form_id": "67-Arani Landscape Survey 04-2025"}
        },
        "01 Shashi TN Landscape Survey": {
            "88-Salem (West) Landscape Survey 04-2025": {"project_id": 6, "form_id": "88-Salem (West) Landscape Survey 04-2025"},
            "89-Salem (North) Landscape Survey 04-2025": {"project_id": 6, "form_id": "89-Salem (North) Landscape Survey 04-2025"},
            "90-Salem (South) Landscape Survey 04-2025": {"project_id": 6, "form_id": "90-Salem (South) Landscape Survey 04-2025"}
        }
    }
}


def fetch_submissions(selected_server, project_id, form_id):
    config = ODK_CONFIGS[selected_server]
    submission_url = f"{config['BASE_URL']}/v1/projects/{project_id}/forms/{form_id}.svc/Submissions"
    response = requests.get(
        submission_url,
        auth=HTTPBasicAuth(config['ODK_USERNAME'], config['ODK_PASSWORD']),
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("value", [])

def filter_submissions_by_date(submissions, selected_date):
    if selected_date:
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        return [submission for submission in submissions if submission['__system']['submissionDate'].startswith(selected_date_str)]
    return submissions

def download_audio_files(selected_server, form_name, project_id, form_id, audio_submissions):
    config = ODK_CONFIGS[selected_server]
    zip_buffer = io.BytesIO()
    download_status = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, (_, row) in enumerate(audio_submissions.iterrows()):
            audio_file = row['bg_audio']
            submission_id = row['__id']
            submitted_by = row.get('group_six', {}).get('submittedBy', 'unknown')

            with st.spinner(f"Downloading {i+1}/{len(audio_submissions)}: {submitted_by}_{audio_file}..."):
                try:
                    audio_url = f"{config['BASE_URL']}/v1/projects/{project_id}/forms/{form_id}/submissions/{submission_id}/attachments/{audio_file}"
                    audio_response = requests.get(
                        audio_url,
                        auth=HTTPBasicAuth(config['ODK_USERNAME'], config['ODK_PASSWORD']),
                        timeout=30
                    )
                    audio_response.raise_for_status()

                    clean_name = f"{submitted_by}_{audio_file}".replace(" ", "_").replace("/", "_").replace("\\", "_")
                    zip_file.writestr(clean_name, audio_response.content)

                    download_status.append(f"✅ Downloaded: {clean_name}")

                except requests.exceptions.RequestException as e:
                    download_status.append(f"❌ Server error for {audio_file}: {str(e)}")
                except Exception as e:
                    download_status.append(f"❌ Unexpected error for {audio_file}: {str(e)}")

    if zip_buffer.getbuffer().nbytes == 0:
        return None, download_status

    zip_buffer.seek(0)  # Reset buffer position
    return zip_buffer, download_status

def main():
    try:
        # Sidebar for server, project, and form selection and date input
        st.sidebar.header("Filter Options")
        selected_server = st.sidebar.selectbox("Select Server", list(forms.keys()))

        if selected_server:
            selected_project = st.sidebar.selectbox("Select Project", list(forms[selected_server].keys()))

            if selected_project:
                selected_form = st.sidebar.selectbox("Select Form", list(forms[selected_server][selected_project].keys()))
                selected_date = st.sidebar.date_input("Select Date", None)

                if selected_form:
                    form_name = selected_form
                    project_id = forms[selected_server][selected_project][selected_form]['project_id']
                    form_id = forms[selected_server][selected_project][selected_form]['form_id']

                    # Fetch submissions for the selected form
                    with st.spinner(f"Fetching submissions for {form_name}..."):
                        data = fetch_submissions(selected_server, project_id, form_id)

                    if not data:
                        st.warning(f"No submissions found for {form_name}.")
                    else:
                        # Filter submissions by date
                        filtered_data = filter_submissions_by_date(data, selected_date)

                        if not filtered_data:
                            st.warning(f"No submissions found for {form_name} on {selected_date}.")
                        else:
                            df = pd.DataFrame(filtered_data)
                            audio_submissions = df[df['bg_audio'].notna()]  # Take all audio files

                            if audio_submissions.empty:
                                st.warning(f"No audio files found in submissions for {form_name}.")
                            else:
                                st.success(f"Found {len(audio_submissions)} audio files to download for {form_name}")
                                st.write(f"Sample files to download for {form_name}:", audio_submissions[['__id', 'bg_audio']])

                                # Test download section
                                if st.button(f"🚀 Download All Audio Files from {form_name}"):
                                    zip_buffer, download_status = download_audio_files(
                                        selected_server, form_name, project_id, form_id, audio_submissions
                                    )

                                    if zip_buffer is None:
                                        st.error("No files were downloaded. Check the status messages below.")
                                    else:
                                        st.success(f"🎉 Download completed for {form_name}!")
                                        st.download_button(
                                            label=f"⬇️ Download {form_name} Audio Files (ZIP)",
                                            data=zip_buffer.getvalue(),
                                            file_name=f"{form_name.replace(' ', '_')}_AUDIOS_{datetime.now().strftime('%Y%m%d')}.zip",
                                            mime="application/zip"
                                        )

                                    # Display download status messages
                                    st.subheader("Download Status")
                                    for status in download_status:
                                        st.write(status)

    except requests.exceptions.RequestException as e:
        st.error(f"Server connection error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
