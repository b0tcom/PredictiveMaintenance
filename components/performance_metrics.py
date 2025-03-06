import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_performance_metrics(processed_data, equipment_data):
    """
    Display performance metrics and KPIs for equipment
    
    Parameters:
    processed_data (dict): Processed sensor data with statistics
    equipment_data (DataFrame): Equipment metadata
    """
    st.header("Performance Metrics")
    
    # Get sensor data
    sensor_data = processed_data['sensor_data']
    
    # Calculate overall metrics
    total_machines = len(equipment_data)
    avg_health_score = equipment_data['health_score'].mean()
    
    # Calculate operational metrics
    operational_data = calculate_operational_metrics(sensor_data, equipment_data)
    
    # Display overall metrics
    st.subheader("Overall Equipment Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Average Health Score",
            value=f"{avg_health_score:.1f}%",
            delta=f"{avg_health_score - 80:.1f}%" if avg_health_score != 80 else None
        )
    
    with col2:
        st.metric(
            label="OEE (Overall Equipment Effectiveness)",
            value=f"{operational_data['oee']:.1f}%",
            delta=f"{operational_data['oee'] - 85:.1f}%" if operational_data['oee'] != 85 else None
        )
    
    with col3:
        st.metric(
            label="MTBF (Mean Time Between Failures)",
            value=f"{operational_data['mtbf']:.1f} days"
        )
    
    with col4:
        st.metric(
            label="MTTR (Mean Time To Repair)",
            value=f"{operational_data['mttr']:.1f} hours",
            delta=f"{5 - operational_data['mttr']:.1f} hours",
            delta_color="inverse"  # Lower is better
        )
    
    # Performance by machine type
    st.subheader("Performance by Machine Type")
    
    # Group by machine type
    machine_type_df = equipment_data.groupby('machine_type').agg({
        'health_score': 'mean',
        'machine_id': 'count'
    }).reset_index()
    
    machine_type_df.columns = ['Machine Type', 'Average Health Score', 'Count']
    
    # Create bar chart
    fig = px.bar(
        machine_type_df,
        x='Machine Type',
        y='Average Health Score',
        color='Average Health Score',
        color_continuous_scale=[(0, 'red'), (0.5, 'yellow'), (1, 'green')],
        range_color=[60, 100],
        text='Average Health Score',
        hover_data=['Count']
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(title='Average Health Score (%)')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance trends
    st.subheader("Performance Trends")
    
    # Select time grouping
    time_grouping = st.radio(
        "Time Aggregation",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True
    )
    
    # Calculate trends based on selected grouping
    trend_data = calculate_performance_trends(sensor_data, time_grouping)
    
    # Display trend chart
    st.plotly_chart(create_trend_chart(trend_data, time_grouping), use_container_width=True)
    
    # Machine comparison
    st.subheader("Machine Comparison")
    
    # Select machines to compare
    selected_machines = st.multiselect(
        "Select Machines to Compare",
        equipment_data['machine_id'].tolist(),
        default=equipment_data['machine_id'].tolist()[:5]  # Default to first 5
    )
    
    # Select metric to compare
    comparison_metric = st.selectbox(
        "Select Comparison Metric",
        ["Health Score", "Temperature", "Vibration", "Power Consumption", "Anomaly Rate"]
    )
    
    # Create comparison chart
    if selected_machines:
        st.plotly_chart(
            create_comparison_chart(processed_data, equipment_data, selected_machines, comparison_metric),
            use_container_width=True
        )
    else:
        st.info("Please select at least one machine to compare")
    
    # Maintenance impact analysis
    st.subheader("Maintenance Impact Analysis")
    
    impact_data = analyze_maintenance_impact(sensor_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Average Performance Improvement After Maintenance",
            value=f"{impact_data['avg_improvement']:.1f}%",
            delta=f"+{impact_data['avg_improvement']:.1f}%"
        )
        
        st.metric(
            label="Average Days Before Performance Degradation",
            value=f"{impact_data['avg_days_before_degradation']:.1f} days"
        )
    
    with col2:
        # Create impact visualization
        fig = go.Figure()
        
        # Before and after maintenance series
        fig.add_trace(go.Scatter(
            x=impact_data['days_relative'],
            y=impact_data['avg_performance'],
            mode='lines+markers',
            name='Performance',
            line=dict(color='royalblue', width=3),
            hovertemplate='Day %{x}: %{y:.1f}%<extra></extra>'
        ))
        
        # Add maintenance line
        fig.add_shape(
            type="line",
            x0=0, y0=0,
            x1=0, y1=100,
            line=dict(color="green", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=0,
            y=100,
            text="Maintenance",
            showarrow=False,
            yshift=-30,
            font=dict(size=12, color="green")
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(title="Days (Relative to Maintenance)"),
            yaxis=dict(title="Performance (%)", range=[60, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)

def calculate_operational_metrics(sensor_data, equipment_data):
    """
    Calculate operational metrics including OEE, MTBF, and MTTR
    
    Parameters:
    sensor_data (DataFrame): Sensor data
    equipment_data (DataFrame): Equipment data
    
    Returns:
    dict: Dictionary of operational metrics
    """
    # In a real application, these would be calculated from actual operational data
    # For demo purposes, we'll generate realistic values
    
    # OEE is typically calculated as Availability × Performance × Quality
    # We'll simulate these components
    availability = np.random.uniform(0.85, 0.95)  # 85-95%
    performance = np.random.uniform(0.80, 0.98)  # 80-98%
    quality = np.random.uniform(0.95, 0.995)  # 95-99.5%
    
    oee = availability * performance * quality * 100  # Convert to percentage
    
    # MTBF - Mean Time Between Failures (in days)
    # Higher health scores should correlate with higher MTBF
    avg_health = equipment_data['health_score'].mean()
    mtbf_base = 30  # Base value of 30 days
    mtbf = mtbf_base * (avg_health / 80)  # Adjust based on health score
    
    # MTTR - Mean Time To Repair (in hours)
    # Random value between 2 and 8 hours
    mttr = np.random.uniform(2, 8)
    
    return {
        'oee': oee,
        'mtbf': mtbf,
        'mttr': mttr,
        'availability': availability * 100,
        'performance': performance * 100,
        'quality': quality * 100
    }

def calculate_performance_trends(sensor_data, time_grouping):
    """
    Calculate performance trends over time
    
    Parameters:
    sensor_data (DataFrame): Sensor data
    time_grouping (str): Time aggregation level (Daily, Weekly, Monthly)
    
    Returns:
    DataFrame: Aggregated trend data
    """
    # Make a copy of the data
    data = sensor_data.copy()
    
    # Convert timestamp to datetime if it's not already
    if not pd.api.types.is_datetime64_dtype(data['timestamp']):
        data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Add date columns
    data['date'] = data['timestamp'].dt.date
    data['week'] = data['timestamp'].dt.isocalendar().week
    data['month'] = data['timestamp'].dt.month
    
    # Define grouping column based on selection
    if time_grouping == "Daily":
        group_col = 'date'
    elif time_grouping == "Weekly":
        group_col = 'week'
    else:  # Monthly
        group_col = 'month'
    
    # Group by time and calculate metrics
    grouped = data.groupby(group_col).agg({
        'temperature': ['mean', 'max'],
        'vibration': ['mean', 'max'],
        'power': ['mean', 'sum'],
        'maintenance_performed': 'sum',
        'timestamp': 'min'  # To get the start date for each group
    })
    
    # Flatten the multi-level columns
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
    
    # Reset index
    trend_data = grouped.reset_index()
    
    # Add simulated performance metric
    # Performance decreases with higher temperature and vibration, and spikes after maintenance
    trend_data['performance'] = 85 - (trend_data['temperature_mean'] - 60) * 0.5 - trend_data['vibration_mean'] * 10
    
    # Performance boost after maintenance
    trend_data.loc[trend_data['maintenance_performed_sum'] > 0, 'performance'] += 5
    
    # Add some random variation
    trend_data['performance'] += np.random.normal(0, 2, size=len(trend_data))
    
    # Cap between 60 and 100
    trend_data['performance'] = trend_data['performance'].clip(60, 100)
    
    # Sort by timestamp
    trend_data = trend_data.sort_values('timestamp_min')
    
    return trend_data

def create_trend_chart(trend_data, time_grouping):
    """
    Create a chart showing performance trends over time
    
    Parameters:
    trend_data (DataFrame): Trend data
    time_grouping (str): Time aggregation level
    
    Returns:
    Figure: Plotly figure
    """
    # Create figure
    fig = go.Figure()
    
    # Add performance line
    fig.add_trace(go.Scatter(
        x=trend_data['timestamp_min'],
        y=trend_data['performance'],
        mode='lines+markers',
        name='Performance',
        line=dict(color='blue', width=3),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Performance: %{y:.1f}%<extra></extra>'
    ))
    
    # Add maintenance markers
    maintenance_points = trend_data[trend_data['maintenance_performed_sum'] > 0]
    
    if not maintenance_points.empty:
        fig.add_trace(go.Scatter(
            x=maintenance_points['timestamp_min'],
            y=maintenance_points['performance'],
            mode='markers',
            name='Maintenance Performed',
            marker=dict(
                color='green',
                size=12,
                symbol='star'
            ),
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Maintenance performed<br>Performance: %{y:.1f}%<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title=f"{time_grouping} Date"),
        yaxis=dict(title="Performance (%)", range=[60, 100]),
        hovermode="closest"
    )
    
    return fig

def create_comparison_chart(processed_data, equipment_data, selected_machines, metric):
    """
    Create a chart comparing machines on a selected metric
    
    Parameters:
    processed_data (dict): Processed data
    equipment_data (DataFrame): Equipment data
    selected_machines (list): List of machine IDs to compare
    metric (str): Metric to compare
    
    Returns:
    Figure: Plotly figure
    """
    # Filter equipment data
    filtered_equipment = equipment_data[equipment_data['machine_id'].isin(selected_machines)]
    
    # Prepare data based on selected metric
    if metric == "Health Score":
        # Use health score from equipment data
        comparison_data = filtered_equipment[['machine_id', 'health_score', 'machine_type']]
        comparison_data.columns = ['Machine ID', 'Value', 'Machine Type']
        title = "Health Score Comparison (%)"
        y_range = [0, 100]
    
    elif metric == "Temperature":
        # Use average temperature from statistics
        comparison_data = []
        for machine_id in selected_machines:
            if machine_id in processed_data['statistics']:
                machine_type = filtered_equipment[filtered_equipment['machine_id'] == machine_id]['machine_type'].iloc[0]
                avg_temp = processed_data['statistics'][machine_id]['temperature']['mean']
                comparison_data.append({
                    'Machine ID': machine_id,
                    'Value': avg_temp,
                    'Machine Type': machine_type
                })
        
        comparison_data = pd.DataFrame(comparison_data)
        title = "Average Temperature (°C)"
        y_range = None
    
    elif metric == "Vibration":
        # Use average vibration from statistics
        comparison_data = []
        for machine_id in selected_machines:
            if machine_id in processed_data['statistics']:
                machine_type = filtered_equipment[filtered_equipment['machine_id'] == machine_id]['machine_type'].iloc[0]
                avg_vibration = processed_data['statistics'][machine_id]['vibration']['mean']
                comparison_data.append({
                    'Machine ID': machine_id,
                    'Value': avg_vibration,
                    'Machine Type': machine_type
                })
        
        comparison_data = pd.DataFrame(comparison_data)
        title = "Average Vibration (mm/s)"
        y_range = None
    
    elif metric == "Power Consumption":
        # Use average power from statistics
        comparison_data = []
        for machine_id in selected_machines:
            if machine_id in processed_data['statistics']:
                machine_type = filtered_equipment[filtered_equipment['machine_id'] == machine_id]['machine_type'].iloc[0]
                avg_power = processed_data['statistics'][machine_id]['power']['mean']
                comparison_data.append({
                    'Machine ID': machine_id,
                    'Value': avg_power,
                    'Machine Type': machine_type
                })
        
        comparison_data = pd.DataFrame(comparison_data)
        title = "Average Power Consumption (kW)"
        y_range = None
    
    elif metric == "Anomaly Rate":
        # Use anomaly percentage from anomalies
        comparison_data = []
        for machine_id in selected_machines:
            if machine_id in processed_data['anomalies']:
                machine_type = filtered_equipment[filtered_equipment['machine_id'] == machine_id]['machine_type'].iloc[0]
                anomaly_pct = processed_data['anomalies'][machine_id]['anomaly_percentage']
                comparison_data.append({
                    'Machine ID': machine_id,
                    'Value': anomaly_pct,
                    'Machine Type': machine_type
                })
        
        comparison_data = pd.DataFrame(comparison_data)
        title = "Anomaly Rate (%)"
        y_range = [0, 15]  # Cap at 15% for better visualization
    
    # Create the chart
    if comparison_data.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title="No data available for the selected metric",
            height=400
        )
        return fig
    
    # Sort by value
    comparison_data = comparison_data.sort_values('Value', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        comparison_data,
        x='Machine ID',
        y='Value',
        color='Machine Type',
        labels={'Value': metric},
        text='Value',
        height=400
    )
    
    # Format text based on metric
    if metric == "Health Score" or metric == "Anomaly Rate":
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    # Update layout
    fig.update_layout(
        title=title,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_tickangle=-45,
        yaxis_range=y_range
    )
    
    return fig

def analyze_maintenance_impact(sensor_data):
    """
    Analyze the impact of maintenance on equipment performance
    
    Parameters:
    sensor_data (DataFrame): Sensor data with maintenance events
    
    Returns:
    dict: Analysis results
    """
    # In a real application, this would analyze actual maintenance events
    # For demo purposes, we'll simulate impact data
    
    # Days relative to maintenance (-30 to +30)
    days_relative = list(range(-30, 31))
    
    # Simulate average performance curve
    # Performance decreases before maintenance and improves afterwards
    base_performance = 85
    pre_maintenance_slope = -0.5  # Performance loss per day before maintenance
    post_maintenance_slope = 0.1  # Performance loss per day after maintenance
    
    # Calculate performance values
    avg_performance = []
    for day in days_relative:
        if day < 0:
            # Before maintenance: gradually decreasing
            perf = base_performance + day * pre_maintenance_slope
        else:
            # After maintenance: immediate improvement, then slow decrease
            immediate_improvement = 10  # Performance boost right after maintenance
            perf = base_performance + immediate_improvement - day * post_maintenance_slope
        
        # Add some noise
        perf += np.random.normal(0, 1)
        
        # Cap between 60 and 100
        perf = max(60, min(100, perf))
        avg_performance.append(perf)
    
    # Calculate metrics
    before_maintenance = avg_performance[29]  # Day before maintenance
    after_maintenance = avg_performance[31]  # Day after maintenance
    avg_improvement = after_maintenance - before_maintenance
    
    # Estimate days before significant degradation
    # Find the day when performance drops below 90% of the post-maintenance level
    threshold = after_maintenance * 0.9
    days_before_degradation = 30  # Default
    for i, perf in enumerate(avg_performance[31:]):
        if perf < threshold:
            days_before_degradation = i
            break
    
    return {
        'days_relative': days_relative,
        'avg_performance': avg_performance,
        'avg_improvement': avg_improvement,
        'avg_days_before_degradation': days_before_degradation
    }
