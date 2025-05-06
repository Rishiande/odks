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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ODK Configuration
ODK_CONFIG = {
    "BASE_URL": "https://tnodk01.indiaintentions.com",
    "USERNAME": os.getenv("ODK_USERNAME", "rushi@tnodk01.ii.com"),
    "PASSWORD": os.getenv("ODK_PASSWORD", "rushi2025&")
}

# Forms structure - Sorted in ascending order
FORMS = {
    "Server 1": {
        "03 BK TN AC Landscape": {
            "55-Hosur": {"project_id": 5, "form_id": "55-Hosur Landscape Survey 04-2025"},
            "63-Tiruvannamalai": {"project_id": 5, "form_id": "63-Tiruvannamalai Landscape Survey 04-2025"},
            "64-Kilpennathur": {"project_id": 5, "form_id": "64-KilpennathurLandscape Survey 04-2025"},
            "67-Arani": {"project_id": 5, "form_id": "67-Arani Landscape Survey 04-2025"},
            "95-Paramathi-Velur": {"project_id": 5, "form_id": "95-Paramathi-Velur Landscape Survey 04-2025"},
            "100-Modakkurichi": {"project_id": 5, "form_id": "100-Modakkurichi Landscape Survey 04-2025"},
            "110-Coonoor": {"project_id": 5, "form_id": "110-Coonoor Landscape Survey 04-2025"},
            "131-Natham": {"project_id": 5, "form_id": "131-Natham Landscape Survey 04-2025"},
            "133-Vedasandur": {"project_id": 5, "form_id": "133-Vedasandur Landscape Survey 05-2025"},
            "148-Kunnam": {"project_id": 5, "form_id": "148-Kunnam Landscape Survey 04-2025"},
            "149-Ariyalur": {"project_id": 5, "form_id": "149-Ariyalur Landscape Survey 04-2025"},
            "152-Vriddhachalam": {"project_id": 5, "form_id": "152-Vriddhachalam Landscape Survey 04-2025"},
            "197-Usilampatti": {"project_id": 5, "form_id": "197-Usilampatti Landscape Survey 04-2025"},
            "223-Alangulam": {"project_id": 5, "form_id": "223-Alangulam Landscape Survey 04-2025"},
            "224-Tirunelveli": {"project_id": 5, "form_id": "224-Tirunelveli Landscape Survey 04-2025"}
        },
        "04 TN AC Landscape": {
            "37-Kancheepuram": {"project_id": 6, "form_id": "37-Kancheepuram Landscape Survey 05-2025"},
            "151-Tittakudi (SC)": {"project_id": 6, "form_id": "151-Tittakudi (SC) Landscape Survey 05-2025"},
            "152-Vriddhachalam": {"project_id": 6, "form_id": "152-Vriddhachalam 05-2025"},
            "153-Neyveli": {"project_id": 6, "form_id": "153-Neyveli Landscape Survey 05-2025"},
            "156-Kurinjipadi": {"project_id": 6, "form_id": "156-Kurinjipadi Landscape Survey 05-2025"},
            "159-Kattumannarkoil (SC)": {"project_id": 6, "form_id": "159-Kattumannarkoil (SC) Landscape Survey 04-2025"},
            "181-Thirumayam": {"project_id": 6, "form_id": "181-Thirumayam Landscape Survey 04-2025"},
            "183-Aranthangi": {"project_id": 6, "form_id": "183-Aranthangi Landscape Survey 04-2025"},
            "204-Sattur": {"project_id": 6, "form_id": "204-Sattur Landscape Survey 05-2025"}
        },
        "BK TN AC Landscape": {
            "3-Thirutthani": {"project_id": 4, "form_id": "3-Thirutthani Landscape Survey 04-2025"},
            "12-Perambur": {"project_id": 4, "form_id": "12-Perambur Landscape Survey 04-2025"},
            "38-Arakkonam": {"project_id": 4, "form_id": "38-Arakkonam (SC) Landscape Survey 04-2025"},
            "39-Sholingur": {"project_id": 4, "form_id": "39-Sholingur Landscape Survey 04-2025"},
            "56-Thalli": {"project_id": 4, "form_id": "56-Thalli Landscape Survey 04-2025"},
            "103-Perundurai": {"project_id": 4, "form_id": "103-Perundurai Landscape Survey 04-2025"},
            "109-Gudalur (SC)": {"project_id": 4, "form_id": "109-Gudalur (SC) Landscape Survey 04-2025"},
            "118-Coimbatore North": {"project_id": 4, "form_id": "118-Coimbatore North Landscape Survey 04-2025"},
            "132-Dindigul": {"project_id": 4, "form_id": "132 Dindigul Landscape Survey 04-2025"},
            "135-Karur": {"project_id": 4, "form_id": "135-Karur Landscape Survey 04-2025"},
            "136-Krishnarayapuram": {"project_id": 4, "form_id": "136-Krishnarayapuram (SC) Landscape Survey 04-2025"},
            "137-Kulithalai": {"project_id": 4, "form_id": "137-Kulithalai Landscape Survey 04-2025"},
            "138-Manapparai": {"project_id": 4, "form_id": "138-Manapparai Landscape Survey 04-2025"},
            "145-Musiri": {"project_id": 4, "form_id": "145-Musiri Landscape Survey 04-2025"},
            "146-Thuraiyur": {"project_id": 4, "form_id": "146. Thuraiyur (SC) Landscape Survey 04-2025"},
            "150-Jayankondam": {"project_id": 4, "form_id": "150-Jayankondam Landscape Survey 04-2025"},
            "155-Cuddalore": {"project_id": 4, "form_id": "155-Cuddalore Landscape Survey 04-2025"},
            "158-Chidambaram": {"project_id": 4, "form_id": "158-Chidambaram Landscape Survey 04-2025"},
            "171-Kumbakonam": {"project_id": 4, "form_id": "171-Kumbakonam Landscape Survey 04-2025"},
            "180-Pudukkottai": {"project_id": 4, "form_id": "180-Pudukkottai Landscape Survey 04-2025"},
            "189-Madurai East": {"project_id": 4, "form_id": "189-Madurai East Landscape Survey 04-2025"},
            "198-Andipatti": {"project_id": 4, "form_id": "198-Andipatti Landscape Survey 04-2025"},
            "199-Periyakulam": {"project_id": 4, "form_id": "199. Periyakulam (SC) Landscape Survey 04-2025"},
            "201-Cumbum": {"project_id": 4, "form_id": "201-Cumbum Landscape Survey 04-2025"}
        },
        "TN Master": {
            "Master Landscape Survey 04-2025 ODK XLSForm": {
                "project_id": 3,
                "form_id": "Master Landscape Survey 04-2025 ODK XLSForm"
            }
        }
    }
}

def fetch_all_submissions(project_id, form_id):
    """Fetch all submissions without date filtering"""
    url = f"{ODK_CONFIG['BASE_URL']}/v1/projects/{project_id}/forms/{urllib.parse.quote(form_id)}.svc/Submissions"
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

def process_submissions(submissions, form_name, project_id, form_id):
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
    
    # Location data - updated with more robust handling
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
    
    # Required columns
    required_columns = [
        'Form Name', 'Date', 'Audio File', 'Audio Present', 'Location Present',
        'Name', 'Gender', 'Age', 'Age Group', 'Caste', 'Block', 'Village',
        'Submitted By', 'Phone Number', 'Interview Length (min)', 'Duration Group',
        'Latitude', 'Longitude', 'instanceID', 'SubmittedBy_AudioFile', 'Custom_Concatenated',
        'Audio Duration (MM:SS)', 'Audio Validity', 'Submission_Order'
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
    selected_server = st.sidebar.selectbox("Server", list(FORMS.keys()))
    selected_project = st.sidebar.selectbox("Project", list(FORMS[selected_server].keys()))
    selected_form = st.sidebar.selectbox("Form", list(FORMS[selected_server][selected_project].keys()))
    
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
                form_info['form_id']
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
                        f"forms/{form_info['form_id']}/submissions/{row['instanceID']}/"
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
