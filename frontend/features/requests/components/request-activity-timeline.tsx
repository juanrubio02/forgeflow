import { useQuery } from "@tanstack/react-query";
import { FileUp, ListChecks, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useMembership } from "@/hooks/use-membership";
import { interpolate, useI18n } from "@/i18n/hooks";
import { getOrganizationMembershipOptions } from "@/lib/api/auth";
import type { RequestActivity } from "@/lib/api/types";
import { formatDateTime, formatRelativeFileSize } from "@/lib/utils";

function activityIcon(type: RequestActivity["type"]) {
  if (type === "DOCUMENT_UPLOADED") {
    return FileUp;
  }

  if (type === "REQUEST_COMMENT_ADDED" || type === "COMMENT_ADDED") {
    return Sparkles;
  }

  if (type === "STATUS_CHANGED") {
    return ListChecks;
  }

  return Sparkles;
}

function activityVariant(type: RequestActivity["type"]) {
  if (type === "DOCUMENT_UPLOADED") {
    return "info" as const;
  }

  if (type === "REQUEST_COMMENT_ADDED" || type === "COMMENT_ADDED") {
    return "neutral" as const;
  }

  if (type === "STATUS_CHANGED") {
    return "warning" as const;
  }

  return "neutral" as const;
}

export function RequestActivityTimeline({
  activities,
}: {
  activities: RequestActivity[];
}) {
  const { locale, messages } = useI18n();
  const { activeMembership } = useMembership();
  const membershipsQuery = useQuery({
    queryKey: ["request-activities-memberships", activeMembership?.organization_id ?? null],
    queryFn: async () =>
      activeMembership?.organization_id
        ? (await getOrganizationMembershipOptions(activeMembership.organization_id)) ?? []
        : [],
    enabled: Boolean(activeMembership?.organization_id),
  });
  const membershipNameById = new Map(
    (membershipsQuery.data ?? []).map((membership) => [membership.id, membership.user_full_name]),
  );

  const formatActivityDescription = (activity: RequestActivity) => {
    const payload = activity.payload as Record<string, unknown>;

    if (activity.type === "REQUEST_CREATED") {
      const source =
        typeof payload.source === "string"
          ? (messages.requests.sources[
              payload.source as keyof typeof messages.requests.sources
            ] ?? messages.common.labels.notAvailable)
          : messages.common.labels.notAvailable;
      const status =
        typeof payload.status === "string"
          ? (messages.requests.statuses[
              payload.status as keyof typeof messages.requests.statuses
            ] ?? messages.common.labels.notAvailable)
          : messages.common.labels.notAvailable;
      const title =
        typeof payload.title === "string" && payload.title.trim()
          ? payload.title
          : messages.requests.timeline.activityRecorded;
      return `${title} · ${source} · ${status}`;
    }

    if (activity.type === "STATUS_CHANGED") {
      const oldStatus =
        typeof payload.old_status === "string"
          ? (messages.requests.statuses[
              payload.old_status as keyof typeof messages.requests.statuses
            ] ?? messages.common.labels.notAvailable)
          : messages.common.labels.notAvailable;
      const newStatus =
        typeof payload.new_status === "string"
          ? (messages.requests.statuses[
              payload.new_status as keyof typeof messages.requests.statuses
            ] ?? messages.common.labels.notAvailable)
          : messages.common.labels.notAvailable;
      return `${oldStatus} -> ${newStatus}`;
    }

    if (activity.type === "REQUEST_ASSIGNED") {
      const assigneeId =
        typeof payload.assigned_membership_id === "string" ? payload.assigned_membership_id : "";
      return membershipNameById.get(assigneeId) ?? messages.requests.comments.unknownAuthor;
    }

    if (activity.type === "REQUEST_COMMENT_ADDED" || activity.type === "COMMENT_ADDED") {
      return membershipNameById.get(activity.membership_id) ?? messages.requests.comments.unknownAuthor;
    }

    if (activity.type === "DOCUMENT_UPLOADED") {
      const filename =
        typeof payload.original_filename === "string"
          ? payload.original_filename
          : messages.common.labels.notAvailable;
      const size =
        typeof payload.size_bytes === "number"
          ? formatRelativeFileSize(payload.size_bytes, locale)
          : messages.common.labels.notAvailable;
      return `${filename} · ${size}`;
    }

    if (activity.type === "DOCUMENT_VERIFIED_DATA_UPDATED") {
      const verifiedStructuredData =
        payload.verified_structured_data &&
        typeof payload.verified_structured_data === "object" &&
        !Array.isArray(payload.verified_structured_data)
          ? (payload.verified_structured_data as Record<string, unknown>)
          : {};
      const fieldLabels = Object.keys(verifiedStructuredData).map((field) =>
        messages.documents.verifiedData.fields[
          field as keyof typeof messages.documents.verifiedData.fields
        ] ?? field,
      );

      return fieldLabels.length
        ? fieldLabels.join(", ")
        : messages.requests.timeline.activityRecorded;
    }

    return messages.requests.timeline.activityRecorded;
  };

  const formatActor = (activity: RequestActivity) =>
    membershipNameById.get(activity.membership_id) ?? messages.requests.comments.unknownAuthor;

  return (
    <Card className="h-full">
      <CardHeader>
        <p className="eyebrow">
          {messages.requests.timeline.eyebrow}
        </p>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <CardTitle>{messages.requests.timeline.title}</CardTitle>
          <Badge variant="neutral" size="sm">
            {interpolate(messages.requests.timeline.events, { count: activities.length })}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        {!activities.length ? (
          <div className="rounded-2xl border border-dashed border-line px-6 py-8 text-sm text-slate-600">
            {messages.requests.timeline.empty}
          </div>
        ) : null}
        {activities.map((activity, index) => {
          const Icon = activityIcon(activity.type);
          return (
            <div key={activity.id} className="relative flex gap-4 pl-1">
              {index < activities.length - 1 ? (
                <div className="absolute left-5 top-11 h-[calc(100%-1.5rem)] w-px bg-line" />
              ) : null}
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[var(--radius-control)] bg-surface shadow-soft">
                <Icon className="h-4 w-4 text-slate-600" />
              </div>
              <div className="min-w-0 flex-1 space-y-2 pb-1">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={activityVariant(activity.type)} size="sm" dot>
                    {messages.requests.activitiesMap[activity.type]}
                  </Badge>
                  <p className="text-sm text-slate-500">
                    {formatDateTime(activity.created_at, locale)}
                  </p>
                </div>
                <p className="text-sm font-medium text-slate-800">
                  {formatActivityDescription(activity)}
                </p>
                <p className="text-sm text-slate-500">
                  {messages.requests.timeline.actor} · {formatActor(activity)}
                </p>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
