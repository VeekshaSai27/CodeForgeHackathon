import { generateLearningExperience } from "../lib/learningEngine";
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

const STEPS = ["Upload", "Quiz", "Dashboard"];

const resourceIcon = {
  video: Video,
  documentation: BookOpen,
  practice: Code2,
};

function SkillNode({
  item,
  index,
  proficiency,
  importance,
  confidence,
}: {
  item: LearningPathItem;
  index: number;
  proficiency?: number;
  importance?: number;
  confidence?: number;
}) {
  const [open, setOpen] = useState(item.status === "current");

  const Icon =
    item.status === "completed"
      ? CheckCircle2
      : item.status === "current"
      ? Zap
      : Lock;

  const statusStyles = {
    completed: "border-success/30 bg-success/5",
    current: "border-primary shadow-md shadow-primary/10",
    locked: "border-border opacity-60",
  };

  // 🔥 Learning Experience Logic
  const experience = generateLearningExperience({
    skill: item.skill,
    proficiency: proficiency ?? 0,
    importance: importance ?? 0,
    confidence: confidence ?? 0,
  });

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
            <p className="text-xs text-muted-foreground capitalize">
              {item.status}
            </p>
          </div>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-muted-foreground transition-transform ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>

      {open && (
        <div className="animate-fade-in mt-4 space-y-4 border-t pt-4">
          {/* Reasoning */}
          <div className="flex gap-2 rounded-lg bg-muted/50 p-3">
            <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
            <p className="text-sm text-muted-foreground">
              {item.reasoning}
            </p>
          </div>

          {/* 🔥 Next Action */}
          <div className="rounded-lg border bg-primary/5 p-3">
            <p className="text-sm font-medium text-primary">
              👉 Next Step: {experience.next_action}
            </p>
          </div>

          {/* 🔥 Mentor Explanation */}
          <div className="flex gap-2 rounded-lg bg-muted/50 p-3">
            <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
            <p className="text-sm text-muted-foreground">
              {experience.mentor_explanation}
            </p>
          </div>

          {/* Backend Resources */}
          {item.resources?.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Resources
              </p>
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

          {/* 🔥 Your Learning Engine Resources */}
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Suggested Learning
            </p>

            {experience.resources.videos.map((v, i) => (
              <div key={i} className="text-sm">🎥 {v}</div>
            ))}

            {experience.resources.docs.map((d, i) => (
              <div key={i} className="text-sm">📄 {d}</div>
            ))}

            {experience.resources.practice.map((p, i) => (
              <div key={i} className="text-sm">🧪 {p}</div>
            ))}
          </div>

          <button className="mt-2 rounded-lg border px-3 py-2 text-sm hover:bg-muted">
            Take Test Again
          </button>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const {
    skills,
    proficiency,
    importance_scores,
    user_confidence,
    setLearningPath,
    learningPath,
  } = useOnboarding();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!skills.length) {
      navigate("/");
      return;
    }

    const load = async () => {
      try {
        const data = (await api.computePath({
          skills,
          proficiency,
          importance_scores,
          user_confidence,
        })) as ComputePathResponse;

        setLearningPath(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to compute learning path."
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [
    skills,
    proficiency,
    importance_scores,
    user_confidence,
    navigate,
    setLearningPath,
  ]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  const path = learningPath?.learning_path || [];

  return (
    <div className="min-h-screen bg-background pb-24">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <StepIndicator steps={STEPS} currentStep={2} />

        <h1 className="mt-6 text-center text-3xl font-bold">
          Your Learning Roadmap
        </h1>

        {/* Skill Summary */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div>
            {skills.map((skill) => (
              <ConfidenceBar
                key={skill}
                label={skill}
                value={user_confidence[skill] ?? 0}
              />
            ))}
          </div>

          <div>
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

        {/* Learning Path */}
        <div className="mt-10 space-y-4">
          {path.map((item, i) => (
            <SkillNode
              key={item.skill}
              item={item}
              index={i}
              proficiency={proficiency[item.skill]}
              importance={importance_scores[item.skill]}
              confidence={user_confidence[item.skill]}
            />
          ))}
        </div>
      </div>

      <ChatPanel />
    </div>
  );
}