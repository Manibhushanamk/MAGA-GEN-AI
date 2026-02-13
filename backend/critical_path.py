from typing import List, Dict

class CriticalPathAnalyzer:
    def __init__(self, schedule: Dict[str, Dict[str, int]], tasks):
        self.schedule = schedule
        self.tasks = tasks

    def identify_critical_path(self) -> Dict:
        """
        Identifies the critical path tasks using Backward Pass (CPM).
        Returns:
            Dict containing:
            - critical_path: List[str] (Task IDs on the critical path)
            - task_analytics: Dict[str, Dict] (ES, EF, LS, LF, Slack per task)
        """
        import networkx as nx

        # 1. Get Project Duration from Schedule
        if not self.schedule:
            return {"critical_path": [], "task_analytics": {}}

        # Determine project duration (max EF of all tasks)
        project_duration = max((t['end'] for t in self.schedule.values()), default=0)

        # 2. Backward Pass (Late Start / Late Finish)
        late_finish = {node: project_duration for node in self.schedule.keys()}
        late_start = {node: 0 for node in self.schedule.keys()}
        
        # Helper to get task duration consistent with Forward Pass
        def get_duration(task_id):
            return self.schedule[task_id]['end'] - self.schedule[task_id]['start']

        # Traverse in Reverse Topological Order
        try:
            # Re-build simple graph if not provided (though it should be passed)
            # Assuming self.tasks contains dependencies to build graph structure if needed
            # But the 'tasks' argument in init was list of generic objects.
            # Let's rely on the structure implicit in the schedule + dependencies from self.tasks
            
            # Better: We need the graph. Re-verify Scheduler passed tasks properly.
            # We'll rebuild a local lightweight graph for topological sort
            G = nx.DiGraph()
            task_map = {t.id: t for t in self.tasks}
            for t_id in self.schedule.keys():
                G.add_node(t_id)
                if t_id in task_map:
                    for dep in task_map[t_id].dependencies:
                        if dep in self.schedule: # Only add if dependency exists in schedule
                            G.add_edge(dep, t_id)

            reverse_order = list(reversed(list(nx.topological_sort(G))))

            for task_id in reverse_order:
                # LF is min(LS) of successors
                successors = list(G.successors(task_id))
                
                if successors:
                    lf = min(late_start[s] for s in successors)
                else:
                    # If no successors, it connects to end of project
                    lf = project_duration
                
                duration = get_duration(task_id)
                ls = lf - duration
                
                late_finish[task_id] = lf
                late_start[task_id] = ls

        except nx.NetworkXUnfeasible:
            # Should receive DAG, but safety first
            return {"critical_path": [], "task_analytics": {}}

        # 3. Calculate Slack & Identify Critical Path
        critical_path = []
        task_analytics = {}

        for task_id in self.schedule.keys():
            es = self.schedule[task_id]['start']
            ef = self.schedule[task_id]['end']
            ls = late_start[task_id]
            lf = late_finish[task_id]
            
            slack = ls - es
            
            # Log logic error if negative slack (rounding tolerance acceptable but pure int math shouldn't drift)
            if slack < 0:
                print(f"WARNING: Negative slack detected for {task_id}: {slack}")
            
            # Critical Loop: Slack == 0 (or close to 0 if we used floats)
            is_critical = slack == 0
            if is_critical:
                critical_path.append(task_id)
            
            task_analytics[task_id] = {
                "es": es, "ef": ef,
                "ls": ls, "lf": lf,
                "slack": slack,
                "is_critical": is_critical
            }
            
        # Sort critical path by start time for readability
        critical_path.sort(key=lambda x: self.schedule[x]['start'])

        return {
            "critical_path": critical_path,
            "task_analytics": task_analytics
        }
