
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class IntelligenceLevel(Enum):
    SYMBOLIC = 0      # Pure logic/rules
    HEURISTIC = 1     # Graph + Pattern Matching
    EXTERNAL = 2      # LLM (Gemini/Local)

class Tone(Enum):
    ASSERTIVE = "assertive"       # Confidence >= 0.8
    CAUTIOUS = "cautious"         # Confidence 0.6 - 0.79
    INCONCLUSIVE = "inconclusive" # Confidence < 0.6
    CALM = "calm"                 # Status/Health checks
    CURIOUS = "curious"           # Searching/Learning
    ANALYTICAL = "analytical"     # Deep code analysis

@dataclass
class ReasoningStep:
    step_id: str
    intent: str
    action: str
    confidence: float
    output_summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TraceLog:
    steps: List[ReasoningStep] = field(default_factory=list)
    session_id: str = "default_session"
    
    def add(self, step: ReasoningStep):
        self.steps.append(step)

    def to_list(self) -> List[str]:
        return [f"Step {s.step_id}: {s.action} (Conf: {s.confidence:.2f})" for s in self.steps]

@dataclass
class EngineResponse:
    content: str
    intent: str
    confidence: float
    level: IntelligenceLevel
    tone: Tone
    trace: TraceLog
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "content": self.content,
            "intent": self.intent,
            "confidence": self.confidence,
            "level": self.level.name,
            "tone": self.tone.value,
            "trace": [s.__dict__ for s in self.trace.steps],
            "meta": self.meta
        }
