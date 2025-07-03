import streamlit as st
import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import io

def load_excel_file(file_path):
    """Load Excel file and return DataFrame"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading file {file_path}: {str(e)}")
        return None

def extract_audio_code(filename):
    """Extract audio code from filename by removing .m4a extension"""
    if isinstance(filename, str) and filename.endswith('.m4a'):
        return filename.replace('.m4a', '')
    return filename

def compare_and_filter_data(main_df, sample_df):
    """Compare main excel data with sample excel and filter based on Accept/Reject"""
    
    # Clean the audio codes in main file
    main_df['audio_code_clean'] = main_df['bg_audio'].apply(extract_audio_code)
    
    # Clean the audio codes in sample file - convert to string first
    sample_df['Audio Code'] = sample_df['Audio Code'].astype(str)
    
    # Create dictionaries for accepted and rejected audio codes
    accepted_codes = set(sample_df[sample_df['Accepted / Rejected'].str.strip().str.lower() == 'accept']['Audio Code'].values)
    rejected_codes = set(sample_df[sample_df['Accepted / Rejected'].str.strip().str.lower() == 'reject']['Audio Code'].values)
    
    # Filter main data based on accepted and rejected codes
    accepted_data = main_df[main_df['audio_code_clean'].isin(accepted_codes)].copy()
    rejected_data = main_df[main_df['audio_code_clean'].isin(rejected_codes)].copy()
    
    # Remove the temporary column
    accepted_data = accepted_data.drop('audio_code_clean', axis=1)
    rejected_data = rejected_data.drop('audio_code_clean', axis=1)
    
    return accepted_data, rejected_data, accepted_codes, rejected_codes

def create_excel_with_worksheets(accepted_data, rejected_data, output_filename):
    """Create Excel file with separate worksheets for accepted and rejected data"""
    
    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write accepted data to 'Accepted' worksheet
        if not accepted_data.empty:
            accepted_data.to_excel(writer, sheet_name='Accepted', index=False)
        else:
            # Create empty sheet if no accepted data
            pd.DataFrame().to_excel(writer, sheet_name='Accepted', index=False)
        
        # Write rejected data to 'Rejected' worksheet
        if not rejected_data.empty:
            rejected_data.to_excel(writer, sheet_name='Rejected', index=False)
        else:
            # Create empty sheet if no rejected data
            pd.DataFrame().to_excel(writer, sheet_name='Rejected', index=False)
    
    output.seek(0)
    return output

def main():
    st.title("Excel File Comparison Tool")
    st.markdown("Compare main Excel file with sample Excel file and create separate worksheets for Accepted and Rejected data")
    
    # File upload section
    st.header("Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CSV Main Excel File")
        main_file = st.file_uploader("Upload CSV Excel File (30-Pallavaram Landscape S.xlsx)", type=['xlsx', 'xls'])
        
    with col2:
        st.subheader("QC Excel File")
        sample_file = st.file_uploader("Upload QC Excel File (30AC.xlsx)", type=['xlsx', 'xls'])
    
    if main_file and sample_file:
        try:
            # Load the files
            main_df = pd.read_excel(main_file)
            sample_df = pd.read_excel(sample_file)
            
            # Display file information
            st.success("Files loaded successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Main File Info")
                st.write(f"Rows: {len(main_df)}")
                st.write(f"Columns: {len(main_df.columns)}")
                if 'bg_audio' in main_df.columns:
                    st.write("✅ 'bg_audio' column found")
                else:
                    st.error("❌ 'bg_audio' column not found")
                
                with st.expander("Show Main File Preview"):
                    st.dataframe(main_df.head())
            
            with col2:
                st.subheader("Sample File Info")
                st.write(f"Rows: {len(sample_df)}")
                st.write(f"Columns: {len(sample_df.columns)}")
                if 'Accepted / Rejected' in sample_df.columns:
                    st.write("✅ 'Accepted / Rejected' column found")
                else:
                    st.error("❌ 'Accepted / Rejected' column not found")
                
                with st.expander("Show Sample File Preview"):
                    st.dataframe(sample_df.head())
            
            # Check if required columns exist
            if 'bg_audio' in main_df.columns and 'Accepted / Rejected' in sample_df.columns:
                
                # Process button
                if st.button("Process Files", type="primary"):
                    with st.spinner("Processing files..."):
                        # Compare and filter data
                        accepted_data, rejected_data, accepted_codes, rejected_codes = compare_and_filter_data(main_df, sample_df)
                        
                        # Display results
                        st.header("Processing Results")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Accepted Codes", len(accepted_codes))
                            st.metric("Accepted Data Rows", len(accepted_data))
                        
                        with col2:
                            st.metric("Total Rejected Codes", len(rejected_codes))
                            st.metric("Rejected Data Rows", len(rejected_data))
                        
                        with col3:
                            st.metric("Total Main File Rows", len(main_df))
                            st.metric("Matched Rows", len(accepted_data) + len(rejected_data))
                        
                        # Show data previews
                        if not accepted_data.empty:
                            with st.expander("Accepted Data Preview"):
                                st.dataframe(accepted_data.head(10))
                        
                        if not rejected_data.empty:
                            with st.expander("Rejected Data Preview"):
                                st.dataframe(rejected_data.head(10))
                        
                        # Create Excel file with separate worksheets
                        excel_output = create_excel_with_worksheets(accepted_data, rejected_data, "Filtered_Data.xlsx")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Filtered Excel File",
                            data=excel_output,
                            file_name="Filtered_Data_with_Worksheets.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        st.success("✅ Processing completed! The Excel file contains two worksheets: 'Accepted' and 'Rejected'")
                        
                        # Summary
                        st.info(f"""
                        **Summary:**
                        - Found {len(accepted_codes)} accepted audio codes
                        - Found {len(rejected_codes)} rejected audio codes
                        - Extracted {len(accepted_data)} rows for accepted data
                        - Extracted {len(rejected_data)} rows for rejected data
                        - Created Excel file with separate 'Accepted' and 'Rejected' worksheets
                        """)
            
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.error("Please make sure your files have the correct format and column names.")

if __name__ == "__main__":
    main()
