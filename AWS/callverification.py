import streamlit as st
import pandas as pd
import requests
import io 

# --- Constants ---
GOOGLE_MAPS_API_KEY = "AIzaSyAhkHfX8mWlUOVI1-d74JjSUVsLp-sk_XA"
COLUMN_NAME = "Location and name of building in which Polling Station located"

# Simplified SURVEYS dictionary
SURVEYS = {
    "server1": {
        "Gopal Ranipet Vellore APP": {
            "41-Ranipet": {
                "excel_file": "server1/Gopal Ranipet Vellore APP/41. Ranipet.xlsx",
                "main_location": "Ranipet"
            },
            "42-Arcot": {
                "excel_file": "server1/Gopal Ranipet Vellore APP/42. Arcot.xlsx",
                "main_location": "Arcot"
            },
            "43-Vellore": {
                "excel_file": "server1/Gopal Ranipet Vellore APP/43. Vellore.xlsx",
                "main_location": "Vellore"
            },
            "44-Anaikattu": {
                "excel_file": "server1/Gopal Ranipet Vellore APP/44. Anaikattu.xlsx",
                "main_location": "Anaikattu"
            }
        },
        "04 TN AC Landscape": {
            "151-Tittakudi (SC)": {
                "excel_file": "server1/04 TN AC Landscape/151. Tittakudi.xlsx",
                "main_location": "Tittakudi (SC)"
            },
            "37-Kancheepuram": {
                "excel_file": "server1/04 TN AC Landscape/37._KANCHEEPURAM.xlsx",
                "main_location": "Kancheepuram"
            },
            "181-Thirumayam": {
                "excel_file": "server1/04 TN AC Landscape/181-Thirumayam.xlsx",
                "main_location": "Thirumayam"
            },
            "204-Sattur": {
                "excel_file": "server1/04 TN AC Landscape/204. Sattur.xlsx",
                "main_location": "Sattur"
            },
            "159-Kattumannarkoil (SC)": {
                "excel_file": "server1/04 TN AC Landscape/159. Kattumannarkoil (SC).xlsx",
                "main_location": "Kattumannarkoil (SC)"
            },
            "156-Kurinjipadi": {
                "excel_file": "server1/04 TN AC Landscape/156. Kurinjiapdi.xlsx",
                "main_location": "Kurinjipadi"
            },
            "183-Aranthangi": {
                "excel_file": "server1/04 TN AC Landscape/183-Aranthangi.xlsx",
                "main_location": "Aranthangi"
            }
        },
        "Krishnagiri APP": {
            "52-Bargur": {
                "excel_file": "server1/Krishnagiri APP/52. Bargur.xlsx",
                "main_location": "Bargur"
            },
            "53-Krishnagiri": {
                "excel_file": "server1/Krishnagiri APP/53. Krishnagiri.xlsx",
                "main_location": "Krishnagiri"
            }
        },
        "Virudhunagar APP": {
            "208-Tiruchuli": {
                "excel_file": "server1/Virudhunagar APP/208. Tiruchuli.xlsx",
                "main_location": "Tiruchuli"
            },
            "206-Virudhunagar": {
                "excel_file": "server1/Virudhunagar APP/206. Virudhunagar.xlsx",
                "main_location": "Virudhunagar"
            },
            "202-Rajapalayam": {
                "excel_file": "server1/Virudhunagar APP/202.Rajapalayam.xlsx",
                "main_location": "Rajapalayam"
            },
            "203-Srivilliputhur (SC)": {
                "excel_file": "server1/Virudhunagar APP/203.Srivlliputhur.xlsx",
                "main_location": "Srivlliputhur"
            },
            "205-Sivakasi": {
                "excel_file": "server1/Virudhunagar APP/205-Sivakasi.xlsx",
                "main_location": "Sivakasi"
            }
        },
        "Thoothukudi APP": {
            "215-Tiruchendur": {
                "excel_file": "server1/Thoothukudi APP/215. Tiruchendur.xlsx",
                "main_location": "Tiruchendur"
            },
            "214-Thoothukkudi": {
                "excel_file": "server1/Thoothukudi APP/214. Thoothukkudi.xlsx",
                "main_location": "Thoothukkudi"
            },
            "216-Srivaikuntam": {
                "excel_file": "server1/Thoothukudi APP/216. Srivaikundam.xlsx",
                "main_location": "Srivaikundam"
            },
            "218-Kovilpatti": {
                "excel_file": "server1/Thoothukudi APP/218. Kovilpatti.xlsx",
                "main_location": "Kovilpatti"
            },
            "213-Vilathikulam": {
                "excel_file": "server1/Thoothukudi APP/213-Vilathikulam.xlsx",
                "main_location": "Vilathikulam"
            },
            "217-Ottapidaram (SC)": {
                "excel_file": "server1/Thoothukudi APP/217 - Ottapidaram (SC).xlsx",
                "main_location": "Ottapidaram (SC)"
            }
        },
        "03 BK TN AC Landscape": {
            "197-Usilampatti": {
                "excel_file": "server1/03 BK TN AC Landscape/197 Usilampatti.xlsx",
                "main_location": "Usilampatti"
            },
            "153-Neyveli": {
                "excel_file": "server1/03 BK TN AC Landscape/153. NEYYELI.xlsx",
                "main_location": "Neyveli"
            },
            "100-Modakkurichi": {
                "excel_file": "server1/03 BK TN AC Landscape/100-Modakkurichi .xlsx",
                "main_location": "Modakkurichi"
            },
            "95-Paramathi-Velur": {
                "excel_file": "server1/03 BK TN AC Landscape/95 Paramathi.xlsx",
                "main_location": "Paramathi-Velur"
            },
            "63-Tiruvannamalai": {
                "excel_file": "server1/03 BK TN AC Landscape/63 Tiruvannamalai.xlsx",
                "main_location": "Tiruvannamalai"
            },
            "62-Chengam (SC)": {
                "excel_file": "server1/03 BK TN AC Landscape/62. Chengam.xlsx",
                "main_location": "Chengam"
            },
            "33-Thiruporur": {
                "excel_file": "server1/03 BK TN AC Landscape/33. THIRUPORUR.xlsx",
                "main_location": "Thiruporur"
            },
            "34-Cheyyur (SC)": {
                "excel_file": "server1/03 BK TN AC Landscape/34. CHEYYUR.xlsx",
                "main_location": "Cheyyur (SC)"
            },
            "55-Hosur": {
                "excel_file": "server1/03 BK TN AC Landscape/55 Hosur.xlsx",
                "main_location": "Hosur"
            }
        },
        "Shashi Sivaganga APP": {
            "184-Karaikudi": {
                "excel_file": "server1/Sai Sivaganga APP/184. Karaikudi.xlsx",
                "main_location": "Karaikudi"
            },
            "185-Tiruppattur": {
                "excel_file": "server1/Sai Sivaganga APP/185. Tiruppattur.xlsx",
                "main_location": "Tiruppattur"
            },
            "186-Sivaganga": {
                "excel_file": "server1/Sai Sivaganga APP/186. Sivaganga.xlsx",
                "main_location": "Sivaganga"
            },
            "187-Manamadurai (SC)": {
                "excel_file": "server1/Sai Sivaganga APP/187. Manamadurai.xlsx",
                "main_location": "Manamadurai (SC)"
            }
        },
        "Tanjavore APP": {
            "176-Pattukkottai": {
                "excel_file": "server1/Tanjavore APP/176. Pattukkottai.xlsx",
                "main_location": "Pattukkottai"
            }
        },
        "BK TN AC Landscape": {
            "146-Thuraiyur (SC)": {
                "excel_file": "server1/BK TN AC Landscape/146 THURAIYUR.xlsx",
                "main_location": "Thuraiyur (SC)"
            },
            "103-Perundurai": {
                "excel_file": "server1/BK TN AC Landscape/103. PERUNDURAI.xlsx",
                "main_location": "Perundurai"
            },
            "132-Dindigul": {
                "excel_file": "server1/BK TN AC Landscape/132. Dindigul.xlsx",
                "main_location": "Dindigul"
            },
            "135-Karur": {
                "excel_file": "server1/BK TN AC Landscape/135. KARUR.xlsx",
                "main_location": "Karur"
            },
            "155-Cuddalore": {
                "excel_file": "server1/BK TN AC Landscape/155. CUDDALORE.xlsx",
                "main_location": "Cuddalore"
            },
            "189-Madurai East": {
                "excel_file": "server1/BK TN AC Landscape/189. MADURAI EAST.xlsx",
                "main_location": "Madurai East"
            },
            "171-Kumbakonam": {
                "excel_file": "server1/BK TN AC Landscape/171. KUMBAKONAM.xlsx",
                "main_location": "Kumbakonam"
            },
            "150-Jayankondam": {
                "excel_file": "server1/BK TN AC Landscape/150. Jayankondam.xlsx",
                "main_location": "Jayankondam"
            },
            "109-Gudalur (SC)": {
                "excel_file": "server1/BK TN AC Landscape/109 Gudalur.xlsx",
                "main_location": "Gudalur"
            },
            "12-Perambur": {
                "excel_file": "server1/BK TN AC Landscape/12. PERAMBUR.xlsx",
                "main_location": "PERAMBUR"
            },
            "136-Krishnarayapuram (SC)": {
                "excel_file": "server1/BK TN AC Landscape/136. KRISHNARAYAPURAM.xlsx",
                "main_location": "KRISHNARAYAPURAM"
            },
            "137-Kulithalai": {
                "excel_file": "server1/BK TN AC Landscape/137. kulithalai.xlsx",
                "main_location": "kulithalai"
            },
            "145-Musiri": {
                "excel_file": "server1/BK TN AC Landscape/145. MUSIRI.xlsx",
                "main_location": "MUSIRI"
            },
            "158-Chidambaram": {
                "excel_file": "server1/BK TN AC Landscape/158. Chidambaram.xlsx",
                "main_location": "Chidambaram"
            },
            "180-Pudukkottai": {
                "excel_file": "server1/BK TN AC Landscape/180. Pudukuttai.xlsx",
                "main_location": "Pudukuttai"
            },
            "198-Andipatti": {
                "excel_file": "server1/BK TN AC Landscape/198. ANDIPATTI.xlsx",
                "main_location": "ANDIPATTI"
            },
            "199. Periyakulam (SC)": {
                "excel_file": "server1/BK TN AC Landscape/199. PERIYAKULAM.xlsx",
                "main_location": "PERIYAKULAM"
            },
            "3-Thirutthani": {
                "excel_file": "server1/BK TN AC Landscape/3. TIRUTTANI.xlsx",
                "main_location": "TIRUTTANI"
            },
            "38-Arakkonam (SC)": {
                "excel_file": "server1/BK TN AC Landscape/38. ARAKKONAM.xlsx",
                "main_location": "Arakkonam (SC)"
            },
            "39-Sholingur": {
                "excel_file": "server1/BK TN AC Landscape/39. SHOLINGHUR.xlsx",
                "main_location": "Sholingur"
            },
            "56-Thalli": {
                "excel_file": "server1/BK TN AC Landscape/56. THALLI.xlsx",
                "main_location": "Thalli"
            },
            "66-Polur": {
                "excel_file": "server1/BK TN AC Landscape/66. POLUR.xlsx",
                "main_location": "Polur"
            },
            "201-Cumbum": {
                "excel_file": "server1/BK TN AC Landscape/201 Cumbum .xlsx",
                "main_location": "Cumbum"
            }
        },
        "Bikas Tenkasi APP": {
            "220-Vasudevanallur (SC)": {
                "excel_file": "server1/Bikas Tenkasi APP/220 - Vasudevanallur(SC).xlsx",
                "main_location": "Vasudevanallur (SC)"
            },
            "221-Kadayanallur": {
                "excel_file": "server1/Bikas Tenkasi APP/221. Kadayanallur.xlsx",
                "main_location": "Kadayanallur"
            },
            "222-Tenkasi": {
                "excel_file": "server1/Bikas Tenkasi APP/222.Thenkasi.xlsx",
                "main_location": "Tenkasi"
            },
            "223-Alangulam": {
                "excel_file": "server1/Bikas Tenkasi APP/223 - Alangulam.xlsx",
                "main_location": "Alangulam"
            }
        },
        "Bikas Tirunelveli APP": {
            "225-Ambasamudram": {
                "excel_file": "server1/Bikas Tirunelveli APP/225. Ambasamudram.xlsx",
                "main_location": "Ambasamudram"
            },
            "227-Nanguneri": {
                "excel_file": "server1/Bikas Tirunelveli APP/227. Nanguneri.xlsx",
                "main_location": "Nanguneri"
            },
            "228-Radhapuram": {
                "excel_file": "server1/Bikas Tirunelveli APP/228. Radhapuram.xlsx",
                "main_location": "Radhapuram"
            }
        },
        "Gopal Misc APP": {
            "148-Kunnam": {
                "excel_file": "server1/Gopal Misc APP/148. KUNNAM.xlsx",
                "main_location": "Kunnam"
            },
            "125-Udumalpet": {
                "excel_file": "server1/Gopal Misc APP/125. UDUMALAIPETTAI.xlsx",
                "main_location": "Udumalpet"
            },
            "5-Poonamallee (SC)": {
                "excel_file": "server1/Gopal Misc APP/5. POONAMALLEE (SC).xlsx",
                "main_location": "Poonamallee (SC)"
            },
            "91-Veerapandi": {
                "excel_file": "server1/Gopal Misc APP/91.Veerapandi.xlsx",
                "main_location": "Veerapandi"
            },
            "92-Rasipuram (SC)": {
                "excel_file": "server1/Gopal Misc APP/92. Rasipuram.xlsx",
                "main_location": "Rasipuram (SC)"
            },
            "60-Pappireddippatti": {
                "excel_file": "server1/Gopal Misc APP/60. Pappireddipatti.xlsx",
                "main_location": "Pappireddipatti"
            }
        },
        "Mahesh Misc APP": {
            "152-Vriddhachalam": {
                "excel_file": "server1/Mahesh Misc APP/152. Vriddhachalam.xlsx",
                "main_location": "Vriddhachalam"
            },
            "186-Sivaganga": {
                "excel_file": "server1/Mahesh Misc APP/186. Sivaganga.xlsx",
                "main_location": "Sivaganga"
            },
            "207-Aruppukkottai": {
                "excel_file": "server1/Mahesh Misc APP/207. Aruppukkottai.xlsx",
                "main_location": "Aruppukkottai"
            },
            "212-Mudhukulathur": {
                "excel_file": "server1/Mahesh Misc APP/212. Mudhukulathur.xlsx",
                "main_location": "Mudhukulathur"
            },
            "224-Tirunelveli": {
                "excel_file": "server1/Mahesh Misc APP/224 Tirunelveli.xlsx",
                "main_location": "Tirunelveli"
            },
            "61-Harur (SC)": {
                "excel_file": "server1/Mahesh Misc APP/61. HARUR.xlsx",
                "main_location": "HARUR"
            },
            "85-Mettur": {
                "excel_file": "server1/Mahesh Misc APP/85.Mettur.xlsx",
                "main_location": "Mettur"
            }
        },
        "Murugan Misc APP": {
            "103-Perundurai": {
                "excel_file": "server1/Murugan Misc APP/103. PERUNDURAI.xlsx",
                "main_location": "Perundurai"
            },
            "155-Cuddalore": {
                "excel_file": "server1/Murugan Misc APP/155. Cuddalore.xlsx",
                "main_location": "Cuddalore"
            },
            "8-Ambattur": {
                "excel_file": "server1/Murugan Misc APP/8-Ambattur.xlsx",
                "main_location": "Ambattur"
            }
        },
        "Moon MISC 01": {
            "5-Poonamallee (SC)": {
                "excel_file": "server1/Moon MISC 01/5. POONAMALLEE (SC).xlsx",
                "main_location": "Poonamallee (SC)"
            },
            "42-Arcot": {
                "excel_file": "server1/Moon MISC 01/42. Arcot.xlsx",
                "main_location": "Arcot"
            },
            "92-Rasipuram (SC)": {
                "excel_file": "server1/Moon MISC 01/92. Rasipuram.xlsx",
                "main_location": "Rasipuram (SC)"
            },
            "125-Udumalpet": {
                "excel_file": "server1/Moon MISC 01/125. UDUMALAIPETTAI.xlsx",
                "main_location": "Udumalpet"
            }
        },
        "Shashi Misc": {
            "7-Maduravoyal": {
                "excel_file": "server1/Shashi Misc/7. MADURAVOYAL.xlsx",
                "main_location": "Maduravoyal"
            },
            "10-Thiruvottiyur": {
                "excel_file": "server1/Shashi Misc/10. THIRUVOTTIYUR.xlsx",
                "main_location": "Thiruvottiyur"
            },
            "13-Kolathur": {
                "excel_file": "server1/Shashi Misc/13. Kolathur.xlsx",
                "main_location": "Kolathur"
            },
            "15-Thiru-Vi-Ka-Nagar (SC)": {
                "excel_file": "server1/Shashi Misc/15 Thiru Vi Ka Nagar.xlsx",
                "main_location": "Thiru-Vi-Ka-Nagar (SC)"
            },
            "16-Egmore (SC)": {
                "excel_file": "server1/Shashi Misc/16. EGMORE.xlsx",
                "main_location": "Egmore (SC)"
            },
            "17-Royapuram": {
                "excel_file": "server1/Shashi Misc/17. Royapuram.xlsx",
                "main_location": "Royapuram"
            },
            "31-Tambaram": {
                "excel_file": "server1/Shashi Misc/31. Tambaram.xlsx",
                "main_location": "Tambaram"
            },
            "97-Kumarapalayam": {
                "excel_file": "server1/Shashi Misc/97. Kumarapalayam.xlsx",
                "main_location": "Kumarapalayam"
            },
            "98-Erode (East)": {
                "excel_file": "server1/Shashi Misc/98. Erode (East).xlsx",
                "main_location": "Erode (East)"
            },
            "149-Ariyalur": {
                "excel_file": "server1/Shashi Misc/149. Ariyalur.xlsx",
                "main_location": "Ariyalur"
            },
            "172-Papanasam": {
                "excel_file": "server1/Shashi Misc/172-Papanasam.xlsx",
                "main_location": "Papanasam"
            }
        },
        "Mahesh Ramanathapuram APP": {
            "211-Ramanathapuram": {
                "excel_file": "server1/Ramanathapuram APP/211. Ramanathapuram.xlsx",
                "main_location": "Ramanathapuram"
            },
            "212-Mudhukulathur": {
                "excel_file": "server1/Ramanathapuram APP/212. Mudhukulathur.xlsx",
                "main_location": "Mudhukulathur"
            },
            "210-Tiruvadanai": {
                "excel_file": "server1/Ramanathapuram APP/210. Thiruvadanai.xlsx",
                "main_location": "Thiruvadanai"
            }
        },
        "LN Kancheepuram": {
            "28-Alandur": {
                "excel_file": "server1/LN Kancheepuram/28. Alandur.xlsx",
                "main_location": "Alandur"
            },
            "29-Sriperumbudur (SC)": {
                "excel_file": "server1/LN Kancheepuram/29. SRIPERUMBUDUR.xlsx",
                "main_location": "Sriperumbudur (SC)"
            },
            "36-Uthiramerur": {
                "excel_file": "server1/LN Kancheepuram/36. UTHIRAMERUR 1.xlsx",
                "main_location": "Uthiramerur"
            },
            "37-Kancheepuram": {
                "excel_file": "server1/LN Kancheepuram/37. KANCHEEPURAM.xlsx",
                "main_location": "Kancheepuram"
            }
        }
    },
    "server2": {
        "01 Bikas TN Landscape Survey": {
            "128-Oddanchatram": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/128. Oddanchatram.xlsx",
                "main_location": "Oddanchatram"
            },
            "127-Palani": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/127. PALANI.xlsx",
                "main_location": "Palani"
            },
            "129-Athoor": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/129. Athoor.xlsx",
                "main_location": "Athoor"
            },
            "44-Anaikattu": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/44. ANAIKATTU.xlsx",
                "main_location": "ANAIKATTU"
            },
            "130-Nilakkottai (SC)": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/130. Nilakkottai.xlsx",
                "main_location": "Nilakkottai"
            },
            "143-Lalgudi": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/143. Lalgudi.xlsx",
                "main_location": "Lalgudi"
            },
            "45-Kilvaithinankuppam (SC)": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/45. Kilvaithinankuppam (SC).xlsx",
                "main_location": "Kilvaithinankuppam"
            },
            "47-Vaniyambadi": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/47. VANIYAMBADI.xlsx",
                "main_location": "Vaniyambadi"
            },
            "69-Vandavasi (SC)": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/69. VANDAVASI.xlsx",
                "main_location": "Vandavasi"
            },
            "81-Gangavalli (SC)": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/81.GANGAVALLI.xlsx",
                "main_location": "Gangavalli"
            },
            "49-Jolarpet": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/49 Jolarpet.xlsx",
                "main_location": "Jolarpet"
            },
            "147-Perambalur (SC)": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/147. Perambalur.xlsx",
                "main_location": "Perambalur"
            },
            "14-Villivakkam": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/14 VILLIVAKKAM.xlsx",
                "main_location": "Villivakkam"
            },
            "150-Jayankondam": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/150. Jayankondam.xlsx",
                "main_location": "Jayankondam"
            },
            "159-Kattumannarkoil (SC)": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/159. Kattumannarkoil.xlsx",
                "main_location": "Kattumannarkoil"
            },
            "173-Thiruvaiyaru": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/173. THIRUVAIYARU.xlsx",
                "main_location": "Thiruvaiyaru"
            },
            "179-Viralimalai": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/179. Viralimalai.xlsx",
                "main_location": "Viralimalai"
            },
            "223-Alangulam": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/223-Alangulam.xlsx",
                "main_location": "Alangulam"
            },
            "24-Thiyagarayanagar": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/24 THIYAGARAYANAGAR.xlsx",
                "main_location": "Thiyagarayanagar"
            },
            "46-Gudiyattam (SC)": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/46-GUDIYATTAM .xlsx",
                "main_location": "Gudiyattam"
            },
            "48-Ambur": {
                "excel_file": "server2/01 Bikas TN Landscape Survey/48-Ambur.xlsx",
                "main_location": "Ambur"
            }
        },
        "01 FMRS TN Landscape Survey": {
            "8-Ambattur": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/8-Ambattur.xlsx",
                "main_location": "Ambattur"
            },
            "65-Kalasapakkam": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/65-Kalasapakkam.xlsx",
                "main_location": "Kalasapakkam"
            },
            "139-Srirangam": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/139-Srirangam.xlsx",
                "main_location": "Srirangam"
            },
            "141-Tiruchirappalli (East)": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/141. TIRUCHIRAPPALLI(EAST).xlsx",
                "main_location": "Tiruchirappalli (East)"
            },
            "163-Nagapattinam": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/163-Nagapattinam.xlsx",
                "main_location": "Nagapattinam"
            },
            "172-Papanasam": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/172-Papanasam.xlsx",
                "main_location": "Papanasam"
            },
            "174-Thanjavur": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/174-Thanjavur.xlsx",
                "main_location": "Thanjavur"
            },
            "177-Peravurani": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/177-Peravurani.xlsx",
                "main_location": "Peravurani"
            },
            "209-Paramakudi (SC)": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/209-Paramakudi.xlsx",
                "main_location": "Paramakudi"
            },
            "213-Vilathikulam": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/213-Vilathikulam.xlsx",
                "main_location": "Vilathikulam"
            },
            "217-Ottapidaram (SC)": {
                "excel_file": "server2/01 FMRS TN Landscape Survey/217 - Ottapidaram .xlsx",
                "main_location": "Ottapidaram"
            }
        },
        "01 Shashi TN Landscape Survey": {
            "88-Salem (West)": {
                "excel_file": "server2/01 Shashi TN Landscape Survey/88.Salem West.xlsx",
                "main_location": "Salem West"
            },
            "89-Salem (North)": {
                "excel_file": "server2/01 Shashi TN Landscape Survey/89.Salem North.xlsx",
                "main_location": "Salem North"
            },
            "90-Salem (South)": {
                "excel_file": "server2/01 Shashi TN Landscape Survey/90.Salem South.xlsx",
                "main_location": "Salem South"
            }
        },
        "02 Bikas TN Landscape Survey": {
            "64-Kilpennathur": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/64 Kilpennathur .xlsx",
                "main_location": "Kilpennathur"
            },
            "155-Cuddalore": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/155. CUDDALORE.xlsx",
                "main_location": "Cuddalore"
            },
            "12-Perambur": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/12. PERAMBUR.xlsx",
                "main_location": "Perambur"
            },
            "131-Natham": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/131 Natham.xlsx",
                "main_location": "Natham"
            },
            "132-Dindigul": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/132. Dindigul.xlsx",
                "main_location": "Dindigul"
            },
            "134-Aravakurichi": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/134-ARAVAKURICHI.xlsx",
                "main_location": "Aravakurichi"
            },
            "135-Karur": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/135. KARUR.xlsx",
                "main_location": "Karur"
            },
            "157-Bhuvanagiri": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/157-BHUVANAGIRI.xlsx",
                "main_location": "Bhuvanagiri"
            },
            "171-Kumbakonam": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/171. KUMBAKONAM.xlsx",
                "main_location": "Kumbakonam"
            },
            "63-Tiruvannamalai": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/63 Tiruvannamalai.xlsx",
                "main_location": "Tiruvannamalai"
            },
            "62-Chengam (SC)": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/62. Chengam.xlsx",
                "main_location": "Chengam"
            },
            "66-Polur": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/66. POLUR.xlsx",
                "main_location": "Polur"
            },
            "67-Arani": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/67 Arani.xlsx",
                "main_location": "Arani"
            }
        },
        "02 FMRS TN Landscape": {
            "191-Madurai North": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/191. Madurai North.xlsx",
                "main_location": "Madurai North"
            },
            "192-Madurai South": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/192. Madurai South.xlsx",
                "main_location": "Madurai South"
            },
            "194-Madurai West": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/194. Madurai West.xlsx",
                "main_location": "Madurai West"
            },
            "196-Thirumangalam": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/196 - Thirumangalam.xlsx",
                "main_location": "Thirumangalam"
            },
            "188-Melur": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/188. Melur.xlsx",
                "main_location": "Melur"
            },
            "190-Sholavandan (SC)": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/190 Sholavandana.xlsx",
                "main_location": "Sholavandan"
            },
            "193-Madurai Central": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/193. Madurai Central.xlsx",
                "main_location": "Madurai Central"
            },
            "195-Thiruparankundram": {
                "excel_file": "server2/02 FMRS TN Landscape Survey/195. Thirupparamkundram.xlsx",
                "main_location": "Thiruparankundram"
            }
        },
        "02 Shashi TN Landscape": {
            "25-Mylapore": {
                "excel_file": "server2/02 Shashi TN Landscape/25. Mylapore.xlsx",
                "main_location": "Mylapore"
            }
        },
        "01 Shankar Subramaniam TN Landscape Survey": {
            "108-Udhagamandalam": {
                "excel_file": "server2/01 Shankar Subramaniam TN Landscape Survey/108-Udhagamandalam.xlsx",
                "main_location": "Udhagamandalam"
            },
            "142-Thiruverumbur": {
                "excel_file": "server2/01 Shankar Subramaniam TN Landscape Survey/142.Thiruverumbur.xlsx",
                "main_location": "Thiruverumbur"
            },
            "144-Manachanallur": {
                "excel_file": "server2/01 Shankar Subramaniam TN Landscape Survey/144. MANACHANALLUR.xlsx",
                "main_location": "Manachanallur"
            },
            "219-Sankarankovil (SC)": {
                "excel_file": "server2/01 Shankar Subramaniam TN Landscape Survey/219-Sankarankovil.xlsx",
                "main_location": "Sankarankovil"
            },
            "54-Veppanahalli": {
                "excel_file": "server2/01 Shankar Subramaniam TN Landscape Survey/54-Veppanahalli.xlsx",
                "main_location": "Veppanahalli"
            },
            "175-Orathanadu": {
                "excel_file": "server2/01 Shankar Subramaniam TN Landscape Survey/175. Orathanadu.xlsx",
                "main_location": "Orathanadu"
            }
        },
        "03 Bikas V6": {
            "40-Katpadi": {
                "excel_file": "server2/03 Bikas V6/40. Katpadi.xlsx",
                "main_location": "Katpadi"
            },
            "41-Ranipet": {
                "excel_file": "server2/03 Bikas V6/41. Ranipet.xlsx",
                "main_location": "Ranipet"
            },
            "42-Arcot": {
                "excel_file": "server2/03 Bikas V6/42. Arcot.xlsx",
                "main_location": "Arcot"
            },
            "50-Tirupattur": {
                "excel_file": "server2/03 Bikas V6/50. TIRUPATTUR.xlsx",
                "main_location": "Tirupattur"
            },
            "63-Tiruvannamalai": {
                "excel_file": "server2/03 Bikas V6/63. TIRUVANNAMALAI.xlsx",
                "main_location": "Tiruvannamalai"
            },
            "154-Panruti": {
                "excel_file": "server2/03 Bikas V6/154. Panruti.xlsx",
                "main_location": "Panruti"
            },
            "207-Aruppukkottai": {
                "excel_file": "server2/03 Bikas V6/207. Aruppukkottai.xlsx",
                "main_location": "Aruppukkottai"
            },
            "182-Alangudi": {
                "excel_file": "server2/03 Bikas V6/182. Alangudi.xlsx",
                "main_location": "Alangudi"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server2/03 Bikas V6/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "86-Edappadi": {
                "excel_file": "server2/03 Bikas V6/86.Edappadi.xlsx",
                "main_location": "Edappadi"
            }
        },
        "Nanda TN Landscape": {
            "162-Poompuhar": {
                "excel_file": "server2/Nanda TN/162._Poompuhar.xlsx",
                "main_location": "Poompuhar"
            },
            "164-Kilvelur (SC)": {
                "excel_file": "server2/Nanda TN/164_Kilevelur.xlsx",
                "main_location": "Kilvelur (SC)"
            },
            "170-Thiruvidaimarudur (SC)": {
                "excel_file": "server2/Nanda TN/170 Thiruvidaimarudur.xlsx",
                "main_location": "Thiruvidaimarudur (SC)"
            },
            "229-Kanniyakumari": {
                "excel_file": "server2/Nanda TN/229. Kanniyakumari.xlsx",
                "main_location": "Kanniyakumari"
            },
            "230-Nagercoil": {
                "excel_file": "server2/Nanda TN/230. Nagercoil.xlsx",
                "main_location": "Nagercoil"
            },
            "154-Panruti": {
                "excel_file": "server2/03 Bikas V6/154. Panruti.xlsx",
                "main_location": "Panruti"
            },
            "155-Cuddalore": {
                "excel_file": "server2/02 Bikas TN Landscape Survey/155. CUDDALORE.xlsx",
                "main_location": "Cuddalore"
            }
        },
        "Shankar Tenkasi": {
            "220-Vasudevanallur (SC)": {
                "excel_file": "server2/Shankar Tenkasi/220 - Vasudevanallur(SC).xlsx",
                "main_location": "Vasudevanallur"
            },
            "219-Sankarankovil (SC)": {
                "excel_file": "server2/Shankar Tenkasi/219. Sankarankovil (SC).xlsx",
                "main_location": "Sankarankovil"
            },
            "221-Kadayanallur": {
                "excel_file": "server2/Shankar Tenkasi/221. Kadayanallur.xlsx",
                "main_location": "Kadayanallur"
            },
            "222-Tenkasi": {
                "excel_file": "server2/Shankar Tenkasi/222.Thenkasi.xlsx",
                "main_location": "Tenkasi"
            },
            "223-Alangulam": {
                "excel_file": "server2/Shankar Tenkasi/223 - Alangulam.xlsx",
                "main_location": "Alangulam"
            }
        },
        "Nanda Kanniyakumari APP": {
            "229-Kanniyakumari": {
                "excel_file": "server2/Nanda Kanniyakumari/229. Kanniyakumari.xlsx",
                "main_location": "Kanniyakumari"
            },
            "230-Nagercoil": {
                "excel_file": "server2/Nanda Kanniyakumari/230. Nagercoil.xlsx",
                "main_location": "Nagercoil"
            },
            "231-Colachal": {
                "excel_file": "server2/Nanda Kanniyakumari/231. Colachal.xlsx",
                "main_location": "Colachal"
            },
            "232-Padmanabhapuram": {
                "excel_file": "server2/Nanda Kanniyakumari/232. Padmanabhapuram.xlsx",
                "main_location": "Padmanabhapuram"
            },
            "233-Vilavancode": {
                "excel_file": "server2/Nanda Kanniyakumari/233. Vilavancode.xlsx",
                "main_location": "Vilavancode"
            },
            "234-Killiyoor": {
                "excel_file": "server2/Nanda Kanniyakumari/234. Killiyoor.xlsx",
                "main_location": "Killiyoor"
            }
        },
        "LN Tirunelveli": {
            "225-Ambasamudram": {
                "excel_file": "server2/LN Tirunelveli/225. Ambasamudram.xlsx",
                "main_location": "Ambasamudram"
            },
            "226-Palayamkottai": {
                "excel_file": "server2/LN Tirunelveli/226. Palayamkottai.xlsx",
                "main_location": "Palayamkottai"
            },
            "227-Nanguneri": {
                "excel_file": "server2/LN Tirunelveli/227. Nanguneri.xlsx",
                "main_location": "Nanguneri"
            },
            "228-Radhapuram": {
                "excel_file": "server2/LN Tirunelveli/228. Radhapuram.xlsx",
                "main_location": "Radhapuram"
            }
        },
        "Sai Thiruvallur": {
            "1-Gummidipoondi": {
                "excel_file": "server2/Sai Thiruvallur/1. GUMMIDIPOONDI.xlsx",
                "main_location": "Gummidipoondi"
            },
            "2-Ponneri (SC)": {
                "excel_file": "server2/Sai Thiruvallur/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "5-Poonamallee": {
                "excel_file": "server2/Sai Thiruvallur/5. POONAMALLEE (SC).xlsx",
                "main_location": "Poonamallee"
            },
            "6-Avadi": {
                "excel_file": "server2/Sai Thiruvallur/6. AVADI.xlsx",
                "main_location": "Avadi"
            },
            "7-Maduravoyal": {
                "excel_file": "server2/Sai Thiruvallur/7. MADURAVOYAL.xlsx",
                "main_location": "Maduravoyal"
            },
            "9-Madavaram": {
                "excel_file": "server2/Sai Thiruvallur/9. MADAVARAM.xlsx",
                "main_location": "Madavaram"
            },
            "10-Thiruvottiyur": {
                "excel_file": "server2/Sai Thiruvallur/10. THIRUVOTTIYUR.xlsx",
                "main_location": "Thiruvottiyur"
            }
        },
        "Shankar Misc": {
            "112-Avanashi (SC)": {
                "excel_file": "server2/Shankar Misc/112. AVANASHI (SC).xlsx",
                "main_location": "Avanashi"
            },
            "27-Shozhinganallur": {
                "excel_file": "server2/Shankar Misc/27. SHOZHINGANALLUR.xlsx",
                "main_location": "Shozhinganallur"
            },
            "28-Alandur": {
                "excel_file": "server2/Shankar Misc/28. Alandur.xlsx",
                "main_location": "Alandur"
            },
            "32-Chengalpattu": {
                "excel_file": "server2/Shankar Misc/32. CHENGALPATTU.xlsx",
                "main_location": "Chengalpattu"
            }
        },
        "01 Sai Namakkal": {
            "92-Rasipuram (SC)": {
                "excel_file": "server2/01 Sai Namakkal/92. Rasipuram.xlsx",
                "main_location": "Rasipuram"
            },
            "94-Namakkal": {
                "excel_file": "server2/01 Sai Namakkal/94. Nammakal.xlsx",
                "main_location": "Namakkal"
            },
            "96-Tiruchengodu": {
                "excel_file": "server2/01 Sai Namakkal/96. Tiruchengodu.xlsx",
                "main_location": "Tiruchengodu"
            },
            "97-Kumarapalayam": {
                "excel_file": "server2/01 Sai Namakkal/97. Kumarapalayam.xlsx",
                "main_location": "Kumarapalayam"
            }
        },
        "Bikas Tiruvannamalai APP": {
            "63-Tiruvannamalai": {
                "excel_file": "server2/Bikas Tiruvannamalai APP/63. TIRUVANNAMALAI.xlsx",
                "main_location": "Tiruvannamalai"
            },
            "69-Vandavasi (SC)": {
                "excel_file": "server2/Bikas Tiruvannamalai APP/69. VANDAVASI.xlsx",
                "main_location": "Vandavasi"
            }
        },
        "Bikas Kallakurichi APP": {
            "78-Rishivandiyam": {
                "excel_file": "server2/Bikas Kallakurichi APP/78. Rishivandiyam.xlsx",
                "main_location": "Rishivandiyam"
            },
            "80-Kallakurichi (SC)": {
                "excel_file": "server2/Bikas Kallakurichi APP/80. Kallakurichi.xlsx",
                "main_location": "Kallakurichi"
            }
        },
        "Bikas Tirupathur APP": {
            "40-Katpadi": {
                "excel_file": "server2/Bikas Tirupathur APP/40. Katpadi.xlsx",
                "main_location": "Katpadi"
            },
            "47-Vaniyambadi": {
                "excel_file": "server2/Bikas Tirupathur APP/47. VANIYAMBADI.xlsx",
                "main_location": "Vaniyambadi"
            },
            "49-Jolarpet": {
                "excel_file": "server2/Bikas Tirupathur APP/49 Jolarpet.xlsx",
                "main_location": "Jolarpet"
            },
            "50-Tirupattur": {
                "excel_file": "server2/Bikas Tirupathur APP/50. TIRUPATTUR.xlsx",
                "main_location": "Tirupattur"
            }
        },
        "Bikas Tiruchirapalli APP": {
            "138-Manapparai": {
                "excel_file": "server2/Bikas Tiruchirapalli APP/138. MANAPPARAI.xlsx",
                "main_location": "Manapparai"
            },
            "140-Tiruchirappalli (West)": {
                "excel_file": "server2/Bikas Tiruchirapalli APP/140. TIRUCHIRAPPALLI(WEST).xlsx",
                "main_location": "Tiruchirappalli (West)"
            }
        },
        "Bikas Viluppuram APP": {
            "70-Gingee": {
                "excel_file": "server2/Bikas Viluppuram APP/70. Gingee.xlsx",
                "main_location": "Gingee"
            },
            "71-Mailam": {
                "excel_file": "server2/Bikas Viluppuram APP/71. Mailam.xlsx",
                "main_location": "Mailam"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server2/Bikas Viluppuram APP/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "73-Vanur (SC)": {
                "excel_file": "server2/Bikas Viluppuram APP/73. Vanur.xlsx",
                "main_location": "Vanur"
            },
            "74-Villupuram": {
                "excel_file": "server2/Bikas Viluppuram APP/74 - Villupuram.xlsx",
                "main_location": "Villupuram"
            },
            "75-Vikravandi": {
                "excel_file": "server2/Bikas Viluppuram APP/75. Vikravandi.xlsx",
                "main_location": "Vikravandi"
            },
            "76-Tirukkoyilur": {
                "excel_file": "server2/Bikas Viluppuram APP/76. Tirukkoyilur.xlsx",
                "main_location": "Tirukkoyilur"
            }
        },
        "Sai Mayiladurutai": {
            "160-Sirkazhi (SC)": {
                "excel_file": "server2/Sai Mayiladurutai/160.Sizkazhi.xlsx",
                "main_location": "Sirkazhi"
            },
            "161-Mayiladuthurai": {
                "excel_file": "server2/Sai Mayiladurutai/161 Mayiladuthurai.xlsx",
                "main_location": "Mayiladuthurai"
            }
        },
        "Bikas Misc": {
            "43-Vellore": {
                "excel_file": "server2/Bikas Misc/43. Vellore.xlsx",
                "main_location": "Vellore"
            },
            "68-Cheyyar": {
                "excel_file": "server2/Bikas Misc/68 Cheyyur.xlsx",
                "main_location": "Cheyyar"
            },
            "148-Kunnam": {
                "excel_file": "server2/Bikas Misc/148. KUNNAM.xlsx",
                "main_location": "Kunnam"
            },
            "149-Ariyalur": {
                "excel_file": "server2/Bikas Misc/149. ARIYALUR.xlsx",
                "main_location": "Ariyalur"
            },
            "160-Sirkazhi (SC)": {
                "excel_file": "server2/Bikas Misc/160.Sizkazhi.xlsx",
                "main_location": "Sirkazhi"
            },
            "161-Mayiladuthurai": {
                "excel_file": "server2/Bikas Misc/161 Mayiladuthurai.xlsx",
                "main_location": "Mayiladuthurai"
            },
            "172-Papanasam": {
                "excel_file": "server2/Bikas Misc/172-Papanasam.xlsx",
                "main_location": "Papanasam"
            },
            "216-Srivaikuntam": {
                "excel_file": "server2/Bikas Misc/216. Srivaikundam.xlsx",
                "main_location": "Srivaikuntam"
            },
            "217-Ottapidaram (SC)": {
                "excel_file": "server2/Bikas Misc/217 - Ottapidaram (SC).xlsx",
                "main_location": "Ottapidaram"
            }
        },
        "Mahesh MISC": {
            "20-Thousand Lights": {
                "excel_file": "server2/Mahesh MISC/20. THOUSAND LIGHTS.xlsx",
                "main_location": "Thousand Lights"
            },
            "95-Paramathi-Velur": {
                "excel_file": "server2/Mahesh MISC/95. Paramathi velur.xlsx",
                "main_location": "Paramathi-Velur"
            },
            "133-Vedasandur": {
                "excel_file": "server2/Mahesh MISC/133. Vedasandur.xlsx",
                "main_location": "Vedasandur"
            },
            "188-Melur": {
                "excel_file": "server2/Mahesh MISC/188. Melur.xlsx",
                "main_location": "Melur"
            },
            "205-Sivakasi": {
                "excel_file": "server2/Mahesh MISC/205-Sivakasi.xlsx",
                "main_location": "Sivakasi"
            },
            "210-Tiruvadanai": {
                "excel_file": "server2/Mahesh MISC/210. Thiruvadanai.xlsx",
                "main_location": "Tiruvadanai"
            },
            "211-Ramanathapuram": {
                "excel_file": "server2/Mahesh MISC/211. Ramanathapuram.xlsx",
                "main_location": "Ramanathapuram"
            }
        },
        "Chennai APP": {
            "11-Dr.Radhakrishnan Nagar": {
                "excel_file": "server2/Chennai APP/11. Dr. Radhakrishnan Nagar.xlsx",
                "main_location": "Dr.Radhakrishnan Nagar"
            },
            "13-Kolathur": {
                "excel_file": "server2/Chennai APP/13. Kolathur.xlsx",
                "main_location": "Kolathur"
            },
            "14-Villivakkam": {
                "excel_file": "server2/Chennai APP/14. VILLIVAKKAM.xlsx",
                "main_location": "Villivakkam"
            },
            "15-Thiru-Vi-Ka-Nagar (SC)": {
                "excel_file": "server2/Chennai APP/15 Thiru Vi Ka Nagar.xlsx",
                "main_location": "Thiru-Vi-Ka-Nagar"
            },
            "16-Egmore (SC)": {
                "excel_file": "server2/Chennai APP/16. EGMORE.xlsx",
                "main_location": "Egmore"
            },
            "17-Royapuram": {
                "excel_file": "server2/Chennai APP/17. Royapuram.xlsx",
                "main_location": "Royapuram"
            },
            "18-Harbour": {
                "excel_file": "server2/Chennai APP/18. Harbour.xlsx",
                "main_location": "Harbour"
            },
            "19-Chepauk-Thiruvallikeni": {
                "excel_file": "server2/Chennai APP/19. Chepauk-Thiruvallikeni.xlsx",
                "main_location": "Chepauk-Thiruvallikeni"
            },
            "20-Thousand Lights": {
                "excel_file": "server2/Chennai APP/20. THOUSAND LIGHTS.xlsx",
                "main_location": "Thousand Lights"
            },
            "21-Anna Nagar": {
                "excel_file": "server2/Chennai APP/21. Anna Nagar.xlsx",
                "main_location": "Anna Nagar"
            },
            "22-Virugampakkam": {
                "excel_file": "server2/Chennai APP/22. Virugampakkam.xlsx",
                "main_location": "Virugampakkam"
            },
            "23-Saidapet": {
                "excel_file": "server2/Chennai APP/23. Saidapet.xlsx",
                "main_location": "Saidapet"
            },
            "24-Thiyagarayanagar": {
                "excel_file": "server2/Chennai APP/24. THIYAGARAYANAGAR.xlsx",
                "main_location": "Thiyagarayanagar"
            },
            "25-Mylapore": {
                "excel_file": "server2/Chennai APP/25. Mylapore.xlsx",
                "main_location": "Mylapore"
            },
            "26-Velachery": {
                "excel_file": "server2/Chennai APP/26. Velachery.xlsx",
                "main_location": "Velachery"
            }
        },
        "Shyam MISC": {
            "2-Ponneri (SC)": {
                "excel_file": "server2/Shyam MISC/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "35-Madurantakam (SC)": {
                "excel_file": "server2/Shyam MISC/35. MADURANTAKAM (SC).xlsx",
                "main_location": "Madurantakam"
            },
            "68-Cheyyar": {
                "excel_file": "server2/Shyam MISC/68 Cheyyur.xlsx",
                "main_location": "Cheyyar"
            },
            "78-Rishivandiyam": {
                "excel_file": "server2/Shyam MISC/78. Rishivandiyam.xlsx",
                "main_location": "Rishivandiyam"
            },
            "79-Sankarapuram": {
                "excel_file": "server2/Shyam MISC/79. Sankarapuram.xlsx",
                "main_location": "Sankarapuram"
            },
            "82-Attur (SC)": {
                "excel_file": "server2/Shyam MISC/82.Attur.xlsx",
                "main_location": "Attur"
            },
            "113-Tiruppur (North)": {
                "excel_file": "server2/Shyam MISC/113. TIRUPPUR (NORTH).xlsx",
                "main_location": "Tiruppur (North)"
            },
            "114-Tiruppur (South)": {
                "excel_file": "server2/Shyam MISC/114. TIRUPPUR (SOUTH).xlsx",
                "main_location": "Tiruppur (South)"
            },
            "227-Nanguneri": {
                "excel_file": "server2/Shyam MISC/227. Nanguneri.xlsx",
                "main_location": "Nanguneri"
            },
            "234-Killiyoor": {
                "excel_file": "server2/Shyam MISC/234. Killiyoor.xlsx",
                "main_location": "Killiyoor"
            }
        },
        "Arun APP": {
            "1-Gummidipoondi": {
                "excel_file": "server2/Arun APP/1. GUMMIDIPOONDI.xlsx",
                "main_location": "Gummidipoondi"
            },
            "2-Ponneri (SC)": {
                "excel_file": "server2/Arun APP/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "9-Madavaram": {
                "excel_file": "server2/Arun APP/9. MADAVARAM.xlsx",
                "main_location": "Madavaram"
            },
            "11-Dr.Radhakrishnan Nagar": {
                "excel_file": "server2/Arun APP/11. Dr. Radhakrishnan Nagar.xlsx",
                "main_location": "Dr.Radhakrishnan Nagar"
            },
            "18-Harbour": {
                "excel_file": "server2/Arun APP/18. Harbour.xlsx",
                "main_location": "Harbour"
            },
            "19-Chepauk-Thiruvallikeni": {
                "excel_file": "server2/Arun APP/19. Chepauk-Thiruvallikeni.xlsx",
                "main_location": "Chepauk-Thiruvallikeni"
            }
        },
        "Omni MISC 01": {
            "4-Thiruvallur": {
                "excel_file": "server2/Omni MISC/4. THIRUVALLUR.xlsx",
                "main_location": "Thiruvallur"
            },
            "34-Cheyyur (SC)": {
                "excel_file": "server2/Omni MISC/34. CHEYYUR.xlsx",
                "main_location": "Cheyyur"
            },
            "35-Madurantakam (SC)": {
                "excel_file": "server2/Omni MISC/35. MADURANTAKAM (SC).xlsx",
                "main_location": "Madurantakam"
            },
            "68-Cheyyar": {
                "excel_file": "server2/Omni MISC/68 Cheyyur.xlsx",
                "main_location": "Cheyyar"
            },
            "70-Gingee": {
                "excel_file": "server2/Omni MISC/70. Gingee.xlsx",
                "main_location": "Gingee"
            },
            "77-Ulundurpettai": {
                "excel_file": "server2/Omni MISC/77-Ulundurpettai.xlsx",
                "main_location": "Ulundurpettai"
            },
            "78-Rishivandiyam": {
                "excel_file": "server2/Omni MISC/78. Rishivandiyam.xlsx",
                "main_location": "Rishivandiyam"
            },
            "79-Sankarapuram": {
                "excel_file": "server2/Omni MISC/79. Sankarapuram.xlsx",
                "main_location": "Sankarapuram"
            },
            "82-Attur (SC)": {
                "excel_file": "server2/Omni MISC/82.Attur.xlsx",
                "main_location": "Attur"
            },
            "96-Tiruchengodu": {
                "excel_file": "server2/Omni MISC/96. Tiruchengodu.xlsx",
                "main_location": "Tiruchengodu"
            },
            "104-Bhavani": {
                "excel_file": "server2/Omni MISC/104. Bhavani.xlsx",
                "main_location": "Bhavani"
            },
            "106-Gobichettipalayam": {
                "excel_file": "server2/Omni MISC/106. GOBICHETTIPALAYAM.xlsx",
                "main_location": "Gobichettipalayam"
            },
            "113-Tiruppur (North)": {
                "excel_file": "server2/Omni MISC/113. TIRUPPUR (NORTH).xlsx",
                "main_location": "Tiruppur (North)"
            },
            "114-Tiruppur (South)": {
                "excel_file": "server2/Omni MISC/114. TIRUPPUR (SOUTH).xlsx",
                "main_location": "Tiruppur (South)"
            },
            "209-Paramakudi (SC)": {
                "excel_file": "server2/Omni MISC/209-Paramakudi.xlsx",
                "main_location": "Paramakudi"
            },
            "213-Vilathikulam": {
                "excel_file": "server2/Omni MISC/213-Vilathikulam.xlsx",
                "main_location": "Vilathikulam"
            },
            "227-Nanguneri": {
                "excel_file": "server2/Omni MISC/227. Nanguneri.xlsx",
                "main_location": "Nanguneri"
            },
            "232-Padmanabhapuram": {
                "excel_file": "server2/Omni MISC/232. Padmanabhapuram.xlsx",
                "main_location": "Padmanabhapuram"
            },
            "233-Vilavancode": {
                "excel_file": "server2/Omni MISC/233. Vilavancode.xlsx",
                "main_location": "Vilavancode"
            },
            "234-Killiyoor": {
                "excel_file": "server2/Omni MISC/234. Killiyoor.xlsx",
                "main_location": "Killiyoor"
            }
        },
        "Omni MISC 02": {
            "1-Gummidipoondi": {
                "excel_file": "server2/Omni MISC 02/1. GUMMIDIPOONDI.xlsx",
                "main_location": "Gummidipoondi"
            },
            "2-Ponneri (SC)": {
                "excel_file": "server2/Omni MISC 02/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "22-Virugampakkam": {
                "excel_file": "server2/Omni MISC 02/22. Virugampakkam.xlsx",
                "main_location": "Virugampakkam"
            },
            "60-Pappireddippatti": {
                "excel_file": "server2/Omni MISC 02/60. Pappireddipatti.xlsx",
                "main_location": "Pappireddippatti"
            },
            "61-Harur (SC)": {
                "excel_file": "server2/Omni MISC 02/61. HARUR.xlsx",
                "main_location": "Harur"
            },
            "71-Mailam": {
                "excel_file": "server2/Omni MISC 02/71. Mailam.xlsx",
                "main_location": "Mailam"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server2/Omni MISC 02/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "82-Attur (SC)": {
                "excel_file": "server2/Omni MISC 02/82.Attur.xlsx",
                "main_location": "Attur"
            },
            "87-Sankari": {
                "excel_file": "server2/Omni MISC 02/87.Sankari.xlsx",
                "main_location": "Sankari"
            },
            "102-Kangayam": {
                "excel_file": "server2/Omni MISC 02/102. KANGAYAM.xlsx",
                "main_location": "Kangayam"
            },
            "107-Bhavanisagar": {
                "excel_file": "server2/Omni MISC 02/107. Bhavanisagar.xlsx",
                "main_location": "Bhavanisagar"
            },
            "115-Palladam": {
                "excel_file": "server2/Omni MISC 02/115. Palladam.xlsx",
                "main_location": "Palladam"
            },
            "117-Kavundampalayam": {
                "excel_file": "server2/Omni MISC 02/117. Kavundampalayam.xlsx",
                "main_location": "Kavundampalayam"
            },
            "118-Coimbatore (North)": {
                "excel_file": "server2/Omni MISC 02/118. Coimbatore North.xlsx",
                "main_location": "Coimbatore (North)"
            },
            "231-Colachal": {
                "excel_file": "server2/Omni MISC 02/231. Colachal.xlsx",
                "main_location": "Colachal"
            }
        },
        "Omni MISC 03": {
            "1-Gummidipoondi": {
                "excel_file": "server2/Omni MISC 03/1. GUMMIDIPOONDI.xlsx",
                "main_location": "Gummidipoondi"
            },
            "2-Ponneri (SC)": {
                "excel_file": "server2/Omni MISC 03/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "6-Avadi": {
                "excel_file": "server2/Omni MISC 03/6. AVADI.xlsx",
                "main_location": "Avadi"
            },
            "9-Madavaram": {
                "excel_file": "server2/Omni MISC 03/9. MADAVARAM.xlsx",
                "main_location": "Madavaram"
            },
            "20-Thousand Lights": {
                "excel_file": "server2/Omni MISC 03/20. THOUSAND LIGHTS.xlsx",
                "main_location": "Thousand Lights"
            },
            "22-Virugampakkam": {
                "excel_file": "server2/Omni MISC 03/22. Virugampakkam.xlsx",
                "main_location": "Virugampakkam"
            },
            "29-Sriperumbudur (SC)": {
                "excel_file": "server2/Omni MISC 03/29. SRIPERUMBUDUR.xlsx",
                "main_location": "Sriperumbudur"
            },
            "36-Uthiramerur": {
                "excel_file": "server2/Omni MISC 03/36. UTHIRAMERUR 1.xlsx",
                "main_location": "Uthiramerur"
            },
            "41-Ranipet": {
                "excel_file": "server2/Omni MISC 03/41. Ranipet.xlsx",
                "main_location": "Ranipet"
            },
            "44-Anaikattu": {
                "excel_file": "server2/Omni MISC 03/44. ANAIKATTU.xlsx",
                "main_location": "Anaikattu"
            },
            "61-Harur (SC)": {
                "excel_file": "server2/Omni MISC 03/61. HARUR.xlsx",
                "main_location": "Harur"
            },
            "71-Mailam": {
                "excel_file": "server2/Omni MISC 03/71. Mailam.xlsx",
                "main_location": "Mailam"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server2/Omni MISC 03/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "73-Vanur (SC)": {
                "excel_file": "server2/Omni MISC 03/73. Vanur.xlsx",
                "main_location": "Vanur"
            },
            "87-Sankari": {
                "excel_file": "server2/Omni MISC 03/87.Sankari.xlsx",
                "main_location": "Sankari"
            },
            "92-Rasipuram (SC)": {
                "excel_file": "server2/Omni MISC 03/92. Rasipuram.xlsx",
                "main_location": "Rasipuram"
            },
            "94-Namakkal": {
                "excel_file": "server2/Omni MISC 03/94. Nammakal.xlsx",
                "main_location": "Namakkal"
            },
            "95-Paramathi-Velur": {
                "excel_file": "server2/Omni MISC 03/95. Paramathi velur.xlsx",
                "main_location": "Paramathi-Velur"
            },
            "102-Kangayam": {
                "excel_file": "server2/Omni MISC 03/102. KANGAYAM.xlsx",
                "main_location": "Kangayam"
            },
            "107-Bhavanisagar": {
                "excel_file": "server2/Omni MISC 03/107. Bhavanisagar.xlsx",
                "main_location": "Bhavanisagar"
            },
            "108-Udhagamandalam": {
                "excel_file": "server2/Omni MISC 03/108-Udhagamandalam.xlsx",
                "main_location": "Udhagamandalam"
            },
            "110-Coonoor": {
                "excel_file": "server2/Omni MISC 03/110 Coonoor.xlsx",
                "main_location": "Coonoor"
            },
            "115-Palladam": {
                "excel_file": "server2/Omni MISC 03/115. Palladam.xlsx",
                "main_location": "Palladam"
            },
            "117-Kavundampalayam": {
                "excel_file": "server2/Omni MISC 03/117. Kavundampalayam.xlsx",
                "main_location": "Kavundampalayam"
            },
            "118-Coimbatore (North)": {
                "excel_file": "server2/Omni MISC 03/118. Coimbatore North.xlsx",
                "main_location": "Coimbatore (North)"
            },
            "120-Coimbatore (South)": {
                "excel_file": "server2/Omni MISC 03/120. Coimbatore (South).xlsx",
                "main_location": "Coimbatore (South)"
            },
            "122-Kinathukadavu": {
                "excel_file": "server2/Omni MISC 03/122. Kinathukadavu.xlsx",
                "main_location": "Kinathukadavu"
            },
            "133.Vedasandur": {
                "excel_file": "server3/Omni MISC 03/133.Vedasandur.xlsx",
                "main_location": "Vedasandur"
            },
            "176-Pattukkottai": {
                "excel_file": "server2/Omni MISC 03/176. Pattukkottai.xlsx",
                "main_location": "Pattukkottai"
            },
            "216-Srivaikuntam": {
                "excel_file": "server3/Omni MISC 03/216.Srivaikundam.xlsx",
                "main_location": "Srivaikuntam"
            },
            "225-Ambasamudram": {
                "excel_file": "server2/Omni MISC 03/225. Ambasamudram.xlsx",
                "main_location": "Ambasamudram"
            },
            "226-Palayamkottai": {
                "excel_file": "server2/Omni MISC 03/226. Palayamkottai.xlsx",
                "main_location": "Palayamkottai"
            },
            "229-Kanniyakumari": {
                "excel_file": "server2/Omni MISC 03/229. Kanniyakumari.xlsx",
                "main_location": "Kanniyakumari"
            },
            "230-Nagercoil": {
                "excel_file": "server2/Omni MISC 03/230. Nagercoil.xlsx",
                "main_location": "Nagercoil"
            },
            "231-Colachal": {
                "excel_file": "server2/Omni MISC 03/231. Colachal.xlsx",
                "main_location": "Colachal"
            }
        }
    },
    "server3": {
        "05 Beekay V6": {
            "4-Thiruvallur": {
                "excel_file": "server3/05 Beekay V6/4. THIRUVALLUR.xlsx",
                "main_location": "Thiruvallur"
            },
            "51-Uthangarai (SC)": {
                "excel_file": "server3/05 Beekay V6/51. UTHANGARI.xlsx",
                "main_location": "Uthangarai"
            },
            "178-Gandharvakottai (SC)": {
                "excel_file": "server3/05 Beekay V6/178. Gandharvakottai.xlsx",
                "main_location": "Gandharvakottai"
            }
        },
        "Sai Tiruppur": {
            "112-Avanashi (SC)": {
                "excel_file": "server3/Sai Tiruppur/112. AVANASHI (SC).xlsx",
                "main_location": "Avanashi"
            },
            "113-Tiruppur (North)": {
                "excel_file": "server3/Sai Tiruppur/113. TIRUPPUR (NORTH).xlsx",
                "main_location": "Tiruppur (North)"
            },
            "114-Tiruppur (South)": {
                "excel_file": "server3/Sai Tiruppur/114. TIRUPPUR (SOUTH).xlsx",
                "main_location": "Tiruppur (South)"
            },
            "125-Udumalpet": {
                "excel_file": "server3/Sai Tiruppur/125. UDUMALAIPETTAI.xlsx",
                "main_location": "UDUMALAIPETTAI"
            },
            "126-Madathukulam": {
                "excel_file": "server3/Sai Tiruppur/126. MADATHUKULAM.xlsx",
                "main_location": "Madathukulam"
            }
        },
        "Sai Murugan Madurai": {
            "140-Tiruchirappalli (West)": {
                "excel_file": "server3/Sai Madurai/140. TIRUCHIRAPPALLI(WEST).xlsx",
                "main_location": "Tiruchirappalli (West)"
            },
            "188-Melur": {
                "excel_file": "server3/Sai Madurai/188. Melur.xlsx",
                "main_location": "Melur"
            },
            "189-Madurai East": {
                "excel_file": "server3/Sai Madurai/189. MADURAI EAST.xlsx",
                "main_location": "MADURAI EAST"
            },
            "190-Sholavandan (SC)": {
                "excel_file": "server3/Sai Madurai/190 Sholavandana.xlsx",
                "main_location": "Sholavandan"
            },
            "191-Madurai North": {
                "excel_file": "server3/Sai Madurai/191. Madurai North.xlsx",
                "main_location": "Madurai North"
            },
            "192-Madurai South": {
                "excel_file": "server3/Sai Madurai/192. Madurai South.xlsx",
                "main_location": "Madurai South"
            },
            "193-Madurai Central": {
                "excel_file": "server3/Sai Madurai/193. Madurai Central.xlsx",
                "main_location": "Madurai Central"
            },
            "194-Madurai West": {
                "excel_file": "server3/Sai Madurai/194. Madurai West.xlsx",
                "main_location": "Madurai West"
            },
            "195-Thiruparankundram": {
                "excel_file": "server3/Sai Madurai/195. Thirupparamkundram.xlsx",
                "main_location": "Thirupparamkundram"
            },
            "196-Thirumangalam": {
                "excel_file": "server3/Sai Madurai/196 - Thirumangalam.xlsx",
                "main_location": "Thirumangalam"
            },
            "197-Usilampatti": {
                "excel_file": "server3/Sai Madurai/197. Usilampatti.xlsx",
                "main_location": "Usilampatti"
            }
        },
        "01 Laxmi Narayana Erode": {
            "98-Erode (East)": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/98. Erode (East).xlsx",
                "main_location": "Erode (East)"
            },
            "99-Erode (West)": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/99. Erode (West).xlsx",
                "main_location": "Erode (West)"
            },
            "101-Dharapuram (SC)": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/101-DHARAPURAM (SC).xlsx",
                "main_location": "Dharapuram"
            },
            "102-Kangayam": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/102. KANGAYAM.xlsx",
                "main_location": "Kangayam"
            },
            "104-Bhavani": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/104. Bhavani.xlsx",
                "main_location": "Bhavani"
            },
            "105-Anthiyur": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/105. ANTHIYUR.xlsx",
                "main_location": "Anthiyur"
            },
            "106-Gobichettipalayam": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/106. GOBICHETTIPALAYAM.xlsx",
                "main_location": "Gobichettipalayam"
            },
            "107-Bhavanisagar": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/107. Bhavanisagar.xlsx",
                "main_location": "Bhavanisagar"
            },
            "115-Palladam": {
                "excel_file": "server3/01 Laxmi Narayana TN Landscape/115. Palladam.xlsx",
                "main_location": "Palladam"
            }
        },
        "Shankar Sai Coimbatore": {
            "111-Mettuppalayam": {
                "excel_file": "server3/02 Sai Coimbatore/111. METTUPALAYAM.xlsx",
                "main_location": "Mettuppalayam"
            },
            "116-Sulur": {
                "excel_file": "server3/02 Sai Coimbatore/116. SULUR.xlsx",
                "main_location": "Sulur"
            },
            "119-Thondamuthur": {
                "excel_file": "server3/02 Sai Coimbatore/119. Thondamuthur.xlsx",
                "main_location": "Thondamuthur"
            },
            "120-Coimbatore (South)": {
                "excel_file": "server3/02 Sai Coimbatore/120. Coimbatore (South).xlsx",
                "main_location": "Coimbatore (South)"
            },
            "121-Singanallur": {
                "excel_file": "server3/02 Sai Coimbatore/121. Singanallur.xlsx",
                "main_location": "Singanallur"
            },
            "122-Kinathukadavu": {
                "excel_file": "server3/02 Sai Coimbatore/122. Kinathukadavu.xlsx",
                "main_location": "Kinathukadavu"
            },
            "123-Pollachi": {
                "excel_file": "server3/02 Sai Coimbatore/123. POLLACHI.xlsx",
                "main_location": "Pollachi"
            },
            "124-Valparai (SC)": {
                "excel_file": "server3/02 Sai Coimbatore/124. VALPARAI.xlsx",
                "main_location": "Valparai"
            }
        },
        "03 Bikas V6": {
            "14-Villivakkam": {
                "excel_file": "server3/03 Bikas V6/14 VILLIVAKKAM.xlsx",
                "main_location": "Villivakkam"
            },
            "44-Anaikattu": {
                "excel_file": "server3/03 Bikas V6/44. Anaikattu.xlsx",
                "main_location": "Anaikattu"
            },
            "81-Gangavalli (SC)": {
                "excel_file": "server3/03 Bikas V6/81.gangavalli.xlsx",
                "main_location": "Gangavalli"
            },
            "176-Pattukkottai": {
                "excel_file": "server3/03 Bikas V6/176. Pattukkottai.xlsx",
                "main_location": "Pattukkottai"
            },
            "182-Alangudi": {
                "excel_file": "server3/03 Bikas V6/182. Alangudi.xlsx",
                "main_location": "Alangudi"
            },
            "207-Aruppukkottai": {
                "excel_file": "server3/03 Bikas V6/207. Aruppukkottai.xlsx",
                "main_location": "Aruppukkottai"
            },
            "223-Alangulam": {
                "excel_file": "server3/03 Bikas V6/223 - Alangulam.xlsx",
                "main_location": "Alangulam"
            }
        },
        "01 Vasu Srinivas TN Landscape": {
            "52-Bargur": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/52. Bargur.xlsx",
                "main_location": "Bargur"
            },
            "70-Gingee": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/70. Gingee.xlsx",
                "main_location": "Gingee"
            },
            "71-Mailam": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/71. Mailam.xlsx",
                "main_location": "Mailam"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "75-Vikravandi": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/75. Vikravandi.xlsx",
                "main_location": "Vikravandi"
            },
            "76-Tirukkoyilur": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/76. Tirukkoyilur.xlsx",
                "main_location": "Tirukkoyilur"
            },
            "117-Kavundampalayam": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/117. Kavundampalayam.xlsx",
                "main_location": "Kavundampalayam"
            },
            "151-Tittakudi (SC)": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/151. Tittakudi.xlsx",
                "main_location": "Tittakudi"
            },
            "176-Pattukkottai": {
                "excel_file": "server3/01 Vasu Srinivas TN Landscape/176. Pattukkottai.xlsx",
                "main_location": "Pattukkottai"
            }
        },
        "01 Bhaskar Srinivas TN Landscape Survey": {
            "77-Ulundurpettai": {
                "excel_file": "server3/01 Bhaskar Srinivas TN Landscape Survey/77-Ulundurpettai.xlsx",
                "main_location": "Ulundurpettai"
            },
            "165-Vedaranyam": {
                "excel_file": "server3/01 Bhaskar Srinivas TN Landscape Survey/165. Vedharanyam.xlsx",
                "main_location": "Vedaranyam"
            },
            "166-Thiruthuraipoondi (SC)": {
                "excel_file": "server3/01 Bhaskar Srinivas TN Landscape Survey/166. Thiruthuraipoondi.xlsx",
                "main_location": "Thiruthuraipoondi"
            },
            "167-Mannargudi": {
                "excel_file": "server3/01 Bhaskar Srinivas TN Landscape Survey/167. Mannargudi.xlsx",
                "main_location": "Mannargudi"
            },
            "168-Thiruvarur": {
                "excel_file": "server3/01 Bhaskar Srinivas TN Landscape Survey/168. Thiruvarur.xlsx",
                "main_location": "Thiruvarur"
            },
            "169-Nannilam": {
                "excel_file": "server3/01 Bhaskar Srinivas TN Landscape Survey/169. Nannilam.xlsx",
                "main_location": "Nannilam"
            },
            "200-Bodinayakanur": {
                "excel_file": "server3/01 Bhaskar Srinivas TN Landscape Survey/200. Bodinayakanur.xlsx",
                "main_location": "Bodinayakanur"
            }
        },
        "01 Nirmal V6": {
            "93-Senthamangalam (ST)": {
                "excel_file": "server3/01 Nirmal V6/93. Senthamangalam.xlsx",
                "main_location": "Senthamangalam"
            },
            "105-Anthiyur": {
                "excel_file": "server3/01 Nirmal V6/105. ANTHIYUR.xlsx",
                "main_location": "Anthiyur"
            }
        },
        "Bikas Tiruvannamalai APP": {
            "63-Tiruvannamalai": {
                "excel_file": "server3/Bikas Tiruvannamalai APP/63. TIRUVANNAMALAI.xlsx",
                "main_location": "Tiruvannamalai"
            },
            "69-Vandavasi (SC)": {
                "excel_file": "server3/Bikas Tiruvannamalai APP/69. VANDAVASI.xlsx",
                "main_location": "Vandavasi"
            }
        },
        "Bikas Kallakurichi APP": {
            "78-Rishivandiyam": {
                "excel_file": "server3/Bikas Kallakurichi APP/78. Rishivandiyam.xlsx",
                "main_location": "Rishivandiyam"
            },
            "80-Kallakurichi (SC)": {
                "excel_file": "server3/Bikas Kallakurichi APP/80. Kallakurichi.xlsx",
                "main_location": "Kallakurichi"
            }
        },
        "Bikas Tirupathur APP": {
            "40-Katpadi": {
                "excel_file": "server3/Bikas Tirupathur APP/40. Katpadi.xlsx",
                "main_location": "Katpadi"
            },
            "47-Vaniyambadi": {
                "excel_file": "server3/Bikas Tirupathur APP/47. VANIYAMBADI.xlsx",
                "main_location": "Vaniyambadi"
            },
            "49-Jolarpet": {
                "excel_file": "server3/Bikas Tirupathur APP/49 Jolarpet.xlsx",
                "main_location": "Jolarpet"
            },
            "50-Tirupattur": {
                "excel_file": "server3/Bikas Tirupathur APP/50. TIRUPATTUR.xlsx",
                "main_location": "Tirupattur"
            }
        },
        "Bikas Tiruchirapalli APP": {
            "138-Manapparai": {
                "excel_file": "server3/Bikas Tiruchirapalli APP/138. MANAPPARAI.xlsx",
                "main_location": "Manapparai"
            },
            "140-Tiruchirappalli (West)": {
                "excel_file": "server3/Bikas Tiruchirapalli APP/140. TIRUCHIRAPPALLI(WEST).xlsx",
                "main_location": "Tiruchirappalli (West)"
            }
        },
        "Bikas Viluppuram APP": {
            "70-Gingee": {
                "excel_file": "server3/Bikas Viluppuram APP/70. Gingee.xlsx",
                "main_location": "Gingee"
            },
            "71-Mailam": {
                "excel_file": "server3/Bikas Viluppuram APP/71. Mailam.xlsx",
                "main_location": "Mailam"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server3/Bikas Viluppuram APP/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "73-Vanur (SC)": {
                "excel_file": "server3/Bikas Viluppuram APP/73. Vanur.xlsx",
                "main_location": "Vanur"
            },
            "74-Villupuram": {
                "excel_file": "server3/Bikas Viluppuram APP/74 - Villupuram.xlsx",
                "main_location": "Villupuram"
            },
            "75-Vikravandi": {
                "excel_file": "server3/Bikas Viluppuram APP/75. Vikravandi.xlsx",
                "main_location": "Vikravandi"
            },
            "76-Tirukkoyilur": {
                "excel_file": "server3/Bikas Viluppuram APP/76. Tirukkoyilur.xlsx",
                "main_location": "Tirukkoyilur"
            }
        },
        "Sai Mahesh Gopal Salem": {
            "82-Attur (SC)": {
                "excel_file": "server3/Sai Salem/82.Attur.xlsx",
                "main_location": "Attur"
            },
            "83-Yercaud (ST)": {
                "excel_file": "server3/Sai Salem/83.Yercaud.xlsx",
                "main_location": "Yercaud"
            },
            "84-Omalur": {
                "excel_file": "server3/Sai Salem/84. Omalur.xlsx",
                "main_location": "Omalur"
            },
            "85-Mettur": {
                "excel_file": "server3/Sai Salem/85.Mettur.xlsx",
                "main_location": "Mettur"
            },
            "86-Edappadi": {
                "excel_file": "server3/Sai Salem/86.Edappadi.xlsx",
                "main_location": "Edappadi"
            },
            "87-Sankari": {
                "excel_file": "server3/Sai Salem/87.Sankari.xlsx",
                "main_location": "Sankari"
            },
            "89-Salem (North)": {
                "excel_file": "server3/Sai Salem/89.Salem North.xlsx",
                "main_location": "Salem (North)"
            },
            "91-Veerapandi": {
                "excel_file": "server3/Sai Salem/91.Veerapandi.xlsx",
                "main_location": "Veerapandi"
            }
        },
        "01 Sai Namakkal": {
            "92-Rasipuram (SC)": {
                "excel_file": "server3/01 Sai Namakkal/92. Rasipuram.xlsx",
                "main_location": "Rasipuram"
            },
            "94-Namakkal": {
                "excel_file": "server3/01 Sai Namakkal/94. Nammakal.xlsx",
                "main_location": "Namakkal"
            },
            "96-Tiruchengodu": {
                "excel_file": "server3/01 Sai Namakkal/96. Tiruchengodu.xlsx",
                "main_location": "Tiruchengodu"
            },
            "97-Kumarapalayam": {
                "excel_file": "server3/01 Sai Namakkal/97. Kumarapalayam.xlsx",
                "main_location": "Kumarapalayam"
            }
        },
        "Bikas Chennai APP": {
            "14-Villivakkam": {
                "excel_file": "server3/Bikas Chennai APP/14. VILLIVAKKAM.xlsx",
                "main_location": "Villivakkam"
            },
            "16-Egmore (SC)": {
                "excel_file": "server3/Bikas Chennai APP/16. EGMORE.xlsx",
                "main_location": "Egmore"
            },
            "18-Harbour": {
                "excel_file": "server3/Bikas Chennai APP/18. Harbour.xlsx",
                "main_location": "Harbour"
            },
            "19-Chepauk-Thiruvallikeni": {
                "excel_file": "server3/Bikas Chennai APP/19. Chepauk-Thiruvallikeni.xlsx",
                "main_location": "Chepauk-Thiruvallikeni"
            },
            "21-Anna Nagar": {
                "excel_file": "server3/Bikas Chennai APP/21. Anna Nagar.xlsx",
                "main_location": "Anna Nagar"
            }
        },
        "Bikas Shashi Dharmapuri APP": {
            "57-Palacodu": {
                "excel_file": "server3/Bikas Dharmapuri APP/57. Palacode.xlsx",
                "main_location": "Palacodu"
            },
            "58-Pennagaram": {
                "excel_file": "server3/Bikas Dharmapuri APP/58. Pennagaram.xlsx",
                "main_location": "Pennagaram"
            },
            "59-Dharmapuri": {
                "excel_file": "server3/Bikas Dharmapuri APP/59. Dharmapuri.xlsx",
                "main_location": "Dharmapuri"
            },
            "60-Pappireddippatti": {
                "excel_file": "server3/Bikas Dharmapuri APP/60. Pappireddipatti.xlsx",
                "main_location": "Pappireddippatti"
            },
            "61-Harur (SC)": {
                "excel_file": "server3/Bikas Dharmapuri APP/61. HARUR.xlsx",
                "main_location": "Harur"
            }
        },
        "Bikas Chengalpattu": {
            "27-Shozhinganallur": {
                "excel_file": "server3/Bikas Chengalpattu/27. SHOZHINGANALLUR.xlsx",
                "main_location": "Shozhinganallur"
            },
            "30-Pallavaram": {
                "excel_file": "server3/Bikas Chengalpattu/30. PALLAVARAM.xlsx",
                "main_location": "Pallavaram"
            },
            "31-Tambaram": {
                "excel_file": "server3/Bikas Chengalpattu/31. Tambaram.xlsx",
                "main_location": "Tambaram"
            },
            "32-Chengalpattu": {
                "excel_file": "server3/Bikas Chengalpattu/32. CHENGALPATTU.xlsx",
                "main_location": "Chengalpattu"
            },
            "33-Thiruporur": {
                "excel_file": "server3/Bikas Chengalpattu/33. THIRUPORUR.xlsx",
                "main_location": "Thiruporur"
            },
            "34-Cheyyur (SC)": {
                "excel_file": "server3/Bikas Chengalpattu/34. CHEYYUR.xlsx",
                "main_location": "Cheyyur"
            },
            "35-Madurantakam (SC)": {
                "excel_file": "server3/Bikas Chengalpattu/35. MADURANTAKAM (SC).xlsx",
                "main_location": "Madurantakam"
            }
        },
        "Moon MISC 02": {
            "43-Vellore": {
                "excel_file": "server3/Moon MISC 02/43. Vellore.xlsx",
                "main_location": "Vellore"
            },
            "84-Omalur": {
                "excel_file": "server3/Moon MISC 02/84. Omalur.xlsx",
                "main_location": "Omalur"
            },
            "86-Edappadi": {
                "excel_file": "server3/Moon MISC 02/86.Edappadi.xlsx",
                "main_location": "Edappadi"
            },
            "107-Bhavanisagar": {
                "excel_file": "server3/Moon MISC 02/107. Bhavanisagar.xlsx",
                "main_location": "Bhavanisagar"
            },
            "110-Coonoor": {
                "excel_file": "server3/Moon MISC 02/110 Coonoor.xlsx",
                "main_location": "Coonoor"
            },
            "111-Mettuppalayam": {
                "excel_file": "server3/Moon MISC 02/111. METTUPALAYAM.xlsx",
                "main_location": "Mettuppalayam"
            },
            "112-Avanashi (SC)": {
                "excel_file": "server3/Moon MISC 02/112. AVANASHI (SC).xlsx",
                "main_location": "Avanashi"
            }
        },
        "Sai Mayiladurutai": {
            "160-Sirkazhi (SC)": {
                "excel_file": "server3/Sai Mayiladurutai/160.Sizkazhi.xlsx",
                "main_location": "Sirkazhi"
            },
            "161-Mayiladuthurai": {
                "excel_file": "server3/Sai Mayiladurutai/161 Mayiladuthurai.xlsx",
                "main_location": "Mayiladuthurai"
            }
        },
        "Bikas Misc": {
            "43-Vellore": {
                "excel_file": "server3/Bikas Misc/43. Vellore.xlsx",
                "main_location": "Vellore"
            },
            "68-Cheyyar": {
                "excel_file": "server3/Bikas Misc/68 Cheyyur.xlsx",
                "main_location": "Cheyyar"
            },
            "148-Kunnam": {
                "excel_file": "server3/Bikas Misc/148. KUNNAM.xlsx",
                "main_location": "Kunnam"
            },
            "149-Ariyalur": {
                "excel_file": "server3/Bikas Misc/149. ARIYALUR.xlsx",
                "main_location": "Ariyalur"
            },
            "160-Sirkazhi (SC)": {
                "excel_file": "server3/Bikas Misc/160.Sizkazhi.xlsx",
                "main_location": "Sirkazhi"
            },
            "161-Mayiladuthurai": {
                "excel_file": "server3/Bikas Misc/161 Mayiladuthurai.xlsx",
                "main_location": "Mayiladuthurai"
            },
            "172-Papanasam": {
                "excel_file": "server3/Bikas Misc/172-Papanasam.xlsx",
                "main_location": "Papanasam"
            },
            "216-Srivaikuntam": {
                "excel_file": "server3/Bikas Misc/216. Srivaikundam.xlsx",
                "main_location": "Srivaikuntam"
            },
            "217-Ottapidaram (SC)": {
                "excel_file": "server3/Bikas Misc/217 - Ottapidaram (SC).xlsx",
                "main_location": "Ottapidaram"
            }
        },
        "Mahesh MISC": {
            "20-Thousand Lights": {
                "excel_file": "server3/Mahesh MISC/20. THOUSAND LIGHTS.xlsx",
                "main_location": "Thousand Lights"
            },
            "95-Paramathi-Velur": {
                "excel_file": "server3/Mahesh MISC/95. Paramathi velur.xlsx",
                "main_location": "Paramathi-Velur"
            },
            "133-Vedasandur": {
                "excel_file": "server3/Mahesh MISC/133. Vedasandur.xlsx",
                "main_location": "Vedasandur"
            },
            "188-Melur": {
                "excel_file": "server3/Mahesh MISC/188. Melur.xlsx",
                "main_location": "Melur"
            },
            "205-Sivakasi": {
                "excel_file": "server3/Mahesh MISC/205-Sivakasi.xlsx",
                "main_location": "Sivakasi"
            },
            "210-Tiruvadanai": {
                "excel_file": "server3/Mahesh MISC/210. Thiruvadanai.xlsx",
                "main_location": "Tiruvadanai"
            },
            "211-Ramanathapuram": {
                "excel_file": "server3/Mahesh MISC/211. Ramanathapuram.xlsx",
                "main_location": "Ramanathapuram"
            }
        },
        "Chennai APP": {
            "11-Dr.Radhakrishnan Nagar": {
                "excel_file": "server3/Chennai APP/11. Dr. Radhakrishnan Nagar.xlsx",
                "main_location": "Dr.Radhakrishnan Nagar"
            },
            "13-Kolathur": {
                "excel_file": "server3/Chennai APP/13. Kolathur.xlsx",
                "main_location": "Kolathur"
            },
            "14-Villivakkam": {
                "excel_file": "server3/Chennai APP/14. VILLIVAKKAM.xlsx",
                "main_location": "Villivakkam"
            },
            "15-Thiru-Vi-Ka-Nagar (SC)": {
                "excel_file": "server3/Chennai APP/15 Thiru Vi Ka Nagar.xlsx",
                "main_location": "Thiru-Vi-Ka-Nagar"
            },
            "16-Egmore (SC)": {
                "excel_file": "server3/Chennai APP/16. EGMORE.xlsx",
                "main_location": "Egmore"
            },
            "17-Royapuram": {
                "excel_file": "server3/Chennai APP/17. Royapuram.xlsx",
                "main_location": "Royapuram"
            },
            "18-Harbour": {
                "excel_file": "server3/Chennai APP/18. Harbour.xlsx",
                "main_location": "Harbour"
            },
            "19-Chepauk-Thiruvallikeni": {
                "excel_file": "server3/Chennai APP/19. Chepauk-Thiruvallikeni.xlsx",
                "main_location": "Chepauk-Thiruvallikeni"
            },
            "20-Thousand Lights": {
                "excel_file": "server3/Chennai APP/20. THOUSAND LIGHTS.xlsx",
                "main_location": "Thousand Lights"
            },
            "21-Anna Nagar": {
                "excel_file": "server3/Chennai APP/21. Anna Nagar.xlsx",
                "main_location": "Anna Nagar"
            },
            "22-Virugampakkam": {
                "excel_file": "server3/Chennai APP/22. Virugampakkam.xlsx",
                "main_location": "Virugampakkam"
            },
            "23-Saidapet": {
                "excel_file": "server3/Chennai APP/23. Saidapet.xlsx",
                "main_location": "Saidapet"
            },
            "24-Thiyagarayanagar": {
                "excel_file": "server3/Chennai APP/24. THIYAGARAYANAGAR.xlsx",
                "main_location": "Thiyagarayanagar"
            },
            "25-Mylapore": {
                "excel_file": "server3/Chennai APP/25. Mylapore.xlsx",
                "main_location": "Mylapore"
            },
            "26-Velachery": {
                "excel_file": "server3/Chennai APP/26. Velachery.xlsx",
                "main_location": "Velachery"
            }
        },
        "Shyam MISC": {
            "2-Ponneri (SC)": {
                "excel_file": "server3/Shyam MISC/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "35-Madurantakam (SC)": {
                "excel_file": "server3/Shyam MISC/35. MADURANTAKAM (SC).xlsx",
                "main_location": "Madurantakam"
            },
            "68-Cheyyar": {
                "excel_file": "server3/Shyam MISC/68 Cheyyur.xlsx",
                "main_location": "Cheyyar"
            },
            "78-Rishivandiyam": {
                "excel_file": "server3/Shyam MISC/78. Rishivandiyam.xlsx",
                "main_location": "Rishivandiyam"
            },
            "79-Sankarapuram": {
                "excel_file": "server3/Shyam MISC/79. Sankarapuram.xlsx",
                "main_location": "Sankarapuram"
            },
            "82-Attur (SC)": {
                "excel_file": "server3/Shyam MISC/82.Attur.xlsx",
                "main_location": "Attur"
            },
            "113-Tiruppur (North)": {
                "excel_file": "server3/Shyam MISC/113. TIRUPPUR (NORTH).xlsx",
                "main_location": "Tiruppur (North)"
            },
            "114-Tiruppur (South)": {
                "excel_file": "server3/Shyam MISC/114. TIRUPPUR (SOUTH).xlsx",
                "main_location": "Tiruppur (South)"
            },
            "227-Nanguneri": {
                "excel_file": "server3/Shyam MISC/227. Nanguneri.xlsx",
                "main_location": "Nanguneri"
            },
            "234-Killiyoor": {
                "excel_file": "server3/Shyam MISC/234. Killiyoor.xlsx",
                "main_location": "Killiyoor"
            }
        },
        "Arun APP": {
            "1-Gummidipoondi": {
                "excel_file": "server3/Arun APP/1. GUMMIDIPOONDI.xlsx",
                "main_location": "Gummidipoondi"
            },
            "2-Ponneri (SC)": {
                "excel_file": "server3/Arun APP/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "9-Madavaram": {
                "excel_file": "server3/Arun APP/9. MADAVARAM.xlsx",
                "main_location": "Madavaram"
            },
            "11-Dr.Radhakrishnan Nagar": {
                "excel_file": "server3/Arun APP/11. Dr. Radhakrishnan Nagar.xlsx",
                "main_location": "Dr.Radhakrishnan Nagar"
            },
            "18-Harbour": {
                "excel_file": "server3/Arun APP/18. Harbour.xlsx",
                "main_location": "Harbour"
            },
            "19-Chepauk-Thiruvallikeni": {
                "excel_file": "server3/Arun APP/19. Chepauk-Thiruvallikeni.xlsx",
                "main_location": "Chepauk-Thiruvallikeni"
            }
        },
        "Omni MISC 01": {
            "4-Thiruvallur": {
                "excel_file": "server3/Omni MISC/4. THIRUVALLUR.xlsx",
                "main_location": "Thiruvallur"
            },
            "34-Cheyyur (SC)": {
                "excel_file": "server3/Omni MISC/34. CHEYYUR.xlsx",
                "main_location": "Cheyyur"
            },
            "35-Madurantakam (SC)": {
                "excel_file": "server3/Omni MISC/35. MADURANTAKAM (SC).xlsx",
                "main_location": "Madurantakam"
            },
            "68-Cheyyar": {
                "excel_file": "server3/Omni MISC/68 Cheyyur.xlsx",
                "main_location": "Cheyyar"
            },
            "70-Gingee": {
                "excel_file": "server3/Omni MISC/70. Gingee.xlsx",
                "main_location": "Gingee"
            },
            "77-Ulundurpettai": {
                "excel_file": "server3/Omni MISC/77-Ulundurpettai.xlsx",
                "main_location": "Ulundurpettai"
            },
            "78-Rishivandiyam": {
                "excel_file": "server3/Omni MISC/78. Rishivandiyam.xlsx",
                "main_location": "Rishivandiyam"
            },
            "79-Sankarapuram": {
                "excel_file": "server3/Omni MISC/79. Sankarapuram.xlsx",
                "main_location": "Sankarapuram"
            },
            "82-Attur (SC)": {
                "excel_file": "server3/Omni MISC/82.Attur.xlsx",
                "main_location": "Attur"
            },
            "96-Tiruchengodu": {
                "excel_file": "server3/Omni MISC/96. Tiruchengodu.xlsx",
                "main_location": "Tiruchengodu"
            },
            "104-Bhavani": {
                "excel_file": "server3/Omni MISC/104. Bhavani.xlsx",
                "main_location": "Bhavani"
            },
            "106-Gobichettipalayam": {
                "excel_file": "server3/Omni MISC/106. GOBICHETTIPALAYAM.xlsx",
                "main_location": "Gobichettipalayam"
            },
            "113-Tiruppur (North)": {
                "excel_file": "server3/Omni MISC/113. TIRUPPUR (NORTH).xlsx",
                "main_location": "Tiruppur (North)"
            },
            "114-Tiruppur (South)": {
                "excel_file": "server3/Omni MISC/114. TIRUPPUR (SOUTH).xlsx",
                "main_location": "Tiruppur (South)"
            },
            "209-Paramakudi (SC)": {
                "excel_file": "server3/Omni MISC/209-Paramakudi.xlsx",
                "main_location": "Paramakudi"
            },
            "213-Vilathikulam": {
                "excel_file": "server3/Omni MISC/213-Vilathikulam.xlsx",
                "main_location": "Vilathikulam"
            },
            "227-Nanguneri": {
                "excel_file": "server3/Omni MISC/227. Nanguneri.xlsx",
                "main_location": "Nanguneri"
            },
            "232-Padmanabhapuram": {
                "excel_file": "server3/Omni MISC/232. Padmanabhapuram.xlsx",
                "main_location": "Padmanabhapuram"
            },
            "233-Vilavancode": {
                "excel_file": "server3/Omni MISC/233. Vilavancode.xlsx",
                "main_location": "Vilavancode"
            },
            "234-Killiyoor": {
                "excel_file": "server3/Omni MISC/234. Killiyoor.xlsx",
                "main_location": "Killiyoor"
            }
        },
        "Omni MISC 02": {
            "1-Gummidipoondi": {
                "excel_file": "server3/Omni MISC 02/1. GUMMIDIPOONDI.xlsx",
                "main_location": "Gummidipoondi"
            },
            "2-Ponneri (SC)": {
                "excel_file": "server3/Omni MISC 02/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "22-Virugampakkam": {
                "excel_file": "server3/Omni MISC 02/22. Virugampakkam.xlsx",
                "main_location": "Virugampakkam"
            },
            "60-Pappireddippatti": {
                "excel_file": "server3/Omni MISC 02/60. Pappireddipatti.xlsx",
                "main_location": "Pappireddippatti"
            },
            "61-Harur (SC)": {
                "excel_file": "server3/Omni MISC 02/61. HARUR.xlsx",
                "main_location": "Harur"
            },
            "71-Mailam": {
                "excel_file": "server3/Omni MISC 02/71. Mailam.xlsx",
                "main_location": "Mailam"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server3/Omni MISC 02/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "82-Attur (SC)": {
                "excel_file": "server3/Omni MISC 02/82.Attur.xlsx",
                "main_location": "Attur"
            },
            "87-Sankari": {
                "excel_file": "server3/Omni MISC 02/87.Sankari.xlsx",
                "main_location": "Sankari"
            },
            "102-Kangayam": {
                "excel_file": "server3/Omni MISC 02/102. KANGAYAM.xlsx",
                "main_location": "Kangayam"
            },
            "107-Bhavanisagar": {
                "excel_file": "server3/Omni MISC 02/107. Bhavanisagar.xlsx",
                "main_location": "Bhavanisagar"
            },
            "115-Palladam": {
                "excel_file": "server3/Omni MISC 02/115. Palladam.xlsx",
                "main_location": "Palladam"
            },
            "117-Kavundampalayam": {
                "excel_file": "server3/Omni MISC 02/117. Kavundampalayam.xlsx",
                "main_location": "Kavundampalayam"
            },
            "118-Coimbatore (North)": {
                "excel_file": "server3/Omni MISC 02/118. Coimbatore North.xlsx",
                "main_location": "Coimbatore (North)"
            },
            "231-Colachal": {
                "excel_file": "server3/Omni MISC 02/231. Colachal.xlsx",
                "main_location": "Colachal"
            }
        },
        "Omni MISC 03": {
            "1-Gummidipoondi": {
                "excel_file": "server3/Omni MISC 03/1. GUMMIDIPOONDI.xlsx",
                "main_location": "Gummidipoondi"
            },
            "2-Ponneri (SC)": {
                "excel_file": "server3/Omni MISC 03/2. Ponneri.xlsx",
                "main_location": "Ponneri"
            },
            "6-Avadi": {
                "excel_file": "server3/Omni MISC 03/6. AVADI.xlsx",
                "main_location": "Avadi"
            },
            "9-Madavaram": {
                "excel_file": "server3/Omni MISC 03/9. MADAVARAM.xlsx",
                "main_location": "Madavaram"
            },
            "20-Thousand Lights": {
                "excel_file": "server3/Omni MISC 03/20. THOUSAND LIGHTS.xlsx",
                "main_location": "Thousand Lights"
            },
            "22-Virugampakkam": {
                "excel_file": "server3/Omni MISC 03/22. Virugampakkam.xlsx",
                "main_location": "Virugampakkam"
            },
            "29-Sriperumbudur (SC)": {
                "excel_file": "server3/Omni MISC 03/29. SRIPERUMBUDUR.xlsx",
                "main_location": "Sriperumbudur"
            },
            "36-Uthiramerur": {
                "excel_file": "server3/Omni MISC 03/36. UTHIRAMERUR 1.xlsx",
                "main_location": "Uthiramerur"
            },
            "41-Ranipet": {
                "excel_file": "server3/Omni MISC 03/41. Ranipet.xlsx",
                "main_location": "Ranipet"
            },
            "44-Anaikattu": {
                "excel_file": "server3/Omni MISC 03/44. ANAIKATTU.xlsx",
                "main_location": "Anaikattu"
            },
            "61-Harur (SC)": {
                "excel_file": "server3/Omni MISC 03/61. HARUR.xlsx",
                "main_location": "Harur"
            },
            "71-Mailam": {
                "excel_file": "server3/Omni MISC 03/71. Mailam.xlsx",
                "main_location": "Mailam"
            },
            "72-Tindivanam (SC)": {
                "excel_file": "server3/Omni MISC 03/72. Tindivanam.xlsx",
                "main_location": "Tindivanam"
            },
            "73-Vanur (SC)": {
                "excel_file": "server3/Omni MISC 03/73. Vanur.xlsx",
                "main_location": "Vanur"
            },
            "87-Sankari": {
                "excel_file": "server3/Omni MISC 03/87.Sankari.xlsx",
                "main_location": "Sankari"
            },
            "92-Rasipuram (SC)": {
                "excel_file": "server3/Omni MISC 03/92. Rasipuram.xlsx",
                "main_location": "Rasipuram"
            },
            "94-Namakkal": {
                "excel_file": "server3/Omni MISC 03/94. Nammakal.xlsx",
                "main_location": "Namakkal"
            },
            "95-Paramathi-Velur": {
                "excel_file": "server3/Omni MISC 03/95. Paramathi velur.xlsx",
                "main_location": "Paramathi-Velur"
            },
            "102-Kangayam": {
                "excel_file": "server3/Omni MISC 03/102. KANGAYAM.xlsx",
                "main_location": "Kangayam"
            },
            "107-Bhavanisagar": {
                "excel_file": "server3/Omni MISC 03/107. Bhavanisagar.xlsx",
                "main_location": "Bhavanisagar"
            },
            "108-Udhagamandalam": {
                "excel_file": "server3/Omni MISC 03/108-Udhagamandalam.xlsx",
                "main_location": "Udhagamandalam"
            },
            "110-Coonoor": {
                "excel_file": "server3/Omni MISC 03/110 Coonoor.xlsx",
                "main_location": "Coonoor"
            },
            "115-Palladam": {
                "excel_file": "server3/Omni MISC 03/115. Palladam.xlsx",
                "main_location": "Palladam"
            },
            "117-Kavundampalayam": {
                "excel_file": "server3/Omni MISC 03/117. Kavundampalayam.xlsx",
                "main_location": "Kavundampalayam"
            },
            "118-Coimbatore (North)": {
                "excel_file": "server3/Omni MISC 03/118. Coimbatore North.xlsx",
                "main_location": "Coimbatore (North)"
            },
            "120-Coimbatore (South)": {
                "excel_file": "server3/Omni MISC 03/120. Coimbatore (South).xlsx",
                "main_location": "Coimbatore (South)"
            },
            "122-Kinathukadavu": {
                "excel_file": "server3/Omni MISC 03/122. Kinathukadavu.xlsx",
                "main_location": "Kinathukadavu"
            },
            "133-Vedasandur": {
                "excel_file": "server3/Omni MISC 03/133. Vedasandur.xlsx",
                "main_location": "Vedasandur"
            },
            "176-Pattukkottai": {
                "excel_file": "server3/Omni MISC 03/176. Pattukkottai.xlsx",
                "main_location": "Pattukkottai"
            },
            "216-Srivaikuntam": {
                "excel_file": "server3/Omni MISC 03/216. Srivaikundam.xlsx",
                "main_location": "Srivaikuntam"
            },
            "225-Ambasamudram": {
                "excel_file": "server3/Omni MISC 03/225. Ambasamudram.xlsx",
                "main_location": "Ambasamudram"
            },
            "226-Palayamkottai": {
                "excel_file": "server3/Omni MISC 03/226. Palayamkottai.xlsx",
                "main_location": "Palayamkottai"
            },
            "229-Kanniyakumari": {
                "excel_file": "server3/Omni MISC 03/229. Kanniyakumari.xlsx",
                "main_location": "Kanniyakumari"
            },
            "230-Nagercoil": {
                "excel_file": "server3/Omni MISC 03/230. Nagercoil.xlsx",
                "main_location": "Nagercoil"
            },
            "231-Colachal": {
                "excel_file": "server3/Omni MISC 03/231. Colachal.xlsx",
                "main_location": "Colachal"
            }
        },
        "Tracking": {
    "17-Royapuram": {
      "excel_file": "server1/Tracking/17. Royapuram.xlsx",
      "main_location": "Royapuram"
    },
    "22-Virugampakkam": {
      "excel_file": "server1/Tracking/22. Virugampakkam.xlsx",
      "main_location": "Virugampakkam"
    },
    "24-Thiyagarayanagar": {
      "excel_file": "server1/Tracking/24. THIYAGARAYANAGAR.xlsx",
      "main_location": "Thiyagarayanagar"
    },
    "25-Mylapore": {
      "excel_file": "server1/Tracking/25. Mylapore.xlsx",
      "main_location": "Mylapore"
    },
    "26-Velachery": {
      "excel_file": "server1/Tracking/26. Velachery.xlsx",
      "main_location": "Velachery"
    },
    "45-Kilvaithinankuppam (SC)": {
      "excel_file": "server1/Tracking/45. Kilvaithinankuppam (SC).xlsx",
      "main_location": "Kilvaithinankuppam (SC)"
    },
    "46-Gudiyattam (SC)": {
      "excel_file": "server1/Tracking/46. GUDIYATTAM.xlsx",
      "main_location": "Gudiyattam (SC)"
    },
    "55-Hosur": {
      "excel_file": "server1/Tracking/55 Hosur.xlsx",
      "main_location": "Hosur"
    },
    "62-Chengam (SC)": {
      "excel_file": "server1/Tracking/62 CHENGAM(SC).xlsx",
      "main_location": "Chengam (SC)"
    },
    "65-Kalasapakkam": {
      "excel_file": "server1/Tracking/65 KALASAPAKKAM.xlsx",
      "main_location": "Kalasapakkam"
    },
    "76-Tirukkoyilur": {
      "excel_file": "server1/Tracking/76. Tirukkoyilur.xlsx",
      "main_location": "Tirukkoyilur"
    },
    "84-Omalur": {
      "excel_file": "server1/Tracking/84. Omalur.xlsx",
      "main_location": "Omalur"
    },
    "86-Edappadi": {
      "excel_file": "server1/Tracking/86.Edappadi.xlsx",
      "main_location": "Edappadi"
    },
    "101-Dharapuram (SC)": {
      "excel_file": "server1/Tracking/101-DHARAPURAM (SC).xlsx",
      "main_location": "Dharapuram (SC)"
    },
    "119-Thondamuthur": {
      "excel_file": "server1/Tracking/119. Thondamuthur.xlsx",
      "main_location": "Thondamuthur"
    },
    "121-Singanallur": {
      "excel_file": "server1/Tracking/121. Singanallur.xlsx",
      "main_location": "Singanallur"
    },
    "126-Madathukulam": {
      "excel_file": "server1/Tracking/126. MADATHUKULAM.xlsx",
      "main_location": "Madathukulam"
    },
    "133-Vedasandur": {
      "excel_file": "server1/Tracking/133. Vedasandur.xlsx",
      "main_location": "Vedasandur"
    },
    "134-Aravakurichi": {
      "excel_file": "server1/Tracking/134. ARAVAKURICHI.xlsx",
      "main_location": "Aravakurichi"
    },
    "150-Jayankondam": {
      "excel_file": "server1/Tracking/150. Jayankondam.xlsx",
      "main_location": "Jayankondam"
    },
    "157-Bhuvanagiri": {
      "excel_file": "server1/Tracking/157. BHUVANAGIRI.xlsx",
      "main_location": "Bhuvanagiri"
    },
    "160-Sirkazhi (SC)": {
      "excel_file": "server1/Tracking/160.Sizkazhi.xlsx",
      "main_location": "Sirkazhi (SC)"
    },
    "170-Thiruvidaimarudur (SC)": {
      "excel_file": "server1/Tracking/170 Thiruvidaimarudur.xlsx",
      "main_location": "Thiruvidaimarudur (SC)"
    },
    "178-Gandharvakottai (SC)": {
      "excel_file": "server1/Tracking/178. Gandharvakottai.xlsx",
      "main_location": "Gandharvakottai (SC)"
    },
    "180-Pudukkottai": {
      "excel_file": "server1/Tracking/180. PADUKKOTTAI.xlsx",
      "main_location": "Pudukkottai"
    },
    "185-Tiruppattur": {
      "excel_file": "server1/Tracking/185. Tiruppattur.xlsx",
      "main_location": "Tiruppattur"
    },
    "186-Sivaganga": {
      "excel_file": "server1/Tracking/186. Sivaganga.xlsx",
      "main_location": "Sivaganga"
    },
    "187-Manamadurai (SC)": {
      "excel_file": "server1/Tracking/187. Manamadurai.xlsx",
      "main_location": "Manamadurai (SC)"
    },
    "208-Tiruchuli": {
      "excel_file": "server1/Tracking/208. Tiruchuli.xlsx",
      "main_location": "Tiruchuli"
    },
    "217-Ottapidaram (SC)": {
      "excel_file": "server1/Tracking/217 - Ottapidaram (SC).xlsx",
      "main_location": "Ottapidaram (SC)"
    },
    "223-Alangulam": {
      "excel_file": "server1/Tracking/223 - Alangulam.xlsx",
      "main_location": "Alangulam"
    },
    "229-Kanniyakumari": {
      "excel_file": "server1/Tracking/229. Kanniyakumari.xlsx",
      "main_location": "Kanniyakumari"
    }
        }
    }
}

# --- Geocoding Function ---
def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY,
        "region": "in"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        result = data["results"][0]
        location = result["geometry"]["location"]
        formatted_address = result["formatted_address"]
        place_id = result["place_id"]
        return {
            "formatted_address": formatted_address,
            "latitude": location["lat"],
            "longitude": location["lng"],
            "google_maps_link": f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        }
    else:
        return {
            "formatted_address": "Not found",
            "latitude": None,
            "longitude": None,
            "google_maps_link": "Not available"
        }

# --- Streamlit App ---
st.title("Polling Station Geolocation")

# Sidebar selection for server
selected_server = st.sidebar.selectbox(
    "Select Server",
    options=list(SURVEYS.keys()),
    index=0
)

# Sidebar selection for APP
selected_app = st.sidebar.selectbox(
    "Select APP",
    options=list(SURVEYS[selected_server].keys()),
    index=0
)

# Multi-selection for constituencies
available_locations = list(SURVEYS[selected_server][selected_app].keys())
selected_locations = st.sidebar.multiselect(
    "Select Assembly Constituency(s)",
    options=available_locations,
    default=[available_locations[0]] if available_locations else []
)

if not selected_locations:
    st.warning("⚠️ Please select at least one Assembly Constituency")
    st.stop()

# Create Excel writer object for multi-sheet output
excel_output = io.BytesIO()
with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
    # Process each selected location
    for selected_location in selected_locations:
        # Retrieve the Excel file path and main location for the current selection
        excel_path = SURVEYS[selected_server][selected_app][selected_location]["excel_file"]
        main_location = SURVEYS[selected_server][selected_app][selected_location]["main_location"]
        
        st.markdown(f"📍 Retrieving GPS coordinates for polling stations in **{main_location}**.")

        try:
            df = pd.read_excel(excel_path)

            if COLUMN_NAME not in df.columns:
                st.error(f"❌ Column '{COLUMN_NAME}' not found in the Excel file for {main_location}.")
                continue

            locations = df[COLUMN_NAME].dropna().unique()
            results = []

            with st.spinner(f"🔍 Geocoding addresses for {main_location}..."):
                for location in locations:
                    full_address = f"{location}, {main_location}"
                    geocode = geocode_address(full_address)

                    results.append({
                        "Original Location": location,
                        "Full Address Searched": full_address,
                        "Formatted Address (Google Maps)": geocode["formatted_address"],
                        "Latitude": geocode["latitude"],
                        "Longitude": geocode["longitude"],
                        "Google Maps Link": geocode["google_maps_link"]
                    })

            # Create DataFrame and write to Excel sheet
            result_df = pd.DataFrame(results)
            sheet_name = main_location[:31]  # Excel sheet names max 31 chars
            result_df.to_excel(writer, sheet_name=sheet_name, index=False)
            st.success(f"✅ Geocoding complete for {main_location}!")

        except FileNotFoundError:
            st.error(f"❌ Excel file not found at path: `{excel_path}`")
        except Exception as e:
            st.error(f"⚠️ An error occurred for {main_location}: {e}")

# Prepare download button for the multi-sheet Excel file
if selected_locations:
    excel_output.seek(0)
    st.download_button(
        "📥 Download All Results as Excel (Multi-Sheet)",
        data=excel_output,
        file_name="polling_stations_geocoded.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )