# Streamlit Cloud expects streamlit_app.py or app.py
# This is a symlink reference to app.py
import sys
from pathlib import Path

# Import from app.py
app_path = Path(__file__).parent / "app.py"
exec(open(app_path).read())
