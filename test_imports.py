import os
import sys

# Add backend to sys.path
backend_path = os.path.join(os.getcwd(), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from core.engine import PrimersEngine
    print("SUCCESS: core.engine imported successfully")
    engine = PrimersEngine()
    print("SUCCESS: PrimersEngine initialized successfully")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
