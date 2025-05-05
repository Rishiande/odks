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
import re
import time
import urllib.parse
import zipfile
from pydub import AudioSegment  # For audio duration

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ODK Credentials
ODK_USERNAME = os.getenv("ODK_USERNAME", "rushi@tnodk01.ii.com")
ODK_PASSWORD = os.getenv("ODK_PASSWORD", "rushi2025&")

# Define required columns globally
required_columns = [
    'Form Name', 'Date', 'Audio File', 'Audio Present', 'Location Present',
    'Name', 'Gender', 'Age', 'Age Group', 'Caste', 'Block', 'Village',
    'Submitted By', 'Phone Number', 'Interview Length (min)', 'Duration Group',
    'Latitude', 'Longitude', 'instanceID', 'SubmittedBy_AudioFile', 'Custom_Concatenated',
    'Audio Duration (MM:SS)', 'Audio Validity'  # New columns
]

# Forms structure
forms = {
    "Server 2": {
        "01 FMRS TN LandScape Survey": {
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
            "Test Landscape Survey 04-2025 copy": {"project_id": 3, "form_id": "Test Landscape Survey 04-2025 copy"}
        }
    }
}


# Fetch data from ODK
@st.cache_data(ttl=60, show_spinner="Fetching data from ODK...")
def get_odk_data(server_url, project_id, form_id):
    """Fetch all submission data from ODK Central with pagination and retries"""
    logger.info(f"Fetching data for form {form_id} in project {project_id}")
    try:
        form_url = f"{server_url}/v1/projects/{project_id}/forms/{urllib.parse.quote(form_id)}.svc"
        submissions_url = f"{form_url}/Submissions"
        all_data = []
        params = {"$top": 100}
        skip = 0
        max_retries = 3

        while True:
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        submissions_url,
                        auth=HTTPBasicAuth(ODK_USERNAME, ODK_PASSWORD),
                        headers={"Accept": "application/json"},
                        params={**params, "$skip": skip},
                        timeout=60
                    )
                    response.raise_for_status()
                    data = response.json()
                    submissions = data.get('value', [])
                    logger.info(f"Fetched {len(submissions)} submissions, skip={skip}, total so far: {len(all_data)}")
                    all_data.extend(submissions)
                    skip += len(submissions)
                    if len(submissions) < 100:
                        logger.info(f"Total submissions fetched for {form_id}: {len(all_data)}")
                        return all_data
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Retry {attempt+1}/{max_retries} for {form_id}: {str(e)}")
                        time.sleep(2 ** attempt)
                        continue
                    logger.error(f"Failed to fetch data for {form_id} after {max_retries} retries: {str(e)}")
                    raise
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"Form {form_id} not found in project {project_id} on {server_url}")
            st.warning(f"Form {form_id} not found in project {project_id}. Please verify the form ID and project ID.")
        else:
            logger.error(f"HTTP error fetching data for {form_id}: {str(e)}")
            st.error(f"Error fetching data for {form_id}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching data for {form_id}: {str(e)}")
        st.error(f"Error fetching data for {form_id}: {str(e)}")
        return []

# Parse date
def parse_date(date_str, fallback_str=None):
    """Parse various date formats and return YYYY-MM-DD"""
    if not date_str or date_str == "Unknown" or not isinstance(date_str, str):
        if fallback_str and isinstance(fallback_str, str):
            date_str = fallback_str
        else:
            logger.warning(f"Invalid date string: {date_str}, no valid fallback")
            return "Unknown"

    try:
        # Try common formats
        for fmt in ["%Y/%m/%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        # Fallback to dateutil parser
        date_str = re.sub(r'[Z+].*', '', date_str).strip()
        parsed_date = parser.parse(date_str, ignoretz=True)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.warning(f"Failed to parse date {date_str}: {str(e)}")
        if fallback_str and isinstance(fallback_str, str) and fallback_str != date_str:
            return parse_date(fallback_str, None)
        return "Unknown"

# Download and validate audio files
def download_and_validate_audio_files(server_url, project_id, form_id, audio_submissions):
    """Download audio files and validate their duration (≥ 8 minutes)"""
    zip_buffer = BytesIO()
    audio_summary = []
    MIN_DURATION_SECONDS = 8 * 60  # 8 minutes in seconds

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, (_, row) in enumerate(audio_submissions.iterrows()):
            audio_file = row['Audio File']
            instance_id = row['instanceID']
            submitted_by = row['Submitted By'] if pd.notnull(row['Submitted By']) else 'unknown'
            clean_name = row['SubmittedBy_AudioFile']

            with st.spinner(f"Processing {i+1}/{len(audio_submissions)}: {clean_name}..."):
                try:
                    audio_url = f"{server_url}/v1/projects/{project_id}/forms/{urllib.parse.quote(form_id)}/submissions/{instance_id}/attachments/{audio_file}"
                    audio_response = requests.get(
                        audio_url,
                        auth=HTTPBasicAuth(ODK_USERNAME, ODK_PASSWORD),
                        timeout=30
                    )
                    audio_response.raise_for_status()

                    # Calculate audio duration
                    audio_buffer = BytesIO(audio_response.content)
                    audio = AudioSegment.from_file(audio_buffer)
                    duration_seconds = len(audio) / 1000  # Convert milliseconds to seconds
                    duration_formatted = f"{int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}"
                    status = "Valid" if duration_seconds >= MIN_DURATION_SECONDS else "Invalid"

                    # Include in ZIP only if valid
                    if status == "Valid":
                        zip_file.writestr(clean_name, audio_response.content)

                    audio_summary.append({
                        "File": clean_name,
                        "Duration (MM:SS)": duration_formatted,
                        "Status": status,
                        "instanceID": instance_id
                    })

                except requests.exceptions.RequestException as e:
                    audio_summary.append({
                        "File": clean_name,
                        "Duration (MM:SS)": "N/A",
                        "Status": "Error",
                        "instanceID": instance_id
                    })
                    logger.error(f"Server error for {audio_file}: {str(e)}")
                except Exception as e:
                    audio_summary.append({
                        "File": clean_name,
                        "Duration (MM:SS)": "N/A",
                        "Status": "Error",
                        "instanceID": instance_id
                    })
                    logger.error(f"Unexpected error for {audio_file}: {str(e)}")

    zip_buffer.seek(0)
    summary_df = pd.DataFrame(audio_summary)
    return zip_buffer, summary_df

# Process submissions
def process_submissions(submissions, form_name, server_url, project_id, form_id):
    if not submissions:
        logger.warning("No submissions provided to process.")
        return None
    df = pd.DataFrame(submissions)
    logger.info(f"Processing {len(df)} submissions for form {form_name}")

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

    # Extract fields
    df['instanceID'] = df.get("instanceID", df.get("__id", "Unknown"))
    df['Form Name'] = form_name
    df['Submitted By'] = df.apply(lambda row: extract_group_six_field(row, 'submittedBy'), axis=1)
    df['Gender'] = df.apply(lambda row: extract_group_six_field(row, 'D3_Gender'), axis=1)
    df['Age'] = df.apply(lambda row: extract_group_six_field(row, 'D4_Age'), axis=1)
    df['Caste'] = df.apply(lambda row: extract_group_six_field(row, 'D5_Caste'), axis=1)
    df['Block'] = df.apply(lambda row: extract_group_six_field(row, 'D1_Block'), axis=1)
    df['Village'] = df.apply(lambda row: extract_group_six_field(row, 'D2_Village_GP'), axis=1)
    df['Name'] = df.apply(lambda row: extract_group_six_field(row, 'D7_Name'), axis=1)
    df['Phone Number'] = df.apply(lambda row: extract_group_six_field(row, 'D8_PhoneNumber'), axis=1)

    # Geolocation
    df['Latitude'], df['Longitude'], df['GeoError'] = zip(*df.apply(extract_geopoint_data, axis=1))
    df['Location Present'] = df.apply(lambda row: "✅" if row['Latitude'] and row['Longitude'] else "❌", axis=1)

    # Audio
    df['Audio File'] = df.get("bg_audio", "Unknown")
    df['Audio Present'] = df['Audio File'].apply(lambda x: "✅" if x and x != "Unknown" else "❌")

    # Combine Submitted By and Audio File
    df['SubmittedBy_AudioFile'] = df.apply(
        lambda row: f"{row['Submitted By']}_{row['Audio File']}".replace(" ", "_").replace("/", "_").replace("\\", "_")
        if row['Audio Present'] == "✅" and pd.notnull(row['Submitted By']) else "N/A",
        axis=1
    )
    df['Custom_Concatenated'] = df['SubmittedBy_AudioFile']

    # Log to confirm column presence
    logger.info(f"Columns after adding Custom_Concatenated: {list(df.columns)}")

    # Date and duration
    df['Date'] = "Unknown"
    df['Interview Length (min)'] = 0.0

    if 'start' in df.columns and 'end' in df.columns:
        try:
            df['submission_datetime'] = df['start'].apply(
                lambda x: pd.to_datetime(x, errors='coerce')
            )
            df['end_datetime'] = df['end'].apply(
                lambda x: pd.to_datetime(x, errors='coerce')
            )
            df['submission_datetime'] = df.apply(
                lambda row: pd.to_datetime(row['__system'].get('submissionDate'), errors='coerce')
                if pd.isna(row['submission_datetime']) and isinstance(row.get('__system'), dict)
                else row['submission_datetime'],
                axis=1
            )
            df['Date'] = df['submission_datetime'].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else "Unknown"
            )
            df['Interview Length (min)'] = df.apply(
                lambda row: (row['end_datetime'] - row['submission_datetime']).total_seconds() / 60.0
                if pd.notnull(row['submission_datetime']) and pd.notnull(row['end_datetime'])
                else 0.0,
                axis=1
            )
        except Exception as e:
            logger.error(f"Error processing dates: {str(e)}")
            st.warning(f"Date processing failed: {str(e)}")
    else:
        logger.warning(f"Missing columns: {'start' if 'start' not in df.columns else ''}, {'end' if 'end' not in df.columns else ''}")
        if '__system' in df.columns:
            df['submission_datetime'] = df['__system'].apply(
                lambda x: pd.to_datetime(x.get('submissionDate'), errors='coerce') if isinstance(x, dict) else pd.NaT
            )
            df['Date'] = df['submission_datetime'].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else "Unknown"
            )

    # Age grouping
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    if df['Age'].notna().any():
        age_bins = [18, 25, 35, 45, 55, float('inf')]
        age_labels = ['18-25', '26-35', '36-45', '46-55', '56+']
        df['Age Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, include_lowest=True, right=False)
    else:
        df['Age Group'] = None

    # Duration grouping
    duration_bins = [0, 5, 10, 15, 20, float('inf')]
    duration_labels = ['0-5 min', '5-10 min', '10-15 min', '15-20 min', '20+ min']
    df['Duration Group'] = pd.cut(df['Interview Length (min)'], bins=duration_bins, labels=duration_labels, include_lowest=True, right=False)

    # Initialize audio duration and validity columns
    df['Audio Duration (MM:SS)'] = "N/A"
    df['Audio Validity'] = "N/A"

    # Select columns
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            logger.warning(f"Column {col} was missing, added with None values")
    df = df[required_columns]
    logger.info(f"Final DataFrame columns: {list(df.columns)}")
    return df

# Create Excel for project
def create_excel_for_project(server_name, project_name, forms_data):
    """Create Excel file for a specific project"""
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        for form_name, form_info in forms_data.items():
            server_url = "https://tnodk01.indiaintentions.com" if server_name == "Server 1" else "https://tnodk02.indiaintentions.com" if server_name == "Server 2" else "https://tnodk03.indiaintentions.com"
            raw_data = get_odk_data(server_url, form_info['project_id'], form_info['form_id'])

            if not raw_data:
                continue

            df = process_submissions(raw_data, form_name, server_url, form_info['project_id'], form_info['form_id'])
            if df is None or df.empty:
                continue

            # Use the entire DataFrame without date filtering
            filtered_df = df

            # Add validation column
            filtered_df['Is Valid'] = filtered_df.apply(
                lambda row: row['Audio Present'] == "✅" and row['Location Present'] == "✅" and row['Audio Validity'] == "Valid",
                axis=1
            )

            # Calculate stats
            total_submissions = len(filtered_df)
            total_valid = filtered_df['Is Valid'].sum()
            total_invalid = total_submissions - total_valid
            validation_rate = (total_valid / total_submissions * 100) if total_submissions > 0 else 0

            # Submissions by person with validation
            submitter_stats = filtered_df.groupby('Submitted By').agg(
                Submission_Count=('Submitted By', 'size'),
                Valid_Count=('Is Valid', 'sum'),
                Avg_Length=('Interview Length (min)', 'mean')
            ).reset_index()
            submitter_stats['Invalid_Count'] = submitter_stats['Submission_Count'] - submitter_stats['Valid_Count']
            submitter_stats['Validation_Rate'] = (submitter_stats['Valid_Count'] / submitter_stats['Submission_Count'] * 100).round(1)
            submitter_stats['Avg_Length'] = submitter_stats['Avg_Length'].round(2)

            # Create summary sheet
            submitter_stats.to_excel(writer, index=False, sheet_name=f"{form_name[:28]}_Stats")

            # Original data with validation
            summary_row = pd.DataFrame([{
                'Form Name': 'SUMMARY STATS',
                'Date': '',
                'Audio File': '',
                'Audio Present': '',
                'Location Present': '',
                'Name': '',
                'Gender': '',
                'Age': '',
                'Age Group': '',
                'Caste': '',
                'Block': '',
                'Village': '',
                'Submitted By': f'Total: {total_submissions} | Valid: {total_valid} ({validation_rate:.1f}%)',
                'Phone Number': '',
                'Interview Length (min)': '',
                'Duration Group': '',
                'Latitude': '',
                'Longitude': '',
                'instanceID': '',
                'SubmittedBy_AudioFile': '',
                'Custom_Concatenated': '',
                'Audio Duration (MM:SS)': '',
                'Audio Validity': '',
                'Is Valid': ''
            }])
            final_df = pd.concat([summary_row, filtered_df], ignore_index=True)
            final_df.to_excel(writer, index=False, sheet_name=form_name[:31])

            workbook = writer.book
            worksheet = writer.sheets[form_name[:31]]
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            for col_num, value in enumerate(final_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            summary_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FFFF00'
            })
            worksheet.set_row(1, None, summary_format)
            for i, col in enumerate(final_df.columns):
                max_len = max(
                    final_df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)

    return excel_buffer

# Streamlit App
st.set_page_config(page_title="server2 Data Filtering", layout="wide")
st.title("📊 ODK Form Data Processor - Multi-Project")

st.markdown("""
<style>
    .stDataFrame {width: 100% !important;}
    .submission-stats {background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;}
    .stat-card {background-color: white; border-radius: 5px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    .valid-badge {background-color: #4CAF50; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px;}
    .invalid-badge {background-color: #F44336; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px;}
</style>
""", unsafe_allow_html=True)

# Main UI
st.sidebar.header("Data Controls")

selected_server = st.sidebar.selectbox("Select Server", list(forms.keys()), key="server_selectbox")

if selected_server:
    projects = forms[selected_server]
    selected_project = st.sidebar.selectbox("Select Project", list(projects.keys()), key="project_selectbox")

    if selected_project:
        project_forms = projects[selected_project]

        if st.sidebar.button("Download All Forms in Project", key="download_project_button"):
            with st.spinner(f"Processing {selected_project}..."):
                excel_buffer = create_excel_for_project(selected_server, selected_project, project_forms)
                excel_buffer.seek(0)
                st.sidebar.download_button(
                    label="⬇️ Download Project Excel",
                    data=excel_buffer,
                    file_name=f"{selected_project.replace(' ', '_')}_submissions.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_project_excel"
                )

        selected_form = st.sidebar.selectbox("Select Form", list(project_forms.keys()), key="form_selectbox")
        if selected_form:
            form_info = project_forms[selected_form]
            server_url = "https://tnodk01.indiaintentions.com" if selected_server == "Server 1" else "https://tnodk02.indiaintentions.com" if selected_server == "Server 2" else "https://tnodk03.indiaintentions.com"

            # Load data from ODK
            with st.spinner(f"Loading {selected_form} data from ODK..."):
                raw_data = get_odk_data(server_url, form_info['project_id'], form_info['form_id'])
                if raw_data:
                    df = process_submissions(raw_data, selected_form, server_url, form_info['project_id'], form_info['form_id'])
                    if df is not None and not df.empty:
                        st.session_state[f'data_{selected_form}'] = df
                        logger.info(f"Stored new DataFrame in session state with columns: {list(df.columns)}")
                    else:
                        logger.warning(f"No valid data processed for {selected_form}")

            # Display data
            if df is not None and not df.empty:
                if 'Date' not in df.columns:
                    st.error("The 'Date' column is missing in the processed data.")
                    logger.error("Missing 'Date' column in DataFrame")
                    st.stop()

                # Use the entire DataFrame without date filtering
                filtered_df = df
                logger.info(f"DataFrame columns for {selected_form}: {list(filtered_df.columns)}")

                if not filtered_df.empty:
                    # Process audio files for duration validation
                    audio_submissions = filtered_df[filtered_df['Audio Present'] == "✅"]
                    audio_summary_df = pd.DataFrame()
                    zip_buffer = None

                    if not audio_submissions.empty and st.button("🚀 Process and Download Valid Audio Files", key="download_audio_button"):
                        with st.spinner(f"Processing audio files for {selected_form}..."):
                            zip_buffer, audio_summary_df = download_and_validate_audio_files(
                                server_url, form_info['project_id'], form_info['form_id'], audio_submissions
                            )

                        if zip_buffer.getbuffer().nbytes > 0:
                            st.success(f"🎉 Processing completed! Only valid audio files (≥ 8 min) included in ZIP.")
                            st.download_button(
                                label=f"⬇️ Download Valid Audio Files (ZIP)",
                                data=zip_buffer,
                                file_name=f"{selected_form.replace(' ', '_')}_VALID_AUDIOS.zip",
                                mime="application/zip",
                                key="download_audio_zip"
                            )
                        else:
                            st.error("No valid audio files were found or processed.")

                        # Update filtered_df with audio duration and validity
                        if not audio_summary_df.empty:
                            audio_summary_df.set_index('instanceID', inplace=True)
                            filtered_df = filtered_df.copy()
                            filtered_df['Audio Duration (MM:SS)'] = filtered_df['instanceID'].map(
                                audio_summary_df['Duration (MM:SS)']
                            ).fillna("N/A")
                            filtered_df['Audio Validity'] = filtered_df['instanceID'].map(
                                audio_summary_df['Status']
                            ).fillna("N/A")

                    # Add validation column
                    filtered_df['Is Valid'] = filtered_df.apply(
                        lambda row: row['Audio Present'] == "✅" and row['Location Present'] == "✅" and row['Audio Validity'] == "Valid",
                        axis=1
                    )

                    # Calculate validation stats
                    total_submissions = len(filtered_df)
                    total_valid = filtered_df['Is Valid'].sum()
                    total_invalid = total_submissions - total_valid
                    validation_rate = (total_valid / total_submissions * 100) if total_submissions > 0 else 0

                    # Submissions by person with validation
                    submitter_stats = filtered_df.groupby('Submitted By').agg(
                        Submission_Count=('Submitted By', 'size'),
                        Valid_Count=('Is Valid', 'sum'),
                        Avg_Length=('Interview Length (min)', 'mean')
                    ).reset_index()
                    submitter_stats['Invalid_Count'] = submitter_stats['Submission_Count'] - submitter_stats['Valid_Count']
                    submitter_stats['Validation_Rate'] = (submitter_stats['Valid_Count'] / submitter_stats['Submission_Count'] * 100).round(1)
                    submitter_stats['Avg_Length'] = submitter_stats['Avg_Length'].round(2)

                    # Display validation summary
                    st.markdown("""
                    <div class="submission-stats">
                        <h3>📊 Submission Validation Summary</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"""
                        <div class="stat-card">
                            <h4>✅ Valid Submissions</h4>
                            <p style="font-size: 24px; font-weight: bold; color: #4CAF50;">{total_valid}</p>
                            <p>{validation_rate:.1f}% of total</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="stat-card">
                            <h4>❌ Invalid Submissions</h4>
                            <p style="font-size: 24px; font-weight: bold; color: #F44336;">{total_invalid}</p>
                            <p>{(100 - validation_rate):.1f}% of total</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        avg_length = filtered_df['Interview Length (min)'].mean()
                        st.markdown(f"""
                        <div class="stat-card">
                            <h4>⏱️ Average Length</h4>
                            <p style="font-size: 24px; font-weight: bold; color: #2196F3;">{avg_length:.1f} min</p>
                            <p>across all submissions</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Submissions by person
                    st.markdown("""
                    <div class="submission-stats">
                        <h3>👥 Submissions by Person</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    st.dataframe(
                        submitter_stats.sort_values('Submission_Count', ascending=False),
                        use_container_width=True,
                        hide_index=True,
                        column_order=['Submitted By', 'Submission_Count', 'Valid_Count', 'Invalid_Count', 'Validation_Rate', 'Avg_Length'],
                        column_config={
                            'Submitted By': 'Submitted By',
                            'Submission_Count': st.column_config.NumberColumn('Total Submissions'),
                            'Valid_Count': st.column_config.NumberColumn('✅ Valid'),
                            'Invalid_Count': st.column_config.NumberColumn('❌ Invalid'),
                            'Validation_Rate': st.column_config.NumberColumn('Validation %', format="%.1f%%"),
                            'Avg_Length': st.column_config.NumberColumn('Avg Length (min)')
                        }
                    )

                    # Audio files summary
                    if not audio_summary_df.empty:
                        st.markdown("""
                        <div class="submission-stats">
                            <h3>🎵 Audio Files Summary</h3>
                            <p>Valid: Duration ≥ 8 minutes, Invalid: Duration < 8 minutes</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.dataframe(
                            audio_summary_df[['File', 'Duration (MM:SS)', 'Status']],
                            use_container_width=True,
                            column_config={
                                'File': 'Audio File',
                                'Duration (MM:SS)': 'Duration',
                                'Status': st.column_config.TextColumn('Validity')
                            }
                        )

                    # Main data display
                    st.markdown(f"""
                    <div class="submission-stats">
                        <h3>📋 Form Data - {selected_form}</h3>
                        <p><strong>Total Submissions:</strong> {total_submissions} |
                        <strong>Valid Submissions:</strong> <span class="valid-badge">{total_valid}</span> |
                        <strong>Invalid Submissions:</strong> <span class="invalid-badge">{total_invalid}</span></p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display the main data with validation column
                    display_columns = required_columns + ['Is Valid']
                    display_df = filtered_df[display_columns]
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        column_config={
                            'Is Valid': st.column_config.CheckboxColumn(
                                "Is Valid",
                                help="Whether the submission has both audio, location data, and valid audio duration (≥ 8 min)",
                                default=False,
                            ),
                            'Audio Validity': st.column_config.TextColumn(
                                "Audio Validity",
                                help="Valid if audio duration is ≥ 8 minutes, Invalid if < 8 minutes"
                            )
                        }
                    )

                    # Prepare Excel with validation data
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        # Write validation summary
                        validation_summary = pd.DataFrame({
                            'Metric': ['Total Submissions', 'Valid Submissions', 'Invalid Submissions', 'Validation Rate'],
                            'Value': [total_submissions, total_valid, total_invalid, f"{validation_rate:.1f}%"]
                        })
                        validation_summary.to_excel(writer, index=False, sheet_name="Validation Summary")

                        # Write audio summary
                        if not audio_summary_df.empty:
                            audio_summary_df[['File', 'Duration (MM:SS)', 'Status']].to_excel(
                                writer, index=False, sheet_name="Audio Summary"
                            )

                        # Write submitter stats
                        submitter_stats.to_excel(writer, index=False, sheet_name="Submissions by Person")

                        # Write data sheet
                        summary_row = pd.DataFrame([{
                            'Form Name': 'SUMMARY STATS',
                            'Date': '',
                            'Audio File': '',
                            'Audio Present': '',
                            'Location Present': '',
                            'Name': '',
                            'Gender': '',
                            'Age': '',
                            'Age Group': '',
                            'Caste': '',
                            'Block': '',
                            'Village': '',
                            'Submitted By': f'Total: {total_submissions} | Valid: {total_valid} ({validation_rate:.1f}%)',
                            'Phone Number': '',
                            'Interview Length (min)': '',
                            'Duration Group': '',
                            'Latitude': '',
                            'Longitude': '',
                            'instanceID': '',
                            'SubmittedBy_AudioFile': '',
                            'Custom_Concatenated': '',
                            'Audio Duration (MM:SS)': '',
                            'Audio Validity': '',
                            'Is Valid': ''
                        }])
                        final_df = pd.concat([summary_row, filtered_df], ignore_index=True)
                        final_df.to_excel(writer, index=False, sheet_name="Form Data")

                        # Formatting
                        workbook = writer.book

                        # Format validation summary
                        worksheet_validation = writer.sheets["Validation Summary"]
                        header_format = workbook.add_format({
                            'bold': True,
                            'text_wrap': True,
                            'valign': 'top',
                            'fg_color': '#D7E4BC',
                            'border': 1
                        })
                        for col_num, value in enumerate(validation_summary.columns.values):
                            worksheet_validation.write(0, col_num, value, header_format)

                        # Format audio summary
                        if not audio_summary_df.empty:
                            worksheet_audio = writer.sheets["Audio Summary"]
                            for col_num, value in enumerate(audio_summary_df[['File', 'Duration (MM:SS)', 'Status']].columns.values):
                                worksheet_audio.write(0, col_num, value, header_format)

                        # Format submitter stats
                        worksheet_submitters = writer.sheets["Submissions by Person"]
                        for col_num, value in enumerate(submitter_stats.columns.values):
                            worksheet_submitters.write(0, col_num, value, header_format)

                        # Format data sheet
                        worksheet_data = writer.sheets["Form Data"]
                        for col_num, value in enumerate(final_df.columns.values):
                            worksheet_data.write(0, col_num, value, header_format)
                        summary_format = workbook.add_format({
                            'bold': True,
                            'bg_color': '#FFFF00'
                        })
                        worksheet_data.set_row(1, None, summary_format)

                        # Auto-adjust column widths
                        for worksheet in [worksheet_validation, worksheet_submitters, worksheet_data] + ([writer.sheets["Audio Summary"]] if not audio_summary_df.empty else []):
                            for i, col in enumerate(validation_summary.columns if worksheet == worksheet_validation
                                              else submitter_stats.columns if worksheet == worksheet_submitters
                                              else audio_summary_df[['File', 'Duration (MM:SS)', 'Status']].columns if worksheet == writer.sheets.get("Audio Summary")
                                              else final_df.columns):
                                max_len = max(
                                    (validation_summary[col] if worksheet == worksheet_validation
                                     else submitter_stats[col] if worksheet == worksheet_submitters
                                     else audio_summary_df[col] if worksheet == writer.sheets.get("Audio Summary")
                                     else final_df[col]).astype(str).map(len).max(),
                                    len(col)
                                ) + 2
                                worksheet.set_column(i, i, max_len)

                    excel_buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download with Validation Data",
                        data=excel_buffer,
                        file_name=f"{selected_form.replace(' ', '_')}_submissions_with_validation.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_form_excel"
                    )
                else:
                    st.warning(f"No submissions found for {selected_form}.")
            else:
                st.warning(f"No data found for {selected_form}")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.markdown("""
    <style>
        .sidebar .sidebar-content {
            width: 300px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("ODK Data Processor")
    st.sidebar.markdown("""
    This application processes and visualizes data from ODK Central.
    - Select a server, project, and form to view all submissions.
    - Download data as Excel files with validation information.
    - Download valid audio files (≥ 8 minutes) as a ZIP.
    """)
