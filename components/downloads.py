import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
import zipfile
from datetime import datetime

# Import libraries for specific file formats
from fpdf import FPDF
from docx import Document
import xlsxwriter
from PIL import Image, ImageDraw, ImageFont

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
        
        # Functions to generate various file formats
        def get_enhanced_equipment_df():
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
            
            return equipment_df
            
        def get_sensor_data_summary():
            """Get a summary of recent sensor data"""
            # Get the most recent readings for each machine
            sensor_data = processed_data['sensor_data'].copy()
            sensor_summary = []
            
            for machine_id in sensor_data['machine_id'].unique():
                machine_data = sensor_data[sensor_data['machine_id'] == machine_id]
                latest_data = machine_data.sort_values('timestamp').iloc[-1].to_dict()
                sensor_summary.append(latest_data)
                
            return pd.DataFrame(sensor_summary)
            
        def get_anomaly_data():
            """Get anomaly data in a structured format"""
            anomaly_data = []
            
            for machine_id, anomaly_info in processed_data['anomalies'].items():
                row = {
                    'machine_id': machine_id,
                    'has_anomalies': anomaly_info['has_anomalies'],
                    'anomaly_score': f"{anomaly_info['anomaly_score']:.3f}",
                    'affected_sensors': ', '.join(anomaly_info['affected_sensors']),
                    'severity': anomaly_info['severity'],
                    'detected_at': anomaly_info.get('detected_at', 'Unknown')
                }
                anomaly_data.append(row)
                
            return pd.DataFrame(anomaly_data)
            
        def get_performance_metrics():
            """Get performance metrics for all machines"""
            metrics_data = []
            
            # For each machine, calculate or extract key performance metrics
            for machine_id in equipment_data['machine_id'].unique():
                if machine_id in processed_data['statistics']:
                    stats = processed_data['statistics'][machine_id]
                    
                    # Calculate overall health score (example metric)
                    temp_health = 100 - max(0, min(100, (stats['temperature']['current'] - 60) * 2))
                    vibration_health = 100 - max(0, min(100, stats['vibration']['current'] * 10))
                    power_health = 100 - max(0, min(100, abs(stats['power']['current'] - 90)))
                    
                    overall_health = (temp_health + vibration_health + power_health) / 3
                    
                    # Calculate OEE (Overall Equipment Effectiveness) - simplified example
                    availability = 0.95  # 95% uptime
                    performance = 0.90   # 90% of max speed
                    quality = 0.98       # 98% good parts
                    
                    # Adjust based on machine status
                    machine_info = equipment_data[equipment_data['machine_id'] == machine_id].iloc[0]
                    if machine_info['status'] == 'Maintenance':
                        availability = 0.0
                    elif machine_info['status'] == 'Warning':
                        availability = 0.8
                        performance = 0.7
                    elif machine_info['status'] == 'Idle':
                        performance = 0.0
                        
                    oee = availability * performance * quality * 100
                    
                    # Add to metrics data
                    metrics_data.append({
                        'machine_id': machine_id,
                        'overall_health': f"{overall_health:.1f}%",
                        'oee': f"{oee:.1f}%",
                        'availability': f"{availability*100:.1f}%",
                        'performance': f"{performance*100:.1f}%",
                        'quality': f"{quality*100:.1f}%",
                        'temperature': f"{stats['temperature']['current']:.1f}°C",
                        'vibration': f"{stats['vibration']['current']:.2f} mm/s",
                        'power_usage': f"{stats['power']['current']:.1f}%"
                    })
            
            return pd.DataFrame(metrics_data)
                    
        def get_historical_trends():
            """Get historical trends from sensor data"""
            sensor_data = processed_data['sensor_data'].copy()
            
            # Group by day and machine, calculate daily averages
            sensor_data['date'] = pd.to_datetime(sensor_data['timestamp']).dt.date
            daily_avg = sensor_data.groupby(['date', 'machine_id']).mean(numeric_only=True).reset_index()
            
            return daily_avg
            
        def generate_csv():
            """Generate CSV file from all application data"""
            # Create an output buffer for ZIP file
            zip_buffer = io.BytesIO()
            
            # Create a ZIP file to contain multiple CSV files
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add equipment data
                equipment_csv = get_enhanced_equipment_df().to_csv(index=False)
                zipf.writestr('equipment_status.csv', equipment_csv)
                
                # Add sensor data summary
                sensor_csv = get_sensor_data_summary().to_csv(index=False)
                zipf.writestr('sensor_readings.csv', sensor_csv)
                
                # Add anomaly data
                anomaly_csv = get_anomaly_data().to_csv(index=False)
                zipf.writestr('anomaly_detection.csv', anomaly_csv)
                
                # Add performance metrics
                metrics_csv = get_performance_metrics().to_csv(index=False)
                zipf.writestr('performance_metrics.csv', metrics_csv)
                
                # Add historical trends if available
                historical_csv = get_historical_trends().to_csv(index=False)
                zipf.writestr('historical_trends.csv', historical_csv)
            
            # Reset buffer position
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        def generate_txt():
            """Generate comprehensive text report from all application data"""
            equipment_df = get_enhanced_equipment_df()
            sensor_data = get_sensor_data_summary()
            anomaly_data = get_anomaly_data()
            metrics_data = get_performance_metrics()
            
            # Create a text report
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report = [
                f"SmartMaintain - {report_type}",
                f"Generated: {current_time}",
                f"Time Period: {time_period}",
                "-" * 80,
                "\n=== EXECUTIVE SUMMARY ===\n"
            ]
            
            # Add executive summary
            critical_count = len([r for _, r in equipment_df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Immediate'])
            warning_count = len([r for _, r in equipment_df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Soon'])
            anomaly_count = len([r for _, r in anomaly_data.iterrows() if r['has_anomalies'] == True])
            
            report.append(f"Total Equipment: {len(equipment_df)}")
            report.append(f"Critical Maintenance Alerts: {critical_count}")
            report.append(f"Warning Maintenance Alerts: {warning_count}")
            report.append(f"Detected Anomalies: {anomaly_count}")
            report.append("")
            
            # Add key metrics
            if not metrics_data.empty:
                avg_health = metrics_data['overall_health'].str.rstrip('%').astype(float).mean()
                avg_oee = metrics_data['oee'].str.rstrip('%').astype(float).mean()
                report.append(f"Average Equipment Health: {avg_health:.1f}%")
                report.append(f"Average OEE: {avg_oee:.1f}%")
            report.append("")
            
            # Critical Issues Section
            report.append("\n=== CRITICAL ISSUES ===\n")
            
            # List machines with immediate maintenance needs
            critical_machines = equipment_df[equipment_df['maintenance_urgency'] == 'Immediate']
            if len(critical_machines) > 0:
                report.append("Machines Requiring Immediate Attention:")
                for _, row in critical_machines.iterrows():
                    report.append(f"- {row['machine_id']} ({row['machine_type']})")
                    report.append(f"  Failure Probability: {row['failure_probability']}")
                    report.append(f"  Days to Failure: {row['days_to_failure']}")
                    report.append(f"  Recommendation: {row.get('recommendation', 'No recommendation')}")
                    report.append("")
            else:
                report.append("No machines require immediate attention.")
                report.append("")
            
            # List significant anomalies
            if not anomaly_data.empty:
                severe_anomalies = anomaly_data[anomaly_data['severity'] == 'High']
                if len(severe_anomalies) > 0:
                    report.append("Significant Anomalies Detected:")
                    for _, row in severe_anomalies.iterrows():
                        report.append(f"- {row['machine_id']}")
                        report.append(f"  Anomaly Score: {row['anomaly_score']}")
                        report.append(f"  Affected Sensors: {row['affected_sensors']}")
                        report.append(f"  Detected At: {row['detected_at']}")
                        report.append("")
            
            # Equipment Details Section
            report.append("\n=== DETAILED EQUIPMENT STATUS ===\n")
            
            # Add equipment summary for all machines
            for _, row in equipment_df.iterrows():
                report.append(f"Machine: {row['machine_id']} ({row['machine_type']})")
                report.append(f"  Status: {row['status']}")
                report.append(f"  Failure Probability: {row['failure_probability']}")
                report.append(f"  Days to Failure: {row['days_to_failure']}")
                report.append(f"  Maintenance Urgency: {row.get('maintenance_urgency', 'Unknown')}")
                report.append(f"  Recommendation: {row.get('recommendation', 'No recommendation')}")
                report.append("")
                
                # Add latest sensor readings for this machine
                if not sensor_data.empty:
                    machine_sensors = sensor_data[sensor_data['machine_id'] == row['machine_id']]
                    if not machine_sensors.empty:
                        latest = machine_sensors.iloc[0]
                        report.append(f"  Latest Sensor Readings:")
                        report.append(f"    Timestamp: {latest.get('timestamp', 'Unknown')}")
                        report.append(f"    Temperature: {latest.get('temperature', 'Unknown'):.1f}°C")
                        report.append(f"    Vibration: {latest.get('vibration', 'Unknown'):.2f} mm/s")
                        report.append(f"    Power: {latest.get('power', 'Unknown'):.1f}%")
                        report.append("")
            
            # Performance Metrics Section
            report.append("\n=== PERFORMANCE METRICS ===\n")
            
            if not metrics_data.empty:
                for _, row in metrics_data.iterrows():
                    report.append(f"Machine: {row['machine_id']}")
                    report.append(f"  Overall Health: {row['overall_health']}")
                    report.append(f"  OEE: {row['oee']}")
                    report.append(f"  Availability: {row['availability']}")
                    report.append(f"  Performance: {row['performance']}")
                    report.append(f"  Quality: {row['quality']}")
                    report.append("")
            
            # Join and return
            return "\n".join(report)
            
        def generate_pdf():
            """Generate comprehensive PDF report with data from all components"""
            # Get all the data we need
            equipment_df = get_enhanced_equipment_df()
            sensor_data = get_sensor_data_summary()
            anomaly_data = get_anomaly_data()
            metrics_data = get_performance_metrics()
            
            # Create PDF document
            pdf = FPDF()
            pdf.add_page()
            
            # Set fonts
            pdf.set_font("Arial", "B", 16)
            
            # Title
            pdf.cell(0, 10, f"SmartMaintain - {report_type}", 0, 1, "C")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
            pdf.cell(0, 10, f"Time Period: {time_period}", 0, 1, "C")
            pdf.ln(5)
            
            # Executive Summary Section
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "EXECUTIVE SUMMARY", 0, 1)
            pdf.ln(2)
            
            # Calculate summary statistics
            critical_count = len([r for _, r in equipment_df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Immediate'])
            warning_count = len([r for _, r in equipment_df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Soon'])
            anomaly_count = len([r for _, r in anomaly_data.iterrows() if r['has_anomalies'] == True])
            
            # Add executive summary in bullet points
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, f"• Total Equipment: {len(equipment_df)}", 0, 1)
            pdf.cell(0, 8, f"• Critical Maintenance Alerts: {critical_count}", 0, 1)
            pdf.cell(0, 8, f"• Warning Maintenance Alerts: {warning_count}", 0, 1)
            pdf.cell(0, 8, f"• Detected Anomalies: {anomaly_count}", 0, 1)
            
            # Add key metrics if available
            if not metrics_data.empty:
                avg_health = metrics_data['overall_health'].str.rstrip('%').astype(float).mean()
                avg_oee = metrics_data['oee'].str.rstrip('%').astype(float).mean()
                pdf.cell(0, 8, f"• Average Equipment Health: {avg_health:.1f}%", 0, 1)
                pdf.cell(0, 8, f"• Average OEE: {avg_oee:.1f}%", 0, 1)
            
            # Equipment data
            pdf.ln(5)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "EQUIPMENT STATUS SUMMARY", 0, 1)
            pdf.ln(2)
            
            # Create table header
            pdf.set_font("Arial", "B", 8)
            pdf.cell(20, 8, "Machine ID", 1, 0, "C")
            pdf.cell(20, 8, "Type", 1, 0, "C")
            pdf.cell(20, 8, "Status", 1, 0, "C")
            pdf.cell(25, 8, "Failure Prob.", 1, 0, "C")
            pdf.cell(20, 8, "Days to Fail", 1, 0, "C")
            pdf.cell(20, 8, "Urgency", 1, 0, "C")
            pdf.cell(50, 8, "Recommendation", 1, 1, "C")
            
            # Add data rows
            pdf.set_font("Arial", "", 7)
            
            for _, row in equipment_df.iterrows():
                pdf.cell(20, 8, str(row['machine_id']), 1, 0)
                pdf.cell(20, 8, str(row['machine_type']), 1, 0)
                pdf.cell(20, 8, str(row['status']), 1, 0)
                pdf.cell(25, 8, str(row.get('failure_probability', 'N/A')), 1, 0)
                pdf.cell(20, 8, str(row.get('days_to_failure', 'N/A')), 1, 0)
                pdf.cell(20, 8, str(row.get('maintenance_urgency', 'Unknown')), 1, 0)
                
                # Truncate recommendation to fit in cell
                recommendation = str(row.get('recommendation', 'No recommendation'))
                if len(recommendation) > 45:
                    recommendation = recommendation[:42] + '...'
                pdf.cell(50, 8, recommendation, 1, 1)
            
            # Critical Issues Section
            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "CRITICAL ISSUES", 0, 1)
            
            # List machines with immediate maintenance needs
            critical_machines = equipment_df[equipment_df['maintenance_urgency'] == 'Immediate']
            
            if len(critical_machines) > 0:
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 8, "Machines Requiring Immediate Attention:", 0, 1)
                pdf.set_font("Arial", "", 10)
                
                for _, row in critical_machines.iterrows():
                    pdf.cell(10, 8, "•", 0, 0)
                    pdf.cell(0, 8, f"{row['machine_id']} ({row['machine_type']}): {row.get('recommendation', '')}", 0, 1)
            else:
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 8, "No machines require immediate attention.", 0, 1)
            
            # Anomaly Detection Section
            if not anomaly_data.empty:
                pdf.ln(5)
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "ANOMALY DETECTION", 0, 1)
                
                severe_anomalies = anomaly_data[anomaly_data['severity'] == 'High']
                if len(severe_anomalies) > 0:
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(0, 8, "Significant Anomalies Detected:", 0, 1)
                    pdf.set_font("Arial", "", 10)
                    
                    for _, row in severe_anomalies.iterrows():
                        pdf.cell(10, 8, "•", 0, 0)
                        pdf.cell(0, 8, f"{row['machine_id']} - Score: {row['anomaly_score']}, Sensors: {row['affected_sensors']}", 0, 1)
                else:
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(0, 8, "No significant anomalies detected.", 0, 1)
            
            # Performance Metrics Section
            if not metrics_data.empty:
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "PERFORMANCE METRICS", 0, 1)
                pdf.ln(2)
                
                # Create table header for metrics
                pdf.set_font("Arial", "B", 8)
                pdf.cell(20, 8, "Machine ID", 1, 0, "C")
                pdf.cell(25, 8, "Health", 1, 0, "C")
                pdf.cell(20, 8, "OEE", 1, 0, "C")
                pdf.cell(25, 8, "Availability", 1, 0, "C")
                pdf.cell(25, 8, "Performance", 1, 0, "C")
                pdf.cell(20, 8, "Quality", 1, 0, "C")
                pdf.cell(40, 8, "Sensor Readings", 1, 1, "C")
                
                # Add metrics data rows
                pdf.set_font("Arial", "", 7)
                
                for _, row in metrics_data.iterrows():
                    pdf.cell(20, 8, str(row['machine_id']), 1, 0)
                    pdf.cell(25, 8, str(row['overall_health']), 1, 0)
                    pdf.cell(20, 8, str(row['oee']), 1, 0)
                    pdf.cell(25, 8, str(row['availability']), 1, 0)
                    pdf.cell(25, 8, str(row['performance']), 1, 0)
                    pdf.cell(20, 8, str(row['quality']), 1, 0)
                    
                    # Add sensor readings summary
                    readings = f"Temp: {row['temperature']}, Vib: {row['vibration']}, Power: {row['power_usage']}"
                    pdf.cell(40, 8, readings, 1, 1)
            
            # Return PDF as bytes
            return pdf.output(dest='S').encode('latin1')
            
        def generate_docx():
            """Generate comprehensive DOCX report with data from all components"""
            # Get all necessary data
            equipment_df = get_enhanced_equipment_df()
            sensor_data = get_sensor_data_summary()
            anomaly_data = get_anomaly_data()
            metrics_data = get_performance_metrics()
            
            # Create document
            doc = Document()
            
            # Add title
            doc.add_heading(f"SmartMaintain - {report_type}", 0)
            doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph(f"Time Period: {time_period}")
            
            # Executive Summary
            doc.add_heading("Executive Summary", level=1)
            
            # Calculate summary statistics
            critical_count = len([r for _, r in equipment_df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Immediate'])
            warning_count = len([r for _, r in equipment_df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Soon'])
            anomaly_count = len([r for _, r in anomaly_data.iterrows() if r['has_anomalies'] == True])
            
            # Add executive summary in bullet points
            summary = doc.add_paragraph()
            summary.add_run("Key Metrics:\n").bold = True
            summary.add_run(f"• Total Equipment: {len(equipment_df)}\n")
            summary.add_run(f"• Critical Maintenance Alerts: {critical_count}\n")
            summary.add_run(f"• Warning Maintenance Alerts: {warning_count}\n")
            summary.add_run(f"• Detected Anomalies: {anomaly_count}\n")
            
            # Add key metrics if available
            if not metrics_data.empty:
                avg_health = metrics_data['overall_health'].str.rstrip('%').astype(float).mean()
                avg_oee = metrics_data['oee'].str.rstrip('%').astype(float).mean()
                summary.add_run(f"• Average Equipment Health: {avg_health:.1f}%\n")
                summary.add_run(f"• Average OEE: {avg_oee:.1f}%\n")
            
            # Critical Issues Section
            doc.add_heading("Critical Issues", level=1)
            
            # List machines with immediate maintenance needs
            critical_machines = equipment_df[equipment_df['maintenance_urgency'] == 'Immediate']
            
            if len(critical_machines) > 0:
                doc.add_paragraph("Machines Requiring Immediate Attention:", style='Heading 2')
                
                for _, row in critical_machines.iterrows():
                    p = doc.add_paragraph(style='List Bullet')
                    p.add_run(f"{row['machine_id']} ({row['machine_type']}): ").bold = True
                    p.add_run(f"Failure probability {row['failure_probability']} in {row['days_to_failure']} days. ")
                    p.add_run(str(row.get('recommendation', 'No recommendation')))
            else:
                doc.add_paragraph("No machines require immediate attention.").italic = True
            
            # Anomaly Detection Section
            if not anomaly_data.empty:
                doc.add_heading("Anomaly Detection Results", level=1)
                
                severe_anomalies = anomaly_data[anomaly_data['severity'] == 'High']
                if len(severe_anomalies) > 0:
                    doc.add_paragraph("Significant Anomalies Detected:", style='Heading 2')
                    
                    for _, row in severe_anomalies.iterrows():
                        p = doc.add_paragraph(style='List Bullet')
                        p.add_run(f"{row['machine_id']}: ").bold = True
                        p.add_run(f"Anomaly Score: {row['anomaly_score']}, Affected Sensors: {row['affected_sensors']}")
                        if 'detected_at' in row:
                            p.add_run(f", Detected At: {row['detected_at']}")
                else:
                    doc.add_paragraph("No significant anomalies detected.").italic = True
            
            # Equipment Status Section
            doc.add_heading("Equipment Status Summary", level=1)
            table = doc.add_table(rows=1, cols=7)
            table.style = 'Table Grid'
            
            # Add header row
            header_cells = table.rows[0].cells
            header_cells[0].text = "Machine ID"
            header_cells[1].text = "Type"
            header_cells[2].text = "Status"
            header_cells[3].text = "Failure Prob."
            header_cells[4].text = "Days to Failure"
            header_cells[5].text = "Urgency"
            header_cells[6].text = "Recommendation"
            
            # Make the header row bold
            for cell in header_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
            
            # Add data rows
            for _, row in equipment_df.iterrows():
                cells = table.add_row().cells
                cells[0].text = str(row['machine_id'])
                cells[1].text = str(row['machine_type'])
                cells[2].text = str(row['status'])
                cells[3].text = str(row.get('failure_probability', 'N/A'))
                cells[4].text = str(row.get('days_to_failure', 'N/A'))
                cells[5].text = str(row.get('maintenance_urgency', 'Unknown'))
                cells[6].text = str(row.get('recommendation', 'No recommendation'))
            
            # Performance Metrics Section
            if not metrics_data.empty:
                doc.add_page_break()
                doc.add_heading("Performance Metrics", level=1)
                
                metrics_table = doc.add_table(rows=1, cols=7)
                metrics_table.style = 'Table Grid'
                
                # Add header row
                header_cells = metrics_table.rows[0].cells
                header_cells[0].text = "Machine ID"
                header_cells[1].text = "Health"
                header_cells[2].text = "OEE"
                header_cells[3].text = "Availability"
                header_cells[4].text = "Performance"
                header_cells[5].text = "Quality"
                header_cells[6].text = "Power Usage"
                
                # Make the header row bold
                for cell in header_cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
                
                # Add metrics data rows
                for _, row in metrics_data.iterrows():
                    cells = metrics_table.add_row().cells
                    cells[0].text = str(row['machine_id'])
                    cells[1].text = str(row['overall_health'])
                    cells[2].text = str(row['oee'])
                    cells[3].text = str(row['availability'])
                    cells[4].text = str(row['performance'])
                    cells[5].text = str(row['quality'])
                    cells[6].text = str(row['power_usage'])
            
            # Sensor Readings Section
            if not sensor_data.empty:
                doc.add_heading("Latest Sensor Readings", level=1)
                
                sensor_table = doc.add_table(rows=1, cols=5)
                sensor_table.style = 'Table Grid'
                
                # Add header row
                header_cells = sensor_table.rows[0].cells
                header_cells[0].text = "Machine ID"
                header_cells[1].text = "Timestamp"
                header_cells[2].text = "Temperature (°C)"
                header_cells[3].text = "Vibration (mm/s)"
                header_cells[4].text = "Power (%)"
                
                # Make the header row bold
                for cell in header_cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
                
                # Add sensor data rows
                for _, row in sensor_data.iterrows():
                    cells = sensor_table.add_row().cells
                    cells[0].text = str(row['machine_id'])
                    cells[1].text = str(row.get('timestamp', 'Unknown'))
                    cells[2].text = f"{row.get('temperature', 'Unknown'):.1f}"
                    cells[3].text = f"{row.get('vibration', 'Unknown'):.2f}"
                    cells[4].text = f"{row.get('power', 'Unknown'):.1f}"
            
            # Add a conclusion
            doc.add_page_break()
            doc.add_heading("Conclusion and Recommendations", level=1)
            conclusion = doc.add_paragraph()
            conclusion.add_run("Summary of Findings: ").bold = True
            conclusion.add_run(f"Based on the analysis of {len(equipment_df)} machines, ")
            
            if critical_count > 0:
                conclusion.add_run(f"{critical_count} machines require immediate maintenance attention. ")
                conclusion.add_run("These should be addressed as soon as possible to prevent failures and downtime. ")
            else:
                conclusion.add_run("no machines require immediate attention at this time. ")
                
            if warning_count > 0:
                conclusion.add_run(f"Additionally, {warning_count} machines have been flagged with warnings ")
                conclusion.add_run("and should be scheduled for maintenance in the near future. ")
                
            if anomaly_count > 0:
                conclusion.add_run(f"\n\nThe system has detected {anomaly_count} anomalies that may indicate developing issues. ")
                conclusion.add_run("These should be investigated to determine their root cause.")
            
            # Save to a bytes stream
            f = io.BytesIO()
            doc.save(f)
            f.seek(0)
            return f.read()
            
        def generate_xlsx():
            """Generate Excel report"""
            # Get data
            df = get_enhanced_equipment_df()
            
            # Create an in-memory output file
            output = io.BytesIO()
            
            # Create workbook and worksheet
            workbook = xlsxwriter.Workbook(output)
            
            # Create format styles
            title_format = workbook.add_format({
                'bold': True, 
                'font_size': 16, 
                'align': 'center',
                'valign': 'vcenter'
            })
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#0066cc',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            cell_format = workbook.add_format({
                'border': 1
            })
            
            # Equipment summary worksheet
            ws_equipment = workbook.add_worksheet("Equipment Summary")
            
            # Add title
            ws_equipment.merge_range('A1:G1', f"SmartMaintain - {report_type}", title_format)
            ws_equipment.merge_range('A2:G2', f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", workbook.add_format({'align': 'center'}))
            ws_equipment.merge_range('A3:G3', f"Time Period: {time_period}", workbook.add_format({'align': 'center'}))
            
            # Add table headers
            headers = ["Machine ID", "Type", "Status", "Failure Probability", "Days to Failure", "Urgency", "Recommendation"]
            for col, header in enumerate(headers):
                ws_equipment.write(4, col, header, header_format)
                
            # Set column widths
            ws_equipment.set_column('A:A', 12)
            ws_equipment.set_column('B:B', 15)
            ws_equipment.set_column('C:C', 12)
            ws_equipment.set_column('D:D', 18)
            ws_equipment.set_column('E:E', 15)
            ws_equipment.set_column('F:F', 12)
            ws_equipment.set_column('G:G', 50)
            
            # Add data rows
            for row_idx, (_, data_row) in enumerate(df.iterrows()):
                ws_equipment.write(row_idx + 5, 0, str(data_row['machine_id']), cell_format)
                ws_equipment.write(row_idx + 5, 1, str(data_row['machine_type']), cell_format)
                ws_equipment.write(row_idx + 5, 2, str(data_row['status']), cell_format)
                ws_equipment.write(row_idx + 5, 3, str(data_row.get('failure_probability', 'N/A')), cell_format)
                ws_equipment.write(row_idx + 5, 4, str(data_row.get('days_to_failure', 'N/A')), cell_format)
                ws_equipment.write(row_idx + 5, 5, str(data_row.get('maintenance_urgency', 'Unknown')), cell_format)
                ws_equipment.write(row_idx + 5, 6, str(data_row.get('recommendation', 'No recommendation')), cell_format)
            
            # Statistics worksheet
            ws_stats = workbook.add_worksheet("Statistics")
            
            # Add title
            ws_stats.merge_range('A1:C1', "System Statistics", title_format)
            
            critical_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Immediate'])
            warning_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Soon'])
            normal_count = len(df) - critical_count - warning_count
            
            # Add statistics
            stats = [
                ["Total Equipment", len(df)],
                ["Critical Alerts", critical_count],
                ["Warning Alerts", warning_count],
                ["Normal Status", normal_count]
            ]
            
            for row_idx, (label, value) in enumerate(stats):
                ws_stats.write(row_idx + 3, 0, label, workbook.add_format({'bold': True}))
                ws_stats.write(row_idx + 3, 1, value)
            
            # Close workbook
            workbook.close()
            
            # Get output value
            output.seek(0)
            return output.getvalue()
            
        def generate_image():
            """Generate a JPG image report (chart)"""
            # Create a white background image
            width, height = 1000, 800
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not available
            try:
                title_font = ImageFont.truetype("Arial", 30)
                header_font = ImageFont.truetype("Arial", 24)
                normal_font = ImageFont.truetype("Arial", 18)
            except IOError:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()
            
            # Add title
            title = f"SmartMaintain - {report_type}"
            draw.text((width//2 - 200, 30), title, fill="black", font=title_font)
            draw.text((width//2 - 150, 70), f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill="black", font=normal_font)
            draw.text((width//2 - 100, 100), f"Time Period: {time_period}", fill="black", font=normal_font)
            
            # Draw a line below the header
            draw.line([(50, 140), (width-50, 140)], fill="black", width=2)
            
            # Get data for visualization
            df = get_enhanced_equipment_df()
            
            # Count machines by urgency
            urgency_counts = {
                'Immediate': 0,
                'Soon': 0,
                'Planned': 0,
                'Normal': 0
            }
            
            for _, row in df.iterrows():
                urgency = row.get('maintenance_urgency', 'Unknown')
                if urgency in urgency_counts:
                    urgency_counts[urgency] += 1
                    
            # Draw chart title
            draw.text((50, 170), "Maintenance Urgency Distribution", fill="black", font=header_font)
            
            # Draw a simple bar chart
            colors = {
                'Immediate': (255, 0, 0),      # Red
                'Soon': (255, 165, 0),         # Orange
                'Planned': (255, 255, 0),      # Yellow
                'Normal': (0, 128, 0)          # Green
            }
            
            # Calculate the maximum value for scaling
            max_value = max(urgency_counts.values()) if urgency_counts.values() else 1
            
            bar_width = 100
            bar_spacing = 50
            bar_height_scale = 300 / max_value  # Scale bars to fit in 300px height
            bar_start_x = 100
            bar_base_y = 500
            
            # Draw bars
            x = bar_start_x
            for category, count in urgency_counts.items():
                bar_height = count * bar_height_scale
                
                # Draw the bar
                draw.rectangle(
                    [(x, bar_base_y - bar_height), (x + bar_width, bar_base_y)],
                    fill=colors.get(category, (200, 200, 200))
                )
                
                # Add the category label
                draw.text((x + 10, bar_base_y + 10), category, fill="black", font=normal_font)
                
                # Add the value on top of the bar
                draw.text((x + 30, bar_base_y - bar_height - 25), str(count), fill="black", font=normal_font)
                
                x += bar_width + bar_spacing
            
            # Draw a horizontal line at the base of the bars
            draw.line([(50, bar_base_y), (width-50, bar_base_y)], fill="black", width=2)
            
            # Add a legend for the chart
            legend_x = 650
            legend_y = 250
            for i, (category, color) in enumerate(colors.items()):
                # Draw color box
                draw.rectangle(
                    [(legend_x, legend_y + i*30), (legend_x + 20, legend_y + i*30 + 20)],
                    fill=color
                )
                # Draw text
                draw.text((legend_x + 30, legend_y + i*30), category, fill="black", font=normal_font)
            
            # Add some additional statistics
            stats_y = 600
            draw.text((50, stats_y), "System Statistics:", fill="black", font=header_font)
            draw.text((50, stats_y + 40), f"Total Equipment: {len(df)}", fill="black", font=normal_font)
            draw.text((50, stats_y + 70), f"Machines Requiring Attention: {urgency_counts['Immediate'] + urgency_counts['Soon']}", fill="black", font=normal_font)
            draw.text((50, stats_y + 100), f"Healthy Machines: {urgency_counts['Normal']}", fill="black", font=normal_font)
            
            # Convert the image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
        
        # Generate the appropriate file based on selected format
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
        
        # Generate appropriate report data based on format
        report_data = None
        if selected_format in ['csv']:
            report_data = generate_csv()
        elif selected_format in ['pdf']:
            report_data = generate_pdf()
        elif selected_format in ['doc', 'docx', 'rtf']:
            report_data = generate_docx()
        elif selected_format in ['xls', 'xlsx']:
            report_data = generate_xlsx()
        elif selected_format in ['txt']:
            report_data = generate_txt()
        elif selected_format in ['jpg', 'jpeg', 'tiff', 'tif', 'xps']:
            report_data = generate_image()
        else:
            # Default to CSV if format not supported
            report_data = generate_csv()
        
        report_name = report_type.lower().replace(" ", "_")
        
        st.download_button(
            label="📊 Download Report",
            data=report_data,
            file_name=f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.{selected_format}",
            mime=mime_types.get(selected_format, "text/csv"),
            help=f"Download {report_type} in {selected_format.upper()} format"
        )
        
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