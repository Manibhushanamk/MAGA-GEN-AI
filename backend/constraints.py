from typing import List, Dict
from backend.models import ProjectInput

class ConstraintEngine:
    def check_feasibility(
        self, 
        schedule: Dict[str, Dict[str, int]], 
        total_cost: float, 
        project_input: ProjectInput,
        tasks_dict: Dict  # Added to access task details for workforce check
    ) -> Dict:
        """
        Checks feasibility against constraints:
        1. Deadline
        2. Budget
        3. Workforce Cap (Daily)
        """
        issues = []
        suggestions = []

        # 1. Budget Check
        if total_cost > project_input.budget:
            overage = total_cost - project_input.budget
            issues.append(f"Budget exceeded by {overage:,.2f}")
            suggestions.append(f"Increase budget by {overage:,.2f} or reduce project scope.")
        
        # 2. Deadline Check
        max_end_date = max((t['end'] for t in schedule.values()), default=0)
        if max_end_date > project_input.deadline:
            delay = max_end_date - project_input.deadline
            issues.append(f"Deadline exceeded by {delay} days.")
            suggestions.append(f"Reduce critical path duration by {delay} days or extend deadline.")

        # 3. Workforce Cap Check (Daily)
        # Build day-by-day usage profile
        daily_usage = {}
        for task_id, timing in schedule.items():
            start, end = timing['start'], timing['end']
            if task_id in tasks_dict:
                required = tasks_dict[task_id].required_workers
                for day in range(start, end):
                    daily_usage[day] = daily_usage.get(day, 0) + required
        
        # Check for violations
        max_workers_needed = 0
        violation_days = 0
        for day, usage in daily_usage.items():
            if usage > max_workers_needed:
                max_workers_needed = usage
            if usage > project_input.workforce_cap:
                violation_days += 1
        
        if violation_days > 0:
            issues.append(f"Workforce cap ({project_input.workforce_cap}) exceeded on {violation_days} days. Peak demand: {max_workers_needed} workers.")
            suggestions.append(f"Increase workforce cap to at least {max_workers_needed} or reschedule non-critical tasks.")

        return {
            "feasible": len(issues) == 0,
            "issues": issues,
            "suggestions": list(set(suggestions)) # Dedup
        }
