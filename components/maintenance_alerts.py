import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_maintenance_alerts(processed_data, equipment_data):
    """
    Display maintenance alerts and recommendations
    
    Parameters:
    processed_data (dict): Processed sensor data with predictions
    equipment_data (DataFrame): Equipment metadata
    """
    st.header("Maintenance Alerts")
    
    # Create dataframe with all equipment and their maintenance status
    maintenance_data = []
    
    for _, machine in equipment_data.iterrows():
        machine_id = machine['machine_id']
        
        # Get prediction data if available
        if machine_id in processed_data['predictions']:
            prediction = processed_data['predictions'][machine_id]
            recommendation = processed_data['recommendations'][machine_id]
            
            # Determine status for sorting
            if recommendation['urgency'] == 'Immediate':
                sort_value = 0
            elif recommendation['urgency'] == 'Soon':
                sort_value = 1
            elif recommendation['urgency'] == 'Planned':
                sort_value = 2
            else:
                sort_value = 3
                
            maintenance_data.append({
                'machine_id': machine_id,
                'machine_type': machine['machine_type'],
                'location': machine['location'],
                'health_score': machine['health_score'],
                'days_to_failure': prediction['days_to_failure'],
                'failure_probability': prediction['failure_probability'] * 100,  # Convert to percentage
                'maintenance_due_days': machine['maintenance_due_days'],
                'last_maintenance': machine['last_maintenance'],
                'urgency': recommendation['urgency'],
                'sort_value': sort_value,
                'recommendation': recommendation['message'],
                'actions': recommendation['actions'],
                'downtime': recommendation['estimated_downtime_hours'],
                'cost': recommendation['estimated_cost']
            })
        else:
            # No prediction data available
            maintenance_data.append({
                'machine_id': machine_id,
                'machine_type': machine['machine_type'],
                'location': machine['location'],
                'health_score': machine['health_score'],
                'days_to_failure': None,
                'failure_probability': None,
                'maintenance_due_days': machine['maintenance_due_days'],
                'last_maintenance': machine['last_maintenance'],
                'urgency': 'Unknown',
                'sort_value': 4,
                'recommendation': 'Insufficient data for recommendation',
                'actions': None,
                'downtime': None,
                'cost': None
            })
    
    # Convert to dataframe and sort by urgency
    maintenance_df = pd.DataFrame(maintenance_data).sort_values('sort_value')
    
    # Display maintenance summary
    st.subheader("Maintenance Summary")
    
    # Count by urgency
    immediate_count = sum(maintenance_df['urgency'] == 'Immediate')
    soon_count = sum(maintenance_df['urgency'] == 'Soon')
    planned_count = sum(maintenance_df['urgency'] == 'Planned')
    
    cols = st.columns(4)
    with cols[0]:
        st.metric(label="Immediate Action", value=immediate_count, delta=f"{immediate_count} machines")
    with cols[1]:
        st.metric(label="Scheduled Soon", value=soon_count, delta=f"{soon_count} machines")
    with cols[2]:
        st.metric(label="Planned", value=planned_count, delta=f"{planned_count} machines")
    with cols[3]:
        st.metric(label="Total Scheduled", value=immediate_count + soon_count + planned_count)
    
    # Display maintenance timeline
    st.subheader("Maintenance Timeline")
    
    # Create timeline data
    timeline_data = []
    current_date = datetime.now().date()
    
    for _, row in maintenance_df.iterrows():
        if row['days_to_failure'] is not None:
            maintenance_date = current_date + timedelta(days=row['days_to_failure'])
            
            timeline_data.append({
                'machine_id': row['machine_id'],
                'date': maintenance_date,
                'urgency': row['urgency'],
                'days_away': row['days_to_failure']
            })
    
    # Sort by date
    timeline_df = pd.DataFrame(timeline_data).sort_values('date')
    
    # Calculate date range for x-axis
    if not timeline_df.empty:
        min_date = current_date
        max_date = max(timeline_df['date']) + timedelta(days=7)
        
        # Create figure
        fig = go.Figure()
        
        # Add current date line
        fig.add_shape(
            type="line",
            x0=current_date,
            y0=0,
            x1=current_date,
            y1=len(timeline_df) + 0.5,
            line=dict(color="black", width=2, dash="dash"),
        )
        
        # Add text for current date
        fig.add_annotation(
            x=current_date,
            y=0,
            text="Today",
            showarrow=False,
            yshift=-20,
            font=dict(size=12, color="black")
        )
        
        # Add one trace per urgency category for better legend
        for urgency, color in [
            ('Immediate', '#E74C3C'),
            ('Soon', '#F39C12'),
            ('Planned', '#2ECC71')
        ]:
            mask = timeline_df['urgency'] == urgency
            fig.add_trace(go.Scatter(
                x=timeline_df[mask]['date'],
                y=timeline_df[mask].index,
                mode='markers',
                marker=dict(
                    size=15,
                    color=color,
                    symbol='square'
                ),
                name=urgency,
                text=timeline_df[mask]['machine_id'],
                hovertemplate='%{text}<br>Date: %{x}<br>Urgency: ' + urgency
            ))
        
        # Update layout
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=40),
            xaxis=dict(
                title="Date",
                range=[min_date, max_date],
                tickformat='%Y-%m-%d'
            ),
            yaxis=dict(
                title="",
                showticklabels=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            ),
            hovermode="closest"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No maintenance events scheduled")
    
    # Display maintenance alerts table
    st.subheader("Maintenance Alerts")
    
    # Filter columns for display
    display_df = maintenance_df[['machine_id', 'machine_type', 'location', 'urgency', 
                                 'days_to_failure', 'failure_probability', 'maintenance_due_days']]
    
    # Format values
    display_df['failure_probability'] = display_df['failure_probability'].apply(
        lambda x: f"{x:.1f}%" if pd.notnull(x) else "Unknown"
    )
    
    # Rename columns
    display_df.columns = ['Machine ID', 'Type', 'Location', 'Urgency', 
                          'Days to Failure', 'Failure Probability', 'Days Until Due']
    
    # Display with formatting
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Detailed recommendations
    st.subheader("Maintenance Recommendations")
    
    # Let user select a machine to view detailed recommendation
    machine_options = maintenance_df[maintenance_df['urgency'] != 'Unknown']['machine_id'].tolist()
    
    if machine_options:
        selected_machine = st.selectbox("Select Machine for Detailed Recommendation", machine_options)
        
        # Get data for selected machine
        machine_data = maintenance_df[maintenance_df['machine_id'] == selected_machine].iloc[0]
        
        # Display recommendation details
        st.markdown(f"### Recommendation for {selected_machine}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**{machine_data['recommendation']}**")
            
            st.markdown("**Recommended Actions:**")
            for action in machine_data['actions']:
                st.markdown(f"- {action}")
        
        with col2:
            # Display metrics
            st.metric("Health Score", f"{machine_data['health_score']:.1f}%")
            
            if machine_data['failure_probability'] is not None:
                st.metric("Failure Probability", f"{machine_data['failure_probability']:.1f}%")
            
            if machine_data['downtime'] is not None:
                st.metric("Est. Downtime", f"{machine_data['downtime']:.1f} hours")
            
            if machine_data['cost'] is not None:
                st.metric("Est. Cost", f"${machine_data['cost']:,.2f}")
    else:
        st.info("No maintenance recommendations available")
