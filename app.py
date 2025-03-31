import streamlit as st
import pandas as pd
import numpy as np
import time
import os
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
from utils.ui_helper import (load_css, render_logo, render_navbar_item, 
                            display_premium_header, display_metric_card,
                            display_alert_item, format_status_html)

# Set page configuration
st.set_page_config(
    page_title="PredictMaint AI - Premium Predictive Maintenance Platform",
    page_icon="⚙️",
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

# Load premium UI theme CSS
load_css()

# App header with premium logo
col1, col2 = st.columns([1, 5])
with col1:
    logo_file = os.path.join("assets", "images", "logo.svg")
    if os.path.exists(logo_file):
        with open(logo_file, "r") as f:
            logo_svg = f.read()
        st.markdown(f"""
        <div style="margin-top: 10px;">
            {logo_svg}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.image("https://via.placeholder.com/80", width=80)
        
with col2:
    st.markdown('<h1 style="font-family: var(--font-display); font-size: 2.5rem; color: var(--primary-800); margin-bottom: 0;">PredictMaint AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; color: var(--neutral-600); margin-top: 0;">Premium AI-Driven Predictive Maintenance Platform</p>', unsafe_allow_html=True)

# Sidebar navigation with premium UI
st.sidebar.markdown("""
<div style="background-color: var(--primary-900); padding: 16px; margin: -16px -16px 20px -16px; text-align: center;">
    <h1 style="color: white; font-family: var(--font-display); font-size: 1.5rem; margin-bottom: 0;">PredictMaint AI</h1>
    <p style="color: var(--primary-300); font-size: 0.8rem; margin-top: 4px;">PREMIUM EDITION</p>
</div>
<div class="nav-group">
    <div class="nav-group-title">MAIN NAVIGATION</div>
</div>
""", unsafe_allow_html=True)

# Create the navigation options with icons
navigation_options = {
    "Dashboard Overview": "dashboard",
    "Equipment Monitoring": "equipment",
    "Maintenance Alerts": "alerts",
    "Performance Metrics": "metrics",
    "Historical Analysis": "history",
    "Downloads": "downloads"
}

# Display navigation icons and labels
page = st.sidebar.radio("", list(navigation_options.keys()), label_visibility="collapsed")

# Display the selected page with premium styling
st.sidebar.markdown("""
<style>
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0.5rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: var(--primary-100);
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label[aria-checked="true"] {
        background-color: rgba(255, 255, 255, 0.15);
        border-left: 3px solid var(--amber-500);
    }
</style>
""", unsafe_allow_html=True)

# Add sidebar separator
st.sidebar.markdown("""
<div style="margin: 20px 0; border-top: 1px solid var(--primary-600); opacity: 0.3;"></div>
<div class="nav-group">
    <div class="nav-group-title">ACTIONS</div>
</div>
""", unsafe_allow_html=True)

# Update data button with premium styling
refresh_button = st.sidebar.button(
    "🔄 Refresh Data", 
    help="Update sensor data and equipment status with the latest readings"
)

if refresh_button:
    # Show a spinner during data refresh
    with st.sidebar.spinner("Refreshing data..."):
        # Generate new data points
        end_time = datetime.now()
        new_data = generate_sensor_data(st.session_state.last_update, end_time, interval_minutes=1)
        st.session_state.sensor_data = pd.concat([st.session_state.sensor_data, new_data]).reset_index(drop=True)
        
        # Update equipment status based on new data
        st.session_state.equipment_data = generate_equipment_data(10, previous_data=st.session_state.equipment_data)
        
        # Update last update time
        st.session_state.last_update = end_time
        
        # Success message with premium styling
        st.sidebar.markdown("""
        <div style="background-color: var(--success); color: white; padding: 10px; border-radius: 4px; margin-top: 10px;">
            <strong>✅ Data refreshed successfully!</strong>
        </div>
        """, unsafe_allow_html=True)

# Display last update time with premium styling
st.sidebar.markdown(f"""
<div style="margin-top: 20px; padding: 10px; background-color: var(--primary-900); border-radius: 4px; text-align: center;">
    <div style="font-size: 0.7rem; color: var(--primary-300); margin-bottom: 4px;">LAST UPDATED</div>
    <div style="font-family: var(--font-mono); font-size: 0.9rem; color: var(--neutral-100);">
        {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
""", unsafe_allow_html=True)

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
        report_data = generate_csv()
    
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

# Premium Footer with enhanced styling
st.markdown("""
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--neutral-300);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div>
            <h3 style="font-family: var(--font-display); color: var(--primary-800); margin: 0; font-size: 1.2rem;">PredictMaint AI</h3>
            <p style="color: var(--neutral-600); margin: 5px 0 0 0; font-size: 0.8rem;">Premium AI-Driven Predictive Maintenance Platform</p>
        </div>
        <div style="display: flex; gap: 15px;">
            <span style="color: var(--primary-600); cursor: pointer;">Documentation</span>
            <span style="color: var(--primary-600); cursor: pointer;">Support</span>
            <span style="color: var(--primary-600); cursor: pointer;">API</span>
            <span style="color: var(--primary-600); cursor: pointer;">Contact</span>
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
        <div style="color: var(--neutral-500); font-size: 0.75rem;">
            © 2025 PredictMaint AI | All Rights Reserved
        </div>
        <div style="color: var(--neutral-500); font-size: 0.75rem; display: flex; gap: 10px;">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>Version 2.4.1 Premium</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
