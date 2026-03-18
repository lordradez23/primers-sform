
import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import PrimersEngine
from core.intent import Intent
from core.types import IntelligenceLevel

def run_shadow_gate():
    """
    V4 Phase 1: Shadow CI Gate.
    Executes architectural audit and outputs verdicts without blocking the process.
    """
    print(" SOVEREIGN GUARD GATE: INITIATING SHADOW AUDIT")
    print("-" * 50)
    
    engine = PrimersEngine()
    
    # 1. Trigger Ecosystem Sync (Local)
    print("1. Synchronizing Local Ecosystem Topology...")
    current_dir = os.getcwd()
    # We simulate an 'executive report' intent which triggers the full risk audit
    res = engine.insights.generate_report()
    
    # 2. Extract Critical Violations
    metrics = res.get("metrics", {})
    hotspots = metrics.get("fragility_hotspots", [])
    compliance = metrics.get("global_compliance_rating", "0%")
    
    print(f"2. Audit Complete. Global Compliance: {compliance}")
    
    critical_found = False
    for hotspot in hotspots:
        if hotspot['risk_type'] == "RED":
            critical_found = True
            print(f"   [SHADOW BLOCK] CRITICAL: {hotspot['node']}")
            print(f"   └─ RISK INDEX: {hotspot['score']} (Threshold: 75.0)")
            print(f"   └─ BLAST RADIUS: {hotspot['blast_radius']}%")
            print(f"   └─ EXPLAINABILITY: High systemic fragility detected in dependent topology.")

    print("-" * 50)
    if critical_found:
        print("RESULT: [SIMULATED FAILURE] Building in Mandatory Mode would be BLOCKED.")
    else:
        print("RESULT: [SUCCESS] No critical structural violations detected.")
    
    # In Shadow Mode, we always exit 0
    sys.exit(0)

if __name__ == "__main__":
    run_shadow_gate()
