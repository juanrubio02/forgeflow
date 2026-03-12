import pytest
from httpx import AsyncClient


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


async def _login(api_client: AsyncClient, email: str, password: str = "StrongPass123!") -> dict:
    response = await api_client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def _membership_headers(access_token: str, membership_id: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "X-Membership-Id": membership_id,
    }


@pytest.mark.anyio
async def test_get_demo_intake_scenarios_returns_available_items(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(api_client, "Demo Org", "demo-org")
    user = await _create_user(api_client, "demo-scenarios@example.com", "Demo Scenarios")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth = await _login(api_client, "demo-scenarios@example.com")

    response = await api_client.get(
        "/demo/intake/scenarios",
        headers=_membership_headers(auth["access_token"], membership["id"]),
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 5
    assert any(item["key"] == "rfq_brackets_email" for item in payload)


@pytest.mark.anyio
async def test_run_demo_intake_scenario_creates_request_and_documents(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(api_client, "Demo Run Org", "demo-run-org")
    user = await _create_user(api_client, "demo-run@example.com", "Demo Run")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth = await _login(api_client, "demo-run@example.com")

    response = await api_client.post(
        "/demo/intake/scenarios/rfq_brackets_email/run",
        headers=_membership_headers(auth["access_token"], membership["id"]),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["scenario_key"] == "rfq_brackets_email"
    assert len(payload["document_ids"]) == 1

    request_response = await api_client.get(
        f"/requests/{payload['request_id']}",
        headers=_membership_headers(auth["access_token"], membership["id"]),
    )
    assert request_response.status_code == 200
    assert request_response.json()["source"] == "EMAIL"

    documents_response = await api_client.get(
        f"/requests/{payload['request_id']}/documents",
        headers=_membership_headers(auth["access_token"], membership["id"]),
    )
    assert documents_response.status_code == 200
    assert len(documents_response.json()) == 1


@pytest.mark.anyio
async def test_run_demo_intake_scenario_respects_tenant_isolation(
    api_client: AsyncClient,
) -> None:
    first_organization = await _create_organization(api_client, "Demo Tenant One", "demo-tenant-one")
    second_organization = await _create_organization(api_client, "Demo Tenant Two", "demo-tenant-two")
    first_user = await _create_user(api_client, "demo-tenant-one@example.com", "Demo Tenant One")
    second_user = await _create_user(api_client, "demo-tenant-two@example.com", "Demo Tenant Two")
    first_membership = await _create_membership(api_client, first_organization["id"], first_user["id"])
    second_membership = await _create_membership(api_client, second_organization["id"], second_user["id"])
    first_auth = await _login(api_client, "demo-tenant-one@example.com")
    second_auth = await _login(api_client, "demo-tenant-two@example.com")

    response = await api_client.post(
        "/demo/intake/scenarios/purchase_order_simple/run",
        headers=_membership_headers(first_auth["access_token"], first_membership["id"]),
    )
    assert response.status_code == 201
    payload = response.json()

    forbidden_read = await api_client.get(
        f"/requests/{payload['request_id']}",
        headers=_membership_headers(second_auth["access_token"], second_membership["id"]),
    )
    assert forbidden_read.status_code == 404


@pytest.mark.anyio
async def test_run_demo_intake_scenario_requires_authentication(
    api_client: AsyncClient,
) -> None:
    response = await api_client.post("/demo/intake/scenarios/rfq_brackets_email/run")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_run_demo_intake_scenario_returns_404_for_missing_scenario(
    api_client: AsyncClient,
) -> None:
    organization = await _create_organization(api_client, "Demo Missing Org", "demo-missing-org")
    user = await _create_user(api_client, "demo-missing@example.com", "Demo Missing")
    membership = await _create_membership(api_client, organization["id"], user["id"])
    auth = await _login(api_client, "demo-missing@example.com")

    response = await api_client.post(
        "/demo/intake/scenarios/missing-scenario/run",
        headers=_membership_headers(auth["access_token"], membership["id"]),
    )

    assert response.status_code == 404
