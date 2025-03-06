import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

def predict_failures(sensor_data, equipment_data):
    """
    Predict equipment failures based on sensor data and equipment information
    
    Parameters:
    sensor_data (DataFrame): IoT sensor data
    equipment_data (DataFrame): Equipment metadata
    
    Returns:
    dict: Dictionary with failure predictions for each machine
    """
    prediction_results = {}
    
    # Process each machine separately
    for machine_id in sensor_data['machine_id'].unique():
        machine_data = sensor_data[sensor_data['machine_id'] == machine_id].copy()
        machine_info = equipment_data[equipment_data['machine_id'] == machine_id]
        
        if machine_info.empty or len(machine_data) < 10:
            continue
            
        machine_info = machine_info.iloc[0]
        
        # Extract features for prediction
        features = prepare_features(machine_data, machine_info)
        
        # Predict failure probability
        failure_prob = predict_failure_probability(features)
        
        # Predict days to failure
        days_to_failure = predict_days_to_failure(features, failure_prob)
        
        # Calculate estimated downtime and cost
        downtime, cost = estimate_impact(machine_info, days_to_failure, failure_prob)
        
        # Store predictions
        prediction_results[machine_id] = {
            'failure_probability': round(failure_prob, 3),
            'days_to_failure': int(days_to_failure),
            'estimated_downtime_hours': round(downtime, 1),
            'estimated_cost': int(cost),
            'prediction_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'confidence': calculate_confidence(machine_data, features)
        }
    
    return prediction_results

def prepare_features(machine_data, machine_info):
    """
    Prepare features for prediction models
    
    Parameters:
    machine_data (DataFrame): Sensor data for a specific machine
    machine_info (Series): Equipment information for a specific machine
    
    Returns:
    dict: Dictionary with engineered features
    """
    # Sort by timestamp
    machine_data = machine_data.sort_values('timestamp')
    
    # Calculate rolling statistics
    recent_data = machine_data.tail(48)  # Last 48 measurements
    
    # Recent trends (linear regression slopes)
    temp_trend = np.polyfit(range(len(recent_data)), recent_data['temperature'], 1)[0] if len(recent_data) > 5 else 0
    vibration_trend = np.polyfit(range(len(recent_data)), recent_data['vibration'], 1)[0] if len(recent_data) > 5 else 0
    
    # Machine age in years
    current_year = datetime.now().year
    installation_year = machine_info['installation_year']
    machine_age = current_year - installation_year
    
    # Days since last maintenance
    try:
        last_maintenance = datetime.strptime(machine_info['last_maintenance'], '%Y-%m-%d')
        days_since_maintenance = (datetime.now() - last_maintenance).days
    except:
        days_since_maintenance = 365  # Default to 1 year if data not available
    
    # Extract statistics
    features = {
        'machine_age': machine_age,
        'installation_year': installation_year,
        'days_since_maintenance': days_since_maintenance,
        'health_score': machine_info['health_score'],
        'avg_temperature': recent_data['temperature'].mean(),
        'max_temperature': recent_data['temperature'].max(),
        'temperature_std': recent_data['temperature'].std(),
        'temperature_trend': temp_trend,
        'avg_vibration': recent_data['vibration'].mean(),
        'max_vibration': recent_data['vibration'].max(),
        'vibration_std': recent_data['vibration'].std(),
        'vibration_trend': vibration_trend,
        'avg_pressure': recent_data['pressure'].mean(),
        'pressure_std': recent_data['pressure'].std(),
        'avg_power': recent_data['power'].mean(),
        'power_std': recent_data['power'].std()
    }
    
    return features

def predict_failure_probability(features):
    """
    Simulate a machine learning model that predicts failure probability
    
    In a real-world application, this would be a trained model.
    For this demo, we use a simplified heuristic algorithm.
    
    Parameters:
    features (dict): Engineered features
    
    Returns:
    float: Probability of failure (0-1)
    """
    # This is a simplified heuristic that would be replaced by a trained model
    base_prob = 0.1
    
    # Age effect
    age_factor = min(0.4, features['machine_age'] * 0.03)
    
    # Maintenance effect
    maintenance_factor = min(0.3, features['days_since_maintenance'] * 0.001)
    
    # Health score effect (inverse - lower health means higher probability)
    health_factor = max(0, (100 - features['health_score']) * 0.005)
    
    # Temperature effect
    temp_factor = features['temperature_trend'] * 20 if features['temperature_trend'] > 0 else 0
    temp_factor += max(0, (features['max_temperature'] - 85) * 0.01) if features['max_temperature'] > 85 else 0
    
    # Vibration effect
    vibration_factor = features['vibration_trend'] * 50 if features['vibration_trend'] > 0 else 0
    vibration_factor += max(0, (features['max_vibration'] - 1.0) * 0.2) if features['max_vibration'] > 1.0 else 0
    
    # Combined probability (capped at 0.95)
    probability = min(0.95, base_prob + age_factor + maintenance_factor + health_factor + temp_factor + vibration_factor)
    
    return probability

def predict_days_to_failure(features, failure_probability):
    """
    Predict the expected number of days until failure
    
    Parameters:
    features (dict): Engineered features
    failure_probability (float): Probability of failure
    
    Returns:
    int: Estimated days until failure
    """
    if failure_probability < 0.2:
        # Low probability: 3-6 months
        return random.randint(90, 180)
    elif failure_probability < 0.4:
        # Medium-low probability: 1-3 months
        return random.randint(30, 90)
    elif failure_probability < 0.6:
        # Medium probability: 2-4 weeks
        return random.randint(14, 30)
    elif failure_probability < 0.8:
        # Medium-high probability: 1-2 weeks
        return random.randint(7, 14)
    else:
        # High probability: 0-7 days
        return random.randint(0, 7)

def estimate_impact(machine_info, days_to_failure, failure_probability):
    """
    Estimate the impact of a failure in terms of downtime and cost
    
    Parameters:
    machine_info (Series): Equipment information
    days_to_failure (int): Days until predicted failure
    failure_probability (float): Probability of failure
    
    Returns:
    tuple: (Estimated downtime in hours, Estimated cost in dollars)
    """
    # Base downtime depends on machine type
    machine_type = machine_info['machine_type']
    
    if machine_type == 'CNC Mill':
        base_downtime = 24
        base_cost = 5000
    elif machine_type == 'Injection Molder':
        base_downtime = 36
        base_cost = 8000
    elif machine_type == 'Robotic Arm':
        base_downtime = 16
        base_cost = 4000
    elif machine_type == 'Assembly Line':
        base_downtime = 48
        base_cost = 12000
    elif machine_type == 'Packaging Unit':
        base_downtime = 12
        base_cost = 3000
    else:
        base_downtime = 24
        base_cost = 6000
    
    # Calculate machine age based on installation year
    current_year = datetime.now().year
    machine_age = current_year - machine_info['installation_year']
    
    # Adjust based on machine age
    age_factor = 1 + (machine_age - 3) * 0.1 if machine_age > 3 else 1
    
    # Adjust based on failure probability (more severe failures take longer to fix)
    severity_factor = 1 + failure_probability
    
    # Calculate final estimates
    estimated_downtime = base_downtime * age_factor * severity_factor
    estimated_cost = base_cost * age_factor * severity_factor
    
    return estimated_downtime, estimated_cost

def calculate_confidence(machine_data, features):
    """
    Calculate confidence level for the prediction
    
    Parameters:
    machine_data (DataFrame): Sensor data for the machine
    features (dict): Engineered features
    
    Returns:
    float: Confidence score (0-1)
    """
    # This is a simplified heuristic based on data quality
    # In a real system, this would be based on model metrics
    
    # More data points = higher confidence
    data_factor = min(0.5, len(machine_data) / 1000)
    
    # More consistent data = higher confidence
    consistency_factor = 0.3 * (1 - min(1, features['temperature_std'] / 10))
    consistency_factor += 0.2 * (1 - min(1, features['vibration_std'] / 0.5))
    
    # Confidence level (0-1)
    confidence = 0.5 + data_factor + consistency_factor
    
    return min(0.95, max(0.5, confidence))

import random  # For the simulate functions
