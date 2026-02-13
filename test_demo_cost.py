from backend.models import ConstructionTask, ProjectInput, CostEstimate
from backend.cost_engine import CostEngine
import json

def test_demo_cost():
    # Setup
    tasks = {
        "T1": ConstructionTask(id="T1", name="Task 1", base_duration_per_sqyard=0.01, required_workers=5, cost_per_day=100, dependencies=[]),
        "T2": ConstructionTask(id="T2", name="Task 2", base_duration_per_sqyard=0.02, required_workers=5, cost_per_day=200, dependencies=["T1"]),
    }
    
    # Schedule: T1 (10 days), T2 (20 days)
    schedule = {
        "T1": {"start": 0, "end": 10},
        "T2": {"start": 10, "end": 30}
    }
    
    project_input = ProjectInput(
        area=1000, floors=1, deadline=100, budget=1000000, workforce_cap=20, 
        api_key="test", provider="gemini"
    )
    
    # Execution
    engine = CostEngine()
    estimate = engine.calculate_total_cost(schedule, tasks, project_input)
    
    print(json.dumps(estimate.dict(), indent=2))
    
    # Verification
    # Labor: 
    # T1: 10 * 100 = 1000
    # T2: 20 * 200 = 4000
    # Total Labor = 5000
    
    # Material:
    # 1000 * 1 * 500 = 500,000
    
    # Overhead:
    # 0.10 * (5000 + 500,000) = 50,500
    
    # Total:
    # 5,000 + 500,000 + 50,500 = 555,500
    
    assert estimate.labor_cost == 5000
    assert estimate.material_cost == 500000
    assert estimate.overhead_cost == 50500
    assert estimate.total_cost == 555500
    
    with open("demo_cost_status.txt", "w") as f:
        f.write("Demo Cost Verification Successful!")

if __name__ == "__main__":
    test_demo_cost()
