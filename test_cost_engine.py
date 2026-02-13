from backend.models import ConstructionTask, ProjectInput, CostEstimate
from backend.cost_engine import CostEngine
import json

def test_cost_engine():
    # 1. Setup
    tasks = [
        ConstructionTask(id="T1", name="Task 1", base_duration_per_sqyard=0.01, required_workers=5, cost_per_day=500, dependencies=[]),
        ConstructionTask(id="T2", name="Task 2", base_duration_per_sqyard=0.02, required_workers=5, cost_per_day=1000, dependencies=["T1"]),
    ]
    task_map = {t.id: t for t in tasks}
    
    # Schedule (Duration T1=10, T2=20 for 1000 sq yards)
    schedule = {
        "T1": {"start": 0, "end": 10},
        "T2": {"start": 10, "end": 30}
    }
    
    project_input = ProjectInput(
        area=1000, floors=2, deadline=100, budget=1000000, workforce_cap=20, 
        api_key="test", provider="gemini"
    )
    
    # 2. Execution
    engine = CostEngine()
    estimate = engine.calculate_total_cost(schedule, project_input, task_map)
    
    print(json.dumps(estimate.dict(), indent=2))
    
    # 3. Verification
    # Labor: 
    # T1: 10 days * 500 = 5000
    # T2: 20 days * 1000 = 20000
    # Total Labor = 25000
    
    # Material:
    # 1000 (area) * 2 (floors) * 500 (coeff) = 1,000,000
    
    # Overhead:
    # 0.10 * (25000 + 1000000) = 102500
    
    # Total:
    # 25000 + 1000000 + 102500 = 1,127,500
    
    assert estimate.labor_cost == 25000
    assert estimate.material_cost == 1000000
    assert estimate.overhead_cost == 102500
    assert estimate.total_cost == 1127500
    
    # Cost per sqyard = 1127.5
    assert estimate.cost_per_sqyard == 1127.5

    with open('cost_status.txt', 'w') as f:
        f.write("Cost Verification Successful!")

if __name__ == "__main__":
    test_cost_engine()
