
import sys
import os

# Set up paths for the Sovereign Engine
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.engine import PrimersEngine

# Initialize Engine
engine = PrimersEngine()

# Query with the new context
queries = [
    "Who are the founders of Primers?",
    "What is the Primers OS?",
    "Describe the intelligence personality framework.",
    "What is the long-term vision of Primers?"
]

print("## SOVEREIGN ENGINE VERIFICATION ##\n")
for q in queries:
    res = engine.process(q)
    print(f"Q: {q}")
    print(f"A: {res.content}\n")
    print("-" * 50)
