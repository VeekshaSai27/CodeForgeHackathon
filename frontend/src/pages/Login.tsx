import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { isLoggedIn } from "@/lib/auth";

const DUMMY_USER = {
  name: "User",
  email: "user@gmail.com",
};

export default function LoginPage() {
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoggedIn()) {
      navigate("/upload", { replace: true });
    }
  }, [navigate]);

  const handleGoogleSignIn = () => {
    localStorage.setItem("user", JSON.stringify(DUMMY_USER));
    navigate("/upload");
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border bg-card shadow-lg shadow-primary/10 px-8 py-10 space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Skill Journey AI
          </h1>
          <p className="text-sm text-muted-foreground">
            Login to continue your personalized learning journey
          </p>
        </div>

        <div className="pt-4">
          <Button
            type="button"
            onClick={handleGoogleSignIn}
            className="w-full h-11 bg-white text-foreground hover:bg-muted border border-input flex items-center justify-center gap-2 text-sm font-medium shadow-sm"
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 via-green-500 to-red-500 text-[11px] font-semibold text-white">
              G
            </span>
            <span>Sign in with Google</span>
          </Button>
        </div>

        <p className="text-xs text-center text-muted-foreground">
          This is a demo login. Google OAuth will be added later.
        </p>
      </div>
    </div>
  );
}
