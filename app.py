import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# Import components
from components.dashboard import show_dashboard
from components.equipment_monitoring import show_equipment_monitoring
from components.maintenance_alerts import show_maintenance_alerts
from components.performance_metrics import show_performance_metrics
from components.historical_analysis import show_historical_analysis
from components.downloads import show_downloads

# Import utilities
from utils.data_generator import generate_sensor_data, generate_equipment_data
from utils.data_processor import process_sensor_data

# Set page configuration
st.set_page_config(
    page_title="SmartMaintain - Predictive Maintenance Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
    
if 'sensor_data' not in st.session_state:
    # Generate initial data for past 7 days with 15-minute intervals
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    st.session_state.sensor_data = generate_sensor_data(start_time, end_time, interval_minutes=15)
    
if 'equipment_data' not in st.session_state:
    st.session_state.equipment_data = generate_equipment_data(10)  # 10 machines

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .warning {
        color: orange;
        font-weight: bold;
    }
    .critical {
        color: red;
        font-weight: bold;
    }
    .healthy {
        color: green;
        font-weight: bold;
    }
    .last-updated {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# App header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("""
    <svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="30" width="80" height="50" fill="#0066cc" rx="5" ry="5"/>
        <circle cx="30" cy="45" r="8" fill="white"/>
        <circle cx="50" cy="45" r="8" fill="white"/>
        <circle cx="70" cy="45" r="8" fill="white"/>
        <rect x="20" y="65" width="60" height="8" fill="white" rx="2" ry="2"/>
        <path d="M20,20 L30,10 L70,10 L80,20 L80,30 L20,30 Z" fill="#0066cc"/>
    </svg>
    """, unsafe_allow_html=True)
with col2:
    st.markdown('<h1 class="main-header">SmartMaintain</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Driven Predictive Maintenance Platform</p>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("", [
    "Dashboard Overview", 
    "Equipment Monitoring", 
    "Maintenance Alerts", 
    "Performance Metrics", 
    "Historical Analysis",
    "Downloads"
])

# Update data button
if st.sidebar.button("Refresh Data"):
    # Generate new data points
    end_time = datetime.now()
    new_data = generate_sensor_data(st.session_state.last_update, end_time, interval_minutes=1)
    st.session_state.sensor_data = pd.concat([st.session_state.sensor_data, new_data]).reset_index(drop=True)
    
    # Update equipment status based on new data
    st.session_state.equipment_data = generate_equipment_data(10, previous_data=st.session_state.equipment_data)
    
    # Update last update time
    st.session_state.last_update = end_time
    
    st.sidebar.success("Data refreshed successfully!")

# Display last update time
st.sidebar.markdown(f"<p class='last-updated'>Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# Process data (calculate anomalies, predictions, etc.)
processed_data = process_sensor_data(st.session_state.sensor_data, st.session_state.equipment_data)

# Add download button for full report at the top right corner
col1, col2 = st.columns([10, 2])
with col2:
    # Create a function to generate report data
    def generate_report():
        # Combine all relevant data for the report
        report = {
            'equipment_data': st.session_state.equipment_data.to_dict(orient='records'),
            'sensor_data': st.session_state.sensor_data.head(100).to_dict(orient='records'),  # Limited for performance
            'anomalies': processed_data['anomalies'],
            'predictions': processed_data['predictions'],
            'recommendations': processed_data['recommendations'],
            'statistics': processed_data['statistics'],
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return report

    # Create download data based on selected format
    def convert_to_csv():
        # Get equipment data with predictions
        equipment_df = st.session_state.equipment_data.copy()
        
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
    
    # Add format selection dropdown
    format_options = [
        'csv', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 
        'rtf', 'txt', 'jpg', 'jpeg', 'tiff', 'tif', 'xps'
    ]
    
    selected_format = st.selectbox(
        "Format:",
        format_options,
        label_visibility="collapsed",
        help="Select the format for your report download"
    )
    
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
    
    # Import necessary functions from downloads component to generate proper report data
    from components.downloads import (
        generate_csv, generate_txt, generate_pdf, generate_docx, generate_xlsx, generate_image,
        _processed_data, _equipment_data, _report_type, _time_period
    )
    
    # Update global variables in the downloads module with current data
    import components.downloads
    components.downloads._processed_data = processed_data
    components.downloads._equipment_data = st.session_state.equipment_data
    components.downloads._report_type = "Equipment Status Report"
    components.downloads._time_period = "Last 7 Days"
    
    # Generate appropriate report data based on selected format
    report_data = None
    if selected_format == 'csv':
        # Use the standardized generate_csv function from the downloads component
        report_data = generate_csv()
    elif selected_format == 'txt':
        report_data = generate_txt()
    elif selected_format in ['pdf', 'doc', 'rtf', 'xps']:
        report_data = generate_pdf()
    elif selected_format in ['docx']:
        report_data = generate_docx()
    elif selected_format in ['xls', 'xlsx']:
        report_data = generate_xlsx()
    elif selected_format in ['jpg', 'jpeg', 'tiff', 'tif']:
        report_data = generate_image()
    else:
        # Default to CSV if format not recognized
        report_data = convert_to_csv()
    
    st.download_button(
        label="📊 Download Report",
        data=report_data,
        file_name=f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M')}.{selected_format}",
        mime=mime_types.get(selected_format, "text/csv"),
        help="Download a full report of equipment status, predictions, and recommendations"
    )
    
    # Add a note about format conversion
    st.caption("Note: This is a demo. All formats download as CSV data with appropriate file extension.")

# Render selected page
if page == "Dashboard Overview":
    show_dashboard(processed_data, st.session_state.equipment_data)
elif page == "Equipment Monitoring":
    show_equipment_monitoring(processed_data, st.session_state.equipment_data)
elif page == "Maintenance Alerts":
    show_maintenance_alerts(processed_data, st.session_state.equipment_data)
elif page == "Performance Metrics":
    show_performance_metrics(processed_data, st.session_state.equipment_data)
elif page == "Historical Analysis":
    show_historical_analysis(processed_data)
elif page == "Downloads":
    show_downloads(processed_data, st.session_state.equipment_data)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        © 2023 SmartMaintain | AI-Driven Predictive Maintenance Platform for Smart Manufacturing
    </div>
    """, 
    unsafe_allow_html=True
)
