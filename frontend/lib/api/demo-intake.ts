import { apiRequest } from "@/lib/api/client";
import type {
  DemoIntakeRunResult,
  DemoIntakeScenario,
} from "@/lib/api/types";

export function listDemoIntakeScenarios(): Promise<DemoIntakeScenario[] | null> {
  return apiRequest<DemoIntakeScenario[]>("/demo/intake/scenarios", {
    includeAuth: true,
    includeMembership: true,
  });
}

export function runDemoIntakeScenario(
  scenarioKey: string,
): Promise<DemoIntakeRunResult | null> {
  return apiRequest<DemoIntakeRunResult>(`/demo/intake/scenarios/${scenarioKey}/run`, {
    method: "POST",
    includeAuth: true,
    includeMembership: true,
  });
}
