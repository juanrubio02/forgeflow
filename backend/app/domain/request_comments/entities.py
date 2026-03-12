from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestComment:
    id: UUID
    request_id: UUID
    organization_id: UUID
    membership_id: UUID
    body: str
    created_at: datetime
    updated_at: datetime

