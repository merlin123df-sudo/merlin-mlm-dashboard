# Streamlit Cloud expects streamlit_app.py or app.py
# This module imports app.py as a normal Python module instead of exec'ing it.
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import app  # noqa: F401
