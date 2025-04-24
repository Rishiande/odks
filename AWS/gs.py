import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
from datetime import datetime
from io import BytesIO
import os

# ODK Credentials
ODK_USERNAME = "rushi@tnodk01.ii.com"
ODK_PASSWORD = "rushi2025&"

# Updated complete forms structure
forms = {
    "Server 1": {
        "TNMaster": {
            "Master Landscape Survey 04-2025 ODK XLSForm": {
                "project_id": 3,
                "form_id": "Master Landscape Survey 04-2025 ODK XLSForm"
            }
        },
        "BK TN AC Landscape": {
            "201-Cumbum": {"project_id": 4, "form_id": "201-Cumbum Landscape Survey 04-2025"},
            "39-Sholingur": {"project_id": 4, "form_id": "39-Sholingur Landscape Survey 04-2025"},
            "155-Cuddalore": {"project_id": 4, "form_id": "155-Cuddalore Landscape Survey 04-2025"},
            "66-Polur": {"project_id": 4, "form_id": "66-Polur Landscape Survey 04-2025"},
            "144-Manachanallur": {"project_id": 4, "form_id": "144-Manachanallur Landscape Survey 04-2025"},
            "145-Musiri": {"project_id": 4, "form_id": "145-Musiri Landscape Survey 04-2025"},
            "56-Thalli": {"project_id": 4, "form_id": "56-Thalli Landscape Survey 04-2025"},
            "3-Thirutthani": {"project_id": 4, "form_id": "3-Thirutthani Landscape Survey 04-2025"},
            "146-Thuraiyur": {"project_id": 4, "form_id": "146. Thuraiyur (SC) Landscape Survey 04-2025"},
            "182-Alangudi": {"project_id": 4, "form_id": "182-Alangudi Landscape Survey 04-2025"},
            "137-Kulithalai": {"project_id": 4, "form_id": "137-Kulithalai Landscape Survey 04-2025"},
            "12-Perambur": {"project_id": 4, "form_id": "12-Perambur Landscape Survey 04-2025"},
            "171-Kumbakonam": {"project_id": 4, "form_id": "171-Kumbakonam Landscape Survey 04-2025"},
            "150-Jayankondam": {"project_id": 4, "form_id": "150-Jayankondam Landscape Survey 04-2025"},
            "132-Dindigul": {"project_id": 4, "form_id": "132 Dindigul Landscape Survey 04-2025"},
            "20-Thousand Lights": {"project_id": 4, "form_id": "20-Thousand Lights Landscape Survey 04-2025"},
            "37-Kancheepuram": {"project_id": 4, "form_id": "37-Kancheepuram Landscape Survey 04-2025"},
            "136-Krishnarayapuram": {"project_id": 4, "form_id": "136-Krishnarayapuram (SC) Landscape Survey 04-2025"},
            "38-Arakkonam": {"project_id": 4, "form_id": "38-Arakkonam (SC) Landscape Survey 04-2025"},
            "200-Bodinayakanur": {"project_id": 4, "form_id": "200-Bodinayakanur Landscape Survey 04-2025"},
            "118-Coimbatore North": {"project_id": 4, "form_id": "118-Coimbatore North Landscape Survey 04-2025"},
            "189-Madurai East": {"project_id": 4, "form_id": "189-Madurai East Landscape Survey 04-2025"},
            "103-Perundurai": {"project_id": 4, "form_id": "103-Perundurai Landscape Survey 04-2025"},
            "199-Periyakulam": {"project_id": 4, "form_id": "199. Periyakulam (SC) Landscape Survey 04-2025"},
            "149-Ariyalur": {"project_id": 4, "form_id": "149-Ariyalur Landscape Survey 04-2025"},
            "135-Karur": {"project_id": 4, "form_id": "135-Karur Landscape Survey 04-2025"},
            "138-Manapparai": {"project_id": 4, "form_id": "138-Manapparai Landscape Survey 04-2025"},
            "152-Vriddhachalam": {"project_id": 4, "form_id": "152-Vriddhachalam Landscape Survey 04-2025"},
            "153-Neyveli": {"project_id": 4, "form_id": "153-Neyveli Landscape Survey 04-2025"},
            "156-Kurinjipadi": {"project_id": 4, "form_id": "156-Kurinjipadi Landscape Survey 04-2025"},
            "161-Mayiladuthurai": {"project_id": 4, "form_id": "161-Mayiladuthurai Landscape Survey 04-2025"},
            "166-Thiruthuraipoondi": {"project_id": 4, "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025"},
            "178-Gandharvakottai": {"project_id": 4, "form_id": "178-Gandharvakottai (SC) Landscape Survey 04-2025 copy 3"},
            "198-Andipatti": {"project_id": 4, "form_id": "198-Andipatti Landscape Survey 04-2025"},
            "51-Uthangarai": {"project_id": 4, "form_id": "51-Uthangarai (SC) Landscape Survey 04-2025"},
            "60-Pappireddippatti": {"project_id": 4, "form_id": "60-Pappireddippatti Landscape Survey 04-2025"},
            "61-Harur": {"project_id": 4, "form_id": "61-Harur (SC) Landscape Survey 04-2025"},
            "180-Pudukkottai": {"project_id": 4, "form_id": "180-Pudukkottai Landscape Survey 04-2025"},
            "158-Chidambaram": {"project_id": 4, "form_id": "158-Chidambaram Landscape Survey 04-2025"},
            "216-Srivaikuntam": {"project_id": 4, "form_id": "216-Srivaikuntam Landscape Survey 04-2025"},
            "133-Vedasandur": {"project_id": 4, "form_id": "133-Vedasandur Landscape Survey 04-2025"},
            "109-Gudalur": {"project_id": 4, "form_id": "109-Gudalur (SC) Landscape Survey 04-2025"},
            "62-Chengam": {"project_id": 4, "form_id": "62-Chengam (SC) Landscape Survey 04-2025"}
        },
        "03 TN AC Landscape": {
            "110-Coonoor": {"project_id": 5, "form_id": "110-Coonoor Landscape Survey 04-2025"},
            "222-Tenkasi": {"project_id": 5, "form_id": "222-Tenkasi Landscape Survey 04-2025"},
            "223-Alangulam": {"project_id": 5, "form_id": "223-Alangulam Landscape Survey 04-2025"},
            "48-Ambur": {"project_id": 5, "form_id": "48-AmburLandscape Survey 04-2025"},
            "49-Jolarpet": {"project_id": 5, "form_id": "49-Jolarpet Landscape Survey 04-2025"},
            "63-Tiruvannamalai": {"project_id": 5, "form_id": "63-Tiruvannamalai Landscape Survey 04-2025"},
            "64-Kilpennathur": {"project_id": 5, "form_id": "64-KilpennathurLandscape Survey 04-2025"},
            "65-Kalasapakkam": {"project_id": 5, "form_id": "65-Kalasapakkam Landscape Survey 04-2025"},
            "67-Arani": {"project_id": 5, "form_id": "67-Arani Landscape Survey 04-2025"},
            "68-Cheyyar": {"project_id": 5, "form_id": "68-Cheyyar Landscape Survey 04-2025"}
        }
    },
    "Server 2": {
        "02 TN Landscape Survey": {
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
            "Test Landscape Survey 04-2025 copy": {"project_id": 3, "form_id": "Test Landscape Survey 04-2025 copy"},
            "V3 Master Landscape Survey 04-2025 ODK XLSForm": {"project_id": 3, "form_id": "V3 Master Landscape Survey 04-2025 ODK XLSForm"}
        }
    }
}

# Streamlit App
st.set_page_config(page_title="ODK Data Processor", layout="wide")
st.title("📊 ODK Form Data Processor - Multi-Project")

# Custom CSS
st.markdown("""
<style>
    .stDataFrame {width: 100% !important;}
    .summary-row {background-color: #FFFACD !important; font-weight: bold !important;}
    .green-check {color: green !important; font-weight: bold !important;}
    .red-x {color: red !important; font-weight: bold !important;}
    .metric-box {border-radius: 5px; padding: 15px; background-color: #f0f2f6; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner="Fetching data from ODK...")
def get_odk_data(server_url, project_id, form_id):
    """Fetch submission data from ODK Central"""
    try:
        form_url = f"{server_url}/v1/projects/{project_id}/forms/{form_id}.svc"
        submissions_url = f"{form_url}/Submissions"
        response = requests.get(
            submissions_url,
            auth=HTTPBasicAuth(ODK_USERNAME, ODK_PASSWORD),
            headers={"Accept": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get('value', [])
    except Exception as e:
        st.error(f"Error fetching data for {form_id}: {str(e)}")
        return []

def safe_json_parse(data):
    """Safely parse JSON strings or return empty dict"""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}
    elif isinstance(data, dict):
        return data
    return {}

def process_submission(sub, form_name):
    """Process individual submission into structured data"""
    # Change this line to get the actual submitter name from group_six
    group_six = safe_json_parse(sub.get('group_six', {}))
    submitted_by = group_six.get('submittedBy', 'Unknown')
    
    uuid = sub.get('__id', '')
    phone_number = group_six.get('D8_PhoneNumber', '')
    
    geopoint = group_six.get('geopoint_widget', {})
    location_present = '✓' if geopoint and 'coordinates' in geopoint else '✗'
    audio_present = '✓' if sub.get('bg_audio') else '✗'
    
    duration = ''
    start_time = sub.get('start')
    end_time = sub.get('end')
    
    if start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time.rstrip('Z'))
            end_dt = datetime.fromisoformat(end_time.rstrip('Z'))
            duration_minutes = round((end_dt - start_dt).total_seconds() / 60, 1)
            duration = f"{duration_minutes} mins"
        except Exception:
            duration = 'N/A'
    
    return {
        'Form Name': form_name,
        'Submitted By': submitted_by,
        'UUID': uuid,
        'Phone Number': phone_number,
        'Location Present': location_present,
        'Audio Present': audio_present,
        'Duration to Fill': duration
    }

def create_excel_for_project(server_name, project_name, forms_data):
    """Create Excel file for a specific project"""
    excel_buffer = BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        for form_name, form_info in forms_data.items():
            # Get data for this form
            server_url = "https://tnodk01.indiaintentions.com" if server_name == "Server 1" else "https://tnodk02.indiaintentions.com"
            raw_data = get_odk_data(server_url, form_info['project_id'], form_info['form_id'])
            
            if not raw_data:
                continue
                
            # Process data
            processed_data = [process_submission(sub, form_name) for sub in raw_data]
            df = pd.DataFrame(processed_data)
            
            # Add summary row
            if not df.empty:
                total_submissions = len(df)
                with_location = len(df[df['Location Present'] == '✓'])
                with_audio = len(df[df['Audio Present'] == '✓'])
                avg_duration = pd.to_numeric(df['Duration to Fill'].str.replace(' mins', ''), errors='coerce').mean()
                avg_duration = f"{avg_duration:.1f} mins" if not pd.isna(avg_duration) else 'N/A'
                
                summary_row = pd.DataFrame([{
                    'Form Name': 'SUMMARY STATS',
                    'Submitted By': f'Total: {total_submissions}',
                    'UUID': '',
                    'Phone Number': '',
                    'Location Present': f'{with_location} ({with_location/total_submissions:.0%})',
                    'Audio Present': f'{with_audio} ({with_audio/total_submissions:.0%})',
                    'Duration to Fill': f'Avg: {avg_duration}'
                }])
                
                final_df = pd.concat([summary_row, df], ignore_index=True)
                
                # Write to Excel sheet
                final_df.to_excel(writer, index=False, sheet_name=form_name[:31])  # Sheet name max 31 chars
                
                # Formatting
                workbook = writer.book
                worksheet = writer.sheets[form_name[:31]]
                
                # Header format
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Format headers
                for col_num, value in enumerate(final_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Symbol formats
                symbol_format_green = workbook.add_format({'font_color': 'green', 'bold': True})
                symbol_format_red = workbook.add_format({'font_color': 'red', 'bold': True})
                
                # Apply conditional formatting
                for col in ['E', 'F']:  # Location and Audio columns
                    worksheet.conditional_format(f'{col}2:{col}{len(final_df)+1}', {
                        'type': 'text',
                        'criteria': 'containing',
                        'value': '✓',
                        'format': symbol_format_green
                    })
                    worksheet.conditional_format(f'{col}2:{col}{len(final_df)+1}', {
                        'type': 'text',
                        'criteria': 'containing',
                        'value': '✗',
                        'format': symbol_format_red
                    })
                
                # Format summary row
                summary_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#FFFF00'
                })
                worksheet.set_row(1, None, summary_format)
                
                # Auto-adjust column widths
                for i, col in enumerate(final_df.columns):
                    max_len = max(
                        final_df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, max_len)
    
    return excel_buffer

# Main UI
selected_server = st.sidebar.selectbox("Select Server", list(forms.keys()))

if selected_server:
    projects = forms[selected_server]
    selected_project = st.sidebar.selectbox("Select Project", list(projects.keys()))
    
    if selected_project:
        project_forms = projects[selected_project]
        
        if st.sidebar.button("Download All Forms in Project"):
            with st.spinner(f"Processing {selected_project}..."):
                excel_buffer = create_excel_for_project(selected_server, selected_project, project_forms)
                excel_buffer.seek(0)
                
                st.sidebar.download_button(
                    label="⬇️ Download Project Excel",
                    data=excel_buffer,
                    file_name=f"{selected_project.replace(' ', '_')}_submissions.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        # Show form selector
        selected_form = st.sidebar.selectbox("Select Form", list(project_forms.keys()))
        
        if selected_form:
            form_info = project_forms[selected_form]
            server_url = "https://tnodk01.indiaintentions.com" if selected_server == "Server 1" else "https://tnodk02.indiaintentions.com"
            
            with st.spinner(f"Loading {selected_form} data..."):
                raw_data = get_odk_data(server_url, form_info['project_id'], form_info['form_id'])
                
                if raw_data:
                    st.success(f"Found {len(raw_data)} submissions for {selected_form}")
                    processed_data = [process_submission(sub, selected_form) for sub in raw_data]
                    df = pd.DataFrame(processed_data)
                    
                    # Add summary row
                    total_submissions = len(df)
                    with_location = len(df[df['Location Present'] == '✓'])
                    with_audio = len(df[df['Audio Present'] == '✓'])
                    avg_duration = pd.to_numeric(df['Duration to Fill'].str.replace(' mins', ''), errors='coerce').mean()
                    avg_duration = f"{avg_duration:.1f} mins" if not pd.isna(avg_duration) else 'N/A'
                    
                    summary_row = pd.DataFrame([{
                        'Form Name': 'SUMMARY STATS',
                        'Submitted By': f'Total: {total_submissions}',
                        'UUID': '',
                        'Phone Number': '',
                        'Location Present': f'{with_location} ({with_location/total_submissions:.0%})',
                        'Audio Present': f'{with_audio} ({with_audio/total_submissions:.0%})',
                        'Duration to Fill': f'Avg: {avg_duration}'
                    }])
                    
                    final_df = pd.concat([summary_row, df], ignore_index=True)
                    
                    # Display styled dataframe
                    styled_df = final_df.style.applymap(
                        lambda x: 'color: green; font-weight: bold;' if x == '✓' else 'color: red; font-weight: bold;' if x == '✗' else '',
                        subset=['Location Present', 'Audio Present']
                    ).apply(lambda x: ['background: #FFFF00']*len(x) if x['Form Name'] == 'SUMMARY STATS' else ['']*len(x), axis=1)
                    
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Download button for individual form
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        final_df.to_excel(writer, index=False, sheet_name=selected_form[:31])
                        
                        # Formatting (same as in create_excel_for_project)
                        workbook = writer.book
                        worksheet = writer.sheets[selected_form[:31]]
                        
                        header_format = workbook.add_format({
                            'bold': True,
                            'text_wrap': True,
                            'valign': 'top',
                            'fg_color': '#D7E4BC',
                            'border': 1
                        })
                        
                        for col_num, value in enumerate(final_df.columns.values):
                            worksheet.write(0, col_num, value, header_format)
                        
                        symbol_format_green = workbook.add_format({'font_color': 'green', 'bold': True})
                        symbol_format_red = workbook.add_format({'font_color': 'red', 'bold': True})
                        
                        for col in ['E', 'F']:
                            worksheet.conditional_format(f'{col}2:{col}{len(final_df)+1}', {
                                'type': 'text',
                                'criteria': 'containing',
                                'value': '✓',
                                'format': symbol_format_green
                            })
                            worksheet.conditional_format(f'{col}2:{col}{len(final_df)+1}', {
                                'type': 'text',
                                'criteria': 'containing',
                                'value': '✗',
                                'format': symbol_format_red
                            })
                        
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
                    
                    excel_buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download This Form",
                        data=excel_buffer,
                        file_name=f"{selected_form.replace(' ', '_')}_submissions.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    with st.expander("🔍 View Raw Data"):
                        st.json(raw_data)
                else:
                    st.warning(f"No data found for {selected_form}")

# Add timestamp
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")