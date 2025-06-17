# Cybersecurity KPI Dashboard for Application Owners

An interactive dashboard for Application Owners (AOs) to monitor, analyze, and improve their application-related security performance. The dashboard features an intelligent suggestion system powered by a compact LLM to provide personalized recommendations.

## Quick Start Guide

1. **Prerequisites**:

   - Python 3.8 or higher (from [python.org](https://python.org))
   - Git with LFS (from [git-scm.com](https://git-scm.com))
   - Git LFS (for downloading model files)

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/TejasParekh5/AO-Dashboard.git
   cd AO-Dashboard
   git lfs pull  # Pull large model files
   ```

3. **Set Up Virtual Environment** (recommended):

   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

4. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Dashboard**:

   - Basic Dashboard:

     - Windows: Double-click `start_dashboard.bat`
     - Linux/Mac: `./start_dashboard.sh`

   - Enhanced Dashboard with AI:
     - Windows: Double-click `start_enhanced_with_api.bat`
     - Linux/Mac: `./start_enhanced_dashboard.sh`

6. **Access the Dashboard**:
   - Basic Dashboard: http://localhost:8050
   - Enhanced Dashboard: http://localhost:8051

## Project Components

The project consists of two main dashboards:

1. **Basic Dashboard** (`dashboard.py`):

   - Essential KPI visualization features
   - Performance metrics and tracking
   - Interactive filtering and export functionality

2. **Enhanced Dashboard** (`enhanced_dashboard.py`):
   - AI-powered suggestion system
   - Advanced visualizations
   - Detailed performance analytics

## Key Features

### Basic Dashboard

- Interactive filtering by Application Owner, Department, and Status
- Real-time visualization of vulnerabilities and risk scores
- Performance tracking and comparison tools
- CSV export functionality
- Critical issue highlighting

### Enhanced Dashboard Additions

- LLM-powered suggestion system
- Advanced relationship mapping visuals
- Detailed AO performance analytics
- Risk concentration visualizations

## File Structure

- `dashboard.py` - Basic dashboard implementation
- `enhanced_dashboard.py` - Enhanced dashboard with AI features
- `suggestion_api.py` - AI suggestion system backend
- `model_utils.py` - Model utility functions
- `train_model.py` - Model training script
- `Cybersecurity_KPI_Minimal.xlsx` - Sample data file
- `models/` - Pre-trained model files (managed with Git LFS)
- Start scripts:
  - `start_dashboard.bat/sh` - Launch basic dashboard
  - `start_enhanced_with_api.bat` - Launch enhanced dashboard with API

## System Requirements

- RAM: 4GB minimum
- Disk Space: ~500MB
- Internet connection (first run)
- Modern web browser (Chrome/Firefox/Edge)

## Troubleshooting

- **Module not found errors**: Ensure virtual environment is activated and dependencies are installed
- **Port conflicts**: Check if ports 8050/8051 are available
- **Missing model files**: Run `git lfs pull` to download model files
- **Permission issues**: Run terminal as administrator (Windows) or use sudo (Linux/Mac)

## Advanced Usage

For detailed instructions on:

- Training custom models
- Modifying the suggestion system
- Advanced configuration options

See `TRAINING_AND_RUNNING_GUIDE.md`

## Data Structure

The dashboard uses `Cybersecurity_KPI_Minimal.xlsx` which contains:

- Application Owner information
- Application and Asset details
- Vulnerability data with severity and risk metrics
