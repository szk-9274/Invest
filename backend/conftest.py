"""
Pytest configuration for backend tests.

Ensures the backend directory is first on sys.path so that
'from main import app' imports from backend/main.py and not python/main.py.
"""
import sys
from pathlib import Path

# Insert backend directory at the VERY beginning of sys.path
_backend_dir = str(Path(__file__).parent)

# Remove python dir if it was already added (to prevent collision)
_python_dir = str(Path(__file__).parent.parent / "python")

# Clear any cached 'main' module from python/
if 'main' in sys.modules:
    del sys.modules['main']

# Remove backend and python dirs, then re-insert in correct order
for p in [_backend_dir, _python_dir]:
    while p in sys.path:
        sys.path.remove(p)

# Backend first, python second
sys.path.insert(0, _backend_dir)
sys.path.append(_python_dir)
