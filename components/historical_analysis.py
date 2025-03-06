import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def show_historical_analysis(processed_data):
    """
    Display historical data analysis and insights
    
    Parameters:
    processed_data (dict): Processed sensor data with statistics
    """
    st.header("Historical Analysis")
    
    # Get sensor data
    sensor_data = processed_data['sensor_data']
    
    # Data selection filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Machine selection
        machine_options = sorted(sensor_data['machine_id'].unique().tolist())
        selected_machine = st.selectbox("Select Equipment", machine_options)
    
    with col2:
        # Date range selection
        min_date = sensor_data['timestamp'].min().date()
        max_date = sensor_data['timestamp'].max().date()
        
        date_range = st.date_input(
            "Select Date Range",
            [max_date - timedelta(days=30), max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = date_range[0]
            end_date = date_range[0]
    
    with col3:
        # Data aggregation selection
        aggregation = st.selectbox(
            "Data Aggregation",
            ["Raw Data", "Hourly Average", "Daily Average", "Weekly Average"]
        )
    
    # Filter data based on selection
    filtered_data = filter_and_aggregate_data(sensor_data, selected_machine, start_date, end_date, aggregation)
    
    if filtered_data.empty:
        st.warning("No data available for the selected filters")
        return
    
    # Overview of selected data
    st.subheader("Data Overview")
    
    # Display basic stats
    data_points = len(filtered_data)
    date_range_days = (end_date - start_date).days + 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Data Points", data_points)
    with col2:
        st.metric("Date Range", f"{date_range_days} days")
    with col3:
        maintenance_count = filtered_data['maintenance_performed'].sum()
        st.metric("Maintenance Events", int(maintenance_count))
    
    # Show data sample
    with st.expander("View Data Sample"):
        display_cols = ['timestamp', 'temperature', 'pressure', 'vibration', 'power', 'maintenance_performed']
        st.dataframe(filtered_data[display_cols].head(10), use_container_width=True)
    
    # Time series analysis
    st.subheader("Time Series Analysis")
    
    # Select sensors to analyze
    selected_sensors = st.multiselect(
        "Select Sensors to Analyze",
        ["Temperature", "Pressure", "Vibration", "Power"],
        default=["Temperature", "Vibration"]
    )
    
    # Create time series charts
    if selected_sensors:
        st.plotly_chart(create_time_series_chart(filtered_data, selected_sensors), use_container_width=True)
    
    # Statistical analysis
    st.subheader("Statistical Analysis")
    
    # Create statistics
    show_statistical_analysis(filtered_data)
    
    # Correlation analysis
    st.subheader("Correlation Analysis")
    
    # Create correlation matrix
    show_correlation_analysis(filtered_data)
    
    # Advanced analytics
    st.subheader("Advanced Analytics")
    
    # PCA analysis of sensor data
    show_pca_analysis(filtered_data)
    
    # Maintenance impact analysis
    st.subheader("Maintenance Impact Analysis")
    
    # Analyze before and after maintenance
    show_maintenance_impact(filtered_data)

def filter_and_aggregate_data(data, machine_id, start_date, end_date, aggregation):
    """
    Filter and aggregate sensor data based on user selection
    
    Parameters:
    data (DataFrame): Raw sensor data
    machine_id (str): Machine ID to filter
    start_date (date): Start date
    end_date (date): End date
    aggregation (str): Aggregation level
    
    Returns:
    DataFrame: Filtered and aggregated data
    """
    # Filter by machine ID
    filtered = data[data['machine_id'] == machine_id].copy()
    
    # Convert timestamp to datetime if needed
    if not pd.api.types.is_datetime64_dtype(filtered['timestamp']):
        filtered['timestamp'] = pd.to_datetime(filtered['timestamp'])
    
    # Filter by date range
    start_datetime = pd.Timestamp(start_date)
    end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    
    filtered = filtered[(filtered['timestamp'] >= start_datetime) & 
                        (filtered['timestamp'] <= end_datetime)]
    
    # Apply aggregation if requested
    if aggregation != "Raw Data":
        # Add time components for grouping
        filtered['hour'] = filtered['timestamp'].dt.floor('H')
        filtered['day'] = filtered['timestamp'].dt.floor('D')
        filtered['week'] = filtered['timestamp'].dt.floor('W')
        
        # Select group column based on aggregation level
        if aggregation == "Hourly Average":
            group_col = 'hour'
        elif aggregation == "Daily Average":
            group_col = 'day'
        else:  # Weekly Average
            group_col = 'week'
        
        # Group and aggregate
        agg_funcs = {
            'temperature': 'mean',
            'pressure': 'mean',
            'vibration': 'mean',
            'power': 'mean',
            'maintenance_performed': 'sum'
        }
        
        filtered = filtered.groupby(group_col).agg(agg_funcs).reset_index()
        filtered.rename(columns={group_col: 'timestamp'}, inplace=True)
    
    return filtered

def create_time_series_chart(data, selected_sensors):
    """
    Create time series chart for selected sensors
    
    Parameters:
    data (DataFrame): Filtered sensor data
    selected_sensors (list): List of selected sensors
    
    Returns:
    Figure: Plotly figure
    """
    # Map sensor names to columns
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
    
    # Melt the data for plotting
    plot_data = data.melt(
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
    
    # Mark maintenance events
    maintenance_events = data[data['maintenance_performed'] > 0]
    
    if not maintenance_events.empty:
        for _, event in maintenance_events.iterrows():
            fig.add_vline(
                x=event['timestamp'],
                line_dash="dash", 
                line_color="green",
                annotation_text="Maintenance",
                annotation_position="top right"
            )
    
    # Add rolling averages
    for sensor in sensor_columns:
        # Calculate 24-point rolling average (may represent hours or days depending on aggregation)
        if len(data) > 24:
            rolling_avg = data[sensor].rolling(24, center=True).mean()
            
            fig.add_trace(go.Scatter(
                x=data['timestamp'],
                y=rolling_avg,
                mode='lines',
                line=dict(width=3, dash='dot'),
                name=f"{sensor_names[sensor]} (Trend)",
                hoverinfo='skip'
            ))
    
    # Improve chart layout
    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    
    return fig

def show_statistical_analysis(data):
    """
    Display statistical analysis of sensor data
    
    Parameters:
    data (DataFrame): Filtered sensor data
    """
    # Get statistical summary
    stats = data[['temperature', 'pressure', 'vibration', 'power']].describe().T
    
    # Add variance and range
    stats['variance'] = data[['temperature', 'pressure', 'vibration', 'power']].var()
    stats['range'] = stats['max'] - stats['min']
    
    # Format the stats
    formatted_stats = stats.round(2)
    
    # Rename the index
    formatted_stats.index = ['Temperature (°C)', 'Pressure (PSI)', 'Vibration (mm/s)', 'Power (kW)']
    
    # Display stats
    st.dataframe(formatted_stats, use_container_width=True)
    
    # Create distribution plots
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature distribution
        fig_temp = px.histogram(
            data, 
            x='temperature',
            nbins=20,
            labels={'temperature': 'Temperature (°C)'},
            title='Temperature Distribution'
        )
        
        fig_temp.add_vline(
            x=data['temperature'].mean(),
            line_dash="dash", 
            line_color="red",
            annotation_text="Mean",
            annotation_position="top right"
        )
        
        fig_temp.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Vibration distribution
        fig_vib = px.histogram(
            data, 
            x='vibration',
            nbins=20,
            labels={'vibration': 'Vibration (mm/s)'},
            title='Vibration Distribution'
        )
        
        fig_vib.add_vline(
            x=data['vibration'].mean(),
            line_dash="dash", 
            line_color="red",
            annotation_text="Mean",
            annotation_position="top right"
        )
        
        fig_vib.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig_vib, use_container_width=True)

def show_correlation_analysis(data):
    """
    Display correlation analysis of sensor data
    
    Parameters:
    data (DataFrame): Filtered sensor data
    """
    # Calculate correlation matrix
    corr_matrix = data[['temperature', 'pressure', 'vibration', 'power']].corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        labels=dict(color="Correlation")
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Correlation Insights")
        
        # Find strongest correlations
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                corr_pairs.append((col1, col2, corr_value))
        
        # Sort by absolute correlation value
        corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # Display insights
        for col1, col2, corr_value in corr_pairs:
            if abs(corr_value) >= 0.5:
                strength = "Strong" if abs(corr_value) >= 0.7 else "Moderate"
                direction = "positive" if corr_value > 0 else "negative"
                
                sensor_names = {
                    'temperature': 'Temperature',
                    'pressure': 'Pressure',
                    'vibration': 'Vibration',
                    'power': 'Power'
                }
                
                st.markdown(f"**{strength} {direction} correlation** between {sensor_names[col1]} and {sensor_names[col2]} ({corr_value:.2f})")
                
                if col1 == 'temperature' and col2 == 'vibration' and corr_value > 0:
                    st.markdown("- Higher temperatures are associated with increased vibration, which may indicate friction issues.")
                elif col1 == 'vibration' and col2 == 'power' and corr_value > 0:
                    st.markdown("- Increased vibration correlates with higher power consumption, suggesting reduced efficiency.")
                elif col1 == 'temperature' and col2 == 'power' and corr_value > 0:
                    st.markdown("- Higher temperatures correlate with increased power usage, which could indicate thermal inefficiency.")

def show_pca_analysis(data):
    """
    Perform and display PCA analysis on sensor data
    
    Parameters:
    data (DataFrame): Filtered sensor data
    """
    # Extract sensor features
    features = data[['temperature', 'pressure', 'vibration', 'power']].copy()
    
    # Skip if too few data points
    if len(features) < 3:
        st.info("Not enough data points for PCA analysis")
        return
    
    # Scale the data
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Apply PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled_features)
    
    # Create DataFrame with PCA results
    pca_df = pd.DataFrame(
        data=pca_result,
        columns=['Principal Component 1', 'Principal Component 2']
    )
    
    # Add timestamp and maintenance for coloring
    pca_df['timestamp'] = data['timestamp']
    pca_df['maintenance_performed'] = data['maintenance_performed']
    
    # Create scatter plot
    fig = px.scatter(
        pca_df,
        x='Principal Component 1',
        y='Principal Component 2',
        color='maintenance_performed',
        color_continuous_scale=[(0, 'blue'), (1, 'green')],
        hover_data={'timestamp': True, 'maintenance_performed': True},
        labels={'maintenance_performed': 'Maintenance'}
    )
    
    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        title="PCA Analysis of Sensor Data"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### PCA Insights")
        
        # Explain PCA and show component loadings
        st.markdown("""
        Principal Component Analysis (PCA) reduces the dimensionality of sensor data while preserving patterns and relationships. This can help identify:
        
        - Clusters of similar operating conditions
        - Outliers that may indicate anomalies
        - Changes in equipment behavior over time
        """)
        
        # Display component loadings
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=['Component 1', 'Component 2'],
            index=['Temperature', 'Pressure', 'Vibration', 'Power']
        )
        
        st.markdown("#### Component Loadings")
        st.dataframe(loadings.round(3))
        
        # Explain variance
        variance_explained = pca.explained_variance_ratio_
        
        st.markdown("#### Variance Explained")
        st.markdown(f"Component 1: {variance_explained[0]:.2%}")
        st.markdown(f"Component 2: {variance_explained[1]:.2%}")
        st.markdown(f"Total: {sum(variance_explained):.2%}")

def show_maintenance_impact(data):
    """
    Analyze and display the impact of maintenance on sensor readings
    
    Parameters:
    data (DataFrame): Filtered sensor data
    """
    # Check if there are any maintenance events
    maintenance_events = data[data['maintenance_performed'] > 0]
    
    if maintenance_events.empty:
        st.info("No maintenance events in the selected data range")
        return
    
    # For each maintenance event, analyze before and after
    impact_results = []
    
    for _, event in maintenance_events.iterrows():
        event_time = event['timestamp']
        
        # Get data before maintenance (up to 7 days before)
        before_start = event_time - pd.Timedelta(days=7)
        before_data = data[(data['timestamp'] >= before_start) & (data['timestamp'] < event_time)]
        
        # Get data after maintenance (up to 7 days after)
        after_end = event_time + pd.Timedelta(days=7)
        after_data = data[(data['timestamp'] > event_time) & (data['timestamp'] <= after_end)]
        
        # Skip if not enough data
        if len(before_data) < 5 or len(after_data) < 5:
            continue
        
        # Calculate metrics
        metrics = {}
        
        for sensor in ['temperature', 'pressure', 'vibration', 'power']:
            before_avg = before_data[sensor].mean()
            after_avg = after_data[sensor].mean()
            change_pct = ((after_avg - before_avg) / before_avg) * 100
            
            metrics[sensor] = {
                'before': before_avg,
                'after': after_avg,
                'change_pct': change_pct
            }
        
        impact_results.append({
            'event_time': event_time,
            'metrics': metrics
        })
    
    # Display results
    if not impact_results:
        st.info("Not enough data around maintenance events for analysis")
        return
    
    # Create visualization of before/after
    col1, col2 = st.columns(2)
    
    with col1:
        # Select metrics to display
        selected_event = st.selectbox(
            "Select Maintenance Event",
            range(len(impact_results)),
            format_func=lambda i: impact_results[i]['event_time'].strftime('%Y-%m-%d %H:%M')
        )
        
        # Get the selected event data
        event_data = impact_results[selected_event]
        event_time = event_data['event_time']
        metrics = event_data['metrics']
        
        # Create summary table
        summary_data = []
        
        for sensor, values in metrics.items():
            summary_data.append({
                'Sensor': sensor.capitalize(),
                'Before': round(values['before'], 2),
                'After': round(values['after'], 2),
                'Change (%)': round(values['change_pct'], 2)
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    
    with col2:
        # Create bar chart of changes
        change_data = []
        
        for sensor, values in metrics.items():
            change_data.append({
                'Sensor': sensor.capitalize(),
                'Change (%)': values['change_pct']
            })
        
        change_df = pd.DataFrame(change_data)
        
        fig = px.bar(
            change_df,
            x='Sensor',
            y='Change (%)',
            color='Change (%)',
            color_continuous_scale=[(0, 'red'), (0.5, 'gray'), (1, 'green')],
            labels={'Change (%)': 'Change After Maintenance (%)'}
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            title=f"Impact of Maintenance on {event_time.strftime('%Y-%m-%d')}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Show detailed time series around the event
    st.subheader("Time Series Around Maintenance Event")
    
    # Get data from 7 days before to 7 days after
    event_time = impact_results[selected_event]['event_time']
    window_start = event_time - pd.Timedelta(days=7)
    window_end = event_time + pd.Timedelta(days=7)
    
    window_data = data[(data['timestamp'] >= window_start) & (data['timestamp'] <= window_end)]
    
    # Select sensor to visualize
    selected_sensor = st.selectbox(
        "Select Sensor to Visualize",
        ["Temperature", "Pressure", "Vibration", "Power"]
    )
    
    # Map selection to column name
    sensor_column = selected_sensor.lower()
    
    # Create time series plot
    fig = px.scatter(
        window_data,
        x='timestamp',
        y=sensor_column,
        labels={'timestamp': 'Time', sensor_column: f"{selected_sensor} Reading"}
    )
    
    # Add line connecting points
    fig.add_trace(go.Scatter(
        x=window_data['timestamp'],
        y=window_data[sensor_column],
        mode='lines',
        line=dict(color='rgba(0,0,255,0.3)'),
        showlegend=False
    ))
    
    # Add before and after averages
    before_avg = window_data[window_data['timestamp'] < event_time][sensor_column].mean()
    after_avg = window_data[window_data['timestamp'] > event_time][sensor_column].mean()
    
    fig.add_hline(
        y=before_avg,
        line_dash="dash", 
        line_color="blue",
        annotation_text="Before Avg",
        annotation_position="top left"
    )
    
    fig.add_hline(
        y=after_avg,
        line_dash="dash", 
        line_color="green",
        annotation_text="After Avg",
        annotation_position="top right"
    )
    
    # Add maintenance event line
    fig.add_vline(
        x=event_time,
        line_dash="solid", 
        line_width=2,
        line_color="red",
        annotation_text="Maintenance",
        annotation_position="top"
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="closest"
    )
    
    st.plotly_chart(fig, use_container_width=True)
