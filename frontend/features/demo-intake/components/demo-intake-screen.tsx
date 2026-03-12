"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileStack, Mail, PlayCircle, Sparkles } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDemoIntakeScenariosQuery, useRunDemoIntakeScenarioMutation } from "@/features/demo-intake/api";
import { useToast } from "@/hooks/use-toast";
import { interpolate, useI18n } from "@/i18n/hooks";

export function DemoIntakeScreen() {
  const router = useRouter();
  const { pushToast } = useToast();
  const { messages } = useI18n();
  const scenariosQuery = useDemoIntakeScenariosQuery();
  const runScenarioMutation = useRunDemoIntakeScenarioMutation();
  const [activeScenarioKey, setActiveScenarioKey] = useState<string | null>(null);

  const handleRunScenario = async (scenarioKey: string) => {
    try {
      setActiveScenarioKey(scenarioKey);
      const result = await runScenarioMutation.mutateAsync(scenarioKey);
      if (!result?.request_id) {
        return;
      }

      pushToast({
        tone: "success",
        title: messages.demoIntake.run.successTitle,
        description: interpolate(messages.demoIntake.run.successDescription, {
          scenario: scenarioKey,
        }),
      });
      router.push(`/requests/${result.request_id}`);
    } catch (error) {
      const detail =
        error instanceof Error
          ? error.message
          : messages.demoIntake.run.fallbackError;
      pushToast({
        tone: "error",
        title: messages.demoIntake.run.errorTitle,
        description: detail,
      });
    } finally {
      setActiveScenarioKey(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={messages.demoIntake.header.eyebrow}
        title={messages.demoIntake.header.title}
        description={messages.demoIntake.header.description}
        actions={
          <Badge variant="info" size="sm" dot>
            {messages.demoIntake.header.badge}
          </Badge>
        }
      />

      {scenariosQuery.isLoading ? (
        <div className="grid gap-4 xl:grid-cols-2">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-[240px] w-full" />
          ))}
        </div>
      ) : scenariosQuery.isError ? (
        <Card>
          <CardContent className="px-8 py-10 text-center text-sm text-slate-600">
            {messages.demoIntake.list.loadError}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 xl:grid-cols-2">
          {(scenariosQuery.data ?? []).map((scenario) => {
            const isRunning =
              runScenarioMutation.isPending && activeScenarioKey === scenario.key;

            return (
              <Card key={scenario.key} className="border-line/70 bg-white/95">
                <CardHeader className="space-y-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="space-y-2">
                      <p className="eyebrow">{messages.demoIntake.card.eyebrow}</p>
                      <CardTitle className="max-w-xl leading-tight">
                        {scenario.title}
                      </CardTitle>
                    </div>
                    <Badge variant="neutral" size="sm">
                      {messages.requests.sources[scenario.source]}
                    </Badge>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Badge variant="info" size="sm">
                      {scenario.expected_document_type
                        ? messages.documents.detectedTypes[scenario.expected_document_type]
                        : messages.documents.detectedTypes.UNKNOWN}
                    </Badge>
                    <Badge variant="neutral" size="sm">
                      {interpolate(messages.demoIntake.card.attachments, {
                        count: scenario.attachments,
                      })}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-5">
                  <p className="text-sm leading-6 text-slate-600">
                    {scenario.description}
                  </p>

                  <div className="grid gap-3 rounded-[var(--radius-panel)] border border-line/70 bg-surface/70 p-4 sm:grid-cols-2">
                    <div className="flex items-start gap-3">
                      <Mail className="mt-0.5 h-4 w-4 text-slate-500" />
                      <div className="space-y-1">
                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                          {messages.demoIntake.card.sender}
                        </p>
                        <p className="text-sm font-medium text-slate-800">
                          {scenario.sender}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <FileStack className="mt-0.5 h-4 w-4 text-slate-500" />
                      <div className="space-y-1">
                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                          {messages.demoIntake.card.flow}
                        </p>
                        <p className="text-sm font-medium text-slate-800">
                          {messages.demoIntake.card.flowValue}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-4 rounded-[var(--radius-panel)] border border-dashed border-line bg-surfaceMuted/65 px-4 py-3">
                    <div className="flex items-center gap-3 text-sm text-slate-600">
                      <Sparkles className="h-4 w-4 text-accent" />
                      <span>{messages.demoIntake.card.intelligenceHint}</span>
                    </div>
                    <Button
                      type="button"
                      onClick={() => handleRunScenario(scenario.key)}
                      disabled={runScenarioMutation.isPending}
                    >
                      <PlayCircle className="h-4 w-4" />
                      {isRunning
                        ? messages.demoIntake.run.pending
                        : messages.demoIntake.run.cta}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
