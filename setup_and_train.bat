@echo off
echo Cybersecurity KPI Dashboard - Model Training Setup
echo =====================================================
echo.
echo This script will install all required dependencies for model training
echo and then start the training process.
echo.
echo Installing dependencies...
pip install -r requirements_enhanced.txt
echo.
echo Running model training...
python train_model.py
echo.
pause
