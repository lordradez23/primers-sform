from enum import Enum, auto
from core.security import SecurityGuard

class Intent(Enum):
    EMPIRICAL_ANALYSIS = auto()
    COMPARATIVE_REASONING = auto()
    PLANNING = auto()
    EXPLANATION = auto()
    VALIDATION = auto()
    INGESTION = auto()
    KNOWLEDGE_ACQUISITION = auto()
    TEACHING = auto()
    EXECUTIVE_INSIGHTS = auto()
    APPLY_REFACTOR = auto()
    UPLOAD = auto()
    FALLBACK = auto()

class IntentRouter:
    def __init__(self):
        self.security = SecurityGuard()

    def route(self, user_input: str) -> Intent:
        # Sanitize and normalize
        normalized = self.security.sanitize_input(user_input.lower())
        
        # Priority 0: Conversational Fillers & Direct Directives
        if normalized.startswith("teach:"):
            return Intent.TEACHING
        if normalized.startswith("upload file:"):
            return Intent.UPLOAD
        if normalized.startswith("ingest") or normalized.startswith("learn from"):
            return Intent.INGESTION if "ingest" in normalized else Intent.KNOWLEDGE_ACQUISITION

        fillers = ["hey", "hello", "hi", "how are you", "who are you", "good morning"]
        if any(normalized == f or normalized.startswith(f + " ") for f in fillers):
            return Intent.FALLBACK

        # Priority 1: High-Risk Technical Commands (Must be specific)
        if "apply" in normalized and "refactor" in normalized:
            return Intent.APPLY_REFACTOR
        
        # Priority 2: Analysis & Reasoning
        if "compare" in normalized or " vs " in normalized:
            return Intent.COMPARATIVE_REASONING
        if "plan" in normalized and "refactor" in normalized:
            return Intent.PLANNING
        if "analyze" in normalized or "review" in normalized:
            return Intent.EMPIRICAL_ANALYSIS
        if "why" in normalized or "explain" in normalized:
            return Intent.EXPLANATION
        if "validate" in normalized or "check" in normalized:
            return Intent.VALIDATION
        if "learn" in normalized or "github" in normalized or "sync ecosystem" in normalized:
            return Intent.KNOWLEDGE_ACQUISITION
        
        if any(k in normalized for k in ["executive", "report", "cto", "optimize", "audit", "predictive"]):
            return Intent.EXECUTIVE_INSIGHTS
            
        return Intent.FALLBACK
