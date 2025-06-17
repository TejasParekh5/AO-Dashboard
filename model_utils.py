import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch


def load_model():
    """
    Load the model - either fine-tuned if available or the default pre-trained model
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fine_tuned_model_path = os.path.join(
        current_dir, 'models/fine_tuned_cybersec_model')

    # Check if fine-tuned model exists
    if os.path.exists(fine_tuned_model_path):
        print(f"Loading fine-tuned model from {fine_tuned_model_path}")
        try:
            model = SentenceTransformer(fine_tuned_model_path)
            return model
        except Exception as e:
            print(f"Error loading fine-tuned model: {e}")
            print("Falling back to pre-trained model")

    # Load pre-trained model
    print("Loading pre-trained model (paraphrase-MiniLM-L3-v2)")
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    return model


def evaluate_model_performance(model, test_contexts, test_suggestions):
    """
    Evaluate model performance on test data
    """
    context_embeddings = model.encode(test_contexts)
    suggestion_embeddings = model.encode(test_suggestions)

    # Calculate similarities
    similarities = cosine_similarity(context_embeddings, suggestion_embeddings)

    # Print results
    print("\nModel Evaluation Results:")
    print("-" * 50)
    for i, context in enumerate(test_contexts):
        print(f"Context {i+1}: {context[:100]}...")
        for j, suggestion in enumerate(test_suggestions):
            print(f"  Suggestion {j+1}: {suggestion}")
            print(f"    Similarity: {similarities[i][j]:.4f}")
        print()

    return similarities


if __name__ == "__main__":
    # Check if GPU is available
    if torch.cuda.is_available():
        print("CUDA is available. Using GPU.")
    else:
        print("CUDA is not available. Using CPU.")

    # Load the model
    model = load_model()

    # Test contexts
    test_contexts = [
        "Application Owner: AO_001 (Alice Singh), Critical/High vulnerabilities: 5, Open vulnerabilities: 8, Days to close: 35",
        "Application Owner: AO_002 (Priya Kapoor), Critical/High vulnerabilities: 0, Open vulnerabilities: 2, Days to close: 15"
    ]

    # Test suggestions
    test_suggestions = [
        "Focus on addressing the high and critical vulnerabilities immediately.",
        "Your vulnerability management process is performing well, keep up the good work.",
        "Consider implementing automated scanning to identify vulnerabilities earlier."
    ]

    # Evaluate
    evaluate_model_performance(model, test_contexts, test_suggestions)

    print("\nYou can now use this model in the suggestion_api.py by updating the model loading code.")
    print("Modify suggestion_api.py to use the fine-tuned model by changing the model loading part.")
    print("\nExample code to replace in suggestion_api.py:")
    print("```python")
    print("from model_utils import load_model")
    print("# Load the sentence transformer model")
    print("try:")
    print("    model = load_model()")
    print("    print(\"Loaded model for suggestions\")")
    print("except Exception as e:")
    print("    print(f\"Error loading model: {e}\")")
    print("    model = None")
    print("```")
