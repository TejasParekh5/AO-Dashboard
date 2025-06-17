# Cybersecurity KPI Dashboard - Simplified Setup Guide

This guide helps you run the Cybersecurity KPI Dashboard without the machine learning components if you're experiencing dependency issues.

## Simple Setup Instructions

1. **Install Python packages**:

   ```
   pip install -r simple_requirements.txt
   ```

2. **Run the simplified dashboard**:

   ```
   .\start_simple_dashboard.bat
   ```

3. **Access the dashboard**:
   Open your browser and go to [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

## Troubleshooting

### Common Issues and Solutions

1. **PyTorch/sentence-transformers Installation Errors**:

   - The simplified version doesn't require these libraries
   - Use the simplified setup instead which uses rule-based suggestions

2. **API Not Running**:

   - Make sure ports 8000 and 8050 are not in use by other applications
   - Check if any antivirus or firewall is blocking the applications

3. **Dashboard Can't Connect to API**:

   - Ensure the API is running (you should see a terminal window for it)
   - The API should be accessible at http://127.0.0.1:8000

4. **Python Environment Issues**:
   - If you have multiple Python installations, use the full path to your Python executable
   - You can edit the .bat file to use a specific Python installation

## Manual Start

If the batch file doesn't work, you can start the components manually:

1. **Start the Simple Suggestion API**:

   ```
   python simple_suggestion_api.py
   ```

2. **Start the Dashboard**:
   ```
   python enhanced_dashboard.py
   ```

## Notes

- The simplified version provides rule-based suggestions instead of ML-powered ones
- All dashboard features remain fully functional
- Data visualization and filtering capabilities work the same way

For more detailed information or if you want to set up the full ML-powered version, please refer to the complete documentation.
