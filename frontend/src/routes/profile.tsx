import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Loader2, LogOut, Mail, Save, ShieldCheck, GraduationCap } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TagInput } from "@/components/TagInput";
import { RequireAuth } from "@/components/RequireAuth";
import { fetchMe, updateMe, updateMyInterests, updateMySkills } from "@/lib/services";
import { getApiErrorMessage } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import type { UserLevel } from "@/types";

export const Route = createFileRoute("/profile")({
  head: () => ({
    meta: [
      { title: "Profile — Intelligent University Observatory" },
      { name: "description", content: "Manage your academic profile, skills and interests." },
    ],
  }),
  component: () => (
    <RequireAuth>
      <ProfilePage />
    </RequireAuth>
  ),
});

function ProfilePage() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();

  const [name, setName] = useState(user?.name ?? "");
  const [level, setLevel] = useState<UserLevel>(user?.level ?? "bachelor");
  const [skills, setSkills] = useState<string[]>(user?.skills ?? []);
  const [interests, setInterests] = useState<string[]>(user?.interests ?? []);

  const [savingAccount, setSavingAccount] = useState(false);
  const [savingSkills, setSavingSkills] = useState(false);
  const [savingInterests, setSavingInterests] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetchMe()
      .then((u) => {
        if (!active) return;
        setUser(u);
        setName(u.name);
        setLevel(u.level);
        setSkills(u.skills ?? []);
        setInterests(u.interests ?? []);
      })
      .catch(() => {
        /* silent — store fallback */
      })
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSaveAccount = async () => {
    setSavingAccount(true);
    try {
      const updated = await updateMe({ name, level });
      setUser(updated);
      toast.success("Profile updated");
    } catch (e) {
      toast.error(getApiErrorMessage(e, "Could not save profile."));
    } finally {
      setSavingAccount(false);
    }
  };

  const onSaveSkills = async () => {
    setSavingSkills(true);
    try {
      const updated = await updateMySkills(skills);
      setUser(updated);
      toast.success("Skills updated");
    } catch (e) {
      toast.error(getApiErrorMessage(e, "Could not save skills."));
    } finally {
      setSavingSkills(false);
    }
  };

  const onSaveInterests = async () => {
    setSavingInterests(true);
    try {
      const updated = await updateMyInterests(interests);
      setUser(updated);
      toast.success("Interests updated");
    } catch (e) {
      toast.error(getApiErrorMessage(e, "Could not save interests."));
    } finally {
      setSavingInterests(false);
    }
  };

  const onLogout = () => {
    logout();
    toast.success("Signed out");
    navigate({ to: "/" });
  };

  const initials = (user?.name ?? "U")
    .split(/\s+/)
    .map((s) => s[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <header className="flex flex-col items-start gap-6 sm:flex-row sm:items-center">
        <span className="flex h-20 w-20 items-center justify-center rounded-2xl gradient-brand text-2xl font-bold text-primary-foreground shadow-elegant">
          {initials}
        </span>
        <div className="flex-1">
          <h1 className="font-display text-3xl font-bold tracking-tight">{user?.name ?? "Your profile"}</h1>
          <p className="mt-1 inline-flex items-center gap-1 text-sm text-muted-foreground">
            <Mail className="h-4 w-4" /> {user?.email}
          </p>
        </div>
        <Button variant="outline" onClick={onLogout}>
          <LogOut className="mr-2 h-4 w-4" /> Sign out
        </Button>
      </header>

      {loading ? (
        <div className="mt-8 flex items-center justify-center py-12 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : (
        <div className="mt-8 space-y-6">
          {/* Account */}
          <section className="rounded-xl border border-border bg-card p-6 shadow-card">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-primary" />
              <h2 className="font-display text-lg font-semibold">Account</h2>
            </div>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Full name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input value={user?.email ?? ""} disabled />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="level">Academic level</Label>
                <Select value={level} onValueChange={(v) => setLevel(v as UserLevel)}>
                  <SelectTrigger id="level"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bachelor">Bachelor</SelectItem>
                    <SelectItem value="master">Master</SelectItem>
                    <SelectItem value="phd">PhD</SelectItem>
                    <SelectItem value="professional">Professional / Researcher</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <Button onClick={onSaveAccount} disabled={savingAccount} className="gradient-brand text-primary-foreground hover:opacity-95">
                {savingAccount ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                Save account
              </Button>
            </div>
          </section>

          {/* Skills */}
          <section className="rounded-xl border border-border bg-card p-6 shadow-card">
            <div className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-primary" />
              <h2 className="font-display text-lg font-semibold">Skills</h2>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              The technologies and methods you're proficient with. We use these to score opportunity matches.
            </p>
            <div className="mt-4">
              <TagInput value={skills} onChange={setSkills} ariaLabel="Edit skills" />
            </div>
            <div className="mt-4 flex justify-end">
              <Button onClick={onSaveSkills} disabled={savingSkills} variant="outline">
                {savingSkills ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                Save skills
              </Button>
            </div>
          </section>

          {/* Interests */}
          <section className="rounded-xl border border-border bg-card p-6 shadow-card">
            <div className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-accent" />
              <h2 className="font-display text-lg font-semibold">Research interests</h2>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Topics you'd like to explore — used to surface relevant opportunities and clusters.
            </p>
            <div className="mt-4">
              <TagInput value={interests} onChange={setInterests} ariaLabel="Edit interests" />
            </div>
            <div className="mt-4 flex justify-end">
              <Button onClick={onSaveInterests} disabled={savingInterests} variant="outline">
                {savingInterests ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                Save interests
              </Button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
