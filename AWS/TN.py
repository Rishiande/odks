import streamlit as st
import pandas as pd
import re
from io import BytesIO

def extract_audio_code_from_bg_audio(bg_audio_value):
    """Extract the numeric part from bg_audio column (remove .m4a extension)"""
    if pd.isna(bg_audio_value) or bg_audio_value in ['', ' ', None]:
        return None
    
    # Convert to string and clean
    audio_str = str(bg_audio_value).strip()
    
    # Remove file extension if present
    audio_code = re.sub(r'\.(m4a|mp3|wav|mp4|aac|flac)$', '', audio_str, flags=re.IGNORECASE)
    
    # Remove any non-digit characters (except decimal point for float handling)
    audio_code = re.sub(r'[^\d.]', '', audio_code)
    
    # Convert to float then to int to handle cases like '1234.0'
    try:
        return str(int(float(audio_code))) if audio_code else None
    except:
        return None

def clean_audio_code(audio_code):
    """Clean and standardize audio codes from both files"""
    if pd.isna(audio_code) or audio_code in ['', ' ', None]:
        return None
    
    # Convert to string and clean
    audio_str = str(audio_code).strip()
    
    # Remove any non-digit characters
    audio_str = re.sub(r'[^\d]', '', audio_str)
    
    # Convert to float then to int to handle cases like '1234.0'
    try:
        return str(int(float(audio_str))) if audio_str else None
    except:
        return None

def compare_audio_codes(sample_df, main_df):
    """Compare audio codes and return matching records from main file"""
    # Clean and standardize audio codes in both files
    sample_df['clean_audio_code'] = sample_df['Audio Code'].apply(clean_audio_code)
    main_df['extracted_audio_code'] = main_df['bg_audio'].apply(extract_audio_code_from_bg_audio)
    
    # Clean Accepted/Rejected column (handle case, spaces, etc.)
    sample_df['status_clean'] = sample_df['Accepted / Rejected'].str.strip().str.lower()
    
    # Separate accepted and rejected records from sample file
    accepted_df = sample_df[sample_df['status_clean'] == 'accepted']
    rejected_df = sample_df[sample_df['status_clean'] == 'rejected']
    
    # Get audio codes for accepted and rejected (cleaned)
    accepted_audio_codes = accepted_df['clean_audio_code'].dropna().unique().tolist()
    rejected_audio_codes = rejected_df['clean_audio_code'].dropna().unique().tolist()
    
    # Find matching records for accepted
    accepted_matching = main_df[main_df['extracted_audio_code'].isin(accepted_audio_codes)]
    
    # Find matching records for rejected
    rejected_matching = main_df[main_df['extracted_audio_code'].isin(rejected_audio_codes)]
    
    # Find remaining records (not in accepted or rejected)
    all_sample_codes = accepted_audio_codes + rejected_audio_codes
    remaining_records = main_df[~main_df['extracted_audio_code'].isin(all_sample_codes)]
    
    # Remove temporary columns
    accepted_matching = accepted_matching.drop('extracted_audio_code', axis=1)
    rejected_matching = rejected_matching.drop('extracted_audio_code', axis=1)
    remaining_records = remaining_records.drop('extracted_audio_code', axis=1)
    
    return accepted_matching, rejected_matching, remaining_records, accepted_df, rejected_df

def convert_df_to_excel(accepted_df, rejected_df, remaining_df):
    """Convert DataFrames to Excel bytes with separate sheets"""
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
        
        # Remaining records sheet
        if len(remaining_df) > 0:
            remaining_df.to_excel(writer, index=False, sheet_name='Rejected by Data verification')
        else:
            pd.DataFrame(columns=['No remaining records found']).to_excel(writer, index=False, sheet_name='Rejected by Data verification')
    
    return output.getvalue()

def validate_sample_file(df):
    """Validate the structure of the sample file"""
    required_columns = ['Audio Code', 'Accepted / Rejected']
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
    
    # Check if Accepted/Rejected has valid values
    if 'Accepted / Rejected' in df.columns:
        valid_status = df['Accepted / Rejected'].str.strip().str.lower().isin(['accepted', 'rejected'])
        if not valid_status.all():
            invalid_values = df[~valid_status]['Accepted / Rejected'].unique()
            return False, f"Invalid values in 'Accepted / Rejected': {', '.join(map(str, invalid_values))}"
    
    return True, "Sample file is valid"

def validate_main_file(df):
    """Validate the structure of the main file"""
    if 'bg_audio' not in df.columns:
        return False, "Missing required column: bg_audio"
    return True, "Main file is valid"

def main():
    st.set_page_config(page_title="Audio Code Comparison Tool", layout="wide")
    
    st.title("🎵 Audio Code Comparison Tool")
    st.markdown("---")
    
    # File upload sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Sample Excel File")
        st.info("Upload the Excel file containing 'Audio Code' and 'Accepted / Rejected' columns")
        sample_file = st.file_uploader(
            "Choose Sample Excel File", 
            type=['xlsx', 'xls'],
            key="sample_file"
        )
        
        if sample_file is not None:
            try:
                sample_df = pd.read_excel(sample_file)
                st.success(f"✅ Sample file loaded successfully!")
                
                # Validate sample file
                is_valid, validation_msg = validate_sample_file(sample_df)
                if not is_valid:
                    st.error(f"❌ Validation Error: {validation_msg}")
                else:
                    st.write(f"**Rows:** {len(sample_df)}")
                    st.write(f"**Columns:** {list(sample_df.columns)}")
                    
                    # Show sample data
                    with st.expander("👀 View Sample Data"):
                        st.dataframe(sample_df.head())
                    
                    # Show status distribution
                    status_counts = sample_df['Accepted / Rejected'].value_counts()
                    st.write("**Accepted/Rejected distribution:**")
                    st.bar_chart(status_counts)
                    
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
                
                # Validate main file
                is_valid, validation_msg = validate_main_file(main_df)
                if not is_valid:
                    st.error(f"❌ Validation Error: {validation_msg}")
                else:
                    st.write(f"**Rows:** {len(main_df)}")
                    st.write(f"**Columns:** {list(main_df.columns)}")
                    
                    # Show sample data
                    with st.expander("👀 View Sample Data"):
                        st.dataframe(main_df.head())
                    
            except Exception as e:
                st.error(f"❌ Error reading main file: {str(e)}")
    
    # Process files if both are uploaded and valid
    if sample_file is not None and main_file is not None:
        try:
            sample_df = pd.read_excel(sample_file)
            main_df = pd.read_excel(main_file)
            
            # Validate files
            sample_valid, sample_msg = validate_sample_file(sample_df)
            main_valid, main_msg = validate_main_file(main_df)
            
            if not sample_valid or not main_valid:
                st.error("❌ Please fix the validation errors before proceeding")
                if not sample_valid:
                    st.error(f"Sample file: {sample_msg}")
                if not main_valid:
                    st.error(f"Main file: {main_msg}")
                return
            
            st.markdown("---")
            st.subheader("🔍 Comparison Results")
            
            # Perform comparison
            accepted_matching, rejected_matching, remaining_records, accepted_sample, rejected_sample = compare_audio_codes(sample_df, main_df)
            
            # Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Sample Records", len(sample_df))
            col2.metric("Main Records", len(main_df))
            col3.metric("Accepted Matches", len(accepted_matching), 
                        f"{len(accepted_sample)} in sample")
            col4.metric("Rejected Matches", len(rejected_matching), 
                        f"{len(rejected_sample)} in sample")
            col5.metric("Remaining Records", len(remaining_records), 
                        f"{len(remaining_records)/len(main_df)*100:.1f}%")
            
            # Results tabs
            tab1, tab2, tab3 = st.tabs(["🟢 Accepted Matches", "🔴 Rejected Matches", "⚠️ Rejected by Data verification"])
            
            with tab1:
                if len(accepted_matching) > 0:
                    st.success(f"Found {len(accepted_matching)} accepted matches")
                    st.dataframe(accepted_matching, use_container_width=True)
                else:
                    st.info("No accepted matches found")
                    st.write("Sample Accepted Audio Codes:")
                    st.write(accepted_sample['Audio Code'].head().tolist())
            
            with tab2:
                if len(rejected_matching) > 0:
                    st.success(f"Found {len(rejected_matching)} rejected matches")
                    st.dataframe(rejected_matching, use_container_width=True)
                else:
                    st.info("No rejected matches found")
                    st.write("Sample Rejected Audio Codes:")
                    st.write(rejected_sample['Audio Code'].head().tolist())
            
            with tab3:
                if len(remaining_records) > 0:
                    st.warning(f"Found {len(remaining_records)} remaining records")
                    st.dataframe(remaining_records, use_container_width=True)
                    
                    # Show some bg_audio values for debugging
                    st.write("Sample bg_audio values from remaining records:")
                    st.write(remaining_records['bg_audio'].head().tolist())
                else:
                    st.info("No remaining records found")
            
            # Debug info
            with st.expander("🐛 Debug Information"):
                st.write("**Sample Accepted Audio Codes (first 10):**")
                st.write(accepted_sample['Audio Code'].head(10).tolist())
                
                st.write("**Sample Rejected Audio Codes (first 10):**")
                st.write(rejected_sample['Audio Code'].head(10).tolist())
                
                st.write("**Main bg_audio extracted codes (first 10):**")
                main_codes = main_df['bg_audio'].apply(extract_audio_code_from_bg_audio).dropna().head(10).tolist()
                st.write(main_codes)
                
                st.write("**Data Types Info:**")
                st.write(f"Sample Audio Code type: {sample_df['Audio Code'].dtype}")
                st.write(f"Main bg_audio type: {main_df['bg_audio'].dtype}")
            
            # Download option
            st.subheader("💾 Download Results")
            excel_data = convert_df_to_excel(accepted_matching, rejected_matching, remaining_records)
            st.download_button(
                label="📥 Download All Results as Excel",
                data=excel_data,
                file_name="audio_comparison_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
            st.exception(e)  # Show full error traceback for debugging
    
    # Instructions
    st.markdown("---")
    st.subheader("📋 Instructions")
    st.markdown("""
    1. **Sample File Requirements**:
       - Must contain columns: `Audio Code` and `Accepted / Rejected`
       - `Accepted / Rejected` values must be "Accepted" or "Rejected" (case insensitive)
       - Audio codes can be numbers or strings (will be cleaned automatically)
    
    2. **Main File Requirements**:
       - Must contain `bg_audio` column
       - Can have file extensions like `.m4a`, `.mp3`, etc. (will be removed automatically)
    
    3. **Troubleshooting**:
       - If no matches are found, check the "Debug Information" section
       - Ensure audio codes in both files are compatible (same numeric values)
       - Check for leading/trailing spaces in your data
    """)

if __name__ == "__main__":
    main()
