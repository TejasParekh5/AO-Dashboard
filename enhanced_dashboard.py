import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback, clientside_callback
import dash_bootstrap_components as dbc
import datetime
import base64
import io
import requests
import json
from dash.exceptions import PreventUpdate
import urllib.parse

# Set the current date
current_date = datetime.datetime(2025, 6, 17)

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

# Calculate AO-Application-Department relationship mapping
ao_app_dept = df[['Application_Owner_ID', 'Application_Owner_Name',
                  'Application_ID', 'Application_Name', 'Dept_Name']].drop_duplicates()

# Calculate trends (group by detection date)
df['Detection_Month'] = pd.to_datetime(
    df['First_Detected_Date']).dt.strftime('%Y-%m')
monthly_trends = df.groupby(['Detection_Month', 'Application_Owner_ID'])[
    'Risk_Score'].mean().reset_index()
monthly_trends = monthly_trends.sort_values('Detection_Month')

# Create a special indicator for CVSS+Risk urgency
df['Urgency_Level'] = 'Normal'
df.loc[df['Is_Critical_High_Over_30'], 'Urgency_Level'] = 'Urgent'
df.loc[df['Is_High_Risk'] & ~df['Is_Critical_High_Over_30'],
       'Urgency_Level'] = 'High'

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True)
app.title = "Cybersecurity KPI Dashboard for Application Owners"

# Define colors for the dashboard
colors = {
    'Critical': '#dc3545',  # Red
    'High': '#fd7e14',      # Orange
    'Medium': '#ffc107',    # Yellow
    'Low': '#28a745',       # Green
    'Open': '#dc3545',      # Red
    'In Progress': '#fd7e14',  # Orange
    'Closed': '#28a745',    # Green
    'Exception': '#6c757d',  # Gray
    'Urgent': '#dc3545',    # Red
    'High Priority': '#fd7e14',  # Orange
    'Normal': '#28a745',    # Green
    'background': '#f8f9fa',
    'text': '#343a40'
}

# Define reusable components


def create_kpi_card(title, value, suffix="", color="#343a40", icon=None, delta=None, delta_color=None):
    card_content = [
        dbc.CardHeader(title),
        dbc.CardBody([
            html.Div([
                html.I(className=icon, style={
                       "fontSize": "2rem", "marginRight": "10px"}) if icon else None,
                html.H2(f"{value}{suffix}", style={"color": color,
                        "fontWeight": "bold", "display": "inline-block"})
            ], style={"display": "flex", "alignItems": "center"}),
            html.P(delta, style={"color": delta_color}) if delta else None
        ])
    ]
    return dbc.Card(card_content, className="h-100 shadow-sm")


# Navigation bar
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.I(className="fas fa-shield-alt me-2",
                        style={"fontSize": "1.5rem"})),
                dbc.Col(dbc.NavbarBrand(
                    "Cybersecurity KPI Dashboard", className="ms-2")),
            ],
                align="center",
            ),
            href="#",
            style={"textDecoration": "none"},
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="#")),
                dbc.NavItem(dbc.NavLink(
                    "AO Performance", href="#ao-performance")),
                dbc.NavItem(dbc.NavLink(
                    "Relationships", href="#relationships")),
                dbc.NavItem(dbc.NavLink(
                    "Urgent Issues", href="#urgent-issues")),
                dbc.NavItem(dbc.NavLink(
                    f"Date: {current_date.strftime('%B %d, %Y')}")),
            ],
                className="ms-auto",
                navbar=True),
            id="navbar-collapse",
            navbar=True,
        ),
    ]),
    color="dark",
    dark=True,
    className="mb-4",
)

# Filter panel
filter_panel = dbc.Card([
    dbc.CardHeader("Filter Controls",
                   className="d-flex justify-content-between align-items-center"),
    dbc.CardBody([
        html.P("Select Application Owner(s):"),
        dcc.Dropdown(
            id='ao-dropdown',
            options=[{'label': f"{name} ({id})", 'value': id}
                     for id, name in df[['Application_Owner_ID', 'Application_Owner_Name']].drop_duplicates().values],
            value=[df['Application_Owner_ID'].iloc[0]],
            multi=True,
            clearable=False
        ),
        html.Div(className="mb-3"),
        html.P("Department:"),
        dcc.Dropdown(
            id='dept-dropdown',
            options=[{'label': dept, 'value': dept}
                     for dept in sorted(df['Dept_Name'].unique())],
            multi=True,
            placeholder="Departments will auto-populate based on AO selection"
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
                   color="primary", className="w-100")
    ])
], className="mb-4 shadow")

# Smart suggestions panel
suggestions_panel = dbc.Card([
    dbc.CardHeader([
        html.Span("🧠 Smart Suggestions", className="me-2"),
        dbc.Badge("AI Powered", color="info", className="ms-2"),
    ], className="d-flex justify-content-between align-items-center"),
    dbc.CardBody([
        html.Div(id="suggestion-content", className="suggestion-box"),
        dbc.Button("Refresh Suggestions", id="refresh-suggestions",
                   color="info", className="w-100 mt-3")
    ])
], className="mb-4 shadow")

# Export panel
export_panel = dbc.Card([
    dbc.CardHeader(
        "Export Options", className="d-flex justify-content-between align-items-center"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Button("Export as CSV", id="export-csv",
                           color="success", className="w-100 mb-2"),
                dcc.Download(id="download-csv")
            ], width=6),
            dbc.Col([
                dbc.Button("Export as PDF", id="export-pdf",
                           color="danger", className="w-100 mb-2"),
                dcc.Download(id="download-pdf")
            ], width=6)
        ])
    ])
], className="mb-4 shadow")

# Define the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container([
        dbc.Row([
            # Left sidebar with filters and tools
            dbc.Col([
                filter_panel,
                suggestions_panel,
                export_panel
            ], width=3),

            # Main content area
            dbc.Col([
                # Top KPI cards row
                dbc.Row([
                    dbc.Col(html.Div(id="kpi-cards"), width=12),
                ], className="mb-4"),

                # Charts row 1
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                "Vulnerability Severity Distribution"),
                            dbc.CardBody([
                                dcc.Graph(id='severity-chart',
                                          config={'displayModeBar': False})
                            ])
                        ], className="h-100 shadow")
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Status Breakdown"),
                            dbc.CardBody([
                                dcc.Graph(id='status-chart',
                                          config={'displayModeBar': False})
                            ])
                        ], className="h-100 shadow")
                    ], width=6)
                ], className="mb-4"),

                # Charts row 2
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Risk Score Distribution"),
                            dbc.CardBody([
                                dcc.Graph(id='risk-score-chart',
                                          config={'displayModeBar': False})
                            ])
                        ], className="h-100 shadow")
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Days to Close by Severity"),
                            dbc.CardBody([
                                dcc.Graph(id='days-to-close-chart',
                                          config={'displayModeBar': False})
                            ])
                        ], className="h-100 shadow")
                    ], width=6)
                ], className="mb-4"),

                # Urgent Issues table
                dbc.Row(id="urgent-issues", children=[
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.Span(
                                    "🚨 Urgent Attention Required", className="me-2"),
                                dbc.Badge("High Priority",
                                          color="danger", className="ms-2"),
                            ], className="d-flex justify-content-between align-items-center"),
                            dbc.CardBody([
                                dash_table.DataTable(
                                    id='urgent-table',
                                    columns=[
                                        {'name': 'Application Owner',
                                            'id': 'Application_Owner_Name'},
                                        {'name': 'Application',
                                            'id': 'Application_Name'},
                                        {'name': 'Vulnerability',
                                            'id': 'Vulnerability_Description'},
                                        {'name': 'Severity',
                                            'id': 'Vulnerability_Severity'},
                                        {'name': 'CVSS Score', 'id': 'CVSS_Score'},
                                        {'name': 'Risk Score', 'id': 'Risk_Score'},
                                        {'name': 'Days Open', 'id': 'Days_Open'},
                                        {'name': 'Status', 'id': 'Status'},
                                        {'name': 'Priority', 'id': 'Priority'}
                                    ],
                                    style_cell={
                                        'textAlign': 'left',
                                        'padding': '8px',
                                        'overflow': 'hidden',
                                        'textOverflow': 'ellipsis',
                                        'maxWidth': 0,
                                    },
                                    style_header={
                                        'backgroundColor': colors['text'],
                                        'color': 'white',
                                        'fontWeight': 'bold'
                                    },
                                    style_data_conditional=[
                                        {
                                            'if': {'filter_query': '{Vulnerability_Severity} contains "Critical"'},
                                            'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                                            'color': colors['Critical']
                                        },
                                        {
                                            'if': {'filter_query': '{Vulnerability_Severity} contains "High"'},
                                            'backgroundColor': 'rgba(253, 126, 20, 0.1)',
                                            'color': colors['High']
                                        },
                                        {
                                            'if': {'filter_query': '{Days_Open} > 30'},
                                            'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {'filter_query': '{CVSS_Score} > 7 || {Risk_Score} > 7'},
                                            'backgroundColor': 'rgba(255, 193, 7, 0.1)',
                                            'fontWeight': 'bold'
                                        }
                                    ],
                                    page_size=5,
                                    sort_action='native',
                                    filter_action='native',
                                )
                            ])
                        ], className="mb-4 shadow")
                    ], width=12)
                ]),

                # AO Performance Panel
                dbc.Row(id="ao-performance", children=[
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.Span("📊 AO Performance Panel",
                                          className="me-2"),
                                dbc.Badge("Comparative Analysis",
                                          color="primary", className="ms-2"),
                            ], className="d-flex justify-content-between align-items-center"),
                            dbc.CardBody([
                                html.Div(id="ao-performance-content")
                            ])
                        ], className="mb-4 shadow")
                    ], width=12)
                ]),

                # Relationship Mapping
                dbc.Row(id="relationships", children=[
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.Span("🔄 Relationship Mapping",
                                          className="me-2"),
                                dbc.Badge("Hierarchical View",
                                          color="secondary", className="ms-2"),
                            ], className="d-flex justify-content-between align-items-center"),
                            dbc.CardBody([
                                dbc.Tabs([
                                    dbc.Tab([
                                        html.P("This visualization shows the hierarchical relationship between Application Owners, Applications, and Departments.",
                                               className="text-muted mt-2"),
                                        dcc.Graph(id='hierarchy-chart',
                                                  config={'displayModeBar': False})
                                    ], label="AO → Apps → Department"),
                                    dbc.Tab([
                                        html.P("This visualization shows the relationship between vulnerabilities, assets, and risk clusters.",
                                               className="text-muted mt-2"),
                                        dcc.Graph(id='risk-cluster-chart',
                                                  config={'displayModeBar': False})
                                    ], label="Vuln → Asset → Risk"),
                                    dbc.Tab([
                                        html.P("This heatmap shows risk concentration by application and severity.",
                                               className="text-muted mt-2"),
                                        dcc.Graph(
                                            id='risk-heatmap', config={'displayModeBar': False})
                                    ], label="Risk Concentration")
                                ])
                            ])
                        ], className="mb-4 shadow")
                    ], width=12)
                ])
            ], width=9)
        ])
    ], fluid=True),

    # Footer
    dbc.Container([
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.P("Cybersecurity KPI Dashboard © 2025",
                       className="text-muted")
            ], width=6),
            dbc.Col([
                html.P("Last updated: June 16, 2025",
                       className="text-muted text-end")
            ], width=6)
        ])
    ], fluid=True)
])

# Callback to update department dropdown based on AO selection


@app.callback(
    Output('dept-dropdown', 'options'),
    Output('dept-dropdown', 'value'),
    Input('ao-dropdown', 'value')
)
def update_dept_dropdown(selected_aos):
    if not selected_aos:
        raise PreventUpdate

    # Filter to get departments related to selected AOs
    filtered_depts = ao_app_dept[ao_app_dept['Application_Owner_ID'].isin(
        selected_aos)]['Dept_Name'].unique()
    dept_options = [{'label': dept, 'value': dept}
                    for dept in sorted(filtered_depts)]

    # Set all related departments as selected by default
    return dept_options, list(filtered_depts)

# Callback for filtering and updating all components


@app.callback(
    [Output('kpi-cards', 'children'),
     Output('severity-chart', 'figure'),
     Output('status-chart', 'figure'),
     Output('risk-score-chart', 'figure'),
     Output('days-to-close-chart', 'figure'),
     Output('urgent-table', 'data'),
     Output('ao-performance-content', 'children'),
     Output('hierarchy-chart', 'figure'),
     Output('risk-cluster-chart', 'figure'),
     Output('risk-heatmap', 'figure')],
    [Input('apply-filters', 'n_clicks')],
    [State('ao-dropdown', 'value'),
     State('dept-dropdown', 'value'),
     State('status-checklist', 'value')]
)
def update_dashboard(n_clicks, ao_ids, dept_names, status_values):
    # Filter data based on selections
    filtered_df = df.copy()

    if ao_ids and len(ao_ids) > 0:
        filtered_df = filtered_df[filtered_df['Application_Owner_ID'].isin(
            ao_ids)]

    if dept_names and len(dept_names) > 0:
        filtered_df = filtered_df[filtered_df['Dept_Name'].isin(dept_names)]

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
        return [], empty_fig, empty_fig, empty_fig, empty_fig, [], html.P("No data available"), empty_fig, empty_fig, empty_fig

    # 1. KPI Cards
    total_vulns = len(filtered_df)
    open_vulns = len(filtered_df[filtered_df['Status'] == 'Open'])
    open_pct = (open_vulns / total_vulns * 100) if total_vulns > 0 else 0
    high_critical = len(filtered_df[filtered_df['Is_Critical_High']])
    high_critical_pct = (high_critical / total_vulns *
                         100) if total_vulns > 0 else 0
    avg_days = filtered_df['Days_to_Close'].mean()
    avg_cvss = filtered_df['CVSS_Score'].mean()
    avg_risk = filtered_df['Risk_Score'].mean()

    kpi_cards = [
        dbc.Row([
            dbc.Col([
                create_kpi_card(
                    "Total Vulnerabilities",
                    total_vulns,
                    icon="fas fa-shield-virus"
                )
            ], width=4),
            dbc.Col([
                create_kpi_card(
                    "Open vs Closed",
                    f"{open_pct:.1f}%",
                    icon="fas fa-lock-open",
                    color=colors['Open'] if open_pct > 50 else colors['Closed'],
                    delta=f"{open_vulns} open, {total_vulns - open_vulns} closed"
                )
            ], width=4),
            dbc.Col([
                create_kpi_card(
                    "Critical/High Issues",
                    high_critical,
                    icon="fas fa-exclamation-triangle",
                    color=colors['Critical'] if high_critical > 0 else colors['Low']
                )
            ], width=4)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                create_kpi_card(
                    "Avg Days to Close",
                    f"{avg_days:.1f}",
                    "days",
                    icon="fas fa-calendar-check",
                    color=colors['High'] if avg_days > 30 else colors['Low']
                )
            ], width=4),
            dbc.Col([
                create_kpi_card(
                    "Avg CVSS Score",
                    f"{avg_cvss:.1f}",
                    icon="fas fa-chart-line",
                    color=colors['Critical'] if avg_cvss > 7 else (
                        colors['High'] if avg_cvss > 5 else colors['Low'])
                )
            ], width=4),
            dbc.Col([
                create_kpi_card(
                    "Avg Risk Score",
                    f"{avg_risk:.1f}",
                    icon="fas fa-tachometer-alt",
                    color=colors['Critical'] if avg_risk > 7 else (
                        colors['High'] if avg_risk > 5 else colors['Low'])
                )
            ], width=4)
        ])
    ]

    # 2. Severity Chart
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
            'Critical': colors['Critical'],
            'High': colors['High'],
            'Medium': colors['Medium'],
            'Low': colors['Low']
        },
        text='Count'
    )
    severity_fig.update_layout(
        xaxis_title='Severity',
        yaxis_title='Count',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font={'color': colors['text']},
        margin=dict(l=40, r=40, t=10, b=40),
    )
    severity_fig.update_traces(textposition='outside')

    # 3. Status Chart
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    status_fig = px.pie(
        status_counts,
        names='Status',
        values='Count',
        color='Status',
        color_discrete_map={
            'Open': colors['Open'],
            'In Progress': colors['In Progress'],
            'Closed': colors['Closed'],
            'Exception': colors['Exception']
        },
        hole=0.4
    )
    status_fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font={'color': colors['text']},
        margin=dict(l=40, r=40, t=10, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    # 4. Risk Score Chart
    risk_score_fig = px.histogram(
        filtered_df,
        x='Risk_Score',
        color_discrete_sequence=['#636EFA'],
        nbins=20
    )
    risk_score_fig.add_vline(
        x=7,
        line_dash="dash",
        line_color=colors['Critical'],
        annotation_text="High Risk Threshold",
        annotation_position="top right"
    )
    risk_score_fig.update_layout(
        xaxis_title='Risk Score',
        yaxis_title='Count',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font={'color': colors['text']},
        margin=dict(l=40, r=40, t=10, b=40),
    )

    # 5. Days to Close Chart
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
            'Critical': colors['Critical'],
            'High': colors['High'],
            'Medium': colors['Medium'],
            'Low': colors['Low']
        },
        text_auto='.1f'
    )
    days_fig.update_layout(
        xaxis_title='Severity',
        yaxis_title='Average Days to Close',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font={'color': colors['text']},
        margin=dict(l=40, r=40, t=10, b=40),
    )
    days_fig.add_hline(
        y=30,
        line_dash="dash",
        line_color=colors['Critical'],
        annotation_text="30 Day Threshold",
        annotation_position="top right"
    )
    days_fig.update_traces(textposition='outside')

    # 6. Urgent Table
    urgent_vulns = filtered_df[
        (filtered_df['Is_Critical_High_Over_30']) |
        (filtered_df['Is_High_Risk'])
    ]
    urgent_data = urgent_vulns.to_dict('records')

    # 7. AO Performance Panel
    if ao_ids and len(ao_ids) > 0:
        # Risk trend over time chart
        ao_trends = monthly_trends[monthly_trends['Application_Owner_ID'].isin(
            ao_ids)]

        # Generate a line for each AO
        risk_trend_fig = go.Figure()

        for ao_id in ao_ids:
            ao_name = df[df['Application_Owner_ID'] ==
                         ao_id]['Application_Owner_Name'].iloc[0]
            ao_data = ao_trends[ao_trends['Application_Owner_ID'] == ao_id]

            if not ao_data.empty:
                risk_trend_fig.add_trace(go.Scatter(
                    x=ao_data['Detection_Month'],
                    y=ao_data['Risk_Score'],
                    mode='lines+markers',
                    name=f"{ao_name} ({ao_id})"
                ))

        # Add overall average line
        overall_trend = df.groupby('Detection_Month')[
            'Risk_Score'].mean().reset_index()
        risk_trend_fig.add_trace(go.Scatter(
            x=overall_trend['Detection_Month'],
            y=overall_trend['Risk_Score'],
            mode='lines',
            line=dict(dash='dash', color='black'),
            name='Organization Average'
        ))

        risk_trend_fig.update_layout(
            title="Risk Score Trend Over Time",
            xaxis_title="Month",
            yaxis_title="Average Risk Score",
            legend_title="Application Owner",
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font={'color': colors['text']},
            margin=dict(l=40, r=40, t=40, b=40),
        )

        # Create AO comparison table
        ao_comparison = []
        all_aos_avg = {
            'cvss': df['CVSS_Score'].mean(),
            'risk': df['Risk_Score'].mean(),
            'days': df['Days_to_Close'].mean(),
            'high_crit': df['Is_Critical_High'].mean() * 100,
            'open': len(df[df['Status'] == 'Open']) / len(df) * 100
        }

        for ao_id in ao_ids:
            ao_data = df[df['Application_Owner_ID'] == ao_id]
            ao_name = ao_data['Application_Owner_Name'].iloc[0]

            ao_metrics = {
                'id': ao_id,
                'name': ao_name,
                'cvss': ao_data['CVSS_Score'].mean(),
                'risk': ao_data['Risk_Score'].mean(),
                'days': ao_data['Days_to_Close'].mean(),
                'high_crit': ao_data['Is_Critical_High'].mean() * 100,
                'open': len(ao_data[ao_data['Status'] == 'Open']) / len(ao_data) * 100 if len(ao_data) > 0 else 0
            }            # Calculate delta from organization average
            ao_metrics['cvss_delta'] = ao_metrics['cvss'] - all_aos_avg['cvss']
            ao_metrics['risk_delta'] = ao_metrics['risk'] - all_aos_avg['risk']
            ao_metrics['days_delta'] = ao_metrics['days'] - all_aos_avg['days']
            ao_metrics['high_crit_delta'] = ao_metrics['high_crit'] - \
                all_aos_avg['high_crit']
            ao_metrics['open_delta'] = ao_metrics['open'] - all_aos_avg['open']

            ao_comparison.append(ao_metrics)

        # Format percentage values in the data with % symbol
        for item in ao_comparison:
            # Add % symbol to high_crit and open fields for display
            item['high_crit_display'] = f"{item['high_crit']:.1f}%"
            item['open_display'] = f"{item['open']:.1f}%"

        # Generate comparison table
        comparison_table = dash_table.DataTable(
            id='ao-comparison-table',
            columns=[
                {'name': 'Application Owner', 'id': 'name'},
                {'name': 'Avg CVSS', 'id': 'cvss', 'type': 'numeric',
                    'format': {'specifier': '.2f'}},
                {'name': 'vs Org', 'id': 'cvss_delta',
                    'type': 'numeric', 'format': {'specifier': '+.2f'}},
                {'name': 'Avg Risk', 'id': 'risk', 'type': 'numeric',
                    'format': {'specifier': '.2f'}},
                {'name': 'vs Org', 'id': 'risk_delta',
                    'type': 'numeric', 'format': {'specifier': '+.2f'}},                {'name': 'Avg Days', 'id': 'days', 'type': 'numeric',
                                                                                         'format': {'specifier': '.1f'}},
                {'name': 'vs Org', 'id': 'days_delta',
                    'type': 'numeric', 'format': {'specifier': '+.1f'}},
                {'name': '% High/Crit', 'id': 'high_crit_display',
                    'type': 'text'},
                {'name': '% Open', 'id': 'open_display',
                    'type': 'text'}
            ],
            data=ao_comparison,
            style_cell={
                'textAlign': 'center',
                'padding': '8px',
                'minWidth': '80px'
            },
            style_header={
                'backgroundColor': colors['text'],
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{cvss_delta} > 0', 'column_id': 'cvss_delta'},
                    'color': colors['Critical']
                },
                {
                    'if': {'filter_query': '{cvss_delta} <= 0', 'column_id': 'cvss_delta'},
                    'color': colors['Low']
                },
                {
                    'if': {'filter_query': '{risk_delta} > 0', 'column_id': 'risk_delta'},
                    'color': colors['Critical']
                },
                {
                    'if': {'filter_query': '{risk_delta} <= 0', 'column_id': 'risk_delta'},
                    'color': colors['Low']
                },
                {
                    'if': {'filter_query': '{days_delta} > 0', 'column_id': 'days_delta'},
                    'color': colors['Critical']
                },
                {
                    'if': {'filter_query': '{days_delta} <= 0', 'column_id': 'days_delta'},
                    'color': colors['Low']
                }
            ]
        )

        # Create AO performance content
        ao_performance_content = [
            dbc.Row([
                dbc.Col([
                    html.H5("Performance Comparison", className="mb-3"),
                    comparison_table
                ], width=12)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=risk_trend_fig, config={
                              'displayModeBar': False})
                ], width=12)
            ])
        ]
    else:
        ao_performance_content = [
            html.P("Select an Application Owner to see performance metrics")]

    # 8. Hierarchical Relationship Chart (AO → Apps → Department)
    # Create nodes and links for the sankey diagram
    ao_app_dept_filtered = ao_app_dept.copy()
    if ao_ids and len(ao_ids) > 0:
        ao_app_dept_filtered = ao_app_dept_filtered[ao_app_dept_filtered['Application_Owner_ID'].isin(
            ao_ids)]
    if dept_names and len(dept_names) > 0:
        ao_app_dept_filtered = ao_app_dept_filtered[ao_app_dept_filtered['Dept_Name'].isin(
            dept_names)]

    # Create unique IDs for each node
    unique_aos = ao_app_dept_filtered[[
        'Application_Owner_ID', 'Application_Owner_Name']].drop_duplicates()
    unique_apps = ao_app_dept_filtered[[
        'Application_ID', 'Application_Name']].drop_duplicates()
    unique_depts = ao_app_dept_filtered['Dept_Name'].drop_duplicates(
    ).reset_index()

    # Create node labels
    ao_labels = [
        f"{row['Application_Owner_Name']} ({row['Application_Owner_ID']})" for _, row in unique_aos.iterrows()]
    app_labels = [
        f"{row['Application_Name']} ({row['Application_ID']})" for _, row in unique_apps.iterrows()]
    dept_labels = [dept for dept in unique_depts['Dept_Name']]

    all_labels = ao_labels + app_labels + dept_labels

    # Create links (AO -> App, App -> Dept)
    links_ao_app = []
    for _, row in ao_app_dept_filtered.iterrows():
        source_idx = ao_labels.index(
            f"{row['Application_Owner_Name']} ({row['Application_Owner_ID']})")
        target_idx = len(
            ao_labels) + app_labels.index(f"{row['Application_Name']} ({row['Application_ID']})")
        links_ao_app.append(
            {'source': source_idx, 'target': target_idx, 'value': 1})

    links_app_dept = []
    for _, row in ao_app_dept_filtered.iterrows():
        source_idx = len(
            ao_labels) + app_labels.index(f"{row['Application_Name']} ({row['Application_ID']})")
        target_idx = len(ao_labels) + len(app_labels) + \
            list(unique_depts['Dept_Name']).index(row['Dept_Name'])
        links_app_dept.append(
            {'source': source_idx, 'target': target_idx, 'value': 1})

    links = links_ao_app + links_app_dept

    # Create Sankey diagram
    hierarchy_fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=["blue"] * len(ao_labels) + ["green"] *
            len(app_labels) + ["red"] * len(dept_labels)
        ),
        link=dict(
            source=[link['source'] for link in links],
            target=[link['target'] for link in links],
            value=[link['value'] for link in links]
        )
    )])

    hierarchy_fig.update_layout(
        title_text="Application Owner → Application → Department Relationships",
        font=dict(size=10),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        margin=dict(l=20, r=20, t=50, b=20),
    )

    # 9. Risk Cluster Chart (Vuln → Asset → Risk)
    # Group vulnerabilities by asset and vulnerability severity
    asset_vuln_severity = filtered_df.groupby(
        ['Asset_Type', 'Vulnerability_Severity']).size().reset_index(name='count')

    # Create a bubble chart
    risk_cluster_fig = px.scatter(
        asset_vuln_severity,
        x="Asset_Type",
        y="Vulnerability_Severity",
        size="count",
        color="Vulnerability_Severity",
        color_discrete_map={
            'Critical': colors['Critical'],
            'High': colors['High'],
            'Medium': colors['Medium'],
            'Low': colors['Low']
        },
        hover_name="Asset_Type",
        text="count",
        size_max=60
    )

    risk_cluster_fig.update_layout(
        title="Vulnerability Concentration by Asset Type and Severity",
        xaxis_title="Asset Type",
        yaxis_title="Vulnerability Severity",
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font={'color': colors['text']},
        margin=dict(l=40, r=40, t=50, b=40),
    )

    # 10. Risk Concentration Heatmap
    # Create a pivot table of risk scores by application and severity
    risk_by_app_severity = pd.pivot_table(
        filtered_df,
        values='Risk_Score',
        index=['Application_Name'],
        columns=['Vulnerability_Severity'],
        aggfunc='mean',
        fill_value=0
    )

    # Reorder columns by severity
    if set(severity_order).issubset(set(risk_by_app_severity.columns)):
        risk_by_app_severity = risk_by_app_severity[severity_order]

    # Create heatmap
    risk_heatmap = px.imshow(
        risk_by_app_severity,
        labels=dict(x="Vulnerability Severity",
                    y="Application", color="Avg Risk Score"),
        x=risk_by_app_severity.columns,
        y=risk_by_app_severity.index,
        color_continuous_scale=[
            [0, colors['Low']],
            [0.33, colors['Medium']],
            [0.66, colors['High']],
            [1, colors['Critical']]
        ],
        text_auto='.1f'
    )

    risk_heatmap.update_layout(
        title="Risk Score Concentration by Application and Severity",
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font={'color': colors['text']},
        margin=dict(l=40, r=40, t=50, b=40),
    )

    return kpi_cards, severity_fig, status_fig, risk_score_fig, days_fig, urgent_data, ao_performance_content, hierarchy_fig, risk_cluster_fig, risk_heatmap

# Callback for suggestion content


@app.callback(
    Output("suggestion-content", "children"),
    [Input("refresh-suggestions", "n_clicks"),
     Input("ao-dropdown", "value")]
)
def update_suggestions(n_clicks, ao_ids):
    if not ao_ids or len(ao_ids) == 0:
        return html.P("Select an Application Owner to see suggestions")

    suggestions_content = []

    # Fetch suggestions from API for each AO
    for ao_id in ao_ids:
        try:
            # Try to connect to the suggestion API
            api_url = f"http://127.0.0.1:8000/suggestions/{ao_id}"
            # Add timeout to prevent hanging
            response = requests.get(api_url, timeout=5)

            if response.status_code == 200:
                # Successfully got suggestions from API
                data = response.json()
                ao_name = data['ao_name']

                # Create styled suggestion items
                suggestion_items = []
                for suggestion in data['suggestions']:
                    text = suggestion['text']
                    priority = suggestion['priority']

                    # Style based on priority
                    if priority == 'urgent':
                        suggestion_items.append(
                            html.Div([
                                html.P(text, className="mb-2")
                            ], className="alert alert-danger")
                        )
                    elif priority == 'medium':
                        suggestion_items.append(
                            html.Div([
                                html.P(text, className="mb-2")
                            ], className="alert alert-warning")
                        )
                    else:  # good
                        suggestion_items.append(
                            html.Div([
                                html.P(text, className="mb-2")
                            ], className="alert alert-success")
                        )

                suggestions_content.append(
                    html.Div([
                        html.H5(
                            f"Suggestions for {ao_name} ({ao_id})", className="mb-3"),
                        html.Div(suggestion_items)
                    ], className="mb-4")
                )
            else:
                # API request failed
                suggestions_content.append(
                    html.Div([
                        html.H5(f"Suggestions for {ao_id}", className="mb-3"),
                        html.Div([
                            html.P(f"Could not retrieve suggestions from API. Status code: {response.status_code}",
                                   className="text-danger"),
                            html.P(
                                "The suggestion service may not be running correctly."),
                            html.Div([
                                html.P("Start the suggestion API with either:"),
                                dbc.Card(
                                    dbc.CardBody([
                                        html.Code(
                                            "python suggestion_api.py  # For ML-based suggestions"),
                                        html.Br(),
                                        html.Code(
                                            "python simple_suggestion_api.py  # For rule-based suggestions")
                                    ]),
                                    className="bg-light mb-2"
                                )
                            ])
                        ], className="alert alert-warning")
                    ], className="mb-4")
                )
        except Exception as e:
            # Handle connection errors to API
            ao_name = df[df['Application_Owner_ID'] ==
                         ao_id]['Application_Owner_Name'].iloc[0] if ao_id in df['Application_Owner_ID'].values else ao_id

            # Check if it's a connection error
            error_msg = str(e)
            if "Connection" in error_msg or "connect" in error_msg or "ConnectTimeoutError" in error_msg or "ConnectionError" in error_msg:
                error_details = "The suggestion API service is not running."
                cmd_hint = "Start the suggestion API with either:"
                commands = [
                    "python suggestion_api.py  # For ML-based suggestions",
                    "python simple_suggestion_api.py  # For rule-based suggestions"
                ]
            else:
                error_details = f"Error: {error_msg}"
                cmd_hint = "Check the API logs for more details."
                commands = []

            suggestions_content.append(
                html.Div([
                    html.H5(
                        f"Suggestions for {ao_name} ({ao_id})", className="mb-3"),
                    html.Div([
                        html.P(error_details, className="text-danger"),
                        html.P(cmd_hint),
                        dbc.Card(
                            dbc.CardBody([
                                html.Code(cmd) for cmd in commands
                            ]),
                            className="bg-light mb-2"
                        ),
                        html.P([
                            "⚠️ ",
                            html.Strong("Important: "),
                            "You must start the suggestion API in a separate terminal window before refreshing suggestions."
                        ], className="mt-2")
                    ], className="alert alert-warning")
                ], className="mb-4")
            )

    return html.Div(suggestions_content)

    return html.Div(suggestions_content)

# Callback for CSV export


@app.callback(
    Output("download-csv", "data"),
    Input("export-csv", "n_clicks"),
    [State('ao-dropdown', 'value'),
     State('dept-dropdown', 'value'),
     State('status-checklist', 'value')],
    prevent_initial_call=True
)
def generate_csv(n_clicks, ao_ids, dept_names, status_values):
    if n_clicks is None:
        return dash.no_update

    # Filter data based on selections
    filtered_df = df.copy()

    if ao_ids and len(ao_ids) > 0:
        filtered_df = filtered_df[filtered_df['Application_Owner_ID'].isin(
            ao_ids)]

    if dept_names and len(dept_names) > 0:
        filtered_df = filtered_df[filtered_df['Dept_Name'].isin(dept_names)]

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
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .card {
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }
            .card:hover {
                box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
                transform: translateY(-2px);
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
                padding: 15px;
                border-radius: 4px;
            }
            .suggestion-box p {
                margin-bottom: 10px;
            }
            .alert {
                border-radius: 8px;
                padding: 12px 15px;
                margin-bottom: 10px;
            }
            .alert-danger {
                border-left: 4px solid #dc3545;
            }
            .alert-warning {
                border-left: 4px solid #ffc107;
            }
            .alert-success {
                border-left: 4px solid #28a745;
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
