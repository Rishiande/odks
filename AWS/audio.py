import requests
from requests.auth import HTTPBasicAuth
import streamlit as st
import pandas as pd
import io
import zipfile
from datetime import datetime
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
import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil import parser
from io import BytesIO
import logging
import os
from dotenv import load_dotenv
import urllib.parse
from pydub import AudioSegment
import math

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
            "183-Aranthangi Landscape Survey 04-2025": {"project_id": 6, "form_id": "183-Aranthangi Landscape Survey 04-2025"},
            "37-Kancheepuram" : {"project_id":6,"form_id":"37-Kancheepuram Landscape Survey 05-2025"}
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
            "72-Tindivanam (SC) Landscape Survey 05-2025": {"project_id": 12, "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025"},
            "154-Panruti Landscape Survey 05-2025":{"project_id":12,"form_id":"154-Panruti Landscape Survey 05-2025"},
            "40-Katpadi Landscape Survey 05-2025" :{"project_id":12,"form_id":"40-Katpadi Landscape Survey 05-2025"}
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
            "129-Athoor Landscape Survey 05-2025": {"project_id": 4, "form_id": "129-Athoor Landscape Survey 05-2025 copy 4"},
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
    },
    "Server 3": {
        "Sai Salem": {
            "82-Attur (SC) Landscape Survey 05-2025": {"project_id": 15, "form_id": "82-Attur (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/82-Attur%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "83-Yercaud (ST) Landscape Survey 05-2025": {"project_id": 15, "form_id": "83-Yercaud (ST) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/83-Yercaud%20(ST)%20Landscape%20Survey%2005-2025.svc"},
            "84-Omalur Landscape Survey 05-2025": {"project_id": 15, "form_id": "84-Omalur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/84-Omalur%20Landscape%20Survey%2005-2025.svc"},
            "85-Mettur Landscape Survey 05-2025": {"project_id": 15, "form_id": "85-Mettur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/85-Mettur%20Landscape%20Survey%2005-2025.svc"},
            "86-Edappadi Landscape Survey 05-2025": {"project_id": 15, "form_id": "86-Edappadi Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/86-Edappadi%20Landscape%20Survey%2005-2025.svc"},
            "87-Sankari Landscape Survey 05-2025": {"project_id": 15, "form_id": "87-Sankari Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/87-Sankari%20Landscape%20Survey%2005-2025.svc"},
            "89-Salem (North) Landscape Survey 05-2025": {"project_id": 15, "form_id": "89-Salem (North) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/89-Salem%20(North)%20Landscape%20Survey%2005-2025.svc"},
            "91-Veerapandi Landscape Survey 05-2025": {"project_id": 15, "form_id": "91-Veerapandi Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/15/forms/91-Veerapandi%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Tiruvannamalai APP": {
            "63-Tiruvannamalai Landscape Survey 05-2025": {"project_id": 19, "form_id": "63-Tiruvannamalai Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/19/forms/63-Tiruvannamalai%20Landscape%20Survey%2005-2025.svc"},
            "69-Vandavasi (SC) Landscape Survey 05-2025": {"project_id": 19, "form_id": "69-Vandavasi (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/19/forms/69-Vandavasi%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        },
        "02 Sai Coimbatore": {
            "111-Mettuppalayam Landscape Survey 05-2025": {"project_id": 12, "form_id": "111-Mettuppalayam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/111-Mettuppalayam%20Landscape%20Survey%2005-2025.svc"},
            "116-Sulur Landscape Survey 05-2025": {"project_id": 12, "form_id": "116-Sulur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/116-Sulur%20Landscape%20Survey%2005-2025.svc"},
            "119-Thondamuthur Landscape Survey 05-2025": {"project_id": 12, "form_id": "119-Thondamuthur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/119-Thondamuthur%20Landscape%20Survey%2005-2025.svc"},
            "120-Coimbatore (South) Landscape Survey 05-2025": {"project_id": 12, "form_id": "120-Coimbatore (South) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/120-Coimbatore%20(South)%20Landscape%20Survey%2005-2025.svc"},
            "121-Singanallur Landscape Survey 05-2025": {"project_id": 12, "form_id": "121-Singanallur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/121-Singanallur%20Landscape%20Survey%2005-2025.svc"},
            "122-Kinathukadavu Landscape Survey 05-2025": {"project_id": 12, "form_id": "122-Kinathukadavu Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/122-Kinathukadavu%20Landscape%20Survey%2005-2025.svc"},
            "123-Pollachi Landscape Survey 05-2025": {"project_id": 12, "form_id": "123-Pollachi Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/123-Pollachi%20Landscape%20Survey%2005-2025.svc"},
            "124-Valparai (SC) Landscape Survey 05-2025": {"project_id": 12, "form_id": "124-Valparai (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/12/forms/124-Valparai%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        },
        "01 Laxmi Narayana Erode": {
            "104-Bhavani Landscape Survey 05-2025": {"project_id": 5, "form_id": "104-Bhavani Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/5/forms/104-Bhavani%20Landscape%20Survey%2005-2025.svc"},
            "106-Gobichettipalayam Landscape Survey 05-2025": {"project_id": 5, "form_id": "106-Gobichettipalayam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/5/forms/106-Gobichettipalayam%20Landscape%20Survey%2005-2025.svc"},
            "107-Bhavanisagar Landscape Survey 05-2025": {"project_id": 5, "form_id": "107-Bhavanisagar Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/5/forms/107-Bhavanisagar%20Landscape%20Survey%2005-2025.svc"},
            "98-Erode (East) Landscape Survey 05-2025": {"project_id": 5, "form_id": "98-Erode (East) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/5/forms/98-Erode%20(East)%20Landscape%20Survey%2005-2025.svc"},
            "99-Erode (West) Landscape Survey 05-2025": {"project_id": 5, "form_id": "99-Erode (West) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/5/forms/99-Erode%20(West)%20Landscape%20Survey%2005-2025.svc"}
        },
        "01 Bhaskar Srinivas TN Landscape Survey": {
            "165-Vedaranyam Landscape Survey 04-2025": {"project_id": 4, "form_id": "165-Vedaranyam Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/165-Vedaranyam%20Landscape%20Survey%2004-2025.svc"},
            "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/166-Thiruthuraipoondi%20(SC)%20Landscape%20Survey%2004-2025.svc"},
            "167-Mannargudi Landscape Survey 04-2025": {"project_id": 4, "form_id": "167-Mannargudi Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/167-Mannargudi%20Landscape%20Survey%2004-2025.svc"},
            "169-Nannilam Landscape Survey 04-2025": {"project_id": 4, "form_id": "169-Nannilam Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/169-Nannilam%20Landscape%20Survey%2004-2025.svc"},
            "200-Bodinayakanur Landscape Survey 04-2025": {"project_id": 4, "form_id": "200-Bodinayakanur Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/200-Bodinayakanur%20Landscape%20Survey%2004-2025.svc"},
            "77-Ulundurpettai Landscape Survey 04-2025": {"project_id": 4, "form_id": "77-Ulundurpettai Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/77-Ulundurpettai%20Landscape%20Survey%2004-2025.svc"},
            "Test TN Landscape Survey 05-2025": {"project_id": 4, "form_id": "Test TN Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/Test%20TN%20Landscape%20Survey%2005-2025.svc"}
        },
        "Closed Forms - 01 Bhaskar Srinivas TN Landscape Survey": {
            "168-Thiruvarur Landscape Survey 04-2025": {"project_id": 4, "form_id": "168-Thiruvarur Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/168-Thiruvarur%20Landscape%20Survey%2004-2025.svc"}
        },
        "Bikas Tiruchirapalli APP": {
            "138-Manapparai Landscape Survey 05-2025": {"project_id": 22, "form_id": "138-Manapparai Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/22/forms/138-Manapparai%20Landscape%20Survey%2005-2025.svc"},
            "140-Tiruchirappalli (West) Landscape Survey 05-2025": {"project_id": 22, "form_id": "140-Tiruchirappalli (West) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/22/forms/140-Tiruchirappalli%20(West)%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Tirupathur APP": {
            "40-Katpadi Landscape Survey 05-2025": {"project_id": 17, "form_id": "40-Katpadi Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/17/forms/40-Katpadi%20Landscape%20Survey%2005-2025.svc"},
            "47-Vaniyambadi Landscape Survey 05-2025": {"project_id": 17, "form_id": "47-Vaniyambadi Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/17/forms/47-Vaniyambadi%20Landscape%20Survey%2005-2025.svc"},
            "49-Jolarpet Landscape Survey 05-2025": {"project_id": 17, "form_id": "49-Jolarpet Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/17/forms/49-Jolarpet%20Landscape%20Survey%2005-2025.svc"},
            "50-Tirupattur Landscape Survey 05-2025": {"project_id": 17, "form_id": "50-Tirupattur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/17/forms/50-Tirupattur%20Landscape%20Survey%2005-2025.svc"}
        },
        "Sai Tiruppur": {
            "126-Madathukulam Landscape Survey 05-2025": {"project_id": 14, "form_id": "126-Madathukulam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/14/forms/126-Madathukulam%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Kallakurichi APP": {
            "78-Rishivandiyam Landscape Survey 05-2025": {"project_id": 21, "form_id": "78-Rishivandiyam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/21/forms/78-Rishivandiyam%20Landscape%20Survey%2005-2025.svc"},
            "80-Kallakurichi (SC) Landscape Survey 05-2025": {"project_id": 21, "form_id": "80-Kallakurichi (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/21/forms/80-Kallakurichi%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        },
        "Sai Madurai": {
            "188-Melur Landscape Survey 05-2025": {"project_id": 13, "form_id": "188-Melur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/188-Melur%20Landscape%20Survey%2005-2025.svc"},
            "190-Sholavandan (SC) Landscape Survey 05-2025": {"project_id": 13, "form_id": "190-Sholavandan (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/190-Sholavandan%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "193-Madurai Central Landscape Survey 05-2025": {"project_id": 13, "form_id": "193-Madurai Central Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/193-Madurai%20Central%20Landscape%20Survey%2005-2025.svc"}
        },
        "01 Vasu Srinivas TN Landscape": {
            "117-Kavundampalayam Landscape Survey 04-2025": {"project_id": 3, "form_id": "117-Kavundampalayam Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/117-Kavundampalayam%20Landscape%20Survey%2004-2025.svc"},
            "151-Tittakudi (SC) Landscape Survey 04-2025": {"project_id": 3, "form_id": "151-Tittakudi (SC) Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/151-Tittakudi%20(SC)%20Landscape%20Survey%2004-2025.svc"},
            "176-Pattukkottai Landscape Survey 04-2025": {"project_id": 3, "form_id": "176-Pattukkottai Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/176-Pattukkottai%20Landscape%20Survey%2004-2025.svc"},
            "52-Bargur Landscape Survey 04-2025": {"project_id": 3, "form_id": "52-Bargur Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/52-Bargur%20Landscape%20Survey%2004-2025.svc"},
            "70-Gingee Landscape Survey 04-2025": {"project_id": 3, "form_id": "70-Gingee Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/70-Gingee%20Landscape%20Survey%2004-2025.svc"},
            "71-Mailam Landscape Survey 05-2025": {"project_id": 3, "form_id": "71-Mailam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/71-Mailam%20Landscape%20Survey%2005-2025.svc"},
            "72-Tindivanam (SC) Landscape Survey 05-2025": {"project_id": 3, "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/72-Tindivanam%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "75-Vikravandi Landscape Survey 04-2025": {"project_id": 3, "form_id": "75-Vikravandi Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/75-Vikravandi%20Landscape%20Survey%2004-2025.svc"}
        },
        "Closed Forms - 01 Vasu Srinivas TN Landscape": {
            "76-Tirukkoyilur Landscape Survey 04-2025": {"project_id": 3, "form_id": "76-Tirukkoyilur Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/76-Tirukkoyilur%20Landscape%20Survey%2004-2025.svc"}
        },
        "01 Nirmal V6": {
            "105-Anthiyur Landscape Survey 05-2025": {"project_id": 9, "form_id": "105-Anthiyur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/9/forms/105-Anthiyur%20Landscape%20Survey%2005-2025.svc"},
            "93-Senthamangalam (ST) Landscape Survey 05-2025": {"project_id": 9, "form_id": "93-Senthamangalam (ST) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/9/forms/93-Senthamangalam%20(ST)%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Viluppuram APP": {
            "72-Tindivanam (SC) Landscape Survey 05-2025": {"project_id": 20, "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/72-Tindivanam%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "73-Vanur (SC) Landscape Survey 05-2025": {"project_id": 20, "form_id": "73-Vanur (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/73-Vanur%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "74-Villupuram Landscape Survey 05-2025": {"project_id": 20, "form_id": "74-Villupuram Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/74-Villupuram%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Chennai APP": {
            "14-Villivakkam Landscape Survey 05-2025": {"project_id": 16, "form_id": "14-Villivakkam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/16/forms/14-Villivakkam%20Landscape%20Survey%2005-2025.svc"},
            "16-Egmore (SC) Landscape Survey 05-2025": {"project_id": 16, "form_id": "16-Egmore (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/16/forms/16-Egmore%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "18-Harbour Landscape Survey 05-2025": {"project_id": 16, "form_id": "18-Harbour Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/16/forms/18-Harbour%20%20Landscape%20Survey%2005-2025.svc"},
            "19-Chepauk-Thiruvallikeni Landscape Survey 05-2025": {"project_id": 16, "form_id": "19-Chepauk-Thiruvallikeni Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/16/forms/19-Chepauk-Thiruvallikeni%20Landscape%20Survey%2005-2025.svc"},
            "21-Anna Nagar Landscape Survey 05-2025": {"project_id": 16, "form_id": "21-Anna Nagar Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/16/forms/21-Anna%20Nagar%20Landscape%20Survey%2005-2025.svc"}
        },
        "01 Sai Namakkal": {
            "92-Rasipuram (SC) Landscape Survey 05-2025": {"project_id": 11, "form_id": "92-Rasipuram (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/11/forms/92-Rasipuram%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "94-Namakkal Landscape Survey 05-2025": {"project_id": 11, "form_id": "94-Namakkal Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/11/forms/94-Namakkal%20Landscape%20Survey%2005-2025.svc"},
            "96-Tiruchengodu Landscape Survey 05-2025": {"project_id": 11, "form_id": "96-Tiruchengodu Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/11/forms/96-Tiruchengodu%20Landscape%20Survey%2005-2025.svc"},
            "97-Kumarapalayam Landscape Survey 05-2025": {"project_id": 11, "form_id": "97-Kumarapalayam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/11/forms/97-Kumarapalayam%20Landscape%20Survey%2005-2025.svc"}
        },
        "05 Beekay V6": {
            "178-Gandharvakottai (SC) Landscape Survey 05-2025": {"project_id": 8, "form_id": "178-Gandharvakottai (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/8/forms/178-Gandharvakottai%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "4-Thiruvallur Landscape Survey 05-2025": {"project_id": 8, "form_id": "4-Thiruvallur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/8/forms/4-Thiruvallur%20Landscape%20Survey%2005-2025.svc"},
            "51-Uthangarai (SC) Landscape Survey 05-2025": {"project_id": 8, "form_id": "51-Uthangarai (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/8/forms/51-Uthangarai%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        },
        "03 Bikas V6": {
            "14-Villivakkam Landscape Survey 05-2025": {"project_id": 10, "form_id": "14-Villivakkam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/10/forms/14-Villivakkam%20Landscape%20Survey%2005-2025.svc"},
            "176-Pattukkottai Landscape Survey 05-2025": {"project_id": 10, "form_id": "176-Pattukkottai Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/10/forms/176-Pattukkottai%20Landscape%20Survey%2005-2025.svc"},
            "182-Alangudi Landscape Survey 05-2025": {"project_id": 10, "form_id": "182-Alangudi Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/10/forms/182-Alangudi%20Landscape%20Survey%2005-2025.svc"},
            "207-Aruppukkottai Landscape Survey 05-2025": {"project_id": 10, "form_id": "207-Aruppukkottai Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/10/forms/207-Aruppukkottai%20Landscape%20Survey%2005-2025.svc"},
            "223-Alangulam Landscape Survey 05-2025": {"project_id": 10, "form_id": "223-Alangulam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/10/forms/223-Alangulam%20Landscape%20Survey%2005-2025.svc"},
            "44-Anaikattu Landscape Survey 05-2025": {"project_id": 10, "form_id": "44-Anaikattu Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/10/forms/44-Anaikattu%20Landscape%20Survey%2005-2025.svc"},
            "81-Gangavalli (SC) Landscape Survey 05-2025": {"project_id": 10, "form_id": "81-Gangavalli (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/10/forms/81-Gangavalli%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Dharmapuri APP": {
            "57-Palacodu Landscape Survey 05-2025": {"project_id": 18, "form_id": "57-Palacodu Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/57-Palacodu%20Landscape%20Survey%2005-2025.svc"},
            "58-Pennagaram Landscape Survey 05-2025": {"project_id": 18, "form_id": "58-Pennagaram Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/58-Pennagaram%20Landscape%20Survey%2005-2025.svc"},
            "59-Dharmapuri Landscape Survey 05-2025": {"project_id": 18, "form_id": "59-Dharmapuri Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/59-Dharmapuri%20Landscape%20Survey%2005-2025.svc"},
            "61-Harur (SC) Landscape Survey 05-2025": {"project_id": 18, "form_id": "61-Harur (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/61-Harur%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        }
    }
}
def fetch_projects(selected_server):
    config = ODK_CONFIGS[selected_server]
    projects_url = f"{config['BASE_URL']}/v1/projects"
    response = requests.get(
        projects_url,
        auth=HTTPBasicAuth(config['ODK_USERNAME'], config['ODK_PASSWORD']),
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def fetch_forms(selected_server, project_id):
    config = ODK_CONFIGS[selected_server]
    forms_url = f"{config['BASE_URL']}/v1/projects/{project_id}/forms"
    response = requests.get(
        forms_url,
        auth=HTTPBasicAuth(config['ODK_USERNAME'], config['ODK_PASSWORD']),
        timeout=30
    )
    response.raise_for_status()
    return response.json()

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

def filter_submissions_by_date_range(submissions, start_date, end_date):
    if start_date and end_date:
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        return [submission for submission in submissions 
                if start_date_str <= submission['__system']['submissionDate'][:10] <= end_date_str]
    return submissions

def download_audio_files(selected_server, project_id, form_id, form_name, audio_submissions):
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

    zip_buffer.seek(0)
    return zip_buffer, download_status

def main():
    try:
        st.sidebar.header("Filter Options")
        selected_server = st.sidebar.selectbox("Select Server", list(ODK_CONFIGS.keys()))
        
        if selected_server:
            start_date = st.sidebar.date_input("Start Date", None)
            end_date = st.sidebar.date_input("End Date", None)

            if start_date and end_date and start_date > end_date:
                st.error("Start date must be before end date!")
                return

            with st.spinner("Fetching projects..."):
                projects = fetch_projects(selected_server)

            zip_buffers = {}
            
            for project in projects:
                project_id = project['id']
                project_name = project.get('name', f"Project_{project_id}")
                
                with st.spinner(f"Fetching forms for {project_name}..."):
                    forms = fetch_forms(selected_server, project_id)
                
                for form in forms:
                    form_id = form['xmlFormId']
                    form_name = form.get('name', form_id)
                    
                    with st.spinner(f"Fetching submissions for {form_name}..."):
                        data = fetch_submissions(selected_server, project_id, form_id)
                    
                    if not data:
                        st.warning(f"No submissions found for {form_name} in {project_name}.")
                        continue

                    filtered_data = filter_submissions_by_date_range(data, start_date, end_date)
                    
                    if not filtered_data:
                        st.warning(f"No submissions found for {form_name} in {project_name} within date range.")
                        continue

                    df = pd.DataFrame(filtered_data)
                    audio_submissions = df[df['bg_audio'].notna()]
                    
                    if audio_submissions.empty:
                        st.warning(f"No audio files found in submissions for {form_name} in {project_name}.")
                        continue

                    st.success(f"Found {len(audio_submissions)} audio files for {form_name} in {project_name}")
                    st.write(f"Sample files for {form_name}:", audio_submissions[['__id', 'bg_audio']])

                    if st.button(f"🚀 Download Audio Files for {form_name} in {project_name}"):
                        zip_buffer, download_status = download_audio_files(
                            selected_server, project_id, form_id, form_name, audio_submissions
                        )

                        if zip_buffer is None:
                            st.error(f"No files downloaded for {form_name}. Check status messages.")
                        else:
                            zip_buffers[f"{project_name}_{form_name}"] = {
                                'buffer': zip_buffer,
                                'project_name': project_name,
                                'form_name': form_name
                            }

                        st.subheader(f"Download Status for {form_name}")
                        for status in download_status:
                            st.write(status)

            # Create project-wise ZIP files
            if zip_buffers:
                for key, zip_info in zip_buffers.items():
                    st.download_button(
                        label=f"⬇️ Download {zip_info['project_name']} - {zip_info['form_name']} Audio Files (ZIP)",
                        data=zip_info['buffer'].getvalue(),
                        file_name=f"{zip_info['project_name']}_{zip_info['form_name']}_AUDIOS_{datetime.now().strftime('%Y%m%d')}.zip",
                        mime="application/zip"
                    )

    except requests.exceptions.RequestException as e:
        st.error(f"Server connection error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
