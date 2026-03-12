import { apiRequest } from "@/lib/api/client";
import type {
  AssignRequestPayload,
  CreateRequestCommentPayload,
  CreateRequestPayload,
  RequestListFilters,
  RequestActivity,
  RequestComment,
  RequestRecord,
  TransitionRequestStatusPayload,
} from "@/lib/api/types";

export function listRequests(filters: RequestListFilters = {}): Promise<RequestRecord[] | null> {
  const searchParams = new URLSearchParams();
  if (filters.q) {
    searchParams.set("q", filters.q);
  }
  if (filters.status) {
    searchParams.set("status", filters.status);
  }
  if (filters.assigned_membership_id) {
    searchParams.set("assigned_membership_id", filters.assigned_membership_id);
  }
  if (filters.source) {
    searchParams.set("source", filters.source);
  }

  const path = searchParams.toString()
    ? `/requests?${searchParams.toString()}`
    : "/requests";

  return apiRequest<RequestRecord[]>(path, {
    includeAuth: true,
    includeMembership: true,
  });
}

export function getRequestById(requestId: string): Promise<RequestRecord | null> {
  return apiRequest<RequestRecord>(`/requests/${requestId}`, {
    includeAuth: true,
    includeMembership: true,
    suppressNotFound: true,
  });
}

export function createRequest(payload: CreateRequestPayload): Promise<RequestRecord | null> {
  return apiRequest<RequestRecord>("/requests", {
    method: "POST",
    includeAuth: true,
    includeMembership: true,
    body: JSON.stringify(payload),
  });
}

export function listRequestActivities(
  requestId: string,
): Promise<RequestActivity[] | null> {
  return apiRequest<RequestActivity[]>(`/requests/${requestId}/activities`, {
    includeAuth: true,
    includeMembership: true,
    suppressNotFound: true,
  });
}

export function listRequestComments(
  requestId: string,
): Promise<RequestComment[] | null> {
  return apiRequest<RequestComment[]>(`/requests/${requestId}/comments`, {
    includeAuth: true,
    includeMembership: true,
    suppressNotFound: true,
  });
}

export function createRequestComment(
  requestId: string,
  payload: CreateRequestCommentPayload,
): Promise<RequestComment | null> {
  return apiRequest<RequestComment>(`/requests/${requestId}/comments`, {
    method: "POST",
    includeAuth: true,
    includeMembership: true,
    body: JSON.stringify(payload),
  });
}

export function transitionRequestStatus(
  requestId: string,
  payload: TransitionRequestStatusPayload,
): Promise<RequestRecord | null> {
  return apiRequest<RequestRecord>(`/requests/${requestId}/status-transitions`, {
    method: "POST",
    includeAuth: true,
    includeMembership: true,
    body: JSON.stringify(payload),
  });
}

export function assignRequest(
  requestId: string,
  payload: AssignRequestPayload,
): Promise<RequestRecord | null> {
  return apiRequest<RequestRecord>(`/requests/${requestId}/assign`, {
    method: "PATCH",
    includeAuth: true,
    includeMembership: true,
    body: JSON.stringify(payload),
  });
}
