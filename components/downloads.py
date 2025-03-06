import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
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
            
        def generate_csv():
            """Generate CSV file from equipment data"""
            return get_enhanced_equipment_df().to_csv(index=False)
            
        def generate_txt():
            """Generate text report"""
            df = get_enhanced_equipment_df()
            
            # Create a text report
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report = [
                f"SmartMaintain - {report_type}",
                f"Generated: {current_time}",
                f"Time Period: {time_period}",
                "\n=== Equipment Status Summary ===\n"
            ]
            
            # Add equipment summary
            for _, row in df.iterrows():
                report.append(f"Machine: {row['machine_id']} ({row['machine_type']})")
                report.append(f"  Status: {row['status']}")
                report.append(f"  Failure Probability: {row['failure_probability']}")
                report.append(f"  Days to Failure: {row['days_to_failure']}")
                report.append(f"  Maintenance Urgency: {row.get('maintenance_urgency', 'Unknown')}")
                report.append(f"  Recommendation: {row.get('recommendation', 'No recommendation')}")
                report.append("")
                
            # Add statistics
            report.append("\n=== System Statistics ===\n")
            critical_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Immediate'])
            warning_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Soon'])
            
            report.append(f"Total Equipment: {len(df)}")
            report.append(f"Critical Alerts: {critical_count}")
            report.append(f"Warning Alerts: {warning_count}")
            
            # Join and return
            return "\n".join(report)
            
        def generate_pdf():
            """Generate PDF report"""
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
            
            # Equipment data
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Equipment Status Summary", 0, 1)
            pdf.ln(2)
            
            # Create table header
            pdf.set_font("Arial", "B", 10)
            pdf.cell(30, 10, "Machine ID", 1, 0, "C")
            pdf.cell(30, 10, "Type", 1, 0, "C")
            pdf.cell(25, 10, "Status", 1, 0, "C")
            pdf.cell(30, 10, "Failure Prob.", 1, 0, "C")
            pdf.cell(30, 10, "Days to Failure", 1, 0, "C")
            pdf.cell(30, 10, "Urgency", 1, 1, "C")
            
            # Add data rows
            pdf.set_font("Arial", "", 9)
            df = get_enhanced_equipment_df()
            
            for _, row in df.iterrows():
                pdf.cell(30, 10, str(row['machine_id']), 1, 0)
                pdf.cell(30, 10, str(row['machine_type']), 1, 0)
                pdf.cell(25, 10, str(row['status']), 1, 0)
                pdf.cell(30, 10, str(row.get('failure_probability', 'N/A')), 1, 0)
                pdf.cell(30, 10, str(row.get('days_to_failure', 'N/A')), 1, 0)
                urgency = str(row.get('maintenance_urgency', 'Unknown'))
                pdf.cell(30, 10, urgency, 1, 1)
            
            # Add statistics
            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "System Statistics", 0, 1)
            
            critical_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Immediate'])
            warning_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Soon'])
            
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, f"Total Equipment: {len(df)}", 0, 1)
            pdf.cell(0, 8, f"Critical Alerts: {critical_count}", 0, 1)
            pdf.cell(0, 8, f"Warning Alerts: {warning_count}", 0, 1)
            
            # Return PDF as bytes
            return pdf.output(dest='S').encode('latin1')
            
        def generate_docx():
            """Generate DOCX report"""
            # Create document
            doc = Document()
            
            # Add title
            doc.add_heading(f"SmartMaintain - {report_type}", 0)
            doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph(f"Time Period: {time_period}")
            
            # Add equipment table
            doc.add_heading("Equipment Status Summary", level=1)
            table = doc.add_table(rows=1, cols=6)
            table.style = 'Table Grid'
            
            # Add header row
            header_cells = table.rows[0].cells
            header_cells[0].text = "Machine ID"
            header_cells[1].text = "Type"
            header_cells[2].text = "Status"
            header_cells[3].text = "Failure Prob."
            header_cells[4].text = "Days to Failure"
            header_cells[5].text = "Urgency"
            
            # Add data rows
            df = get_enhanced_equipment_df()
            for _, row in df.iterrows():
                cells = table.add_row().cells
                cells[0].text = str(row['machine_id'])
                cells[1].text = str(row['machine_type'])
                cells[2].text = str(row['status'])
                cells[3].text = str(row.get('failure_probability', 'N/A'))
                cells[4].text = str(row.get('days_to_failure', 'N/A'))
                cells[5].text = str(row.get('maintenance_urgency', 'Unknown'))
            
            # Add recommendations section
            doc.add_heading("Maintenance Recommendations", level=1)
            for _, row in df.iterrows():
                if 'recommendation' in row and row['recommendation']:
                    p = doc.add_paragraph()
                    p.add_run(f"{row['machine_id']}: ").bold = True
                    p.add_run(str(row.get('recommendation', 'No recommendation')))
            
            # Add statistics
            doc.add_heading("System Statistics", level=1)
            
            critical_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Immediate'])
            warning_count = len([r for _, r in df.iterrows() if 'maintenance_urgency' in r and r['maintenance_urgency'] == 'Soon'])
            
            doc.add_paragraph(f"Total Equipment: {len(df)}")
            doc.add_paragraph(f"Critical Alerts: {critical_count}")
            doc.add_paragraph(f"Warning Alerts: {warning_count}")
            
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