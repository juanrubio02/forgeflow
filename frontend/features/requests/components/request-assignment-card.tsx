"use client";

import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { useAssignRequestMutation } from "@/features/requests/api";
import { getOrganizationMembershipOptions } from "@/lib/api/auth";
import type { RequestRecord } from "@/lib/api/types";
import { useToast } from "@/hooks/use-toast";
import { useI18n } from "@/i18n/hooks";
import { ApiError } from "@/lib/api/client";
import { useEffect, useMemo, useState } from "react";

export function RequestAssignmentCard({ request }: { request: RequestRecord }) {
  const { messages } = useI18n();
  const { pushToast } = useToast();
  const [selectedMembershipId, setSelectedMembershipId] = useState(
    request.assigned_membership_id ?? "",
  );
  const assignmentMutation = useAssignRequestMutation(request.id);
  const membershipsQuery = useQuery({
    queryKey: ["organization-memberships", request.organization_id],
    queryFn: async () =>
      (await getOrganizationMembershipOptions(request.organization_id)) ?? [],
    enabled: Boolean(request.organization_id),
  });

  useEffect(() => {
    setSelectedMembershipId(request.assigned_membership_id ?? "");
  }, [request.assigned_membership_id]);

  const assignedMember = useMemo(
    () =>
      membershipsQuery.data?.find(
        (membership) => membership.id === request.assigned_membership_id,
      ) ?? null,
    [membershipsQuery.data, request.assigned_membership_id],
  );

  return (
    <Card>
      <CardHeader>
        <p className="eyebrow">{messages.requests.assignment.eyebrow}</p>
        <CardTitle className="mt-2">{messages.requests.assignment.title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="surface-muted rounded-[var(--radius-control)] p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            {messages.requests.assignment.current}
          </p>
          <p className="mt-2 text-sm font-semibold tracking-[-0.01em] text-slate-900">
            {assignedMember
              ? `${assignedMember.user_full_name} · ${assignedMember.role}`
              : messages.requests.assignment.unassigned}
          </p>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="request-assignment-membership">
            {messages.requests.assignment.selectLabel}
          </label>
          <Select
            id="request-assignment-membership"
            value={selectedMembershipId}
            onChange={(event) => setSelectedMembershipId(event.target.value)}
            disabled={membershipsQuery.isLoading || membershipsQuery.isError}
          >
            <option value="">{messages.requests.assignment.selectPlaceholder}</option>
            {(membershipsQuery.data ?? []).map((membership) => (
              <option key={membership.id} value={membership.id}>
                {membership.user_full_name} · {membership.role}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex justify-end">
          <Button
            type="button"
            disabled={
              assignmentMutation.isPending ||
              !selectedMembershipId ||
              selectedMembershipId === request.assigned_membership_id
            }
            onClick={async () => {
              try {
                await assignmentMutation.mutateAsync({
                  assigned_membership_id: selectedMembershipId,
                });
                pushToast({
                  tone: "success",
                  title: messages.requests.assignment.successTitle,
                  description: messages.requests.assignment.successDescription,
                });
              } catch (error) {
                pushToast({
                  tone: "error",
                  title: messages.requests.assignment.errorTitle,
                  description:
                    error instanceof ApiError
                      ? error.detail
                      : messages.requests.assignment.fallbackError,
                });
              }
            }}
          >
            {assignmentMutation.isPending
              ? messages.requests.assignment.assigning
              : messages.requests.assignment.assign}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

