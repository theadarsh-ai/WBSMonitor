"""
Azure AI Client - Shared LLM interface for all agents.
Provides unified access to Azure OpenAI for intelligent decision-making.
"""
import os
from typing import List, Dict, Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import config


class AzureAIClient:
    """Shared Azure OpenAI client for all agents."""
    
    def __init__(self):
        """Initialize Azure OpenAI client with credentials from config."""
        self.llm = None
        
        if config.AZURE_INFERENCE_CREDENTIAL and config.AZURE_INFERENCE_ENDPOINT:
            try:
                self.llm = AzureChatOpenAI(
                    azure_endpoint=config.AZURE_INFERENCE_ENDPOINT,
                    api_key=config.AZURE_INFERENCE_CREDENTIAL,
                    api_version=config.AZURE_API_VERSION or "2024-02-15-preview",
                    deployment_name=config.AZURE_DEPLOYMENT_NAME or "gpt-4",
                    temperature=0.7,
                    max_tokens=2000
                )
                print("✓ Azure AI client initialized successfully")
            except Exception as e:
                print(f"⚠️ Azure AI initialization failed: {e}")
                self.llm = None
        else:
            print("⚠️ Azure AI credentials not configured")
    
    def is_available(self) -> bool:
        """Check if AI client is available."""
        return self.llm is not None
    
    def generate_response(self, system_prompt: str, user_message: str) -> Optional[str]:
        """
        Generate AI response with system and user messages.
        
        Args:
            system_prompt: System instructions for the AI
            user_message: User query or context
            
        Returns:
            AI-generated response or None if unavailable
        """
        if not self.is_available():
            return None
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"⚠️ Azure AI error: {e}")
            return None
    
    def analyze_tasks(self, tasks: List[Dict], analysis_type: str) -> Optional[str]:
        """
        Analyze tasks using AI for various purposes.
        
        Args:
            tasks: List of task dictionaries
            analysis_type: Type of analysis (risk, reallocation, prediction, etc.)
            
        Returns:
            AI analysis result
        """
        if not self.is_available():
            return None
        
        task_summary = "\n".join([
            f"- {task['task_name']}: {task.get('completion_percent', 0)}% complete, "
            f"Due: {task.get('end_date', 'N/A')}, Module: {task.get('module', 'N/A')}"
            for task in tasks[:20]  # Limit to 20 tasks to avoid token limits
        ])
        
        system_prompts = {
            "risk": "You are an expert project risk analyst. Analyze tasks and identify potential risks beyond basic metrics.",
            "reallocation": "You are an expert resource allocation specialist. Suggest optimal task reassignments.",
            "prediction": "You are an expert project timeline predictor. Forecast realistic completion dates.",
            "email": "You are an expert business communication writer. Create professional, actionable emails."
        }
        
        system_prompt = system_prompts.get(analysis_type, "You are a helpful project management assistant.")
        
        return self.generate_response(system_prompt, task_summary)


# Singleton instance
_ai_client = None

def get_ai_client() -> AzureAIClient:
    """Get singleton AI client instance."""
    global _ai_client
    if _ai_client is None:
        _ai_client = AzureAIClient()
    return _ai_client
