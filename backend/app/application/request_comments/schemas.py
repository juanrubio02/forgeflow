from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RequestCommentReadModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    request_id: UUID
    organization_id: UUID
    membership_id: UUID
    body: str
    created_at: datetime
    updated_at: datetime

