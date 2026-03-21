import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle2, Loader2, ArrowRight } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { StepIndicator } from "@/components/StepIndicator";
import { useOnboarding } from "@/context/OnboardingContext";
import { api } from "@/lib/api";
import { runCode } from "@/lib/codeRunner";
import type { QuizQuestion, EvaluateTestResponse } from "@/types/onboarding";

const STEPS = ["Upload", "Quiz", "Dashboard"];

export default function QuizPage() {
  const navigate = useNavigate();
  const { skills, setEvaluation } = useOnboarding();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [codeOutputs, setCodeOutputs] = useState<Record<string, string>>({});
  const [codeRunning, setCodeRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!skills.length) {
      navigate("/");
      return;
    }

    const load = async () => {
      try {
        const data = (await api.generateTest(skills)) as { questions: QuizQuestion[] };
        const limitedQuestions = (data.questions || []).slice(0, 25);
        setQuestions(limitedQuestions);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load quiz.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [skills, navigate]);

  const current = questions[currentIdx];
  const progress = questions.length ? ((currentIdx + 1) / questions.length) * 100 : 0;
  const isLast = currentIdx === questions.length - 1;
  const selectedAnswer = current ? answers[current.id] : undefined;
  const isCoding = current?.type === "coding";
  const canProceed = isCoding
    ? !!(answers[current?.id ?? ""]?.trim())
    : !!selectedAnswer;

  const selectOption = (option: string) => {
    if (!current) return;
    setAnswers((prev) => ({ ...prev, [current.id]: option }));
  };

  const handleCodeChange = (code: string) => {
    if (!current) return;
    setAnswers((prev) => ({ ...prev, [current.id]: code }));
  };

  const handleRunCode = async () => {
    if (!current) return;
    const code = answers[current.id] ?? current.starterCode ?? "";
    setCodeRunning(true);
    const output = await runCode(code, current.language || "javascript");
    setCodeOutputs((prev) => ({ ...prev, [current.id]: output }));
    setCodeRunning(false);
  };

  const handleNext = async () => {
    if (!isLast) {
      setCurrentIdx((i) => i + 1);
      return;
    }

    setSubmitting(true);
    try {
      const data = await api.evaluateTest(answers) as EvaluateTestResponse;
      setEvaluation(data);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit quiz.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="animate-fade-in flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Generating your skill assessment…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="animate-fade-in rounded-xl border bg-card p-8 text-center shadow-sm">
          <p className="text-destructive">{error}</p>
          <Button onClick={() => navigate("/")} className="mt-4" variant="outline">
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-2xl px-4 py-8 sm:py-12">
        <StepIndicator steps={STEPS} currentStep={1} />

        {/* Progress */}
        <div className="mt-8 mb-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>Question {currentIdx + 1} of {questions.length}</span>
          <span className="font-medium tabular-nums">{Math.round(progress)}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {current && (
          <div className="animate-fade-up mt-8" key={current.id}>
            <div className="rounded-xl border bg-card p-6 shadow-sm sm:p-8">
              <span className="mb-2 inline-block rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                {current.skill}
              </span>
              <div className="mt-2 text-lg font-semibold text-foreground sm:text-xl [&>p]:leading-snug [&>p]:my-0 [&_code]:rounded [&_code]:bg-muted [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:text-sm [&_code]:font-mono [&_code]:text-foreground">
                <ReactMarkdown>{current.question}</ReactMarkdown>
              </div>
              {(!current.type || current.type === "mcq") && (
                <div className="mt-6 space-y-3">
                  {current.options.map((opt) => {
                    const selected = selectedAnswer === opt;
                    return (
                      <button
                        key={opt}
                        onClick={() => selectOption(opt)}
                        className={`w-full rounded-lg border px-4 py-3.5 text-left text-sm font-medium transition-all active:scale-[0.98] ${
                          selected
                            ? "border-primary bg-primary/5 text-foreground ring-2 ring-primary/20"
                            : "border-border bg-card text-foreground hover:border-primary/30 hover:bg-muted/50"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
                              selected ? "border-primary bg-primary" : "border-muted-foreground/30"
                            }`}
                          >
                            {selected && <CheckCircle2 className="h-3 w-3 text-primary-foreground" />}
                          </div>
                          <span className="[&>p]:my-0 [&_code]:rounded [&_code]:bg-muted [&_code]:px-1 [&_code]:py-0.5 [&_code]:text-xs [&_code]:font-mono">
                            <ReactMarkdown>{opt}</ReactMarkdown>
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}

              {current.type === "coding" && (
                <div className="mt-6 space-y-4">
                  <textarea
                    className="min-h-[200px] w-full rounded-md border bg-muted/40 p-3 font-mono text-sm outline-none focus-visible:ring-2 focus-visible:ring-primary"
                    value={answers[current.id] ?? current.starterCode ?? ""}
                    onChange={(e) => handleCodeChange(e.target.value)}
                    spellCheck={false}
                  />
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs text-muted-foreground">
                      Language: {current.language || "javascript"}
                    </span>
                    <Button type="button" variant="outline" size="sm" onClick={handleRunCode} disabled={codeRunning}>
                      {codeRunning ? <><Loader2 className="mr-1 h-3 w-3 animate-spin" />Running…</> : "Run Code"}
                    </Button>
                  </div>
                  <div className="rounded-md border bg-muted/40 p-3">
                    <div className="mb-1 text-xs font-medium text-muted-foreground">Output</div>
                    <pre className="max-h-40 overflow-auto whitespace-pre-wrap break-words text-xs font-mono text-foreground">
                      {codeOutputs[current.id] || "(no output yet)"}
                    </pre>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <Button
                onClick={handleNext}
                disabled={!canProceed || submitting}
                className="min-w-[140px] shadow-lg shadow-primary/20 active:scale-[0.97] disabled:shadow-none"
              >
                {submitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Submitting…
                  </>
                ) : isLast ? (
                  "View Results"
                ) : (
                  <>
                    Next
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
