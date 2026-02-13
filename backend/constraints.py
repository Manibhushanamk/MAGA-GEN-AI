from typing import List, Dict
from backend.models import ProjectInput

class ConstraintEngine:
    def check_feasibility(self, schedule: Dict[str, Dict[str, int]], total_cost: float, project_input: ProjectInput) -> Dict:
        """
        Checks if the schedule and cost meet the project constraints (deadline, budget, workforce).
        TODO: Implement logic to compare against deadlines and budget.
        """
        issues = []
        if total_cost > project_input.budget:
            issues.append("Project exceeds budget.")
        
        # specific deadline check placeholder
        max_end_date = max((t['end'] for t in schedule.values()), default=0)
        if max_end_date > project_input.deadline:
            issues.append("Project exceeds deadline.")

        return {
            "feasible": len(issues) == 0,
            "issues": issues,
            "suggestions": ["Increase budget", "Add more workers"] if issues else []
        }
