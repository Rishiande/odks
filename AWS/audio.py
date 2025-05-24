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
import random
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
from urllib.parse import quote 
# Streamlit Setup
st.set_page_config(page_title="ODK Audio Test Downloader", layout="centered")
st.title("🔊 ODK Audio Test Download (All Files from Each Form)")

# Set up logging
logger = logging.getLogger(__name__)

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
        "Mahesh Misc APP": {
            "152-Vriddhachalam Landscape Survey 05-2025": {"project_id": 18, "form_id": "152-Vriddhachalam Landscape Survey 05-2025"},
            "186-Sivaganga Landscape Survey 05-2025":{"project_id":18,"form_id":"186-Sivaganga Landscape Survey 05-2025"},
            "207-Aruppukkottai Landscape Survey 05-2025":{"project_id":18,"form_id":"207-Aruppukkottai Landscape Survey 05-2025"},
            "212-Mudhukulathur Landscape Survey 05-2025":{"project_id":18,"form_id":"212-Mudhukulathur Landscape Survey 05-2025"},
            "224-Tirunelveli Landscape Survey 05-2025":{"project_id":18,"form_id":"224-Tirunelveli Landscape Survey 05-2025"},
            "61-Harur (SC) Landscape Survey 05-2025":{"project_id":18,"form_id":"61-Harur (SC) Landscape Survey 05-2025"},
            "85-Mettur Landscape Survey 05-2025":{"project_id":18,"form_id":"85-Mettur Landscape Survey 05-2025"}
        },
        "LN Kancheepuram": {
            "28-Alandur Landscape Survey 05-2025": {"project_id": 17, "form_id": "28-Alandur Landscape Survey 05-2025"},
            "29-Sriperumbudur (SC) Landscape Survey 05-2025": {"project_id": 17, "form_id": "29-Sriperumbudur (SC) Landscape Survey 05-2025"},
            "36-Uthiramerur Landscape Survey 05-2025": {"project_id": 17, "form_id": "36-Uthiramerur Landscape Survey 05-2025"},
            "37-Kancheepuram Landscape Survey 05-2025": {"project_id": 17, "form_id": "37-Kancheepuram Landscape Survey 05-2025"},
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
            "109-Gudalur (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "109-Gudalur (SC) Landscape Survey 04-2025"},
            "55-Hosur Landscape Survey 04-2025": {"project_id": 5, "form_id": "55-Hosur Landscape Survey 04-2025"}
        },
        "Bikas Tirunelveli APP": {
            "225-Ambasamudram Landscape Survey 05-2025": {"project_id": 14, "form_id": "225-Ambasamudram Landscape Survey 05-2025"},
            "227-Nanguneri Landscape Survey 05-2025": {"project_id": 14, "form_id": "227-Nanguneri Landscape Survey 05-2025"},
            "228-Radhapuram Landscape Survey 05-2025": {"project_id": 14, "form_id": "228-Radhapuram Landscape Survey 05-2025"}
        },
        "Gopal Misc APP": {
            "148-Kunnam Landscape Survey 05-2025": {"project_id": 16, "form_id": "148-Kunnam Landscape Survey 05-2025"},
            "5-Poonamallee (SC) Landscape Survey 05-2025": {"project_id": 16, "form_id": "5-Poonamallee (SC) Landscape Survey 05-2025"},
            "91-Veerapandi Landscape Survey 05-2025": {"project_id": 16, "form_id": "91-Veerapandi Landscape Survey 05-2025"},
            "125-Udumalpet Landscape Survey 05-2025": {"project_id": 16, "form_id": "125-Udumalpet Landscape Survey 05-2025"},
            "92-Rasipuram (SC) Landscape Survey 05-2025": {"project_id": 16, "form_id": "92-Rasipuram (SC) Landscape Survey 05-2025"},
            "60-Pappireddippatti Landscape Survey 05-2025":{"project_id":16,"form_id":"60-Pappireddippatti Landscape Survey 05-2025"}
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
            "189-Madurai East Landscape Survey 04-2025": {"project_id": 4, "form_id": "189-Madurai East Landscape Survey 04-2025"},
            "66-Polur Landscape Survey 04-2025": {"project_id": 4, "form_id": "66-Polur Landscape Survey 04-2025"},
            "56-Thalli Landscape Survey 04-2025": {"project_id": 4, "form_id": "56-Thalli Landscape Survey 04-2025"},
            "39-Sholingur Landscape Survey 04-2025": {"project_id": 4, "form_id": "39-Sholingur Landscape Survey 04-2025"},
            "38-Arakkonam (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "38-Arakkonam (SC) Landscape Survey 04-2025"},
            "201-Cumbum Landscape Survey 04-2025": {"project_id": 4, "form_id": "201-Cumbum Landscape Survey 04-2025"},
            "199. Periyakulam (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "199. Periyakulam (SC) Landscape Survey 04-2025"},
            "198-Andipatti Landscape Survey 04-2025": {"project_id": 4, "form_id": "198-Andipatti Landscape Survey 04-2025"},
            "180-Pudukkottai Landscape Survey 04-2025": {"project_id": 4, "form_id": "180-Pudukkottai Landscape Survey 04-2025"},
            "158-Chidambaram Landscape Survey 04-2025": {"project_id": 4, "form_id": "158-Chidambaram Landscape Survey 04-2025"},
            "145-Musiri Landscape Survey 04-2025": {"project_id": 4, "form_id": "145-Musiri Landscape Survey 04-2025"},
            "137-Kulithalai Landscape Survey 04-2025": {"project_id": 4, "form_id": "137-Kulithalai Landscape Survey 04-2025"},
            "136-Krishnarayapuram (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "136-Krishnarayapuram (SC) Landscape Survey 04-2025"},
            "12-Perambur Landscape Survey 04-2025": {"project_id": 4, "form_id": "12-Perambur Landscape Survey 04-2025"},
            "109-Gudalur (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "109-Gudalur (SC) Landscape Survey 04-2025"},
            "135-Karur Landscape Survey 04-2025": {"project_id": 4, "form_id": "135-Karur Landscape Survey 04-2025"},
            "3-Thirutthani Landscape Survey 04-2025":{"project_id":4,"form_id":"3-Thirutthani Landscape Survey 04-2025"}
        },
        "03 BK TN AC Landscape": {
            "100-Modakkurichi Landscape Survey 04-2025": {"project_id": 5, "form_id": "100-Modakkurichi Landscape Survey 04-2025"},
            "153-Neyveli Landscape Survey 05-2025": {"project_id": 5, "form_id": "153-Neyveli Landscape Survey 05-2025"},
            "197-Usilampatti Landscape Survey 04-2025": {"project_id": 5, "form_id": "197-Usilampatti Landscape Survey 04-2025"},
            "62-Chengam (SC) Landscape Survey 05-2025": {"project_id": 5, "form_id": "62-Chengam (SC) Landscape Survey 05-2025"},
            "63-Tiruvannamalai Landscape Survey 04-2025": {"project_id": 5, "form_id": "63-Tiruvannamalai Landscape Survey 04-2025"},
            "95-Paramathi-Velur Landscape Survey 05-2025": {"project_id": 5, "form_id": "95-Paramathi-Velur Landscape Survey 05-2025"},
            "33-Thiruporur Landscape Survey 05-2025": {"project_id": 5, "form_id": "33-Thiruporur Landscape Survey 05-2025"},
            "34-Cheyyur (SC) Landscape Survey 05-2025 copy 3": {"project_id": 5, "form_id": "34-Cheyyur (SC) Landscape Survey 05-2025 copy 3"},
            "55-Hosur Landscape Survey 04-2025":{"project_id":5,"form_id":"55-Hosur Landscape Survey 04-2025"}
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
            "37-Kancheepuram": {"project_id": 6, "form_id": "37-Kancheepuram Landscape Survey 05-2025"},
            "183-Aranthangi Landscape Survey 04-2025": {"project_id": 6, "form_id": "183-Aranthangi Landscape Survey 04-2025"}
        },
        "Thoothukudi APP": {
            "214-Thoothukkudi Landscape Survey 05-2025": {"project_id": 10, "form_id": "214-Thoothukkudi Landscape Survey 05-2025"},
            "215-Tiruchendur Landscape Survey 05-2025": {"project_id": 10, "form_id": "215-Tiruchendur Landscape Survey 05-2025"},
            "216-Srivaikuntam Landscape Survey 05-2025": {"project_id": 10, "form_id": "216-Srivaikuntam Landscape Survey 05-2025"},
            "218-Kovilpatti Landscape Survey 05-2025": {"project_id": 10, "form_id": "218-Kovilpatti Landscape Survey 05-2025"},
            "213-Vilathikulam Landscape Survey 05-2025": {"project_id": 10, "form_id": "213-Vilathikulam Landscape Survey 05-2025"},
            "217-Ottapidaram (SC) Landscape Survey 05-2025": {"project_id": 10, "form_id": "217-Ottapidaram (SC) Landscape Survey 05-2025"}
        },
        "Moon MISC": {
            "125-Udumalpet Landscape Survey 05-2025": {"project_id": 21, "form_id": "125-Udumalpet Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/21/forms/125-Udumalpet%20Landscape%20Survey%2005-2025.svc"},
            "42-Arcot Landscape Survey 05-2025": {"project_id": 21, "form_id": "42-Arcot Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/21/forms/42-Arcot%20Landscape%20Survey%2005-2025.svc"},
            "5-Poonamallee (SC) Landscape Survey 05-2025": {"project_id": 21, "form_id": "5-Poonamallee (SC) Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/21/forms/5-Poonamallee%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "92-Rasipuram (SC) Landscape Survey 05-2025": {"project_id": 21, "form_id": "92-Rasipuram (SC) Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/21/forms/92-Rasipuram%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        },
        "Murugan Misc APP": {
            "103-Perundurai Landscape Survey 05-2025": {"project_id": 19, "form_id": "103-Perundurai Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/19/forms/103-Perundurai%20Landscape%20Survey%2005-2025.svc"},
            "155-Cuddalore Landscape Survey 05-2025": {"project_id": 19, "form_id": "155-Cuddalore Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/19/forms/155-Cuddalore%20Landscape%20Survey%2005-2025.svc"},
            "8-Ambattur Landscape Survey 05-2025": {"project_id": 19, "form_id": "8-Ambattur Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/19/forms/8-Ambattur%20Landscape%20Survey%2005-2025.svc"}
        },
        "Shashi Misc": {
            "149-Ariyalur Landscape Survey 05-2025": {"project_id": 20, "form_id": "149-Ariyalur Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/20/forms/149-Ariyalur%20Landscape%20Survey%2005-2025.svc"},
            "172-Papanasam Landscape Survey 05-2025": {"project_id": 20, "form_id": "172-Papanasam Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/20/forms/172-Papanasam%20Landscape%20Survey%2005-2025.svc"},
            "31-Tambaram Landscape Survey 05-2025": {"project_id": 20, "form_id": "31-Tambaram Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/20/forms/31-Tambaram%20Landscape%20Survey%2005-2025.svc"},
            "7-Maduravoyal Landscape Survey 05-2025": {"project_id": 20, "form_id": "7-Maduravoyal Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/20/forms/7-Maduravoyal%20Landscape%20Survey%2005-2025.svc"},
            "97-Kumarapalayam Landscape Survey 05-2025": {"project_id": 20, "form_id": "97-Kumarapalayam Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/20/forms/97-Kumarapalayam%20Landscape%20Survey%2005-2025.svc"},
            "98-Erode (East) Landscape Survey 05-2025": {"project_id": 20, "form_id": "98-Erode (East) Landscape Survey 05-2025", "url": "https://tnodk01.indiaintentions.com/v1/projects/20/forms/98-Erode%20(East)%20Landscape%20Survey%2005-2025.svc"},
            "10-Thiruvottiyur Landscape Survey 05-2025":{"project_id":20,"form_id":"10-Thiruvottiyur Landscape Survey 05-2025"},
            "13-Kolathur Landscape Survey 05-2025":{"project_id":20,"form_id":"13-Kolathur Landscape Survey 05-2025"},
            "15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 05-2025":{"project_id":20,"form_id":"15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 05-2025"},
            "16-Egmore (SC) Landscape Survey 05-2025":{"project_id":20,"form_id":"16-Egmore (SC) Landscape Survey 05-2025"},
            "17-Royapuram Landscape Survey 05-2025":{"project_id":20,"form_id":"17-Royapuram Landscape Survey 05-2025"}
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
            "154-Panruti Landscape Survey 05-2025": {"project_id": 12, "form_id": "154-Panruti Landscape Survey 05-2025"},
            "40-Katpadi Landscape Survey 05-2025": {"project_id": 12, "form_id": "40-Katpadi Landscape Survey 05-2025"},
            "63-Tiruvannamalai Landscape Survey 05-2025": {"project_id": 12, "form_id": "63-Tiruvannamalai Landscape Survey 05-2025"},
            "154-Panruti Landscape Survey 05-2025":{"project_id":12,"form_id":"154-Panruti Landscape Survey 05-2025"},
            "86-Edappadi Landscape Survey 05-2025":{"project_id":12,"form_id":"86-Edappadi Landscape Survey 05-2025"}
        },
        "Nanda TN Landscape": {
            "128-Oddanchatram Landscape Survey 05-2025": {"project_id": 11, "form_id": "128-Oddanchatram Landscape Survey 05-2025"},
            "154-Panruti Landscape Survey 05-2025": {"project_id": 11, "form_id": "154-Panruti Landscape Survey 05-2025"},
            "155-Cuddalore Landscape Survey 05-2025": {"project_id": 11, "form_id": "155-Cuddalore Landscape Survey 05-2025"},
            "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025": {"project_id": 11, "form_id": "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025"},
            "162-Poompuhar Landscape Survey 05-2025": {"project_id": 11, "form_id": "162-Poompuhar Landscape Survey 05-2025"},
            "164-Kilvelur (SC) Landscape Survey 05-2025": {"project_id": 11, "form_id": "164-Kilvelur (SC) Landscape Survey 05-2025"},
            "164-Kilvelur (SC) Landscape Survey 05-2025 V6":{"project_id":11,"form_id":"164-Kilvelur (SC) Landscape Survey 05-2025 V6"},
            "162-Poompuhar Landscape Survey 05-2025 V6": {"project_id": 11, "form_id": "162-Poompuhar Landscape Survey 05-2025 V6"},
            "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025 V6": {"project_id": 11, "form_id": "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025 V6"},
            "162-Poompuhar Landscape Survey 05-2025 V6": {"project_id": 11, "form_id": "162-Poompuhar Landscape Survey 05-2025 V6"},
            "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025 V6": {"project_id": 11, "form_id": "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025 V6"},
            "229-Kanniyakumari Landscape Survey 05-2025": {"project_id": 11, "form_id": "229-Kanniyakumari Landscape Survey 05-2025"},
            "230-Nagercoil Landscape Survey 05-2025": {"project_id": 11, "form_id": "230-Nagercoil Landscape Survey 05-2025"}
        },
        "LN Tirunelveli": {
            "225-Ambasamudram Landscape Survey 05-2025": {"project_id": 16, "form_id": "225-Ambasamudram Landscape Survey 05-2025"},
            "226-Palayamkottai Landscape Survey 05-2025": {"project_id": 16, "form_id": "226-Palayamkottai Landscape Survey 05-2025"},
            "227-Nanguneri Landscape Survey 05-2025": {"project_id": 16, "form_id": "227-Nanguneri Landscape Survey 05-2025"},
            "228-Radhapuram Landscape Survey 05-2025": {"project_id": 16, "form_id": "228-Radhapuram Landscape Survey 05-2025"}
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
            "220-Vasudevanallur (SC) Landscape Survey 05-2025": {"project_id": 13, "form_id": "220-Vasudevanallur (SC) Landscape Survey 05-2025"},
            "219-Sankarankovil (SC) Landscape Survey 05-2025": {"project_id": 13, "form_id": "219-Sankarankovil (SC) Landscape Survey 05-2025"},
            "221-Kadayanallur Landscape Survey 05-2025": {"project_id": 13, "form_id": "221-Kadayanallur Landscape Survey 05-2025"},
            "222-Tenkasi Landscape Survey 05-2025": {"project_id": 13, "form_id": "222-Tenkasi Landscape Survey 05-2025"},
            "223-Alangulam Landscape Survey 05-2025": {"project_id": 13, "form_id": "223-Alangulam Landscape Survey 05-2025"}
        },
        "02 FMRS TN Landscape Survey": {
            "188-Melur Landscape Survey 04-2025": {"project_id": 7, "form_id": "188-Melur Landscape Survey 04-2025"},
            "190-Sholavandan (SC) Landscape Survey 04-2025": {"project_id": 7, "form_id": "190-Sholavandan (SC) Landscape Survey 04-2025"},
            "191-Madurai North Landscape Survey 04-2025": {"project_id": 7, "form_id": "191-Madurai North Landscape Survey 04-2025"},
            "192-Madurai South Landscape Survey 04-2025": {"project_id": 7, "form_id": "192-Madurai South Landscape Survey 04-2025"},
            "193-Madurai Central Landscape Survey 04-2025": {"project_id": 7, "form_id": "193-Madurai Central Landscape Survey 04-2025"},
            "194-Madurai West Landscape Survey 04-2025": {"project_id": 7, "form_id": "194-Madurai West Landscape Survey 04-2025"},
            "196-Thirumangalam Landscape Survey 04-2025": {"project_id": 7, "form_id": "196-Thirumangalam Landscape Survey 04-2025"},
            "195-Thiruparankundram Landscape Survey 04-2025": {"project_id": 7, "form_id": "195-Thiruparankundram Landscape Survey 04-2025"}
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
            "81-Gangavalli (SC) Landscape Survey 05-2025": {"project_id": 4, "form_id": "81-Gangavalli (SC) Landscape Survey 05-2025"},
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
        "Shankar Misc":{
            "112-Avanashi (SC) Landscape Survey 05-2025":{"project_id":17,"form_id":"112-Avanashi (SC) Landscape Survey 05-2025"},
            "27-Shozhinganallur Landscape Survey 05-2025":{"project_id":17,"form_id":"27-Shozhinganallur Landscape Survey 05-2025"},
            "28-Alandur Landscape Survey 05-2025":{"project_id":17,"form_id":"28-Alandur Landscape Survey 05-2025"},
            "32-Chengalpattu Landscape Survey 05-2025":{"project_id":17,"form_id":"32-Chengalpattu Landscape Survey 05-2025"}
        },
        "02 Bikas TN Landscape Survey": {
            "155-Cuddalore Landscape Survey 04-2025": {"project_id": 5, "form_id": "155-Cuddalore Landscape Survey 04-2025"},
            "64-Kilpennathur Landscape Survey 04-2025": {"project_id": 5, "form_id": "64-Kilpennathur Landscape Survey 04-2025"},
            "12-PeramburLandscape Survey 04-2025": {"project_id": 5, "form_id": "12-PeramburLandscape Survey 04-2025"},
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
        },
        "01 FMRS TN Landscape Survey":{
            "139-SrirangamLandscape Survey 04-2025":{"project_id":3,"form_id":"139-SrirangamLandscape Survey 04-2025"},
            "141-Tiruchirappalli (East) Landscape Survey 04-2025":{"project_id":3,"form_id":"141-Tiruchirappalli (East) Landscape Survey 04-2025"},
            "163-Nagapattinam Landscape Survey 04-2025":{"project_id":3,"form_id":"163-Nagapattinam Landscape Survey 04-2025"},
            "172-Papanasam Landscape Survey 04-2025":{"project_id":3,"form_id":"172-Papanasam Landscape Survey 04-2025"},
            "174-Thanjavur Landscape Survey 04-2025":{"project_id":3,"form_id":"174-Thanjavur Landscape Survey 04-2025"},
            "177-Peravurani Landscape Survey 04-2025":{"project_id":3,"form_id":"177-Peravurani Landscape Survey 04-2025"},
            "209-Paramakudi (SC) Landscape Survey 04-2025":{"project_id":3,"form_id":"209-Paramakudi (SC) Landscape Survey 04-2025"},
            "213-Vilathikulam Landscape Survey 04-2025":{"project_id":3,"form_id":"213-Vilathikulam Landscape Survey 04-2025"},
            "217 - Ottapidaram (SC) Landscape Survey 04-2025":{"project_id":3,"form_id":"217 - Ottapidaram (SC) Landscape Survey 04-2025"},
            "65-Kalasapakkam Landscape Survey 04-2025":{"project_id":3,"form_id":"65-Kalasapakkam Landscape Survey 04-2025"},
            "8-Ambattur Landscape Survey 04-2025":{"project_id":3,"form_id":"8-Ambattur Landscape Survey 04-2025"}
        },
        "Sai Thiruvallur": {
            "1-Gummidipoondi Landscape Survey 05-2025": {"project_id": 15, "form_id": "1-Gummidipoondi Landscape Survey 05-2025", "url": "https://tnodk02.indiaintentions.com/v1/projects/15/forms/1-Gummidipoondi%20Landscape%20Survey%2005-2025.svc"},
            "10-Thiruvottiyur Landscape Survey 05-2025": {"project_id": 15, "form_id": "10-Thiruvottiyur Landscape Survey 05-2025", "url": "https://tnodk02.indiaintentions.com/v1/projects/15/forms/10-Thiruvottiyur%20Landscape%20Survey%2005-2025.svc"},
            "2-Ponneri (SC) Landscape Survey 05-2025": {"project_id": 15, "form_id": "2-Ponneri (SC) Landscape Survey 05-2025", "url": "https://tnodk02.indiaintentions.com/v1/projects/15/forms/2-Ponneri%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "5-Poonamallee Landscape Survey 05-2025": {"project_id": 15, "form_id": "5-Poonamallee Landscape Survey 05-2025", "url": "https://tnodk02.indiaintentions.com/v1/projects/15/forms/5-Poonamallee%20Landscape%20Survey%2005-2025.svc"},
            "6-Avadi Landscape Survey 05-2025": {"project_id": 15, "form_id": "6-Avadi Landscape Survey 05-2025", "url": "https://tnodk02.indiaintentions.com/v1/projects/15/forms/6-Avadi%20Landscape%20Survey%2005-2025.svc"},
            "7-Maduravoyal Landscape Survey 05-2025": {"project_id": 15, "form_id": "7-Maduravoyal Landscape Survey 05-2025", "url": "https://tnodk02.indiaintentions.com/v1/projects/15/forms/7-Maduravoyal%20Landscape%20Survey%2005-2025.svc"},
            "9-Madavaram Landscape Survey 05-2025": {"project_id": 15, "form_id": "9-Madavaram Landscape Survey 05-2025", "url": "https://tnodk02.indiaintentions.com/v1/projects/15/forms/9-Madavaram%20Landscape%20Survey%2005-2025.svc"}
        }
    },
    "Server 3": {
        "Sai Mahesh Gopal Salem": {
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
        "Shankar Sai Coimbatore": {
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
            "99-Erode (West) Landscape Survey 05-2025": {"project_id": 5, "form_id": "99-Erode (West) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/5/forms/99-Erode%20(West)%20Landscape%20Survey%2005-2025.svc"},
            "101-Dharapuram (SC) Landscape Survey 05-2025":{"project_id":5,"form_id":"101-Dharapuram (SC) Landscape Survey 05-2025"},
            "102-Kangayam Landscape Survey 05-2025":{"project_id":5,"form_id":"102-Kangayam Landscape Survey 05-2025"},
            "115-Palladam Landscape Survey 05-2025":{"project_id":5,"form_id":"115-Palladam Landscape Survey 05-2025"}
        },
        "01 Bhaskar Srinivas TN Landscape Survey": {
            "165-Vedaranyam Landscape Survey 04-2025": {"project_id": 4, "form_id": "165-Vedaranyam Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/165-Vedaranyam%20Landscape%20Survey%2004-2025.svc"},
            "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/166-Thiruthuraipoondi%20(SC)%20Landscape%20Survey%2004-2025.svc"},
            "167-Mannargudi Landscape Survey 04-2025": {"project_id": 4, "form_id": "167-Mannargudi Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/167-Mannargudi%20Landscape%20Survey%2004-2025.svc"},
            "169-Nannilam Landscape Survey 04-2025": {"project_id": 4, "form_id": "169-Nannilam Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/169-Nannilam%20Landscape%20Survey%2004-2025.svc"},
            "200-Bodinayakanur Landscape Survey 04-2025": {"project_id": 4, "form_id": "200-Bodinayakanur Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/200-Bodinayakanur%20Landscape%20Survey%2004-2025.svc"},
            "77-Ulundurpettai Landscape Survey 04-2025": {"project_id": 4, "form_id": "77-Ulundurpettai Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/77-Ulundurpettai%20Landscape%20Survey%2004-2025.svc"},
            "Test TN Landscape Survey 05-2025": {"project_id": 4, "form_id": "Test TN Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/4/forms/Test%20TN%20Landscape%20Survey%2005-2025.svc"},
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
            "126-Madathukulam Landscape Survey 05-2025": {"project_id": 14, "form_id": "126-Madathukulam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/14/forms/126-Madathukulam%20Landscape%20Survey%2005-2025.svc"},
            "112-Avanashi (SC)Landscape Survey 05-2025": {"project_id": 14, "form_id": "112-Avanashi (SC)Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/14/forms/112-Avanashi%20(SC)Landscape%20Survey%2005-2025.svc"},
            "113-Tiruppur (North) Landscape Survey 05-2025 2 copy 8": {"project_id": 14, "form_id": "113-Tiruppur (North) Landscape Survey 05-2025 2 copy 8", "url": "https://tnodk03.indiaintentions.com/v1/projects/14/forms/113-Tiruppur%20(North)%20Landscape%20Survey%2005-2025%202%20copy%208.svc"},
            "114-Tiruppur (South) Landscape Survey 05-2025": {"project_id": 14, "form_id": "114-Tiruppur (South) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/14/forms/114-Tiruppur%20(South)%20Landscape%20Survey%2005-2025.svc"},
            "125-Udumalpet Landscape Survey 05-2025": {"project_id": 14, "form_id": "125-Udumalpet Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/14/forms/125-Udumalpet%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Kallakurichi APP": {
            "78-Rishivandiyam Landscape Survey 05-2025": {"project_id": 21, "form_id": "78-Rishivandiyam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/21/forms/78-Rishivandiyam%20Landscape%20Survey%2005-2025.svc"},
            "80-Kallakurichi (SC) Landscape Survey 05-2025": {"project_id": 21, "form_id": "80-Kallakurichi (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/21/forms/80-Kallakurichi%20(SC)%20Landscape%20Survey%2005-2025.svc"}
        },
        "Sai Murugan Madurai": {
            "188-Melur Landscape Survey 05-2025": {"project_id": 13, "form_id": "188-Melur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/188-Melur%20Landscape%20Survey%2005-2025.svc"},
            "190-Sholavandan (SC) Landscape Survey 05-2025": {"project_id": 13, "form_id": "190-Sholavandan (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/190-Sholavandan%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "193-Madurai Central Landscape Survey 05-2025": {"project_id": 13, "form_id": "193-Madurai Central Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/193-Madurai%20Central%20Landscape%20Survey%2005-2025.svc"},
            "189-Madurai East Landscape Survey 05-2025": {"project_id": 13, "form_id": "189-Madurai East Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/189-Madurai%20East%20Landscape%20Survey%2005-2025.svc"},
            "191-Madurai North Landscape Survey 05-2025 2": {"project_id": 13, "form_id": "191-Madurai North Landscape Survey 05-2025 2", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/191-Madurai%20North%20Landscape%20Survey%2005-2025%202.svc"},
            "192-Madurai South Landscape Survey 05-2025": {"project_id": 13, "form_id": "192-Madurai South Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/192-Madurai%20South%20Landscape%20Survey%2005-2025.svc"},
            "194-Madurai West Landscape Survey 05-2025": {"project_id": 13, "form_id": "194-Madurai West Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/194-Madurai%20West%20Landscape%20Survey%2005-2025.svc"},
            "195-Thiruparankundram Landscape Survey 05-2025": {"project_id": 13, "form_id": "195-Thiruparankundram Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/195-Thiruparankundram%20Landscape%20Survey%2005-2025.svc"},
            "196-Thirumangalam Landscape Survey 05-2025": {"project_id": 13, "form_id": "196-Thirumangalam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/196-Thirumangalam%20Landscape%20Survey%2005-2025.svc"},
            "197-Usilampatti Landscape Survey 05-2025": {"project_id": 13, "form_id": "197-Usilampatti Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/197-Usilampatti%20Landscape%20Survey%2005-2025.svc"},
            "140-Tiruchirappalli (West) Landscape Survey 05-2025": {"project_id": 13, "form_id": "140-Tiruchirappalli (West) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/13/forms/140-Tiruchirappalli%20(West)%20Landscape%20Survey%2005-2025.svc"}
        },
        "01 Vasu Srinivas TN Landscape": {
            "117-Kavundampalayam Landscape Survey 04-2025": {"project_id": 3, "form_id": "117-Kavundampalayam Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/117-Kavundampalayam%20Landscape%20Survey%2004-2025.svc"},
            "151-Tittakudi (SC) Landscape Survey 04-2025": {"project_id": 3, "form_id": "151-Tittakudi (SC) Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/151-Tittakudi%20(SC)%20Landscape%20Survey%2004-2025.svc"},
            "176-Pattukkottai Landscape Survey 04-2025": {"project_id": 3, "form_id": "176-Pattukkottai Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/176-Pattukkottai%20Landscape%20Survey%2004-2025.svc"},
            "52-Bargur Landscape Survey 04-2025": {"project_id": 3, "form_id": "52-Bargur Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/52-Bargur%20Landscape%20Survey%2004-2025.svc"},
            "70-Gingee Landscape Survey 04-2025": {"project_id": 3, "form_id": "70-Gingee Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/70-Gingee%20Landscape%20Survey%2004-2025.svc"},
            "71-Mailam Landscape Survey 05-2025": {"project_id": 3, "form_id": "71-Mailam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/71-Mailam%20Landscape%20Survey%2005-2025.svc"},
            "72-Tindivanam (SC) Landscape Survey 05-2025": {"project_id": 3, "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/72-Tindivanam%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "75-Vikravandi Landscape Survey 04-2025": {"project_id": 3, "form_id": "75-Vikravandi Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/75-Vikravandi%20Landscape%20Survey%2004-2025.svc"},
            "76-Tirukkoyilur Landscape Survey 04-2025": {"project_id": 3, "form_id": "76-Tirukkoyilur Landscape Survey 04-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/3/forms/76-Tirukkoyilur%20Landscape%20Survey%2004-2025.svc"}
        },
        "Bikas Viluppuram APP": {
            "72-Tindivanam (SC) Landscape Survey 05-2025": {"project_id": 20, "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/72-Tindivanam%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "73-Vanur (SC) Landscape Survey 05-2025": {"project_id": 20, "form_id": "73-Vanur (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/73-Vanur%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "74-Villupuram Landscape Survey 05-2025": {"project_id": 20, "form_id": "74-Villupuram Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/74-Villupuram%20Landscape%20Survey%2005-2025.svc"},
            "70-Gingee Landscape Survey 05-2025": {"project_id": 20, "form_id": "70-Gingee Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/70-Gingee%20Landscape%20Survey%2005-2025.svc"},
            "71-Mailam Landscape Survey 05-2025": {"project_id": 20, "form_id": "71-Mailam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/71-Mailam%20Landscape%20Survey%2005-2025.svc"},
            "75-Vikravandi Landscape Survey 05-2025": {"project_id": 20, "form_id": "75-Vikravandi Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/75-Vikravandi%20Landscape%20Survey%2005-2025.svc"},
            "76-Tirukkoyilur Landscape Survey 05-2025": {"project_id": 20, "form_id": "76-Tirukkoyilur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/20/forms/76-Tirukkoyilur%20Landscape%20Survey%2005-2025.svc"}
        },
        "Chennai APP": {
            "11-Dr.Radhakrishnan Nagar Landscape Survey 05-2025":{"project_id":29,"form_id":"11-Dr.Radhakrishnan Nagar Landscape Survey 05-2025"},
            "13-Kolathur Landscape Survey 05-2025":{"project_id":29,"form_id":"13-Kolathur Landscape Survey 05-2025"},
            "14-Villivakkam Landscape Survey 05-2025":{"project_id":29,"form_id":"14-Villivakkam Landscape Survey 05-2025"},
            "15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 05-2025":{"project_id":29,"form_id":"15-Thiru-Vi-Ka-Nagar (SC) Landscape Survey 05-2025"},
            "16-Egmore (SC) Landscape Survey 05-2025":{"project_id":29,"form_id":"16-Egmore (SC) Landscape Survey 05-2025"},
            "17-Royapuram Landscape Survey 05-2025":{"project_id":29,"form_id":"17-Royapuram Landscape Survey 05-2025"},
            "18-Harbour Landscape Survey 05-2025":{"project_id":29,"form_id":"18-Harbour Landscape Survey 05-2025"},
            "19-Chepauk-Thiruvallikeni Landscape Survey 05-2025":{"project_id":29,"form_id":"19-Chepauk-Thiruvallikeni Landscape Survey 05-2025"},
            "20-Thousand Lights Landscape Survey 05-2025":{"project_id":29,"form_id":"20-Thousand Lights Landscape Survey 05-2025"},
            "21-Anna Nagar Landscape Survey 05-2025":{"project_id":29,"form_id":"21-Anna Nagar Landscape Survey 05-2025"},
            "22-Virugampakkam Landscape Survey 05-2025":{"project_id":29,"form_id":"22-Virugampakkam Landscape Survey 05-2025"},
            "23-Saidapet Landscape Survey 05-2025":{"project_id":29,"form_id":"23-Saidapet Landscape Survey 05-2025"},
            "24-Thiyagarayanagar Landscape Survey 05-2025":{"project_id":29,"form_id":"24-Thiyagarayanagar Landscape Survey 05-2025"},
            "25-Mylapore Landscape Survey 05-2025":{"project_id":29,"form_id":"25-Mylapore Landscape Survey 05-2025"},
            "26-Velachery Landscape Survey 05-2025":{"project_id":29,"form_id":"26-Velachery Landscape Survey 05-2025"}
        },
        "Bikas Chennai APP":{
            "16-Egmore (SC) Landscape Survey 05-2025":{"project_id":16,"form_id":"16-Egmore (SC) Landscape Survey 05-2025"},
            "18-Harbour Landscape Survey 05-2025":{"project_id":16,"form_id":"18-Harbour Landscape Survey 05-2025"},
            "19-Chepauk-Thiruvallikeni Landscape Survey 05-2025":{"project_id":16,"form_id":"19-Chepauk-Thiruvallikeni Landscape Survey 05-2025"},
            "21-Anna Nagar Landscape Survey 05-2025":{"project_id":16,"form_id":"21-Anna Nagar Landscape Survey 05-2025"},
            "14-Villivakkam Landscape Survey 05-2025":{"project_id":16,"form_id":"14-Villivakkam Landscape Survey 05-2025"}
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
        "Bikas Shashi Dharmapuri APP": {
            "57-Palacodu Landscape Survey 05-2025": {"project_id": 18, "form_id": "57-Palacodu Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/57-Palacodu%20Landscape%20Survey%2005-2025.svc"},
            "58-Pennagaram Landscape Survey 05-2025": {"project_id": 18, "form_id": "58-Pennagaram Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/58-Pennagaram%20Landscape%20Survey%2005-2025.svc"},
            "59-Dharmapuri Landscape Survey 05-2025": {"project_id": 18, "form_id": "59-Dharmapuri Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/59-Dharmapuri%20Landscape%20Survey%2005-2025.svc"},
            "61-Harur (SC) Landscape Survey 05-2025": {"project_id": 18, "form_id": "61-Harur (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/61-Harur%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "60-Pappireddippatti Landscape Survey 05-2025": {"project_id": 18, "form_id": "60-Pappireddippatti Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/18/forms/60-Pappireddippatti%20Landscape%20Survey%2005-2025.svc"}
        },
        "Bikas Chengalpattu": {
            "27-Shozhinganallur Landscape Survey 05-2025": {"project_id": 23, "form_id": "27-Shozhinganallur Landscape Survey 05-2025"},
            "30-Pallavaram Landscape Survey 05-2025": {"project_id": 23, "form_id": "30-Pallavaram Landscape Survey 05-2025"},
            "31-Tambaram Landscape Survey 05-2025": {"project_id": 23, "form_id": "31-Tambaram Landscape Survey 05-2025"},
            "32-Chengalpattu Landscape Survey 05-2025": {"project_id": 23, "form_id": "32-Chengalpattu Landscape Survey 05-2025"},
            "33-Thiruporur Landscape Survey 05-2025": {"project_id": 23, "form_id": "33-Thiruporur Landscape Survey 05-2025"},
            "34-Cheyyur (SC) Landscape Survey 05-2025": {"project_id": 23, "form_id": "34-Cheyyur (SC) Landscape Survey 05-2025"},
            "35-Madurantakam (SC) Landscape Survey 05-2025": {"project_id": 23, "form_id": "35-Madurantakam (SC) Landscape Survey 05-2025"}
        },
        "Bikas Misc": {
            "148-Kunnam Landscape Survey 05-2025": {"project_id": 24, "form_id": "148-Kunnam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/148-Kunnam%20Landscape%20Survey%2005-2025.svc"},
            "149-Ariyalur Landscape Survey 05-2025": {"project_id": 24, "form_id": "149-Ariyalur Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/149-Ariyalur%20Landscape%20Survey%2005-2025.svc"},
            "160-Sirkazhi (SC) Landscape Survey 05-2025": {"project_id": 24, "form_id": "160-Sirkazhi (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/160-Sirkazhi%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "161-Mayiladuthurai Landscape Survey 05-2025": {"project_id": 24, "form_id": "161-Mayiladuthurai Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/161-Mayiladuthurai%20Landscape%20Survey%2005-2025.svc"},
            "172-Papanasam Landscape Survey 05-2025": {"project_id": 24, "form_id": "172-Papanasam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/172-Papanasam%20Landscape%20Survey%2005-2025.svc"},
            "216-Srivaikuntam Landscape Survey 05-2025": {"project_id": 24, "form_id": "216-Srivaikuntam Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/216-Srivaikuntam%20Landscape%20Survey%2005-2025.svc"},
            "217-Ottapidaram (SC) Landscape Survey 05-2025": {"project_id": 24, "form_id": "217-Ottapidaram (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/217-Ottapidaram%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "43-Vellore Landscape Survey 05-2025": {"project_id": 24, "form_id": "43-Vellore Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/43-Vellore%20Landscape%20Survey%2005-2025.svc"},
            "68-Cheyyar Landscape Survey 05-2025": {"project_id": 24, "form_id": "68-Cheyyar Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/24/forms/68-Cheyyar%20Landscape%20Survey%2005-2025.svc"}
        },
        "Sai Mayiladurutai": {
            "160-Sirkazhi (SC) Landscape Survey 05-2025": {"project_id": 26, "form_id": "160-Sirkazhi (SC) Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/26/forms/160-Sirkazhi%20(SC)%20Landscape%20Survey%2005-2025.svc"},
            "161-Mayiladuthurai Landscape Survey 05-2025": {"project_id": 26, "form_id": "161-Mayiladuthurai Landscape Survey 05-2025", "url": "https://tnodk03.indiaintentions.com/v1/projects/26/forms/161-Mayiladuthurai%20Landscape%20Survey%2005-2025.svc"}
        },
        "Shyam MISC":{
            "113-Tiruppur (North) Landscape Survey 05-2025 2 copy 8":{"project_id":31,"form_id":"113-Tiruppur (North) Landscape Survey 05-2025 2 copy 8"},
            "114-Tiruppur (South) Landscape Survey 05-2025":{"project_id":31,"form_id":"114-Tiruppur (South) Landscape Survey 05-2025"},
            "227-Nanguneri Landscape Survey 05-2025":{"project_id":31,"form_id":"227-Nanguneri Landscape Survey 05-2025"},
            "234-Killiyoor Landscape Survey 05-2025":{"project_id":31,"form_id":"234-Killiyoor Landscape Survey 05-2025"},
            "35-Madurantakam (SC) Landscape Survey 05-2025":{"project_id":31,"form_id":"35-Madurantakam (SC) Landscape Survey 05-2025"},
            "68-Cheyyar Landscape Survey 05-2025":{"project_id":31,"form_id":"68-Cheyyar Landscape Survey 05-2025"},
            "78-Rishivandiyam Landscape Survey 05-2025":{"project_id":31,"form_id":"78-Rishivandiyam Landscape Survey 05-2025"},
            "79-Sankarapuram Landscape Survey 05-2025":{"project_id":31,"form_id":"79-Sankarapuram Landscape Survey 05-2025"},
            "82-Attur (SC) Landscape Survey 05-2025":{"project_id":31,"form_id":"82-Attur (SC) Landscape Survey 05-2025"}
        },
        "01 Nirmal V6":{
            "105-Anthiyur Landscape Survey 05-2025":{"project_id":9,"form_id":"105-Anthiyur Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/9/forms/105-Anthiyur%20Landscape%20Survey%2005-2025.svc"},
            "93-Senthamangalam (ST) Landscape Survey 05-2025":{"project_id":9,"form_id":"93-Senthamangalam (ST) Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/9/forms/93-Senthamangalam%20(ST)%20Landscape%20Survey%2005-2025.svc"}
        },
        "Arun APP":{
            "1-Gummidipoondi Landscape Survey 05-2025":{"project_id":30,"form_id":"1-Gummidipoondi Landscape Survey 05-2025"},
            "11-Dr.Radhakrishnan Nagar Landscape Survey 05-2025":{"project_id":30,"form_id":"11-Dr.Radhakrishnan Nagar Landscape Survey 05-2025"},
            "18-Harbour Landscape Survey 05-2025":{"project_id":30,"form_id":"18-Harbour Landscape Survey 05-2025"},
            "19-Chepauk-Thiruvallikeni Landscape Survey 05-2025":{"project_id":30,"form_id":"19-Chepauk-Thiruvallikeni Landscape Survey 05-2025"},
            "2-Ponneri (SC) Landscape Survey 05-2025":{"project_id":30,"form_id":"2-Ponneri (SC) Landscape Survey 05-2025"},
            "9-Madavaram Landscape Survey 05-2025":{"project_id":30,"form_id":"9-Madavaram Landscape Survey 05-2025"}
        },
        "Moon MISC 02":{
            "107-Bhavanisagar Landscape Survey 05-2025":{"project_id":27,"form_id":"107-Bhavanisagar Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/27/forms/107-Bhavanisagar%20Landscape%20Survey%2005-2025.svc"},
            "110-Coonoor Landscape Survey 05-2025":{"project_id":27,"form_id":"110-Coonoor Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/27/forms/110-Coonoor%20Landscape%20Survey%2005-2025.svc"},
            "111-Mettuppalayam Landscape Survey 05-2025":{"project_id":27,"form_id":"111-Mettuppalayam Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/27/forms/111-Mettuppalayam%20Landscape%20Survey%2005-2025.svc"},
            "112-Avanashi (SC)Landscape Survey 05-2025":{"project_id":27,"form_id":"112-Avanashi (SC)Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/27/forms/112-Avanashi%20(SC)Landscape%20Survey%2005-2025.svc"},
            "43-Vellore Landscape Survey 05-2025":{"project_id":27,"form_id":"43-Vellore Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/27/forms/43-Vellore%20Landscape%20Survey%2005-2025.svc"},
            "84-Omalur Landscape Survey 05-2025":{"project_id":27,"form_id":"84-Omalur Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/27/forms/84-Omalur%20Landscape%20Survey%2005-2025.svc"},
            "86-Edappadi Landscape Survey 05-2025":{"project_id":27,"form_id":"86-Edappadi Landscape Survey 05-2025"}
        },
        "Mahesh MISC":{
            "133-Vedasandur Landscape Survey 05-2025":{"project_id":25,"form_id":"133-Vedasandur Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/25/forms/133-Vedasandur%20Landscape%20Survey%2005-2025.svc"},
            "188-Melur Landscape Survey 05-2025":{"project_id":25,"form_id":"188-Melur Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/25/forms/188-Melur%20Landscape%20Survey%2005-2025.svc"},
            "20-Thousand Lights Landscape Survey 05-2025":{"project_id":25,"form_id":"20-Thousand Lights Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/25/forms/20-Thousand%20Lights%20Landscape%20Survey%2005-2025.svc"},
            "205-Sivakasi Landscape Survey 05-2025":{"project_id":25,"form_id":"205-Sivakasi Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/25/forms/205-Sivakasi%20Landscape%20Survey%2005-2025.svc"},
            "210-Tiruvadanai Landscape Survey 05-2025":{"project_id":25,"form_id":"210-Tiruvadanai Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/25/forms/210-Tiruvadanai%20Landscape%20Survey%2005-2025.svc"},
            "211-Ramanathapuram Landscape Survey 05-2025":{"project_id":25,"form_id":"211-Ramanathapuram Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/25/forms/211-Ramanathapuram%20Landscape%20Survey%2005-2025.svc"},
            "95-Paramathi-Velur Landscape Survey 05-2025":{"project_id":25,"form_id":"95-Paramathi-Velur Landscape Survey 05-2025","url":"https://tnodk03.indiaintentions.com/v1/projects/25/forms/95-Paramathi-Velur%20Landscape%20Survey%2005-2025.svc"}
        },
        "Omni MISC": {
            "104-Bhavani Landscape Survey 05-2025": {"project_id": 32, "form_id": "104-Bhavani Landscape Survey 05-2025"},
            "106-Gobichettipalayam Landscape Survey 05-2025": {"project_id": 32, "form_id": "106-Gobichettipalayam Landscape Survey 05-2025"},
            "113-Tiruppur (North) Landscape Survey 05-2025 2 copy 8": {"project_id": 32, "form_id": "113-Tiruppur (North) Landscape Survey 05-2025 2 copy 8"},
            "114-Tiruppur (South) Landscape Survey 05-2025": {"project_id": 32, "form_id": "114-Tiruppur (South) Landscape Survey 05-2025"},
            "209-Paramakudi (SC) Landscape Survey 05-2025": {"project_id": 32, "form_id": "209-Paramakudi (SC) Landscape Survey 05-2025"},
            "213-Vilathikulam Landscape Survey 05-2025": {"project_id": 32, "form_id": "213-Vilathikulam Landscape Survey 05-2025"},
            "227-Nanguneri Landscape Survey 05-2025": {"project_id": 32, "form_id": "227-Nanguneri Landscape Survey 05-2025"},
            "232-Padmanabhapuram Landscape Survey 05-2025": {"project_id": 32, "form_id": "232-Padmanabhapuram Landscape Survey 05-2025"},
            "233-Vilavancode Landscape Survey 05-2025": {"project_id": 32, "form_id": "233-Vilavancode Landscape Survey 05-2025"},
            "234-Killiyoor Landscape Survey 05-2025": {"project_id": 32, "form_id": "234-Killiyoor Landscape Survey 05-2025"},
            "34-Cheyyur (SC) Landscape Survey 05-2025": {"project_id": 32, "form_id": "34-Cheyyur (SC) Landscape Survey 05-2025"},
            "35-Madurantakam (SC) Landscape Survey 05-2025": {"project_id": 32, "form_id": "35-Madurantakam (SC) Landscape Survey 05-2025"},
            "4-Thiruvallur Landscape Survey 05-2025": {"project_id": 32, "form_id": "4-Thiruvallur Landscape Survey 05-2025"},
            "68-Cheyyar Landscape Survey 05-2025": {"project_id": 32, "form_id": "68-Cheyyar Landscape Survey 05-2025"},
            "70-Gingee Landscape Survey 05-2025": {"project_id": 32, "form_id": "70-Gingee Landscape Survey 05-2025"},
            "77-Ulundurpettai Landscape Survey 05-2025": {"project_id": 32, "form_id": "77-Ulundurpettai Landscape Survey 05-2025"},
            "78-Rishivandiyam Landscape Survey 05-2025": {"project_id": 32, "form_id": "78-Rishivandiyam Landscape Survey 05-2025"},
            "79-Sankarapuram Landscape Survey 05-2025": {"project_id": 32, "form_id": "79-Sankarapuram Landscape Survey 05-2025"},
            "82-Attur (SC) Landscape Survey 05-2025": {"project_id": 32, "form_id": "82-Attur (SC) Landscape Survey 05-2025"},
            "96-Tiruchengodu Landscape Survey 05-2025": {"project_id": 32, "form_id": "96-Tiruchengodu Landscape Survey 05-2025"}
        }
    }
}

def fetch_all_submissions(selected_server, project_id, form_id, start_date=None, end_date=None):
    """Fetch all submissions with optional date filtering"""
    config = ODK_CONFIGS[selected_server]
    url = f"{config['BASE_URL']}/v1/projects/{project_id}/forms/{urllib.parse.quote(form_id)}.svc/Submissions"
    all_data = []
    skip = 0
    batch_size = 500

    try:
        while True:
            params = {"$top": batch_size, "$skip": skip}
            if start_date or end_date:
                filter_conditions = []
                if start_date:
                    filter_conditions.append(f"__system/submissionDate ge {start_date.strftime('%Y-%m-%dT00:00:00.000Z')}")
                if end_date:
                    filter_conditions.append(f"__system/submissionDate le {end_date.strftime('%Y-%m-%dT23:59:59.999Z')}")
                params["$filter"] = " and ".join(filter_conditions)

            response = requests.get(
                url,
                auth=HTTPBasicAuth(config['ODK_USERNAME'], config['ODK_PASSWORD']),
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

    except Exception as e:
        st.error(f"Failed to fetch data for form {form_id}: {str(e)}")
        logger.error(f"Error fetching submissions for form {form_id}: {str(e)}")
        return []

    return all_data

def download_audio_files(selected_server, form_name, project_id, form_id, audio_submissions):
    """Download audio files from submissions and return as zip buffer"""
    config = ODK_CONFIGS[selected_server]
    zip_buffer = io.BytesIO()
    download_status = []

    try:
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

        # Check if zip has content before returning
        if zip_buffer.tell() == 0:
            zip_buffer.close()
            return None, download_status

        zip_buffer.seek(0)
        return zip_buffer, download_status

    except Exception as e:
        st.error(f"Error creating ZIP file: {str(e)}")
        logger.error(f"Error creating ZIP file: {str(e)}")
        zip_buffer.close()
        return None, download_status

def get_date_suffix(start_date, end_date):
    """Generate date suffix for file names based on start and end dates"""
    if start_date and end_date:
        return f"_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    elif start_date:
        return f"_after_{start_date.strftime('%Y%m%d')}"
    elif end_date:
        return f"_before_{end_date.strftime('%Y%m%d')}"
    return ""

def create_combined_zip(audio_files_data, server_name, date_suffix):
    """Create a combined ZIP file from multiple form audio files"""
    zip_buffer_all = io.BytesIO()
    download_status_all = []
    
    try:
        with zipfile.ZipFile(zip_buffer_all, "w", zipfile.ZIP_DEFLATED) as zip_file_all:
            for project_name, form_name, zip_data, status_list in audio_files_data:
                if zip_data and len(zip_data) > 0:
                    # Create a temporary BytesIO from the zip data
                    temp_buffer = io.BytesIO(zip_data)
                    try:
                        with zipfile.ZipFile(temp_buffer, 'r') as temp_zip:
                            for file_info in temp_zip.namelist():
                                file_content = temp_zip.read(file_info)
                                # Create nested folder structure
                                nested_path = f"{project_name.replace(' ', '_')}/{form_name.replace(' ', '_')}/{file_info}"
                                zip_file_all.writestr(nested_path, file_content)
                    except zipfile.BadZipFile:
                        st.warning(f"Skipping corrupted zip data for {project_name}/{form_name}")
                    finally:
                        temp_buffer.close()
                
                download_status_all.extend(status_list)
        
        # Check if the combined zip has content
        if zip_buffer_all.tell() == 0:
            zip_buffer_all.close()
            return None, download_status_all
        
        zip_buffer_all.seek(0)
        return zip_buffer_all, download_status_all
        
    except Exception as e:
        st.error(f"Error creating combined ZIP file: {str(e)}")
        logger.error(f"Error creating combined ZIP file: {str(e)}")
        zip_buffer_all.close()
        return None, download_status_all

def main():
    try:
        st.sidebar.header("Filter Options")

        selected_server = st.sidebar.selectbox("Select Server", list(forms.keys()))

        if selected_server:
            projects = list(forms[selected_server].keys())
            if not projects:
                st.warning(f"No projects found for server {selected_server}.")
                return

            form_selection_mode = st.sidebar.radio(
                "Form Selection Mode",
                ["Select All Forms", "Select Multiple Projects", "Select Multiple Forms", "Select Forms within Project", "Select Individual Form"],
                horizontal=False
            )

            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input("Start Date", None)
            with col2:
                end_date = st.date_input("End Date", None)

            # Generate date suffix for file names
            date_suffix = get_date_suffix(start_date, end_date)

            if form_selection_mode == "Select All Forms":
                if st.button(f"🚀 Fetch All Forms for All Projects in {selected_server}"):
                    audio_files_data = []

                    total_projects = len(projects)
                    for project_idx, project_name in enumerate(projects, 1):
                        with st.spinner(f"Processing project {project_name} ({project_idx}/{total_projects})..."):
                            all_forms = forms[selected_server][project_name]
                            total_forms = len(all_forms)

                            for form_idx, (form_name, form_info) in enumerate(all_forms.items(), 1):
                                with st.spinner(f"Processing {form_name} ({form_idx}/{total_forms}) in project {project_name}..."):
                                    project_id = form_info['project_id']
                                    form_id = form_info['form_id']

                                    data = fetch_all_submissions(
                                        selected_server, project_id, form_id,
                                        start_date, end_date
                                    )

                                    if data:
                                        df = pd.DataFrame(data)
                                        audio_submissions = df[df['bg_audio'].notna()]

                                        if not audio_submissions.empty:
                                            zip_buffer, download_status = download_audio_files(
                                                selected_server, form_name,
                                                project_id, form_id, audio_submissions
                                            )

                                            if zip_buffer:
                                                # Store the zip data as bytes
                                                zip_data = zip_buffer.getvalue()
                                                zip_buffer.close()  # Close the buffer after getting the data
                                                
                                                audio_files_data.append((project_name, form_name, zip_data, download_status))
                                                st.success(f"✅ Processed {form_name} in {project_name} - {len(audio_submissions)} audio files")
                                            else:
                                                st.warning(f"⚠️ No files downloaded for {form_name} in {project_name}")
                                                audio_files_data.append((project_name, form_name, None, download_status))
                                        else:
                                            st.warning(f"⚠️ No audio files found for {form_name} in {project_name}")
                                    else:
                                        st.warning(f"⚠️ No submissions found for {form_name} in {project_name}")

                    # Create combined ZIP file
                    if audio_files_data:
                        combined_zip, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                        
                        if combined_zip:
                            st.success(f"🎉 All projects and forms processed successfully for {selected_server}!")
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            file_name = f"{selected_server.replace(' ', '_')}_ALL_PROJECTS_AUDIOS_{timestamp}{date_suffix}.zip"
                            
                            st.download_button(
                                label=f"⬇️ Download All Audio Files for {selected_server} (ZIP)",
                                data=combined_zip.getvalue(),
                                file_name=file_name,
                                mime="application/zip"
                            )
                            
                            # Close the combined zip buffer after use
                            combined_zip.close()

                            with st.expander("Show Download Status"):
                                for status in combined_status:
                                    st.write(status)
                        else:
                            st.warning(f"No audio files were found across all projects in {selected_server}")
                    else:
                        st.warning(f"No forms processed for {selected_server}")

            elif form_selection_mode == "Select Multiple Projects":
                selected_projects = st.sidebar.multiselect(
                    "Select Projects",
                    projects,
                    help="Select one or more projects to process all their forms"
                )
                
                if selected_projects:
                    if st.button(f"🚀 Fetch All Forms for Selected Projects"):
                        audio_files_data = []

                        total_selected_projects = len(selected_projects)
                        for project_idx, project_name in enumerate(selected_projects, 1):
                            with st.spinner(f"Processing project {project_name} ({project_idx}/{total_selected_projects})..."):
                                all_forms = forms[selected_server][project_name]
                                total_forms = len(all_forms)

                                for form_idx, (form_name, form_info) in enumerate(all_forms.items(), 1):
                                    with st.spinner(f"Processing {form_name} ({form_idx}/{total_forms}) in project {project_name}..."):
                                        project_id = form_info['project_id']
                                        form_id = form_info['form_id']

                                        data = fetch_all_submissions(
                                            selected_server, project_id, form_id,
                                            start_date, end_date
                                        )

                                        if data:
                                            df = pd.DataFrame(data)
                                            audio_submissions = df[df['bg_audio'].notna()]

                                            if not audio_submissions.empty:
                                                zip_buffer, download_status = download_audio_files(
                                                    selected_server, form_name,
                                                    project_id, form_id, audio_submissions
                                                )

                                                if zip_buffer:
                                                    # Store the zip data as bytes
                                                    zip_data = zip_buffer.getvalue()
                                                    zip_buffer.close()
                                                    
                                                    audio_files_data.append((project_name, form_name, zip_data, download_status))
                                                    st.success(f"✅ Processed {form_name} in {project_name} - {len(audio_submissions)} audio files")
                                                else:
                                                    st.warning(f"⚠️ No files downloaded for {form_name} in {project_name}")
                                                    audio_files_data.append((project_name, form_name, None, download_status))
                                            else:
                                                st.warning(f"⚠️ No audio files found for {form_name} in {project_name}")
                                        else:
                                            st.warning(f"⚠️ No submissions found for {form_name} in {project_name}")

                        # Create combined ZIP file
                        if audio_files_data:
                            combined_zip, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                            
                            if combined_zip:
                                st.success(f"🎉 Selected projects processed successfully for {selected_server}!")
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                selected_projects_str = "_".join([p.replace(' ', '_') for p in selected_projects])
                                file_name = f"{selected_server.replace(' ', '_')}_SELECTED_PROJECTS_{selected_projects_str}_AUDIOS_{timestamp}{date_suffix}.zip"
                                
                                st.download_button(
                                    label=f"⬇️ Download Selected Projects Audio Files (ZIP)",
                                    data=combined_zip.getvalue(),
                                    file_name=file_name,
                                    mime="application/zip"
                                )
                                
                                combined_zip.close()

                                with st.expander("Show Download Status"):
                                    for status in combined_status:
                                        st.write(status)
                            else:
                                st.warning(f"No audio files were found in selected projects")
                        else:
                            st.warning(f"No forms processed for selected projects")

            elif form_selection_mode == "Select Forms within Project":
                selected_project = st.sidebar.selectbox(
                    "Select Project",
                    projects,
                    help="Select a project to choose multiple forms from"
                )
                
                if selected_project:
                    project_forms = list(forms[selected_server][selected_project].keys())
                    selected_forms = st.sidebar.multiselect(
                        f"Select Forms from {selected_project}",
                        project_forms,
                        help="Select one or more forms from the selected project"
                    )
                    
                    if selected_forms:
                        if st.button(f"🚀 Fetch Selected Forms from {selected_project}"):
                            audio_files_data = []
                            
                            total_selected_forms = len(selected_forms)
                            for form_idx, form_name in enumerate(selected_forms, 1):
                                form_info = forms[selected_server][selected_project][form_name]
                                project_id = form_info['project_id']
                                form_id = form_info['form_id']

                                with st.spinner(f"Processing {form_name} ({form_idx}/{total_selected_forms}) in project {selected_project}..."):
                                    data = fetch_all_submissions(
                                        selected_server, project_id, form_id,
                                        start_date, end_date
                                    )

                                    if data:
                                        df = pd.DataFrame(data)
                                        audio_submissions = df[df['bg_audio'].notna()]

                                        if not audio_submissions.empty:
                                            zip_buffer, download_status = download_audio_files(
                                                selected_server, form_name,
                                                project_id, form_id, audio_submissions
                                            )

                                            if zip_buffer:
                                                # Store the zip data as bytes
                                                zip_data = zip_buffer.getvalue()
                                                zip_buffer.close()
                                                
                                                audio_files_data.append((selected_project, form_name, zip_data, download_status))
                                                st.success(f"✅ Processed {form_name} in {selected_project} - {len(audio_submissions)} audio files")
                                            else:
                                                st.warning(f"⚠️ No files downloaded for {form_name} in {selected_project}")
                                                audio_files_data.append((selected_project, form_name, None, download_status))
                                        else:
                                            st.warning(f"⚠️ No audio files found for {form_name} in {selected_project}")
                                    else:
                                        st.warning(f"⚠️ No submissions found for {form_name} in {selected_project}")

                            # Create combined ZIP file
                            if audio_files_data:
                                combined_zip, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                                
                                if combined_zip:
                                    st.success(f"🎉 Selected forms from {selected_project} processed successfully!")
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    selected_forms_str = "_".join([f.replace(' ', '_') for f in selected_forms])
                                    file_name = f"{selected_server.replace(' ', '_')}_{selected_project.replace(' ', '_')}_SELECTED_FORMS_{selected_forms_str}_AUDIOS_{timestamp}{date_suffix}.zip"
                                    
                                    st.download_button(
                                        label=f"⬇️ Download Selected Forms from {selected_project} (ZIP)",
                                        data=combined_zip.getvalue(),
                                        file_name=file_name,
                                        mime="application/zip"
                                    )
                                    
                                    combined_zip.close()

                                    with st.expander("Show Download Status"):
                                        for status in combined_status:
                                            st.write(status)
                                else:
                                    st.warning(f"No audio files were found in selected forms from {selected_project}")
                            else:
                                st.warning(f"No forms processed from {selected_project}")

            elif form_selection_mode == "Select Multiple Forms":
                # Create a list of all forms with their project info
                all_forms_with_projects = []
                for project_name in projects:
                    for form_name, form_info in forms[selected_server][project_name].items():
                        all_forms_with_projects.append({
                            'display_name': f"{project_name} - {form_name}",
                            'project_name': project_name,
                            'form_name': form_name,
                            'project_id': form_info['project_id'],
                            'form_id': form_info['form_id']
                        })

                if not all_forms_with_projects:
                    st.warning(f"No forms found across all projects in {selected_server}.")
                    return

                form_options = [form['display_name'] for form in all_forms_with_projects]
                
                selected_form_options = st.sidebar.multiselect(
                    "Select Forms",
                    form_options,
                    help="Select one or more forms to process"
                )

                if selected_form_options:
                    if st.button(f"🚀 Fetch Selected Forms"):
                        audio_files_data = []
                        
                        total_selected_forms = len(selected_form_options)
                        for form_idx, selected_form_option in enumerate(selected_form_options, 1):
                            # Find the corresponding form info
                            form_info = next(f for f in all_forms_with_projects if f['display_name'] == selected_form_option)
                            
                            project_name = form_info['project_name']
                            form_name = form_info['form_name']
                            project_id = form_info['project_id']
                            form_id = form_info['form_id']

                            with st.spinner(f"Processing {form_name} in {project_name} ({form_idx}/{total_selected_forms})..."):
                                data = fetch_all_submissions(
                                    selected_server, project_id, form_id,
                                    start_date, end_date
                                )

                                if data:
                                    df = pd.DataFrame(data)
                                    audio_submissions = df[df['bg_audio'].notna()]

                                    if not audio_submissions.empty:
                                        zip_buffer, download_status = download_audio_files(
                                            selected_server, form_name,
                                            project_id, form_id, audio_submissions
                                        )

                                        if zip_buffer:
                                            # Store the zip data as bytes
                                            zip_data = zip_buffer.getvalue()
                                            zip_buffer.close()
                                            
                                            audio_files_data.append((project_name, form_name, zip_data, download_status))
                                            st.success(f"✅ Processed {form_name} in {project_name} - {len(audio_submissions)} audio files")
                                        else:
                                            st.warning(f"⚠️ No files downloaded for {form_name} in {project_name}")
                                            audio_files_data.append((project_name, form_name, None, download_status))
                                    else:
                                        st.warning(f"⚠️ No audio files found for {form_name} in {project_name}")
                                else:
                                    st.warning(f"⚠️ No submissions found for {form_name} in {project_name}")

                        # Create combined ZIP file
                        if audio_files_data:
                            combined_zip, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                            
                            if combined_zip:
                                st.success(f"🎉 Selected forms processed successfully!")
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                file_name = f"{selected_server.replace(' ', '_')}_SELECTED_FORMS_AUDIOS_{timestamp}{date_suffix}.zip"
                                
                                st.download_button(
                                    label=f"⬇️ Download Selected Forms Audio Files (ZIP)",
                                    data=combined_zip.getvalue(),
                                    file_name=file_name,
                                    mime="application/zip"
                                )
                                
                                combined_zip.close()

                                with st.expander("Show Download Status"):
                                    for status in combined_status:
                                        st.write(status)
                            else:
                                st.warning(f"No audio files were found in selected forms")
                        else:
                            st.warning(f"No forms processed")

            else:  # Select Individual Form
                all_forms_with_projects = []
                for project_name in projects:
                    for form_name, form_info in forms[selected_server][project_name].items():
                        all_forms_with_projects.append((project_name, form_name, form_info['project_id'], form_info['form_id']))

                if not all_forms_with_projects:
                    st.warning(f"No forms found across all projects in {selected_server}.")
                    return

                form_options = [f"{project_name} - {form_name}" for project_name, form_name, _, _ in all_forms_with_projects]
                selected_form_option = st.sidebar.selectbox("Select Form", form_options)

                if selected_form_option:
                    selected_idx = form_options.index(selected_form_option)
                    project_name, form_name, project_id, form_id = all_forms_with_projects[selected_idx]

                    with st.spinner(f"Fetching submissions for {form_name} in project {project_name}..."):
                        data = fetch_all_submissions(
                            selected_server, project_id, form_id,
                            start_date, end_date
                        )

                    if not data:
                        date_range_msg = ""
                        if start_date and end_date:
                            date_range_msg = f" between {start_date} and {end_date}"
                        elif start_date:
                            date_range_msg = f" after {start_date}"
                        elif end_date:
                            date_range_msg = f" before {end_date}"
                        st.warning(f"No submissions found for {form_name} in {project_name}{date_range_msg}.")
                    else:
                        df = pd.DataFrame(data)
                        audio_submissions = df[df['bg_audio'].notna()]

                        if audio_submissions.empty:
                            st.warning(f"No audio files found in submissions for {form_name} in {project_name}.")
                        else:
                            st.success(f"Found {len(audio_submissions)} audio files to download for {form_name} in {project_name}")

                            with st.expander("Preview files to download"):
                                st.dataframe(audio_submissions[['__id', 'bg_audio']])

                            if st.button(f"🚀 Download Audio Files from {form_name} (Project: {project_name})"):
                                zip_buffer, download_status = download_audio_files(
                                    selected_server, form_name,
                                    project_id, form_id, audio_submissions
                                )

                                if zip_buffer is None:
                                    st.error("No files were downloaded. Check the status messages below.")
                                else:
                                    st.success(f"🎉 Download completed for {form_name} in {project_name}!")
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    file_name = f"{project_name.replace(' ', '_')}_{form_name.replace(' ', '_')}_AUDIOS_{timestamp}{date_suffix}.zip"
                                    
                                    # Get the zip data before closing
                                    zip_data = zip_buffer.getvalue()
                                    zip_buffer.close()
                                    
                                    st.download_button(
                                        label=f"⬇️ Download {form_name} Audio Files (ZIP)",
                                        data=zip_data,
                                        file_name=file_name,
                                        mime="application/zip"
                                    )

                                    st.subheader("Download Status")
                                    for status in download_status:
                                        st.write(status)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
