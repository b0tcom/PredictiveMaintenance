import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def detect_anomalies(sensor_data):
    """
    Detect anomalies in sensor data using Isolation Forest algorithm
    
    Parameters:
    sensor_data (DataFrame): IoT sensor data
    
    Returns:
    dict: Dictionary with anomaly detection results for each machine
    """
    anomaly_results = {}
    
    # Process each machine separately
    for machine_id in sensor_data['machine_id'].unique():
        machine_data = sensor_data[sensor_data['machine_id'] == machine_id].copy()
        
        # Skip if not enough data
        if len(machine_data) < 10:
            continue
            
        # Extract features for anomaly detection
        features = machine_data[['temperature', 'pressure', 'vibration', 'power']].copy()
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Train isolation forest model
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,  # Assuming 5% of data points are anomalies
            random_state=42
        )
        
        # Fit and predict
        machine_data['anomaly_score'] = model.fit_predict(scaled_features)
        
        # Convert to binary (1: normal, -1: anomaly)
        machine_data['is_anomaly'] = machine_data['anomaly_score'].apply(lambda x: x == -1)
        
        # Find the most recent anomalies
        recent_anomalies = machine_data[machine_data['is_anomaly']].sort_values('timestamp', ascending=False).head(5)
        
        # Extract anomaly information
        anomaly_info = []
        for _, row in recent_anomalies.iterrows():
            # Determine which sensor(s) contributed to the anomaly
            sensor_values = {
                'temperature': row['temperature'],
                'pressure': row['pressure'],
                'vibration': row['vibration'],
                'power': row['power']
            }
            
            # Get z-scores for each sensor
            z_scores = {}
            for sensor in ['temperature', 'pressure', 'vibration', 'power']:
                mean_val = features[sensor].mean()
                std_val = features[sensor].std()
                if std_val > 0:
                    z_scores[sensor] = abs((sensor_values[sensor] - mean_val) / std_val)
                else:
                    z_scores[sensor] = 0
            
            # Identify the most unusual sensor(s)
            unusual_sensors = [sensor for sensor, z_score in z_scores.items() if z_score > 2.0]
            
            if not unusual_sensors:
                unusual_sensors = [max(z_scores.items(), key=lambda x: x[1])[0]]
            
            anomaly_info.append({
                'timestamp': row['timestamp'],
                'unusual_sensors': unusual_sensors,
                'sensor_values': sensor_values,
                'z_scores': z_scores
            })
        
        # Calculate overall anomaly statistics
        anomaly_count = machine_data['is_anomaly'].sum()
        anomaly_percentage = (anomaly_count / len(machine_data)) * 100
        
        # Store results for this machine
        anomaly_results[machine_id] = {
            'recent_anomalies': anomaly_info,
            'anomaly_count': int(anomaly_count),
            'anomaly_percentage': round(anomaly_percentage, 2),
            'has_recent_anomaly': len(recent_anomalies) > 0
        }
    
    return anomaly_results
