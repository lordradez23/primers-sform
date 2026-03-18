from typing import List, Dict, Any, Optional
from datetime import datetime
from knowledge.store import KnowledgeStore

class AutonomousAuditor:
    """
    PHASE 9: AUTONOMOUS AUDITOR
    Proactively identifies architectural debt and prepares interventions.
    """
    def __init__(self, store: KnowledgeStore):
        self.store = store

    def identify_primary_debt(self) -> Optional[Dict[str, Any]]:
        """
        Scans the knowledge base for the file with the highest debt (Complexity/LOC).
        """
        analyses = self.store.get_all_analyses()
        if not analyses:
            return None

        # Sort by debt factors
        debt_list = []
        for source, data in analyses.items():
            score = data.get("loc", 0) + (data.get("class_count", 0) * 50)
            debt_list.append({"source": source, "debt": score, "data": data})

        debt_list.sort(key=lambda x: x["debt"], reverse=True)
        return debt_list[0] if debt_list else None

    def calculate_velocity(self, source: str) -> float:
        """
        Calculates the 'Complexity Velocity' (debt growth per analysis).
        """
        history = self.store.get_history(source, limit=5)
        if len(history) < 2:
            return 0.0
        
        # Simple velocity: Delta complexity / Delta observations
        newest = history[0]['complexity']
        oldest = history[-1]['complexity']
        return (newest - oldest) / (len(history) - 1)

    def get_forecast(self, source: str) -> Dict[str, Any]:
        """
        Predicts future structural health based on current velocity.
        """
        velocity = self.calculate_velocity(source)
        history = self.store.get_history(source, limit=1)
        current_health = history[0]['health_score'] if history else 100
        current_complexity = history[0]['complexity'] if history else 0
        
        # Predict when health will hit < 50
        # If health drops 10 pts per 20 complexity pts
        health_decay_rate = 0.5 
        future_complexity = current_complexity + (velocity * 5) # 5 snapshots ahead
        predicted_health = max(0, current_health - (velocity * health_decay_rate * 5))
        
        return {
            "source": source,
            "current_velocity": round(velocity, 2),
            "predicted_health_5_cycles": round(predicted_health, 1),
            "trend": "STABLE" if velocity == 0 else "DEGRADATION" if velocity > 0 else "OPTIMIZATION"
        }

    def prepare_proactive_alert(self, health_score: int) -> Optional[str]:
        """
        Generates a proactive warning if the system is drifting or velocity is high.
        """
        target = self.identify_primary_debt()
        if not target: return None
        
        velocity = self.calculate_velocity(target['source'])
        forecast = self.get_forecast(target['source'])

        if health_score < 100 or velocity > 0.5:
            msg = f"ARCHITECTURAL FORECAST: `{target['source']}` is degrading (velocity: {forecast['current_velocity']})."
            if forecast['predicted_health_5_cycles'] < 60:
                msg += f" High risk of structural failure in 5 cycles. Proactive refactor recommended."
            else:
                msg += f" Structural Health currently {health_score}%. Fix architectural debt?"
            return msg
        return None
