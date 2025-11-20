"""Central configuration for data paths and model defaults."""

from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
CARE_PLANS_DIR: Path = DATA_DIR / "care_plans"
RISK_ASSESSMENTS_DIR: Path = DATA_DIR / "risk_assessments"
INCIDENTS_CSV: Path = DATA_DIR / "incidents.csv"
CHROMA_DIR: Path = BASE_DIR / ".chroma_db"

CHAT_MODEL_NAME: str = "gpt-4o-mini"
EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"

__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "CARE_PLANS_DIR",
    "RISK_ASSESSMENTS_DIR",
    "INCIDENTS_CSV",
    "CHROMA_DIR",
    "CHAT_MODEL_NAME",
    "EMBEDDING_MODEL_NAME",
]
