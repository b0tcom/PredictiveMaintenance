# Architecture Overview - SmartMaintain Predictive Maintenance Platform

## 1. Overview

SmartMaintain is a web-based predictive maintenance platform designed for manufacturing environments. The platform uses IoT sensor data, machine learning algorithms, and data visualization to monitor industrial equipment in real-time, predict potential failures, and optimize maintenance schedules. The primary goal is to reduce downtime, extend equipment lifespan, and minimize maintenance costs.

The application is built as a single-page web application using Streamlit as the frontend framework. It leverages Python-based machine learning algorithms for anomaly detection and failure prediction.

## 2. System Architecture

The system follows a simplified Model-View-Controller (MVC) pattern:

- **View Layer**: Streamlit components handle UI rendering and user interactions
- **Controller Layer**: The main `app.py` file controls application flow and state
- **Model Layer**: Data generation, processing, and ML models handle business logic

```
                  +-------------------+
                  |     User (Web     |
                  |     Browser)      |
                  +--------+----------+
                           |
                           v
+---------------------------------------------+
|                 Streamlit Server            |
|  +----------------+      +---------------+  |
|  |                |      |               |  |
|  |  Components    |<---->|    app.py     |  |
|  |  (UI Modules)  |      | (Controller)  |  |
|  |                |      |               |  |
|  +----------------+      +-------+-------+  |
|                                  |          |
|           +---------------------+|          |
|           |                      v          |
|  +--------v-------+      +------+-------+  |
|  |                |      |              |  |
|  |     Utils      |      |    Models    |  |
|  | (Data Handling)|      | (ML Engines) |  |
|  |                |      |              |  |
|  +----------------+      +--------------+  |
+---------------------------------------------+
```

## 3. Key Components

### 3.1 Frontend (View Layer)

The frontend is built using Streamlit, a Python framework for creating data applications. The UI is divided into several components:

- **Dashboard (`components/dashboard.py`)**: Main overview with key metrics and visualizations
- **Equipment Monitoring (`components/equipment_monitoring.py`)**: Real-time sensor data display
- **Maintenance Alerts (`components/maintenance_alerts.py`)**: Critical alerts and recommendations
- **Performance Metrics (`components/performance_metrics.py`)**: KPIs and operational metrics
- **Historical Analysis (`components/historical_analysis.py`)**: Analysis of past data
- **Downloads (`components/downloads.py`)**: Report generation and export functionality

### 3.2 Application Controller

- **Main App (`app.py`)**: Manages application state, handles routing between components, and coordinates data flow.

### 3.3 Data Processing and Models

- **Data Generator (`utils/data_generator.py`)**: Generates synthetic sensor data for demo purposes
- **Data Processor (`utils/data_processor.py`)**: Transforms raw sensor data into actionable insights
- **Anomaly Detection (`models/anomaly_detection.py`)**: Identifies abnormal equipment behavior using Isolation Forest algorithm
- **Failure Prediction (`models/failure_prediction.py`)**: Predicts potential failures using Random Forest classifiers

### 3.4 Utilities

- **Visualization Generator (`utils/visualization_generator.py`)**: Creates visualizations for reports
- **Version Tracker (`utils/version_tracker.py`)**: Tracks document versions for SR&ED compliance

## 4. Data Flow

1. **Data Acquisition**: 
   - In a production environment, data would be collected from IoT sensors connected to manufacturing equipment
   - In the current implementation, synthetic data is generated to simulate real-world sensor readings

2. **Data Processing**:
   - Raw sensor data (temperature, pressure, vibration, power) is processed to extract meaningful features
   - Anomaly detection algorithms identify unusual patterns that may indicate equipment issues
   - Failure prediction models estimate probability and time to failure for each machine

3. **Visualization and Alerts**:
   - Processed data is displayed through interactive dashboards
   - Critical alerts are generated based on prediction results
   - Maintenance recommendations are provided with actionable steps

4. **Reporting**:
   - Users can generate and download various report formats
   - SR&ED-specific documentation is available for compliance purposes

## 5. External Dependencies

### 5.1 Primary Dependencies

- **Streamlit**: Web application framework
- **Pandas/NumPy**: Data manipulation and numerical computing
- **Scikit-learn**: Machine learning algorithms
- **Plotly**: Interactive data visualization
- **FPDF/Docx/XlsxWriter**: Report generation in various formats

### 5.2 Development and Deployment

- **Replit**: Development and hosting environment
- **Nix**: Package management system

## 6. Deployment Strategy

The application is configured for deployment on Replit's infrastructure with the following characteristics:

- **Container-based**: Deployed in a containerized environment
- **Auto-scaling**: Configured for automatic scaling based on demand
- **Port Mapping**: External port 80 mapped to internal port 5000
- **Python Environment**: Uses Python 3.11

The deployment process is defined in the `.replit` file, which specifies the command to run the application (`streamlit run app.py`) and configures the necessary environment.

## 7. Future Architecture Considerations

Based on the attached assets and project documentation, potential architectural enhancements include:

1. **Real IoT Integration**: Replace synthetic data generation with actual IoT sensor connectivity
2. **Edge Computing**: Add edge processing capabilities for low-latency critical alerts
3. **Cloud Backend**: Implement a proper database for persistent storage of historical data
4. **Enhanced Security**: Add authentication, authorization, and data encryption
5. **API Layer**: Develop a proper API for integration with ERP and MES systems

These enhancements would transform the current demo/prototype into a production-ready system suitable for manufacturing environments.