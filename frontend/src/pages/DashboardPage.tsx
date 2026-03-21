import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Loader2,
  BookOpen,
  Video,
  Code2,
  Lock,
  CheckCircle2,
  Zap,
  Lightbulb,
  ArrowRight,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { StepIndicator } from "@/components/StepIndicator";
import { ConfidenceBar } from "@/components/ConfidenceBar";
import { useOnboarding } from "@/context/OnboardingContext";
import { api } from "@/lib/api";
import { ChatPanel } from "@/components/ChatPanel";
import type { ComputePathResponse, LearningPathItem } from "@/types/onboarding";
import { logout } from "@/lib/auth";

const STEPS = ["Upload", "Quiz", "Dashboard"];

const resourceIcon = {
  video: Video,
  documentation: BookOpen,
  practice: Code2,
};

function SkillNode({ item, index }: { item: LearningPathItem; index: number }) {
  const [open, setOpen] = useState(item.status === "current");
  const Icon = item.status === "completed" ? CheckCircle2 : item.status === "current" ? Zap : Lock;

  const statusStyles = {
    completed: "border-success/30 bg-success/5",
    current: "border-primary shadow-md shadow-primary/10",
    locked: "border-border opacity-60",
  };

  return (
    <div
      className={`animate-fade-up rounded-xl border p-5 transition-all ${statusStyles[item.status]}`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between text-left active:scale-[0.99]"
      >
        <div className="flex items-center gap-3">
          <div
            className={`flex h-9 w-9 items-center justify-center rounded-lg ${
              item.status === "completed"
                ? "bg-success text-success-foreground"
                : item.status === "current"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            }`}
          >
            <Icon className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">{item.skill}</h3>
            <p className="text-xs text-muted-foreground capitalize">{item.status}</p>
          </div>
        </div>
        <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="animate-fade-in mt-4 space-y-4 border-t pt-4">
          {/* Reasoning */}
          <div className="flex gap-2 rounded-lg bg-muted/50 p-3">
            <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
            <p className="text-sm text-muted-foreground">{item.reasoning}</p>
          </div>

          {/* Resources */}
          {item.resources?.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Resources</p>
              {item.resources.map((r, i) => {
                const RIcon = resourceIcon[r.type] || BookOpen;
                return (
                  <a
                    key={i}
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 rounded-lg border bg-card px-4 py-3 text-sm font-medium text-foreground transition-all hover:border-primary/30 hover:shadow-sm active:scale-[0.98]"
                  >
                    <RIcon className="h-4 w-4 text-primary" />
                    <span className="flex-1">{r.title}</span>
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                  </a>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { skills, proficiency, importance_scores, user_confidence, setLearningPath, learningPath } = useOnboarding();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  useEffect(() => {
    if (!skills.length) {
      navigate("/");
      return;
    }

    const load = async () => {
      try {
        const data = await api.computePath({
          skills,
          proficiency,
          importance_scores,
          user_confidence,
        }) as ComputePathResponse;
        setLearningPath(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to compute learning path.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [skills, proficiency, importance_scores, user_confidence, navigate, setLearningPath]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="animate-fade-in flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Computing your personalized learning path…</p>
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
            Start Over
          </Button>
        </div>
      </div>
    );
  }

  const path = learningPath?.learning_path || [];

  return (
    <div className="min-h-screen bg-background pb-24">
      <div className="mx-auto max-w-4xl px-4 py-8 sm:py-12">
        <div className="flex items-center justify-between gap-4">
          <StepIndicator steps={STEPS} currentStep={2} />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </div>

        <div className="animate-fade-up mt-8 text-center">
          <h1 className="text-balance text-3xl font-bold tracking-tight text-foreground sm:text-4xl" style={{ lineHeight: "1.1" }}>
            Your Learning Roadmap
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-muted-foreground">
            A personalized path based on your skill gaps, job requirements, and confidence levels.
          </p>
        </div>

        {/* Skill Summary */}
        <section className="animate-fade-up stagger-2 mt-10">
          <h2 className="mb-4 text-lg font-semibold text-foreground">Skill Confidence Overview</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border bg-card p-5 shadow-sm">
              <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Your Confidence</p>
              <div className="space-y-4">
                {skills.map((skill) => (
                  <ConfidenceBar
                    key={skill}
                    label={skill}
                    value={user_confidence[skill] ?? 0}
                  />
                ))}
              </div>
            </div>
            <div className="rounded-xl border bg-card p-5 shadow-sm">
              <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Test Proficiency</p>
              <div className="space-y-4">
                {skills.map((skill) => (
                  <ConfidenceBar
                    key={skill}
                    label={skill}
                    value={proficiency[skill] ?? 0}
                    colorClass="bg-info"
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Learning Path */}
        <section className="mt-10">
          <h2 className="mb-4 text-lg font-semibold text-foreground">Learning Path</h2>
          <div className="relative space-y-4">
            {/* Connecting line */}
            <div className="absolute left-[29px] top-[44px] bottom-6 w-px bg-border sm:left-[29px]" />
            {path.map((item, i) => (
              <SkillNode key={item.skill} item={item} index={i} />
            ))}
          </div>
        </section>
      </div>

      <ChatPanel />
    </div>
  );
}
