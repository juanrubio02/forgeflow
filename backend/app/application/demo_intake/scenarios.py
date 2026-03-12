import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.domain.document_processing_results.document_types import DocumentDetectedType
from app.domain.requests.sources import RequestSource


@dataclass(frozen=True, slots=True)
class DemoScenarioAttachment:
    filename: str
    content_type: str
    template_kind: str
    content: str


@dataclass(frozen=True, slots=True)
class DemoIntakeScenario:
    key: str
    title: str
    source: RequestSource
    sender: str
    subject: str
    body: str
    expected_document_type: DocumentDetectedType
    description: str
    initial_comment: str | None
    attachments: tuple[DemoScenarioAttachment, ...]


@lru_cache(maxsize=1)
def load_demo_intake_scenarios() -> dict[str, DemoIntakeScenario]:
    base_dir = Path(__file__).resolve().parents[3] / "demo_data" / "intake_scenarios"
    scenarios: dict[str, DemoIntakeScenario] = {}

    for scenario_file in sorted(base_dir.glob("*.json")):
        payload = json.loads(scenario_file.read_text())
        attachments = tuple(
            DemoScenarioAttachment(
                filename=item["filename"],
                content_type=item["content_type"],
                template_kind=item["template_kind"],
                content=item["content"],
            )
            for item in payload["attachments"]
        )
        scenario = DemoIntakeScenario(
            key=payload["key"],
            title=payload["title"],
            source=RequestSource(payload["source"]),
            sender=payload["sender"],
            subject=payload["subject"],
            body=payload["body"],
            expected_document_type=DocumentDetectedType(payload["expected_document_type"]),
            description=payload["description"],
            initial_comment=payload.get("initial_comment"),
            attachments=attachments,
        )
        scenarios[scenario.key] = scenario

    return scenarios
