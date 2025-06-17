# Cybersecurity KPI Dashboard for Application Owners

An interactive dashboard for Application Owners (AOs) to monitor, analyze, and improve their application-related security performance. The dashboard features an intelligent suggestion system powered by a compact LLM to provide personalized recommendations.

## Project Components

This project contains two main dashboards:

1. **Standard Dashboard** (`dashboard.py`) - Basic dashboard with essential KPI visualization features
2. **Enhanced Dashboard** (`enhanced_dashboard.py`) - Advanced dashboard with additional features and ML-powered suggestion system

## Features

### Standard Dashboard Features

- **Interactive Filtering**: Filter by Application Owner, Department, and Status
- **Real-time Visualizations**: Track vulnerabilities, risk scores, and remediation progress
- **Performance Metrics**: Individual AO performance tracking and comparison
- **Export Functionality**: Export insights as CSV for further analysis
- **Highlight Critical Issues**:
  - Vulnerabilities open > 30 days with High or Critical severity
  - Items with CVSS_Score > 7 or Risk_Score > 7 flagged as urgent

### Enhanced Dashboard Additional Features

- **Smart Suggestion System**: LLM-driven feedback engine to help AOs improve their cybersecurity KPIs
- **Relationship Mapping Visuals**: Hierarchical sankey diagrams and bubble charts
- **AO Performance Panel**: Detailed metrics comparing AO to organization average
- **Risk Concentration Visualizations**: Heatmaps and additional analysis tools

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required packages:

```bash
# For standard dashboard
pip install -r requirements.txt

# For enhanced dashboard with ML capabilities
pip install -r requirements_enhanced.txt
```

## Running the Dashboards

### Standard Dashboard

```bash
python dashboard.py
```

### Enhanced Dashboard with ML Suggestions

First, start the suggestion API:

```bash
python suggestion_api.py
```

Then in a new terminal, start the dashboard:

```bash
python enhanced_dashboard.py
```

### Quick Start (Enhanced Dashboard)

For convenience, you can use the provided batch file to start both the suggestion API and enhanced dashboard:

```bash
start_full_system.bat
```

The dashboard will be available at http://127.0.0.1:8050/ in your web browser.

## Dashboard Components

1. **Filter Controls**: Select Application Owner, Department, and Status
2. **Smart Suggestions**: AI-generated recommendations based on AO's performance data
3. **Severity Distribution**: Breakdown of vulnerabilities by severity
4. **Status Tracker**: Current status of all vulnerabilities
5. **Risk Score Analysis**: Distribution of risk scores with high-risk threshold
6. **Days to Close Analysis**: Average remediation time by severity
7. **Urgent Issues Table**: Highlighting critical issues requiring immediate attention
8. **AO Performance Panel**: Detailed metrics for the selected Application Owner

## Data Structure

The dashboard uses the `Cybersecurity_KPI_Minimal.xlsx` file which contains:

- Application Owner information
- Application and Asset details
- Vulnerability data including severity, CVSS scores, and risk metrics

## Training the ML Model

See `TRAINING_AND_RUNNING_GUIDE.md` for detailed instructions on training the model and running the full system.
