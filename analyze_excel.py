import pandas as pd
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the Excel file
excel_path = os.path.join(current_dir, 'Cybersecurity_KPI_Minimal.xlsx')

# Read the Excel file
print(f"Reading Excel file: {excel_path}")
try:
    # List all sheets in the Excel file
    xls = pd.ExcelFile(excel_path)
    sheets = xls.sheet_names
    print(f"Sheets in the Excel file: {sheets}")

    # Analyze each sheet
    for sheet in sheets:
        print(f"\n=== Analysis of sheet: {sheet} ===")
        df = pd.read_excel(excel_path, sheet_name=sheet)

        # Display basic information
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")

        # Display first few rows
        print("\nSample data:")
        print(df.head())

        # Check for null values
        null_counts = df.isnull().sum()
        print("\nNull value counts:")
        print(null_counts[null_counts > 0] if any(
            null_counts > 0) else "No null values")

        # Basic statistics for numeric columns
        print("\nBasic statistics for numeric columns:")
        print(df.describe().T)

        # Check unique values for categorical columns
        print("\nUnique values for selected columns:")
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].nunique() < 10:
                print(f"{col}: {df[col].nunique()} unique values")
                if df[col].nunique() < 20:  # Only show if not too many unique values
                    print(f"    Values: {df[col].unique()}")

except Exception as e:
    print(f"Error reading Excel file: {e}")
