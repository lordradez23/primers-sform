
from typing import List, Dict, Any, Callable
from collections import deque
from core.types import ReasoningStep, TraceLog, Tone
from core.intent import Intent

class ReasoningGraph:
    def __init__(self, trace: TraceLog):
        self.trace = trace
        self.steps: List[ReasoningStep] = []
        self._max_depth = 6 # Guardrail

    def add_step(self, intent: Intent, action: str, confidence: float, summary: str, meta: Dict = None):
        if len(self.steps) >= self._max_depth:
            raise RecursionError("Max reasoning depth exceeded.")
            
        step = ReasoningStep(
            step_id=f"step_{len(self.steps)+1}",
            intent=intent.name,
            action=action,
            confidence=confidence,
            output_summary=summary,
            metadata=meta or {}
        )
        self.steps.append(step)
        self.trace.add(step)
        
    def get_aggregated_confidence(self) -> float:
        if not self.steps: return 0.0
        return sum(s.confidence for s in self.steps) / len(self.steps)

    def derive_tone(self, intent: Intent, confidence: float) -> Tone:
        # Priority mapping based on intent
        if intent == Intent.EMPIRICAL_ANALYSIS:
            return Tone.ANALYTICAL
        if intent in [Intent.INGESTION, Intent.KNOWLEDGE_ACQUISITION]:
            return Tone.CURIOUS
        if intent == Intent.VALIDATION:
            return Tone.CALM
        
        # Fallback to confidence-based logic
        if confidence >= 0.8: return Tone.ASSERTIVE
        if confidence >= 0.6: return Tone.CAUTIOUS
        return Tone.INCONCLUSIVE
