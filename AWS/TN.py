import streamlit as st
import pandas as pd
import re
from io import BytesIO

def extract_audio_code_from_bg_audio(bg_audio_value):
    """Extract the numeric part from bg_audio column (remove .m4a extension)"""
    if pd.isna(bg_audio_value):
        return None
    
    # Convert to string and remove .m4a extension
    audio_str = str(bg_audio_value)
    # Remove file extension if present
    audio_code = re.sub(r'\.(m4a|mp3|wav|mp4)$', '', audio_str, flags=re.IGNORECASE)
    return audio_code

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

def convert_df_to_excel(accepted_df, rejected_df, remaining_df):
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

def main():
    st.set_page_config(page_title="Audio Code Comparison Tool", layout="wide")
    
    st.title("🎵 Audio Code Comparison Tool")
    st.markdown("---")
    
    # Create two columns for file uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Sample Excel File")
        st.info("Upload the Excel file containing 'Audio Code' column")
        sample_file = st.file_uploader(
            "Choose Sample Excel File", 
            type=['xlsx', 'xls'],
            key="sample_file"
        )
        
        if sample_file is not None:
            try:
                sample_df = pd.read_excel(sample_file)
                st.success(f"✅ Sample file loaded successfully!")
                st.write(f"**Rows:** {len(sample_df)}")
                st.write(f"**Columns:** {list(sample_df.columns)}")
                
                # Check if Audio Code column exists
                if 'Audio Code' in sample_df.columns:
                    st.write(f"**Audio Code samples:**")
                    st.write(sample_df['Audio Code'].head().tolist())
                    
                    # Check if Accepted / Rejected column exists
                    if 'Accepted / Rejected' in sample_df.columns:
                        st.write(f"**Accepted/Rejected distribution:**")
                        status_counts = sample_df['Accepted / Rejected'].value_counts()
                        st.write(status_counts.to_dict())
                    else:
                        st.error("❌ 'Accepted / Rejected' column not found in sample file!")
                else:
                    st.error("❌ 'Audio Code' column not found in sample file!")
                    
            except Exception as e:
                st.error(f"❌ Error reading sample file: {str(e)}")
    
    with col2:
        st.subheader("📁 Main Excel File")
        st.info("Upload the Excel file containing 'bg_audio' column")
        main_file = st.file_uploader(
            "Choose Main Excel File", 
            type=['xlsx', 'xls'],
            key="main_file"
        )
        
        if main_file is not None:
            try:
                main_df = pd.read_excel(main_file)
                st.success(f"✅ Main file loaded successfully!")
                st.write(f"**Rows:** {len(main_df)}")
                st.write(f"**Columns:** {list(main_df.columns)}")
                
                # Check if bg_audio column exists
                if 'bg_audio' in main_df.columns:
                    st.write(f"**bg_audio samples:**")
                    st.write(main_df['bg_audio'].head().tolist())
                else:
                    st.error("❌ 'bg_audio' column not found in main file!")
                    
            except Exception as e:
                st.error(f"❌ Error reading main file: {str(e)}")
    
    # Process files if both are uploaded
    if sample_file is not None and main_file is not None:
        try:
            sample_df = pd.read_excel(sample_file)
            main_df = pd.read_excel(main_file)
            
            # Validate required columns
            if 'Audio Code' not in sample_df.columns:
                st.error("❌ 'Audio Code' column not found in sample file!")
                return
                
            if 'Accepted / Rejected' not in sample_df.columns:
                st.error("❌ 'Accepted / Rejected' column not found in sample file!")
                return
                
            if 'bg_audio' not in main_df.columns:
                st.error("❌ 'bg_audio' column not found in main file!")
                return
            
            st.markdown("---")
            st.subheader("🔍 Comparison Results")
            
            # Perform comparison
            accepted_matching, rejected_matching, remaining_records, accepted_sample, rejected_sample = compare_audio_codes(sample_df, main_df)
            
            # Create metrics in columns
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Sample Records", len(sample_df))
            with col2:
                st.metric("Main Records", len(main_df))
            with col3:
                st.metric("Accepted Matches", len(accepted_matching))
            with col4:
                st.metric("Rejected Matches", len(rejected_matching))
            with col5:
                st.metric("Remaining Records", len(remaining_records))
            
            # Show accepted vs rejected breakdown
            st.subheader("📊 Sample File Breakdown")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Accepted Records**: {len(accepted_sample)}")
                if len(accepted_sample) > 0:
                    st.write("Sample Audio Codes:")
                    st.write(accepted_sample['Audio Code'].head().tolist())
                    
            with col2:
                st.info(f"**Rejected Records**: {len(rejected_sample)}")
                if len(rejected_sample) > 0:
                    st.write("Sample Audio Codes:")
                    st.write(rejected_sample['Audio Code'].head().tolist())
            
            # Display results
            if len(accepted_matching) > 0 or len(rejected_matching) > 0 or len(remaining_records) > 0:
                st.success(f"✅ Found matches and remaining records!")
                
                # Tabs for accepted, rejected, and remaining
                tab1, tab2, tab3 = st.tabs(["🟢 Accepted Matches", "🔴 Rejected Matches", "⚠️ Rejected by Data verification"])
                
                with tab1:
                    if len(accepted_matching) > 0:
                        st.success(f"Found {len(accepted_matching)} accepted matches")
                        st.dataframe(accepted_matching, use_container_width=True)
                    else:
                        st.info("No accepted matches found")
                
                with tab2:
                    if len(rejected_matching) > 0:
                        st.success(f"Found {len(rejected_matching)} rejected matches")
                        st.dataframe(rejected_matching, use_container_width=True)
                    else:
                        st.info("No rejected matches found")
                
                with tab3:
                    if len(remaining_records) > 0:
                        st.warning(f"Found {len(remaining_records)} remaining records (not in sample file)")
                        st.info("These records were not found in the sample file's accepted or rejected lists")
                        st.dataframe(remaining_records, use_container_width=True)
                    else:
                        st.info("No remaining records found")
                
                # Download option
                st.subheader("💾 Download Results")
                excel_data = convert_df_to_excel(accepted_matching, rejected_matching, remaining_records)
                st.download_button(
                    label="📥 Download All Results as Excel (3 Separate Sheets)",
                    data=excel_data,
                    file_name="audio_comparison_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Show summary
                st.subheader("📈 Summary")
                total_processed = len(accepted_matching) + len(rejected_matching) + len(remaining_records)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Processed", total_processed)
                with col2:
                    if total_processed > 0:
                        coverage_percentage = ((len(accepted_matching) + len(rejected_matching)) / total_processed) * 100
                        st.metric("Sample Coverage", f"{coverage_percentage:.1f}%")
                    else:
                        st.metric("Sample Coverage", "0%")
                with col3:
                    if total_processed > 0:
                        remaining_percentage = (len(remaining_records) / total_processed) * 100
                        st.metric("Remaining %", f"{remaining_percentage:.1f}%")
                    else:
                        st.metric("Remaining %", "0%")
                
                # Show detailed comparison
                with st.expander("🔍 View Detailed Comparison"):
                    st.write("**Accepted Audio Codes from Sample:**")
                    accepted_codes = accepted_sample['Audio Code'].astype(str).tolist()
                    st.write(accepted_codes[:10])  # Show first 10
                    
                    st.write("**Rejected Audio Codes from Sample:**")
                    rejected_codes = rejected_sample['Audio Code'].astype(str).tolist()
                    st.write(rejected_codes[:10])  # Show first 10
                    
                    st.write("**Main bg_audio (extracted codes):**")
                    main_codes = main_df['bg_audio'].apply(extract_audio_code_from_bg_audio).tolist()
                    st.write([code for code in main_codes[:10] if code is not None])  # Show first 10
                    
                    st.write("**Remaining Records (first 5 bg_audio codes):**")
                    if len(remaining_records) > 0:
                        remaining_codes = remaining_records['bg_audio'].head().tolist()
                        st.write(remaining_codes)
                    else:
                        st.write("No remaining records")
                    
            else:
                st.warning("⚠️ No matching records found!")
                
                # Show some debug info
                with st.expander("🔧 Debug Information"):
                    st.write("**Accepted Audio Codes (first 10):**")
                    accepted_codes = accepted_sample['Audio Code'].astype(str).tolist()
                    st.write(accepted_codes[:10])
                    
                    st.write("**Rejected Audio Codes (first 10):**")
                    rejected_codes = rejected_sample['Audio Code'].astype(str).tolist()
                    st.write(rejected_codes[:10])
                    
                    st.write("**Main bg_audio extracted codes (first 10):**")
                    main_codes = main_df['bg_audio'].apply(extract_audio_code_from_bg_audio).tolist()
                    st.write([code for code in main_codes[:10] if code is not None])
                    
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
    
    # Instructions
    st.markdown("---")
    st.subheader("📋 Instructions")
    st.markdown("""
    1. **Sample Excel File**: Upload the Excel file containing the 'Audio Code' and 'Accepted / Rejected' columns
       - Audio Code Format: `1745739346222` (numeric codes)
       - Accepted / Rejected: `Accepted` or `Rejected` (case insensitive)
    
    2. **Main Excel File**: Upload the Excel file containing the 'bg_audio' column
       - Format: `1746440155390.m4a` (codes with file extensions)
    
    3. **Process**: The tool will:
       - Separate accepted and rejected records from sample file
       - Extract numeric codes from bg_audio column (remove file extensions)
       - Compare both accepted and rejected codes with main file
       - Generate separate results for accepted, rejected, and remaining matches
    
    4. **Output**: Download Excel file with **three sheets**:
       - **Accepted Matches**: All matching records for accepted audio codes
       - **Rejected Matches**: All matching records for rejected audio codes
       - **Rejected by Data verification**: All remaining records from main file (not in sample file)
    
    5. **Download**: Download the results as a single Excel file with three separate sheets
    
    6. **Summary**: View coverage statistics and remaining records percentage
    """)

if __name__ == "__main__":
    main()
