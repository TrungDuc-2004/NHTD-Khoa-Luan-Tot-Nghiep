# utils/logger.py

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# file log mới mỗi ngày
LOG_FILE = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("KeywordLogger")

def create_session_log():
    logger.info("========== NEW SESSION STARTED ==========")
