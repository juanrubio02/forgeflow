from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.domain.requests.sources import RequestSource
from app.domain.requests.statuses import RequestStatus


async def _create_organization(api_client: AsyncClient, name: str, slug: str) -> dict:
    response = await api_client.post("/organizations", json={"name": name, "slug": slug})
    assert response.status_code == 201
    return response.json()


async def _create_user(
    api_client: AsyncClient,
    email: str,
    full_name: str,
    password: str = "StrongPass123!",
) -> dict:
    response = await api_client.post(
        "/users",
        json={"email": email, "full_name": full_name, "password": password},
    )
    assert response.status_code == 201
    return response.json()


async def _login(
    api_client: AsyncClient,
    email: str,
    password: str = "StrongPass123!",
) -> dict:
    response = await api_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def _membership_headers(access_token: str, membership_id: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "X-Membership-Id": membership_id,
    }


async def _create_membership(
    api_client: AsyncClient,
    organization_id: str,
    user_id: str,
    role: str = "ADMIN",
) -> dict:
    response = await api_client.post(
        f"/organizations/{organization_id}/memberships",
        json={"user_id": user_id, "role": role},
    )
    assert response.status_code == 201
    return response.json()


async def _create_request(
    api_client: AsyncClient,
    membership_id: str,
    access_token: str,
    title: str = "Need industrial filters",
) -> dict:
    response = await api_client.post(
        "/requests",
        json={
            "title": title,
            "description": "Initial request payload",
            "source": RequestSource.EMAIL.value,
        },
        headers=_membership_headers(access_token, membership_id),
    )
    assert response.status_code == 201
    return response.json()


async def _create_request_comment(
    api_client: AsyncClient,
    request_id: str,
    membership_id: str,
    access_token: str,
    body: str = "Initial internal comment",
) -> dict:
    response = await api_client.post(
        f"/requests/{request_id}/comments",
        json={"body": body},
        headers=_membership_headers(access_token, membership_id),
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.anyio
async def test_get_requests_returns_only_active_tenant_requests(api_client: AsyncClient) -> None:
    first_organization = await _create_organization(
        api_client,
        "Tenant Requests One",
        "tenant-requests-one",
    )
    second_organization = await _create_organization(
        api_client,
        "Tenant Requests Two",
        "tenant-requests-two",
    )
    first_user = await _create_user(api_client, "tenant-one@example.com", "Tenant One")
    second_user = await _create_user(api_client, "tenant-two@example.com", "Tenant Two")
    first_membership = await _create_membership(
        api_client,
        first_organization["id"],
        first_user["id"],
    )
    second_membership = await _create_membership(
        api_client,
        second_organization["id"],
        second_user["id"],
    )
    first_auth = await _login(api_client, "tenant-one@example.com")
    second_auth = await _login(api_client, "tenant-two@example.com")

    first_request = await _create_request(
        api_client,
        first_membership["id"],
        first_auth["access_token"],
        title="Tenant one request",
    )
    await _create_request(
        api_client,
        second_membership["id"],
        second_auth["access_token"],
        title="Tenant two request",
    )

    response = await api_client.get(
        "/requests",
        headers=_membership_headers(first_auth["access_token"], first_membership["id"]),
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == first_request["id"]
    assert payload[0]["organization_id"] == first_organization["id"]


@pytest.mark.anyio
async def test_get_requests_supports_title_search(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Search Requests", "search-requests")
    user = await _create_user(api_client, "search-requests@example.com", "Search Requests")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "search-requests@example.com")

    await _create_request(api_client, membership["id"], auth_payload["access_token"], title="Need industrial valves")
    matching_request = await _create_request(
        api_client,
        membership["id"],
        auth_payload["access_token"],
        title="Need stainless pumps",
    )

    response = await api_client.get(
        "/requests?q=stainless",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == matching_request["id"]


@pytest.mark.anyio
async def test_get_requests_supports_status_filter(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Status Filter Org", "status-filter-org")
    user = await _create_user(api_client, "status-filter@example.com", "Status Filter")
    membership = await _create_membership(api_client, organization["id"], user["id"], role="OWNER")
    auth_payload = await _login(api_client, "status-filter@example.com")

    target_request = await _create_request(
        api_client,
        membership["id"],
        auth_payload["access_token"],
        title="Status filter request",
    )
    transition_response = await api_client.post(
        f"/requests/{target_request['id']}/status-transitions",
        json={"new_status": RequestStatus.UNDER_REVIEW.value},
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )
    assert transition_response.status_code == 200

    response = await api_client.get(
        f"/requests?status={RequestStatus.UNDER_REVIEW.value}",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [target_request["id"]]


@pytest.mark.anyio
async def test_get_requests_supports_assigned_membership_filter(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Assignee Filter Org", "assignee-filter-org")
    owner = await _create_user(api_client, "assignee-owner@example.com", "Assignee Owner")
    assignee = await _create_user(api_client, "assignee-user@example.com", "Assignee User")
    owner_membership = await _create_membership(api_client, organization["id"], owner["id"], role="OWNER")
    assignee_membership = await _create_membership(api_client, organization["id"], assignee["id"], role="MEMBER")
    auth_payload = await _login(api_client, "assignee-owner@example.com")
    request_payload = await _create_request(api_client, owner_membership["id"], auth_payload["access_token"])

    assign_response = await api_client.patch(
        f"/requests/{request_payload['id']}/assign",
        json={"assigned_membership_id": assignee_membership["id"]},
        headers=_membership_headers(auth_payload["access_token"], owner_membership["id"]),
    )
    assert assign_response.status_code == 200

    response = await api_client.get(
        f"/requests?assigned_membership_id={assignee_membership['id']}",
        headers=_membership_headers(auth_payload["access_token"], owner_membership["id"]),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [request_payload["id"]]


@pytest.mark.anyio
async def test_get_requests_supports_source_filter(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Source Filter Org", "source-filter-org")
    user = await _create_user(api_client, "source-filter@example.com", "Source Filter")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "source-filter@example.com")

    await _create_request(api_client, membership["id"], auth_payload["access_token"], title="Email request")
    response_manual = await api_client.post(
        "/requests",
        json={
            "title": "Manual request",
            "description": "Created manually",
            "source": RequestSource.MANUAL.value,
        },
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )
    assert response_manual.status_code == 201

    response = await api_client.get(
        f"/requests?source={RequestSource.MANUAL.value}",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 200
    assert [item["source"] for item in response.json()] == [RequestSource.MANUAL.value]


@pytest.mark.anyio
async def test_post_requests_creates_request(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Acme Requests", "acme-requests")
    user = await _create_user(api_client, "requester@example.com", "Requester Example")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "requester@example.com")

    response = await api_client.post(
        "/requests",
        json={
            "title": "Need stainless steel pumps",
            "description": "For new production line",
            "source": RequestSource.EMAIL.value,
        },
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    payload = response.json()

    assert response.status_code == 201
    assert payload["organization_id"] == organization["id"]
    assert payload["created_by_membership_id"] == membership["id"]
    assert payload["title"] == "Need stainless steel pumps"
    assert payload["description"] == "For new production line"
    assert payload["source"] == RequestSource.EMAIL.value
    assert payload["status"] == RequestStatus.NEW.value


@pytest.mark.anyio
async def test_post_requests_allows_member_role(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Member Requests", "member-requests")
    user = await _create_user(api_client, "member-requester@example.com", "Member Requester")
    membership = await _create_membership(
        api_client,
        organization["id"],
        user["id"],
        role="MEMBER",
    )
    auth_payload = await _login(api_client, "member-requester@example.com")

    response = await api_client.post(
        "/requests",
        json={
            "title": "Need industrial valves",
            "description": "Requested by member",
            "source": RequestSource.WEB_FORM.value,
        },
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 201
    assert response.json()["created_by_membership_id"] == membership["id"]
    assert response.json()["status"] == RequestStatus.NEW.value


@pytest.mark.anyio
async def test_get_request_by_id_returns_existing_request(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Nova Requests", "nova-requests")
    user = await _create_user(api_client, "nova-requester@example.com", "Nova Requester")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "nova-requester@example.com")
    request_payload = await _create_request(
        api_client,
        membership["id"],
        auth_payload["access_token"],
        title="Need conveyor belt",
    )

    response = await api_client.get(
        f"/requests/{request_payload['id']}",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 200
    assert response.json()["id"] == request_payload["id"]
    assert response.json()["status"] == RequestStatus.NEW.value


@pytest.mark.anyio
async def test_post_request_comments_creates_comment_and_activity(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(api_client, "Comment Org", "comment-org")
    user = await _create_user(api_client, "commenter@example.com", "Commenter")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "commenter@example.com")
    request_payload = await _create_request(api_client, membership["id"], auth_payload["access_token"])

    response = await api_client.post(
        f"/requests/{request_payload['id']}/comments",
        json={"body": "Need to validate lead times with procurement."},
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["request_id"] == request_payload["id"]
    assert payload["membership_id"] == membership["id"]
    assert payload["body"] == "Need to validate lead times with procurement."

    comments_response = await api_client.get(
        f"/requests/{request_payload['id']}/comments",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )
    assert comments_response.status_code == 200
    assert comments_response.json()[0]["id"] == payload["id"]

    activities_response = await api_client.get(
        f"/requests/{request_payload['id']}/activities",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )
    assert activities_response.status_code == 200
    assert any(
        activity["type"] == "REQUEST_COMMENT_ADDED"
        and activity["payload"]["comment_id"] == payload["id"]
        for activity in activities_response.json()
    )


@pytest.mark.anyio
async def test_request_comments_are_tenant_scoped(api_client: AsyncClient) -> None:
    first_organization = await _create_organization(api_client, "Comment Tenant One", "comment-tenant-one")
    second_organization = await _create_organization(api_client, "Comment Tenant Two", "comment-tenant-two")
    first_user = await _create_user(api_client, "comment-tenant-one@example.com", "Comment Tenant One")
    second_user = await _create_user(api_client, "comment-tenant-two@example.com", "Comment Tenant Two")
    first_membership = await _create_membership(api_client, first_organization["id"], first_user["id"])
    second_membership = await _create_membership(api_client, second_organization["id"], second_user["id"])
    first_auth = await _login(api_client, "comment-tenant-one@example.com")
    second_auth = await _login(api_client, "comment-tenant-two@example.com")
    request_payload = await _create_request(api_client, first_membership["id"], first_auth["access_token"])

    response = await api_client.post(
        f"/requests/{request_payload['id']}/comments",
        json={"body": "Attempting cross-tenant comment"},
        headers=_membership_headers(second_auth["access_token"], second_membership["id"]),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_request_comments_require_authentication(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Comment Auth Org", "comment-auth-org")
    user = await _create_user(api_client, "comment-auth@example.com", "Comment Auth")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "comment-auth@example.com")
    request_payload = await _create_request(api_client, membership["id"], auth_payload["access_token"])

    response = await api_client.post(
        f"/requests/{request_payload['id']}/comments",
        json={"body": "Unauthenticated comment attempt"},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_patch_assign_request_updates_assigned_membership(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Assign Org", "assign-org")
    owner = await _create_user(api_client, "assign-owner@example.com", "Assign Owner")
    assignee = await _create_user(api_client, "assign-user@example.com", "Assign User")
    owner_membership = await _create_membership(
        api_client,
        organization["id"],
        owner["id"],
        role="OWNER",
    )
    assignee_membership = await _create_membership(
        api_client,
        organization["id"],
        assignee["id"],
        role="MEMBER",
    )
    auth_payload = await _login(api_client, "assign-owner@example.com")
    request_payload = await _create_request(api_client, owner_membership["id"], auth_payload["access_token"])

    response = await api_client.patch(
        f"/requests/{request_payload['id']}/assign",
        json={"assigned_membership_id": assignee_membership["id"]},
        headers=_membership_headers(auth_payload["access_token"], owner_membership["id"]),
    )

    assert response.status_code == 200
    assert response.json()["assigned_membership_id"] == assignee_membership["id"]

    activities_response = await api_client.get(
        f"/requests/{request_payload['id']}/activities",
        headers=_membership_headers(auth_payload["access_token"], owner_membership["id"]),
    )
    assert activities_response.status_code == 200
    assert any(
        activity["type"] == "REQUEST_ASSIGNED"
        and activity["payload"]["assigned_membership_id"] == assignee_membership["id"]
        for activity in activities_response.json()
    )


@pytest.mark.anyio
async def test_patch_assign_request_is_tenant_scoped(api_client: AsyncClient) -> None:
    first_organization = await _create_organization(api_client, "Assign Tenant One", "assign-tenant-one")
    second_organization = await _create_organization(api_client, "Assign Tenant Two", "assign-tenant-two")
    first_user = await _create_user(api_client, "assign-tenant-one@example.com", "Assign Tenant One")
    second_user = await _create_user(api_client, "assign-tenant-two@example.com", "Assign Tenant Two")
    first_membership = await _create_membership(api_client, first_organization["id"], first_user["id"], role="OWNER")
    second_membership = await _create_membership(api_client, second_organization["id"], second_user["id"], role="OWNER")
    first_auth = await _login(api_client, "assign-tenant-one@example.com")
    second_auth = await _login(api_client, "assign-tenant-two@example.com")
    request_payload = await _create_request(api_client, first_membership["id"], first_auth["access_token"])

    response = await api_client.patch(
        f"/requests/{request_payload['id']}/assign",
        json={"assigned_membership_id": second_membership["id"]},
        headers=_membership_headers(first_auth["access_token"], first_membership["id"]),
    )

    assert response.status_code == 409

    forbidden_response = await api_client.patch(
        f"/requests/{request_payload['id']}/assign",
        json={"assigned_membership_id": first_membership["id"]},
        headers=_membership_headers(second_auth["access_token"], second_membership["id"]),
    )

    assert forbidden_response.status_code == 404


@pytest.mark.anyio
async def test_patch_assign_request_requires_authentication(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Assign Auth Org", "assign-auth-org")
    user = await _create_user(api_client, "assign-auth@example.com", "Assign Auth")
    membership = await _create_membership(api_client, organization["id"], user["id"], role="OWNER")
    auth_payload = await _login(api_client, "assign-auth@example.com")
    request_payload = await _create_request(api_client, membership["id"], auth_payload["access_token"])

    response = await api_client.patch(
        f"/requests/{request_payload['id']}/assign",
        json={"assigned_membership_id": membership["id"]},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_post_requests_returns_401_without_authentication(
    api_client: AsyncClient,
) -> None:
    response = await api_client.post(
        "/requests",
        json={
            "title": "Missing auth request",
            "description": None,
            "source": RequestSource.API.value,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token."


@pytest.mark.anyio
async def test_post_requests_returns_403_for_membership_from_other_user(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(api_client, "Alpha Requests", "alpha-requests")
    owner_user = await _create_user(api_client, "owner@example.com", "Owner User")
    intruder_user = await _create_user(api_client, "intruder@example.com", "Intruder User")
    foreign_membership = await _create_membership(
        api_client,
        organization["id"],
        owner_user["id"],
    )
    intruder_auth = await _login(api_client, "intruder@example.com")

    response = await api_client.post(
        "/requests",
        json={
            "title": "Foreign membership request",
            "description": None,
            "source": RequestSource.EMAIL.value,
        },
        headers=_membership_headers(intruder_auth["access_token"], foreign_membership["id"]),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Membership context is invalid."


@pytest.mark.anyio
async def test_get_request_by_id_returns_not_found(api_client: AsyncClient) -> None:
    organization = await _create_organization(api_client, "Missing Requests", "missing-requests")
    user = await _create_user(api_client, "missing-requests@example.com", "Missing Requests")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "missing-requests@example.com")

    response = await api_client.get(
        f"/requests/{uuid4()}",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_request_by_id_returns_not_found_for_foreign_tenant(
    api_client: AsyncClient,
) -> None:
    owner_organization = await _create_organization(
        api_client,
        "Owner Requests",
        "owner-requests",
    )
    foreign_organization = await _create_organization(
        api_client,
        "Foreign Requests",
        "foreign-requests",
    )
    owner_user = await _create_user(api_client, "owner-requests@example.com", "Owner Requests")
    foreign_user = await _create_user(
        api_client,
        "foreign-requests@example.com",
        "Foreign Requests",
    )
    owner_membership = await _create_membership(
        api_client,
        owner_organization["id"],
        owner_user["id"],
    )
    foreign_membership = await _create_membership(
        api_client,
        foreign_organization["id"],
        foreign_user["id"],
    )
    owner_auth = await _login(api_client, "owner-requests@example.com")
    foreign_auth = await _login(api_client, "foreign-requests@example.com")
    request_payload = await _create_request(
        api_client,
        owner_membership["id"],
        owner_auth["access_token"],
    )

    response = await api_client.get(
        f"/requests/{request_payload['id']}",
        headers=_membership_headers(foreign_auth["access_token"], foreign_membership["id"]),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_post_request_status_transitions_updates_request_status(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(api_client, "Transition Org", "transition-org")
    user = await _create_user(api_client, "transition@example.com", "Transition User")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "transition@example.com")
    request_payload = await _create_request(
        api_client=api_client,
        membership_id=membership["id"],
        access_token=auth_payload["access_token"],
        title="Need stainless steel pumps",
    )

    response = await api_client.post(
        f"/requests/{request_payload['id']}/status-transitions",
        json={"new_status": RequestStatus.UNDER_REVIEW.value},
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 200
    assert response.json()["id"] == request_payload["id"]
    assert response.json()["status"] == RequestStatus.UNDER_REVIEW.value


@pytest.mark.anyio
async def test_post_request_status_transitions_returns_conflict_for_invalid_transition(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(
        api_client, "Invalid Transition Org", "invalid-transition-org"
    )
    user = await _create_user(api_client, "invalid-transition@example.com", "Invalid Transition")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "invalid-transition@example.com")
    request_payload = await _create_request(
        api_client=api_client,
        membership_id=membership["id"],
        access_token=auth_payload["access_token"],
    )

    response = await api_client.post(
        f"/requests/{request_payload['id']}/status-transitions",
        json={"new_status": RequestStatus.WON.value},
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot transition request from 'NEW' to 'WON'."


@pytest.mark.anyio
async def test_post_request_status_transitions_returns_403_for_member_role(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(api_client, "Member Transition", "member-transition")
    user = await _create_user(api_client, "member-transition@example.com", "Member Transition")
    membership = await _create_membership(
        api_client,
        organization["id"],
        user["id"],
        role="MEMBER",
    )
    auth_payload = await _login(api_client, "member-transition@example.com")
    request_payload = await _create_request(
        api_client=api_client,
        membership_id=membership["id"],
        access_token=auth_payload["access_token"],
    )

    response = await api_client.post(
        f"/requests/{request_payload['id']}/status-transitions",
        json={"new_status": RequestStatus.UNDER_REVIEW.value},
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Membership role 'MEMBER' is not allowed to perform 'TRANSITION_REQUEST_STATUS'."
    )


@pytest.mark.anyio
async def test_post_request_status_transitions_returns_not_found_for_missing_request(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(
        api_client, "Missing Request Transition", "missing-request-transition"
    )
    user = await _create_user(api_client, "missing-request@example.com", "Missing Request")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "missing-request@example.com")

    response = await api_client.post(
        f"/requests/{uuid4()}/status-transitions",
        json={"new_status": RequestStatus.UNDER_REVIEW.value},
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_post_request_status_transitions_returns_403_for_invalid_membership_context(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(
        api_client, "Missing Membership Transition", "missing-membership-transition"
    )
    user = await _create_user(
        api_client, "missing-membership@example.com", "Missing Membership"
    )
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "missing-membership@example.com")
    request_payload = await _create_request(
        api_client=api_client,
        membership_id=membership["id"],
        access_token=auth_payload["access_token"],
    )

    response = await api_client.post(
        f"/requests/{request_payload['id']}/status-transitions",
        json={"new_status": RequestStatus.UNDER_REVIEW.value},
        headers=_membership_headers(auth_payload["access_token"], str(uuid4())),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Membership context is invalid."


@pytest.mark.anyio
async def test_post_request_status_transitions_returns_conflict_for_membership_from_other_organization(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(
        api_client, "Alpha Transition Org", "alpha-transition-org"
    )
    other_organization = await _create_organization(
        api_client, "Beta Transition Org", "beta-transition-org"
    )
    user = await _create_user(api_client, "cross-transition@example.com", "Cross Transition")
    request_membership = await _create_membership(api_client, organization["id"], user["id"])
    other_membership = await _create_membership(api_client, other_organization["id"], user["id"])
    auth_payload = await _login(api_client, "cross-transition@example.com")
    request_payload = await _create_request(
        api_client=api_client,
        membership_id=request_membership["id"],
        access_token=auth_payload["access_token"],
    )

    response = await api_client.post(
        f"/requests/{request_payload['id']}/status-transitions",
        json={"new_status": RequestStatus.UNDER_REVIEW.value},
        headers=_membership_headers(auth_payload["access_token"], other_membership["id"]),
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "The provided request does not belong to the provided organization."
    )


@pytest.mark.anyio
async def test_post_request_status_transitions_creates_status_changed_activity(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(
        api_client, "Timeline Transition Org", "timeline-transition-org"
    )
    user = await _create_user(api_client, "timeline-transition@example.com", "Timeline Transition")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth_payload = await _login(api_client, "timeline-transition@example.com")
    request_payload = await _create_request(
        api_client=api_client,
        membership_id=membership["id"],
        access_token=auth_payload["access_token"],
        title="Need stateful request",
    )

    transition_response = await api_client.post(
        f"/requests/{request_payload['id']}/status-transitions",
        json={"new_status": RequestStatus.UNDER_REVIEW.value},
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )
    activities_response = await api_client.get(
        f"/requests/{request_payload['id']}/activities",
        headers=_membership_headers(auth_payload["access_token"], membership["id"]),
    )

    assert transition_response.status_code == 200
    assert activities_response.status_code == 200
    activities = activities_response.json()
    assert len(activities) == 2
    assert activities[1]["type"] == "STATUS_CHANGED"
    assert activities[1]["membership_id"] == membership["id"]
    assert activities[1]["payload"]["old_status"] == RequestStatus.NEW.value
    assert activities[1]["payload"]["new_status"] == RequestStatus.UNDER_REVIEW.value
