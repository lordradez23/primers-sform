
import sys
import os

# Add current directory to path
sys.path.append(os.path.abspath("backend"))

from core.engine import PrimersEngine

def test_system():
    engine = PrimersEngine()
    
    print("\n--- TEST 1: INGESTION ---")
    # Ingest the backend directory itself
    resp = engine.process("ingest backend")
    print(f"[{resp.intent}] {resp.content}")
    
    if resp.intent != "ingestion":
        print("Ingestion failed!")
        return

    print("\n--- TEST 2: ANALYSIS ---")
    # Analyze the ingested corpus
    resp = engine.process("analyze corpus")
    print(f"[{resp.intent}] {resp.content}")
    
    print("\n--- TEST 3: COMPARISON ---")
    # Compare two known files
    # Note: filenames in raw_data are relative to ingested path
    # e.g. "core/engine.py" vs "cognition/comparator.py"
    # On Windows, relpath uses backslashes
    import os
    sep = os.sep
    file_a = f"core{sep}engine.py"
    file_b = f"cognition{sep}comparator.py"
    
    resp = engine.process(f"compare {file_a} vs {file_b}")
    print(f"[{resp.intent}] {resp.content}")

    print("\n--- TEST 4: GITHUB LEARNING ---")
    # Test learning from GitHub (using octocat)
    resp = engine.process("learn from github octocat")
    print(f"[{resp.intent}] {resp.content}")

if __name__ == "__main__":
    test_system()
