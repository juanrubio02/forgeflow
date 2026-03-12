"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  assignRequest,
  createRequestComment,
  createRequest,
  getRequestById,
  listRequestActivities,
  listRequestComments,
  listRequests,
  transitionRequestStatus,
} from "@/lib/api/requests";
import type {
  AssignRequestPayload,
  CreateRequestCommentPayload,
  CreateRequestPayload,
  RequestListFilters,
  TransitionRequestStatusPayload,
} from "@/lib/api/types";

export const requestsKeys = {
  all: ["requests"] as const,
  detail: (requestId: string) => ["requests", requestId] as const,
  activities: (requestId: string) => ["requests", requestId, "activities"] as const,
  comments: (requestId: string) => ["request-comments", requestId] as const,
};

export function useRequestsQuery(filters: RequestListFilters = {}) {
  return useQuery({
    queryKey: [...requestsKeys.all, "list", filters],
    queryFn: async () => (await listRequests(filters)) ?? [],
  });
}

export function useRequestQuery(requestId: string) {
  return useQuery({
    queryKey: requestsKeys.detail(requestId),
    queryFn: async () => getRequestById(requestId),
    enabled: Boolean(requestId),
  });
}

export function useRequestActivitiesQuery(requestId: string) {
  return useQuery({
    queryKey: requestsKeys.activities(requestId),
    queryFn: async () => (await listRequestActivities(requestId)) ?? [],
    enabled: Boolean(requestId),
  });
}

export function useRequestCommentsQuery(requestId: string) {
  return useQuery({
    queryKey: requestsKeys.comments(requestId),
    queryFn: async () => (await listRequestComments(requestId)) ?? [],
    enabled: Boolean(requestId),
  });
}

export function useCreateRequestMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateRequestPayload) => createRequest(payload),
    onSuccess: async (request) => {
      await queryClient.invalidateQueries({ queryKey: requestsKeys.all });
      if (request?.id) {
        queryClient.setQueryData(requestsKeys.detail(request.id), request);
      }
    },
  });
}

export function useTransitionRequestStatusMutation(requestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TransitionRequestStatusPayload) =>
      transitionRequestStatus(requestId, payload),
    onSuccess: async (request) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: requestsKeys.all }),
        queryClient.invalidateQueries({ queryKey: requestsKeys.activities(requestId) }),
      ]);

      if (request) {
        queryClient.setQueryData(requestsKeys.detail(requestId), request);
      }
    },
  });
}

export function useCreateRequestCommentMutation(requestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateRequestCommentPayload) =>
      createRequestComment(requestId, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: requestsKeys.comments(requestId) }),
        queryClient.invalidateQueries({ queryKey: requestsKeys.activities(requestId) }),
      ]);
    },
  });
}

export function useAssignRequestMutation(requestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AssignRequestPayload) => assignRequest(requestId, payload),
    onSuccess: async (request) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: requestsKeys.detail(requestId) }),
        queryClient.invalidateQueries({ queryKey: requestsKeys.activities(requestId) }),
      ]);
      if (request) {
        queryClient.setQueryData(requestsKeys.detail(requestId), request);
      }
    },
  });
}
