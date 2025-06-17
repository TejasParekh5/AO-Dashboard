import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import torch
import requests
import time
import sys
import huggingface_hub
import subprocess
import importlib.util

# Check for required packages


def check_install_package(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"Package '{package_name}' not found. Installing...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name])
            print(f"Successfully installed {package_name}")
            return True
        except Exception as e:
            print(f"Error installing {package_name}: {e}")
            return False
    return True


# Check for required packages
required_packages = ['datasets', 'transformers',
                     'torch', 'sentence-transformers']
missing_packages = []

for package in required_packages:
    if not check_install_package(package):
        missing_packages.append(package)

if missing_packages:
    print(
        f"\nWARNING: Some required packages could not be installed: {', '.join(missing_packages)}")
    print("You may need to install them manually with:")
    print(f"pip install {' '.join(missing_packages)}")

# Set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, 'Cybersecurity_KPI_Minimal.xlsx')
model_output_path = os.path.join(
    current_dir, 'models/fine_tuned_cybersec_model')
# Path for local model cache
model_cache_path = os.path.join(
    current_dir, 'models/cache/paraphrase-MiniLM-L3-v2')

# Make sure the model directory exists
os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
os.makedirs(model_cache_path, exist_ok=True)

# Load data
print(f"Loading data from: {excel_path}")
df = pd.read_excel(excel_path)

# Configure Hugging Face token if available
hf_token = os.environ.get('HF_TOKEN')
if hf_token:
    print("Using Hugging Face token from environment")
    huggingface_hub.login(token=hf_token)

# Function to safely load model with fallback options


def load_model_safely(model_name, local_path=None):
    """Load a model with retry logic and fallback to local cache if available"""
    # First check if we have a local cached version
    if local_path and os.path.exists(local_path) and len(os.listdir(local_path)) > 0:
        print(f"Loading model from local cache: {local_path}")
        try:
            return SentenceTransformer(local_path)
        except Exception as e:
            print(f"Error loading from cache: {e}")
            print("Will try downloading from Hugging Face...")

    # Try downloading with exponential backoff
    max_retries = 5
    base_delay = 1
    for attempt in range(max_retries):
        try:
            print(
                f"Downloading model from Hugging Face (attempt {attempt+1}/{max_retries})...")
            model = SentenceTransformer(model_name)

            # If successful and we have a local path, save for future use
            if local_path:
                print(f"Saving model to local cache: {local_path}")
                model.save(local_path)

            return model
        except Exception as e:
            if "429" in str(e):
                # Rate limit hit, implement exponential backoff
                delay = min(base_delay * (2 ** attempt),
                            60)  # Cap at 60 seconds
                print(
                    f"Rate limit hit. Waiting {delay} seconds before retry...")
                time.sleep(delay)
            else:
                print(f"Error downloading model: {e}")
                if attempt == max_retries - 1:
                    print("All download attempts failed.")
                    raise

    raise Exception("Failed to load model after multiple attempts")

# Create training data: pairs of (context, suggestion) with similarity scores


def create_training_examples():
    # Load the base model we'll fine-tune
    try:
        base_model = load_model_safely(
            'paraphrase-MiniLM-L3-v2', model_cache_path)
    except Exception as e:
        print(f"Critical error: Unable to load the base model: {e}")
        print("\nTIP: You may need to obtain a Hugging Face API token from https://huggingface.co/settings/tokens")
        print("Then set it as an environment variable: HF_TOKEN=your_token_here")
        print("Or try running with the simplified API instead which doesn't require the model.")
        sys.exit(1)

    # Generate contexts for each AO
    train_examples = []

    # Get unique AOs
    aos = df['Application_Owner_ID'].unique()

    for ao_id in aos:
        ao_data = df[df['Application_Owner_ID'] == ao_id]
        ao_name = ao_data['Application_Owner_Name'].iloc[0]

        # Calculate metrics for this AO
        critical_high_count = ao_data['Vulnerability_Severity'].isin(
            ['Critical', 'High']).sum()
        open_vulns = ao_data[ao_data['Status'] == 'Open'].shape[0]
        avg_days_to_close = ao_data['Days_to_Close'].mean()
        high_risk_count = ((ao_data['CVSS_Score'] > 7) | (
            ao_data['Risk_Score'] > 7)).sum()
        repeat_count = ao_data['Number_of_Repeats'].mean()

        # Create context description
        context = f"""
        Application Owner: {ao_id} ({ao_name})
        Applications: {', '.join(ao_data['Application_Name'].unique())}
        Critical/High vulnerabilities: {critical_high_count}
        Open vulnerabilities: {open_vulns}
        Average closure time: {avg_days_to_close:.1f} days
        High risk items: {high_risk_count}
        Repeat issues average: {repeat_count:.1f}
        """

        # Create relevant suggestion pairs with high similarity (1.0)
        if critical_high_count > 3:
            train_examples.append(InputExample(
                texts=[
                    context, f"Focus on addressing the {critical_high_count} high and critical vulnerabilities immediately."],
                label=1.0
            ))

        if open_vulns > 5:
            train_examples.append(InputExample(
                texts=[
                    context, f"You have {open_vulns} open vulnerabilities. Prioritize these for immediate remediation."],
                label=1.0
            ))

        if avg_days_to_close > 30:
            train_examples.append(InputExample(
                texts=[
                    context, f"Your average time to close vulnerabilities is {avg_days_to_close:.1f} days, which is above the 30-day target."],
                label=1.0
            ))

        if high_risk_count > 0:
            train_examples.append(InputExample(
                texts=[
                    context, f"There are {high_risk_count} high-risk items (CVSS or Risk Score > 7) that require urgent attention."],
                label=1.0
            ))

        # Add some non-relevant suggestions with low similarity (0.0-0.3)
        if critical_high_count == 0:
            train_examples.append(InputExample(
                texts=[
                    context, "Focus on addressing the critical and high vulnerabilities immediately."],
                label=0.2
            ))

        # Add medium similarity examples (0.5-0.7)
        train_examples.append(InputExample(
            texts=[
                context, "Regular security training for your team could help reduce vulnerability introduction."],
            label=0.6
        ))

    return train_examples


# Create the training data
print("Creating training examples...")
train_examples = create_training_examples()
print(f"Created {len(train_examples)} training examples")

# Fine-tune the model


def train_model():
    # Load the base model with our safe loading function
    try:
        print("Loading base model for training...")
        model = load_model_safely('paraphrase-MiniLM-L3-v2', model_cache_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Unable to continue with training.")
        return False

    # Create data loader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

    # Use cosine similarity loss
    train_loss = losses.CosineSimilarityLoss(model)

    # Train the model
    print("Training model...")
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=10,
        warmup_steps=100,
        show_progress_bar=True
    )

    # Save the fine-tuned model
    model.save(model_output_path)
    print(f"Model saved to {model_output_path}")


if __name__ == "__main__":
    # Check if CUDA is available for GPU training
    if torch.cuda.is_available():
        print("Training on GPU")
    else:
        print("Training on CPU")

    try:
        success = train_model()
        if success is not False:  # Only show success if we didn't have an explicit failure
            print("Training complete!")
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
    except ModuleNotFoundError as e:
        missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
        print(f"\nMissing required module: {missing_module}")
        print(f"\nPlease install it with:")
        print(f"pip install {missing_module}")
        print("\nOr run the setup_and_train.bat script to install all dependencies automatically.")
    except Exception as e:
        print(f"\nError during training: {e}")
        print("\nIf you're encountering rate limit issues with Hugging Face:")
        print("1. Obtain a token from https://huggingface.co/settings/tokens")
        print("2. Set it as an environment variable before running:")
        print("   $env:HF_TOKEN='your_token_here'  # PowerShell")
        print("   set HF_TOKEN=your_token_here     # CMD")
        print("\nIf you're missing dependencies, run:")
        print("pip install -r requirements_enhanced.txt")
        print("\nAlternatively, you can use the simplified dashboard which doesn't require the model:")
        print("1. Install simplified requirements: pip install -r simple_requirements.txt")
        print("2. Run the simplified dashboard: .\\start_simple_dashboard.bat")
