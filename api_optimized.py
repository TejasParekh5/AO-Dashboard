from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import datetime
import json
import logging
import asyncio
import time
from functools import lru_cache
import hashlib

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set the current date
current_date = datetime.datetime(2025, 6, 17)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="CyberSec Pro API",
    description="Advanced Cybersecurity KPI and AI Suggestion API with ML-powered insights",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add middleware for better performance and security
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8050", "http://localhost:8050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the Excel file
excel_path = os.path.join(current_dir, 'Cybersecurity_KPI_Minimal.xlsx')

# Global variables for caching
_data_cache = None
_model_cache = None
_cache_timestamp = None
CACHE_DURATION = 300  # 5 minutes

@lru_cache(maxsize=128)
def get_data_hash():
    """Get hash of the Excel file for cache invalidation"""
    try:
        with open(excel_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return str(time.time())

def load_data():
    """Load and process data with caching"""
    global _data_cache, _cache_timestamp
    
    current_time = time.time()
    
    # Check if cache is valid
    if (_data_cache is not None and 
        _cache_timestamp is not None and 
        current_time - _cache_timestamp < CACHE_DURATION):
        return _data_cache
    
    logger.info(f"Loading data from: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path)
        
        # Add derived columns for analysis
        df['Days_Open'] = np.where(
            pd.isna(df['Closure_Date']),
            (current_date - pd.to_datetime(df['First_Detected_Date'])).dt.days,
            df['Days_to_Close']
        )
        
        df['Is_Critical_High'] = df['Vulnerability_Severity'].isin(['Critical', 'High'])
        df['Is_Over_30_Days'] = df['Days_Open'] > 30
        df['Is_Critical_High_Over_30'] = df['Is_Critical_High'] & df['Is_Over_30_Days']
        df['Is_High_Risk'] = (df['CVSS_Score'] > 7) | (df['Risk_Score'] > 7)
        
        # Cache the processed data
        _data_cache = df
        _cache_timestamp = current_time
        
        logger.info(f"✅ Data loaded successfully: {len(df)} records")
        return df
        
    except Exception as e:
        logger.error(f"❌ Error loading data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data loading failed: {str(e)}")

def load_model():
    """Load ML model with caching"""
    global _model_cache
    
    if _model_cache is not None:
        return _model_cache
    
    model_path = os.path.join(current_dir, 'models/fine_tuned_cybersec_model')
    
    try:
        logger.info("Loading ML model...")
        model = SentenceTransformer(model_path)
        _model_cache = model
        logger.info("✅ ML model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"❌ Error loading model: {str(e)}")
        return None

# Initialize data and model
df = load_data()
model = load_model()

# Helper function to convert numpy values to Python native types
def convert_numpy_types(obj):
    """Convert numpy types to JSON-serializable Python types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

# Enhanced suggestion templates with improved logic
suggestion_templates = [
    {
        "template": "[CRITICAL] Immediate action required: {critical_high_count} critical/high vulnerabilities need urgent remediation.",
        "priority": "urgent",
        "condition": lambda m: m['critical_high_count'] > 5,
        "weight": 1.0
    },
    {
        "template": "[URGENT] {old_vulns_count} vulnerabilities have been open for over 30 days. This significantly increases risk exposure.",
        "priority": "urgent", 
        "condition": lambda m: m['old_vulns_count'] > 3,
        "weight": 0.9
    },
    {
        "template": "[WARNING] Your average remediation time ({avg_days_to_close:.1f} days) exceeds the department average ({dept_avg:.1f} days).",
        "priority": "medium",
        "condition": lambda m: m['avg_days_to_close'] > m['dept_avg'] + 5,
        "weight": 0.7
    },
    {
        "template": "[URGENT] {high_risk_count} high-risk vulnerabilities (CVSS/Risk Score > 7) require immediate attention.",
        "priority": "urgent",
        "condition": lambda m: m['high_risk_count'] > 1,
        "weight": 0.8
    },
    {
        "template": "[RECOMMENDATION] Review patch management for Application '{worst_app}' - it shows the highest vulnerability exposure.",
        "priority": "medium",
        "condition": lambda m: 'worst_app' in m and m['worst_app'] != 'Unknown',
        "weight": 0.6
    },
    {
        "template": "[OPTIMIZATION] Implement automated vulnerability scanning to reduce detection time and improve security posture.",
        "priority": "medium",
        "condition": lambda m: m['avg_days_to_close'] > 20,
        "weight": 0.5
    },
    {
        "template": "[TRAINING] Security awareness training recommended - repeat vulnerabilities ({repeat_count:.1f}) indicate process gaps.",
        "priority": "medium",
        "condition": lambda m: m['repeat_count'] > 1.5,
        "weight": 0.6
    },
    {
        "template": "[STRATEGIC] Establish vulnerability prioritization framework for {dept_name} department to improve response efficiency.",
        "priority": "medium",
        "condition": lambda m: m['critical_high_count'] > 0,
        "weight": 0.4
    },
    {
        "template": "[EXCELLENCE] Outstanding vulnerability management for Application '{best_app}' - consider replicating these practices.",
        "priority": "good",
        "condition": lambda m: 'best_app' in m,
        "weight": 0.3
    },
    {
        "template": "[SUCCESS] Team performance is above average - continue current remediation practices for sustained security improvements.",
        "priority": "good",
        "condition": lambda m: m['avg_days_to_close'] < 15,
        "weight": 0.2
    }
]

# Define enhanced request and response models
class MetricsRequest(BaseModel):
    ao_id: str = Field(..., description="Application Owner ID")

class SuggestionItem(BaseModel):
    text: str = Field(..., description="Suggestion text")
    priority: str = Field(..., description="Priority level")
    relevance_score: float = Field(..., description="ML-calculated relevance score")
    weight: float = Field(..., description="Template weight")

class SuggestionResponse(BaseModel):
    ao_id: str
    ao_name: str
    suggestions: List[SuggestionItem]
    metrics: Dict[str, Any]
    performance: Dict[str, float]

class ChatbotRequest(BaseModel):
    ao_id: Optional[str] = Field(None, description="Application Owner ID")
    question: str = Field(..., description="User question")

class ChatbotResponse(BaseModel):
    response: str = Field(..., description="Chatbot response text")
    confidence: float = Field(..., description="Response confidence score")
    processing_time: float = Field(..., description="Response processing time")

# Enhanced knowledge base with better coverage
knowledge_base = [
    {
        "question": "How can I improve my risk score?",
        "answer": "Focus on addressing high-risk vulnerabilities with CVSS scores > 7, prioritize critical and high severity issues, and implement regular security assessments.",
        "category": "risk_management"
    },
    {
        "question": "What is my average closure time?",
        "answer": "Your average closure time indicates how quickly you resolve security vulnerabilities. Reducing this time minimizes risk exposure and improves security posture.",
        "category": "performance"
    },
    {
        "question": "How can I reduce vulnerabilities?",
        "answer": "Implement automated scanning, regular security training, proactive patch management, and establish a vulnerability prioritization framework.",
        "category": "prevention"
    },
    {
        "question": "What are critical vulnerabilities?",
        "answer": "Critical vulnerabilities have CVSS scores of 9.0-10.0 and pose immediate threats. They require immediate remediation within 24-72 hours.",
        "category": "severity"
    },
    {
        "question": "How to prioritize vulnerabilities?",
        "answer": "Prioritize by severity (Critical > High > Medium > Low), business impact, asset criticality, and exploit availability. Address critical issues first.",
        "category": "prioritization"
    },
    {
        "question": "What is CVSS score?",
        "answer": "CVSS (Common Vulnerability Scoring System) rates vulnerability severity from 0-10. Scores 9.0-10.0 are Critical, 7.0-8.9 are High, 4.0-6.9 are Medium, 0.1-3.9 are Low.",
        "category": "metrics"
    }
]

@lru_cache(maxsize=64)
def calculate_metrics_for_ao(ao_id: str):
    """Calculate metrics for an AO with caching"""
    df = load_data()
    
    # Filter data for this AO
    ao_data = df[df['Application_Owner_ID'] == ao_id]
    
    if len(ao_data) == 0:
        raise HTTPException(status_code=404, detail=f"No data found for Application Owner {ao_id}")
    
    # Get AO name
    ao_name = ao_data['Application_Owner_Name'].iloc[0]
    
    # Calculate comprehensive metrics
    metrics = {
        'ao_id': ao_id,
        'ao_name': ao_name,
        'critical_high_count': int(ao_data['Is_Critical_High'].sum()),
        'old_vulns_count': int(ao_data['Is_Over_30_Days'].sum()),
        'high_risk_count': int(ao_data['Is_High_Risk'].sum()),
        'avg_days_to_close': float(ao_data['Days_to_Close'].mean()),
        'dept_avg': float(df['Days_to_Close'].mean()),
        'repeat_count': float(ao_data['Number_of_Repeats'].mean()),
        'total_vulnerabilities': len(ao_data),
        'open_vulnerabilities': len(ao_data[ao_data['Status'] == 'Open']),
        'dept_name': ao_data['Dept_Name'].iloc[0] if len(ao_data) > 0 else "Unknown"
    }
    
    # Calculate application-specific metrics
    app_metrics = {}
    for app in ao_data['Application_Name'].unique():
        app_data = ao_data[ao_data['Application_Name'] == app]
        app_metrics[app] = {
            'avg_days': float(app_data['Days_to_Close'].mean()),
            'critical_high': int(app_data['Is_Critical_High'].sum()),
            'high_risk': int(app_data['Is_High_Risk'].sum())
        }
    
    # Find worst and best applications
    if app_metrics:
        worst_app = max(app_metrics, key=lambda x: (
            app_metrics[x]['critical_high'], 
            app_metrics[x]['avg_days']
        ))
        metrics['worst_app'] = worst_app
        
        # Find best app (low issues, fast resolution)
        best_apps = [
            app for app, app_data in app_metrics.items()
            if app_data['critical_high'] == 0 and app_data['avg_days'] < metrics['dept_avg']
        ]
        if best_apps:
            metrics['best_app'] = best_apps[0]
    
    return metrics

async def generate_suggestions_for_ao(ao_id: str):
    """Generate AI-powered suggestions for an Application Owner"""
    start_time = time.time()
    
    try:
        # Get metrics (cached)
        metrics = calculate_metrics_for_ao(ao_id)
        
        # Generate applicable suggestions
        applicable_suggestions = []
        for template_data in suggestion_templates:
            if template_data["condition"](metrics):
                try:
                    formatted_text = template_data["template"].format(**metrics)
                    suggestion = {
                        "text": formatted_text,
                        "priority": template_data["priority"],
                        "weight": template_data["weight"],
                        "relevance_score": 0.0  # Will be calculated if model available
                    }
                    applicable_suggestions.append(suggestion)
                except KeyError as e:
                    logger.warning(f"Missing key in metrics for template: {e}")
                    continue
        
        # Enhance with ML scoring if model is available
        if model and applicable_suggestions:
            # Create context for ML ranking
            ao_context = f"""
            Application Owner: {metrics['ao_id']} ({metrics['ao_name']})
            Department: {metrics['dept_name']}
            Critical/High vulnerabilities: {metrics['critical_high_count']}
            Vulnerabilities > 30 days: {metrics['old_vulns_count']}
            Average closure time: {metrics['avg_days_to_close']:.1f} days
            High risk items: {metrics['high_risk_count']}
            Total vulnerabilities: {metrics['total_vulnerabilities']}
            """
            
            try:
                # Calculate embeddings
                context_embedding = model.encode([ao_context])[0]
                suggestion_texts = [s["text"] for s in applicable_suggestions]
                suggestion_embeddings = model.encode(suggestion_texts)
                
                # Calculate similarity scores
                similarities = cosine_similarity([context_embedding], suggestion_embeddings)[0]
                
                # Update suggestions with ML scores
                for i, suggestion in enumerate(applicable_suggestions):
                    suggestion["relevance_score"] = float(similarities[i])
                
                # Sort by combined score (relevance * weight)
                applicable_suggestions.sort(
                    key=lambda x: x["relevance_score"] * x["weight"], 
                    reverse=True
                )
                
            except Exception as e:
                logger.warning(f"ML scoring failed, using template weights: {e}")
                # Fallback to weight-based sorting
                applicable_suggestions.sort(key=lambda x: x["weight"], reverse=True)
        
        # Prepare response
        performance_metrics = {
            "processing_time": time.time() - start_time,
            "suggestions_generated": len(applicable_suggestions),
            "ml_scoring_enabled": model is not None
        }
        
        result = SuggestionResponse(
            ao_id=metrics['ao_id'],
            ao_name=metrics['ao_name'],
            suggestions=applicable_suggestions[:5],  # Top 5 suggestions
            metrics=convert_numpy_types(metrics),
            performance=performance_metrics
        )
        
        logger.info(f"Generated {len(applicable_suggestions)} suggestions for {ao_id} in {performance_metrics['processing_time']:.3f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error generating suggestions for {ao_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")

# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """API health check and status"""
    return {
        "message": "CyberSec Pro API v2.0 - Advanced Cybersecurity Analytics",
        "status": "operational",
        "timestamp": datetime.datetime.now().isoformat(),
        "features": ["AI Suggestions", "ML-Powered Insights", "Real-time Analytics"],
        "version": "2.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "data_loaded": _data_cache is not None,
        "model_loaded": _model_cache is not None,
        "cache_age": time.time() - _cache_timestamp if _cache_timestamp else None,
        "records_count": len(_data_cache) if _data_cache is not None else 0
    }

@app.get("/suggestions/{ao_id}", response_model=SuggestionResponse, tags=["AI Suggestions"])
async def get_suggestions(ao_id: str):
    """Get AI-powered suggestions for an Application Owner"""
    logger.info(f"📊 Generating suggestions for AO: {ao_id}")
    return await generate_suggestions_for_ao(ao_id)

class MultipleSuggestionsRequest(BaseModel):
    aos: List[Dict[str, Any]] = Field(..., description="List of Application Owner data")

class MultipleSuggestionsResponse(BaseModel):
    suggestions: List[SuggestionItem]
    total_aos: int
    performance: Dict[str, float]

@app.post("/suggestions", response_model=MultipleSuggestionsResponse, tags=["AI Suggestions"])
async def get_multiple_suggestions(request: MultipleSuggestionsRequest):
    """Get AI-powered suggestions for multiple Application Owners"""
    start_time = time.time()
    logger.info(f"📊 Generating suggestions for {len(request.aos)} AOs")
    
    all_suggestions = []
    processed_aos = 0
    
    try:
        for ao_data in request.aos:
            if 'ao_id' in ao_data:
                ao_suggestions = await generate_suggestions_for_ao(ao_data['ao_id'])
                if ao_suggestions and ao_suggestions.suggestions:
                    # Add AO context to each suggestion
                    for suggestion in ao_suggestions.suggestions:
                        suggestion_dict = suggestion.dict() if hasattr(suggestion, 'dict') else suggestion
                        suggestion_dict['ao_id'] = ao_data['ao_id']
                        suggestion_dict['ao_name'] = ao_data.get('ao_name', 'Unknown')
                        all_suggestions.append(SuggestionItem(**suggestion_dict))
                processed_aos += 1
        
        # Sort by relevance score and take top suggestions
        all_suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        top_suggestions = all_suggestions[:10]  # Limit to top 10
        
        processing_time = time.time() - start_time
        
        logger.info(f"Generated {len(top_suggestions)} suggestions from {processed_aos} AOs in {processing_time:.3f}s")
        
        return MultipleSuggestionsResponse(
            suggestions=top_suggestions,
            total_aos=processed_aos,
            performance={
                "processing_time": processing_time,
                "suggestions_generated": len(top_suggestions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating multiple suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@app.get("/aos", tags=["Data"])
async def get_all_aos():
    """Get all Application Owners"""
    df = load_data()
    aos = df[['Application_Owner_ID', 'Application_Owner_Name']].drop_duplicates()
    return {
        "application_owners": convert_numpy_types(aos.to_dict('records')),
        "count": len(aos)
    }

@app.get("/departments", tags=["Data"])
async def get_departments():
    """Get all departments"""
    df = load_data()
    departments = df['Dept_Name'].unique().tolist()
    return {
        "departments": convert_numpy_types(departments),
        "count": len(departments)
    }

@app.get("/applications", tags=["Data"])
async def get_applications(ao_id: Optional[str] = None):
    """Get applications, optionally filtered by AO"""
    df = load_data()
    
    if ao_id:
        apps = df[df['Application_Owner_ID'] == ao_id]['Application_Name'].unique().tolist()
    else:
        apps = df['Application_Name'].unique().tolist()
    
    return {
        "applications": convert_numpy_types(apps),
        "count": len(apps),
        "filtered_by_ao": ao_id
    }

@app.post("/chatbot", response_model=ChatbotResponse, tags=["AI Assistant"])
async def chatbot_query(request: ChatbotRequest):
    """Enhanced AI chatbot for cybersecurity guidance"""
    start_time = time.time()
    
    if model is None:
        logger.error("🤖 Chatbot model unavailable")
        raise HTTPException(status_code=503, detail="AI Assistant temporarily unavailable")
    
    try:
        logger.info(f"🤖 Processing chatbot query: {request.question[:50]}...")
        
        # Generate question embedding
        question_embedding = model.encode([request.question])[0]
        
        best_match = None
        best_score = -1
        
        # Find best matching answer from knowledge base
        for item in knowledge_base:
            answer_embedding = model.encode([item["question"]])[0]
            score = cosine_similarity([question_embedding], [answer_embedding])[0][0]
            
            logger.debug(f"Comparing with: {item['question'][:30]}... Score: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_match = item
        
        response_time = time.time() - start_time
        
        if best_match and best_score > 0.3:  # Minimum threshold
            logger.info(f"✅ Best match found: {best_match['question'][:30]}... (score: {best_score:.3f})")
            return ChatbotResponse(
                response=best_match["answer"],
                confidence=float(best_score),
                processing_time=response_time
            )
        else:
            logger.warning("❓ No relevant answer found")
            return ChatbotResponse(
                response="I'm sorry, I couldn't find a specific answer to your question. For cybersecurity best practices, consider: regular vulnerability assessments, timely patch management, security training, and implementing defense-in-depth strategies.",
                confidence=0.0,
                processing_time=response_time
            )
            
    except Exception as e:
        logger.error(f"❌ Chatbot error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Assistant error: {str(e)}")

@app.get("/analytics/summary", tags=["Analytics"])
async def get_analytics_summary():
    """Get overall analytics summary"""
    df = load_data()
    
    summary = {
        "total_vulnerabilities": len(df),
        "critical_vulnerabilities": len(df[df['Vulnerability_Severity'] == 'Critical']),
        "high_vulnerabilities": len(df[df['Vulnerability_Severity'] == 'High']),
        "open_vulnerabilities": len(df[df['Status'] == 'Open']),
        "average_cvss_score": float(df['CVSS_Score'].mean()),
        "average_risk_score": float(df['Risk_Score'].mean()),
        "average_days_to_close": float(df['Days_to_Close'].mean()),
        "departments_count": len(df['Dept_Name'].unique()),
        "application_owners_count": len(df['Application_Owner_ID'].unique()),
        "applications_count": len(df['Application_Name'].unique())
    }
    
    return convert_numpy_types(summary)

# Serve static files
app.mount("/static", StaticFiles(directory=current_dir), name="static")

@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/assets/favicon.ico")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CyberSec Pro API v2.0 starting up...")
    logger.info(f"📊 Data records: {len(df) if df is not None else 'Not loaded'}")
    logger.info(f"🧠 ML Model: {'Loaded' if model else 'Not available'}")
    logger.info("✅ API ready to serve requests")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 CyberSec Pro API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8001,
        log_level="info",
        access_log=True
    )
