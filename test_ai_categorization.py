"""
Test AI task categorization to debug why all categories are empty.
"""
import sys
from utils.ai_decision_engine import get_decision_engine
from agents.data_collection_agent import DataCollectionAgent

# Collect real tasks
print("📊 Loading tasks from WBS...")
data_agent = DataCollectionAgent()
tasks = data_agent.collect_project_data()

if not tasks:
    print("❌ No tasks found!")
    sys.exit(1)

print(f"✓ Loaded {len(tasks)} tasks")
print(f"\nSample task structure:")
sample = tasks[0]
for key, value in sample.items():
    print(f"  {key}: {value}")

# Test AI categorization
print(f"\n🤖 Testing AI batch assessment...")
engine = get_decision_engine()

if not engine.ai_client.is_available():
    print("❌ AI client not available!")
    sys.exit(1)

print("✓ AI client is available")

# Take a small sample for testing
test_tasks = tasks[:5]
print(f"\n📝 Testing with {len(test_tasks)} tasks:")
for task in test_tasks:
    print(f"  - {task.get('task_name', 'Unknown')}: {task.get('completion_percent', 0)}% complete")

print(f"\n🔬 Running AI batch assessment...")
result = engine.batch_assess_tasks_ai(test_tasks)

print(f"\n📊 Results:")
print(f"  Critical: {len(result.get('critical_escalation', []))}")
print(f"  Alert: {len(result.get('alert', []))}")
print(f"  At Risk: {len(result.get('at_risk', []))}")
print(f"  On Track: {len(result.get('on_track', []))}")

print(f"\n🔍 Detailed categorization:")
for category, task_list in result.items():
    print(f"\n{category.upper()} ({len(task_list)} tasks):")
    for task in task_list:
        print(f"  - {task.get('task_name', 'Unknown')}")
        print(f"    Risk: {task.get('risk_level', 'N/A')}")
        print(f"    Reason: {task.get('risk_reason', 'N/A')}")
