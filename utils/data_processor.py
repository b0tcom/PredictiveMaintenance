import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.anomaly_detection import detect_anomalies
from models.failure_prediction import predict_failures

def process_sensor_data(sensor_data, equipment_data):
    """
    Process sensor data to calculate anomalies, predictions, and maintenance recommendations
    
    Parameters:
    sensor_data (DataFrame): Raw sensor data from IoT devices
    equipment_data (DataFrame): Equipment metadata
    
    Returns:
    dict: Processed data including anomalies, predictions, and recommendations
    """
    processed_data = {
        'sensor_data': sensor_data.copy(),
        'equipment_data': equipment_data.copy(),
        'anomalies': {},
        'predictions': {},
        'recommendations': {},
        'statistics': {}
    }
    
    # Calculate summary statistics for each machine
    machine_stats = {}
    for machine_id in sensor_data['machine_id'].unique():
        machine_data = sensor_data[sensor_data['machine_id'] == machine_id]
        
        # Get most recent data
        recent_data = machine_data.sort_values('timestamp').tail(24)  # Last 24 readings
        
        # Calculate stats
        stats = {
            'temperature': {
                'current': recent_data['temperature'].iloc[-1],
                'mean': recent_data['temperature'].mean(),
                'min': recent_data['temperature'].min(),
                'max': recent_data['temperature'].max(),
                'std': recent_data['temperature'].std()
            },
            'pressure': {
                'current': recent_data['pressure'].iloc[-1],
                'mean': recent_data['pressure'].mean(),
                'min': recent_data['pressure'].min(),
                'max': recent_data['pressure'].max(),
                'std': recent_data['pressure'].std()
            },
            'vibration': {
                'current': recent_data['vibration'].iloc[-1],
                'mean': recent_data['vibration'].mean(),
                'min': recent_data['vibration'].min(),
                'max': recent_data['vibration'].max(),
                'std': recent_data['vibration'].std()
            },
            'power': {
                'current': recent_data['power'].iloc[-1],
                'mean': recent_data['power'].mean(),
                'min': recent_data['power'].min(),
                'max': recent_data['power'].max(),
                'std': recent_data['power'].std()
            }
        }
        
        machine_stats[machine_id] = stats
    
    processed_data['statistics'] = machine_stats
    
    # Detect anomalies for each machine
    anomaly_results = detect_anomalies(sensor_data)
    processed_data['anomalies'] = anomaly_results
    
    # Predict failures
    prediction_results = predict_failures(sensor_data, equipment_data)
    processed_data['predictions'] = prediction_results
    
    # Generate maintenance recommendations
    recommendations = {}
    for machine_id, prediction in prediction_results.items():
        machine_info = equipment_data[equipment_data['machine_id'] == machine_id].iloc[0]
        
        if prediction['failure_probability'] > 0.7:
            urgency = "Immediate"
            message = f"Schedule immediate maintenance for {machine_id}. High risk of failure within {prediction['days_to_failure']} days."
            actions = ["Replace bearings", "Check lubrication", "Verify alignment", "Inspect electrical connections"]
        elif prediction['failure_probability'] > 0.4:
            urgency = "Soon"
            message = f"Plan maintenance for {machine_id} within {max(1, prediction['days_to_failure'] - 7)} days."
            actions = ["Inspect for unusual wear", "Check lubrication", "Monitor vibration levels"]
        elif prediction['failure_probability'] > 0.2:
            urgency = "Planned"
            message = f"Include {machine_id} in next planned maintenance cycle."
            actions = ["Routine inspection", "Check sensor calibration"]
        else:
            urgency = "Normal"
            message = f"No immediate action required for {machine_id}."
            actions = ["Continue regular monitoring"]
            
        recommendations[machine_id] = {
            'urgency': urgency,
            'message': message,
            'actions': actions,
            'estimated_downtime': prediction['estimated_downtime_hours'],
            'estimated_cost': prediction['estimated_cost']
        }
    
    processed_data['recommendations'] = recommendations
    
    return processed_data
