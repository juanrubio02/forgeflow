import { apiRequest } from "@/lib/api/client";
import type {
  AssignRequestPayload,
  CreateRequestCommentPayload,
  CreateRequestPayload,
  RequestActivity,
  RequestComment,
  RequestRecord,
  TransitionRequestStatusPayload,
} from "@/lib/api/types";

export function listRequests(): Promise<RequestRecord[] | null> {
  return apiRequest<RequestRecord[]>("/requests", {
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
