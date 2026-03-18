
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    docstring: bool
    is_async: bool
    decorators: List[str]
    complexity: int = 1

@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    methods: List[FunctionInfo]
    docstring: bool
    decorators: List[str]

@dataclass
class AnalysisResult:
    source: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    loc: int = 0
    raw_content: str = ""

@dataclass
class Interpretation:
    source: str
    complexity_score: float
    role: str  # 'worker', 'coordinator', 'god_object_candidate'
    smells: List[str] = field(default_factory=list)
    relative_complexity: float = 1.0 # 2.4x baseline, etc.

@dataclass
class RefactorPlan:
    goal: str
    steps: List[str]
    risk: str # 'Low', 'Medium', 'High'
    expected_gain: str
    current_code: Optional[str] = None
    proposed_code: Optional[str] = None

@dataclass
class Judgement:
    summary: str
    risks: List[str]
    recommendations: List[str]
    refactor_plan: Optional[RefactorPlan] = None
    confidence_score: float = 0.0

@dataclass
class DiffPoint:
    metric: str
    target_a_val: float
    target_b_val: float
    delta_percent: float

@dataclass
class ComparisonResult:
    target_a: str
    target_b: str
    diffs: List[DiffPoint]
    winner: str # 'target_a', 'target_b', 'tie'
    rationale: str
