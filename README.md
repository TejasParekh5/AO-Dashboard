# 🛡️ CyberSec Pro Dashboard - Enterprise Security Analytics

<div align="center">
  <img src="https://img.shields.io/badge/Version-2.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8%2B-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/Dashboard-Dash-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/AI-Powered-purple.svg" alt="AI">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg" alt="Status">
</div>

## 📋 Overview

**CyberSec Pro Dashboard** is an advanced, AI-powered cybersecurity analytics platform designed for Application Owners (AOs) to monitor, analyze, and improve their application security posture. The dashboard provides real-time insights, intelligent recommendations, and comprehensive vulnerability management capabilities.

### 🎯 Key Features

- **🔍 Real-time Security Analytics** - Live monitoring of vulnerabilities, risk scores, and security metrics
- **🤖 AI-Powered Insights** - Machine learning-driven suggestions and recommendations
- **💬 Intelligent Chatbot** - Interactive AI assistant for security guidance
- **📊 Advanced Visualizations** - Interactive charts and dashboards with Plotly
- **🎛️ Smart Filtering** - Dynamic filtering by Application Owner, Department, and Status
- **📈 KPI Monitoring** - Critical security metrics and performance indicators
- **📥 Export Capabilities** - CSV and PDF report generation
- **🎨 Professional UI** - Modern, responsive design with custom styling
- **⚡ High Performance** - Optimized for handling large datasets

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download here](https://python.org)
- **Git** - [Download here](https://git-scm.com)
- **4GB RAM minimum** (8GB recommended for optimal performance)
- **1GB free disk space**

### 🛠️ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YourUsername/CyberSec-Pro-Dashboard.git
   cd CyberSec-Pro-Dashboard
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\\Scripts\\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Data File**
   ```bash
   # Ensure Cybersecurity_KPI_Minimal.xlsx is in the root directory
   python inspect_dataset.py
   ```

## 🏃‍♂️ Running the Dashboard

### Method 1: Automated Scripts (Recommended)

**Windows:**
```bash
# Start both dashboard and API
START_OPTIMIZED_DASHBOARD.bat
```

**PowerShell:**
```powershell
# Enhanced PowerShell script
.\\scripts\\start_optimized_dashboard.ps1
```

### Method 2: Manual Start

1. **Start the API Server** (Terminal 1)
   ```bash
   python api_optimized.py
   ```
   - API will run on: `http://localhost:8001`

2. **Start the Dashboard** (Terminal 2)
   ```bash
   python dashboard_optimized.py
   ```
   - Dashboard will run on: `http://localhost:8050`

3. **Access the Dashboard**
   - Open your browser and navigate to: `http://localhost:8050`

## 🧠 AI Model Training

### Training Your Own Model

1. **Prepare Training Data**
   ```bash
   python inspect_dataset.py  # Analyze your data
   ```

2. **Train the Model**
   ```bash
   python train_model.py
   ```
   - Model will be saved to: `models/fine_tuned_cybersec_model/`
   - Training typically takes 10-30 minutes depending on your hardware

3. **Validate Model Performance**
   ```bash
   python model_utils.py  # Test model performance
   ```

### Using Pre-trained Models

The dashboard comes with a pre-trained cybersecurity model optimized for:
- **Vulnerability Analysis**
- **Risk Assessment**
- **Security Recommendations**
- **Best Practices Guidance**

## 📁 Project Structure

```
CyberSec-Pro-Dashboard/
├── 📊 dashboard_optimized.py          # Main dashboard application
├── 🔌 api_optimized.py               # FastAPI backend for AI features
├── 🧠 train_model.py                 # Model training script
├── 🔧 model_utils.py                 # Model utilities and testing
├── 📈 analyze_excel.py               # Data analysis tools
├── 🔍 inspect_dataset.py             # Dataset inspection
├── 📋 requirements.txt               # Python dependencies
├── 📄 Cybersecurity_KPI_Minimal.xlsx # Sample security data
├── 🎨 assets/                        # CSS, JS, and static files
│   ├── css/dashboard.css             # Custom dashboard styling
│   └── js/dashboard.js               # Dashboard JavaScript
├── 🤖 models/                        # AI models directory
│   ├── fine_tuned_cybersec_model/    # Custom trained model
│   └── cache/                        # Model cache
├── 📜 scripts/                       # Automation scripts
│   ├── start_optimized_dashboard.ps1 # PowerShell startup
│   └── optimize_project.ps1          # Project optimization
├── 🔧 backup_simplified_files/       # Backup configurations
└── 📚 docs/                          # Documentation
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=False

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Model Configuration
MODEL_PATH=models/fine_tuned_cybersec_model
CACHE_SIZE=1000

# Data Configuration
DATA_FILE=Cybersecurity_KPI_Minimal.xlsx
```

### Dashboard Customization

1. **Custom Styling**: Edit `assets/css/dashboard.css`
2. **Custom JavaScript**: Edit `assets/js/dashboard.js`
3. **Color Scheme**: Modify CSS variables in dashboard.css
4. **Logo/Branding**: Replace assets in `assets/` directory

## 📊 Features Deep Dive

### 🎛️ Smart Filters
- **Application Owner Selection**: Multi-select dropdown
- **Department Filtering**: Dynamic department filtering
- **Status Filtering**: Checkbox-based status selection
- **Real-time Updates**: Instant chart and data updates

### 🤖 AI Insights Panel
- **Intelligent Suggestions**: ML-powered recommendations
- **Risk Analysis**: Automated risk assessment
- **Best Practices**: Security guideline suggestions
- **Performance Insights**: KPI improvement recommendations

### 💬 AI Security Assistant
- **Interactive Chatbot**: Natural language security queries
- **Context-Aware**: Understands your current dashboard context
- **Knowledge Base**: Trained on cybersecurity best practices
- **Real-time Responses**: Instant answers to security questions

### 📈 Analytics & Visualizations
- **Vulnerability Distribution**: Pie charts and bar graphs
- **Risk Score Analysis**: Trend analysis and histograms
- **Status Breakdowns**: Current security posture overview
- **Time Series**: Historical trend analysis

## 🧪 Testing

### Running Tests

```bash
# Test dashboard functionality
python test_dashboard_components.py

# Test API endpoints
python test_fixes.py

# Validate data integrity
python analyze_excel.py
```

### Manual Testing Checklist

- [ ] Dashboard loads without errors
- [ ] All filters work correctly
- [ ] Charts update dynamically
- [ ] AI suggestions generate properly
- [ ] Chatbot responds to queries
- [ ] Export functions work
- [ ] API endpoints are accessible

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill existing processes
   taskkill /f /im python.exe  # Windows
   # or
   pkill -f python  # Linux/Mac
   ```

2. **Model Loading Errors**
   ```bash
   # Re-download models
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')"
   ```

3. **Data File Issues**
   ```bash
   # Verify data file integrity
   python inspect_dataset.py
   ```

4. **Dependency Issues**
   ```bash
   # Reinstall dependencies
   pip install --upgrade -r requirements.txt
   ```

### Performance Optimization

- **Large Datasets**: Consider data sampling for datasets > 10,000 records
- **Memory Usage**: Monitor RAM usage; restart services if needed
- **Browser Cache**: Clear browser cache if UI issues occur
- **Model Cache**: Pre-warm model cache for faster responses

## 📦 Deployment

### Local Production

```bash
# Use Gunicorn for production (Linux/Mac)
pip install gunicorn
gunicorn dashboard_optimized:server -b 0.0.0.0:8050

# Use Waitress for production (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=8050 dashboard_optimized:server
```

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8050 8001
CMD ["python", "dashboard_optimized.py"]
```

## 🤝 Contributing

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 Python style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes
- Test on multiple Python versions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dash Framework** - For the excellent web application framework
- **Plotly** - For powerful data visualization capabilities
- **Sentence Transformers** - For state-of-the-art NLP models
- **FastAPI** - For high-performance API framework
- **Bootstrap** - For responsive UI components

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YourUsername/CyberSec-Pro-Dashboard/issues)
- **Documentation**: [Wiki](https://github.com/YourUsername/CyberSec-Pro-Dashboard/wiki)
- **Email**: your.email@example.com

---

<div align="center">
  <b>🛡️ Built with ❤️ for Cybersecurity Professionals</b>
</div>

## 🔄 Version History

### v2.0.0 (Latest)
- ✅ Complete UI/UX redesign with professional styling
- ✅ AI-powered chatbot integration
- ✅ Enhanced filtering and analytics
- ✅ Performance optimizations
- ✅ Fixed all duplicate component issues
- ✅ Comprehensive error handling

### v1.0.0
- 🎯 Initial release with basic dashboard functionality
- 📊 Core visualizations and KPI monitoring
- 🔍 Basic filtering capabilities
