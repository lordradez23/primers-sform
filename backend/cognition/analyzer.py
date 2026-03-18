
from typing import List, Dict
from cognition.models import AnalysisResult

class CodeAnalyzer:
    """
    LAYER 1: ANALYSIS
    Pure data extraction. No opinions.
    """
    def __init__(self):
        self.raw_data: Dict[str, AnalysisResult] = {}

    def analyze(self, content: str, source: str) -> AnalysisResult:
        import ast
        
        lines = content.split('\n')
        result = AnalysisResult(source=source, loc=len(lines), raw_content=content)
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fallback to empty or naive for non-Python or broken files
            print(f"SyntaxError parsing {source}")
            return result

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result.imports.append(f"import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        result.imports.append(f"from {module} import {alias.name}")
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Only top-level functions (not methods inside classes for this list, 
                # unless we want flat listing. Let's keep distinct.)
                # Actually, ast.walk hits all nodes. We need context.
                # Let's iterate body of Module instead.
                pass
        
        # Proper recursive-ish extraction from Module body
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.functions.append(self._extract_function(node))
            elif isinstance(node, ast.ClassDef):
                result.classes.append(self._extract_class(node))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                # Already handled? No, let's do imports here to be safe and clean.
                 if isinstance(node, ast.Import):
                    for alias in node.names:
                        result.imports.append(f"import {alias.name}")
                 elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        result.imports.append(f"from {module} import {alias.name}")

        self.raw_data[source] = result
        return result

    def _extract_function(self, node) -> 'FunctionInfo':
        import ast
        from cognition.models import FunctionInfo
        
        args = [a.arg for a in node.args.args]
        is_async = isinstance(node, ast.AsyncFunctionDef)
        docstring = ast.get_docstring(node) is not None
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        # Simple complexity heuristic: count branches
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1

        return FunctionInfo(
            name=node.name,
            args=args,
            docstring=docstring,
            is_async=is_async,
            decorators=decorators,
            complexity=complexity
        )

    def _extract_class(self, node) -> 'ClassInfo':
        import ast
        from cognition.models import ClassInfo
        
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_function(item))
        
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id if hasattr(base.value, 'id') else '?'}.{base.attr}")
                
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        docstring = ast.get_docstring(node) is not None
        
        return ClassInfo(
            name=node.name,
            bases=bases,
            methods=methods,
            docstring=docstring,
            decorators=decorators
        )

    def _get_decorator_name(self, node):
        import ast
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
             return self._get_decorator_name(node.func)
        elif isinstance(node, ast.Attribute):
             return f"{self._get_decorator_name(node.value)}.{node.attr}"
        return "decorator"

    def get_corpus_stats(self) -> Dict[str, float]:
        """Calculates baseline averages for the current corpus."""
        if not self.raw_data:
            return {"avg_complexity": 0, "avg_imports": 0}
        
        total_complexity = 0
        total_imports = 0
        count = len(self.raw_data)

        for res in self.raw_data.values():
            # Rough complexity metric for baseline calculation
            comp = len(res.classes) + len(res.functions) + len(res.imports)
            total_complexity += comp
            total_imports += len(res.imports)
        
        return {
            "avg_complexity": total_complexity / count,
            "avg_imports": total_imports / count
        }
