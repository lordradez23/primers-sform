
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.engine import PrimersEngine

engine = PrimersEngine()
msg = "upload file: test.txt\ncontent: This is a test file content."
response = engine.process(msg)

print(f"Response Content: {response.content}")
print(f"Intent: {response.intent}")
