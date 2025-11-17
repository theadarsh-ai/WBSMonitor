"""
AI Decision Engine - 100% Agentic Decision Making System
Replaces ALL hardcoded rules with intelligent AI-powered decisions.

This engine uses Azure OpenAI to make autonomous decisions about:
- Task risk assessment
- Priority classification
- Escalation timing
- Task reallocation
- Timeline predictions
- Resource optimization
"""
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from utils.azure_ai_client import get_ai_client


class AIDecisionEngine:
    """
    Fully autonomous AI decision-making engine.
    NO hardcoded thresholds - ALL decisions made by AI.
    """
    
    def __init__(self):
        """Initialize AI Decision Engine with advanced capabilities."""
        self.ai_client = get_ai_client()
        self.decision_history = []  # Track decisions for learning
        
    def assess_task_risk_ai(self, task: Dict, project_context: Optional[Dict] = None) -> Dict:
        """
        AI-powered task risk assessment - NO hardcoded rules.
        
        Args:
            task: Task dictionary with all task details
            project_context: Optional context about the overall project
            
        Returns:
            Dictionary with {
                'risk_level': str (critical_escalation|alert|at_risk|on_track),
                'risk_reason': str,
                'confidence': float (0-1),
                'recommended_actions': List[str],
                'urgency_score': int (1-100)
            }
        """
        if not self.ai_client.is_available():
            return self._fallback_assessment(task)
        
        # Prepare comprehensive task context for AI
        task_context = self._prepare_task_context(task, project_context)
        
        system_prompt = """You are an expert AI project risk analyst with decades of experience. 
You assess task risks holistically, considering:
- Timeline constraints and completion progress
- Complexity and dependencies
- Historical patterns and trends
- Team capacity and workload
- Business impact and criticality
- Seasonal/contextual factors

Categorize each task into ONE of these risk levels:
1. critical_escalation: Requires immediate attention, high business impact
2. alert: Needs action soon, potential for delays
3. at_risk: Concerning trend, monitor closely
4. on_track: Progressing well, no immediate concerns

Provide your assessment in JSON format:
{
    "risk_level": "one of: critical_escalation|alert|at_risk|on_track",
    "risk_reason": "brief explanation (1-2 sentences)",
    "confidence": 0.85,
    "recommended_actions": ["action 1", "action 2"],
    "urgency_score": 75,
    "key_factors": ["factor 1", "factor 2"]
}"""
        
        user_message = f"""Assess the risk for this task:

Task Details:
{json.dumps(task_context, indent=2, default=str)}

Provide a comprehensive risk assessment in JSON format."""
        
        try:
            response = self.ai_client.generate_response(system_prompt, user_message)
            
            # Handle None response from AI client
            if response is None:
                print("⚠️ AI returned None - using fallback assessment")
                return self._fallback_assessment(task)
            
            # Parse AI response
            # Extract JSON from response (may have markdown code blocks)
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            assessment = json.loads(response_clean)
            
            # Store decision for learning
            self._record_decision('risk_assessment', task, assessment)
            
            return assessment
            
        except Exception as e:
            print(f"⚠️ AI risk assessment error: {e}")
            return self._fallback_assessment(task)
    
    def batch_assess_tasks_ai(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        AI-powered batch task assessment with chunking for performance.
        Analyzes tasks in smaller batches to avoid timeouts.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Categorized tasks by risk level
        """
        if not self.ai_client.is_available():
            return self._batch_fallback(tasks)
        
        # Process in chunks of 20 tasks for better performance
        CHUNK_SIZE = 20
        all_categorized = {
            'critical_escalation': [],
            'alert': [],
            'at_risk': [],
            'on_track': []
        }
        
        # Process tasks in chunks
        for i in range(0, len(tasks), CHUNK_SIZE):
            chunk = tasks[i:i+CHUNK_SIZE]
            chunk_result = self._assess_task_chunk(chunk)
            
            # Merge results
            for category in all_categorized:
                all_categorized[category].extend(chunk_result.get(category, []))
        
        return all_categorized
    
    def _assess_task_chunk(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Process a single chunk of tasks with AI assessment."""
        batch_context = self._prepare_batch_context(tasks)
        
        system_prompt = """You are an expert AI project analyst. Analyze these tasks and assign risk levels.

For EACH task, return JSON array:
[
    {
        "task_id": "task identifier",
        "task_name": "task name",
        "risk_level": "critical_escalation|alert|at_risk|on_track",
        "risk_reason": "brief explanation",
        "confidence": 0.85,
        "urgency_score": 75
    }
]

Risk levels:
- critical_escalation: Immediate action needed, high business impact
- alert: Needs attention soon, potential delays
- at_risk: Concerning trend, monitor closely
- on_track: Progressing well

Be decisive. Return ONLY the JSON array."""
        
        user_message = f"""Analyze these {len(tasks)} tasks:

{batch_context}

Return JSON array with assessment for EACH task."""
        
        try:
            import time
            start_time = time.time()
            
            response = self.ai_client.generate_response(system_prompt, user_message)
            
            elapsed = time.time() - start_time
            print(f"⏱️ AI chunk assessment took {elapsed:.1f}s for {len(tasks)} tasks")
            
            if response is None:
                print("⚠️ AI returned None - using fallback")
                return self._categorize_chunk_fallback(tasks)
            
            # Parse AI response
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            assessments = json.loads(response_clean)
            
            # Categorize tasks
            categorized = {
                'critical_escalation': [],
                'alert': [],
                'at_risk': [],
                'on_track': []
            }
            
            # Map assessments back to tasks
            task_map = {task.get('task_id') or task.get('task_name'): task for task in tasks}
            
            for assessment in assessments:
                task_id = assessment.get('task_id') or assessment.get('task_name')
                task = task_map.get(task_id)
                
                if task:
                    task['risk_level'] = assessment['risk_level']
                    task['risk_reason'] = assessment['risk_reason']
                    task['ai_confidence'] = assessment.get('confidence', 0.75)
                    task['urgency_score'] = assessment.get('urgency_score', 50)
                    categorized[assessment['risk_level']].append(task)
            
            # Record decision
            self._record_decision('batch_assessment', {'count': len(tasks)}, assessments)
            
            return categorized
            
        except Exception as e:
            print(f"⚠️ AI chunk assessment error: {e}")
            return self._categorize_chunk_fallback(tasks)
    
    def _categorize_chunk_fallback(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Fallback categorization for a chunk when AI fails."""
        return {
            'critical_escalation': [],
            'alert': [],
            'at_risk': [],
            'on_track': tasks
        }
    
    def should_escalate_ai(self, task: Dict, recipients: List[str]) -> Dict:
        """
        AI decides whether to escalate a task and how.
        
        Returns:
            {
                'should_escalate': bool,
                'escalation_level': str (immediate|urgent|routine),
                'recipients': List[str],
                'reason': str,
                'recommended_timeline': str
            }
        """
        if not self.ai_client.is_available():
            return {'should_escalate': True, 'escalation_level': 'urgent', 
                    'recipients': recipients, 'reason': 'Default escalation'}
        
        task_summary = self._prepare_task_context(task)
        
        system_prompt = """You are an expert escalation manager. Decide if and how to escalate issues.
Consider:
- Actual business impact
- Stakeholder communication preferences
- Alert fatigue (avoid spam)
- Timing appropriateness
- Actionability

Return JSON:
{
    "should_escalate": true|false,
    "escalation_level": "immediate|urgent|routine|none",
    "recipients": ["list", "of", "emails"],
    "reason": "why this decision",
    "recommended_timeline": "when to follow up"
}"""
        
        user_message = f"""Should this task be escalated?

Task: {json.dumps(task_summary, indent=2, default=str)}
Potential Recipients: {recipients}

Provide escalation decision in JSON."""
        
        try:
            response = self.ai_client.generate_response(system_prompt, user_message)
            
            # Handle None response from AI client
            if response is None:
                return {'should_escalate': True, 'escalation_level': 'urgent',
                        'recipients': recipients, 'reason': 'Fallback escalation (AI unavailable)'}
            
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            decision = json.loads(response_clean)
            self._record_decision('escalation', task, decision)
            return decision
        except Exception as e:
            print(f"⚠️ AI escalation decision error: {e}")
            return {'should_escalate': True, 'escalation_level': 'urgent',
                    'recipients': recipients, 'reason': 'Fallback escalation'}
    
    def suggest_task_reallocation_ai(self, task: Dict, available_resources: List[Dict]) -> Optional[Dict]:
        """
        AI suggests optimal task reallocation for self-healing.
        
        Returns:
            {
                'should_reallocate': bool,
                'recommended_assignee': str,
                'reason': str,
                'expected_improvement': str,
                'confidence': float
            }
        """
        if not self.ai_client.is_available():
            return None
        
        system_prompt = """You are an expert resource allocation AI. Suggest optimal task reassignments.
Consider:
- Current workload distribution
- Skill matching
- Deadline proximity
- Team dynamics
- Past performance

Return JSON:
{
    "should_reallocate": true|false,
    "recommended_assignee": "name or id",
    "reason": "why this assignment",
    "expected_improvement": "predicted outcome",
    "confidence": 0.85
}"""
        
        context = {
            'task': self._prepare_task_context(task),
            'available_resources': available_resources
        }
        
        user_message = f"""Suggest task reallocation:

{json.dumps(context, indent=2, default=str)}

Provide reallocation recommendation in JSON."""
        
        try:
            response = self.ai_client.generate_response(system_prompt, user_message)
            
            # Handle None response from AI client
            if response is None:
                return None
            
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            decision = json.loads(response_clean)
            self._record_decision('reallocation', task, decision)
            return decision
        except Exception as e:
            print(f"⚠️ AI reallocation error: {e}")
            return None
    
    def predict_timeline_ai(self, task: Dict, dependencies: List[Dict]) -> Dict:
        """
        AI predicts realistic completion timeline.
        
        Returns:
            {
                'predicted_completion_date': str,
                'confidence': float,
                'risk_factors': List[str],
                'buffer_recommendation': int (days)
            }
        """
        if not self.ai_client.is_available():
            return {'predicted_completion_date': task.get('end_date'), 'confidence': 0.5}
        
        system_prompt = """You are an expert project timeline predictor with AI-powered forecasting.
Analyze task progress, dependencies, and historical patterns to predict realistic completion dates.

Return JSON:
{
    "predicted_completion_date": "YYYY-MM-DD",
    "confidence": 0.85,
    "risk_factors": ["factor 1", "factor 2"],
    "buffer_recommendation": 5,
    "reasoning": "explanation"
}"""
        
        context = {
            'task': self._prepare_task_context(task),
            'dependencies': dependencies
        }
        
        user_message = f"""Predict completion timeline:

{json.dumps(context, indent=2, default=str)}

Provide timeline prediction in JSON."""
        
        try:
            response = self.ai_client.generate_response(system_prompt, user_message)
            
            # Handle None response from AI client
            if response is None:
                return {'predicted_completion_date': task.get('end_date'), 'confidence': 0.5,
                        'risk_factors': ['AI unavailable'], 'buffer_recommendation': 0}
            
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            prediction = json.loads(response_clean)
            self._record_decision('timeline_prediction', task, prediction)
            return prediction
        except Exception as e:
            print(f"⚠️ AI timeline prediction error: {e}")
            return {'predicted_completion_date': task.get('end_date'), 'confidence': 0.5}
    
    def _prepare_task_context(self, task: Dict, project_context: Optional[Dict] = None) -> Dict:
        """Prepare comprehensive task context for AI analysis."""
        context = {
            'task_id': task.get('task_id'),
            'task_name': task.get('task_name'),
            'module': task.get('module'),
            'completion_percent': task.get('completion_percent', 0),
            'start_date': str(task.get('start_date', '')),
            'end_date': str(task.get('end_date', '')),
            'assigned_to': task.get('assigned_to', 'Unassigned'),
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_month': datetime.now().strftime('%B %Y')
        }
        
        # Add project context if available
        if project_context:
            context['project_context'] = project_context
        
        return context
    
    def _prepare_batch_context(self, tasks: List[Dict]) -> str:
        """Prepare batch context for multiple tasks."""
        task_summaries = []
        for task in tasks[:30]:  # Limit to 30 tasks to avoid token limits
            summary = (
                f"Task: {task.get('task_name')}\n"
                f"  ID: {task.get('task_id', 'N/A')}\n"
                f"  Module: {task.get('module', 'N/A')}\n"
                f"  Completion: {task.get('completion_percent', 0)}%\n"
                f"  Due: {task.get('end_date', 'N/A')}\n"
                f"  Assigned: {task.get('assigned_to', 'Unassigned')}"
            )
            task_summaries.append(summary)
        
        return "\n\n".join(task_summaries)
    
    def _fallback_assessment(self, task: Dict) -> Dict:
        """Fallback assessment when AI is unavailable."""
        return {
            'risk_level': 'on_track',
            'risk_reason': 'AI unavailable - using conservative assessment',
            'confidence': 0.3,
            'recommended_actions': ['Enable AI for intelligent assessment'],
            'urgency_score': 50
        }
    
    def _batch_fallback(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Fallback batch assessment when AI is unavailable."""
        return {
            'critical_escalation': [],
            'alert': [],
            'at_risk': [],
            'on_track': tasks
        }
    
    def _record_decision(self, decision_type: str, input_data: Dict, output_data: Dict):
        """Record decisions for future learning and analysis."""
        self.decision_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': decision_type,
            'input': input_data,
            'output': output_data
        })
        
        # Keep last 100 decisions in memory
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]
    
    def get_decision_insights(self) -> Dict:
        """Analyze decision history for insights and learning."""
        if not self.decision_history:
            return {'total_decisions': 0}
        
        insights = {
            'total_decisions': len(self.decision_history),
            'by_type': {},
            'recent_patterns': []
        }
        
        # Count decisions by type
        for decision in self.decision_history:
            decision_type = decision['type']
            insights['by_type'][decision_type] = insights['by_type'].get(decision_type, 0) + 1
        
        return insights


# Singleton instance
_decision_engine = None

def get_decision_engine() -> AIDecisionEngine:
    """Get singleton AI Decision Engine instance."""
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = AIDecisionEngine()
    return _decision_engine
