from typing import Dict
from backend.models import ProjectInput, ConstructionTask, CostEstimate

class CostEngine:
    """
    Component-Based Cost Engine

    Assumptions:
    - Labor cost is derived from task duration x task.cost_per_day.
    - Material cost is derived from area x floors x material_coefficient.
    - Overhead is fixed at 10% of (labor + material).
    """

    MATERIAL_COEFFICIENT = 500
    OVERHEAD_PERCENTAGE = 0.10

    def calculate_total_cost(
        self,
        schedule: Dict[str, Dict[str, int]],
        tasks: Dict[str, ConstructionTask],
        project_input: ProjectInput
    ) -> CostEstimate:

        total_labor_cost = 0.0

        for task_id, timing in schedule.items():
            if task_id in tasks:
                task = tasks[task_id]
                duration = timing["end"] - timing["start"]
                task_cost = duration * task.cost_per_day
                total_labor_cost += task_cost

        material_cost = (
            project_input.area
            * project_input.floors
            * self.MATERIAL_COEFFICIENT
        )

        overhead_cost = (
            total_labor_cost + material_cost
        ) * self.OVERHEAD_PERCENTAGE

        total_cost = total_labor_cost + material_cost + overhead_cost

        cost_per_sqyard = total_cost / project_input.area if project_input.area > 0 else 0

        return CostEstimate(
            labor_cost=round(total_labor_cost, 2),
            material_cost=round(material_cost, 2),
            overhead_cost=round(overhead_cost, 2),
            total_cost=round(total_cost, 2),
            cost_per_sqyard=round(cost_per_sqyard, 2)
        )
