
import sys
import os

# Set up paths for the Sovereign Engine
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.engine import PrimersEngine

# Load the foundational knowledge markdown
md_path = os.path.join(os.getcwd(), 'primers_ingestion_core.md')
with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Initialize Engine
engine = PrimersEngine()

# Use the UPLOAD intent (processed as special command)
# This will persist the knowledge to M2 (KnowledgeStore)
cmd = f"upload file: primers_ingestion_core.md\ncontent: {content}"
response = engine.process(cmd)

print(f"Outcome: {response.content}")
print(f"Factual memory initialized for 8 core Prime strategic modules.")
