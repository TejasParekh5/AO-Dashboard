from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import datetime
import json

# Set the current date
current_date = datetime.datetime(2025, 6, 17)

# Create FastAPI app
app = FastAPI(title="Cybersecurity KPI Suggestion API",
              description="API for generating smart suggestions for Application Owners based on their security metrics")

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the Excel file
excel_path = os.path.join(current_dir, 'Cybersecurity_KPI_Minimal.xlsx')

# Load the data
print(f"Loading data from: {excel_path}")
df = pd.read_excel(excel_path)

# Add some derived columns for analysis
df['Days_Open'] = np.where(pd.isna(df['Closure_Date']),
                           (current_date -
                            pd.to_datetime(df['First_Detected_Date'])).dt.days,
                           df['Days_to_Close'])

df['Is_Critical_High'] = df['Vulnerability_Severity'].isin(
    ['Critical', 'High'])
df['Is_Over_30_Days'] = df['Days_Open'] > 30
df['Is_Critical_High_Over_30'] = df['Is_Critical_High'] & df['Is_Over_30_Days']
df['Is_High_Risk'] = (df['CVSS_Score'] > 7) | (df['Risk_Score'] > 7)

# Helper function to convert numpy values to Python native types


def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


# Load the sentence transformer model
try:
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    print("Loaded sentence transformer model for suggestions")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Define suggestion templates with priority tags
suggestion_templates = [
    {
        "template": "🚨 Focus on addressing the {critical_high_count} high and critical vulnerabilities immediately.",
        "priority": "urgent",
        "condition": lambda metrics: metrics['critical_high_count'] > 3
    },
    {
        "template": "🚨 You have {old_vulns_count} vulnerabilities open for more than 30 days. Prioritize these for immediate remediation.",
        "priority": "urgent",
        "condition": lambda metrics: metrics['old_vulns_count'] > 5
    },
    {
        "template": "⚠️ Your average time to close vulnerabilities is {avg_days_to_close:.1f} days. The department average is {dept_avg:.1f} days.",
        "priority": "medium",
        "condition": lambda metrics: metrics['avg_days_to_close'] > metrics['dept_avg']
    },
    {
        "template": "🚨 There are {high_risk_count} high-risk items (CVSS or Risk Score > 7) that require urgent attention.",
        "priority": "urgent",
        "condition": lambda metrics: metrics['high_risk_count'] > 2
    },
    {
        "template": "⚠️ Consider reviewing your patch management process to improve remediation time, especially for Application {worst_app}.",
        "priority": "medium",
        "condition": lambda metrics: True  # Always consider this
    },
    {
        "template": "⚠️ Implementing automated scanning could help identify vulnerabilities earlier and reduce your average detection time.",
        "priority": "medium",
        "condition": lambda metrics: metrics['avg_days_to_close'] > 25
    },
    {
        "template": "⚠️ Regular security training for your team could reduce the vulnerability introduction rate, especially for repeating issues ({repeat_count}).",
        "priority": "medium",
        "condition": lambda metrics: metrics['repeat_count'] > 1
    },
    {
        "template": "⚠️ Establish a vulnerability prioritization framework to help focus on Critical issues in {dept_name} department.",
        "priority": "medium",
        "condition": lambda metrics: metrics['critical_high_count'] > 0
    },
    {
        "template": "✅ Your vulnerability management for Application {best_app} is performing well. Consider applying similar practices to other applications.",
        "priority": "good",
        "condition": lambda metrics: 'best_app' in metrics
    },
    {
        "template": "✅ Your team has successfully reduced the average closure time for Medium severity issues. Continue this good practice.",
        "priority": "good",
        "condition": lambda metrics: metrics['avg_days_to_close'] < 20
    }
]

# Define the request and response models


class MetricsRequest(BaseModel):
    ao_id: str


class SuggestionResponse(BaseModel):
    ao_id: str
    ao_name: str
    suggestions: List[Dict[str, Any]]
    metrics: Dict[str, Any]

# Function to generate suggestions based on AO metrics


def generate_suggestions_for_ao(ao_id):
    if model is None:
        return {"error": "Suggestion system temporarily unavailable."}

    # Filter data for this AO
    ao_data = df[df['Application_Owner_ID'] == ao_id]

    # If no data for this AO
    if len(ao_data) == 0:
        return {"error": f"No data available for Application Owner {ao_id}."}

    # Get AO name
    ao_name = ao_data['Application_Owner_Name'].iloc[0]

    # Calculate metrics for this AO
    critical_high_count = ao_data['Is_Critical_High'].sum()
    old_vulns_count = ao_data['Is_Over_30_Days'].sum()
    high_risk_count = ao_data['Is_High_Risk'].sum()
    avg_days_to_close = ao_data['Days_to_Close'].mean()
    repeat_count = ao_data['Number_of_Repeats'].mean()

    # Get department metrics
    dept_names = ao_data['Dept_Name'].unique()
    dept_avg = df['Days_to_Close'].mean()

    # Calculate application-specific metrics to find best and worst apps
    app_metrics = {}
    for app in ao_data['Application_Name'].unique():
        app_data = ao_data[ao_data['Application_Name'] == app]
        app_metrics[app] = {
            'avg_days': app_data['Days_to_Close'].mean(),
            'critical_high': app_data['Is_Critical_High'].sum(),
            'high_risk': app_data['Is_High_Risk'].sum()
        }

    # Find worst and best apps
    if app_metrics:
        worst_app = max(app_metrics, key=lambda x: (
            app_metrics[x]['critical_high'], app_metrics[x]['avg_days']))

        # Find best app only if there's one with good metrics
        best_apps = [app for app, metrics in app_metrics.items()
                     if metrics['critical_high'] == 0 and metrics['avg_days'] < dept_avg]

        best_app = best_apps[0] if best_apps else None
    else:
        worst_app = None
        best_app = None

    # Compile metrics for template formatting and conditions
    metrics = {
        'critical_high_count': critical_high_count,
        'old_vulns_count': old_vulns_count,
        'high_risk_count': high_risk_count,
        'avg_days_to_close': avg_days_to_close,
        'dept_avg': dept_avg,
        'repeat_count': repeat_count,
        'worst_app': worst_app,
        'dept_name': dept_names[0] if len(dept_names) > 0 else "Unknown"
    }

    if best_app:
        metrics['best_app'] = best_app

    # Create context from the AO's data for embedding
    ao_context = f"""
    Application Owner: {ao_id} ({ao_name})
    Applications: {', '.join(ao_data['Application_Name'].unique())}
    Critical/High vulnerabilities: {critical_high_count}
    Vulnerabilities > 30 days: {old_vulns_count}
    Average closure time: {avg_days_to_close:.1f} days
    High risk items: {high_risk_count}
    Repeat issues average: {repeat_count:.1f}
    """

    # Generate and format applicable suggestions
    applicable_suggestions = []
    for template_data in suggestion_templates:
        if template_data["condition"](metrics):
            try:
                formatted = template_data["template"].format(**metrics)
                applicable_suggestions.append({
                    "text": formatted,
                    "priority": template_data["priority"]
                })
            except Exception as e:
                print(f"Error formatting suggestion: {e}")

    # If we have the model, rank suggestions by relevance
    if model and applicable_suggestions:
        context_embedding = model.encode([ao_context])[0]
        suggestion_texts = [s["text"] for s in applicable_suggestions]
        suggestion_embeddings = model.encode(suggestion_texts)

        # Calculate similarity
        similarities = cosine_similarity(
            [context_embedding], suggestion_embeddings)[0]

        # Add similarity scores and sort
        for i, suggestion in enumerate(applicable_suggestions):
            suggestion["relevance_score"] = float(similarities[i])

        applicable_suggestions.sort(
            key=lambda x: x["relevance_score"], reverse=True)    # Prepare the final response
    result = {
        "ao_id": ao_id,
        "ao_name": ao_name,
        "suggestions": applicable_suggestions[:5],  # Return top 5 suggestions
        "metrics": metrics
    }

    # Convert all numpy types to Python native types
    result = convert_numpy_types(result)

    return result

# API endpoints


@app.get("/")
async def root():
    return {"message": "Cybersecurity KPI Suggestion API is running"}


@app.get("/suggestions/{ao_id}", response_model=SuggestionResponse)
async def get_suggestions(ao_id: str):
    if ao_id not in df['Application_Owner_ID'].unique():
        raise HTTPException(
            status_code=404, detail=f"Application Owner {ao_id} not found")

    suggestions = generate_suggestions_for_ao(ao_id)

    if "error" in suggestions:
        raise HTTPException(status_code=500, detail=suggestions["error"])

    return suggestions


@app.get("/aos")
async def get_all_aos():
    aos = df[['Application_Owner_ID', 'Application_Owner_Name']
             ].drop_duplicates().to_dict('records')
    # Convert any numpy types
    aos = convert_numpy_types(aos)
    return {"application_owners": aos}


@app.get("/departments")
async def get_departments():
    departments = df['Dept_Name'].unique().tolist()
    # Convert any numpy types
    departments = convert_numpy_types(departments)
    return {"departments": departments}


@app.get("/applications")
async def get_applications(ao_id: Optional[str] = None):
    if ao_id:
        apps = df[df['Application_Owner_ID'] ==
                  ao_id]['Application_Name'].unique().tolist()
    else:
        apps = df['Application_Name'].unique().tolist()
    # Convert any numpy types
    apps = convert_numpy_types(apps)
    return {"applications": apps}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
