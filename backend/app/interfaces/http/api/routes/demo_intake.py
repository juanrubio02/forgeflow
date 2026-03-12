from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.schemas import AuthenticatedMembershipReadModel
from app.application.demo_intake.schemas import (
    DemoIntakeRunResultReadModel,
    DemoIntakeScenarioReadModel,
)
from app.application.demo_intake.services import (
    ListDemoIntakeScenariosUseCase,
    RunDemoIntakeScenarioUseCase,
)
from app.application.documents.processing import DocumentProcessingDispatcher
from app.application.documents.storage import DocumentStorage
from app.application.documents.services import (
    CreateDocumentUseCase,
    EnqueueDocumentProcessingUseCase,
    UploadDocumentUseCase,
)
from app.application.request_comments.services import CreateRequestCommentUseCase
from app.application.requests.services import CreateRequestUseCase
from app.infrastructure.database.session import get_db_session
from app.infrastructure.documents.repositories import SqlAlchemyDocumentRepository
from app.infrastructure.organization_memberships.repositories import (
    SqlAlchemyOrganizationMembershipRepository,
)
from app.infrastructure.organizations.repositories import SqlAlchemyOrganizationRepository
from app.infrastructure.request_activities.repositories import SqlAlchemyRequestActivityRepository
from app.infrastructure.request_comments.repositories import SqlAlchemyRequestCommentRepository
from app.infrastructure.requests.repositories import SqlAlchemyRequestRepository
from app.interfaces.http.dependencies import (
    get_current_membership,
    get_document_processing_dispatcher,
    get_document_storage,
)

router = APIRouter(prefix="/demo/intake", tags=["demo-intake"])


@router.get("/scenarios", response_model=list[DemoIntakeScenarioReadModel])
async def list_demo_intake_scenarios(
    current_membership: AuthenticatedMembershipReadModel = Depends(get_current_membership),
) -> list[DemoIntakeScenarioReadModel]:
    use_case = ListDemoIntakeScenariosUseCase()
    return use_case.execute()


@router.post(
    "/scenarios/{scenario_key}/run",
    response_model=DemoIntakeRunResultReadModel,
    status_code=status.HTTP_201_CREATED,
)
async def run_demo_intake_scenario(
    scenario_key: str,
    session: AsyncSession = Depends(get_db_session),
    current_membership: AuthenticatedMembershipReadModel = Depends(get_current_membership),
    document_storage: DocumentStorage = Depends(get_document_storage),
    document_processing_dispatcher: DocumentProcessingDispatcher = Depends(
        get_document_processing_dispatcher
    ),
) -> DemoIntakeRunResultReadModel:
    request_repository = SqlAlchemyRequestRepository(session=session)
    document_repository = SqlAlchemyDocumentRepository(session=session)
    membership_repository = SqlAlchemyOrganizationMembershipRepository(session=session)
    organization_repository = SqlAlchemyOrganizationRepository(session=session)
    activity_repository = SqlAlchemyRequestActivityRepository(session=session)
    request_comment_repository = SqlAlchemyRequestCommentRepository(session=session)

    create_request_use_case = CreateRequestUseCase(
        request_repository=request_repository,
        request_activity_repository=activity_repository,
        organization_repository=organization_repository,
        organization_membership_repository=membership_repository,
    )
    create_document_use_case = CreateDocumentUseCase(
        document_repository=document_repository,
        request_repository=request_repository,
        organization_membership_repository=membership_repository,
        request_activity_repository=activity_repository,
    )
    upload_document_use_case = UploadDocumentUseCase(
        document_storage=document_storage,
        create_document_use_case=create_document_use_case,
    )
    enqueue_document_processing_use_case = EnqueueDocumentProcessingUseCase(
        document_repository=document_repository,
        document_processing_dispatcher=document_processing_dispatcher,
    )
    create_request_comment_use_case = CreateRequestCommentUseCase(
        request_repository=request_repository,
        request_comment_repository=request_comment_repository,
        request_activity_repository=activity_repository,
    )
    use_case = RunDemoIntakeScenarioUseCase(
        create_request_use_case=create_request_use_case,
        upload_document_use_case=upload_document_use_case,
        enqueue_document_processing_use_case=enqueue_document_processing_use_case,
        create_request_comment_use_case=create_request_comment_use_case,
    )
    return await use_case.execute(
        scenario_key=scenario_key,
        organization_id=current_membership.organization_id,
        membership_id=current_membership.id,
    )
