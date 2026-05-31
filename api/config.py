"""
Application configuration.
"""
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3366/vitality")

# Model
CHECKPOINT_PATH = os.path.join(BASE_DIR, "checkpoints", "best_model.pth")
IMAGE_SIZE = 224
