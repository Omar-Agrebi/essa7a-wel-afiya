import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useMemo, useState, type FormEvent } from "react";
import { ArrowLeft, ArrowRight, Check, Eye, EyeOff, GraduationCap, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { TagInput } from "@/components/TagInput";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { loginUser, registerUser } from "@/lib/services";
import { getApiErrorMessage } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import type { UserLevel } from "@/types";

export const Route = createFileRoute("/register")({
  head: () => ({
    meta: [
      { title: "Create account — Intelligent University Observatory" },
      { name: "description", content: "Build your academic profile and start receiving personalised opportunities." },
    ],
  }),
  component: RegisterPage,
});

const INTEREST_SUGGESTIONS = [
  "Machine Learning", "NLP", "Computer Vision", "Robotics",
  "Cybersecurity", "Cloud Computing", "Bioinformatics",
  "HCI", "Quantum Computing", "Distributed Systems",
];
const SKILL_SUGGESTIONS = [
  "Python", "PyTorch", "TensorFlow", "SQL", "Docker",
  "Kubernetes", "React", "TypeScript", "Linux", "Git",
];

const STEPS = ["Account", "Academic", "Skills"] as const;

function passwordStrength(pwd: string): { score: number; label: string; color: string } {
  let s = 0;
  if (pwd.length >= 8) s++;
  if (/[A-Z]/.test(pwd)) s++;
  if (/[0-9]/.test(pwd)) s++;
  if (/[^A-Za-z0-9]/.test(pwd)) s++;
  if (pwd.length >= 12) s++;
  const labels = ["Too short", "Weak", "Fair", "Good", "Strong", "Excellent"];
  const colors = [
    "bg-destructive", "bg-destructive", "bg-warning", "bg-warning", "bg-success", "bg-success",
  ];
  return { score: s, label: labels[s] ?? "Weak", color: colors[s] ?? "bg-destructive" };
}

function RegisterPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [level, setLevel] = useState<UserLevel>("bachelor");
  const [interests, setInterests] = useState<string[]>([]);
  const [skills, setSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const strength = useMemo(() => passwordStrength(password), [password]);

  const validateStep = (): string | null => {
    if (step === 0) {
      if (!name.trim()) return "Please enter your full name.";
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Please enter a valid email address.";
      if (password.length < 8) return "Password must be at least 8 characters.";
    }
    if (step === 1) {
      if (interests.length === 0) return "Add at least one academic interest.";
    }
    if (step === 2) {
      if (skills.length === 0) return "Add at least one skill.";
    }
    return null;
  };

  const next = () => {
    const v = validateStep();
    if (v) {
      setError(v);
      return;
    }
    setError(null);
    setStep((s) => Math.min(STEPS.length - 1, s + 1));
  };

  const prev = () => {
    setError(null);
    setStep((s) => Math.max(0, s - 1));
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const v = validateStep();
    if (v) {
      setError(v);
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await registerUser({ name, email, password, skills, interests, level });
      const auth = await loginUser({ email, password });
      setAuth(auth.access_token, auth.user);
      toast.success("Account created — welcome aboard!");
      navigate({ to: "/dashboard" });
    } catch (err) {
      const msg = getApiErrorMessage(err, "Could not create your account.");
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-xl items-center px-4 py-12 sm:px-6">
      <div className="w-full">
        <div className="mb-8 text-center">
          <span className="mx-auto mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl gradient-brand text-primary-foreground shadow-elegant">
            <GraduationCap className="h-6 w-6" />
          </span>
          <h1 className="font-display text-2xl font-bold">Build your academic profile</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Three quick steps and we'll start curating opportunities for you.
          </p>
        </div>

        {/* Stepper */}
        <ol className="mb-8 flex items-center justify-between gap-2" aria-label="Progress">
          {STEPS.map((label, i) => {
            const done = i < step;
            const active = i === step;
            return (
              <li key={label} className="flex flex-1 items-center gap-2">
                <span
                  className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-xs font-semibold transition",
                    done && "border-primary bg-primary text-primary-foreground",
                    active && "border-primary bg-primary/10 text-primary",
                    !done && !active && "border-border bg-card text-muted-foreground",
                  )}
                  aria-current={active ? "step" : undefined}
                >
                  {done ? <Check className="h-4 w-4" /> : i + 1}
                </span>
                <span
                  className={cn(
                    "hidden text-xs font-medium sm:inline",
                    active ? "text-foreground" : "text-muted-foreground",
                  )}
                >
                  {label}
                </span>
                {i < STEPS.length - 1 && (
                  <span className={cn("h-px flex-1", done ? "bg-primary" : "bg-border")} />
                )}
              </li>
            );
          })}
        </ol>

        <form
          onSubmit={submit}
          className="space-y-5 rounded-2xl border border-border bg-card p-6 shadow-elegant"
        >
          {step === 0 && (
            <>
              <div className="space-y-2">
                <Label htmlFor="name">Full name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Ada Lovelace" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@university.edu"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPwd ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    className="pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPwd((v) => !v)}
                    aria-label={showPwd ? "Hide password" : "Show password"}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1.5 text-muted-foreground hover:text-foreground"
                  >
                    {showPwd ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {password && (
                  <div className="space-y-1">
                    <div className="flex h-1.5 gap-1">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <span
                          key={i}
                          className={cn(
                            "h-full flex-1 rounded-full transition",
                            i < strength.score ? strength.color : "bg-muted",
                          )}
                        />
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground">{strength.label}</p>
                  </div>
                )}
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <div className="space-y-2">
                <Label htmlFor="level">Academic level</Label>
                <Select value={level} onValueChange={(v) => setLevel(v as UserLevel)}>
                  <SelectTrigger id="level">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bachelor">Bachelor</SelectItem>
                    <SelectItem value="master">Master</SelectItem>
                    <SelectItem value="phd">PhD</SelectItem>
                    <SelectItem value="professional">Professional / Researcher</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="interests">Research interests</Label>
                <TagInput
                  id="interests"
                  value={interests}
                  onChange={setInterests}
                  ariaLabel="Add an interest"
                  placeholder="e.g. Machine Learning"
                  suggestions={INTEREST_SUGGESTIONS}
                />
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="space-y-2">
                <Label htmlFor="skills">Skills</Label>
                <TagInput
                  id="skills"
                  value={skills}
                  onChange={setSkills}
                  ariaLabel="Add a skill"
                  placeholder="e.g. Python"
                  suggestions={SKILL_SUGGESTIONS}
                />
              </div>
              <div className="rounded-lg border border-border bg-secondary/40 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Profile review</p>
                <dl className="mt-3 space-y-2 text-sm">
                  <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Name</dt><dd className="font-medium">{name}</dd></div>
                  <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Email</dt><dd className="truncate font-medium">{email}</dd></div>
                  <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Level</dt><dd className="font-medium capitalize">{level}</dd></div>
                  <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Interests</dt><dd className="text-right">{interests.length} added</dd></div>
                  <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Skills</dt><dd className="text-right">{skills.length} added</dd></div>
                </dl>
              </div>
            </>
          )}

          {error && (
            <div role="alert" className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between gap-3 pt-2">
            <Button type="button" variant="ghost" onClick={prev} disabled={step === 0 || loading}>
              <ArrowLeft className="mr-1 h-4 w-4" /> Back
            </Button>
            {step < STEPS.length - 1 ? (
              <Button type="button" onClick={next} className="gradient-brand text-primary-foreground hover:opacity-95">
                Continue <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            ) : (
              <Button type="submit" disabled={loading} className="gradient-brand text-primary-foreground hover:opacity-95">
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create account
              </Button>
            )}
          </div>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
