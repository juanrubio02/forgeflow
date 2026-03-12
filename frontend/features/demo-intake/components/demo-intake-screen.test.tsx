import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import { DemoIntakeScreen } from "@/features/demo-intake/components/demo-intake-screen";

const pushMock = vi.fn();
const mutateAsyncMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

vi.mock("@/features/demo-intake/api", () => ({
  useDemoIntakeScenariosQuery: () => ({
    isLoading: false,
    isError: false,
    data: [
      {
        key: "rfq_brackets_email",
        title: "RFQ - Stainless Steel Mounting Brackets",
        source: "EMAIL",
        sender: "procurement@powergensystems.com",
        expected_document_type: "QUOTE_REQUEST",
        attachments: 1,
        description: "Standard incoming RFQ with metal part requirements.",
      },
      {
        key: "technical_spec_document",
        title: "Technical specification package",
        source: "EMAIL",
        sender: "engineering@novafluid.com",
        expected_document_type: "TECHNICAL_SPEC",
        attachments: 1,
        description: "Specification document with materials and operating conditions.",
      },
    ],
  }),
  useRunDemoIntakeScenarioMutation: () => ({
    isPending: false,
    mutateAsync: mutateAsyncMock,
  }),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({
    pushToast: vi.fn(),
  }),
}));

describe("DemoIntakeScreen", () => {
  beforeEach(() => {
    pushMock.mockReset();
    mutateAsyncMock.mockReset();
  });

  it("renders demo intake scenario cards", () => {
    render(<DemoIntakeScreen />);

    expect(screen.getByText(/simulador de intake demo/i)).toBeInTheDocument();
    expect(
      screen.getByText(/RFQ - Stainless Steel Mounting Brackets/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/Technical specification package/i)).toBeInTheDocument();
  });

  it("runs a scenario and redirects to request detail", async () => {
    mutateAsyncMock.mockResolvedValue({
      request_id: "req-123",
      document_ids: ["doc-1"],
      scenario_key: "rfq_brackets_email",
    });

    render(<DemoIntakeScreen />);

    fireEvent.click(screen.getAllByRole("button", { name: /generar solicitud/i })[0]);

    await waitFor(() => {
      expect(mutateAsyncMock).toHaveBeenCalledWith("rfq_brackets_email");
      expect(pushMock).toHaveBeenCalledWith("/requests/req-123");
    });
  });
});
