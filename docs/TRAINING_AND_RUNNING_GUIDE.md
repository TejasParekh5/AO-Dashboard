# Training and Running Guide

# Cybersecurity KPI Dashboard with Smart Suggestion System

This guide will walk you through the process of training the model and running the dashboard.

## Step 1: Install Requirements

First, make sure all required packages are installed:

```bash
pip install -r requirements_enhanced.txt
```

## Step 2: Train the Model (Optional)

You can use the pre-trained Sentence Transformer model or fine-tune it with your cybersecurity data:

```bash
# Run the training script
python train_model.py
```

This will:

1. Load your cybersecurity data from the Excel file
2. Create training examples based on AO contexts and appropriate suggestions
3. Fine-tune the Sentence Transformer model
4. Save the model to the 'models/fine_tuned_cybersec_model' directory

Training takes about 15-30 minutes depending on your hardware. GPU acceleration is used if available.

## Step 3: Test the Model (Optional)

To verify the model's performance:

```bash
# Test model performance
python model_utils.py
```

This will:

1. Load either your fine-tuned model (if available) or the pre-trained model
2. Run sample predictions on test contexts
3. Show how to integrate the model with the suggestion API

## Step 4: Modify the Suggestion API (Optional)

If you've trained a custom model, update the suggestion_api.py file to use it:

1. Open suggestion_api.py
2. Find the model loading section
3. Replace it with the code to use your fine-tuned model (as shown in model_utils.py output)

## Step 5: Start the Suggestion API

Start the suggestion API service:

```bash
# Start the API
python suggestion_api.py
```

This will:

1. Load your data from the Excel file
2. Load the model (fine-tuned or pre-trained)
3. Start a FastAPI server on port 8000

Keep this running in its own terminal window.

## Step 6: Start the Dashboard

In a new terminal, start the Dash dashboard:

```bash
# Start the dashboard
python enhanced_dashboard.py
```

This will:

1. Load your data from the Excel file
2. Connect to the suggestion API
3. Start a Dash web server on port 8050

## Step 7: Access the Dashboard

Open your web browser and navigate to:
http://127.0.0.1:8050/

You should now see the interactive dashboard. To use the dashboard:

1. Select one or more Application Owners from the dropdown
2. The departments will auto-populate based on your selection
3. Click "Apply Filters" to update the dashboard
4. Click "Refresh Suggestions" to get AI-powered recommendations
5. Explore the various visualizations and data tables
6. Use the export buttons to download data as needed

## Using the Start Script (Alternative)

For convenience, you can use the provided start script to launch both services:

```bash
# Windows Command Prompt
start_enhanced_dashboard.bat

# Windows PowerShell
.\start_enhanced_dashboard.bat

# Unix/Linux
./start_enhanced_dashboard.sh
```

## Troubleshooting

1. **Suggestion API not connecting**

   - Ensure the suggestion API is running (port 8000)
   - Check for error messages in the API terminal

2. **Model loading errors**

   - Verify the model path is correct
   - Ensure you have sufficient disk space

3. **Dashboard not displaying data**

   - Verify the Excel file is in the correct location
   - Check for error messages in the dashboard terminal

4. **Slow performance**

   - Consider using a smaller dataset for testing
   - Close other resource-intensive applications

5. **Script execution issues in PowerShell**

   - If you get "not recognized as the name of a cmdlet" when running scripts, use `.\` before the filename
   - Example: Use `.\start_enhanced_dashboard.bat` instead of `start_enhanced_dashboard.bat`
   - This is because PowerShell doesn't execute scripts from the current directory by default for security reasons

6. **Format errors in DataTable**

   - If you see errors like "invalid format: .1f%", it means Dash doesn't support that format specifier
   - For percentage columns, use 'type': 'text' and format the values manually before displaying
   - Example fix: Change `'format': {'specifier': '.1f%'}` to `'type': 'text'` and format data with `f"{value:.1f}%"`

7. **Serialization errors with NumPy types**

   - If you see errors like "PydanticSerializationError: Unable to serialize unknown type: <class 'numpy.int64'>", it means FastAPI cannot automatically serialize NumPy data types
   - Add proper conversion by using `.item()` method on NumPy values before returning them from API endpoints
   - Example fix: `metrics["value"] = metrics["value"].item() # Convert numpy.int64 to int`

8. **Dependency issues with sentence-transformers**
   - If you encounter errors loading sentence-transformers or its dependencies (PyTorch, etc.)
   - Make sure you've installed all requirements with `pip install -r requirements_enhanced.txt`
   - Check that your Python environment has sufficient permissions to install packages

## Advanced Customization

### Customizing Suggestions

To add or modify suggestion templates:

1. Open suggestion_api.py
2. Find the `suggestion_templates` list
3. Add or modify the templates and their priority conditions

### Modifying Visualizations

To customize the dashboard visualizations:

1. Open enhanced_dashboard.py
2. Find the relevant callback function (e.g., `update_dashboard`)
3. Modify the figure creation code as needed
