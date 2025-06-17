import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import base64
import io

# Set the current date
current_date = datetime.datetime(2025, 6, 16)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the Excel file
excel_path = os.path.join(current_dir, 'Cybersecurity_KPI_Minimal.xlsx')

# Read the Excel file
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

# Load a small sentence transformer model for suggestions
try:
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    print("Loaded sentence transformer model for suggestions")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Function to generate suggestions for AOs


def generate_suggestions(ao_id):
    if model is None:
        return "Suggestion system temporarily unavailable."

    ao_data = df[df['Application_Owner_ID'] == ao_id]

    # If no data for this AO
    if len(ao_data) == 0:
        return "No data available for this Application Owner."

    # Calculate metrics for this AO
    critical_high_count = ao_data['Is_Critical_High'].sum()
    old_vulns_count = ao_data['Is_Over_30_Days'].sum()
    high_risk_count = ao_data['Is_High_Risk'].sum()
    avg_days_to_close = ao_data['Days_to_Close'].mean()

    # Base suggestion templates
    suggestion_templates = [
        "Based on your current metrics, focus on addressing the {critical_high_count} high and critical vulnerabilities.",
        "You have {old_vulns_count} vulnerabilities open for more than 30 days. Consider prioritizing these for immediate remediation.",
        "Your average time to close vulnerabilities is {avg_days_to_close:.1f} days. The department average is {dept_avg:.1f} days.",
        "There are {high_risk_count} high-risk items (CVSS or Risk Score > 7) that require urgent attention.",
        "Consider reviewing your patch management process to improve remediation time.",
        "Implementing automated scanning could help identify vulnerabilities earlier.",
        "Regular security training for your team could reduce vulnerability introduction rate.",
        "Establishing a vulnerability prioritization framework may help focus remediation efforts."
    ]

    # Create context from the AO's data
    ao_context = f"""
    Application Owner: {ao_id}
    Applications: {', '.join(ao_data['Application_Name'].unique())}
    Critical/High vulnerabilities: {critical_high_count}
    Vulnerabilities > 30 days: {old_vulns_count}
    Average closure time: {avg_days_to_close:.1f} days
    High risk items: {high_risk_count}
    """

    # Format suggestion templates with actual data
    dept_avg = df['Days_to_Close'].mean()
    formatted_suggestions = []
    for template in suggestion_templates:
        try:
            formatted = template.format(
                critical_high_count=critical_high_count,
                old_vulns_count=old_vulns_count,
                avg_days_to_close=avg_days_to_close,
                dept_avg=dept_avg,
                high_risk_count=high_risk_count
            )
            formatted_suggestions.append(formatted)
        except:
            formatted_suggestions.append(template)

    # Encode the context
    if model:
        context_embedding = model.encode([ao_context])[0]
        suggestion_embeddings = model.encode(formatted_suggestions)

        # Calculate similarity
        similarities = cosine_similarity(
            [context_embedding], suggestion_embeddings)[0]

        # Get top 3 most relevant suggestions
        top_indices = similarities.argsort()[-3:][::-1]
        top_suggestions = [formatted_suggestions[i] for i in top_indices]

        return "\n\n".join(top_suggestions)
    else:
        # Fallback if model isn't loaded
        return "\n\n".join(formatted_suggestions[:3])


# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Cybersecurity KPI Dashboard for Application Owners"

# Define the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Cybersecurity KPI Dashboard",
                    className="text-primary my-4"),
            html.H4("Application Owner Performance Monitoring",
                    className="text-secondary mb-4")
        ], width=8),
        dbc.Col([
            html.Div([
                html.H5(f"Date: {current_date.strftime('%B %d, %Y')}"),
                html.P("Last updated: Today", className="text-muted")
            ], className="text-right pt-4")
        ], width=4)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filter Controls"),
                dbc.CardBody([
                    html.P("Select Application Owner:"),
                    dcc.Dropdown(
                        id='ao-dropdown',
                        options=[{'label': f"{name} ({id})", 'value': id}
                                 for id, name in df[['Application_Owner_ID', 'Application_Owner_Name']].drop_duplicates().values],
                        value=df['Application_Owner_ID'].iloc[0],
                        clearable=False
                    ),
                    html.Div(className="mb-3"),
                    html.P("Select Department:"),
                    dcc.Dropdown(
                        id='dept-dropdown',
                        options=[{'label': dept, 'value': dept}
                                 for dept in sorted(df['Dept_Name'].unique())],
                        value=df['Dept_Name'].unique()[0],
                        clearable=False
                    ),
                    html.Div(className="mb-3"),
                    html.P("Filter by Status:"),
                    dcc.Checklist(
                        id='status-checklist',
                        options=[{'label': status, 'value': status}
                                 for status in sorted(df['Status'].unique())],
                        value=df['Status'].unique().tolist(),
                        inline=True
                    ),
                    html.Div(className="mb-3"),
                    dbc.Button("Apply Filters", id="apply-filters",
                               color="primary", className="mt-2")
                ])
            ], className="mb-4"),

            dbc.Card([
                dbc.CardHeader("Smart Suggestions"),
                dbc.CardBody([
                    html.Div(id="suggestion-content",
                             className="suggestion-box"),
                    dbc.Button(
                        "Refresh Suggestions", id="refresh-suggestions", color="info", className="mt-2")
                ])
            ], className="mb-4"),

            dbc.Card([
                dbc.CardHeader("Export Options"),
                dbc.CardBody([
                    dbc.Button("Export as PDF", id="export-pdf",
                               color="success", className="me-2"),
                    dbc.Button("Export as CSV", id="export-csv",
                               color="success", className="me-2"),
                    dcc.Download(id="download-csv")
                ])
            ])
        ], width=3),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            "Critical & High Severity Vulnerabilities"),
                        dbc.CardBody([
                            dcc.Graph(id='severity-chart',
                                      style={'height': '300px'})
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Vulnerabilities by Status"),
                        dbc.CardBody([
                            dcc.Graph(id='status-chart',
                                      style={'height': '300px'})
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Risk Score Distribution"),
                        dbc.CardBody([
                            dcc.Graph(id='risk-score-chart',
                                      style={'height': '300px'})
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Days to Close by Severity"),
                        dbc.CardBody([
                            dcc.Graph(id='days-to-close-chart',
                                      style={'height': '300px'})
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),

            dbc.Card([
                dbc.CardHeader("Urgent Attention Required"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='urgent-table',
                        columns=[
                            {'name': 'Application', 'id': 'Application_Name'},
                            {'name': 'Asset', 'id': 'Asset_Name'},
                            {'name': 'Vulnerability',
                                'id': 'Vulnerability_Description'},
                            {'name': 'Severity', 'id': 'Vulnerability_Severity'},
                            {'name': 'CVSS Score', 'id': 'CVSS_Score'},
                            {'name': 'Risk Score', 'id': 'Risk_Score'},
                            {'name': 'Days Open', 'id': 'Days_Open'},
                            {'name': 'Status', 'id': 'Status'}
                        ],
                        style_cell={
                            'textAlign': 'left',
                            'padding': '8px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                        },
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'white',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{Days_Open} > 30 && {Vulnerability_Severity} contains "Critical"'},
                                'backgroundColor': 'rgba(255, 0, 0, 0.2)',
                                'color': 'red'
                            },
                            {
                                'if': {'filter_query': '{Days_Open} > 30 && {Vulnerability_Severity} contains "High"'},
                                'backgroundColor': 'rgba(255, 165, 0, 0.2)',
                                'color': 'orange'
                            },
                            {
                                'if': {'filter_query': '{CVSS_Score} > 7 || {Risk_Score} > 7'},
                                'backgroundColor': 'rgba(255, 255, 0, 0.2)',
                                'fontWeight': 'bold'
                            }
                        ],
                        page_size=5,
                        sort_action='native',
                        filter_action='native',
                    )
                ])
            ], className="mb-4"),

            dbc.Card([
                dbc.CardHeader("Application Owner Performance Panel"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div(id="ao-performance-metrics")
                        ], width=12)
                    ])
                ])
            ])
        ], width=9)
    ])
], fluid=True)

# Callback for filtering and updating all charts


@app.callback(
    [Output('severity-chart', 'figure'),
     Output('status-chart', 'figure'),
     Output('risk-score-chart', 'figure'),
     Output('days-to-close-chart', 'figure'),
     Output('urgent-table', 'data'),
     Output('ao-performance-metrics', 'children'),
     Output('suggestion-content', 'children')],
    [Input('apply-filters', 'n_clicks'),
     Input('refresh-suggestions', 'n_clicks')],
    [State('ao-dropdown', 'value'),
     State('dept-dropdown', 'value'),
     State('status-checklist', 'value')]
)
def update_charts(n_clicks, refresh_clicks, ao_id, dept_name, status_values):
    # Filter data based on selections
    filtered_df = df.copy()

    if ao_id:
        filtered_df = filtered_df[filtered_df['Application_Owner_ID'] == ao_id]

    if dept_name:
        filtered_df = filtered_df[filtered_df['Dept_Name'] == dept_name]

    if status_values and len(status_values) > 0:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_values)]

    # If no data after filtering
    if len(filtered_df) == 0:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No data available for the selected filters",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[
                {
                    "text": "No matching data found",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20}
                }
            ]
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, [], [], "No data available for the selected filters"

    # 1. Severity Chart
    severity_counts = filtered_df['Vulnerability_Severity'].value_counts(
    ).reset_index()
    severity_counts.columns = ['Severity', 'Count']
    severity_order = ['Critical', 'High', 'Medium', 'Low']
    severity_counts['Severity'] = pd.Categorical(
        severity_counts['Severity'], categories=severity_order, ordered=True)
    severity_counts = severity_counts.sort_values('Severity')

    severity_fig = px.bar(
        severity_counts,
        x='Severity',
        y='Count',
        color='Severity',
        color_discrete_map={
            'Critical': 'red',
            'High': 'orange',
            'Medium': 'yellow',
            'Low': 'green'
        },
        title='Vulnerabilities by Severity'
    )
    severity_fig.update_layout(xaxis_title='Severity', yaxis_title='Count')

    # 2. Status Chart
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    status_fig = px.pie(
        status_counts,
        names='Status',
        values='Count',
        color='Status',
        color_discrete_map={
            'Open': 'red',
            'In Progress': 'orange',
            'Closed': 'green',
            'Exception': 'grey'
        },
        title='Vulnerabilities by Status'
    )

    # 3. Risk Score Chart
    risk_score_fig = px.histogram(
        filtered_df,
        x='Risk_Score',
        color_discrete_sequence=['#636EFA'],
        title='Risk Score Distribution',
        nbins=20
    )
    risk_score_fig.add_vline(
        x=7, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
    risk_score_fig.update_layout(xaxis_title='Risk Score', yaxis_title='Count')

    # 4. Days to Close Chart
    days_by_severity = filtered_df.groupby('Vulnerability_Severity')[
        'Days_to_Close'].mean().reset_index()
    days_by_severity['Vulnerability_Severity'] = pd.Categorical(
        days_by_severity['Vulnerability_Severity'],
        categories=severity_order,
        ordered=True
    )
    days_by_severity = days_by_severity.sort_values('Vulnerability_Severity')

    days_fig = px.bar(
        days_by_severity,
        x='Vulnerability_Severity',
        y='Days_to_Close',
        color='Vulnerability_Severity',
        color_discrete_map={
            'Critical': 'red',
            'High': 'orange',
            'Medium': 'yellow',
            'Low': 'green'
        },
        title='Average Days to Close by Severity'
    )
    days_fig.update_layout(xaxis_title='Severity', yaxis_title='Days')

    # 5. Urgent Table
    urgent_vulns = filtered_df[
        (filtered_df['Is_Critical_High_Over_30']) |
        (filtered_df['Is_High_Risk'])
    ]
    urgent_data = urgent_vulns.to_dict('records')

    # 6. AO Performance Metrics
    if ao_id:
        ao_name = df[df['Application_Owner_ID'] ==
                     ao_id]['Application_Owner_Name'].iloc[0]
        ao_apps = filtered_df['Application_Name'].nunique()
        ao_assets = filtered_df['Asset_Name'].nunique()

        # Calculate metrics
        total_vulns = len(filtered_df)
        open_vulns = len(filtered_df[filtered_df['Status'] == 'Open'])
        high_critical = len(filtered_df[filtered_df['Is_Critical_High']])
        avg_days = filtered_df['Days_to_Close'].mean()
        high_risk = len(filtered_df[filtered_df['Is_High_Risk']])

        # Create performance gauge chart
        ao_avg_risk = filtered_df['Risk_Score'].mean()
        all_avg_risk = df['Risk_Score'].mean()

        performance_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ao_avg_risk,
            delta={'reference': all_avg_risk, 'increasing': {
                'color': 'red'}, 'decreasing': {'color': 'green'}},
            gauge={
                'axis': {'range': [0, 10], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 3], 'color': 'green'},
                    {'range': [3, 7], 'color': 'yellow'},
                    {'range': [7, 10], 'color': 'red'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 7
                }
            },
            title={'text': "Average Risk Score (vs Overall Avg)"}
        ))

        performance_gauge.update_layout(height=250)

        # Create the performance metrics panel
        performance_metrics = [
            dbc.Row([
                dbc.Col([
                    html.H4(f"{ao_name} ({ao_id})"),
                    html.P(
                        f"Managing {ao_apps} Applications across {ao_assets} Assets")
                ], width=6),
                dbc.Col([
                    dcc.Graph(figure=performance_gauge,
                              config={'displayModeBar': False})
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{total_vulns}"),
                            html.P("Total Vulnerabilities")
                        ], className="text-center")
                    ])
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{open_vulns}"),
                            html.P("Open Vulnerabilities")
                        ], className="text-center bg-warning text-white" if open_vulns > 0 else "text-center")
                    ])
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{high_critical}"),
                            html.P("Critical/High")
                        ], className="text-center bg-danger text-white" if high_critical > 0 else "text-center")
                    ])
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{avg_days:.1f}"),
                            html.P("Avg Days to Close")
                        ], className="text-center")
                    ])
                ])
            ])
        ]
    else:
        performance_metrics = [
            html.P("Select an Application Owner to see performance metrics")]

    # 7. Generate suggestions
    suggestions = generate_suggestions(ao_id)
    suggestion_content = html.Div([
        html.P("Smart Suggestions for Improvement:"),
        html.Div([html.P(s) for s in suggestions.split('\n\n')])
    ])

    return severity_fig, status_fig, risk_score_fig, days_fig, urgent_data, performance_metrics, suggestion_content

# Callback for CSV export


@app.callback(
    Output("download-csv", "data"),
    Input("export-csv", "n_clicks"),
    [State('ao-dropdown', 'value'),
     State('dept-dropdown', 'value'),
     State('status-checklist', 'value')],
    prevent_initial_call=True
)
def generate_csv(n_clicks, ao_id, dept_name, status_values):
    if n_clicks is None:
        return dash.no_update

    # Filter data based on selections
    filtered_df = df.copy()

    if ao_id:
        filtered_df = filtered_df[filtered_df['Application_Owner_ID'] == ao_id]

    if dept_name:
        filtered_df = filtered_df[filtered_df['Dept_Name'] == dept_name]

    if status_values and len(status_values) > 0:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_values)]

    return dcc.send_data_frame(filtered_df.to_csv, "cybersecurity_kpi_export.csv")


# Add custom CSS for better styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .card {
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .card-header {
                background-color: #343a40;
                color: white;
                border-radius: 10px 10px 0 0 !important;
                padding: 12px 20px;
                font-weight: bold;
            }
            .suggestion-box {
                background-color: #f8f9fa;
                border-left: 4px solid #17a2b8;
                padding: 15px;
                border-radius: 4px;
            }
            .suggestion-box p {
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the server
if __name__ == '__main__':
    app.run(debug=True, port=8050)
