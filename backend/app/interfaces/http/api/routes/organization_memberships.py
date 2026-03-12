from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.organization_memberships.commands import CreateOrganizationMembershipCommand
from app.application.organization_memberships.schemas import (
    OrganizationMembershipOptionReadModel,
    OrganizationMembershipReadModel,
)
from app.application.organization_memberships.services import (
    CreateOrganizationMembershipUseCase,
    GetOrganizationMembershipUseCase,
    ListOrganizationMembershipsUseCase,
)
from app.application.auth.schemas import AuthenticatedMembershipReadModel
from app.infrastructure.database.session import get_db_session
from app.infrastructure.organization_memberships.repositories import (
    SqlAlchemyOrganizationMembershipRepository,
)
from app.infrastructure.organizations.repositories import SqlAlchemyOrganizationRepository
from app.infrastructure.users.repositories import SqlAlchemyUserRepository
from app.interfaces.http.dependencies import get_current_membership
from app.interfaces.http.schemas.organization_memberships import (
    CreateOrganizationMembershipRequest,
)

router = APIRouter(prefix="/organizations/{organization_id}/memberships", tags=["memberships"])


@router.post("", response_model=OrganizationMembershipReadModel, status_code=status.HTTP_201_CREATED)
async def create_organization_membership(
    organization_id: UUID,
    payload: CreateOrganizationMembershipRequest,
    session: AsyncSession = Depends(get_db_session),
) -> OrganizationMembershipReadModel:
    membership_repository = SqlAlchemyOrganizationMembershipRepository(session=session)
    organization_repository = SqlAlchemyOrganizationRepository(session=session)
    user_repository = SqlAlchemyUserRepository(session=session)
    use_case = CreateOrganizationMembershipUseCase(
        organization_membership_repository=membership_repository,
        organization_repository=organization_repository,
        user_repository=user_repository,
    )
    command = CreateOrganizationMembershipCommand(
        organization_id=organization_id,
        user_id=payload.user_id,
        role=payload.role,
    )
    return await use_case.execute(command)


@router.get("/{membership_id}", response_model=OrganizationMembershipReadModel)
async def get_organization_membership(
    organization_id: UUID,
    membership_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> OrganizationMembershipReadModel:
    repository = SqlAlchemyOrganizationMembershipRepository(session=session)
    use_case = GetOrganizationMembershipUseCase(
        organization_membership_repository=repository,
    )
    return await use_case.execute(
        organization_id=organization_id,
        membership_id=membership_id,
    )


@router.get("", response_model=list[OrganizationMembershipOptionReadModel])
async def list_organization_memberships(
    organization_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_membership: AuthenticatedMembershipReadModel = Depends(get_current_membership),
) -> list[OrganizationMembershipOptionReadModel]:
    if current_membership.organization_id != organization_id:
        return []

    membership_repository = SqlAlchemyOrganizationMembershipRepository(session=session)
    user_repository = SqlAlchemyUserRepository(session=session)
    use_case = ListOrganizationMembershipsUseCase(
        organization_membership_repository=membership_repository,
        user_repository=user_repository,
    )
    return await use_case.execute(organization_id=organization_id)
