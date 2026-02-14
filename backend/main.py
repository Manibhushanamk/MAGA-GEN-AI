from fastapi import FastAPI, HTTPException
from backend.models import ProjectInput, ProjectAnalysisResponse, ConstructionTask
from backend.scheduler import Scheduler
from backend.cost_engine import CostEngine
from backend.constraints import ConstraintEngine
from backend.simulation import RiskSimulator
from backend.gemini_service import GeminiService
from backend.config import settings

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# gemini_service = GeminiService() # Removed: Using LLMFactory per request

# Placeholder tasks (as per requirement to define 15 tasks)
# In a real app, these might come from a DB or be passed in the request.
# For this skeleton, we'll define a few key tasks.
DEFAULT_TASKS = [
    ConstructionTask(id="T1", name="Site Clearing & Preparation", base_duration_per_sqyard=0.005, required_workers=4, cost_per_day=400, dependencies=[]),
    ConstructionTask(id="T2", name="Excavation", base_duration_per_sqyard=0.01, required_workers=6, cost_per_day=700, dependencies=["T1"]),
    ConstructionTask(id="T3", name="Foundation Laying", base_duration_per_sqyard=0.02, required_workers=10, cost_per_day=1200, dependencies=["T2"]),
    ConstructionTask(id="T4", name="Plinth Beam & Slab", base_duration_per_sqyard=0.015, required_workers=12, cost_per_day=1400, dependencies=["T3"]),
    ConstructionTask(id="T5", name="Superstructure (Brickwork)", base_duration_per_sqyard=0.03, required_workers=15, cost_per_day=1800, dependencies=["T4"]),
    ConstructionTask(id="T6", name="Roof Slab Casting", base_duration_per_sqyard=0.01, required_workers=20, cost_per_day=2500, dependencies=["T5"]),
    ConstructionTask(id="T7", name="Door & Window Frames", base_duration_per_sqyard=0.008, required_workers=4, cost_per_day=500, dependencies=["T5"]),
    ConstructionTask(id="T8", name="Electrical Conduit Fitting", base_duration_per_sqyard=0.005, required_workers=3, cost_per_day=450, dependencies=["T5"]),
    ConstructionTask(id="T9", name="Plumbing Rough-ins", base_duration_per_sqyard=0.005, required_workers=3, cost_per_day=450, dependencies=["T5"]),
    ConstructionTask(id="T10", name="Internal Plastering", base_duration_per_sqyard=0.015, required_workers=10, cost_per_day=1100, dependencies=["T6", "T7", "T8", "T9"]),
    ConstructionTask(id="T11", name="External Plastering", base_duration_per_sqyard=0.015, required_workers=10, cost_per_day=1200, dependencies=["T6"]),
    ConstructionTask(id="T12", name="Flooring & Tiling", base_duration_per_sqyard=0.02, required_workers=8, cost_per_day=1000, dependencies=["T10"]),
    ConstructionTask(id="T13", name="Painting & Finishing", base_duration_per_sqyard=0.012, required_workers=6, cost_per_day=800, dependencies=["T11", "T12"]),
    ConstructionTask(id="T14", name="Electrical & Plumbing Fixtures", base_duration_per_sqyard=0.005, required_workers=4, cost_per_day=600, dependencies=["T13"]),
    ConstructionTask(id="T15", name="Site Cleanup & Handover", base_duration_per_sqyard=0.003, required_workers=3, cost_per_day=300, dependencies=["T14"]),
]

@app.post("/analyze_project", response_model=ProjectAnalysisResponse)
async def analyze_project(project_input: ProjectInput):
    """
    Analyzes the project feasibility, cost, schedule, and risks.
    """
    # 1. Scheduling
    scheduler = Scheduler(DEFAULT_TASKS)
    schedule = scheduler.calculate_schedule(project_input)
    if not schedule:
        raise HTTPException(status_code=400, detail="Unable to calculate schedule (possible cycle)")
    
    total_duration = scheduler.get_total_duration(schedule)

    # 2. Critical Path
    from backend.critical_path import CriticalPathAnalyzer
    cp_analyzer = CriticalPathAnalyzer(schedule, DEFAULT_TASKS) # tasks param is technically unused by updated CP logic but kept for sig match if needed, or better remove if clean
    # Actually, my previous CP implementation doesn't use the second arg 'tasks' effectively, 
    # but let's stick to the class init signature: __init__(self, schedule: Dict[str, Dict[str, int]], tasks)
    cp_result = cp_analyzer.identify_critical_path()
    critical_path = cp_result.get("critical_path", [])
    task_analytics = cp_result.get("task_analytics", {})

    # 3. Cost
    # 3. Cost
    cost_engine = CostEngine()
    tasks_dict = {t.id: t for t in DEFAULT_TASKS}
    total_cost_estimate = cost_engine.calculate_total_cost(
        schedule,
        tasks_dict,
        project_input
    )
    total_cost = total_cost_estimate.total_cost 

    # 4. Constraints
    constraint_engine = ConstraintEngine()
    feasibility = constraint_engine.check_feasibility(
        schedule, 
        total_cost, 
        project_input,
        tasks_dict
    )

    # 5. Simulation
    risk_simulator = RiskSimulator()
    simulation_results = risk_simulator.run_simulation(DEFAULT_TASKS, project_input)

    # 6. LLM Summary
    project_data = {
        "input_parameters": project_input.dict(),
        "duration": total_duration,
        "cost_breakdown": total_cost_estimate.dict(),
        "feasibility": feasibility,
        "risks": simulation_results.dict(),
        "critical_path": critical_path
    }
    
    try:
        from backend.llm_factory import LLMFactory
        llm_service = LLMFactory.get_service(project_input.provider, project_input.api_key)
        summary = llm_service.generate_summary(project_data)
    except Exception as e:
        summary = f"LLM Summary Validation Failed: {str(e)}"

    return ProjectAnalysisResponse(
        deterministic_schedule=schedule,
        total_duration=total_duration,
        total_cost=total_cost_estimate,
        feasibility_status="Feasible" if feasibility['feasible'] else "Infeasible",
        constraint_issues=feasibility.get("issues", []),
        optimization_suggestions=feasibility.get("suggestions", []),
        simulation_results=simulation_results,
        critical_path_tasks=critical_path,
        executive_summary=summary
    )

@app.get("/")
async def root():
    return {"message": "BuildWise 2.0 Backend is running"}
