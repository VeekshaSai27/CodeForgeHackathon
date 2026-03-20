import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, FileText, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StepIndicator } from "@/components/StepIndicator";
import { useOnboarding } from "@/context/OnboardingContext";
import { api } from "@/lib/api";
import type { AnalyzeProfileResponse } from "@/types/onboarding";

const STEPS = ["Upload", "Quiz", "Dashboard"];

export default function UploadPage() {
  const navigate = useNavigate();
  const { setAnalysis } = useOnboarding();
  const [resume, setResume] = useState("");
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setResume(text);
  };

  const handleAnalyze = async () => {
    if (!resume.trim() || !jd.trim()) {
      setError("Please provide both your resume and the job description.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const data = await api.analyzeProfile(resume, jd) as AnalyzeProfileResponse;
      setAnalysis(data);
      navigate("/quiz");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-3xl px-4 py-8 sm:py-12">
        <StepIndicator steps={STEPS} currentStep={0} />

        <div className="animate-fade-up mt-8 text-center">
          <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
            <Sparkles className="h-3.5 w-3.5" />
            AI-Powered Analysis
          </div>
          <h1 className="text-balance text-3xl font-bold tracking-tight text-foreground sm:text-4xl" style={{ lineHeight: "1.1" }}>
            Let's map your skills
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-muted-foreground">
            Paste your resume and the job description — we'll identify your strengths and gaps instantly.
          </p>
        </div>

        <div className="animate-fade-up stagger-2 mt-10 space-y-6">
          {/* Resume */}
          <div className="rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md">
            <div className="mb-3 flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <FileText className="h-4 w-4 text-primary" />
                Your Resume
              </label>
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-primary hover:bg-primary/5 transition-colors active:scale-[0.97]"
              >
                <Upload className="h-3 w-3" />
                Upload file
              </button>
              <input
                ref={fileRef}
                type="file"
                accept=".txt,.pdf,.doc,.docx"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
            <textarea
              value={resume}
              onChange={(e) => setResume(e.target.value)}
              placeholder="Paste your resume content here..."
              rows={7}
              className="w-full resize-none rounded-lg border-0 bg-muted/50 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/20 transition-shadow"
            />
          </div>

          {/* Job Description */}
          <div className="rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md">
            <label className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
              <FileText className="h-4 w-4 text-accent" />
              Job Description
            </label>
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste the job description here..."
              rows={7}
              className="w-full resize-none rounded-lg border-0 bg-muted/50 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/20 transition-shadow"
            />
          </div>

          {error && (
            <p className="animate-fade-in rounded-lg bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
              {error}
            </p>
          )}

          <Button
            onClick={handleAnalyze}
            disabled={loading || !resume.trim() || !jd.trim()}
            className="w-full h-12 text-base font-semibold shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all active:scale-[0.98] disabled:opacity-50 disabled:shadow-none"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing your profile…
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Analyze My Skills
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
