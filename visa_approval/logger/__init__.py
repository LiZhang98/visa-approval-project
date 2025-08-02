import logging
import os

from from_root import from_root
from datetime import datetime
from pathlib import Path

def get_project_root() -> Path:
    """Get the root directory of the project."""
    return Path(__file__).resolve().parent.parent.parent

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

log_dir = 'logs'

logs_path = os.path.join(get_project_root(), log_dir, LOG_FILE)

os.makedirs(os.path.join(get_project_root(), log_dir), exist_ok=True)



logging.basicConfig(
    filename=logs_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
