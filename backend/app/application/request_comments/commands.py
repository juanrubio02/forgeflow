from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateRequestCommentCommand(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    organization_id: UUID
    membership_id: UUID
    body: str = Field(min_length=1, max_length=10000)

