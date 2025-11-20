"""Streamlit UI for CareOps Guardian."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.build_vector_store import build_vector_store
from src.config import CARE_PLANS_DIR, CHROMA_DIR, INCIDENTS_CSV
from src.guardian import generate_guardian_report
from src.incidents import load_incidents
from src.rag_pipeline import answer_question
from src.rules import summarise_rules

load_dotenv()

st.set_page_config(
    page_title="CareOps Guardian",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def get_service_user_ids() -> List[str]:
    """Return all available service-user IDs based on care-plan files."""

    ids: set[str] = set()
    if CARE_PLANS_DIR.exists():
        for path in CARE_PLANS_DIR.glob("*.md"):
            ids.add(path.stem.split("_")[0].upper())
    return sorted(ids)


@st.cache_data(show_spinner=False)
def get_incident_records() -> List[Dict[str, str]]:
    """Load incident metadata for quick selection in the UI."""

    incidents = load_incidents(INCIDENTS_CSV)
    records: List[Dict[str, str]] = []
    for incident in incidents:
        records.append(
            {
                "incident_id": incident.incident_id,
                "service_user_id": incident.service_user_id,
                "date": incident.date.isoformat(),
                "time": incident.time.strftime("%H:%M"),
                "category": incident.category,
                "severity": incident.severity,
                "location": incident.location,
                "brief": incident.brief_description,
            }
        )
    records.sort(key=lambda rec: (rec["date"], rec["time"]), reverse=True)
    return records


@st.cache_data(show_spinner=False)
def get_rules_snapshot() -> str:
    """Return the latest textual summary of rule results."""

    return summarise_rules()


def _format_incident_option(record: Dict[str, str]) -> str:
    return (
        f"{record['incident_id']} · {record['service_user_id']} · "
        f"{record['category']} ({record['severity']}) on {record['date']}"
    )


def _vector_store_ready() -> bool:
    if not CHROMA_DIR.exists():
        return False
    try:
        next(CHROMA_DIR.iterdir())
        return True
    except StopIteration:
        return False


def _ensure_vector_store() -> bool:
    if _vector_store_ready():
        return True
    if not os.environ.get("OPENAI_API_KEY"):
        st.sidebar.error("OPENAI_API_KEY missing; cannot build vector store.")
        return False
    try:
        with st.spinner("Building vector store (one-off)..."):
            build_vector_store(CHROMA_DIR)
    except Exception as exc:  # pragma: no cover - safety
        st.sidebar.error(f"Vector store build failed: {exc}")
        return False
    return True


service_users = get_service_user_ids()
incident_records = get_incident_records()

st.sidebar.header("Dataset status")
st.sidebar.metric("Service users", len(service_users) or "–")
st.sidebar.metric("Incidents", len(incident_records) or "–")

if not os.environ.get("OPENAI_API_KEY"):
    st.sidebar.error("OPENAI_API_KEY not found in environment.")

vector_store_ready = _ensure_vector_store()
if not vector_store_ready:
    st.sidebar.warning("Vector store unavailable. Add OPENAI_API_KEY or pre-build locally.")

st.title("CareOps Guardian UI")
st.caption("Prototype console-to-UI bridge for care queries, rule insights, and QA reports.")

if not vector_store_ready:
    st.warning("Vector store unavailable, so RAG-powered features are disabled until embeddings exist.")

care_tab, incident_tab, rules_tab = st.tabs(
    ["Care Q&A", "Incident QA", "Risk Rules"]
)

with care_tab:
    st.subheader("Ask about a service user")

    if not vector_store_ready:
        st.info("Build the vector store or provide OPENAI_API_KEY to enable care queries.")
    elif not service_users:
        st.info("No care plans found under data/care_plans. Generate data first.")
    else:
        selected_user = st.selectbox(
            "Service user",
            service_users,
            index=0,
            key="care_service_user",
        )
        question_text = st.text_area(
            "Question",
            value="Summarise transfers and falls risk",
            height=120,
            key="care_question",
        )

        if st.button("Generate care answer", type="primary", key="care_submit"):
            if not question_text.strip():
                st.warning("Please enter a question to ask.")
            else:
                with st.spinner("Running RAG pipeline..."):
                    try:
                        response = answer_question(selected_user, question_text.strip())
                    except Exception as exc:  # pragma: no cover - runtime safeguard
                        st.error(f"Failed to generate answer: {exc}")
                    else:
                        st.session_state["care_result"] = {
                            "service_user": selected_user,
                            "question": question_text.strip(),
                            "answer": response,
                        }

        if care_result := st.session_state.get("care_result"):
            st.markdown(
                f"**Service user:** {care_result['service_user']}  \
**Question:** {care_result['question']}"
            )
            st.markdown("---")
            st.markdown(care_result["answer"])

with incident_tab:
    st.subheader("Generate an incident QA report")

    if not vector_store_ready:
        st.info("Build the vector store or provide OPENAI_API_KEY to enable Guardian reports.")
    elif not incident_records:
        st.info("No incidents found. Generate dataset first.")
    else:
        selected_incident = st.selectbox(
            "Incident",
            incident_records,
            format_func=_format_incident_option,
            key="incident_select",
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Service user", selected_incident["service_user_id"])
        col2.metric("Severity", selected_incident["severity"])
        col3.metric("Category", selected_incident["category"])
        st.caption(f"Location: {selected_incident['location']} · {selected_incident['date']} {selected_incident['time']}")
        st.write(selected_incident["brief"])

        if st.button("Generate QA report", type="primary", key="incident_submit"):
            with st.spinner("Calling Guardian orchestrator..."):
                try:
                    report = generate_guardian_report(selected_incident["incident_id"])
                except Exception as exc:  # pragma: no cover - runtime safeguard
                    st.error(f"Failed to generate report: {exc}")
                else:
                    st.session_state["incident_report"] = {
                        "incident_id": selected_incident["incident_id"],
                        "report": report,
                    }

        if incident_result := st.session_state.get("incident_report"):
            st.markdown(f"**Incident ID:** {incident_result['incident_id']}")
            st.markdown("---")
            st.markdown(incident_result["report"])

with rules_tab:
    st.subheader("Rule snapshot")
    st.caption("Outputs from deterministic analytics over the incident dataset.")

    if st.button("Refresh rules snapshot", key="rules_refresh"):
        get_rules_snapshot.clear()

    snapshot = get_rules_snapshot()
    st.code(snapshot or "No rule summary available.")
