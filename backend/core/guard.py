from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import enum

class PolicySeverity(enum.Enum):
    INFO = "info"
    ADVISORY = "advisory"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKER = "blocker"

@dataclass
class PolicyViolation:
    policy_id: str
    message: str
    severity: PolicySeverity
    target: str # File or module name
    mitigation: str

class PolicyGuard:
    """
    PHASE 8: ARCHITECTURAL GUARD
    Enforces structural integrity and identifies drift.
    """
    def __init__(self):
        self.rules = {
            "MAX_LOC": 1000,
            "MAX_COMPLEXITY": 20,
            "COHESION_THRESHOLD": 5, # Classes per file
            "FORBIDDEN_DEPS": {
                "core": ["main", "app"], # Core should never depend on main runners
                "cognition": ["main"]
            }
        }

    def check_drift(self, analysis_results: List[Any], edges: List[Dict[str, str]]) -> List[PolicyViolation]:
        violations = []
        
        # 1. Inspect Results
        for res in analysis_results:
            # Check LOC
            if res.loc > self.rules["MAX_LOC"]:
                violations.append(PolicyViolation(
                    "MAX_LOC",
                    f"Module '{res.source}' exceeds LOC budget ({res.loc}/{self.rules['MAX_LOC']})",
                    PolicySeverity.WARNING,
                    res.source,
                    "Consider splitting into smaller sub-modules."
                ))
            
            # Check Cohesion (God Object Lite)
            class_count = len(res.classes)
            if class_count > self.rules["COHESION_THRESHOLD"]:
                violations.append(PolicyViolation(
                    "LOW_COHESION",
                    f"Module '{res.source}' contains {class_count} classes. High risk of low cohesion.",
                    PolicySeverity.WARNING,
                    res.source,
                    "Group related classes into a new package."
                ))

        # 2. Inspect Dependencies (Edges)
        for edge in edges:
            source = edge["source"].lower()
            target = edge["target"].lower()
            
            for base, forbidden in self.rules["FORBIDDEN_DEPS"].items():
                if base in source:
                    if any(f in target for f in forbidden):
                        violations.append(PolicyViolation(
                            "DEPENDENCY_INVERSION_VIOLATION",
                            f"Architetcural Leak: Lower-level '{source}' depends on higher-level '{target}'",
                            PolicySeverity.BLOCKER,
                            source,
                            "Refactor interfaces to use dependency injection or abstract base classes."
                        ))
        
        return violations

    def get_health_score(self, violations: List[PolicyViolation]) -> int:
        score = 100
        for v in violations:
            if v.severity == PolicySeverity.BLOCKER: score -= 25
            if v.severity == PolicySeverity.WARNING: score -= 10
            if v.severity == PolicySeverity.INFO: score -= 2
        return max(0, score)
