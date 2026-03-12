"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { runDemoIntakeScenario, listDemoIntakeScenarios } from "@/lib/api/demo-intake";
import { requestsKeys } from "@/features/requests/api";

export const demoIntakeKeys = {
  all: ["demo-intake"] as const,
  scenarios: () => [...demoIntakeKeys.all, "scenarios"] as const,
};

export function useDemoIntakeScenariosQuery() {
  return useQuery({
    queryKey: demoIntakeKeys.scenarios(),
    queryFn: async () => (await listDemoIntakeScenarios()) ?? [],
  });
}

export function useRunDemoIntakeScenarioMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (scenarioKey: string) => runDemoIntakeScenario(scenarioKey),
    onSuccess: async (result) => {
      await queryClient.invalidateQueries({ queryKey: requestsKeys.all });
      if (result?.request_id) {
        await queryClient.invalidateQueries({
          queryKey: requestsKeys.detail(result.request_id),
        });
      }
    },
  });
}
