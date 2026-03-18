
# 🔹 PRIMERS REPOSITORY INTELLIGENCE
# --------------------------------
# Provides semantic search and analysis for local/remote codebases.

import re
from typing import List, Dict, Any

class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, Any] = {}
        self.edges: List[Dict[str, str]] = []

    def add_node(self, name: str, node_type: str, metadata: Dict):
        self.nodes[name] = {"type": node_type, "meta": metadata}

    def add_edge(self, source: str, target: str, relation: str):
        self.edges.append({"source": source, "target": target, "relation": relation})

    def find_related(self, query: str) -> List[Dict]:
        results = []
        for name, data in self.nodes.items():
            if query.lower() in name.lower() or query.lower() in str(data["meta"]).lower():
                results.append({"name": name, "data": data})
        return results

class RepoAnalyst:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.trace_log: List[str] = []

    def log_step(self, msg: str):
        self.trace_log.append(msg)

    def analyze_chunk(self, content: str, source: str):
        """
        Extracts entities and adds to graph with heuristics.
        """
        lines = content.split('\n')
        imports = []
        functions = []
        classes = []
        
        for line in lines:
            line = line.strip()
            # Imports / Dependencies
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
                # Try to extract the module name
                parts = line.split()
                target_module = ""
                if line.startswith('from '):
                    target_module = parts[1]
                else:
                    target_module = parts[1].split('.')[0]
                
                if target_module and target_module not in ["os", "sys", "json", "typing", "requests"]:
                    self.graph.add_edge(source, target_module, "depends_on")

            # Classes
            elif line.startswith('class '):
                try:
                    name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    classes.append(name)
                    self.graph.add_node(name, "class", {"source": source, "complexity": 1})
                except:
                    pass
            # Functions
            elif line.startswith('def '):
                try:
                    name = line.split('def ')[1].split('(')[0].strip()
                    functions.append(name)
                    self.graph.add_node(name, "function", {"source": source, "complexity": 1})
                except:
                    pass

        # Heuristic: file responsibility
        file_complexity = len(imports) + len(functions) + len(classes)
        role = "worker"
        if len(imports) > 5:
            role = "coordinator"
        elif len(classes) > 2:
            role = "god_object_candidate"
        
        self.graph.add_node(source, "file", {
            "role": role, 
            "imports": len(imports),
            "complexity": file_complexity
        })
        
        self.log_step(f"Analyzed {source}: Found {len(classes)} classes, {len(functions)} functions. Role: {role}")

    def get_insights(self, query: str) -> str:
        hits = self.graph.find_related(query)
        if not hits:
            return "No specific code entities found matching that query."
        
        summary = "Analysis Results:\n"
        for h in hits:
            meta = h['data']['meta']
            summary += f"- [{h['data']['type'].upper()}] {h['name']} ({meta.get('role', 'standard')})\n"
            if 'complexity' in meta:
                 summary += f"  (Complexity: {meta['complexity']}/10)\n"
        return summary

    def get_smells(self) -> List[str]:
        smells = []
        for name, node in self.graph.nodes.items():
            if node['type'] == 'file' and node['meta'].get('complexity', 0) > 10:
                smells.append(f"High Complexity Module: {name} (Score: {node['meta']['complexity']})")
            if node['type'] == 'file' and node['meta'].get('role') == 'god_object_candidate':
                smells.append(f"God Object Risk: {name} handles too many classes.")
        return smells if smells else ["Codebase appears clean based on current heuristics."]

    def get_blueprint(self) -> str:
        """
        Generates a Mermaid-compatible dependency graph.
        """
        if not self.graph.edges:
            return "Insufficient structural data for blueprint."
        
        mermaid = "graph TD\n"
        for edge in self.graph.edges:
            s = edge['source'].replace('/', '_').replace('.', '_')
            t = edge['target'].replace('/', '_').replace('.', '_')
            mermaid += f"  {s} --> {t}\n"
        return f"```mermaid\n{mermaid}\n```"
