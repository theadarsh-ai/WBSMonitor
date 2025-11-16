"""
Dependency Tracker Agent - Tracks cross-module dependencies and impacts.
Enhanced with AI for dependency insights and risk propagation analysis.
"""
from typing import List, Dict, Set, Optional
import networkx as nx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.azure_ai_client import get_ai_client


class DependencyTrackerAgent:
    """Agent responsible for tracking task dependencies with AI-powered insights."""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.ai_client = get_ai_client()
    
    def build_dependency_graph(self, tasks: List[Dict]):
        """
        Build dependency graph from task list.
        
        Args:
            tasks: List of task dictionaries
        """
        self.dependency_graph.clear()
        
        # Add all tasks as nodes
        for task in tasks:
            task_id = task['task_id']
            self.dependency_graph.add_node(
                task_id,
                name=task['task_name'],
                module=task.get('module', ''),
                completion=task.get('completion_percent', 0),
                status=task.get('status', '')
            )
        
        # Add dependency edges
        for task in tasks:
            task_id = task['task_id']
            dependencies = task.get('dependencies', '')
            
            if dependencies and str(dependencies).strip():
                # Parse dependencies (assuming comma-separated IDs)
                dep_ids = self._parse_dependencies(dependencies)
                
                for dep_id in dep_ids:
                    if dep_id in [t['task_id'] for t in tasks]:
                        # Edge from dependency to task (dependency must complete first)
                        self.dependency_graph.add_edge(dep_id, task_id)
        
        print(f"✓ Built dependency graph with {self.dependency_graph.number_of_nodes()} nodes and {self.dependency_graph.number_of_edges()} edges")
    
    def get_downstream_impacts(self, task_id: int) -> List[Dict]:
        """
        Get all tasks impacted by delays in the given task.
        
        Args:
            task_id: Task ID to analyze
            
        Returns:
            List of impacted task details
        """
        if task_id not in self.dependency_graph:
            return []
        
        # Get all descendants (tasks that depend on this task)
        impacted_ids = list(nx.descendants(self.dependency_graph, task_id))
        
        impacted_tasks = []
        for imp_id in impacted_ids:
            node_data = self.dependency_graph.nodes[imp_id]
            impacted_tasks.append({
                'task_id': imp_id,
                'task_name': node_data['name'],
                'module': node_data['module'],
                'completion': node_data['completion'],
                'status': node_data['status']
            })
        
        return impacted_tasks
    
    def get_critical_path(self) -> List[int]:
        """
        Identify critical path in the project.
        
        Returns:
            List of task IDs on critical path
        """
        try:
            # Find longest path (critical path)
            critical_path = nx.dag_longest_path(self.dependency_graph)
            return critical_path
        except:
            return []
    
    def analyze_module_dependencies(self, tasks: List[Dict]) -> Dict[str, List[str]]:
        """
        Analyze dependencies between project modules.
        
        Returns:
            Dictionary mapping modules to their dependent modules
        """
        module_deps = {}
        
        for task in tasks:
            task_id = task['task_id']
            module = task.get('module', '')
            
            if not module:
                continue
            
            if module not in module_deps:
                module_deps[module] = set()
            
            # Get upstream tasks
            if task_id in self.dependency_graph:
                predecessors = list(self.dependency_graph.predecessors(task_id))
                
                for pred_id in predecessors:
                    pred_module = self.dependency_graph.nodes[pred_id].get('module', '')
                    if pred_module and pred_module != module:
                        module_deps[module].add(pred_module)
        
        # Convert sets to lists
        return {k: list(v) for k, v in module_deps.items()}
    
    def get_impact_analysis(self, task: Dict, all_tasks: List[Dict]) -> str:
        """
        Generate impact analysis for a delayed task.
        
        Returns:
            String describing the impact
        """
        task_id = task['task_id']
        impacted = self.get_downstream_impacts(task_id)
        
        if not impacted:
            return "No direct downstream impacts identified."
        
        modules_impacted = set(t['module'] for t in impacted if t.get('module'))
        
        analysis = f"This task delay impacts {len(impacted)} downstream task(s)"
        
        if modules_impacted:
            analysis += f" across {len(modules_impacted)} module(s): {', '.join(modules_impacted)}"
        
        critical_impacted = [t for t in impacted if t['completion'] < 100]
        if critical_impacted:
            analysis += f". {len(critical_impacted)} of these tasks are incomplete and at risk."
        
        return analysis
    
    def _parse_dependencies(self, dependencies_str: str) -> List[int]:
        """Parse dependency string into list of task IDs."""
        if not dependencies_str or str(dependencies_str).lower() == 'nan':
            return []
        
        dep_list = []
        parts = str(dependencies_str).split(',')
        
        for part in parts:
            try:
                dep_id = int(part.strip())
                dep_list.append(dep_id)
            except:
                continue
        
        return dep_list
