"""
Simplified CyberSec Pro Dashboard - Direct Model Integration
No API server required - all functionality in one process
"""

from model_integration import generate_suggestions_direct, chatbot_response_direct
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback
import dash_bootstrap_components as dbc
import datetime
import base64
import io
from dash.exceptions import PreventUpdate
import warnings
warnings.filterwarnings('ignore')

# Import our direct model integration

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

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                      "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"],
                suppress_callback_exceptions=True,
                title="CyberSec Pro Dashboard")

# Define color palette for consistent styling
colors = {
    'primary': '#1f2937',
    'secondary': '#374151',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'info': '#3b82f6',
    'light': '#f9fafb',
    'dark': '#111827',
    'critical': '#dc2626',
    'high': '#ea580c',
    'medium': '#d97706',
    'low': '#65a30d'
}

# Enhanced navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink([html.I(className="fas fa-shield-alt me-2"), "CyberSec Pro"],
                                href="#", style={"color": "white", "fontSize": "1.2rem", "fontWeight": "bold"})),
        dbc.NavItem(dbc.NavLink([html.I(className="fas fa-calendar me-2"), current_date.strftime('%B %d, %Y')],
                                disabled=True, style={"color": "rgba(255,255,255,0.7)"})),
    ],
    brand="🛡️ Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
    className="mb-4 shadow-sm",
)

# Filter panel
filter_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-filter me-2"),
            html.Span("Smart Filters", style={"fontWeight": "600"})
        ])
    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white"}),
    dbc.CardBody([
        html.Div([
            html.Label([html.I(className="fas fa-user-tie me-2"), "Application Owner(s):"],
                       className="form-label", style={"fontWeight": "600", "color": "#1e293b"}),
            dcc.Dropdown(
                id='ao-dropdown',
                options=[{'label': f"{name} ({id})", 'value': id}
                         for id, name in df[['Application_Owner_ID', 'Application_Owner_Name']].drop_duplicates().values],
                value=[df['Application_Owner_ID'].iloc[0]],
                multi=True,
                clearable=False,
                className="mb-3"
            ),
        ]),
        html.Div([
            html.Label([html.I(className="fas fa-building me-2"), "Department:"],
                       className="form-label", style={"fontWeight": "600", "color": "#1e293b"}),
            dcc.Dropdown(
                id='dept-dropdown',
                options=[{'label': dept, 'value': dept}
                         for dept in sorted(df['Dept_Name'].unique())],
                multi=True,
                placeholder="Auto-populated based on AO selection",
                className="mb-3"
            ),
        ]),
        html.Div([
            html.Label([html.I(className="fas fa-tasks me-2"), "Status Filter:"],
                       className="form-label", style={"fontWeight": "600", "color": "#1e293b"}),
            dbc.Checklist(
                id='status-checklist',
                options=[{'label': status, 'value': status}
                         for status in sorted(df['Status'].unique())],
                value=list(df['Status'].unique()),
                inline=True,
                className="mb-3"
            ),
        ]),
        dbc.Button([html.I(className="fas fa-sync-alt me-2"), "Apply Filters"],
                   id="apply-filters", color="primary", className="w-100")
    ])
], className="mb-4 shadow-sm")

# AI Insights panel
suggestions_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-brain me-2"),
            html.Span("AI Insights", style={"fontWeight": "600"}),
            dbc.Badge("No API Required", color="success",
                      className="ms-2", style={"fontSize": "0.7rem"})
        ])
    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white"}),
    dbc.CardBody([
        dcc.Loading(
            id="loading-suggestions",
            children=[html.Div(
                id="suggestion-content", className="suggestion-box", style={"minHeight": "200px"})],
            type="default"
        ),
        dbc.Button([html.I(className="fas fa-refresh me-2"), "Refresh Insights"],
                   id="refresh-suggestions", color="info", className="w-100 mt-3")
    ])
], className="mb-4 shadow-sm")

# AI Assistant panel (integrated chatbot)
ai_assistant_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-robot",
                   style={"fontSize": "1.2rem", "color": "#3182ce", "marginRight": "0.75rem"}),
            html.Span("AI Security Assistant", style={
                      "fontWeight": "600", "fontSize": "1.1rem"})
        ])
    ], style={"background": "linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)"}),
    dbc.CardBody([
        html.Div(id="chatbot-response", children=[
            html.P("👋 Hello! I'm your AI security assistant. Ask me about vulnerability management, best practices, or dashboard features.",
                   style={"margin": "0", "color": "#4a5568", "fontStyle": "italic"})
        ], style={"minHeight": "150px", "maxHeight": "250px", "overflowY": "auto",
                  "padding": "1rem", "background": "#f7fafc", "borderRadius": "0.5rem",
                  "border": "1px solid #e2e8f0", "marginBottom": "1rem"}),
        dbc.InputGroup([
            dbc.Input(
                id="chatbot-input",
                placeholder="Ask about security insights, vulnerabilities, or recommendations...",
                type="text",
                style={"borderRadius": "0.5rem 0 0 0.5rem"}
            ),
            dbc.Button([html.I(className="fas fa-paper-plane")],
                       id="chatbot-submit", color="primary",
                       style={"borderRadius": "0 0.5rem 0.5rem 0", "width": "50px"})
        ], size="sm"),
    ])
], className="mb-4 shadow-sm")

# Export panel
export_panel = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.I(className="fas fa-download me-2"),
            html.Span("Export & Reports", style={"fontWeight": "600"})
        ])
    ], style={"background": "linear-gradient(90deg, #1e293b 0%, #374151 100%)", "color": "white"}),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-file-csv me-2"), "Export CSV"],
                           id="export-csv", color="success", className="w-100 mb-2"),
                dcc.Download(id="download-csv")
            ], width=6),
            dbc.Col([
                dbc.Button([html.I(className="fas fa-file-pdf me-2"), "Export PDF"],
                           id="export-pdf", color="danger", className="w-100 mb-2"),
                dcc.Download(id="download-pdf")
            ], width=6)
        ])
    ])
], className="mb-4 shadow-sm")

# Main layout
app.layout = dbc.Container([
    navbar,

    dbc.Row([
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

            # Charts Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.I(className="fas fa-chart-pie me-2"), "Severity Distribution"],
                                       style={"background": colors['primary'], "color": "white"}),
                        dbc.CardBody(
                            [dcc.Graph(id='severity-chart', config={'displayModeBar': False})])
                    ], className="h-100 shadow-sm")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.I(className="fas fa-chart-donut me-2"), "Status Breakdown"],
                                       style={"background": colors['primary'], "color": "white"}),
                        dbc.CardBody(
                            [dcc.Graph(id='status-chart', config={'displayModeBar': False})])
                    ], className="h-100 shadow-sm")
                ], width=6)
            ], className="mb-4"),

            # Urgent Issues Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.I(className="fas fa-exclamation-triangle me-2"), "Urgent Issues (>30 Days)"],
                                       style={"background": colors['danger'], "color": "white"}),
                        dbc.CardBody([
                            html.Div(id='urgent-table')
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ])

        ], width=9)
    ])
], fluid=True)

# Callbacks


@app.callback(
    Output('dept-dropdown', 'options'),
    Output('dept-dropdown', 'value'),
    [Input('ao-dropdown', 'value')]
)
def update_dept_dropdown(selected_aos):
    """Update department dropdown based on selected Application Owners"""
    if not selected_aos:
        return [], []

    filtered_df = df[df['Application_Owner_ID'].isin(selected_aos)]
    dept_options = [{'label': dept, 'value': dept}
                    for dept in sorted(filtered_df['Dept_Name'].unique())]

    if len(selected_aos) == 1:
        return dept_options, list(filtered_df['Dept_Name'].unique())
    else:
        return dept_options, []


@app.callback(
    Output("suggestion-content", "children"),
    [Input('ao-dropdown', 'value'),
     Input('dept-dropdown', 'value'),
     Input("refresh-suggestions", "n_clicks")]
)
def update_suggestions(selected_aos, selected_depts, refresh_clicks):
    """Generate AI suggestions using direct model integration"""
    if not selected_aos:
        return html.P("Please select at least one Application Owner to get personalized insights.",
                      className="text-muted")

    try:
        # Use direct model integration instead of API call
        suggestions = generate_suggestions_direct(selected_aos, selected_depts)

        if not suggestions:
            return html.P("No specific suggestions available for current selection.",
                          className="text-muted")

        suggestion_cards = []
        for i, suggestion in enumerate(suggestions, 1):
            priority_color = {
                'High': 'danger',
                'Medium': 'warning',
                'Low': 'info'
            }.get(suggestion.get('priority', 'Low'), 'info')

            card = dbc.Card([
                dbc.CardBody([
                    html.H6([
                        dbc.Badge(suggestion.get('priority', 'Low'),
                                  color=priority_color, className="me-2"),
                        suggestion.get('title', f'Suggestion {i}')
                    ], className="card-title"),
                    html.P(suggestion.get('description', 'No description available'),
                           className="card-text small"),
                    html.P([
                        html.Strong("Action: "),
                        suggestion.get('action', 'No action specified')
                    ], className="card-text small text-muted mb-1"),
                    html.P([
                        html.Strong("Impact: "),
                        suggestion.get('impact', 'Impact not specified')
                    ], className="card-text small text-muted mb-0")
                ])
            ], className="mb-2", style={"fontSize": "0.9rem"})

            suggestion_cards.append(card)

        return suggestion_cards

    except Exception as e:
        return html.Div([
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error generating suggestions: {str(e)}"
            ], color="warning", className="mb-0")
        ])


@app.callback(
    Output("chatbot-response", "children"),
    [Input("chatbot-submit", "n_clicks"),
     Input("chatbot-input", "n_submit")],
    [State("chatbot-input", "value"),
     State('ao-dropdown', 'value'),
     State('dept-dropdown', 'value')]
)
def handle_chatbot(submit_clicks, input_submit, user_message, selected_aos, selected_depts):
    """Handle chatbot interaction using direct model integration"""
    if not submit_clicks and not input_submit:
        return [html.P("👋 Hello! I'm your AI security assistant. Ask me about vulnerability management, best practices, or dashboard features.",
                       style={"margin": "0", "color": "#4a5568", "fontStyle": "italic"})]

    if not user_message or not user_message.strip():
        return [html.P("Please enter a question or message.", style={"color": "#e53e3e"})]

    try:
        # Prepare context data for the chatbot
        context_data = None
        if selected_aos:
            filtered_df = df[df['Application_Owner_ID'].isin(selected_aos)]
            if selected_depts:
                filtered_df = filtered_df[filtered_df['Dept_Name'].isin(
                    selected_depts)]
            context_data = {'filtered_data': filtered_df}

        # Use direct model integration instead of API call
        response = chatbot_response_direct(user_message, context_data)

        return [
            html.Div([
                html.P([html.Strong("You: "), user_message],
                       style={"marginBottom": "0.5rem", "color": "#2d3748"}),
                html.P([html.Strong("🤖 Assistant: "), response],
                       style={"marginBottom": "1rem", "color": "#4a5568", "whiteSpace": "pre-line"})
            ])
        ]

    except Exception as e:
        return [html.P(f"Sorry, I encountered an error: {str(e)}", style={"color": "#e53e3e"})]

# Additional callbacks for charts, KPIs, etc. (same as before but without API calls)


@app.callback(
    Output("kpi-cards", "children"),
    [Input('ao-dropdown', 'value'),
     Input('dept-dropdown', 'value'),
     Input('status-checklist', 'value')]
)
def update_kpi_cards(selected_aos, selected_depts, selected_statuses):
    """Update KPI cards based on filters"""
    if not selected_aos or not selected_statuses:
        return html.P("Please select filters to view KPIs", className="text-muted")

    # Filter data
    filtered_df = df[df['Application_Owner_ID'].isin(selected_aos)]
    if selected_depts:
        filtered_df = filtered_df[filtered_df['Dept_Name'].isin(
            selected_depts)]
    filtered_df = filtered_df[filtered_df['Status'].isin(selected_statuses)]

    # Calculate metrics
    total_vulns = len(filtered_df)
    critical_high = len(
        filtered_df[filtered_df['Vulnerability_Severity'].isin(['Critical', 'High'])])
    avg_days_open = filtered_df['Days_Open'].mean() if len(
        filtered_df) > 0 else 0
    urgent_count = len(filtered_df[filtered_df['Days_Open'] > 30])
    avg_cvss = filtered_df['CVSS_Score'].mean() if len(filtered_df) > 0 else 0
    high_risk = len(filtered_df[filtered_df['CVSS_Score'] > 7])

    cards = [
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_vulns:,}",
                            className="card-title text-primary"),
                    html.P("Total Vulnerabilities", className="card-text")
                ])
            ], className="text-center shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{critical_high:,}",
                            className="card-title text-danger"),
                    html.P("Critical/High", className="card-text")
                ])
            ], className="text-center shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_days_open:.1f}",
                            className="card-title text-warning"),
                    html.P("Avg Days Open", className="card-text")
                ])
            ], className="text-center shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{urgent_count:,}",
                            className="card-title text-danger"),
                    html.P("Urgent (>30 Days)", className="card-text")
                ])
            ], className="text-center shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_cvss:.1f}",
                            className="card-title text-info"),
                    html.P("Avg CVSS Score", className="card-text")
                ])
            ], className="text-center shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{high_risk:,}",
                            className="card-title text-warning"),
                    html.P("High Risk (CVSS>7)", className="card-text")
                ])
            ], className="text-center shadow-sm")
        ], width=2)
    ]

    return dbc.Row(cards)

# Add the remaining callbacks for charts and export functionality...
# (Same logic as before but without API dependencies)


if __name__ == '__main__':
    print("🚀 Starting CyberSec Pro Dashboard - Simplified Version")
    print("=" * 60)
    print("✅ No API server required - everything in one process!")
    print("📊 Direct model integration for better performance")
    print("🌐 Dashboard URL: http://localhost:8050")
    print("=" * 60)

    app.run_server(debug=False, host='0.0.0.0', port=8050)
