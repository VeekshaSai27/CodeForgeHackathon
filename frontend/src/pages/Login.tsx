import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { isLoggedIn } from "@/lib/auth";

type Tab = "signin" | "signup";

export default function LoginPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isLoggedIn()) navigate("/upload", { replace: true });
  }, [navigate]);

  const saveUser = (displayName: string, displayEmail: string) => {
    localStorage.setItem("user", JSON.stringify({ name: displayName, email: displayEmail }));
    navigate("/upload");
  };

  const handleGoogle = () => saveUser("User", "user@gmail.com");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (tab === "signup") {
      if (!name.trim()) return setError("Please enter your name.");
      if (password !== confirm) return setError("Passwords do not match.");
      if (password.length < 6) return setError("Password must be at least 6 characters.");
    }
    if (!email.trim()) return setError("Please enter your email.");
    if (!password) return setError("Please enter your password.");

    setLoading(true);
    // Simulate async auth — replace with real API call when auth backend is ready
    setTimeout(() => {
      setLoading(false);
      saveUser(tab === "signup" ? name.trim() : email.split("@")[0], email.trim());
    }, 600);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">

        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
            <Sparkles className="h-3.5 w-3.5" />
            AI-Powered Learning
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Skill Journey AI</h1>
          <p className="text-sm text-muted-foreground">Your personalized path to career growth</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border bg-card shadow-lg shadow-primary/10 px-8 py-8 space-y-6">

          {/* Tabs */}
          <div className="flex rounded-lg bg-muted p-1 gap-1">
            {(["signin", "signup"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => { setTab(t); setError(""); }}
                className={`flex-1 rounded-md py-1.5 text-sm font-medium transition-all ${
                  tab === t
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {t === "signin" ? "Sign In" : "Sign Up"}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {tab === "signup" && (
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full rounded-lg border bg-muted/50 px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 transition"
                />
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full rounded-lg border bg-muted/50 px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 transition"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border bg-muted/50 px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 transition"
              />
            </div>

            {tab === "signup" && (
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Confirm Password</label>
                <input
                  type="password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-lg border bg-muted/50 px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 transition"
                />
              </div>
            )}

            {error && (
              <p className="rounded-lg bg-destructive/10 px-3 py-2 text-xs text-destructive">{error}</p>
            )}

            <Button type="submit" disabled={loading} className="w-full h-11 font-semibold shadow-md shadow-primary/20">
              {loading
                ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Please wait…</>
                : tab === "signin" ? "Sign In" : "Create Account"
              }
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-xs text-muted-foreground">or continue with</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          {/* Google */}
          <Button
            type="button"
            onClick={handleGoogle}
            className="w-full h-11 bg-white text-foreground hover:bg-muted border border-input flex items-center justify-center gap-2 text-sm font-medium shadow-sm"
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 via-green-500 to-red-500 text-[11px] font-semibold text-white">
              G
            </span>
            Sign in with Google
          </Button>
        </div>
      </div>
    </div>
  );
}
