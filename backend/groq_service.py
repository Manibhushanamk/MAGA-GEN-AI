from backend.llm_factory import BaseLLMService
from typing import Dict
from openai import OpenAI

class GroqService(BaseLLMService):
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        self.model = "llama-3.3-70b-versatile"

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
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful construction project assistant."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary with Groq: {str(e)}"
