"use client";

import { Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useI18n } from "@/i18n/hooks";
import type {
  OrganizationMembershipOption,
  RequestSource,
  RequestStatus,
} from "@/lib/api/types";

export interface RequestListFilterState {
  q: string;
  status: RequestStatus | "";
  assigned_membership_id: string;
  source: RequestSource | "";
}

export function RequestFiltersBar({
  filters,
  memberships,
  onChange,
  onReset,
}: {
  filters: RequestListFilterState;
  memberships: OrganizationMembershipOption[];
  onChange: (next: RequestListFilterState) => void;
  onReset: () => void;
}) {
  const { messages } = useI18n();

  return (
    <Card>
      <CardContent className="flex flex-col gap-4 px-6 py-5 xl:flex-row xl:items-end">
        <div className="relative min-w-0 flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            value={filters.q}
            onChange={(event) => onChange({ ...filters, q: event.target.value })}
            placeholder={messages.requests.filters.searchPlaceholder}
            className="pl-10"
            aria-label={messages.requests.filters.searchLabel}
          />
        </div>
        <div className="grid gap-4 md:grid-cols-3 xl:min-w-[42rem] xl:flex-1">
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="requests-filter-status">
              {messages.requests.filters.statusLabel}
            </label>
            <Select
              id="requests-filter-status"
              value={filters.status}
              onChange={(event) =>
                onChange({ ...filters, status: event.target.value as RequestStatus | "" })
              }
            >
              <option value="">{messages.requests.filters.allStatuses}</option>
              {Object.entries(messages.requests.statuses).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="requests-filter-assignee">
              {messages.requests.filters.assigneeLabel}
            </label>
            <Select
              id="requests-filter-assignee"
              value={filters.assigned_membership_id}
              onChange={(event) =>
                onChange({ ...filters, assigned_membership_id: event.target.value })
              }
            >
              <option value="">{messages.requests.filters.allAssignees}</option>
              {memberships.map((membership) => (
                <option key={membership.id} value={membership.id}>
                  {membership.user_full_name} · {messages.common.memberships[membership.role]}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="requests-filter-source">
              {messages.requests.filters.sourceLabel}
            </label>
            <Select
              id="requests-filter-source"
              value={filters.source}
              onChange={(event) =>
                onChange({ ...filters, source: event.target.value as RequestSource | "" })
              }
            >
              <option value="">{messages.requests.filters.allSources}</option>
              {Object.entries(messages.requests.sources).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </Select>
          </div>
        </div>
        <Button type="button" variant="secondary" onClick={onReset}>
          {messages.requests.filters.reset}
        </Button>
      </CardContent>
    </Card>
  );
}
