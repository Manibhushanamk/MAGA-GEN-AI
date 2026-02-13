from backend.models import ConstructionTask, ProjectInput
from backend.scheduler import Scheduler
from backend.critical_path import CriticalPathAnalyzer
import json

def test_critical_path():
    # Diamond Graph: T1 -> T2, T3 -> T4
    # T1: 10 days
    # T2: 20 days (Critical Path)
    # T3: 10 days
    # T4: 20 days
    
    tasks = [
        ConstructionTask(id="T1", name="Task 1", base_duration_per_sqyard=0.01, required_workers=5, cost_per_day=500, dependencies=[]),
        ConstructionTask(id="T2", name="Task 2", base_duration_per_sqyard=0.02, required_workers=5, cost_per_day=500, dependencies=["T1"]),
        ConstructionTask(id="T3", name="Task 3", base_duration_per_sqyard=0.01, required_workers=5, cost_per_day=500, dependencies=["T1"]),
        ConstructionTask(id="T4", name="Task 4", base_duration_per_sqyard=0.02, required_workers=5, cost_per_day=500, dependencies=["T2", "T3"]),
    ]
    
    project_input = ProjectInput(area=1000, floors=1, deadline=100, budget=100000, workforce_cap=20, api_key="test", provider="gemini")
    
    # 1. Schedule
    scheduler = Scheduler(tasks)
    schedule = scheduler.calculate_schedule(project_input)
    
    # 2. Critical Path
    cp_analyzer = CriticalPathAnalyzer(schedule, tasks)
    result = cp_analyzer.identify_critical_path()
    
    cp = result['critical_path']
    analytics = result['task_analytics']
    
    with open('cp_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    # Verification
    # Path 1: T1(10) + T2(20) + T4(20) = 50
    # Path 2: T1(10) + T3(10) + T4(20) = 40
    # Critical Path should be T1, T2, T4. T3 has 10 days slack.
    
    print("Critical Path:", cp)
    print("T2 Slack:", analytics['T2']['slack'])
    print("T3 Slack:", analytics['T3']['slack'])

    assert "T1" in cp
    assert "T2" in cp
    assert "T4" in cp
    assert "T3" not in cp
    
    assert analytics['T2']['slack'] == 0
    assert analytics['T3']['slack'] == 10
    
    with open('cp_status.txt', 'w') as f:
        f.write("CPM Verification Successful!")

if __name__ == "__main__":
    test_critical_path()
