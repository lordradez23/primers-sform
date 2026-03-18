
from typing import List, Dict
from cognition.models import AnalysisResult, ComparisonResult, DiffPoint

class Comparator:
    def compare(self, analysis_a: AnalysisResult, analysis_b: AnalysisResult) -> ComparisonResult:
        """
        Compare two analysis results to find structural and complexity differences.
        """
        diffs = []
        
        # 1. Complexity Comparison
        # Recalculate based on new model structure
        comp_a = len(analysis_a.imports) + sum(f.complexity for f in analysis_a.functions) + sum(len(c.methods) for c in analysis_a.classes)
        comp_b = len(analysis_b.imports) + sum(f.complexity for f in analysis_b.functions) + sum(len(c.methods) for c in analysis_b.classes)
        
        delta = 0.0
        if comp_a > 0:
            delta = ((comp_b - comp_a) / comp_a) * 100
        
        diffs.append(DiffPoint("Complexity (Structural)", float(comp_a), float(comp_b), delta))
        
        # 2. Structure Comparison
        loc_delta = 0.0
        if analysis_a.loc > 0:
            loc_delta = ((analysis_b.loc - analysis_a.loc) / analysis_a.loc) * 100
        diffs.append(DiffPoint("LOC", float(analysis_a.loc), float(analysis_b.loc), loc_delta))
        
        # 3. Determine Winner (Simpler is usually better)
        winner = "tie"
        rationale = "Both approaches are similar in complexity."
        if comp_a < comp_b * 0.8:
            winner = analysis_a.source
            rationale = f"{analysis_a.source} is significantly simpler ({abs(delta):.1f}% less complex)."
        elif comp_b < comp_a * 0.8:
            winner = analysis_b.source
            rationale = f"{analysis_b.source} is significantly simpler ({abs(delta):.1f}% less complex)."
            
        return ComparisonResult(
            target_a=analysis_a.source,
            target_b=analysis_b.source,
            diffs=diffs,
            winner=winner,
            rationale=rationale
        )
