"""
Direct Model Integration Module
Replaces API calls with direct model access for better performance and simplicity
"""

import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CyberSecModelIntegration:
    """Direct model integration class for dashboard"""

    def __init__(self, model_path="models/fine_tuned_cybersec_model", data_file="Cybersecurity_KPI_Minimal.xlsx"):
        self.model_path = model_path
        self.data_file = data_file
        self.model = None
        self.df = None
        self.current_date = datetime.datetime(2025, 6, 17)
        self._initialize()

    def _initialize(self):
        """Initialize model and data"""
        try:
            logger.info("Loading cybersecurity model...")
            self.model = SentenceTransformer(self.model_path)
            logger.info("✅ Model loaded successfully")

            logger.info("Loading security data...")
            self.df = pd.read_excel(self.data_file)
            logger.info(f"✅ Data loaded: {len(self.df)} records")

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise

    @lru_cache(maxsize=100)
    def generate_suggestions(self, ao_ids, dept_names=None, max_suggestions=4):
        """Generate AI-powered suggestions for selected Application Owners"""
        try:
            if isinstance(ao_ids, str):
                ao_ids = [ao_ids]
            if isinstance(dept_names, str):
                dept_names = [dept_names] if dept_names else None

            # Filter data
            filtered_df = self.df[self.df['Application_Owner_ID'].isin(ao_ids)]
            if dept_names:
                filtered_df = filtered_df[filtered_df['Dept_Name'].isin(
                    dept_names)]

            suggestions = []

            # Suggestion 1: Critical vulnerabilities analysis
            critical_high = filtered_df[filtered_df['Vulnerability_Severity'].isin([
                                                                                   'Critical', 'High'])]
            if len(critical_high) > 0:
                avg_days = critical_high['Days_Open'].mean()
                suggestions.append({
                    "priority": "High",
                    "title": "Critical Vulnerability Management",
                    "description": f"You have {len(critical_high)} critical/high vulnerabilities with an average of {avg_days:.1f} days open. Prioritize immediate attention.",
                    "action": "Review and patch critical vulnerabilities within 24-48 hours",
                    "impact": "High security risk reduction"
                })

            # Suggestion 2: Long-running vulnerabilities
            old_vulns = filtered_df[filtered_df['Days_Open'] > 30]
            if len(old_vulns) > 0:
                suggestions.append({
                    "priority": "Medium",
                    "title": "Long-Running Vulnerabilities",
                    "description": f"{len(old_vulns)} vulnerabilities have been open for over 30 days. These require immediate attention.",
                    "action": "Implement vulnerability lifecycle management process",
                    "impact": "Reduced exposure window"
                })

            # Suggestion 3: CVSS score analysis
            high_cvss = filtered_df[filtered_df['CVSS_Score'] > 7.0]
            if len(high_cvss) > 0:
                avg_cvss = high_cvss['CVSS_Score'].mean()
                suggestions.append({
                    "priority": "High",
                    "title": "High CVSS Score Vulnerabilities",
                    "description": f"{len(high_cvss)} vulnerabilities with CVSS > 7.0 (avg: {avg_cvss:.1f}). These represent significant security risks.",
                    "action": "Prioritize patching based on CVSS scores and exploitability",
                    "impact": "Significant risk mitigation"
                })

            # Suggestion 4: Status optimization
            open_status = filtered_df[filtered_df['Status'].isin(
                ['Open', 'In Progress'])]
            if len(open_status) > 0:
                suggestions.append({
                    "priority": "Medium",
                    "title": "Vulnerability Status Optimization",
                    "description": f"{len(open_status)} vulnerabilities are currently open or in progress. Focus on closure workflows.",
                    "action": "Implement tracking and follow-up processes for open vulnerabilities",
                    "impact": "Improved vulnerability management efficiency"
                })

            return suggestions[:max_suggestions]

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return [{
                "priority": "Low",
                "title": "Suggestion Generation Error",
                "description": f"Unable to generate suggestions: {str(e)}",
                "action": "Check data and model configuration",
                "impact": "N/A"
            }]

    def chatbot_response(self, user_message, context_data=None):
        """Generate chatbot response based on user query and dashboard context"""
        try:
            # Basic response patterns based on keywords
            message_lower = user_message.lower()

            # Security best practices
            if any(word in message_lower for word in ['best practice', 'recommend', 'should', 'how to']):
                return self._get_best_practices_response(message_lower)

            # Vulnerability queries
            elif any(word in message_lower for word in ['vulnerability', 'vuln', 'cve', 'patch']):
                return self._get_vulnerability_response(message_lower, context_data)

            # Risk assessment
            elif any(word in message_lower for word in ['risk', 'score', 'cvss', 'severity']):
                return self._get_risk_response(message_lower, context_data)

            # Dashboard help
            elif any(word in message_lower for word in ['dashboard', 'filter', 'chart', 'data']):
                return self._get_dashboard_help_response(message_lower)

            # General security advice
            else:
                return self._get_general_response(message_lower)

        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try rephrasing your question or contact support."

    def _get_best_practices_response(self, message):
        """Generate best practices response"""
        practices = [
            "🔒 Implement a vulnerability management lifecycle with clear SLAs",
            "📊 Prioritize vulnerabilities based on CVSS scores and business impact",
            "⏰ Set target remediation times: Critical (24-48h), High (7 days), Medium (30 days)",
            "🔄 Establish regular vulnerability scanning and assessment schedules",
            "📝 Maintain comprehensive documentation of all security findings",
            "👥 Ensure proper communication between security and development teams"
        ]
        return f"Here are key cybersecurity best practices:\n\n" + "\n".join(practices)

    def _get_vulnerability_response(self, message, context_data):
        """Generate vulnerability-specific response"""
        if context_data and 'filtered_data' in context_data:
            df_filtered = context_data['filtered_data']
            critical_count = len(
                df_filtered[df_filtered['Vulnerability_Severity'] == 'Critical'])
            high_count = len(
                df_filtered[df_filtered['Vulnerability_Severity'] == 'High'])

            return f"Based on your current data:\n\n" \
                   f"🔴 Critical vulnerabilities: {critical_count}\n" \
                   f"🟠 High vulnerabilities: {high_count}\n\n" \
                   f"Recommendation: Focus on critical vulnerabilities first, then address high-severity issues. " \
                   f"Implement automated patching where possible and maintain an asset inventory for tracking."
        else:
            return "Vulnerability management involves identifying, assessing, and mitigating security weaknesses. " \
                   "Key steps include: regular scanning, risk assessment, prioritization, patching, and verification."

    def _get_risk_response(self, message, context_data):
        """Generate risk assessment response"""
        return "Risk assessment should consider:\n\n" \
               "📊 CVSS scores for technical severity\n" \
               "💼 Business impact and asset criticality\n" \
               "🎯 Threat landscape and exploit availability\n" \
               "🛡️ Existing security controls and mitigations\n\n" \
               "Use a risk matrix to prioritize remediation efforts effectively."

    def _get_dashboard_help_response(self, message):
        """Generate dashboard help response"""
        return "Dashboard Help:\n\n" \
               "🎛️ Use filters to focus on specific Application Owners or Departments\n" \
               "📊 Charts update automatically based on your filter selections\n" \
               "💡 AI Insights provide personalized recommendations\n" \
               "📥 Export functionality allows you to download data as CSV or PDF\n" \
               "🔄 Refresh buttons update data and suggestions\n\n" \
               "Navigate through different sections to explore your security metrics!"

    def _get_general_response(self, message):
        """Generate general security response"""
        return "I'm your cybersecurity assistant! I can help you with:\n\n" \
               "🛡️ Security best practices and recommendations\n" \
               "📊 Vulnerability management guidance\n" \
               "🎯 Risk assessment and prioritization\n" \
               "📋 Dashboard navigation and features\n" \
               "💡 Customized insights based on your data\n\n" \
               "Feel free to ask about any specific security topics or dashboard features!"


# Create global instance
cybersec_model = None


def get_model_instance():
    """Get or create model instance (singleton pattern)"""
    global cybersec_model
    if cybersec_model is None:
        cybersec_model = CyberSecModelIntegration()
    return cybersec_model


def generate_suggestions_direct(ao_ids, dept_names=None):
    """Direct function to generate suggestions (replaces API call)"""
    model = get_model_instance()
    return model.generate_suggestions(ao_ids, dept_names)


def chatbot_response_direct(user_message, context_data=None):
    """Direct function for chatbot (replaces API call)"""
    model = get_model_instance()
    return model.chatbot_response(user_message, context_data)
