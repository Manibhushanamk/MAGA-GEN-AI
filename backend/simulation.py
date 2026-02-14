import numpy as np
import networkx as nx
import math
from typing import Dict, List
from backend.models import SimulationResult, ProjectInput, ConstructionTask

class RiskSimulator:
    def run_simulation(
        self, 
        tasks: List[ConstructionTask],
        project_input: ProjectInput,
        num_simulations: int = 500
    ) -> SimulationResult:
        """
        Runs Monte Carlo simulations to estimate project duration risk.
        Logic:
        1. Build graph structure.
        2. Calculate base durations.
        3. For N runs: vary durations (0.85-1.15) and compute critical path length.
        4. Calculate P50, P80, and Risk Probability.
        """
        # 1. Build Graph & Base Durations
        graph = nx.DiGraph()
        base_durations = {}
        
        for task in tasks:
            # Calculate deterministic duration (matching Scheduler logic)
            duration = math.ceil(task.base_duration_per_sqyard * project_input.area)
            base_durations[task.id] = max(1, int(duration))
            graph.add_node(task.id)
            for dep in task.dependencies:
                graph.add_edge(dep, task.id)
        
        # Safety check for cycles
        if not nx.is_directed_acyclic_graph(graph):
            return SimulationResult(
                p50_duration=0, p80_duration=0, deadline_risk_probability=100.0
            )

        # Pre-compute topological order for fast iteration
        topo_order = list(nx.topological_sort(graph))
        
        simulated_durations = []
        
        # 2. Run Simulations
        for _ in range(num_simulations):
            # Sample durations for this run
            run_durations = {}
            for t_id, base in base_durations.items():
                variation = np.random.uniform(0.85, 1.15)
                run_durations[t_id] = base * variation
            
            # Forward Pass to find Total Duration
            dataset_ef = {node: 0.0 for node in graph.nodes()}
            
            for task_id in topo_order:
                predecessors = list(graph.predecessors(task_id))
                if predecessors:
                    es = max(dataset_ef[p] for p in predecessors)
                else:
                    es = 0.0
                
                dataset_ef[task_id] = es + run_durations[task_id]
            
            project_duration = max(dataset_ef.values(), default=0)
            simulated_durations.append(project_duration)
            
        # 3. Analyze Results
        p50 = np.percentile(simulated_durations, 50)
        p80 = np.percentile(simulated_durations, 80)
        
        deadline = project_input.deadline
        risk_count = sum(1 for d in simulated_durations if d > deadline)
        risk_prob = (risk_count / num_simulations) * 100 # Return as percentage
        
        return SimulationResult(
            p50_duration=float(round(p50, 1)), # Round for cleaner JSON
            p80_duration=float(round(p80, 1)),
            deadline_risk_probability=float(round(risk_prob, 1))
        )
