
import os
import json
from datetime import datetime
from typing import Dict, Any, List
from core.guardrails import SovereignGuardrails
from core.risk import RiskScoringCore

class ExecutiveInsights:
    """
    COMMERCIAL LAYER: Transforms raw architectural data into high-level business intelligence.
    Designed for CTO/VPE personas to track ROI, Risk, and Velocity.
    """
    def __init__(self, m2_store):
        self.m2 = m2_store
        self.guardrails = SovereignGuardrails()
        # Initialize Risk Engine with scratch root
        current_dir = os.path.dirname(__file__)
        scratch_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        self.risk_engine = RiskScoringCore(scratch_root)

    def generate_report(self) -> Dict[str, Any]:
        """
        Derives an executive summary from the M2 database.
        """
        # 1. Fetch Analyses
        analyses = self.m2.get_all_analyses()
        total_nodes = len(analyses)
        
        # 2. Calculate "Architectural Debt" Coefficient
        debt_score = self._calculate_debt(analyses)
        
        # 3. Estimated "Refactor Cost" (Market Value)
        # 1 debt point = $150 (approx. developer hour cost)
        estimated_cost = debt_score * 150
        
        # 4. Success Potential
        # Based on how well patterns are established
        roi_potential = self._calculate_roi(analyses)

        # 5. Ecosystem Breath
        projects = set()
        for source in analyses.keys():
            # Assume source paths like 'c:/.../scratch/project-name/file.py'
            if "scratch" in source:
                parts = source.split("scratch")[1].split(os.sep)
                if len(parts) > 1:
                    projects.add(parts[1])
        
        ecosystem_depth = len(projects) if projects else 1
        
        # 6. Global Compliance
        violations = self.guardrails.audit_workspace(analyses)
        compliance_score = max(0, 100 - (len(violations) * 2))

        # 7. Systemic Fragility Mapping (V4 Core)
        graph = self.m2.get_graph()
        risk_nodes = self.risk_engine.compute_risk(analyses, graph)
        
        # Extract Top 3 Hotspots (Highest Total Risk)
        hotspots = sorted(risk_nodes.values(), key=lambda x: x.total_risk_score, reverse=True)[:3]
        fragility_report = []
        for h in hotspots:
            fragility_report.append({
                "node": h.source,
                "score": round(h.total_risk_score, 1),
                "risk_type": h.classification,
                "blast_radius": round(h.criticality_risk * 100, 1)
            })
            # Persist Snapshot for V4 Trend Audit
            self.m2.save_risk_snapshot(h.source, h.structural_risk, h.volatility_risk, h.knowledge_risk, h.criticality_risk, h.total_risk_score, h.classification)

        # 8. PDM (Primers Debt Multiplier) Economics
        # Value = (RiskIndex * BusinessCriticality * Exposure)
        pdm_score = self._calculate_pdm(risk_nodes)
        
        # 9. Dynamic Technical Debt (Adjusted by PDM)
        # Base Debt * PDM multiplier
        adjusted_debt_cost = estimated_cost * pdm_score

        # 7. Predictive Savings Forecast
        # Total Units * Efficiency Multiplier * Avg Dev Day Cost
        annual_savings = (total_nodes * 250) + (compliance_score * 120)
        
        # 8. Repaid Debt (Sovereign Auto-Refactor)
        repaid_debt = self.m2.get_repaid_debt()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_structural_units": total_nodes,
                "project_ecosystem_depth": ecosystem_depth,
                "global_compliance_rating": f"{compliance_score}%",
                "architectural_health": max(0, 100 - (debt_score / 10)),
                "technical_debt_cost": adjusted_debt_cost,
                "base_debt_exposure": estimated_cost,
                "pdm_multiplier": f"{pdm_score:.2f}x",
                "total_debt_repaid": repaid_debt,
                "fragility_hotspots": fragility_report,
                "velocity_risk": "HIGH" if debt_score > 500 or any(h.total_risk_score > 70 for h in hotspots) else "STABLE",
                "roi_potential": f"{roi_potential}%",
                "annual_savings_forecast": annual_savings,
                "efficiency_roi": f"{(roi_potential * 1.4):.1f}%"
            },
            "recommendations": self._generate_recommendations(debt_score, total_nodes),
            "market_verdict": self._get_market_verdict(debt_score)
        }

    def _calculate_debt(self, analyses: Dict) -> float:
        # Scale by complexity and repository count
        return sum(a.get('complexity', 5) for a in analyses.values()) * 0.8
        
    def _calculate_pdm(self, risk_nodes: Dict) -> float:
        """
        V4 Financial Engine (Hardened): PDM = 1 + (Σ w_i * A_i / Σ w_i)
        Uses Weighted Mean to prevent inflation from ecosystem size.
        """
        if not risk_nodes: return 1.0
        
        amplifications = []
        for node in risk_nodes.values():
            # A_i = (RiskIndex/100) * (1 + Criticality)
            # We use normalized criticality (C) to amplify the risk
            amp = (node.total_risk_score / 100.0) * (1.0 + node.criticality_risk)
            amplifications.append(amp)
        
        if not amplifications: return 1.0
        
        # Aggregation: Weighted mean prioritizing high-risk hotspots (Top 20% or Top 5)
        # This focuses on "Risk Concentration" rather than total node count
        sorted_amps = sorted(amplifications, reverse=True)
        top_k = max(1, min(len(sorted_amps), 10)) # Top 10 hotspots
        concentration_risk = sum(sorted_amps[:top_k]) / top_k
        
        # PDM = 1 + (α * concentration_risk)
        # α = 2.0 (scaling factor for senior engineer overhead / incident probability)
        pdm = 1.0 + (2.0 * concentration_risk)
            
        return min(3.5, pdm)

    def _calculate_roi(self, analyses: Dict) -> int:
        # ROI is higher if the code is modular
        if not analyses: return 0
        return min(98, 50 + (len(analyses) // 2))

    def _generate_recommendations(self, debt: float, nodes: int) -> List[str]:
        recs = []
        if debt > 1000:
            recs.append("EXECUTION REQUIRED: Immediate liquidation of god-objects is mandatory to survive technical bankruptcy.")
        if nodes < 10:
            recs.append("EXPANSION MANDATE: Force-merge core logic into new modules to capture technical market share.")
        else:
            recs.append("DOMINANCE: Enforce the current modular pattern. Any deviation will be blocked by Sovereign Guardrails.")
        return recs

    def _get_market_verdict(self, debt: float) -> str:
        if debt < 500:
            return "ELITE STATUS - Pristine Architecture; Ready for Global Dominance"
        elif debt < 1500:
            return "WARNING - Structural Friction Detected; Executive Intervention Required"
        else:
            return "BANKRUPT - Technical Debt Overload; Halt All Development and Refactor"
