import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sensor_data(start_time, end_time, interval_minutes=15, num_machines=10):
    """
    Generate realistic IoT sensor data for manufacturing equipment
    
    Parameters:
    start_time (datetime): Start time for data generation
    end_time (datetime): End time for data generation
    interval_minutes (int): Interval between measurements in minutes
    num_machines (int): Number of machines to generate data for
    
    Returns:
    pandas.DataFrame: Generated sensor data
    """
    # Calculate number of time points
    total_minutes = int((end_time - start_time).total_seconds() / 60)
    num_points = total_minutes // interval_minutes + 1
    
    # Create time points
    time_points = [start_time + timedelta(minutes=i*interval_minutes) for i in range(num_points)]
    
    # Generate data for each machine
    all_data = []
    
    for machine_id in range(1, num_machines + 1):
        # Base parameters for this machine
        base_temp = random.uniform(50, 70)  # Base temperature in celsius
        base_pressure = random.uniform(80, 120)  # Base pressure in PSI
        base_vibration = random.uniform(0.2, 0.8)  # Base vibration in mm/s
        base_power = random.uniform(200, 500)  # Base power consumption in kW
        
        # Trend components (some machines will show degradation over time)
        has_temp_trend = random.choice([True, False, False])  # 1/3 chance of temperature trend
        has_vibration_trend = random.choice([True, False, False])  # 1/3 chance of vibration trend
        
        temp_trend_factor = random.uniform(0.01, 0.05) if has_temp_trend else 0
        vibration_trend_factor = random.uniform(0.001, 0.01) if has_vibration_trend else 0
        
        # Scheduled maintenance events (sudden drops in values)
        maintenance_points = []
        if random.random() < 0.5:  # 50% chance of having maintenance during this period
            maintenance_points = [random.randint(0, num_points-1) for _ in range(random.randint(1, 3))]
        
        # Generate data points
        for i, timestamp in enumerate(time_points):
            # Time of day and day of week effects
            hour = timestamp.hour
            weekday = timestamp.weekday()
            
            # Machines run hotter during peak hours (9am-5pm) and weekdays
            time_factor = 1.0 + 0.1 * (9 <= hour <= 17) + 0.05 * (0 <= weekday <= 4)
            
            # Trends over time (equipment degradation)
            trend_factor = 1.0 + (i / num_points)
            
            # Random variations
            temp_variation = random.normalvariate(0, 2)
            pressure_variation = random.normalvariate(0, 5)
            vibration_variation = random.normalvariate(0, 0.1)
            power_variation = random.normalvariate(0, 20)
            
            # Calculate values with seasonality, trends and random variations
            temperature = base_temp * time_factor + temp_variation + (i * temp_trend_factor * trend_factor)
            pressure = base_pressure * time_factor + pressure_variation
            vibration = base_vibration * time_factor + vibration_variation + (i * vibration_trend_factor * trend_factor)
            power = base_power * time_factor + power_variation
            
            # Inject anomalies
            if random.random() < 0.02:  # 2% chance of random spike
                anomaly_factor = random.uniform(1.2, 1.5)
                anomaly_type = random.choice(['temperature', 'pressure', 'vibration', 'power'])
                
                if anomaly_type == 'temperature':
                    temperature *= anomaly_factor
                elif anomaly_type == 'pressure':
                    pressure *= anomaly_factor
                elif anomaly_type == 'vibration':
                    vibration *= anomaly_factor
                else:
                    power *= anomaly_factor
            
            # Reset after maintenance
            if i in maintenance_points:
                temperature = base_temp + temp_variation
                vibration = base_vibration + vibration_variation
                maintenance_performed = 1
            else:
                maintenance_performed = 0
            
            # Add data point
            all_data.append({
                'timestamp': timestamp,
                'machine_id': f'Machine-{machine_id}',
                'temperature': round(temperature, 2),
                'pressure': round(pressure, 2),
                'vibration': round(vibration, 3),
                'power': round(power, 2),
                'maintenance_performed': maintenance_performed
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    return df

def generate_equipment_data(num_machines, previous_data=None):
    """
    Generate equipment metadata and status information
    
    Parameters:
    num_machines (int): Number of machines to generate data for
    previous_data (DataFrame): Previous equipment data to update (optional)
    
    Returns:
    pandas.DataFrame: Generated equipment data
    """
    machine_types = ['CNC Mill', 'Injection Molder', 'Robotic Arm', 'Assembly Line', 
                     'Packaging Unit', 'Conveyor System', 'Welding Robot', 'Press Machine']
    manufacturers = ['ABB', 'Siemens', 'Fanuc', 'Bosch', 'Mitsubishi', 'Rockwell', 'Honeywell', 'Schneider']
    installation_years = range(2015, 2023)
    
    if previous_data is not None:
        # Update existing data
        data = previous_data.copy()
        
        # Update status, health_score, and maintenance_due_days based on simulated degradation
        for idx, row in data.iterrows():
            # Randomly decrease health score for some machines
            if random.random() < 0.3:  # 30% chance of health score change
                decrease = random.uniform(0.1, 1.0)
                new_score = max(0, row['health_score'] - decrease)
                data.at[idx, 'health_score'] = round(new_score, 1)
                
                # Update status based on new health score
                if new_score < 60:
                    data.at[idx, 'status'] = 'Critical'
                elif new_score < 80:
                    data.at[idx, 'status'] = 'Warning'
                else:
                    data.at[idx, 'status'] = 'Healthy'
                
                # Update maintenance due date
                if new_score < 70:
                    data.at[idx, 'maintenance_due_days'] = max(0, row['maintenance_due_days'] - random.randint(1, 3))
                
        return data
    
    # Generate new data
    data = []
    for i in range(1, num_machines + 1):
        machine_id = f'Machine-{i}'
        machine_type = random.choice(machine_types)
        manufacturer = random.choice(manufacturers)
        installation_year = random.choice(installation_years)
        
        # Generate health score (0-100, higher is better)
        health_score = random.uniform(60, 100)
        
        # Status based on health score
        if health_score < 70:
            status = 'Critical'
            maintenance_due_days = random.randint(0, 7)
        elif health_score < 85:
            status = 'Warning'
            maintenance_due_days = random.randint(7, 30)
        else:
            status = 'Healthy'
            maintenance_due_days = random.randint(30, 90)
        
        # Location in the factory
        location = f'Zone-{random.choice("ABCDEF")}'
        
        data.append({
            'machine_id': machine_id,
            'machine_type': machine_type,
            'manufacturer': manufacturer,
            'installation_year': installation_year,
            'health_score': round(health_score, 1),
            'status': status,
            'maintenance_due_days': maintenance_due_days,
            'location': location,
            'last_maintenance': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(data)
