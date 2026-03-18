
from typing import List, Dict, Any
from core.guard import PolicySeverity

class PolicyViolation:
    def __init__(self, policy_id: str, target: str, message: str, severity: PolicySeverity, mitigation: str):
        self.policy_id = policy_id
        self.target = target
        self.message = message
        self.severity = severity
        self.mitigation = mitigation

class SovereignGuardrails:
    """
    ENTERPRISE LAYER: Enforces global architectural standards across the ecosystem.
    Used by CTOs to prevent technical debt growth.
    """
    def __init__(self):
        self.global_rules = [
            {
                "id": "PR-01",
                "name": "Dependency Isolation",
                "description": "Modules must not have circular dependencies.",
                "severity": PolicySeverity.CRITICAL
            },
            {
                "id": "PR-02",
                "name": "Structural Cohesion",
                "description": "Classes should not exceed 500 lines of code.",
                "severity": PolicySeverity.WARNING
            },
            {
                "id": "PR-03",
                "name": "Audit Logging",
                "description": "All destructive actions must be logged to M2.",
                "severity": PolicySeverity.ADVISORY
            }
        ]

    def audit_workspace(self, analyses: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        for source, data in analyses.items():
            # Rule PR-02: Size Check
            loc = data.get("loc", 0)
            if loc > 500:
                violations.append(PolicyViolation(
                    "PR-02", source, 
                    f"Structural unit '{source}' exceeeds 500 LOC ({loc}).",
                    PolicySeverity.WARNING,
                    "Break down the module into smaller functional components."
                ))
            
            # Rule PR-03: Complexity Check
            complexity = data.get("complexity", 0)
            if complexity > 15:
                violations.append(PolicyViolation(
                    "PR-04", source,
                    f"Cyclomatic complexity is too high ({complexity}).",
                    PolicySeverity.CRITICAL,
                    "Simplify control flow or extract logic into helper methods."
                ))
        return violations
