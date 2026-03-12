"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useCreateRequestCommentMutation } from "@/features/requests/api";
import { useMembership } from "@/hooks/use-membership";
import { useToast } from "@/hooks/use-toast";
import { interpolate, useI18n } from "@/i18n/hooks";
import { getOrganizationMembershipOptions } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import type { RequestComment } from "@/lib/api/types";
import { formatDateTime } from "@/lib/utils";

export function RequestCommentsPanel({
  requestId,
  comments,
  isLoading,
  isError,
}: {
  requestId: string;
  comments: RequestComment[];
  isLoading: boolean;
  isError: boolean;
}) {
  const { locale, messages } = useI18n();
  const { pushToast } = useToast();
  const { activeMembership } = useMembership();
  const [body, setBody] = useState("");
  const createCommentMutation = useCreateRequestCommentMutation(requestId);
  const membershipsQuery = useQuery({
    queryKey: ["request-comments-memberships", activeMembership?.organization_id ?? null],
    queryFn: async () =>
      activeMembership?.organization_id
        ? (await getOrganizationMembershipOptions(activeMembership.organization_id)) ?? []
        : [],
    enabled: Boolean(activeMembership?.organization_id),
  });

  const authorByMembershipId = new Map(
    (membershipsQuery.data ?? []).map((membership) => [membership.id, membership.user_full_name]),
  );

  return (
    <Card className="h-full">
      <CardHeader>
        <p className="eyebrow">{messages.requests.comments.eyebrow}</p>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <CardTitle>{messages.requests.comments.title}</CardTitle>
          <span className="inline-flex rounded-full border border-line bg-surface px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-slate-600">
            {interpolate(messages.requests.comments.count, { count: comments.length })}
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="space-y-3 rounded-[var(--radius-control)] border border-line/70 bg-surface/70 px-4 py-4">
          <label className="text-sm font-medium" htmlFor="request-comment-body">
            {messages.requests.comments.inputLabel}
          </label>
          <Textarea
            id="request-comment-body"
            value={body}
            onChange={(event) => setBody(event.target.value)}
            placeholder={messages.requests.comments.placeholder}
          />
          <div className="flex justify-end">
            <Button
              type="button"
              disabled={createCommentMutation.isPending || !body.trim()}
              onClick={async () => {
                try {
                  await createCommentMutation.mutateAsync({ body: body.trim() });
                  setBody("");
                  pushToast({
                    tone: "success",
                    title: messages.requests.comments.successTitle,
                    description: messages.requests.comments.successDescription,
                  });
                } catch (error) {
                  pushToast({
                    tone: "error",
                    title: messages.requests.comments.errorTitle,
                    description:
                      error instanceof ApiError
                        ? error.detail
                        : messages.requests.comments.fallbackError,
                  });
                }
              }}
            >
              {createCommentMutation.isPending
                ? messages.requests.comments.posting
                : messages.requests.comments.post}
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="rounded-2xl border border-dashed border-line px-6 py-8 text-sm text-slate-600">
            {messages.requests.comments.loading}
          </div>
        ) : isError ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4 text-sm text-amber-800">
            {messages.requests.comments.loadError}
          </div>
        ) : !comments.length ? (
          <div className="rounded-2xl border border-dashed border-line px-6 py-8 text-sm text-slate-600">
            {messages.requests.comments.empty}
          </div>
        ) : (
          <div className="space-y-3">
            {comments.map((comment) => (
              <div
                key={comment.id}
                className="rounded-[var(--radius-control)] border border-line/70 bg-surface/80 px-4 py-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold tracking-[-0.01em] text-slate-900">
                    {messages.requests.comments.author} ·{" "}
                    <span>{authorByMembershipId.get(comment.membership_id) ?? messages.requests.comments.unknownAuthor}</span>
                  </p>
                  <p className="text-sm text-slate-500">
                    {formatDateTime(comment.created_at, locale)}
                  </p>
                </div>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {comment.body}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
