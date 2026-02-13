from backend.llm_factory import BaseLLMService
from typing import Dict
import google.generativeai as genai

class GeminiService(BaseLLMService):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_summary(self, project_data: Dict) -> str:
        prompt = f"""
        You are a construction project management expert. Analyze the following project data and provide an executive summary.
        
        Project Data:
        {project_data}
        
        Your summary should include:
        1. Feasibility Assessment
        2. Key Risks Analysis
        3. Strategic Optimization Recommendations
        
        Keep it professional, concise, and actionable.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            try:
                available = [m.name for m in genai.list_models()]
                return f"Error: {str(e)}. Available models for your key: {available}"
            except Exception as list_error:
                return f"Error generating summary with Gemini: {str(e)}. Could not list models: {str(list_error)}"
