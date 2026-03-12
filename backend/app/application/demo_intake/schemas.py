from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.document_processing_results.document_types import DocumentDetectedType
from app.domain.requests.sources import RequestSource


class DemoIntakeScenarioReadModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    title: str
    source: RequestSource
    sender: str
    expected_document_type: DocumentDetectedType
    attachments: int
    description: str


class DemoIntakeRunResultReadModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    request_id: UUID
    document_ids: list[UUID]
    scenario_key: str

