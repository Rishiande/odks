import requests
from requests.auth import HTTPBasicAuth
import streamlit as st
import pandas as pd
import io
import zipfile
from datetime import datetime
import json
import logging
import urllib.parse
from dateutil import parser
from urllib.parse import quote 

# Streamlit Setup
st.set_page_config(page_title="ODK Audio Test Downloader", layout="centered")
st.title("🔊 ODK Audio Test Download (All Files from Each Form)")

# Set up logging
logger = logging.getLogger(__name__)

# ODK Configurations for each server
ODK_CONFIGS = {
    "Server 1": {
        "ODK_USERNAME": "anil@iiodk.com",
        "ODK_PASSWORD": "FormAdmin123!",
        "BASE_URL": "https://tnodk04.indiaintentions.com"
    }
}

forms = {
    "Server 1": {
        "Delta Tracker Mayiladuthurai": {
            "160-Sirkazhi (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 10, "form_id": "160-Sirkazhi (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "161-Mayiladuthurai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 10, "form_id": "161-Mayiladuthurai Tracking Survey 08-2025 ODK XLSForm"},
            "162-Poompuhar Tracking Survey 08-2025 ODK XLSForm": {"project_id": 10, "form_id": "162-Poompuhar Tracking Survey 08-2025 ODK XLSForm"}
        },
        "Delta Tracking Pudukkottai": {
            "178-Gandharvakottai (SC) Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "178-Gandharvakottai (SC) Tracking Survey 08-2025 ODK XLSForm"},
            "179-Viralimalai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "179-Viralimalai Tracking Survey 08-2025 ODK XLSForm"},
            "180-Pudukkottai Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "180-Pudukkottai Tracking Survey 08-2025 ODK XLSForm"},
            "181-Thirumayam Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "181-Thirumayam Tracking Survey 08-2025 ODK XLSForm"},
            "182-Alangudi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "182-Alangudi Tracking Survey 08-2025 ODK XLSForm"},
            "183-Aranthangi Tracking Survey 08-2025 ODK XLSForm": {"project_id": 8, "form_id": "183-Aranthangi racking Survey 08-2025 ODK XLSForm",}
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
    """Download audio files from submissions and return as zip data bytes"""
    config = ODK_CONFIGS[selected_server]
    zip_buffer = io.BytesIO()
    download_status = []
    successful_downloads = 0

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
                        successful_downloads += 1
                        download_status.append(f"✅ Downloaded: {clean_name}")

                    except requests.exceptions.RequestException as e:
                        download_status.append(f"❌ Server error for {audio_file}: {str(e)}")
                    except Exception as e:
                        download_status.append(f"❌ Unexpected error for {audio_file}: {str(e)}")

        # Check if zip has content before returning
        if successful_downloads == 0:
            zip_buffer.close()
            return None, download_status

        # Get the zip data as bytes before closing buffer
        zip_data = zip_buffer.getvalue()
        zip_buffer.close()
        return zip_data, download_status

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
    total_files_added = 0
    
    try:
        with zipfile.ZipFile(zip_buffer_all, "w", zipfile.ZIP_DEFLATED) as zip_file_all:
            for project_name, form_name, zip_data, status_list in audio_files_data:
                if zip_data and len(zip_data) > 0:
                    # Create a temporary BytesIO from the zip data bytes
                    temp_buffer = io.BytesIO(zip_data)
                    try:
                        with zipfile.ZipFile(temp_buffer, 'r') as temp_zip:
                            for file_info in temp_zip.namelist():
                                file_content = temp_zip.read(file_info)
                                # Create nested folder structure
                                nested_path = f"{project_name.replace(' ', '_')}/{form_name.replace(' ', '_')}/{file_info}"
                                zip_file_all.writestr(nested_path, file_content)
                                total_files_added += 1
                    except zipfile.BadZipFile:
                        st.warning(f"Skipping corrupted zip data for {project_name}/{form_name}")
                    except Exception as e:
                        st.warning(f"Error processing zip data for {project_name}/{form_name}: {str(e)}")
                    finally:
                        # Always close the temporary buffer
                        temp_buffer.close()
                
                download_status_all.extend(status_list)
        
        # Check if the combined zip has content
        if total_files_added == 0:
            zip_buffer_all.close()
            return None, download_status_all
        
        # Get the zip data as bytes before closing
        zip_data = zip_buffer_all.getvalue()
        zip_buffer_all.close()
        return zip_data, download_status_all
        
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
                                            zip_data, download_status = download_audio_files(
                                                selected_server, form_name,
                                                project_id, form_id, audio_submissions
                                            )

                                            if zip_data:
                                                audio_files_data.append((project_name, form_name, zip_data, download_status))
                                                st.success(f"✅ Processed {form_name} in {project_name} - {len(audio_submissions)} audio files found, {len([s for s in download_status if '✅' in s])} downloaded")
                                            else:
                                                st.warning(f"⚠️ No files downloaded for {form_name} in {project_name}")
                                                audio_files_data.append((project_name, form_name, None, download_status))
                                        else:
                                            st.warning(f"⚠️ No audio files found for {form_name} in {project_name}")
                                    else:
                                        st.warning(f"⚠️ No submissions found for {form_name} in {project_name}")

                    # Create combined ZIP file
                    if audio_files_data:
                        combined_zip_data, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                        
                        if combined_zip_data:
                            st.success(f"🎉 All projects and forms processed successfully for {selected_server}!")
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            file_name = f"{selected_server.replace(' ', '_')}_ALL_PROJECTS_AUDIOS_{timestamp}{date_suffix}.zip"
                            
                            st.download_button(
                                label=f"⬇️ Download All Audio Files for {selected_server} (ZIP)",
                                data=combined_zip_data,
                                file_name=file_name,
                                mime="application/zip"
                            )

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
                                                zip_data, download_status = download_audio_files(
                                                    selected_server, form_name,
                                                    project_id, form_id, audio_submissions
                                                )

                                                if zip_data:
                                                    audio_files_data.append((project_name, form_name, zip_data, download_status))
                                                    st.success(f"✅ Processed {form_name} in {project_name} - {len(audio_submissions)} audio files found, {len([s for s in download_status if '✅' in s])} downloaded")
                                                else:
                                                    st.warning(f"⚠️ No files downloaded for {form_name} in {project_name}")
                                                    audio_files_data.append((project_name, form_name, None, download_status))
                                            else:
                                                st.warning(f"⚠️ No audio files found for {form_name} in {project_name}")
                                        else:
                                            st.warning(f"⚠️ No submissions found for {form_name} in {project_name}")

                        # Create combined ZIP file
                        if audio_files_data:
                            combined_zip_data, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                            
                            if combined_zip_data:
                                st.success(f"🎉 Selected projects processed successfully for {selected_server}!")
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                selected_projects_str = "_".join([p.replace(' ', '_') for p in selected_projects])
                                file_name = f"{selected_server.replace(' ', '_')}_SELECTED_PROJECTS_{selected_projects_str}_AUDIOS_{timestamp}{date_suffix}.zip"
                                
                                st.download_button(
                                    label=f"⬇️ Download Selected Projects Audio Files (ZIP)",
                                    data=combined_zip_data,
                                    file_name=file_name,
                                    mime="application/zip"
                                )

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
                                            zip_data, download_status = download_audio_files(
                                                selected_server, form_name,
                                                project_id, form_id, audio_submissions
                                            )

                                            if zip_data:
                                                audio_files_data.append((selected_project, form_name, zip_data, download_status))
                                                st.success(f"✅ Processed {form_name} in {selected_project} - {len(audio_submissions)} audio files found, {len([s for s in download_status if '✅' in s])} downloaded")
                                            else:
                                                st.warning(f"⚠️ No files downloaded for {form_name} in {selected_project}")
                                                audio_files_data.append((selected_project, form_name, None, download_status))
                                        else:
                                            st.warning(f"⚠️ No audio files found for {form_name} in {selected_project}")
                                    else:
                                        st.warning(f"⚠️ No submissions found for {form_name} in {selected_project}")

                            # Create combined ZIP file
                            if audio_files_data:
                                combined_zip_data, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                                
                                if combined_zip_data:
                                    st.success(f"🎉 Selected forms from {selected_project} processed successfully!")
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    selected_forms_str = "_".join([f.replace(' ', '_') for f in selected_forms])
                                    file_name = f"{selected_server.replace(' ', '_')}_{selected_project.replace(' ', '_')}_SELECTED_FORMS_{selected_forms_str}_AUDIOS_{timestamp}{date_suffix}.zip"
                                    
                                    st.download_button(
                                        label=f"⬇️ Download Selected Forms from {selected_project} (ZIP)",
                                        data=combined_zip_data,
                                        file_name=file_name,
                                        mime="application/zip"
                                    )

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
                                        zip_data, download_status = download_audio_files(
                                            selected_server, form_name,
                                            project_id, form_id, audio_submissions
                                        )

                                        if zip_data:
                                            audio_files_data.append((project_name, form_name, zip_data, download_status))
                                            st.success(f"✅ Processed {form_name} in {project_name} - {len(audio_submissions)} audio files found, {len([s for s in download_status if '✅' in s])} downloaded")
                                        else:
                                            st.warning(f"⚠️ No files downloaded for {form_name} in {project_name}")
                                            audio_files_data.append((project_name, form_name, None, download_status))
                                    else:
                                        st.warning(f"⚠️ No audio files found for {form_name} in {project_name}")
                                else:
                                    st.warning(f"⚠️ No submissions found for {form_name} in {project_name}")

                        # Create combined ZIP file
                        if audio_files_data:
                            combined_zip_data, combined_status = create_combined_zip(audio_files_data, selected_server, date_suffix)
                            
                            if combined_zip_data:
                                st.success(f"🎉 Selected forms processed successfully!")
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                file_name = f"{selected_server.replace(' ', '_')}_SELECTED_FORMS_AUDIOS_{timestamp}{date_suffix}.zip"
                                
                                st.download_button(
                                    label=f"⬇️ Download Selected Forms Audio Files (ZIP)",
                                    data=combined_zip_data,
                                    file_name=file_name,
                                    mime="application/zip"
                                )

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
                                zip_data, download_status = download_audio_files(
                                    selected_server, form_name,
                                    project_id, form_id, audio_submissions
                                )

                                if zip_data is None:
                                    st.error("No files were downloaded. Check the status messages below.")
                                else:
                                    successful_downloads = len([s for s in download_status if '✅' in s])
                                    st.success(f"🎉 Download completed for {form_name} in {project_name}! {successful_downloads}/{len(audio_submissions)} files downloaded")
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    file_name = f"{project_name.replace(' ', '_')}_{form_name.replace(' ', '_')}_AUDIOS_{timestamp}{date_suffix}.zip"
                                    
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
