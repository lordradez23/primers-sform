
from typing import Dict, List
from cognition.models import AnalysisResult, Interpretation

class HeuristicEngine:
    """
    LAYER 2: INTERPRETATION
    Applies rules and baselines to the raw data.
    """
    def interpret(self, data: AnalysisResult, baseline: Dict[str, float]) -> Interpretation:
        # 1. Calculate Raw Complexity
        # Now incorporating method complexity 
        func_complexity = sum(f.complexity for f in data.functions)
        class_complexity = sum(sum(m.complexity for m in c.methods) for c in data.classes)
        raw_complexity = len(data.imports) + func_complexity + class_complexity + len(data.classes)
        
        # 2. Compare to Baseline
        avg = baseline.get("avg_complexity", 10)
        if avg == 0: avg = 10
        relative_complexity = raw_complexity / avg

        # 3. Assign Role
        role = "worker"
        if len(data.imports) > (baseline.get("avg_imports", 5) * 1.5):
            role = "coordinator"
        if relative_complexity > 2.0:
            role = "god_object_candidate"
        if data.loc < 10:
            role = "stub"

        # 4. Detect Smells (Enhanced with AST data)
        smells = []
        if relative_complexity > 2.5:
            smells.append(f"Excessive Complexity ({relative_complexity:.1f}x avg)")
        if len(data.classes) > 1 and len(data.functions) > 10:
            smells.append("Mixed Responsibilities (Classes + many functions)")

        # AST-based Smells
        for f in data.functions:
            if f.complexity > 10:
                smells.append(f"Complex Function '{f.name}' (CC: {f.complexity})")
            if not f.docstring and f.complexity > 5:
                smells.append(f"Undocumented Complex Function '{f.name}'")
        
        for c in data.classes:
            if len(c.methods) > 20:
                smells.append(f"Large Class '{c.name}' ({len(c.methods)} methods)")
            for m in c.methods:
                 if m.complexity > 10:
                      smells.append(f"Complex Method '{c.name}.{m.name}' (CC: {m.complexity})")

        return Interpretation(
            source=data.source,
            complexity_score=float(raw_complexity),
            role=role,
            smells=smells,
            relative_complexity=relative_complexity
        )
