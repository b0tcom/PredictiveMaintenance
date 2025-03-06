import streamlit as st
import pandas as pd
from datetime import datetime

def show_downloads(processed_data, equipment_data):
    """
    Display a dedicated downloads page with various report formats and evidence options
    
    Parameters:
    processed_data (dict): Processed sensor data with statistics and predictions
    equipment_data (DataFrame): Equipment metadata
    """
    st.header("📥 Downloads and Reports")
    
    # Introduction
    st.markdown("""
    This page allows you to download various reports and supporting evidence files 
    for your predictive maintenance system. Select from the options below to generate 
    the type of report or documentation you need.
    """)
    
    # Create columns for layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Maintenance Reports")
        
        # Report Type Selection
        report_type = st.radio(
            "Report Type:",
            ["Equipment Status Summary", "Maintenance Alerts", "Predictive Analysis", "Performance Metrics", "Complete System Report"],
            index=4
        )
        
        # Format selection
        st.subheader("Format Options")
        format_options = [
            'csv', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 
            'rtf', 'txt', 'jpg', 'jpeg', 'tiff', 'tif', 'xps'
        ]
        
        selected_format = st.selectbox(
            "Select Format:",
            format_options
        )
        
        # Time period selection
        st.subheader("Time Period")
        time_period = st.radio(
            "Select time period:",
            ["Last 24 Hours", "Last Week", "Last Month", "Last Quarter", "Last Year", "Custom Range"]
        )
        
        if time_period == "Custom Range":
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Start Date", datetime.now().date())
            with col_date2:
                end_date = st.date_input("End Date", datetime.now().date())
        
        # Generate and provide download button
        st.subheader("Generate Report")
        
        # Create CSV download button - for demo all reports use the same data
        def convert_to_csv():
            # Get equipment data with predictions
            equipment_df = equipment_data.copy()
            
            # Add prediction data
            for idx, row in equipment_df.iterrows():
                machine_id = row['machine_id']
                if machine_id in processed_data['predictions']:
                    prediction = processed_data['predictions'][machine_id]
                    equipment_df.at[idx, 'failure_probability'] = f"{prediction['failure_probability'] * 100:.1f}%"
                    equipment_df.at[idx, 'days_to_failure'] = prediction['days_to_failure']
                    
                    if machine_id in processed_data['recommendations']:
                        recommendation = processed_data['recommendations'][machine_id]
                        equipment_df.at[idx, 'maintenance_urgency'] = recommendation['urgency']
                        equipment_df.at[idx, 'recommendation'] = recommendation['message']
                        
            return equipment_df.to_csv(index=False)
            
        csv_data = convert_to_csv()
        
        # Set appropriate mime types based on format
        mime_types = {
            'csv': "text/csv",
            'pdf': "application/pdf",
            'doc': "application/msword",
            'docx': "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            'xls': "application/vnd.ms-excel",
            'xlsx': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            'rtf': "application/rtf",
            'txt': "text/plain",
            'jpg': "image/jpeg",
            'jpeg': "image/jpeg",
            'tiff': "image/tiff",
            'tif': "image/tiff",
            'xps': "application/oxps"
        }
        
        report_name = report_type.lower().replace(" ", "_")
        
        st.download_button(
            label="📊 Download Report",
            data=csv_data,
            file_name=f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.{selected_format}",
            mime=mime_types.get(selected_format, "text/csv"),
            help=f"Download {report_type} in {selected_format.upper()} format"
        )
        
        st.caption("Note: This is a demo. All formats download as CSV data with appropriate file extension.")
        
    with col2:
        st.subheader("Supporting Evidence")
        
        st.markdown("""
        Select the types of supporting evidence to include with your report.
        These documents help validate your maintenance decisions and processes.
        """)
        
        # Evidence options
        evidence_options = [
            "Project planning documents",
            "Records of resources allocated to the project, time sheets",
            "Design of experiments",
            "Project records, laboratory notebooks",
            "Design, system architecture, and source code",
            "Records of trial runs",
            "Progress reports, minutes of project meetings",
            "Test protocols, test data, analysis of test results, conclusions",
            "Photographs and videos",
            "Samples, prototypes, scrap, or other artefacts",
            "Contracts"
        ]
        
        selected_evidence = st.multiselect(
            "Select supporting evidence to include:",
            evidence_options
        )
        
        if selected_evidence:
            st.success(f"Selected {len(selected_evidence)} evidence items to include.")
            
            # In a real application, we would prepare these documents
            # For the demo, we'll just show a button that downloads a placeholder
            
            st.download_button(
                label="📎 Download Evidence Package",
                data="This is a placeholder for the selected evidence documents.",
                file_name=f"evidence_package_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                help="Download selected evidence files (demo)"
            )
            
            st.caption("Note: This is a demo. The evidence package contains placeholder text.")
        
        # Additional information
        st.subheader("Documentation")
        
        st.markdown("""
        Standard documentation available for download:
        """)
        
        doc_options = {
            "User Manual": "Complete instructions for system operation",
            "Technical Specifications": "Detailed technical information",
            "Installation Guide": "System setup and configuration",
            "API Documentation": "For system integration",
            "Compliance Certificates": "Industry and regulatory compliance"
        }
        
        for doc_name, doc_desc in doc_options.items():
            st.markdown(f"**{doc_name}**: {doc_desc}")
            st.download_button(
                label=f"Download {doc_name}",
                data=f"This is a placeholder for the {doc_name} document.",
                file_name=f"{doc_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                help=f"Download {doc_name} (demo)"
            )