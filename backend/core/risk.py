
import os
import subprocess
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

@dataclass
class RiskNode:
    source: str
    structural_risk: float = 0.0  # S: Complexity/LOC
    volatility_risk: float = 0.0  # V: Churn/Change freq
    knowledge_risk: float = 0.0    # K: Author concentration (Bus Factor)
    criticality_risk: float = 0.0  # C: Centrality (Blast Radius)
    total_risk_score: float = 0.0
    classification: str = "GREEN"

class RiskScoringCore:
    """
    V4 CORE: The mathematical engine for systemic fragility mapping.
    Uses normalized sub-scores: RiskIndex = 100 * (wS*S + wV*V + wK*K + wC*C)
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.risk_data: Dict[str, RiskNode] = {}
        # V4 Weights
        self.wS, self.wV, self.wK, self.wC = 0.30, 0.30, 0.15, 0.25

    def compute_risk(self, analyses: Dict[str, Any], ecosystem_graph: Dict[str, List[str]]) -> Dict[str, RiskNode]:
        """
        Computes multi-dimensional risk for every node in the ecosystem.
        - S: Structural (Normalized LOC/Complexity)
        - V: Volatility (Churn Percentile)
        - K: Knowledge (Bus Factor proxy)
        - C: Criticality (Visibility Fan-in Percentile)
        """
        # 1. S: Structural Risk
        s_scores = []
        for source, data in analyses.items():
            node = RiskNode(source=source)
            complexity = data.get("complexity", 1.0)
            loc = data.get("loc", 1.0)
            # Log-scaled raw structural score
            node.structural_risk = (complexity / 20.0) * 0.7 + (loc / 500.0) * 0.3
            s_scores.append(node.structural_risk)
            self.risk_data[source] = node

        # 2. V & K: Volatility and Knowledge Risk
        self._calculate_git_metrics()

        # 3. C: Criticality Risk (Visibility Fan-in / Transitive Reach)
        self._calculate_visibility_fanin(ecosystem_graph)

        # 4. Percentile Normalization (V4 Stability)
        self._normalize_scores()

        # 5. Total RiskIndex Calculation
        for node in self.risk_data.values():
            node.total_risk_score = 100 * (
                (node.structural_risk * self.wS) + 
                (node.volatility_risk * self.wV) + 
                (node.knowledge_risk * self.wK) + 
                (node.criticality_risk * self.wC)
            )
            
            # V4 Classification Tiers
            if node.total_risk_score > 75: node.classification = "RED"    # Structural Instability
            elif node.total_risk_score > 55: node.classification = "ORANGE" # Economic Risk
            elif node.total_risk_score > 35: node.classification = "YELLOW" # Governance
            elif node.criticality_risk > 0.7: node.classification = "BLUE"  # Strategic Hub
            else: node.classification = "GREEN"

        return self.risk_data

    def _normalize_scores(self):
        """Robust percentile normalization to prevent ecosystem-size inflation."""
        def get_percentiles(attr):
            values = sorted([getattr(n, attr) for n in self.risk_data.values()])
            if not values: return
            for node in self.risk_data.values():
                val = getattr(node, attr)
                # Percentile rank
                rank = sum(1 for v in values if v < val) / len(values)
                setattr(node, attr, rank)

        for attr in ["structural_risk", "volatility_risk", "criticality_risk"]:
            get_percentiles(attr)

    def _calculate_git_metrics(self):
        """Analyzes git history for churn (V) and author silos (K)."""
        try:
            cmd = ["git", "log", "--since=3.months.ago", "--name-only", "--pretty=format:%ae"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=self.workspace_root, text=True)
            stdout, _ = process.communicate()

            churn_map = {}
            author_map = {}
            current_author = None
            
            for line in stdout.split("\n"):
                line = line.strip()
                if not line: continue
                if "@" in line:
                    current_author = line
                elif os.path.exists(os.path.join(self.workspace_root, line)):
                    file_path = line
                    # Normalize path relative to workspace root
                    rel_path = os.path.relpath(os.path.join(self.workspace_root, line), self.workspace_root).replace('\\', '/')
                    churn_map[rel_path] = churn_map.get(rel_path, 0) + 1
                    if rel_path not in author_map: author_map[rel_path] = set()
                    author_map[rel_path].add(current_author)

            for node_path, node in self.risk_data.items():
                # Cross-reference with raw analysis path
                match_key = next((k for k in churn_map.keys() if k in node_path), None)
                if match_key:
                    node.volatility_risk = churn_map[match_key]
                    authors = len(author_map.get(match_key, []))
                    if authors == 1: node.knowledge_risk = 0.9
                    elif authors == 2: node.knowledge_risk = 0.4
                    else: node.knowledge_risk = 0.1
        except Exception: pass

    def _calculate_visibility_fanin(self, graph: Dict[str, List[str]]):
        """
        Computes Transitive Reach (how many nodes indirectly depend on this).
        This is a robust measure of 'Blast Radius'.
        """
        # Reverse the graph to find dependents (transitive fan-in)
        reverse_graph = {}
        for src, targets in graph.items():
            for tgt in targets:
                if tgt not in reverse_graph: reverse_graph[tgt] = []
                reverse_graph[tgt].append(src)
        
        def count_reach(node, visited):
            if node not in reverse_graph: return 0
            count = 0
            for dep in reverse_graph[node]:
                if dep not in visited:
                    visited.add(dep)
                    count += 1 + count_reach(dep, visited)
            return count

        for node_path, node in self.risk_data.items():
            # Extract possible key from path
            graph_key = next((k for k in reverse_graph.keys() if k in node_path), None)
            if graph_key:
                node.criticality_risk = count_reach(graph_key, {graph_key})
