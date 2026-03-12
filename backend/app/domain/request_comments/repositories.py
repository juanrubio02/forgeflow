from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.request_comments.entities import RequestComment


class RequestCommentRepository(ABC):
    @abstractmethod
    async def add(self, comment: RequestComment) -> RequestComment:
        raise NotImplementedError

    @abstractmethod
    async def list_by_request_id(self, request_id: UUID) -> list[RequestComment]:
        raise NotImplementedError

    @abstractmethod
    async def save_changes(self) -> None:
        raise NotImplementedError

