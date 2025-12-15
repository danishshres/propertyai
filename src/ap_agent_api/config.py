import os
from dotenv import load_dotenv
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
PROPERTY_RESULTS_DIR = BASE_DIR / "property_results"

load_dotenv(dotenv_path=os.path.join(os.path.abspath(BASE_DIR), ".env"))
