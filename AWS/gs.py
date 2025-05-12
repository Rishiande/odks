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
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ODK Configuration
ODK_CONFIG = {
    "server1": {
        "BASE_URL": "https://tnodk01.indiaintentions.com",
        "USERNAME": os.getenv("ODK_USERNAME", "rushi@tnodk01.ii.com"),
        "PASSWORD": os.getenv("ODK_PASSWORD", "rushi2025&")
    },
    "server2": {
        "BASE_URL": "https://tnodk02.indiaintentions.com",
        "USERNAME": os.getenv("ODK_USERNAME_SERVER2", "rushi@tnodk01.ii.com"),
        "PASSWORD": os.getenv("ODK_PASSWORD_SERVER2", "rushi2025&")
    },
    "server3": {
        "BASE_URL": "https://tnodk03.indiaintentions.com",
        "USERNAME": os.getenv("ODK_USERNAME_SERVER3", "rushi@tnodk01.ii.com"),
        "PASSWORD": os.getenv("ODK_PASSWORD_SERVER3", "rushi2025&")
    }
}

# Survey configurations
SURVEYS = {
    "server1": {
        "Krishnagiri APP": {
            "52-Bargur": {
                "form_id": "52-Bargur Landscape Survey 05-2025",
                "project_id": 7
            },
            "53-Krishnagiri": {
                "form_id": "53-Krishnagiri Landscape Survey 05-2025",
                "project_id": 7
            }
        },
        "04 TN AC Landscape": {
            "151-Tittakudi (SC)": {
                "form_id": "151-Tittakudi (SC) Landscape Survey 05-2025",
                "project_id": 6
            },
            "156-Kurinjipadi": {
                "form_id": "156-Kurinjipadi Landscape Survey 05-2025",
                "project_id": 6
            },
            "159-Kattumannarkoil (SC)": {
                "form_id": "159-Kattumannarkoil (SC) Landscape Survey 04-2025",
                "project_id": 6
            },
            "181-Thirumayam": {
                "form_id": "181-Thirumayam Landscape Survey 04-2025",
                "project_id": 6
            },
            "204-Sattur": {
                "form_id": "204-Sattur Landscape Survey 05-2025",
                "project_id": 6
            },
            "37-Kancheepuram": {
                "form_id": "37-Kancheepuram Landscape Survey 05-2025",
                "project_id": 6
            }
        },
        "03 BK TN AC Landscape": {
            "100-Modakkurichi": {
                "form_id": "100-Modakkurichi Landscape Survey 04-2025",
                "project_id": 5
            },
            "153-Neyveli": {
                "form_id": "153-Neyveli Landscape Survey 05-2025",
                "project_id": 5
            },
            "197-Usilampatti": {
                "form_id": "197-Usilampatti Landscape Survey 04-2025",
                "project_id": 5
            },
            "63-Tiruvannamalai": {
                "form_id": "63-Tiruvannamalai Landscape Survey 04-2025",
                "project_id": 5
            },
            "95-Paramathi-Velur": {
                "form_id": "95-Paramathi-Velur Landscape Survey 05-2025",
                "project_id": 5
            }
        },
        "Thoothukudi APP": {
            "215-Tiruchendur": {
                "form_id": "215-Tiruchendur Landscape Survey 05-2025",
                "project_id": 10
            }
        },
        "Virudhunagar APP": {
            "206-Virudhunagar": {
                "form_id": "206-Virudhunagar Landscape Survey 05-2025",
                "project_id": 8
            },
            "208-Tiruchuli": {
                "form_id": "208-Tiruchuli Landscape Survey 05-2025",
                "project_id": 8
            }
        },
        "Tanjavore APP": {
            "176-Pattukkottai": {
                "form_id": "176-Pattukkottai Landscape Survey 05-2025",
                "project_id": 9
            }
        },
        "BK TN AC Landscape": {
            "103-Perundurai": {
                "form_id": "103-Perundurai Landscape Survey 04-2025",
                "project_id": 4
            },
            "132 Dindigul": {
                "form_id": "132 Dindigul Landscape Survey 04-2025",
                "project_id": 4
            },
            "135-Karur": {
                "form_id": "135-Karur Landscape Survey 04-2025",
                "project_id": 4
            },
            "146. Thuraiyur (SC)": {
                "form_id": "146. Thuraiyur (SC) Landscape Survey 04-2025",
                "project_id": 4
            },
            "150-Jayankondam": {
                "form_id": "150-Jayankondam Landscape Survey 04-2025",
                "project_id": 4
            },
            "155-Cuddalore": {
                "form_id": "155-Cuddalore Landscape Survey 04-2025",
                "project_id": 4
            },
            "171-Kumbakonam": {
                "form_id": "171-Kumbakonam Landscape Survey 04-2025",
                "project_id": 4
            },
            "189-Madurai East": {
                "form_id": "189-Madurai East Landscape Survey 04-2025",
                "project_id": 4
            }
        },
        "Ramanathapuram APP": {
            "211-Ramanathapuram": {
                "form_id": "211-Ramanathapuram Landscape Survey 05-2025",
                "project_id": 11
            },
            "212-Mudhukulathur": {
                "form_id": "212-Mudhukulathur Landscape Survey 05-2025",
                "project_id": 11
            }
        },
        "Sai Sivaganga APP": {
            "184-Karaikudi": {
                "form_id": "184-Karaikudi Landscape Survey 05-2025",
                "project_id": 12
            },
            "185-Tiruppattur": {
                "form_id": "185-Tiruppattur Landscape Survey 05-2025",
                "project_id": 12
            },
            "186-Sivaganga": {
                "form_id": "186-Sivaganga Landscape Survey 05-2025",
                "project_id": 12
            },
            "187-Manamadurai (SC)": {
                "form_id": "187-Manamadurai (SC) Landscape Survey 05-2025",
                "project_id": 12
            }
        }
    },
    "server2": {
        "01 Shankar Subramaniam TN Landscape Survey": {
            "108-Udhagamandalam": {
                "form_id": "108-Udhagamandalam Landscape Survey 04-2025",
                "project_id": 10
            },
            "142-Thiruverumbur": {
                "form_id": "142-Thiruverumbur Landscape Survey 04-2025",
                "project_id": 10
            },
            "143-Lalgudi": {
                "form_id": "143-Lalgudi Landscape Survey 05-2025",
                "project_id": 10
            },
            "144-Manachanallur": {
                "form_id": "144-Manachanallur Landscape Survey 04-2025",
                "project_id": 10
            },
            "175-Orathanadu": {
                "form_id": "175-Orathanadu Landscape Survey 05-2025",
                "project_id": 10
            },
            "219-Sankarankovil (SC)": {
                "form_id": "219-Sankarankovil (SC) Landscape Survey 04-2025",
                "project_id": 10
            },
            "54-Veppanahalli": {
                "form_id": "54-Veppanahalli Landscape Survey 04-2025",
                "project_id": 10
            }
        },
        "Nanda TN Landscape": {
            "128-Oddanchatram": {
                "form_id": "128-Oddanchatram Landscape Survey 05-2025",
                "project_id": 11
            },
            "154-Panruti": {
                "form_id": "154-Panruti Landscape Survey 05-2025",
                "project_id": 11
            },
            "155-Cuddalore": {
                "form_id": "155-Cuddalore Landscape Survey 05-2025",
                "project_id": 11
            },
            "162-Poompuhar": {
                "form_id": "162-Poompuhar Landscape Survey 05-2025",
                "project_id": 11
            },
            "164-Kilvelur (SC)": {
                "form_id": "164-Kilvelur (SC) Landscape Survey 05-2025",
                "project_id": 11
            },
            "170-Thiruvidaimarudur (SC)": {
                "form_id": "170-Thiruvidaimarudur (SC) Landscape Survey 05-2025",
                "project_id": 11
            }
        },
        "Shankar Tenkasi": {
            "220-Vasudevanallur (SC)": {
                "form_id": "220-Vasudevanallur (SC) Landscape Survey 05-2025",
                "project_id": 13
            }
        },
        "Nanda Kanniyakumari APP": {
            "229-Kanniyakumari": {
                "form_id": "229-Kanniyakumari Landscape Survey 05-2025",
                "project_id": 14
            },
            "230-Nagercoil": {
                "form_id": "230-Nagercoil Landscape Survey 05-2025",
                "project_id": 14
            },
            "231-Colachal": {
                "form_id": "231-Colachal Landscape Survey 05-2025",
                "project_id": 14
            },
            "232-Padmanabhapuram": {
                "form_id": "232-Padmanabhapuram Landscape Survey 05-2025",
                "project_id": 14
            },
            "233-Vilavancode": {
                "form_id": "233-Vilavancode Landscape Survey 05-2025",
                "project_id": 14
            },
            "234-Killiyoor": {
                "form_id": "234-Killiyoor Landscape Survey 05-2025",
                "project_id": 14
            }
        },
        "01 FMRS TN Landscape Survey": {
            "141-Tiruchirappalli (East)": {
                "form_id": "141-Tiruchirappalli (East) Landscape Survey 04-2025",
                "project_id": 3
            },
            "172-Papanasam": {
                "form_id": "172-Papanasam Landscape Survey 04-2025",
                "project_id": 3
            },
            "177-Peravurani": {
                "form_id": "177-Peravurani Landscape Survey 04-2025",
                "project_id": 3
            },
            "209-Paramakudi (SC)": {
                "form_id": "209-Paramakudi (SC) Landscape Survey 04-2025",
                "project_id": 3
            },
            "213-Vilathikulam": {
                "form_id": "213-Vilathikulam Landscape Survey 04-2025",
                "project_id": 3
            },
            "217-Ottapidaram (SC)": {
                "form_id": "217 - Ottapidaram (SC) Landscape Survey 04-2025",
                "project_id": 3
            },
            "65-Kalasapakkam": {
                "form_id": "65-Kalasapakkam Landscape Survey 04-2025",
                "project_id": 3
            },
            "8-Ambattur": {
                "form_id": "8-Ambattur Landscape Survey 04-2025",
                "project_id": 3
            }
        },
        "02 FMRS TN Landscape Survey": {
            "188-Melur": {
                "form_id": "188-Melur Landscape Survey 04-2025",
                "project_id": 7
            },
            "190-Sholavandan (SC)": {
                "form_id": "190-Sholavandan (SC) Landscape Survey 04-2025",
                "project_id": 7
            },
            "191-Madurai North": {
                "form_id": "191-Madurai North Landscape Survey 04-2025",
                "project_id": 7
            },
            "192-Madurai South": {
                "form_id": "192-Madurai South Landscape Survey 04-2025",
                "project_id": 7
            },
            "193-Madurai Central": {
                "form_id": "193-Madurai Central Landscape Survey 04-2025",
                "project_id": 7
            },
            "194-Madurai West": {
                "form_id": "194-Madurai West Landscape Survey 04-2025",
                "project_id": 7
            },
            "195-Thiruparankundram": {
                "form_id": "195-Thiruparankundram Landscape Survey 04-2025",
                "project_id": 7
            },
            "196-Thirumangalam": {
                "form_id": "196-Thirumangalam Landscape Survey 04-2025",
                "project_id": 7
            }
        },
        "01 Bikas TN Landscape Survey": {
            "127-Palani": {
                "form_id": "127-Palani Landscape Survey 05-2025",
                "project_id": 4
            },
            "128-Oddanchatram": {
                "form_id": "128-Oddanchatram Landscape Survey 05-2025",
                "project_id": 4
            },
            "129-Athoor": {
                "form_id": "129-Athoor Landscape Survey 05-2025 copy 4",
                "project_id": 4
            },
            "130-Nilakkottai (SC)": {
                "form_id": "130-Nilakkottai (SC) Landscape Survey 05-2025",
                "project_id": 4
            },
            "143-Lalgudi": {
                "form_id": "143-Lalgudi Landscape Survey 05-2025",
                "project_id": 4
            },
            "147-Perambalur (SC)": {
                "form_id": "147-Perambalur (SC) Landscape Survey 04-2025",
                "project_id": 4
            },
            "45-Kilvaithinankuppam (SC)": {
                "form_id": "45-Kilvaithinankuppam (SC) Landscape Survey 05-2025",
                "project_id": 4
            },
            "47-Vaniyambadi": {
                "form_id": "47-Vaniyambadi Landscape Survey 05-2025",
                "project_id": 4
            },
            "49-Jolarpet": {
                "form_id": "49-Jolarpet Landscape Survey 04-2025",
                "project_id": 4
            },
            "69-Vandavasi (SC)": {
                "form_id": "69-Vandavasi (SC) Landscape Survey 05-2025",
                "project_id": 4
            },
            "81-Gangavalli (SC)": {
                "form_id": "81-Gangavalli (SC) Landscape Survey 05-2025",
                "project_id": 4
            }
        },
        "02 Shashi TN Landscape": {
            "25-Mylapore": {
                "form_id": "25-Mylapore Landscape Survey 04-2025",
                "project_id": 8
            }
        },
        "02 Bikas TN Landscape Survey": {
            "155-Cuddalore": {
                "form_id": "155-Cuddalore Landscape Survey 04-2025",
                "project_id": 5
            },
            "64-Kilpennathur": {
                "form_id": "64-Kilpennathur Landscape Survey 04-2025",
                "project_id": 5
            }
        },
        "01 Shashi TN Landscape Survey": {
            "88-Salem (West)": {
                "form_id": "88-Salem (West) Landscape Survey 04-2025",
                "project_id": 6
            },
            "89-Salem (North)": {
                "form_id": "89-Salem (North) Landscape Survey 04-2025",
                "project_id": 6
            },
            "90-Salem (South)": {
                "form_id": "90-Salem (South) Landscape Survey 04-2025",
                "project_id": 6
            },
            "83-Yercaud (ST)": {
                "form_id": "83-Yercaud (ST) Landscape Survey 04-2025",
                "project_id": 6
            }
        },
        "03 Bikas V6": {
            "40-Katpadi": {
                "form_id": "40-Katpadi Landscape Survey 05-2025",
                "project_id": 12
            },
            "41-Ranipet": {
                "form_id": "41-Ranipet Landscape Survey 05-2025",
                "project_id": 12
            },
            "42-Arcot": {
                "form_id": "42-Arcot Landscape Survey 05-2025",
                "project_id": 12
            },
            "50-Tirupattur": {
                "form_id": "50-Tirupattur Landscape Survey 05-2025",
                "project_id": 12
            },
            "63-Tiruvannamalai": {
                "form_id": "63-Tiruvannamalai Landscape Survey 05-2025",
                "project_id": 12
            },
            "72-Tindivanam (SC)": {
                "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025",
                "project_id": 12
            },
            "73-Vanur": {
                "form_id": "73-Vanur Landscape Survey 05-2025",
                "project_id": 12
            },
            "78-Rishivandiyam": {
                "form_id": "78-Rishivandiyam Landscape Survey 05-2025",
                "project_id": 12
            },
            "80-Kallakurichi": {
                "form_id": "80-Kallakurichi Landscape Survey 05-2025",
                "project_id": 12
            },
            "154-Panruti": {
                "form_id": "154-Panruti Landscape Survey 05-2025",
                "project_id": 12
            },
            "182-Alangudi": {
                "form_id": "182-Alangudi Landscape Survey 05-2025",
                "project_id": 12
            },
            "207-Aruppukkottai": {
                "form_id": "207-Aruppukkottai Landscape Survey 05-2025",
                "project_id": 12
            },
            "208-Tiruchuli": {
                "form_id": "208-Tiruchuli Landscape Survey 05-2025",
                "project_id": 12
            }
        }
    },
    "server3": {
        "01 Bhaskar Srinivas TN Landscape Survey": {
            "166-Thiruthuraipoondi(SC)": {
                "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025",
                "project_id": 4
            },
            "168-Thiruvarur": {
                "form_id": "168-Thiruvarur Landscape Survey 04-2025",
                "project_id": 4
            },
            "167-Mannargudi": {
                "form_id": "167-Mannargudi Landscape Survey 04-2025",
                "project_id": 4
            },
            "165-Vedaranyam": {
                "form_id": "165-Vedaranyam Landscape Survey 04-2025",
                "project_id": 4
            },
            "Test TN Landscape Survey 04-2025": {
                "form_id": "Test TN Landscape Survey 04-2025",
                "project_id": 4
            },
            "200-Bodinayakanur": {
                "form_id": "200-Bodinayakanur Landscape Survey 04-2025",
                "project_id": 4
            },
            "169-Nannilam": {
                "form_id": "169-Nannilam Landscape Survey 04-2025",
                "project_id": 4
            },
            "77-Ulundurpettai": {
                "form_id": "77-Ulundurpettai Landscape Survey 04-2025",
                "project_id": 4
            }
        },
        "01 Laxmi Narayana Erode": {
            "104-Bhavani": {
                "form_id": "104-Bhavani Landscape Survey 05-2025",
                "project_id": 5
            },
            "106-Gobichettipalayam": {
                "form_id": "106-Gobichettipalayam Landscape Survey 05-2025",
                "project_id": 5
            },
            "107-Bhavanisagar": {
                "form_id": "107-Bhavanisagar Landscape Survey 05-2025",
                "project_id": 5
            },
            "98-Erode(East)": {
                "form_id": "98-Erode (East) Landscape Survey 05-2025",
                "project_id": 5
            },
            "99-Erode(West)": {
                "form_id": "99-Erode (West) Landscape Survey 05-2025",
                "project_id": 5
            }
        },
        "01 Nirmal V6": {
            "105-Anthiyur": {
                "form_id": "105-Anthiyur Landscape Survey 05-2025",
                "project_id": 9
            },
            "93-Senthamangalam(ST)": {
                "form_id": "93-Senthamangalam (ST) Landscape Survey 05-2025",
                "project_id": 9
            }
        },
        "05 Beekay V6": {
            "178-Gandharvakottai (SC)": {
                "form_id": "178-Gandharvakottai (SC) Landscape Survey 05-2025",
                "project_id": 8
            },
            "4-Thiruvallur": {
                "form_id": "4-Thiruvallur Landscape Survey 05-2025",
                "project_id": 8
            },
            "51-Uthangarai (SC)": {
                "form_id": "51-Uthangarai (SC) Landscape Survey 05-2025",
                "project_id": 8
            }
        },
        "01 Vasu Srinivas TN Landscape": {
            "117-Kavundampalayam": {
                "form_id": "117-Kavundampalayam Landscape Survey 04-2025",
                "project_id": 3
            },
            "151-Tittakudi (SC)": {
                "form_id": "151-Tittakudi (SC) Landscape Survey 04-2025",
                "project_id": 3
            },
            "176-Pattukkottai": {
                "form_id": "176-Pattukkottai Landscape Survey 04-2025",
                "project_id": 3
            },
            "52-Bargur": {
                "form_id": "52-Bargur Landscape Survey 04-2025",
                "project_id": 3
            },
            "70-Gingee": {
                "form_id": "70-Gingee Landscape Survey 04-2025",
                "project_id": 3
            },
            "71-Mailam": {
                "form_id": "71-Mailam Landscape Survey 05-2025",
                "project_id": 3
            },
            "72-Tindivanam (SC)": {
                "form_id": "72-Tindivanam (SC) Landscape Survey 05-2025",
                "project_id": 3
            },
            "75-Vikravandi": {
                "form_id": "75-Vikravandi Landscape Survey 04-2025",
                "project_id": 3
            }
        },
        "Sai Tiruppur": {
            "126-Madathukulam": {
                "form_id": "126-Madathukulam Landscape Survey 05-2025",
                "project_id": 14
            }
        },
        "Sai Madurai": {
            "188-Melur": {
                "form_id": "188-Melur Landscape Survey 05-2025",
                "project_id": 13
            },
            "190-Sholavandan (SC)": {
                "form_id": "190-Sholavandan (SC) Landscape Survey 05-2025",
                "project_id": 13
            },
            "193-Madurai Central": {
                "form_id": "193-Madurai Central Landscape Survey 05-2025",
                "project_id": 13
            }
        },
        "01 Sai Namakkal": {
            "92-Rasipuram (SC)": {
                "form_id": "92-Rasipuram (SC) Landscape Survey 05-2025",
                "project_id": 11
            },
            "94-Namakkal": {
                "form_id": "94-Namakkal Landscape Survey 05-2025",
                "project_id": 11
            },
            "96-Tiruchengodu": {
                "form_id": "96-Tiruchengodu Landscape Survey 05-2025",
                "project_id": 11
            },
            "97-Kumarapalayam": {
                "form_id": "97-Kumarapalayam Landscape Survey 05-2025",
                "project_id": 11
            }
        },
        "02 Sai Coimbatore": {
            "111-Mettuppalayam": {
                "form_id": "111-Mettuppalayam Landscape Survey 05-2025",
                "project_id": 12
            },
            "116-Sulur": {
                "form_id": "116-Sulur Landscape Survey 05-2025",
                "project_id": 12
            },
            "119-Thondamuthur": {
                "form_id": "119-Thondamuthur Landscape Survey 05-2025",
                "project_id": 12
            },
            "120-Coimbatore (South)": {
                "form_id": "120-Coimbatore (South) Landscape Survey 05-2025",
                "project_id": 12
            },
            "121-Singanallur": {
                "form_id": "121-Singanallur Landscape Survey 05-2025",
                "project_id": 12
            },
            "122-Kinathukadavu": {
                "form_id": "122-Kinathukadavu Landscape Survey 05-2025",
                "project_id": 12
            },
            "123-Pollachi": {
                "form_id": "123-Pollachi Landscape Survey 05-2025",
                "project_id": 12
            },
            "124-Valparai (SC)": {
                "form_id": "124-Valparai (SC) Landscape Survey 05-2025",
                "project_id": 12
            }
        },
        "03 Bikas V6": {
            "14-Villivakkam": {
                "form_id": "14-Villivakkam Landscape Survey 05-2025",
                "project_id": 10
            },
            "176-Pattukkottai": {
                "form_id": "176-Pattukkottai Landscape Survey 05-2025",
                "project_id": 10
            },
            "182-Alangudi": {
                "form_id": "182-Alangudi Landscape Survey 05-2025",
                "project_id": 10
            },
            "207-Aruppukkottai": {
                "form_id": "207-Aruppukkottai Landscape Survey 05-2025",
                "project_id": 10
            },
            "223-Alangulam": {
                "form_id": "223-Alangulam Landscape Survey 05-2025",
                "project_id": 10
            },
            "44-Anaikattu": {
                "form_id": "44-Anaikattu Landscape Survey 05-2025",
                "project_id": 10
            },
            "81-Gangavalli (SC)": {
                "form_id": "81-Gangavalli (SC) Landscape Survey 05-2025",
                "project_id": 10
            }
        }
    }
}

def fetch_all_submissions(server, project_id, form_id):
    """Fetch all submissions without date filtering"""
    config = ODK_CONFIG.get(server, {})
    base_url = config.get("BASE_URL", "")
    username = config.get("USERNAME", "")
    password = config.get("PASSWORD", "")

    url = f"{base_url}/v1/projects/{project_id}/forms/{urllib.parse.quote(form_id)}.svc/Submissions"
    all_data = []
    skip = 0
    batch_size = 500

    try:
        while True:
            params = {"$top": batch_size, "$skip": skip}
            response = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
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
        logger.error(f"Error fetching submissions for form {form_id}: {str(e)}")
        return []

    return all_data

def process_submissions(submissions, form_name, project_id, form_id, server_path, project_name, survey_name):
    """Process submissions with specified fields"""
    if not submissions:
        logger.warning(f"No submissions provided for form {form_name}.")
        return None

    # Debug: Log the input values
    logger.info(f"process_submissions: server_path={repr(server_path)}, project_name={repr(project_name)}, survey_name={repr(survey_name)}")

    df = pd.DataFrame(submissions)

    # Handle submission IDs
    id_col = 'instanceID' if 'instanceID' in df.columns else '__id'

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
            except Exception as e:
                logger.warning(f"Error parsing group_six JSON: {str(e)}")
                g6 = {}
        logger.info(f"group_six content: {g6}")  # Debugging line
        return str(g6.get(field, 'Field not available')).strip()

    # Required fields
    df['Name'] = df.apply(lambda r: extract_field(r, 'D1_Name'), axis=1)
    df['D7_Name'] = df.apply(lambda r: extract_field(r, 'D7_Name'), axis=1)  # Add D7_Name field
    df['Submitted By'] = df.apply(lambda r: extract_field(r, 'submittedBy'), axis=1)
    df['Phone Number'] = df.apply(lambda r: extract_field(r, 'D8_PhoneNumber'), axis=1)

    # New column to indicate if Phone Number is present
    df['Phone Number Present'] = df['Phone Number'].apply(lambda x: "✅" if x and x.strip() else "❌")

    # Audio files
    df['Audio File'] = df.get('bg_audio', 'Unknown')
    df['Audio Present'] = df['Audio File'].apply(lambda x: "✅" if x and x != "Unknown" else "❌")

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

    # Required columns
    required_columns = [
        'Form Name', 'Date', 'Audio File', 'Audio Present', 'Location Present',
        'Submitted By', 'Name', 'D7_Name', 'Phone Number', 'Phone Number Present', 'instanceID'
    ]

    # Ensure all columns exist
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    return df[required_columns]

def sanitize_sheet_name(name):
    """Sanitize form name to be a valid Excel sheet name"""
    # Remove invalid characters and replace with underscore
    invalid_chars = r'[\\\/:*?\[\]]'
    sanitized = re.sub(invalid_chars, '_', name)
    # Truncate to 31 characters (Excel limit)
    sanitized = sanitized[:31]
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # If empty after sanitization, use a default name
    return sanitized if sanitized else "Sheet"

def main():
    st.set_page_config(page_title="ODK Data Processor", layout="wide")
    st.title("📊 ODK Form Data Processor")

    # Initialize session state for selections
    if 'server_path' not in st.session_state:
        st.session_state.server_path = list(SURVEYS.keys())[0]
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None

    # Sidebar controls
    st.sidebar.header("Filters")

    # Server selection
    server_path = st.sidebar.selectbox("Server", list(SURVEYS.keys()), index=0, key="server_path_select")

    # Reset project if server changes
    if server_path != st.session_state.server_path:
        st.session_state.server_path = server_path
        st.session_state.selected_project = None

    # Project selection
    if server_path in SURVEYS:
        project_options = list(SURVEYS[server_path].keys())
        if not st.session_state.selected_project or st.session_state.selected_project not in project_options:
            st.session_state.selected_project = project_options[0]
        selected_project = st.sidebar.selectbox("Project", project_options, index=project_options.index(st.session_state.selected_project), key="project_select")
    else:
        st.error("Invalid server selected.")
        return

    # Normalize selections to avoid whitespace issues
    server_path = server_path.strip()
    selected_project = selected_project.strip()

    # Debug: Log selected values
    st.write(f"Selected Values: server_path={repr(server_path)}, project={repr(selected_project)}")

    # Initialize session state for data
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'form_dfs' not in st.session_state:
        st.session_state.form_dfs = {}

    # Main content
    if st.button("Load All Forms in Project"):
        with st.spinner(f"Fetching all submissions for project {selected_project}..."):
            all_dfs = []
            form_dfs = {}
            form_options = list(SURVEYS[server_path][selected_project].keys())

            for form_name in form_options:
                form_info = SURVEYS[server_path][selected_project][form_name]
                submissions = fetch_all_submissions(
                    server_path,
                    form_info['project_id'],
                    form_info['form_id']
                )

                if submissions:
                    df = process_submissions(
                        submissions,
                        form_name,
                        form_info['project_id'],
                        form_info['form_id'],
                        server_path,
                        selected_project,
                        form_name
                    )
                    if df is not None:
                        all_dfs.append(df)
                        form_dfs[form_name] = df
                    else:
                        st.warning(f"No submissions found for form {form_name}")
                else:
                    st.error(f"Failed to fetch submissions for form {form_name}")

            if all_dfs:
                combined_df = pd.concat(all_dfs, ignore_index=True)
                st.session_state.df = combined_df
                st.session_state.form_dfs = form_dfs
                st.success(f"Loaded {len(combined_df)} submissions from {len(all_dfs)} forms")
            else:
                st.warning("No submissions found for any forms in this project")

    # Display data
    if st.session_state.df is not None:
        st.subheader("All Submission Data")
        st.dataframe(st.session_state.df)

        # Export
        st.subheader("Data Export")

        # Create two columns for download buttons
        col1, col2 = st.columns(2)

        with col1:
            # CSV Download (combined)
            csv = st.session_state.df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Full CSV",
                csv,
                f"{selected_project}_all_forms_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key='csv-download'
            )

        with col2:
            # Excel Download (separate sheets per form)
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                for form_name, df in st.session_state.form_dfs.items():
                    sanitized_name = sanitize_sheet_name(form_name)
                    df.to_excel(writer, index=False, sheet_name=sanitized_name)
                writer.close()

                st.download_button(
                    "📥 Download Full Excel (XLSX)",
                    excel_buffer.getvalue(),
                    f"{selected_project}_all_forms_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key='excel-download'
                )

if __name__ == "__main__":
    main()
