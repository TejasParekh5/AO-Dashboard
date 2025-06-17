import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
import warnings
warnings.filterwarnings('ignore')

# Set the current date
current_date = datetime.datetime(2025, 6, 17)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the Excel file
excel_path = os.path.join(current_dir, 'Cybersecurity_KPI_Minimal.xlsx')

# Read the Excel file
print(f"🔄 Loading data from: {excel_path}")
df = pd.read_excel(excel_path)
print(f"✅ Loaded {len(df)} records successfully")

# Add some derived columns for analysis
df['Days_Open'] = np.where(pd.isna(df['Closure_Date']),
                           (current_date -
                            pd.to_datetime(df['First_Detected_Date'])).dt.days,
                           df['Days_to_Close'])

df['Is_Critical_High'] = df['Vulnerability_Severity'].isin(['Critical', 'High'])
df['Is_Over_30_Days'] = df['Days_Open'] > 30
df['Is_Critical_High_Over_30'] = df['Is_Critical_High'] & df['Is_Over_30_Days']
df['Is_High_Risk'] = (df['CVSS_Score'] > 7) | (df['Risk_Score'] > 7)

# Calculate AO-Application-Department relationship mapping
ao_app_dept = df[['Application_Owner_ID', 'Application_Owner_Name',
                  'Application_ID', 'Application_Name', 'Dept_Name']].drop_duplicates()

# Calculate trends (group by detection date)
df['Detection_Month'] = pd.to_datetime(df['First_Detected_Date']).dt.strftime('%Y-%m')
monthly_trends = df.groupby(['Detection_Month', 'Application_Owner_ID'])['Risk_Score'].mean().reset_index()
monthly_trends = monthly_trends.sort_values('Detection_Month')

# Create a special indicator for CVSS+Risk urgency
df['Urgency_Level'] = 'Normal'
df.loc[df['Is_Critical_High_Over_30'], 'Urgency_Level'] = 'Urgent'
df.loc[df['Is_High_Risk'] & ~df['Is_Critical_High_Over_30'], 'Urgency_Level'] = 'High'

# Initialize the Dash app with enhanced theme and assets
app = dash.Dash(__name__,
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP,
                    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
                    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
                    '/assets/css/dashboard.css'  # Our custom CSS
                ],
                external_scripts=[
                    '/assets/js/dashboard.js'  # Our custom JS
                ],
                suppress_callback_exceptions=True,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"},
                    {"name": "description", "content": "Advanced Cybersecurity KPI Dashboard"},
                    {"name": "author", "content": "Cybersecurity Team"}
                ])

app.title = "CyberSec Pro Dashboard - Advanced Analytics"

# Define enhanced color scheme
colors = {
    'Critical': '#dc2626',     # Red 600
    'High': '#ea580c',         # Orange 600  
    'Medium': '#d97706',       # Amber 600
    'Low': '#16a34a',          # Green 600
    'Open': '#dc2626',         # Red 600
    'In Progress': '#ea580c',  # Orange 600
    'Closed': '#16a34a',       # Green 600
    'Exception': '#6b7280',    # Gray 500
    'Urgent': '#dc2626',       # Red 600
    'High Priority': '#ea580c', # Orange 600
    'Normal': '#16a34a',       # Green 600
    'primary': '#0d47a1',      # Blue 900
    'secondary': '#1565c0',    # Blue 700
    'accent': '#42a5f5',       # Blue 400
    'background': '#f8fafc',   # Slate 50
    'surface': '#ffffff',      # White
    'text': '#1e293b',         # Slate 800
    'text_secondary': '#64748b', # Slate 500
    'success': '#16a34a',      # Green 600
    'warning': '#d97706',      # Amber 600
    'info': '#0ea5e9',         # Sky 500
    'danger': '#dc2626'        # Red 600
}

# Enhanced KPI card component
def create_enhanced_kpi_card(title, value, suffix="", color="#0d47a1", icon=None, delta=None, delta_color=None, trend_data=None):
    """Create an enhanced KPI card with animations and trends"""
    
    # Determine delta styling
    delta_style = {}
    delta_icon = ""
    if delta is not None:
        if delta > 0:
            delta_style = {"color": "#dc2626", "background": "rgba(220, 38, 38, 0.1)"}
            delta_icon = "fas fa-arrow-up"
        elif delta < 0:
            delta_style = {"color": "#16a34a", "background": "rgba(22, 163, 74, 0.1)"}
            delta_icon = "fas fa-arrow-down"
        else:
            delta_style = {"color": "#6b7280", "background": "rgba(107, 114, 128, 0.1)"}
            delta_icon = "fas fa-minus"
    
    # Create mini trend chart if data provided
    trend_chart = None
    if trend_data and len(trend_data) > 1:
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(
            y=trend_data,
            mode='lines',
            line=dict(color=color, width=2),
            fill='tonexty',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)'
        ))
        trend_fig.update_layout(
            height=60,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        trend_chart = dcc.Graph(figure=trend_fig, config={'displayModeBar': False}, style={'height': '60px'})

    card_content = [
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className=icon, style={"fontSize": "1.5rem", "color": color, "marginBottom": "0.5rem"}) if icon else None,
                        html.H6(title, className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "600", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                        html.H2(f"{value}{suffix}", className="mb-0", style={"color": color, "fontWeight": "800", "fontSize": "2.5rem", "lineHeight": "1"}),
                        html.Div([
                            html.I(className=delta_icon, style={"fontSize": "0.75rem", "marginRight": "0.25rem"}) if delta is not None else None,
                            html.Span(f"{abs(delta):.1f}%" if delta is not None else "", style={"fontSize": "0.75rem", "fontWeight": "600"})
                        ], style={**delta_style, "padding": "0.25rem 0.5rem", "borderRadius": "0.375rem", "display": "inline-flex", "alignItems": "center", "marginTop": "0.5rem"}) if delta is not None else None
                    ], style={"flex": "1"}),
                    html.Div([
                        trend_chart
                    ], style={"width": "80px"}) if trend_chart else None
                ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between"})
            ])
        ], style={"padding": "1.5rem"})
    ]
    
    return dbc.Card(card_content, className="h-100 shadow-sm border-0 kpi-card", style={"borderRadius": "1rem"})

# Enhanced navigation bar
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.I(className="fas fa-shield-halved", style={"fontSize": "1.75rem", "color": "white"})),
                dbc.Col(dbc.NavbarBrand("CyberSec Pro Dashboard", className="ms-2", style={"fontWeight": "700", "fontSize": "1.5rem"})),
            ], align="center", className="g-0"),
            href="/",
            style={"textDecoration": "none"},
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            dbc.Nav([                dbc.NavItem(dbc.NavLink([html.I(className="fas fa-home me-2"), "Dashboard"], href="/", style={"fontWeight": "500"})),
                dbc.NavItem(dbc.NavLink([html.I(className="fas fa-chart-line me-2"), "Analytics"], href="#analytics", style={"fontWeight": "500"})),
                dbc.NavItem(dbc.NavLink([html.I(className="fas fa-network-wired me-2"), "Relationships"], href="#relationships", style={"fontWeight": "500"})),
                dbc.NavItem(dbc.NavLink([html.I(className="fas fa-exclamation-triangle me-2"), "Urgent"], href="#urgent-issues", style={"fontWeight": "500"})),
                dbc.NavItem(dbc.NavLink([html.I(className="fas fa-calendar me-2"), current_date.strftime('%B %d, %Y')], disabled=True, style={"color": "rgba(255,255,255,0.7)"})),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True,
        ),
    ], fluid=True),
    color="primary",
    dark=True,
    className="mb-4 shadow-sm",
    style={"background": "linear-gradient(90deg, #0d47a1 0%, #1565c0 100%)"}
)

# Enhanced filter panel
filter_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-filter me-2"),
            html.Span("Smart Filters", style={"fontWeight": "600"})
        ])
    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white", "border": "none"}),
    dbc.CardBody([
        html.Div([
            html.Label([html.I(className="fas fa-user-tie me-2"), "Application Owner(s):"], className="form-label", style={"fontWeight": "600", "color": "#1e293b"}),
            dcc.Dropdown(
                id='ao-dropdown',
                options=[{'label': f"{name} ({id})", 'value': id}
                         for id, name in df[['Application_Owner_ID', 'Application_Owner_Name']].drop_duplicates().values],
                value=[df['Application_Owner_ID'].iloc[0]],
                multi=True,
                clearable=False,
                className="mb-3",
                style={"borderRadius": "0.5rem"}
            ),
        ]),
        html.Div([
            html.Label([html.I(className="fas fa-building me-2"), "Department:"], className="form-label", style={"fontWeight": "600", "color": "#1e293b"}),
            dcc.Dropdown(
                id='dept-dropdown',
                options=[{'label': dept, 'value': dept}
                         for dept in sorted(df['Dept_Name'].unique())],
                multi=True,
                placeholder="Auto-populated based on AO selection",
                className="mb-3",
                style={"borderRadius": "0.5rem"}
            ),
        ]),
        html.Div([
            html.Label([html.I(className="fas fa-tasks me-2"), "Status Filter:"], className="form-label", style={"fontWeight": "600", "color": "#1e293b"}),            dbc.Checklist(
                id='status-checklist',
                options=[{'label': status, 'value': status}
                         for status in sorted(df['Status'].unique())],
                value=list(df['Status'].unique()),
                inline=True,
                className="mb-3"
            ),
        ]),
        dbc.Button([html.I(className="fas fa-sync-alt me-2"), "Apply Filters"], 
                  id="apply-filters", color="primary", className="w-100",
                  style={"borderRadius": "0.5rem", "fontWeight": "600"})
    ], style={"padding": "1.5rem"})
], className="mb-4 shadow-sm border-0", style={"borderRadius": "1rem"})

# Enhanced suggestions panel
suggestions_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-brain me-2"),
            html.Span("AI Insights", style={"fontWeight": "600"}),
            dbc.Badge("Powered by ML", color="info", className="ms-2", style={"fontSize": "0.7rem"})
        ])
    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white", "border": "none"}),
    dbc.CardBody([
        html.Div(id="suggestion-content", className="suggestion-box", style={"minHeight": "200px"}),
        dbc.Button([html.I(className="fas fa-refresh me-2"), "Refresh Insights"], 
                  id="refresh-suggestions", color="info", className="w-100 mt-3",
                  style={"borderRadius": "0.5rem", "fontWeight": "600"})
    ], style={"padding": "1.5rem"})
], className="mb-4 shadow-sm border-0", style={"borderRadius": "1rem"})

# Enhanced export panel
export_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-download me-2"),
            html.Span("Export & Reports", style={"fontWeight": "600"})
        ])
    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white", "border": "none"}),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-file-csv me-2"), "Export CSV"], 
                          id="export-csv", color="success", className="w-100 mb-2",
                          style={"borderRadius": "0.5rem", "fontWeight": "600"}),
                dcc.Download(id="download-csv")
            ], width=6),
            dbc.Col([
                dbc.Button([html.I(className="fas fa-file-pdf me-2"), "Export PDF"], 
                          id="export-pdf", color="danger", className="w-100 mb-2",
                          style={"borderRadius": "0.5rem", "fontWeight": "600"}),
                dcc.Download(id="download-pdf")
            ], width=6)
        ])
    ], style={"padding": "1.5rem"})
], className="mb-4 shadow-sm border-0", style={"borderRadius": "1rem"})

# Enhanced chatbot layout (removed due to duplicate IDs - using ai_assistant_panel instead)

# Professional AI Assistant Panel
ai_assistant_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-robot", 
                  style={"fontSize": "1.2rem", "color": "#3182ce", "marginRight": "0.75rem"}),
            html.Span("AI Security Assistant", 
                     style={"fontWeight": "600", "fontSize": "1.1rem", "color": "#1a202c"})
        ], style={"display": "flex", "alignItems": "center"})
    ], style={
        "background": "linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)",
        "borderBottom": "1px solid #e2e8f0",
        "borderRadius": "0.75rem 0.75rem 0 0"
    }),
    dbc.CardBody([
        html.Div(id="chatbot-response", children=[], 
                style={
                    "minHeight": "200px", 
                    "maxHeight": "300px", 
                    "overflowY": "auto",
                    "padding": "1rem",
                    "background": "#f7fafc",
                    "borderRadius": "0.5rem",
                    "border": "1px solid #e2e8f0",
                    "marginBottom": "1rem",
                    "fontSize": "0.9rem",
                    "lineHeight": "1.5"
                }),
        dbc.InputGroup([
            dbc.Input(
                id="chatbot-input",
                placeholder="Ask about security insights, vulnerabilities, or recommendations...",
                type="text",
                style={
                    "borderRadius": "0.5rem 0 0 0.5rem",
                    "border": "1px solid #e2e8f0",
                    "fontSize": "0.9rem"
                }
            ),
            dbc.Button([
                html.I(className="fas fa-paper-plane")
            ], 
                id="chatbot-submit", 
                color="primary", 
                style={
                    "borderRadius": "0 0.5rem 0.5rem 0",
                    "background": "linear-gradient(135deg, #3182ce 0%, #2d3748 100%)",
                    "border": "none",
                    "width": "50px"
                }
            )
        ], size="sm"),
        html.Div([
            html.Small("💡 Try asking: 'What are my highest risk vulnerabilities?' or 'How can I improve security?'",
                      style={"color": "#718096", "fontSize": "0.75rem", "lineHeight": "1.4"})
        ], style={"marginTop": "0.5rem", "padding": "0.5rem", "background": "#edf2f7", "borderRadius": "0.375rem"})
    ], style={"padding": "1.25rem"})
], className="mb-4 shadow-sm border-0", 
  style={
      "borderRadius": "0.75rem",
      "border": "1px solid #e2e8f0",
      "background": "#ffffff"
  })


# Main application layout with enhanced structure
app.layout = html.Div([
    # Custom CSS and JavaScript
    html.Link(rel='stylesheet', href='/assets/css/dashboard.css'),
    html.Script(src='/assets/js/dashboard.js'),
    
    navbar,
    
    # Main dashboard content directly embedded
    dbc.Container([
        # Loading component
        dcc.Loading(
            id="loading-main",
            type="circle",
            children=[                dbc.Row([
                    # Sidebar
                    dbc.Col([
                        filter_panel,
                        suggestions_panel,
                        ai_assistant_panel,
                        export_panel
                    ], width=3),

                    # Main content area
                    dbc.Col([
                        # KPI Cards Row
                        dbc.Row([
                            dbc.Col(html.Div(id="kpi-cards"), width=12),
                        ], className="mb-4"),

                        # Charts Row 1
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.I(className="fas fa-chart-pie me-2"),
                                        "Vulnerability Severity Distribution"
                                    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white", "border": "none", "fontWeight": "600"}),
                                    dbc.CardBody([
                                        dcc.Graph(id='severity-chart', config={'displayModeBar': False})
                                    ])
                                ], className="h-100 shadow-sm border-0", style={"borderRadius": "1rem"})
                            ], width=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.I(className="fas fa-chart-donut me-2"),
                                        "Status Breakdown"
                                    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white", "border": "none", "fontWeight": "600"}),
                                    dbc.CardBody([
                                        dcc.Graph(id='status-chart', config={'displayModeBar': False})
                                    ])
                                ], className="h-100 shadow-sm border-0", style={"borderRadius": "1rem"})
                            ], width=6)
                        ], className="mb-4"),

                        # Charts Row 2
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.I(className="fas fa-chart-bar me-2"),
                                        "Risk Score Distribution"
                                    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white", "border": "none", "fontWeight": "600"}),
                                    dbc.CardBody([
                                        dcc.Graph(id='risk-score-chart', config={'displayModeBar': False})
                                    ])
                                ], className="h-100 shadow-sm border-0", style={"borderRadius": "1rem"})
                            ], width=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.I(className="fas fa-clock me-2"),
                                        "Remediation Time Analysis"
                                    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white", "border": "none", "fontWeight": "600"}),
                                    dbc.CardBody([
                                        dcc.Graph(id='days-to-close-chart', config={'displayModeBar': False})
                                    ])
                                ], className="h-100 shadow-sm border-0", style={"borderRadius": "1rem"})
                            ], width=6)
                        ], className="mb-4"),

                        # Urgent Issues Table
                        dbc.Row(id="urgent-issues", children=[
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.I(className="fas fa-exclamation-triangle me-2"),
                                        "Critical Attention Required",
                                        dbc.Badge("High Priority", color="danger", className="ms-2")
                                    ], style={"background": "linear-gradient(90deg, #dc2626 0%, #b91c1c 100%)", "color": "white", "border": "none", "fontWeight": "600"}),
                                    dbc.CardBody([
                                        dash_table.DataTable(
                                            id='urgent-table',
                                            columns=[
                                                {'name': 'Application Owner', 'id': 'Application_Owner_Name'},
                                                {'name': 'Application', 'id': 'Application_Name'},
                                                {'name': 'Vulnerability', 'id': 'Vulnerability_Description'},
                                                {'name': 'Severity', 'id': 'Vulnerability_Severity'},
                                                {'name': 'CVSS Score', 'id': 'CVSS_Score', 'type': 'numeric'},
                                                {'name': 'Risk Score', 'id': 'Risk_Score', 'type': 'numeric'},
                                                {'name': 'Days Open', 'id': 'Days_Open', 'type': 'numeric'},
                                                {'name': 'Status', 'id': 'Status'},
                                                {'name': 'Priority', 'id': 'Priority'}
                                            ],
                                            style_cell={
                                                'textAlign': 'left',
                                                'padding': '12px',
                                                'fontFamily': 'Inter, sans-serif',
                                                'fontSize': '0.875rem'
                                            },
                                            style_header={
                                                'backgroundColor': '#1e293b',
                                                'color': 'white',
                                                'fontWeight': '600',
                                                'textTransform': 'uppercase',
                                                'letterSpacing': '0.5px'
                                            },
                                            style_data_conditional=[
                                                {
                                                    'if': {'filter_query': '{Vulnerability_Severity} contains "Critical"'},
                                                    'backgroundColor': 'rgba(220, 38, 38, 0.1)',
                                                    'color': '#dc2626',
                                                    'fontWeight': '600'
                                                },
                                                {
                                                    'if': {'filter_query': '{Vulnerability_Severity} contains "High"'},
                                                    'backgroundColor': 'rgba(234, 88, 12, 0.1)',
                                                    'color': '#ea580c',
                                                    'fontWeight': '500'
                                                }
                                            ],
                                            page_size=10,
                                            sort_action='native',
                                            filter_action='native',
                                            style_table={'borderRadius': '0.5rem', 'overflow': 'hidden'}
                                        )
                                    ], style={"padding": "1.5rem"})
                                ], className="shadow-sm border-0", style={"borderRadius": "1rem"})
                            ], width=12)
                        ], className="mb-4"),                        # Additional sections will be added here...                        
                    ], width=9)
                ])
            ]
        )
    ], fluid=True),
    
    # Footer
    html.Footer([
        dbc.Container([
            html.Hr(style={"margin": "3rem 0 2rem 0", "border": "none", "height": "1px", "background": "linear-gradient(90deg, transparent, #e2e8f0, transparent)"}),
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.I(className="fas fa-shield-halved me-2", style={"color": "#1a365d"}),
                        "CyberSec Pro Dashboard © 2025"
                    ], className="text-muted mb-0", style={"fontWeight": "500"})
                ], width=6),
                dbc.Col([
                    html.P([
                        html.I(className="fas fa-sync-alt me-2", style={"color": "#38a169"}),
                        f"Last updated: {current_date.strftime('%B %d, %Y at %I:%M %p')}"
                    ], className="text-muted text-end mb-0", style={"fontWeight": "500"})
                ], width=6)
            ])
        ], fluid=True)
    ], style={"background": "#f7fafc", "padding": "2rem 0", "marginTop": "4rem"})
])

# Add the loading components (optional additional loading overlays)
additional_loading = dcc.Loading(
    id="loading-suggestions",
    type="circle",
    children=[html.Div(id="loading-output-suggestions")],
    style={"position": "fixed", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)", "zIndex": "9999"}
)

print("✅ Enhanced dashboard layout created successfully!")
print("🚀 Starting optimized dashboard server...")

# ========================================
# ENHANCED CALLBACKS WITH OPTIMIZATIONS
# ========================================

# Utility function for API calls with error handling
def safe_api_call(endpoint, data=None, timeout=10):
    """Make safe API calls with proper error handling"""
    try:
        url = f"http://127.0.0.1:8001{endpoint}"
        if data:
            response = requests.post(url, json=data, timeout=timeout)
        else:
            response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code}"
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server. Please ensure it's running."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# Enhanced callback for department dropdown based on AO selection
@app.callback(
    Output('dept-dropdown', 'options'),
    Output('dept-dropdown', 'value'),
    [Input('ao-dropdown', 'value')],
    prevent_initial_call=False
)
def update_dept_dropdown(selected_aos):
    """Update department dropdown based on selected Application Owners"""
    if not selected_aos:
        return [], []
    
    # Filter data based on selected AOs
    filtered_df = df[df['Application_Owner_ID'].isin(selected_aos)]
    dept_options = [{'label': dept, 'value': dept} 
                   for dept in sorted(filtered_df['Dept_Name'].unique())]
    
    # Auto-select departments if only one AO is selected
    if len(selected_aos) == 1:
        dept_values = filtered_df['Dept_Name'].unique().tolist()
    else:
        dept_values = []
    
    return dept_options, dept_values

# Enhanced KPI cards callback with trend analysis
@app.callback(
    Output('kpi-cards', 'children'),
    [Input('ao-dropdown', 'value'),
     Input('dept-dropdown', 'value'),
     Input('status-checklist', 'value')],
    prevent_initial_call=False
)
def update_kpi_cards(selected_aos, selected_depts, selected_statuses):
    """Update KPI cards with enhanced metrics and trends"""
    # Ensure inputs are lists and not None
    selected_aos = selected_aos if selected_aos else []
    selected_depts = selected_depts if selected_depts else []
    selected_statuses = selected_statuses if selected_statuses else []
    
    # Convert to lists if they're not already
    if not isinstance(selected_aos, list):
        selected_aos = list(selected_aos) if selected_aos else []
    if not isinstance(selected_depts, list):
        selected_depts = list(selected_depts) if selected_depts else []
    if not isinstance(selected_statuses, list):
        selected_statuses = list(selected_statuses) if selected_statuses else []
    
    if not selected_aos or not selected_statuses:
        return html.Div("Please select filters to display KPIs", className="text-center text-muted p-5")
    
    # Filter data
    filtered_df = df[
        (df['Application_Owner_ID'].isin(selected_aos)) &
        (df['Status'].isin(selected_statuses))
    ]
    
    if selected_depts:
        filtered_df = filtered_df[filtered_df['Dept_Name'].isin(selected_depts)]
    
    if filtered_df.empty:
        return html.Div("No data matches the selected filters", className="text-center text-muted p-5")
    
    # Calculate metrics
    total_vulns = len(filtered_df)
    critical_high_count = len(filtered_df[filtered_df['Is_Critical_High']])
    critical_high_over_30 = len(filtered_df[filtered_df['Is_Critical_High_Over_30']])
    avg_risk_score = filtered_df['Risk_Score'].mean()
    avg_cvss_score = filtered_df['CVSS_Score'].mean()
    open_vulns = len(filtered_df[filtered_df['Status'] == 'Open'])
    
    # Calculate trends (compare with previous period)
    current_month = current_date.strftime('%Y-%m')
    prev_month_data = df[df['Detection_Month'] < current_month]
    
    # Trend calculations
    prev_total = len(prev_month_data) if not prev_month_data.empty else total_vulns
    total_trend = ((total_vulns - prev_total) / prev_total * 100) if prev_total > 0 else 0
    
    # Create trend data for mini charts
    monthly_counts = df.groupby('Detection_Month').size().tail(6).values.tolist()
    risk_trends = df.groupby('Detection_Month')['Risk_Score'].mean().tail(6).values.tolist()
    
    return dbc.Row([
        dbc.Col([
            create_enhanced_kpi_card(
                title="Total Vulnerabilities",
                value=f"{total_vulns:,}",
                color=colors['primary'],
                icon="fas fa-bug",
                delta=total_trend,
                trend_data=monthly_counts
            )
        ], width=2),
        dbc.Col([
            create_enhanced_kpi_card(
                title="Critical & High",
                value=f"{critical_high_count:,}",
                color=colors['Critical'],
                icon="fas fa-exclamation-triangle",
                delta=None
            )
        ], width=2),
        dbc.Col([
            create_enhanced_kpi_card(
                title="Urgent (>30 days)",
                value=f"{critical_high_over_30:,}",
                color=colors['Urgent'],
                icon="fas fa-clock",
                delta=None
            )
        ], width=2),
        dbc.Col([
            create_enhanced_kpi_card(
                title="Avg Risk Score",
                value=f"{avg_risk_score:.1f}",
                suffix="/10",
                color=colors['warning'] if avg_risk_score > 7 else colors['success'],
                icon="fas fa-chart-line",
                trend_data=risk_trends
            )
        ], width=2),
        dbc.Col([
            create_enhanced_kpi_card(
                title="Avg CVSS Score",
                value=f"{avg_cvss_score:.1f}",
                suffix="/10",
                color=colors['info'],
                icon="fas fa-shield-alt"
            )
        ], width=2),
        dbc.Col([
            create_enhanced_kpi_card(
                title="Open Issues",
                value=f"{open_vulns:,}",
                color=colors['Open'],
                icon="fas fa-folder-open"
            )
        ], width=2)
    ], className="g-3")

# Enhanced charts callbacks with improved styling
@app.callback(
    [Output('severity-chart', 'figure'),
     Output('status-chart', 'figure'),
     Output('risk-score-chart', 'figure'),
     Output('days-to-close-chart', 'figure')],
    [Input('ao-dropdown', 'value'),
     Input('dept-dropdown', 'value'),
     Input('status-checklist', 'value')],
    prevent_initial_call=False
)
def update_charts(selected_aos, selected_depts, selected_statuses):
    """Update all charts with enhanced styling and interactivity"""
    # Ensure inputs are lists and not None
    selected_aos = selected_aos if selected_aos else []
    selected_depts = selected_depts if selected_depts else []
    selected_statuses = selected_statuses if selected_statuses else []
    
    # Convert to lists if they're not already
    if not isinstance(selected_aos, list):
        selected_aos = list(selected_aos) if selected_aos else []
    if not isinstance(selected_depts, list):
        selected_depts = list(selected_depts) if selected_depts else []
    if not isinstance(selected_statuses, list):
        selected_statuses = list(selected_statuses) if selected_statuses else []
        
    if not selected_aos or not selected_statuses:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Please select filters to display data",
            template="plotly_white",
            height=300
        )
        return empty_fig, empty_fig, empty_fig, empty_fig
    
    # Filter data
    filtered_df = df[
        (df['Application_Owner_ID'].isin(selected_aos)) &
        (df['Status'].isin(selected_statuses))
    ]
    
    if selected_depts:
        filtered_df = filtered_df[filtered_df['Dept_Name'].isin(selected_depts)]
    
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No data matches the selected filters",
            template="plotly_white",
            height=300
        )
        return empty_fig, empty_fig, empty_fig, empty_fig
    
    # Enhanced chart styling template
    chart_template = {
        'layout': {
            'template': 'plotly_white',
            'height': 350,
            'margin': dict(l=20, r=20, t=40, b=20),
            'font': {'family': 'Inter, sans-serif', 'size': 12},
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'hovermode': 'closest'
        }
    }
    
    # 1. Severity Distribution (Enhanced Donut Chart)
    severity_counts = filtered_df['Vulnerability_Severity'].value_counts()
    severity_colors = [colors.get(sev, '#6b7280') for sev in severity_counts.index]
    
    severity_fig = go.Figure(data=[go.Pie(
        labels=severity_counts.index,
        values=severity_counts.values,
        hole=0.6,
        marker=dict(colors=severity_colors, line=dict(color='white', width=2)),
        textinfo='label+percent+value',
        textposition='outside',        hovertemplate='<b>%{label}</b><br>' +
                     'Count: %{value}<br>' +
                     'Percentage: %{percent}<br>' +
                     '<extra></extra>'
    )])
    
    severity_fig.update_layout(
        **chart_template['layout'],
        title=dict(text="Vulnerability Severity Distribution", x=0.5, font=dict(size=16)),
        annotations=[dict(text=f'Total<br><b>{len(filtered_df)}</b>', x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    
    # 2. Status Breakdown (Enhanced Bar Chart)
    status_counts = filtered_df['Status'].value_counts()
    status_colors = [colors.get(status, '#6b7280') for status in status_counts.index]
    
    status_fig = go.Figure(data=[go.Bar(
        x=status_counts.values,
        y=status_counts.index,
        orientation='h',
        marker=dict(color=status_colors, line=dict(color='white', width=1)),        text=status_counts.values,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' +
                     'Count: %{x}<br>' +
                     '<extra></extra>'
    )])
    
    status_fig.update_layout(
        **chart_template['layout'],
        title=dict(text="Status Breakdown", x=0.5, font=dict(size=16)),
        xaxis=dict(title="Count", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(title="Status")
    )
    
    # 3. Risk Score Distribution (Enhanced Histogram)
    risk_fig = go.Figure(data=[go.Histogram(        x=filtered_df['Risk_Score'],
        nbinsx=20,
        marker=dict(color=colors['accent'], opacity=0.7, line=dict(color='white', width=1)),
        hovertemplate='Risk Score: %{x}<br>' +
                     'Count: %{y}<br>' +
                     '<extra></extra>'
    )])
    
    risk_fig.update_layout(
        **chart_template['layout'],
        title=dict(text="Risk Score Distribution", x=0.5, font=dict(size=16)),
        xaxis=dict(title="Risk Score", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(title="Frequency", showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    
    # Add vertical lines for risk thresholds
    risk_fig.add_vline(x=7, line_dash="dash", line_color="red", 
                      annotation_text="High Risk Threshold", annotation_position="top")
    risk_fig.add_vline(x=4, line_dash="dash", line_color="orange",
                      annotation_text="Medium Risk", annotation_position="top")
    
    # 4. Remediation Time Analysis (Enhanced Box Plot)
    days_fig = go.Figure()
    
    # Add box plot for each severity
    for severity in filtered_df['Vulnerability_Severity'].unique():
        severity_data = filtered_df[filtered_df['Vulnerability_Severity'] == severity]
        days_fig.add_trace(go.Box(
            y=severity_data['Days_to_Close'].dropna(),
            name=severity,
            marker=dict(color=colors.get(severity, '#6b7280')),            boxpoints='outliers',
            hovertemplate=f'<b>{severity}</b><br>' +
                         'Days to Close: %{y}<br>' +
                         '<extra></extra>'
        ))
    
    days_fig.update_layout(
        **chart_template['layout'],
        title=dict(text="Remediation Time by Severity", x=0.5, font=dict(size=16)),
        xaxis=dict(title="Vulnerability Severity"),
        yaxis=dict(title="Days to Close", showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    
    return severity_fig, status_fig, risk_fig, days_fig

# Enhanced urgent issues table callback
@app.callback(
    Output('urgent-table', 'data'),
    [Input('ao-dropdown', 'value'),
     Input('dept-dropdown', 'value'),
     Input('status-checklist', 'value')],
    prevent_initial_call=False
)
def update_urgent_table(selected_aos, selected_depts, selected_statuses):
    """Update urgent issues table with filtered data"""
    # Ensure inputs are lists and not None
    selected_aos = selected_aos if selected_aos else []
    selected_depts = selected_depts if selected_depts else []
    selected_statuses = selected_statuses if selected_statuses else []
    
    # Convert to lists if they're not already
    if not isinstance(selected_aos, list):
        selected_aos = list(selected_aos) if selected_aos else []
    if not isinstance(selected_depts, list):
        selected_depts = list(selected_depts) if selected_depts else []
    if not isinstance(selected_statuses, list):
        selected_statuses = list(selected_statuses) if selected_statuses else []
        
    if not selected_aos or not selected_statuses:
        return []
    
    # Filter for urgent issues
    filtered_df = df[
        (df['Application_Owner_ID'].isin(selected_aos)) &
        (df['Status'].isin(selected_statuses)) &
        (df['Is_Critical_High_Over_30'] | (df['CVSS_Score'] > 8) | (df['Risk_Score'] > 8))
    ]
    
    if selected_depts:
        filtered_df = filtered_df[filtered_df['Dept_Name'].isin(selected_depts)]
    
    # Sort by urgency (CVSS Score, then Risk Score, then Days Open)
    filtered_df = filtered_df.sort_values(['CVSS_Score', 'Risk_Score', 'Days_Open'], ascending=[False, False, False])
    
    # Select and format columns for display
    urgent_data = filtered_df[[
        'Application_Owner_Name', 'Application_Name', 'Vulnerability_Description',
        'Vulnerability_Severity', 'CVSS_Score', 'Risk_Score', 'Days_Open', 'Status', 'Priority'
    ]].head(20).to_dict('records')
    
    return urgent_data

# Enhanced suggestions callback with improved API integration
@app.callback(
    Output('suggestion-content', 'children'),
    [Input('refresh-suggestions', 'n_clicks'),
     Input('ao-dropdown', 'value')],
    prevent_initial_call=False
)
def update_suggestions(n_clicks, selected_aos):
    """Update AI suggestions with enhanced error handling"""
    # Ensure input is a list and not None
    selected_aos = selected_aos if selected_aos else []
    if not isinstance(selected_aos, list):
        selected_aos = list(selected_aos) if selected_aos else []
        
    if not selected_aos:
        return html.Div([
            html.I(className="fas fa-info-circle me-2", style={"color": "#6b7280"}),
            html.Span("Please select Application Owner(s) to get personalized insights.", 
                     style={"color": "#6b7280", "fontStyle": "italic"})
        ])
    
    try:
        # Prepare data for suggestions API
        ao_data = []
        for ao_id in selected_aos:
            ao_df = df[df['Application_Owner_ID'] == ao_id]
            if not ao_df.empty:
                ao_info = {
                    'ao_id': ao_id,
                    'ao_name': ao_df['Application_Owner_Name'].iloc[0],
                    'total_vulns': len(ao_df),
                    'critical_high': len(ao_df[ao_df['Is_Critical_High']]),
                    'over_30_days': len(ao_df[ao_df['Is_Over_30_Days']]),
                    'avg_risk_score': float(ao_df['Risk_Score'].mean()),
                    'avg_cvss_score': float(ao_df['CVSS_Score'].mean()),
                    'open_issues': len(ao_df[ao_df['Status'] == 'Open']),
                    'dept_name': ao_df['Dept_Name'].iloc[0]
                }
                ao_data.append(ao_info)
        
        # Make API call
        suggestions_data, error = safe_api_call('/suggestions', {'aos': ao_data})
        
        if error:
            return html.Div([
                html.I(className="fas fa-exclamation-triangle me-2", style={"color": "#dc2626"}),
                html.Span(f"Error loading suggestions: {error}", style={"color": "#dc2626"})
            ])
        
        if not suggestions_data or not suggestions_data.get('suggestions'):
            return html.Div([
                html.I(className="fas fa-lightbulb me-2", style={"color": "#f59e0b"}),
                html.Span("No suggestions available at this time.", style={"color": "#6b7280"})
            ])
        
        # Format suggestions with enhanced UI
        suggestion_cards = []
        for idx, suggestion in enumerate(suggestions_data['suggestions'][:5]):  # Limit to 5 suggestions
            suggestion_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H6([
                                html.I(className="fas fa-lightbulb me-2", style={"color": "#f59e0b"}),
                                f"Insight #{idx + 1}"
                            ], className="mb-2", style={"color": "#1e293b", "fontWeight": "600"}),
                            html.P(suggestion.get('text', suggestion.get('template', 'No suggestion text')), 
                                  className="mb-0", style={"lineHeight": "1.6"})
                        ])
                    ], style={"padding": "1rem"})
                ], className="mb-3 border-0", style={
                    "background": "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
                    "borderRadius": "0.75rem",
                    "border": "1px solid #e2e8f0"
                })
            )
        
        return html.Div(suggestion_cards)
        
    except Exception as e:
        return html.Div([
            html.I(className="fas fa-exclamation-triangle me-2", style={"color": "#dc2626"}),
            html.Span(f"Unexpected error: {str(e)}", style={"color": "#dc2626"})
        ])

# Enhanced export callbacks
@app.callback(
    Output("download-csv", "data"),
    [Input("export-csv", "n_clicks")],
    [State('ao-dropdown', 'value'),
     State('dept-dropdown', 'value'),
     State('status-checklist', 'value')],
    prevent_initial_call=True
)
def export_csv(n_clicks, selected_aos, selected_depts, selected_statuses):
    """Export filtered data to CSV with enhanced formatting"""
    # Ensure inputs are lists and not None
    selected_aos = selected_aos if selected_aos else []
    selected_depts = selected_depts if selected_depts else []
    selected_statuses = selected_statuses if selected_statuses else []
    
    # Convert to lists if they're not already
    if not isinstance(selected_aos, list):
        selected_aos = list(selected_aos) if selected_aos else []
    if not isinstance(selected_depts, list):
        selected_depts = list(selected_depts) if selected_depts else []
    if not isinstance(selected_statuses, list):
        selected_statuses = list(selected_statuses) if selected_statuses else []
        
    if not n_clicks or not selected_aos or not selected_statuses:
        raise PreventUpdate
    
    # Filter data
    filtered_df = df[
        (df['Application_Owner_ID'].isin(selected_aos)) &
        (df['Status'].isin(selected_statuses))
    ]
    
    if selected_depts:
        filtered_df = filtered_df[filtered_df['Dept_Name'].isin(selected_depts)]
    
    # Format timestamp
    timestamp = current_date.strftime('%Y%m%d_%H%M%S')
    filename = f"cybersec_dashboard_export_{timestamp}.csv"
    
    return dcc.send_data_frame(filtered_df.to_csv, filename, index=False)

# ========================================
# CHATBOT FUNCTIONALITY
# ========================================

# Chatbot callback with enhanced features
@app.callback(
    Output('chatbot-response', 'children'),
    [Input('chatbot-submit', 'n_clicks')],
    [State('chatbot-input', 'value'),
     State('ao-dropdown', 'value')],
    prevent_initial_call=True
)
def update_chatbot_response(n_clicks, user_input, selected_aos):
    """Enhanced chatbot with context-aware responses"""
    if not n_clicks or not user_input:
        return html.Div([
            html.I(className="fas fa-robot me-2", style={"color": "#6b7280", "fontSize": "2rem"}),
            html.Div([
                html.H5("AI Security Assistant", className="mb-2", style={"color": "#1e293b"}),
                html.P("I'm here to help you with cybersecurity insights, risk analysis, and best practices. Ask me anything!", 
                      className="text-muted mb-0")
            ])
        ], style={"textAlign": "center", "padding": "2rem"})
      # Prepare chatbot request data
    chatbot_data = {
        'question': user_input,
        'ao_id': selected_aos[0] if selected_aos else None  # Use first selected AO if available
    }
      # Make chatbot API call
    chatbot_response, error = safe_api_call('/chatbot', chatbot_data)
    
    if error:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error: {error}"
        ], color="danger", className="mb-0")
    
    if not chatbot_response or not chatbot_response.get('response'):
        return dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
        ], color="warning", className="mb-0")
    
    # Format response with enhanced styling
    response_text = chatbot_response['response']
    confidence = chatbot_response.get('confidence', 0.8)
    
    # Determine confidence color
    confidence_color = "#16a34a" if confidence > 0.8 else "#f59e0b" if confidence > 0.6 else "#dc2626"
    
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-user me-2", style={"color": "#6b7280"}),
                        html.Strong("You:", style={"color": "#1e293b"})
                    ], className="mb-2"),
                    html.P(user_input, style={
                        "background": "#f1f5f9", 
                        "padding": "0.75rem", 
                        "borderRadius": "0.5rem",
                        "margin": "0"
                    })
                ], className="mb-3"),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-robot me-2", style={"color": "#0d47a1"}),
                        html.Strong("AI Assistant:", style={"color": "#1e293b"}),
                        dbc.Badge(f"Confidence: {confidence:.0%}", 
                                color="success" if confidence > 0.8 else "warning" if confidence > 0.6 else "danger",
                                className="ms-2", style={"fontSize": "0.7rem"})
                    ], className="mb-2"),
                    html.Div(
                        dcc.Markdown(response_text, style={"margin": "0"}),
                        style={
                            "background": "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
                            "padding": "1rem",
                            "borderRadius": "0.5rem",
                            "border": f"1px solid {confidence_color}",
                            "borderLeft": f"4px solid {confidence_color}"
                        }
                    )
                ])
            ])
        ], className="border-0 shadow-sm", style={"borderRadius": "0.75rem"})
    ])

# ========================================
# CLIENT-SIDE CALLBACKS FOR PERFORMANCE
# ========================================

# Client-side callback for real-time filtering
app.clientside_callback(
    """
    function(n_clicks) {
        // Add smooth animations to cards
        const cards = document.querySelectorAll('.kpi-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
        return window.dash_clientside.no_update;
    }
    """,
    Output('apply-filters', 'n_clicks'),
    [Input('apply-filters', 'n_clicks')]
)

# ========================================
# SERVER STARTUP AND CONFIGURATION
# ========================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CYBERSEC PRO DASHBOARD - OPTIMIZED VERSION")
    print("="*60)
    print(f"📊 Dashboard Version: 2.0 Enhanced")
    print(f"📅 Current Date: {current_date.strftime('%B %d, %Y')}")
    print(f"📈 Total Records Loaded: {len(df):,}")
    print(f"🏢 Application Owners: {df['Application_Owner_ID'].nunique()}")
    print(f"🏬 Departments: {df['Dept_Name'].nunique()}")
    print(f"⚠️  Critical/High Issues: {len(df[df['Is_Critical_High']]):,}")
    print(f"🔥 Urgent Issues (>30 days): {len(df[df['Is_Critical_High_Over_30']]):,}")
    print("="*60)
    print("🎯 Features Enabled:")
    print("   ✅ Enhanced UI with custom CSS/JS")
    print("   ✅ Real-time filtering and analytics")
    print("   ✅ AI-powered suggestions")
    print("   ✅ Interactive chatbot")
    print("   ✅ Advanced data visualizations")
    print("   ✅ Export functionality")
    print("   ✅ Responsive design")
    print("   ✅ Performance optimizations")
    print("="*60)
    print("🌐 Starting server...")
    print("   Dashboard URL: http://localhost:8050")
    print("   API Server: http://localhost:8001 (ensure it's running)")
    print("="*60)
    
    try:
        app.run_server(
            debug=False,  # Set to False for production
            host='0.0.0.0',
            port=8050,
            dev_tools_hot_reload=False,
            dev_tools_ui=False
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Troubleshooting tips:")
        print("   1. Check if port 8050 is already in use")
        print("   2. Ensure API server is running on port 8001")
        print("   3. Check firewall settings")
        print("   4. Try running as administrator")
