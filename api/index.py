import os
import sys

# Add the backend directory to the path so modules like 'core', 'cognition' etc are found
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_path)

# Now import from main.py which is inside the backend directory
from main import app as fastapi_app

app = fastapi_app
