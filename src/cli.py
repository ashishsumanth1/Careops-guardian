"""Command-line interface for CareOps Guardian."""

import argparse

from .guardian import generate_guardian_report
from .rag_pipeline import answer_question


def _handle_care_query(service_user_id: str, question_parts: list[str]) -> None:
    question_text = " ".join(question_parts)
    response = answer_question(service_user_id, question_text)

    print(f"Service User: {service_user_id.upper()}")
    print(f"Question: {question_text}")
    print("Answer:\n")
    print(response)


def _handle_incident_report(incident_id: str) -> None:
    report = generate_guardian_report(incident_id)
    print(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="CareOps Guardian CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    care_parser = subparsers.add_parser("care", help="Ask a question about a service user")
    care_parser.add_argument("service_user_id", help="Service user ID, e.g. SU001")
    care_parser.add_argument("question", nargs="+", help="Question to ask about the service user")

    incident_parser = subparsers.add_parser("incident", help="Generate a QA report for an incident ID")
    incident_parser.add_argument("incident_id", help="Incident ID, e.g. INC001016")

    args = parser.parse_args()

    if args.command == "care":
        _handle_care_query(args.service_user_id, args.question)
    elif args.command == "incident":
        _handle_incident_report(args.incident_id)
    else:  # pragma: no cover
        parser.error("Unknown command")


if __name__ == "__main__":
    main()