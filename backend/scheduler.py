from typing import List, Dict
from backend.models import ConstructionTask, ProjectInput
import networkx as nx

class Scheduler:
    def __init__(self, tasks: List[ConstructionTask]):
        self.tasks = {t.id: t for t in tasks}
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        for task_id, task in self.tasks.items():
            self.graph.add_node(task_id, duration=task.base_duration_per_sqyard) # Placeholder duration
            for dep in task.dependencies:
                if dep in self.tasks:
                    self.graph.add_edge(dep, task_id)

    def calculate_schedule(self, project_input: ProjectInput) -> Dict[str, Dict[str, int]]:
        """
        Calculates the start and end dates for each task using Forward Pass (CPM).
        Returns a dictionary mapping task_id to {'start': day, 'end': day}.
        """
        schedule = {}
        
        # 1. Calculate Durations
        # Use simple ceiling to ensure whole days. 
        # For very small tasks, minimum duration is 1 day.
        import math
        task_durations = {}
        for task_id, task in self.tasks.items():
            duration = math.ceil(task.base_duration_per_sqyard * project_input.area)
            task_durations[task_id] = max(1, int(duration))

        # 2. Cycle Detection
        if not nx.is_directed_acyclic_graph(self.graph):
            print("Cycle detected in dependencies") # Log error
            return {}

        # 3. Forward Pass (Earliest Start / Earliest Finish)
        # Initialize ES and EF for all nodes
        earliest_start = {node: 0 for node in self.graph.nodes()}
        earliest_finish = {node: 0 for node in self.graph.nodes()}

        try:
            sorted_tasks = list(nx.topological_sort(self.graph))
            
            for task_id in sorted_tasks:
                # ES is max of predecessor EFs
                predecessors = list(self.graph.predecessors(task_id))
                if predecessors:
                    es = max(earliest_finish[p] for p in predecessors)
                else:
                    es = 0
                
                duration = task_durations.get(task_id, 1)
                ef = es + duration
                
                earliest_start[task_id] = es
                earliest_finish[task_id] = ef
                
                schedule[task_id] = {'start': es, 'end': ef}
                
        except nx.NetworkXUnfeasible:
            return {}
        
        return schedule

    def get_total_duration(self, schedule: Dict[str, Dict[str, int]]) -> int:
        if not schedule:
            return 0
        return max(task['end'] for task in schedule.values())
