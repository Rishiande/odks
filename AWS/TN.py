import streamlit as st
import pandas as pd
import re
import os
from io import BytesIO
from pathlib import Path
import glob
import zipfile

# Configuration - Update these paths as needed
SAMPLE_FILES_PATH = r"C:\Users\rishi\Desktop\AWS\Samples Files"
MAIN_FILES_PATH = r"C:\Users\rishi\Desktop\AWS\Main Files"

def extract_audio_code_from_bg_audio(bg_audio_value):
    """Extract the numeric part from bg_audio column (remove .m4a extension)"""
    if pd.isna(bg_audio_value):
        return None
    
    # Convert to string and remove .m4a extension
    audio_str = str(bg_audio_value)
    # Remove file extension if present
    audio_code = re.sub(r'\.(m4a|mp3|wav|mp4)$', '', audio_str, flags=re.IGNORECASE)
    return audio_code

def get_excel_files_from_folder(folder_path):
    """Get list of Excel files from a folder"""
    if not os.path.exists(folder_path):
        return []
    
    excel_files = []
    for ext in ['*.xlsx', '*.xls']:
        excel_files.extend(glob.glob(os.path.join(folder_path, ext)))
    
    # Return just the filenames (not full paths) for display
    return [os.path.basename(f) for f in excel_files]

def load_excel_file(folder_path, filename):
    """Load Excel file from folder"""
    full_path = os.path.join(folder_path, filename)
    return pd.read_excel(full_path)

def compare_audio_codes(sample_df, main_df):
    """Compare audio codes and return matching records from main file"""
    
    # Extract audio codes from main file bg_audio column
    main_df['extracted_audio_code'] = main_df['bg_audio'].apply(extract_audio_code_from_bg_audio)
    
    # Separate accepted and rejected records from sample file
    accepted_df = sample_df[sample_df['Accepted / Rejected'].str.lower().str.strip() == 'accepted']
    rejected_df = sample_df[sample_df['Accepted / Rejected'].str.lower().str.strip() == 'rejected']
    
    # Get audio codes for accepted and rejected
    accepted_audio_codes = accepted_df['Audio Code'].astype(str).tolist()
    rejected_audio_codes = rejected_df['Audio Code'].astype(str).tolist()
    
    # Find matching records for accepted
    accepted_matching = main_df[main_df['extracted_audio_code'].isin(accepted_audio_codes)]
    
    # Find matching records for rejected
    rejected_matching = main_df[main_df['extracted_audio_code'].isin(rejected_audio_codes)]
    
    # Find remaining records (not in accepted or rejected)
    all_sample_codes = accepted_audio_codes + rejected_audio_codes
    remaining_records = main_df[~main_df['extracted_audio_code'].isin(all_sample_codes)]
    
    # Remove the temporary column from all DataFrames
    accepted_matching = accepted_matching.drop('extracted_audio_code', axis=1)
    rejected_matching = rejected_matching.drop('extracted_audio_code', axis=1)
    remaining_records = remaining_records.drop('extracted_audio_code', axis=1)
    
    return accepted_matching, rejected_matching, remaining_records, accepted_df, rejected_df

def convert_df_to_excel(accepted_df, rejected_df, remaining_df, output_filename):
    """Convert DataFrames to Excel bytes with separate sheets for accepted, rejected, and remaining"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Accepted matches sheet
        if len(accepted_df) > 0:
            accepted_df.to_excel(writer, index=False, sheet_name='Accepted Matches')
        else:
            pd.DataFrame(columns=['No accepted matches found']).to_excel(writer, index=False, sheet_name='Accepted Matches')
        
        # Rejected matches sheet
        if len(rejected_df) > 0:
            rejected_df.to_excel(writer, index=False, sheet_name='Rejected Matches')
        else:
            pd.DataFrame(columns=['No rejected matches found']).to_excel(writer, index=False, sheet_name='Rejected Matches')
        
        # Remaining records sheet (Rejected by Data verification)
        if len(remaining_df) > 0:
            remaining_df.to_excel(writer, index=False, sheet_name='Rejected by Data verification')
        else:
            pd.DataFrame(columns=['No remaining records found']).to_excel(writer, index=False, sheet_name='Rejected by Data verification')
    
    return output.getvalue()

def process_per_sample_file(selected_sample_files, selected_main_files):
    """Process files organized by sample file - each sample file gets its own output"""
    
    per_sample_results = {}
    overall_summary = []
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_operations = len(selected_sample_files) * len(selected_main_files)
    current_operation = 0
    
    for sample_file in selected_sample_files:
        try:
            # Initialize results for this sample file
            sample_results = {
                'accepted_matches': [],
                'rejected_matches': [],
                'remaining_records': [],
                'summary': [],
                'sample_file_name': sample_file
            }
            
            # Load sample file
            sample_df = load_excel_file(SAMPLE_FILES_PATH, sample_file)
            
            # Validate sample file
            if 'Audio Code' not in sample_df.columns or 'Accepted / Rejected' not in sample_df.columns:
                st.error(f"❌ Required columns missing in sample file: {sample_file}")
                continue
            
            for main_file in selected_main_files:
                try:
                    current_operation += 1
                    progress = current_operation / total_operations
                    progress_bar.progress(progress)
                    status_text.text(f"Processing: {sample_file} vs {main_file} ({current_operation}/{total_operations})")
                    
                    # Load main file
                    main_df = load_excel_file(MAIN_FILES_PATH, main_file)
                    
                    # Validate main file
                    if 'bg_audio' not in main_df.columns:
                        st.warning(f"⚠️ 'bg_audio' column missing in main file: {main_file}")
                        continue
                    
                    # Perform comparison
                    accepted_matching, rejected_matching, remaining_records, accepted_sample, rejected_sample = compare_audio_codes(sample_df, main_df)
                    
                    # Add main file info to results
                    if len(accepted_matching) > 0:
                        accepted_matching['Main_File'] = main_file
                        sample_results['accepted_matches'].append(accepted_matching)
                    
                    if len(rejected_matching) > 0:
                        rejected_matching['Main_File'] = main_file
                        sample_results['rejected_matches'].append(rejected_matching)
                    
                    if len(remaining_records) > 0:
                        remaining_records['Main_File'] = main_file
                        sample_results['remaining_records'].append(remaining_records)
                    
                    # Add summary info
                    summary_row = {
                        'Sample_File': sample_file,
                        'Main_File': main_file,
                        'Sample_Records': len(sample_df),
                        'Main_Records': len(main_df),
                        'Accepted_Matches': len(accepted_matching),
                        'Rejected_Matches': len(rejected_matching),
                        'Remaining_Records': len(remaining_records),
                        'Total_Processed': len(accepted_matching) + len(rejected_matching) + len(remaining_records)
                    }
                    sample_results['summary'].append(summary_row)
                    overall_summary.append(summary_row)
                    
                except Exception as e:
                    st.error(f"❌ Error processing {main_file} with {sample_file}: {str(e)}")
                    continue
            
            # Combine results for this sample file
            combined_sample_results = {}
            for key in ['accepted_matches', 'rejected_matches', 'remaining_records']:
                if sample_results[key]:
                    combined_sample_results[key] = pd.concat(sample_results[key], ignore_index=True)
                else:
                    combined_sample_results[key] = pd.DataFrame()
            
            combined_sample_results['summary'] = pd.DataFrame(sample_results['summary'])
            combined_sample_results['sample_file_name'] = sample_file
            
            # Store results for this sample file
            per_sample_results[sample_file] = combined_sample_results
                    
        except Exception as e:
            st.error(f"❌ Error processing sample file {sample_file}: {str(e)}")
            continue
    
    # Clear progress
    progress_bar.empty()
    status_text.empty()
    
    # Create overall summary
    overall_summary_df = pd.DataFrame(overall_summary)
    
    return per_sample_results, overall_summary_df

def create_zip_with_all_results(per_sample_results):
    """Create a ZIP file containing separate Excel files for each sample file"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for sample_file, results in per_sample_results.items():
            # Create Excel file for this sample
            excel_data = convert_df_to_excel(
                results['accepted_matches'], 
                results['rejected_matches'], 
                results['remaining_records'],
                f"{sample_file}_results.xlsx"
            )
            
            # Add to ZIP with clean filename
            clean_name = re.sub(r'[^\w\-_\.]', '_', sample_file)
            zip_file.writestr(f"{clean_name}_results.xlsx", excel_data)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def main():
    st.set_page_config(page_title="Enhanced Audio Code Comparison Tool - Per Sample Output", layout="wide")
    
    st.title("🎵 Enhanced Audio Code Comparison Tool")
    st.markdown("### Multi-File Processing with Per-Sample File Output")
    st.markdown("---")
    
    # Display folder paths
    st.subheader("📁 Configured Folder Paths")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Sample Files Path:** `{SAMPLE_FILES_PATH}`")
        # Check if sample folder exists
        if os.path.exists(SAMPLE_FILES_PATH):
            sample_files = get_excel_files_from_folder(SAMPLE_FILES_PATH)
            st.success(f"✅ Found {len(sample_files)} Excel files")
        else:
            st.error("❌ Sample folder not found!")
            sample_files = []
    
    with col2:
        st.info(f"**Main Files Path:** `{MAIN_FILES_PATH}`")
        # Check if main folder exists
        if os.path.exists(MAIN_FILES_PATH):
            main_files = get_excel_files_from_folder(MAIN_FILES_PATH)
            st.success(f"✅ Found {len(main_files)} Excel files")
        else:
            st.error("❌ Main folder not found!")
            main_files = []
    
    # File selection section
    if sample_files and main_files:
        st.markdown("---")
        st.subheader("📋 Select Files for Processing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Select Sample Files:**")
            selected_sample_files = st.multiselect(
                "Choose sample files to process",
                sample_files,
                default=None,
                help="Select one or more sample files containing 'Audio Code' and 'Accepted / Rejected' columns"
            )
            
            if selected_sample_files:
                st.success(f"✅ Selected {len(selected_sample_files)} sample files")
                with st.expander("View Selected Sample Files"):
                    for file in selected_sample_files:
                        st.write(f"• {file}")
        
        with col2:
            st.write("**Select Main Files:**")
            selected_main_files = st.multiselect(
                "Choose main files to process",
                main_files,
                default=None,
                help="Select one or more main files containing 'bg_audio' column"
            )
            
            if selected_main_files:
                st.success(f"✅ Selected {len(selected_main_files)} main files")
                with st.expander("View Selected Main Files"):
                    for file in selected_main_files:
                        st.write(f"• {file}")
        
        # Process button
        if selected_sample_files and selected_main_files:
            st.markdown("---")
            
            # Show processing summary
            total_combinations = len(selected_sample_files) * len(selected_main_files)
            st.info(f"📊 **Processing Summary:** {len(selected_sample_files)} sample files × {len(selected_main_files)} main files = {total_combinations} total combinations")
            st.info(f"🎯 **Output Strategy:** Each sample file will generate its own separate output containing comparisons with all selected main files")
            
            if st.button("🚀 Start Processing", type="primary"):
                st.markdown("---")
                st.subheader("⚙️ Processing Files...")
                
                # Process files per sample file
                per_sample_results, overall_summary_df = process_per_sample_file(selected_sample_files, selected_main_files)
                
                if not overall_summary_df.empty:
                    st.success("✅ Processing completed successfully!")
                    
                    # Display overall summary
                    st.subheader("📊 Overall Processing Summary")
                    st.dataframe(overall_summary_df, use_container_width=True)
                    
                    # Show overall metrics
                    total_accepted = sum(len(results['accepted_matches']) for results in per_sample_results.values())
                    total_rejected = sum(len(results['rejected_matches']) for results in per_sample_results.values())
                    total_remaining = sum(len(results['remaining_records']) for results in per_sample_results.values())
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Accepted", total_accepted)
                    with col2:
                        st.metric("Total Rejected", total_rejected)
                    with col3:
                        st.metric("Total Remaining", total_remaining)
                    with col4:
                        st.metric("Total Processed", total_accepted + total_rejected + total_remaining)
                    
                    # Display results per sample file
                    st.subheader("📋 Results by Sample File")
                    
                    # Create tabs for each sample file
                    sample_tabs = st.tabs([f"📄 {sample_file}" for sample_file in selected_sample_files])
                    
                    for idx, (sample_file, tab) in enumerate(zip(selected_sample_files, sample_tabs)):
                        with tab:
                            if sample_file in per_sample_results:
                                results = per_sample_results[sample_file]
                                
                                # Show metrics for this sample file
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Accepted", len(results['accepted_matches']))
                                with col2:
                                    st.metric("Rejected", len(results['rejected_matches']))
                                with col3:
                                    st.metric("Remaining", len(results['remaining_records']))
                                with col4:
                                    st.metric("Total", len(results['accepted_matches']) + len(results['rejected_matches']) + len(results['remaining_records']))
                                
                                # Show summary for this sample file
                                st.write("**📊 Summary for this Sample File:**")
                                st.dataframe(results['summary'], use_container_width=True)
                                
                                # Show detailed results in sub-tabs
                                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🟢 Accepted", "🔴 Rejected", "⚠️ Remaining"])
                                
                                with sub_tab1:
                                    if not results['accepted_matches'].empty:
                                        st.success(f"Found {len(results['accepted_matches'])} accepted matches")
                                        st.dataframe(results['accepted_matches'], use_container_width=True)
                                    else:
                                        st.info("No accepted matches found")
                                
                                with sub_tab2:
                                    if not results['rejected_matches'].empty:
                                        st.success(f"Found {len(results['rejected_matches'])} rejected matches")
                                        st.dataframe(results['rejected_matches'], use_container_width=True)
                                    else:
                                        st.info("No rejected matches found")
                                
                                with sub_tab3:
                                    if not results['remaining_records'].empty:
                                        st.warning(f"Found {len(results['remaining_records'])} remaining records")
                                        st.dataframe(results['remaining_records'], use_container_width=True)
                                    else:
                                        st.info("No remaining records found")
                                
                                # Individual download for this sample file
                                st.markdown("---")
                                if not results['accepted_matches'].empty or not results['rejected_matches'].empty or not results['remaining_records'].empty:
                                    excel_data = convert_df_to_excel(
                                        results['accepted_matches'], 
                                        results['rejected_matches'], 
                                        results['remaining_records'],
                                        f"{sample_file}_results.xlsx"
                                    )
                                    
                                    clean_name = re.sub(r'[^\w\-_\.]', '_', sample_file)
                                    st.download_button(
                                        label=f"📥 Download Results for {sample_file}",
                                        data=excel_data,
                                        file_name=f"{clean_name}_results.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key=f"download_{idx}"
                                    )
                            else:
                                st.error(f"No results found for {sample_file}")
                    
                    # Download section for all results
                    st.markdown("---")
                    st.subheader("💾 Download All Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Download all results as ZIP
                        if per_sample_results:
                            zip_data = create_zip_with_all_results(per_sample_results)
                            st.download_button(
                                label="📦 Download All Results (ZIP)",
                                data=zip_data,
                                file_name="all_sample_results.zip",
                                mime="application/zip",
                                help="Contains separate Excel files for each sample file"
                            )
                    
                    with col2:
                        # Download overall summary
                        if not overall_summary_df.empty:
                            csv_summary = overall_summary_df.to_csv(index=False)
                            st.download_button(
                                label="📊 Download Overall Summary (CSV)",
                                data=csv_summary,
                                file_name="overall_processing_summary.csv",
                                mime="text/csv"
                            )
                
                else:
                    st.error("❌ No results generated. Please check your files and try again.")
        
        else:
            st.info("👆 Please select both sample and main files to start processing")
    
    else:
        st.warning("⚠️ Please ensure both sample and main folders exist and contain Excel files")
        
        # Show path configuration help
        st.markdown("---")
        st.subheader("⚙️ Path Configuration")
        st.markdown("""
        **To update folder paths:**
        1. Edit the paths at the top of the script:
           - `SAMPLE_FILES_PATH = r"C:\\Users\\rishi\\Desktop\\AWS\\Samples Files"`
           - `MAIN_FILES_PATH = r"C:\\Users\\rishi\\Desktop\\AWS\\Main Files"`
        2. Make sure both folders exist and contain Excel files
        3. Restart the Streamlit application
        """)
    
    # Instructions
    st.markdown("---")
    st.subheader("📋 How to Use - Enhanced Per-Sample Output")
    st.markdown("""
    ### 🎯 **Purpose**
    This enhanced tool processes multiple Excel files and **organizes results by sample file** - each sample file gets its own dedicated output.
    
    ### 📂 **Folder Structure**
    - **Sample Files Folder**: Contains Excel files with 'Audio Code' and 'Accepted / Rejected' columns
    - **Main Files Folder**: Contains Excel files with 'bg_audio' column
    
    ### 🔄 **Processing Flow**
    1. **Select Files**: Choose multiple sample and main files
    2. **Process**: Each sample file is compared against ALL selected main files
    3. **Results**: Get separate outputs for each sample file
    4. **Download**: Individual Excel files per sample + ZIP with all results
    
    ### 📊 **Output Organization**
    - **Per Sample File**: Each sample file generates its own Excel with 3 sheets:
      - ✅ **Accepted Matches**: All accepted matches from all main files
      - ❌ **Rejected Matches**: All rejected matches from all main files  
      - ⚠️ **Rejected by Data verification**: All remaining records from all main files
    - **Overall Summary**: Combined statistics across all processing
    
    ### 🎉 **New Benefits**
    - ✅ **Organized Output**: Each sample file gets its own dedicated result
    - ✅ **Individual Downloads**: Download results for specific sample files
    - ✅ **Bulk Download**: ZIP file with all sample results
    - ✅ **Clear Organization**: Easy to find results for specific sample files
    - ✅ **Source Tracking**: Main file names included in results
    - ✅ **Comprehensive Summary**: Both per-sample and overall statistics
    
    ### 📋 **Example**
    If you have:
    - 3 Sample Files: `Sample_A.xlsx`, `Sample_B.xlsx`, `Sample_C.xlsx`
    - 2 Main Files: `Main_1.xlsx`, `Main_2.xlsx`
    
    You'll get:
    - 3 separate Excel outputs (one for each sample file)
    - Each output contains matches from both main files
    - 1 ZIP file containing all 3 Excel files
    - Overall summary showing all 6 combinations processed
    """)

if __name__ == "__main__":
    main()
