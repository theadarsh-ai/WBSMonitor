"""
Dependency Tracker Agent - 100% AI-Powered Dependency Analysis
AI analyzes complex dependency chains and predicts cascading impacts.
NO hardcoded rules - ALL analysis powered by AI.
"""
from typing import List, Dict, Set, Optional
import networkx as nx
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.azure_ai_client import get_ai_client


class DependencyTrackerAgent:
    """
    100% AI-Agentic Dependency Tracker.
    Uses AI to analyze complex dependency chains and predict impacts.
    """
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.ai_client = get_ai_client()
        print("🤖 Dependency Tracker initialized in FULLY AI-POWERED mode")
    
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
                status=task.get('status', ''),
                risk_level=task.get('risk_level', 'on_track')
            )
        
        # Add dependency edges
        for task in tasks:
            task_id = task['task_id']
            dependencies = task.get('dependencies', '')
            
            if dependencies and str(dependencies).strip():
                dep_ids = self._parse_dependencies(dependencies)
                
                for dep_id in dep_ids:
                    if dep_id in [t['task_id'] for t in tasks]:
                        self.dependency_graph.add_edge(dep_id, task_id)
        
        print(f"✓ Dependency graph: {self.dependency_graph.number_of_nodes()} nodes, {self.dependency_graph.number_of_edges()} edges")
    
    def get_ai_dependency_impact_analysis(self, task: Dict, all_tasks: List[Dict]) -> str:
        """
        AI-powered cascading impact analysis.
        Analyzes how task delays propagate through dependency chains.
        
        Returns:
            AI-generated impact analysis
        """
        if not self.ai_client.is_available():
            return self._fallback_impact_analysis(task, all_tasks)
        
        task_id = task['task_id']
        
        # Get downstream tasks
        downstream = self.get_downstream_impacts(task_id)
        
        if not downstream:
            return "✓ No direct downstream dependencies. Task is a leaf node."
        
        # Prepare context for AI
        task_context = {
            'affected_task': {
                'name': task.get('task_name'),
                'module': task.get('module'),
                'completion': task.get('completion_percent', 0),
                'risk_level': task.get('risk_level', 'unknown')
            },
            'downstream_tasks': [
                {
                    'name': t['task_name'],
                    'module': t['module'],
                    'completion': t['completion'],
                    'status': t['status']
                }
                for t in downstream[:15]  # Limit for tokens
            ]
        }
        
        system_prompt = """You are an expert AI dependency impact analyst.
Analyze how delays in one task will cascade through dependent tasks.

Consider:
- Direct vs indirect impacts
- Critical path implications
- Resource constraints
- Module interdependencies
- Compounding delays

Provide:
1. **Immediate Impact**: First-order effects
2. **Cascading Risks**: How delays propagate
3. **Critical Concerns**: Highest-risk dependencies
4. **Mitigation Strategy**: How to minimize impact

Be specific and actionable. Limit to 5-6 sentences."""
        
        user_message = f"""Analyze cascading dependency impact:

{json.dumps(task_context, indent=2)}

Provide impact analysis."""
        
        try:
            analysis = self.ai_client.generate_response(system_prompt, user_message)
            return f"🧠 AI Dependency Impact Analysis:\n\n{analysis}"
        except Exception as e:
            print(f"⚠️ AI dependency analysis error: {e}")
            return self._fallback_impact_analysis(task, all_tasks)
    
    def get_ai_critical_path_insights(self, tasks: List[Dict]) -> str:
        """
        AI analyzes the critical path and provides strategic insights.
        
        Returns:
            AI-generated critical path analysis
        """
        if not self.ai_client.is_available():
            critical_path = self.get_critical_path()
            return f"Critical path: {len(critical_path)} tasks (AI unavailable for detailed analysis)"
        
        critical_path_ids = self.get_critical_path()
        
        if not critical_path_ids:
            return "✓ No critical path identified (graph may have cycles or be empty)"
        
        # Get task details for critical path
        critical_tasks = []
        task_map = {t['task_id']: t for t in tasks}
        
        for task_id in critical_path_ids:
            if task_id in task_map:
                task = task_map[task_id]
                critical_tasks.append({
                    'name': task.get('task_name'),
                    'module': task.get('module'),
                    'completion': task.get('completion_percent', 0),
                    'due_date': str(task.get('end_date', 'N/A')),
                    'risk_level': task.get('risk_level', 'unknown')
                })
        
        system_prompt = """You are an expert AI project scheduler analyzing the critical path.

The critical path determines the minimum project duration. Any delay on this path delays the entire project.

Analyze the critical path tasks and provide:
1. **Path Health**: Overall risk assessment
2. **Bottlenecks**: Tasks most likely to cause delays
3. **Acceleration Opportunities**: Where to add resources
4. **Strategic Recommendations**: Top 2-3 actions

Be specific and actionable. Limit to 5-6 sentences."""
        
        user_message = f"""Analyze this critical path:

{json.dumps({'critical_path_length': len(critical_tasks), 'tasks': critical_tasks}, indent=2)}

Provide strategic insights."""
        
        try:
            insights = self.ai_client.generate_response(system_prompt, user_message)
            return f"🧠 AI Critical Path Analysis:\n\n{insights}\n\nCritical Path Length: {len(critical_tasks)} tasks"
        except Exception as e:
            print(f"⚠️ AI critical path analysis error: {e}")
            return f"Critical path: {len(critical_tasks)} tasks"
    
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
                'status': node_data['status'],
                'risk_level': node_data.get('risk_level', 'unknown')
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
        Get AI-powered impact analysis for a task.
        
        Returns:
            String describing the impact
        """
        return self.get_ai_dependency_impact_analysis(task, all_tasks)
    
    def _fallback_impact_analysis(self, task: Dict, all_tasks: List[Dict]) -> str:
        """Fallback analysis when AI unavailable."""
        task_id = task['task_id']
        impacted = self.get_downstream_impacts(task_id)
        
        if not impacted:
            return "No direct downstream impacts identified."
        
        modules_impacted = set(t['module'] for t in impacted if t.get('module'))
        
        analysis = f"Impacts {len(impacted)} downstream task(s)"
        
        if modules_impacted:
            analysis += f" across {len(modules_impacted)} module(s): {', '.join(modules_impacted)}"
        
        critical_impacted = [t for t in impacted if t['completion'] < 100]
        if critical_impacted:
            analysis += f". {len(critical_impacted)} incomplete tasks at risk."
        
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
