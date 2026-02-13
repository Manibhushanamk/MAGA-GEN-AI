from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ConstructionTask(BaseModel):
    id: str
    name: str
    base_duration_per_sqyard: float = Field(..., description="Duration in days per square yard")
    required_workers: int
    cost_per_day: float
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this task depends on")

class ProjectInput(BaseModel):
    area: float = Field(..., description="Total area in square yards")
    floors: int = Field(..., description="Number of floors")
    deadline: int = Field(..., description="Deadline in days")
    budget: float = Field(..., description="Total budget in currency units")
    workforce_cap: int = Field(..., description="Maximum number of workers available per day")
    provider: str = Field(default="gemini", description="LLM Provider: 'gemini' or 'groq'")
    api_key: str = Field(..., description="API Key for the selected provider")


class SimulationResult(BaseModel):
    p50_duration: float
    p80_duration: float
    deadline_risk_probability: float

class CostEstimate(BaseModel):
    labor_cost: float
    material_cost: float
    overhead_cost: float
    total_cost: float
    cost_per_sqyard: float

class ProjectAnalysisResponse(BaseModel):
    deterministic_schedule: Dict[str, Dict[str, int]] = Field(..., description="Task start and end days")
    total_duration: int
    total_cost: CostEstimate
    feasibility_status: str
    optimization_suggestions: List[str]
    simulation_results: SimulationResult
    critical_path_tasks: List[str]
    executive_summary: str = Field(default="", description="AI-generated executive summary")
