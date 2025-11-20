"""Risk rules and analytics over incidents."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

from .config import INCIDENTS_CSV, RISK_ASSESSMENTS_DIR
from .incidents import Incident, load_incidents


def _is_fall_category(category: str) -> bool:
    lowered = category.strip().lower()
    return "fall" in lowered


def find_frequent_fallers(
    incidents: List[Incident],
    threshold: int = 3,
    window_days: int = 30,
) -> List[str]:
    """Service users with more than `threshold` falls in the recent window."""

    if not incidents:
        return []

    most_recent: date = max(incident.date for incident in incidents)
    window_start = most_recent - timedelta(days=window_days)

    fall_counts: Dict[str, int] = defaultdict(int)
    for incident in incidents:
        if _is_fall_category(incident.category) and window_start <= incident.date <= most_recent:
            fall_counts[incident.service_user_id] += 1

    return [su_id for su_id, count in fall_counts.items() if count > threshold]


def count_high_severity_by_user(incidents: List[Incident]) -> Dict[str, int]:
    """Count high severity incidents per service user."""

    counts: Dict[str, int] = defaultdict(int)
    for incident in incidents:
        if incident.severity.strip().lower() == "high":
            counts[incident.service_user_id] += 1
    return dict(counts)


def users_with_falls_but_no_falls_assessment() -> List[str]:
    """Service users with falls incidents but missing falls risk assessment files."""

    incidents = load_incidents(INCIDENTS_CSV)
    fallers = {inc.service_user_id for inc in incidents if _is_fall_category(inc.category)}

    missing: List[str] = []
    for su_id in sorted(fallers):
        expected_file = RISK_ASSESSMENTS_DIR / f"{su_id}_falls_risk.md"
        if not expected_file.exists():
            missing.append(su_id)
    return missing


def summarise_rules() -> str:
    """Run rule checks and return a textual summary."""

    incidents = load_incidents(INCIDENTS_CSV)
    frequent_fallers = find_frequent_fallers(incidents)
    high_severity_counts = count_high_severity_by_user(incidents)
    missing_falls = users_with_falls_but_no_falls_assessment()

    lines = [
        "CareOps Guardian Risk Summary",
        "================================",
        f"Total incidents reviewed: {len(incidents)}",
        "",
        "Frequent fallers (>{} falls in last 30 days):".format(3),
        "  - " + ", ".join(frequent_fallers) if frequent_fallers else "  None flagged",
        "",
        "High severity incidents per service user:",
    ]

    if high_severity_counts:
        for su_id, count in sorted(high_severity_counts.items(), key=lambda x: x[0]):
            lines.append(f"  - {su_id}: {count}")
    else:
        lines.append("  None recorded")

    lines.extend(
        [
            "",
            "Service users with falls but missing falls risk assessment:",
            "  - " + ", ".join(missing_falls) if missing_falls else "  All fallers have assessments",
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(summarise_rules())