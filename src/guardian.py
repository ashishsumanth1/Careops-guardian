"""Guardian orchestration combining rules and RAG for incident QA."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .config import CHAT_MODEL_NAME, INCIDENTS_CSV
from .incidents import Incident, load_incidents
from .rag_pipeline import answer_question
from .rules import count_high_severity_by_user, find_frequent_fallers, summarise_rules


@lru_cache(maxsize=1)
def _all_incidents() -> List[Incident]:
    return load_incidents(INCIDENTS_CSV)


def get_incident_by_id(incident_id: str) -> Incident:
    """Return a single incident by ID or raise ValueError."""

    for incident in _all_incidents():
        if incident.incident_id == incident_id:
            return incident
    raise ValueError(f"Incident '{incident_id}' not found")


def build_context_for_incident(incident_id: str) -> Dict[str, object]:
    """Assemble rule results and RAG summary for an incident."""

    incidents = _all_incidents()
    incident = get_incident_by_id(incident_id)
    service_user_id = incident.service_user_id

    frequent_fallers = set(find_frequent_fallers(incidents))
    high_severity_counts = count_high_severity_by_user(incidents)

    service_user_summary = answer_question(
        service_user_id,
        (
            "Summarise this person's care plan, key risks, and control measures. "
            "Focus on falls, behaviour, medication, and any safeguarding instructions."
        ),
    )

    return {
        "incident": incident,
        "service_user_summary": service_user_summary,
        "is_frequent_faller": service_user_id in frequent_fallers,
        "high_severity_count": high_severity_counts.get(service_user_id, 0),
        "global_rules_summary": summarise_rules(),
    }


def generate_guardian_report(incident_id: str) -> str:
    """Combine incident details, rules, and RAG into a QA report."""

    ctx = build_context_for_incident(incident_id)
    incident: Incident = ctx["incident"]
    llm = ChatOpenAI(model=CHAT_MODEL_NAME, temperature=0)

    system_message = SystemMessage(
        content=(
            "You are a QA assistant for a domiciliary care provider. "
            "Given an incident, service-user care summary, and rule-based flags, produce: "
            "1) short narrative summary, 2) bullet risks/controls, 3) follow-up actions."
        )
    )

    user_message = HumanMessage(
        content=(
            f"Incident ID: {incident.incident_id}\n"
            f"Service User ID: {incident.service_user_id}\n"
            f"Date: {incident.date} {incident.time}\n"
            f"Location: {incident.location}\n"
            f"Category: {incident.category} | Severity: {incident.severity}\n"
            f"Brief: {incident.brief_description}\n"
            f"Body: {incident.body_text}\n\n"
            f"Service user summary: {ctx['service_user_summary']}\n\n"
            f"Frequent faller flag: {ctx['is_frequent_faller']}\n"
            f"High severity incidents on record: {ctx['high_severity_count']}\n\n"
            "Global rules overview:\n"
            f"{ctx['global_rules_summary']}"
        )
    )

    response = llm.invoke([system_message, user_message])
    return getattr(response, "content", str(response))


if __name__ == "__main__":
    example_id = _all_incidents()[0].incident_id if _all_incidents() else ""
    if not example_id:
        raise SystemExit("No incidents available to summarise.")
    print(generate_guardian_report(example_id))