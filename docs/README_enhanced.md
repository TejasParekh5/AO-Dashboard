# Advanced Cybersecurity KPI Dashboard with Smart Suggestion System

An intelligent, interactive dashboard for Application Owners (AOs) to monitor, analyze, and improve their application-related security performance. The dashboard features an LLM-powered suggestion system that provides personalized recommendations based on security metrics.

## Key Features

### 1. Interactive Filtering

- Multi-select Application Owner dropdown
- Department auto-populates based on AO → Application → Department relationship
- Status filtering options

### 2. KPI Visualization Panel

- Key metrics per AO and application:
  - Average CVSS Score & Risk Score
  - Percentage of Open vs Closed vulnerabilities
  - Average Days to Close
  - Total High/Critical issues
  - Repeat Issue Count

### 3. Urgent Issues Table

- Highlights vulnerabilities:
  - Open >30 days with Severity = High or Critical
  - CVSS > 7 or Risk Score > 7
- Includes actionable columns: Status, Priority, AO Name, Application

### 4. AO Performance Panel

- Compares each AO's performance with organization average
- Visualizations:
  - Risk trend over time (line chart)
  - Vulnerability distribution by severity (bar chart)
  - Heatmap of Risk Score by Application & Severity

### 5. Relationship Mapping Visuals

- AO → Applications → Department (hierarchical sankey diagram)
- Vulnerability → Asset → Risk Cluster (bubble chart)
- Risk concentration by severity & application (heatmap)

### 6. LLM-Based Smart Suggestion System

- Uses Sentence Transformers (compact LLM) for lightweight inference
- Provides personalized, contextual improvement tips based on metrics
- Suggestions tagged with priority:
  - 🚨 Urgent (red)
  - ⚠️ Medium Priority (yellow)
  - ✅ Performing Well (green)

### 7. Export Capabilities

- Filtered views and KPI tables exportable as CSV
- Suggestions & AO performance reports exportable as PDF

## System Architecture

The system consists of two main components:

1. **Suggestion API** (FastAPI):

   - Processes AO metrics to generate contextual suggestions
   - Uses Sentence Transformers for intelligent ranking
   - Provides suggestions via a REST API

2. **Dashboard Application** (Dash):
   - Interactive web interface for data visualization
   - Connects to Suggestion API for smart recommendations
   - Provides filtering, analysis, and export capabilities

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

### Option 1: Run with Smart Suggestions (Recommended)

Use the provided startup script to launch both the suggestion API and dashboard:

```bash
start_enhanced_dashboard.bat
```

### Option 2: Run Dashboard Only

If you only need the dashboard without smart suggestions:

```bash
python enhanced_dashboard.py
```

The dashboard will be available at http://127.0.0.1:8050/ in your web browser.

## Data Structure

The dashboard uses the `Cybersecurity_KPI_Minimal.xlsx` file which contains:

- Application Owner information (ID, Name)
- Application and Asset details (ID, Name, Type)
- Vulnerability data (Severity, CVSS scores, Risk metrics)
- Remediation tracking (Detection dates, Closure dates, Days to Close)
- Department affiliations

## Technical Implementation

- **Backend**: Python, Pandas, FastAPI
- **Frontend**: Plotly Dash with Bootstrap components
- **ML**: Sentence Transformers (SBERT)
- **Data**: Excel data source with derived metrics

## Relationships Tracked

The system handles these important relationships:

- One Application Owner may manage multiple Applications
- One Application Owner may be linked to multiple Departments via apps
- Applications are associated with multiple Assets
- Assets have different Vulnerability profiles
- Vulnerabilities have varying Severity and Risk levels
