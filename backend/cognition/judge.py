
from typing import List, Optional
from cognition.models import Interpretation, Judgement, RefactorPlan

class JudgementCore:
    """
    LAYER 3: JUDGMENT
    Formulates human-readable conclusions and recommendations.
    """
    def assess(self, interpretation: Interpretation, content: str = "") -> Judgement:
        # 1. Formulate Summary
        summary = f"File '{interpretation.source}' acting as {interpretation.role.upper()}."
        if interpretation.relative_complexity > 1.2:
            summary += f" Complexity is {interpretation.relative_complexity:.1f}x baseline."
        
        # 2. Assess Risks
        risks = []
        for smell in interpretation.smells:
            risks.append(f"Risk: {smell}")
        if interpretation.role == "god_object_candidate":
            risks.append("Critical Risk: High coupling probability.")

        # 3. Generate Recommendations & Plan
        recommendations = []
        plan = None
        
        if interpretation.relative_complexity > 2.0:
            recommendations.append("Immediate refactor recommended.")
            plan = self._plan_refactor(interpretation, content)
        elif interpretation.role == "coordinator":
            recommendations.append("Verify import necessity.")
        else:
            recommendations.append("Code structure is within nominal parameters.")

        # 4. Calibration
        confidence = self._calibrate_confidence(interpretation)

        return Judgement(
            summary=summary,
            risks=risks,
            recommendations=recommendations,
            refactor_plan=plan,
            confidence_score=confidence
        )

    def _plan_refactor(self, interp: Interpretation, content: str = "") -> RefactorPlan:
        steps = []
        if "Mixed Responsibilities" in str(interp.smells):
            steps.append("Extract standalone functions to 'utils.py'")
            steps.append("Separate classes into distinct files")
        
        # New AST-based refactor steps
        for smell in interp.smells:
            if "Complex Function" in smell:
                try:
                    func_name = smell.split("'")[1]
                    steps.append(f"Break down function '{func_name}' into smaller helper functions.")
                except: pass
            if "Large Class" in smell:
                try:
                    class_name = smell.split("'")[1]
                    steps.append(f"Apply Extract Class refactoring to '{class_name}'.")
                except: pass
            if "Undocumented" in smell:
                 steps.append("Add docstrings to public API surface.")

        if interp.complexity_score > 30 and not steps:
            steps.append("Split file into sub-modules based on import clusters")

        # Simulate proposed code (Symbolic Refactoring)
        proposed = content
        if "Add docstrings" in str(steps) and '"""' not in content:
            proposed = f'"""\nRefactored by Primers Intelligence\nProject: {interp.source}\n"""\n' + content

        return RefactorPlan(
            goal=f"Reduce complexity of {interp.source}",
            steps=steps or ["Perform manual audit of dependencies"],
            risk="Medium",
            expected_gain=f"Complexity -{int((interp.relative_complexity - 1.0)*100/2)}%",
            current_code=content,
            proposed_code=proposed
        )

    def _calibrate_confidence(self, interp: Interpretation) -> float:
        # Starting base
        score = 0.5
        # Gain confidence if finding strong signals
        if interp.role != "worker": score += 0.2
        if interp.smells: score += 0.2
        # Cap at 0.95 (never 100% certain without execution)
        return min(0.95, score)
