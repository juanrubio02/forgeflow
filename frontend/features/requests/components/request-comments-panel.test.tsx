import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { RequestCommentsPanel } from "@/features/requests/components/request-comments-panel";

const mutateAsync = vi.fn();

vi.mock("@/features/requests/api", () => ({
  useCreateRequestCommentMutation: () => ({
    isPending: false,
    mutateAsync,
  }),
}));

vi.mock("@/hooks/use-membership", () => ({
  useMembership: () => ({
    activeMembership: {
      id: "mem-1",
      role: "ADMIN",
    },
  }),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({
    pushToast: vi.fn(),
  }),
}));

describe("RequestCommentsPanel", () => {
  it("renders comments and posts a new one", async () => {
    render(
      <RequestCommentsPanel
        requestId="req-1"
        isLoading={false}
        isError={false}
        comments={[
          {
            id: "comment-1",
            request_id: "req-1",
            organization_id: "org-1",
            membership_id: "mem-1",
            body: "Need supplier clarification.",
            created_at: "2026-03-12T09:00:00Z",
            updated_at: "2026-03-12T09:00:00Z",
          },
        ]}
      />,
    );

    expect(screen.getByText("Need supplier clarification.")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/añadir comentario interno/i), {
      target: { value: "Please verify the coating spec." },
    });
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /publicar comentario/i }));
    });

    expect(mutateAsync).toHaveBeenCalledWith({
      body: "Please verify the coating spec.",
    });
  });
});
