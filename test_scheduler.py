from backend.models import ConstructionTask, ProjectInput
from backend.scheduler import Scheduler
import json

def test_scheduler():
    # Define tasks (subset of main.py for easier manual verification)
    tasks = [
        ConstructionTask(id="T1", name="Task 1", base_duration_per_sqyard=0.01, required_workers=5, cost_per_day=500, dependencies=[]),
        ConstructionTask(id="T2", name="Task 2", base_duration_per_sqyard=0.02, required_workers=5, cost_per_day=500, dependencies=["T1"]),
        ConstructionTask(id="T3", name="Task 3", base_duration_per_sqyard=0.01, required_workers=5, cost_per_day=500, dependencies=["T1"]),
        ConstructionTask(id="T4", name="Task 4", base_duration_per_sqyard=0.02, required_workers=5, cost_per_day=500, dependencies=["T2", "T3"]),
    ]

    # Project Input (1000 sq yards)
    # T1 duration = 0.01 * 1000 = 10 days
    # T2 duration = 0.02 * 1000 = 20 days
    # T3 duration = 0.01 * 1000 = 10 days
    # T4 duration = 0.02 * 1000 = 20 days
    
    # Expected Schedule:
    # T1: Start 0, End 10 (Duration 10)
    # T2: Start 10, End 30 (Duration 20) (Dep T1)
    # T3: Start 10, End 20 (Duration 10) (Dep T1)
    # T4: Start 30, End 50 (Duration 20) (Dep T2(end 30), T3(end 20) -> Max is 30)

    project_input = ProjectInput(area=1000, floors=1, deadline=100, budget=100000, workforce_cap=20)
    
    scheduler = Scheduler(tasks)
    schedule = scheduler.calculate_schedule(project_input)
    
    with open('test_result.json', 'w') as f:
        json.dump(schedule, f, indent=2)
    
    # Assertions
    assert schedule['T1']['start'] == 0
    assert schedule['T1']['end'] == 10
    assert schedule['T2']['start'] == 10
    assert schedule['T2']['end'] == 30
    assert schedule['T3']['start'] == 10
    assert schedule['T3']['end'] == 20
    assert schedule['T4']['start'] == 30
    assert schedule['T4']['end'] == 50
    
    with open('test_status.txt', 'w') as f:
        f.write("Verification Successful!")

if __name__ == "__main__":
    test_scheduler()
