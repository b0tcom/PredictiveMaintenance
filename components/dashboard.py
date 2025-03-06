import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_dashboard(processed_data, equipment_data):
    """
    Display the main dashboard overview with key metrics and visualizations
    
    Parameters:
    processed_data (dict): Processed sensor data and predictions
    equipment_data (DataFrame): Equipment metadata
    """
    st.header("Dashboard Overview")
    
    # Get key metrics
    total_machines = len(equipment_data)
    critical_machines = sum(equipment_data['status'] == 'Critical')
    warning_machines = sum(equipment_data['status'] == 'Warning')
    healthy_machines = sum(equipment_data['status'] == 'Healthy')
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Equipment", value=total_machines)
    with col2:
        st.metric(label="Healthy", value=healthy_machines, delta=f"{healthy_machines/total_machines:.0%}")
    with col3:
        st.metric(label="Warning", value=warning_machines, delta=f"{warning_machines/total_machines:.0%}", delta_color="off")
    with col4:
        st.metric(label="Critical", value=critical_machines, delta=f"{critical_machines/total_machines:.0%}", delta_color="inverse")
    
    # Equipment status overview
    st.subheader("Equipment Status Overview")
    
    # Status distribution
    fig_status = px.pie(
        equipment_data, 
        names='status', 
        color='status',
        color_discrete_map={'Healthy': '#2ECC71', 'Warning': '#F39C12', 'Critical': '#E74C3C'},
        hole=0.4
    )
    fig_status.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    # Health score by machine
    fig_health = px.bar(
        equipment_data.sort_values('health_score'), 
        x='machine_id', 
        y='health_score',
        color='status',
        color_discrete_map={'Healthy': '#2ECC71', 'Warning': '#F39C12', 'Critical': '#E74C3C'},
        labels={'machine_id': 'Machine ID', 'health_score': 'Health Score (%)'},
        text='health_score'
    )
    fig_health.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        xaxis_tickangle=-45
    )
    
    # Display charts side by side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_status, use_container_width=True)
    with col2:
        st.plotly_chart(fig_health, use_container_width=True)
    
    # Recent anomalies section
    st.subheader("Recent Anomalies")
    
    # Count machines with anomalies
    machines_with_anomalies = 0
    recent_anomaly_list = []
    
    for machine_id, anomaly_data in processed_data['anomalies'].items():
        if anomaly_data['has_recent_anomaly']:
            machines_with_anomalies += 1
            for anomaly in anomaly_data['recent_anomalies'][:3]:  # Take top 3 most recent
                recent_anomaly_list.append({
                    'machine_id': machine_id,
                    'timestamp': anomaly['timestamp'],
                    'unusual_sensors': ', '.join(anomaly['unusual_sensors']),
                    'machine_type': equipment_data[equipment_data['machine_id'] == machine_id]['machine_type'].iloc[0]
                })
    
    if machines_with_anomalies > 0:
        # Create anomaly DataFrame and display
        anomaly_df = pd.DataFrame(recent_anomaly_list).sort_values('timestamp', ascending=False)
        anomaly_df['timestamp'] = anomaly_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.write(f"Found anomalies in {machines_with_anomalies} machines")
        st.dataframe(anomaly_df, use_container_width=True)
    else:
        st.info("No recent anomalies detected")
    
    # Predicted failures section
    st.subheader("Predicted Failures")
    
    # Show predictions with high probability
    high_risk_predictions = []
    
    for machine_id, prediction in processed_data['predictions'].items():
        if prediction['failure_probability'] > 0.4:  # Show only high and medium risk
            machine_type = equipment_data[equipment_data['machine_id'] == machine_id]['machine_type'].iloc[0]
            high_risk_predictions.append({
                'machine_id': machine_id,
                'machine_type': machine_type,
                'failure_probability': prediction['failure_probability'] * 100,  # Convert to percentage
                'days_to_failure': prediction['days_to_failure'],
                'estimated_downtime': prediction['estimated_downtime_hours'],
                'estimated_cost': f"${prediction['estimated_cost']:,.2f}"
            })
    
    if high_risk_predictions:
        predictions_df = pd.DataFrame(high_risk_predictions).sort_values('failure_probability', ascending=False)
        predictions_df['failure_probability'] = predictions_df['failure_probability'].round(1).astype(str) + '%'
        
        st.dataframe(predictions_df, use_container_width=True)
        
        # Map view of equipment
        st.subheader("Equipment Location Map")
        
        # Create a simple map layout of the factory zones
        generate_factory_map(equipment_data, processed_data)
    else:
        st.info("No high-risk failures predicted at this time")

def generate_factory_map(equipment_data, processed_data):
    """
    Generate a visual map of the factory with equipment status
    
    Parameters:
    equipment_data (DataFrame): Equipment metadata
    processed_data (dict): Processed data with predictions
    """
    # Prepare data for the map
    zones = equipment_data['location'].unique()
    
    # Create a grid layout
    rows = 2
    cols = 3
    
    # Create figure
    fig = go.Figure()
    
    # Assign positions to each zone
    zone_positions = {
        'Zone-A': (0, 0),
        'Zone-B': (1, 0),
        'Zone-C': (2, 0),
        'Zone-D': (0, 1),
        'Zone-E': (1, 1),
        'Zone-F': (2, 1)
    }
    
    # Add rectangles for each zone
    for zone, (col, row) in zone_positions.items():
        x0 = col * 0.33
        x1 = (col + 1) * 0.33
        y0 = row * 0.5
        y1 = (row + 1) * 0.5
        
        fig.add_shape(
            type="rect",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(color="Gray", width=2),
            fillcolor="LightGray",
            opacity=0.3
        )
        
        # Add zone label
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=(y0 + y1) / 2 + 0.15,
            text=zone,
            showarrow=False,
            font=dict(size=14, color="black")
        )
        
        # Get equipment in this zone
        zone_equipment = equipment_data[equipment_data['location'] == zone]
        
        # Display each piece of equipment as a marker
        for i, (_, machine) in enumerate(zone_equipment.iterrows()):
            # Position within zone
            pos_x = x0 + 0.08 + (i % 3) * 0.08
            pos_y = y0 + 0.08 + (i // 3) * 0.15
            
            # Determine color based on status
            if machine['status'] == 'Critical':
                color = '#E74C3C'  # Red
            elif machine['status'] == 'Warning':
                color = '#F39C12'  # Orange
            else:
                color = '#2ECC71'  # Green
            
            # Determine size based on health score
            size = 20 - (machine['health_score'] / 10)
            
            # Add marker
            fig.add_trace(
                go.Scatter(
                    x=[pos_x],
                    y=[pos_y],
                    mode='markers+text',
                    marker=dict(
                        size=size,
                        color=color,
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    text=[machine['machine_id'].replace('Machine-', '')],
                    textposition="middle center",
                    textfont=dict(
                        family="Arial",
                        size=10,
                        color="white"
                    ),
                    hoverinfo='text',
                    hovertext=f"{machine['machine_id']}<br>Type: {machine['machine_type']}<br>Status: {machine['status']}<br>Health: {machine['health_score']}%",
                    name=machine['machine_id']
                )
            )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.05]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.05])
    )
    
    st.plotly_chart(fig, use_container_width=True)
