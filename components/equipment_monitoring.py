import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_equipment_monitoring(processed_data, equipment_data):
    """
    Display equipment monitoring interface with real-time sensor data
    
    Parameters:
    processed_data (dict): Processed sensor data with statistics
    equipment_data (DataFrame): Equipment metadata
    """
    st.header("Equipment Monitoring")
    
    # Equipment selection
    machine_list = equipment_data['machine_id'].tolist()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_machine = st.selectbox("Select Equipment", machine_list)
        
        # Get machine info
        machine_info = equipment_data[equipment_data['machine_id'] == selected_machine].iloc[0]
        
        # Display machine info
        st.subheader("Equipment Information")
        info_cols = st.columns(2)
        with info_cols[0]:
            st.markdown(f"**Type:** {machine_info['machine_type']}")
            st.markdown(f"**Manufacturer:** {machine_info['manufacturer']}")
            st.markdown(f"**Location:** {machine_info['location']}")
        with info_cols[1]:
            st.markdown(f"**Installation:** {machine_info['installation_year']}")
            st.markdown(f"**Last Maintenance:** {machine_info['last_maintenance']}")
            
        # Health score gauge
        health_score = machine_info['health_score']
        health_color = '#E74C3C' if health_score < 70 else '#F39C12' if health_score < 85 else '#2ECC71'
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Health Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': health_color},
                'steps': [
                    {'range': [0, 70], 'color': 'rgba(231, 76, 60, 0.2)'},
                    {'range': [70, 85], 'color': 'rgba(243, 156, 18, 0.2)'},
                    {'range': [85, 100], 'color': 'rgba(46, 204, 113, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig_gauge.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Status indicator
        status = machine_info['status']
        status_color = '#E74C3C' if status == 'Critical' else '#F39C12' if status == 'Warning' else '#2ECC71'
        
        st.markdown(f"""
            <div style="background-color: {status_color}; padding: 10px; border-radius: 5px; text-align: center; color: white;">
                <h3 style="margin: 0;">{status}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Maintenance info
        days_to_maintenance = machine_info['maintenance_due_days']
        
        st.markdown(f"""
            <div style="margin-top: 20px;">
                <p><strong>Next Maintenance Due:</strong> {days_to_maintenance} days</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Get data for this machine
        machine_data = processed_data['sensor_data'][processed_data['sensor_data']['machine_id'] == selected_machine]
        
        # Current values
        st.subheader("Current Sensor Readings")
        
        # Get stats for this machine
        if selected_machine in processed_data['statistics']:
            stats = processed_data['statistics'][selected_machine]
            
            # Display current values in columns
            val_cols = st.columns(4)
            with val_cols[0]:
                current_temp = stats['temperature']['current']
                avg_temp = stats['temperature']['mean']
                temp_diff = current_temp - avg_temp
                st.metric(
                    label="Temperature (°C)", 
                    value=f"{current_temp:.1f}",
                    delta=f"{temp_diff:.1f}"
                )
                
            with val_cols[1]:
                current_pressure = stats['pressure']['current']
                avg_pressure = stats['pressure']['mean']
                pressure_diff = current_pressure - avg_pressure
                st.metric(
                    label="Pressure (PSI)", 
                    value=f"{current_pressure:.1f}",
                    delta=f"{pressure_diff:.1f}"
                )
                
            with val_cols[2]:
                current_vibration = stats['vibration']['current']
                avg_vibration = stats['vibration']['mean']
                vibration_diff = current_vibration - avg_vibration
                st.metric(
                    label="Vibration (mm/s)", 
                    value=f"{current_vibration:.2f}",
                    delta=f"{vibration_diff:.2f}",
                    delta_color="inverse"  # Lower vibration is better
                )
                
            with val_cols[3]:
                current_power = stats['power']['current']
                avg_power = stats['power']['mean']
                power_diff = current_power - avg_power
                st.metric(
                    label="Power (kW)", 
                    value=f"{current_power:.1f}",
                    delta=f"{power_diff:.1f}"
                )
        
        # Time series charts
        st.subheader("Sensor Trends")
        
        # Time range selection
        time_range = st.radio(
            "Time Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Data"],
            horizontal=True
        )
        
        # Filter data based on selected time range
        end_time = machine_data['timestamp'].max()
        
        if time_range == "Last 24 Hours":
            start_time = end_time - timedelta(hours=24)
        elif time_range == "Last 7 Days":
            start_time = end_time - timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = machine_data['timestamp'].min()
        
        filtered_data = machine_data[machine_data['timestamp'].between(start_time, end_time)]
        
        # Select sensors to display
        selected_sensors = st.multiselect(
            "Select Sensors to Display",
            ["Temperature", "Pressure", "Vibration", "Power"],
            default=["Temperature", "Vibration"]
        )
        
        # Map selection to columns
        sensor_columns = []
        for sensor in selected_sensors:
            if sensor == "Temperature":
                sensor_columns.append("temperature")
            elif sensor == "Pressure":
                sensor_columns.append("pressure")
            elif sensor == "Vibration":
                sensor_columns.append("vibration")
            elif sensor == "Power":
                sensor_columns.append("power")
        
        # Create time series chart
        if filtered_data.empty:
            st.info("No data available for the selected time range")
        else:
            # Melt the data for plotting
            plot_data = filtered_data.melt(
                id_vars=['timestamp'],
                value_vars=sensor_columns,
                var_name='Sensor',
                value_name='Value'
            )
            
            # Rename sensor names for display
            sensor_names = {
                'temperature': 'Temperature (°C)',
                'pressure': 'Pressure (PSI)',
                'vibration': 'Vibration (mm/s)',
                'power': 'Power (kW)'
            }
            plot_data['Sensor'] = plot_data['Sensor'].map(sensor_names)
            
            # Create line chart
            fig = px.line(
                plot_data,
                x='timestamp',
                y='Value',
                color='Sensor',
                line_shape='spline',
                labels={'timestamp': 'Time', 'Value': 'Sensor Reading'}
            )
            
            # Improve chart layout
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Maintenance history and anomalies
        cols = st.columns(2)
        
        with cols[0]:
            st.subheader("Maintenance History")
            
            # In a real application, this would come from a database
            # Here we'll generate some mock maintenance history
            maintenance_history = [
                {"date": machine_info['last_maintenance'], "type": "Scheduled", "description": "Full inspection and lubricant change"},
                {"date": "2022-09-15", "type": "Unscheduled", "description": "Replace worn bearing"},
                {"date": "2022-06-10", "type": "Scheduled", "description": "Routine maintenance and calibration"}
            ]
            
            maintenance_df = pd.DataFrame(maintenance_history)
            st.dataframe(maintenance_df, use_container_width=True)
        
        with cols[1]:
            st.subheader("Recent Anomalies")
            
            # Check if there are any anomalies for this machine
            if selected_machine in processed_data['anomalies'] and processed_data['anomalies'][selected_machine]['recent_anomalies']:
                anomaly_data = processed_data['anomalies'][selected_machine]['recent_anomalies']
                
                anomaly_list = []
                for anomaly in anomaly_data:
                    anomaly_list.append({
                        "Date": anomaly['timestamp'].strftime('%Y-%m-%d %H:%M'),
                        "Sensors": ", ".join(anomaly['unusual_sensors']),
                        "Severity": "High" if len(anomaly['unusual_sensors']) > 1 else "Medium"
                    })
                
                anomaly_df = pd.DataFrame(anomaly_list)
                st.dataframe(anomaly_df, use_container_width=True)
            else:
                st.info("No anomalies detected for this equipment")
