import pandas as pd

# Load the dataset
file_path = 'Cybersecurity_KPI_Minimal.xlsx'
try:
    df = pd.read_excel(file_path)
    print("Dataset loaded successfully.")
    print("Columns:", df.columns)
    print("Sample Data:")
    print(df.head())

    # Display unique Application Owner IDs
    print("Unique Application Owner IDs:")
    print(df['Application_Owner_ID'].unique())
except Exception as e:
    print(f"Error loading dataset: {e}")
