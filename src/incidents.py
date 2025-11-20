"""Incident model and loader for CareOps Guardian."""

from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
from typing import List

import pandas as pd
from pydantic import BaseModel

from .config import INCIDENTS_CSV


class Incident(BaseModel):
    """Typed representation of a single incident record."""

    incident_id: str
    service_user_id: str
    date: date
    time: time
    location: str
    brief_description: str
    body_text: str
    severity: str
    category: str


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def load_incidents(csv_path: Path) -> List[Incident]:
    """Load incidents from CSV into typed Incident objects."""

    df = pd.read_csv(csv_path)
    incidents: List[Incident] = []

    for _, row in df.iterrows():
        incidents.append(
            Incident(
                incident_id=row["incident_id"],
                service_user_id=row["service_user_id"],
                date=_parse_date(row["date"]),
                time=_parse_time(row["time"]),
                location=row["location"],
                brief_description=row["brief_description"],
                body_text=row["body_text"],
                severity=row["severity"],
                category=row["category"],
            )
        )
    return incidents


if __name__ == "__main__":
    incident_list = load_incidents(INCIDENTS_CSV)
    print(f"Loaded {len(incident_list)} incidents from {INCIDENTS_CSV}.")
    for incident in incident_list[:3]:
        print(incident)
