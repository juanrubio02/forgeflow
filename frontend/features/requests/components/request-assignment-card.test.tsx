import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { RequestAssignmentCard } from "@/features/requests/components/request-assignment-card";

const mutateAsync = vi.fn();

vi.mock("@tanstack/react-query", async () => {
  const actual = await vi.importActual<typeof import("@tanstack/react-query")>(
    "@tanstack/react-query",
  );
  return {
    ...actual,
    useQuery: () => ({
      data: [
        {
          id: "mem-1",
          organization_id: "org-1",
          user_id: "user-1",
          user_full_name: "Alice Admin",
          user_email: "alice@example.com",
          role: "ADMIN",
          is_active: true,
          created_at: "2026-03-12T09:00:00Z",
          updated_at: "2026-03-12T09:00:00Z",
        },
        {
          id: "mem-2",
          organization_id: "org-1",
          user_id: "user-2",
          user_full_name: "Bob Member",
          user_email: "bob@example.com",
          role: "MEMBER",
          is_active: true,
          created_at: "2026-03-12T09:00:00Z",
          updated_at: "2026-03-12T09:00:00Z",
        },
      ],
      isLoading: false,
      isError: false,
    }),
  };
});

vi.mock("@/features/requests/api", () => ({
  useAssignRequestMutation: () => ({
    isPending: false,
    mutateAsync,
  }),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({
    pushToast: vi.fn(),
  }),
}));

describe("RequestAssignmentCard", () => {
  it("renders assignment UI and triggers mutation", async () => {
    render(
      <RequestAssignmentCard
        request={{
          id: "req-1",
          organization_id: "org-1",
          title: "Need valves",
          description: null,
          status: "UNDER_REVIEW",
          source: "EMAIL",
          created_by_membership_id: "mem-1",
          assigned_membership_id: "mem-1",
          created_at: "2026-03-12T09:00:00Z",
          updated_at: "2026-03-12T10:00:00Z",
        }}
      />,
    );

    expect(screen.getByText(/Alice Admin · ADMIN/i, { selector: "p" })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/responsable/i), {
      target: { value: "mem-2" },
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /asignar solicitud/i }));
    });

    expect(mutateAsync).toHaveBeenCalledWith({
      assigned_membership_id: "mem-2",
    });
  });
});
