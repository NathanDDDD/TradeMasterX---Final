#!/usr/bin/env python3
"""Test import of AI components"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

try:
    print("Testing ObserverAgent import...")
    from trademasterx.ai.observer_agent import ObserverAgent
    print("✅ ObserverAgent imported successfully")
except Exception as e:
    print(f"❌ ObserverAgent import failed: {e}")

try:
    print("Testing AIOrchestrator import...")
    from trademasterx.ai.ai_orchestrator import AIOrchestrator
    print("✅ AIOrchestrator imported successfully")
except Exception as e:
    print(f"❌ AIOrchestrator import failed: {e}")

try:
    print("Testing ReinforcementEngine import...")
    from trademasterx.ai.reinforcement_engine import ReinforcementEngine
    print("✅ ReinforcementEngine imported successfully")
except Exception as e:
    print(f"❌ ReinforcementEngine import failed: {e}")

try:
    print("Testing AnomalyAuditor import...")
    from trademasterx.ai.anomaly_auditor import AnomalyAuditor
    print("✅ AnomalyAuditor imported successfully")
except Exception as e:
    print(f"❌ AnomalyAuditor import failed: {e}")

try:
    print("Testing AIDashboard import...")
    from trademasterx.interface.web.ai_dashboard import AIDashboard
    print("✅ AIDashboard imported successfully")
except Exception as e:
    print(f"❌ AIDashboard import failed: {e}")

print("Import test completed.")
