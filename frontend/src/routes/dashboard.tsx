import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Activity,
  Bell,
  CalendarClock,
  ChevronDown,
  ChevronUp,
  Loader2,
  PlayCircle,
  RotateCw,
  Sparkles,
  Target,
  CheckCheck,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { CardSkeleton, EmptyState, ErrorState } from "@/components/States";
import { OpportunityCard } from "@/components/OpportunityCard";
import { RequireAuth } from "@/components/RequireAuth";
import { cn } from "@/lib/utils";
import { formatRelative } from "@/lib/opportunity-utils";
import {
  fetchNotifications,
  fetchPipelineStatus,
  fetchRecommendations,
  markAllNotificationsRead,
  markNotificationRead,
  refreshRecommendations,
  runPipeline,
} from "@/lib/services";
import { getApiErrorMessage } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import type { NotificationItem, PipelineStatus, Recommendation } from "@/types";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — Intelligent University Observatory" },
      { name: "description", content: "Your personalised academic command center." },
    ],
  }),
  component: () => (
    <RequireAuth>
      <DashboardPage />
    </RequireAuth>
  ),
});

function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [recsLoading, setRecsLoading] = useState(true);
  const [recsError, setRecsError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [notifLoading, setNotifLoading] = useState(true);

  const [pipeline, setPipeline] = useState<PipelineStatus | null>(null);
  const [pipelineOpen, setPipelineOpen] = useState(false);
  const [runningPipeline, setRunningPipeline] = useState(false);

  const loadRecs = async () => {
    setRecsLoading(true);
    setRecsError(null);
    try {
      const data = await fetchRecommendations(10);
      setRecs(data);
    } catch (e) {
      setRecsError(getApiErrorMessage(e, "Could not load recommendations."));
    } finally {
      setRecsLoading(false);
    }
  };

  const loadNotifs = async () => {
    setNotifLoading(true);
    try {
      const data = await fetchNotifications();
      setNotifications(data);
    } catch {
      /* silent */
    } finally {
      setNotifLoading(false);
    }
  };

  const loadPipeline = async () => {
    try {
      const data = await fetchPipelineStatus();
      setPipeline(data);
    } catch {
      /* silent */
    }
  };

  useEffect(() => {
    loadRecs();
    loadNotifs();
    loadPipeline();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      const data = await refreshRecommendations();
      setRecs(data);
      toast.success("Recommendations refreshed");
    } catch (e) {
      toast.error(getApiErrorMessage(e, "Could not refresh recommendations."));
    } finally {
      setRefreshing(false);
    }
  };

  const onRunPipeline = async () => {
    setRunningPipeline(true);
    try {
      const data = await runPipeline();
      setPipeline(data);
      toast.success("Pipeline triggered");
    } catch (e) {
      toast.error(getApiErrorMessage(e, "Could not start pipeline."));
    } finally {
      setRunningPipeline(false);
    }
  };

  const onMarkRead = async (id: string) => {
    setNotifications((list) => list.map((n) => (n.id === id ? { ...n, status: "read" } : n)));
    try {
      await markNotificationRead(id);
    } catch {
      toast.error("Could not mark as read");
      loadNotifs();
    }
  };

  const onMarkAll = async () => {
    setNotifications((list) => list.map((n) => ({ ...n, status: "read" as const })));
    try {
      await markAllNotificationsRead();
      toast.success("All notifications marked as read");
    } catch {
      toast.error("Could not update notifications");
      loadNotifs();
    }
  };

  const unreadCount = notifications.filter((n) => n.status === "unread").length;
  const expiringSoon = recs.filter((r) => {
    const d = new Date(r.opportunity.deadline).getTime() - Date.now();
    return d >= 0 && d <= 7 * 86_400_000;
  }).length;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <header className="mb-8">
        <p className="text-sm text-muted-foreground">Welcome back</p>
        <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
          {user?.name?.split(" ")[0] ?? "Researcher"}'s observatory
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Your personalised command center for academic opportunities.
        </p>
      </header>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard icon={Sparkles} label="Recommendations" value={recsLoading ? "—" : String(recs.length)} accent="primary" />
        <StatCard icon={CalendarClock} label="Expiring this week" value={recsLoading ? "—" : String(expiringSoon)} accent={expiringSoon > 0 ? "destructive" : "muted"} />
        <StatCard icon={Bell} label="Unread notifications" value={notifLoading ? "—" : String(unreadCount)} accent={unreadCount > 0 ? "accent" : "muted"} />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        {/* Recommendations */}
        <section className="lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-xl font-semibold">Recommended for you</h2>
            <Button variant="outline" size="sm" onClick={onRefresh} disabled={refreshing}>
              {refreshing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RotateCw className="mr-2 h-4 w-4" />}
              Refresh
            </Button>
          </div>

          {recsLoading ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
            </div>
          ) : recsError ? (
            <ErrorState message={recsError} onRetry={loadRecs} />
          ) : recs.length === 0 ? (
            <EmptyState
              icon={Target}
              title="No recommendations yet"
              message="Refresh to compute matches based on your profile, or update your skills and interests."
              action={
                <div className="flex gap-2">
                  <Button onClick={onRefresh}>Compute matches</Button>
                  <Button variant="outline" asChild><Link to="/profile">Edit profile</Link></Button>
                </div>
              }
            />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {recs.map((r) => (
                <OpportunityCard
                  key={r.opportunity.id}
                  opportunity={r.opportunity}
                  matchScore={r.score}
                  matchReasons={r.match_reasons}
                />
              ))}
            </div>
          )}
        </section>

        {/* Sidebar: notifications + pipeline */}
        <aside className="space-y-6">
          <div className="rounded-xl border border-border bg-card shadow-card">
            <div className="flex items-center justify-between border-b border-border p-4">
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4 text-primary" />
                <h2 className="font-semibold">Notifications</h2>
                {unreadCount > 0 && (
                  <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-destructive px-1.5 text-[10px] font-semibold text-destructive-foreground">
                    {unreadCount}
                  </span>
                )}
              </div>
              {unreadCount > 0 && (
                <Button variant="ghost" size="sm" onClick={onMarkAll} aria-label="Mark all as read">
                  <CheckCheck className="mr-1 h-4 w-4" /> Mark all
                </Button>
              )}
            </div>
            <div className="max-h-[440px] overflow-y-auto">
              {notifLoading ? (
                <div className="flex items-center justify-center p-8 text-muted-foreground">
                  <Loader2 className="h-5 w-5 animate-spin" />
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-8 text-center text-sm text-muted-foreground">
                  You're all caught up.
                </div>
              ) : (
                <ul className="divide-y divide-border">
                  {notifications.map((n) => (
                    <li key={n.id}>
                      <button
                        onClick={() => n.status === "unread" && onMarkRead(n.id)}
                        className={cn(
                          "flex w-full items-start gap-3 p-4 text-left transition hover:bg-secondary/50",
                          n.status === "unread" && "bg-primary/5",
                        )}
                      >
                        <span className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", n.status === "unread" ? "bg-primary" : "bg-muted")} />
                        <div className="min-w-0 flex-1">
                          <p className={cn("text-sm leading-snug", n.status === "unread" ? "font-semibold" : "font-medium text-foreground/80")}>
                            {n.title}
                          </p>
                          <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">{n.message}</p>
                          <p className="mt-1 text-[11px] text-muted-foreground">{formatRelative(n.created_at)}</p>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Pipeline */}
          <div className="rounded-xl border border-border bg-card shadow-card">
            <button
              onClick={() => setPipelineOpen((v) => !v)}
              className="flex w-full items-center justify-between p-4"
              aria-expanded={pipelineOpen}
            >
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-primary" />
                <h2 className="font-semibold">Discovery pipeline</h2>
                {pipeline && (
                  <span
                    className={cn(
                      "inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium",
                      pipeline.status === "running" && "bg-warning/20 text-warning-foreground",
                      pipeline.status === "completed" && "bg-success/20 text-success",
                      pipeline.status === "failed" && "bg-destructive/20 text-destructive",
                      pipeline.status === "idle" && "bg-muted text-muted-foreground",
                    )}
                  >
                    {pipeline.status}
                  </span>
                )}
              </div>
              {pipelineOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            {pipelineOpen && (
              <div className="space-y-3 border-t border-border p-4">
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">Last run</dt>
                    <dd>{pipeline?.last_run ? formatRelative(pipeline.last_run) : "—"}</dd>
                  </div>
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">Last success</dt>
                    <dd>{pipeline?.last_success ? formatRelative(pipeline.last_success) : "—"}</dd>
                  </div>
                  {pipeline?.message && (
                    <div className="rounded-md bg-secondary/50 p-2 text-xs text-muted-foreground">
                      {pipeline.message}
                    </div>
                  )}
                </dl>
                <Button onClick={onRunPipeline} disabled={runningPipeline} className="w-full" variant="outline">
                  {runningPipeline ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <PlayCircle className="mr-2 h-4 w-4" />}
                  Run pipeline
                </Button>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  accent,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  accent: "primary" | "accent" | "destructive" | "muted";
}) {
  const accentClass = {
    primary: "text-primary bg-primary/10",
    accent: "text-accent bg-accent/10",
    destructive: "text-destructive bg-destructive/10",
    muted: "text-muted-foreground bg-muted",
  }[accent];
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-card">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{label}</p>
        <span className={cn("flex h-8 w-8 items-center justify-center rounded-lg", accentClass)}>
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <p className="mt-3 font-display text-3xl font-bold tabular-nums">{value}</p>
    </div>
  );
}
