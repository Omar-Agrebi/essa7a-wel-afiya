import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  CalendarClock,
  ExternalLink,
  Layers,
  MapPin,
  Share2,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/States";
import {
  formatDeadline,
  getCategoryLabel,
  getDaysUntil,
  getTypeBadgeClasses,
  getTypeLabel,
} from "@/lib/opportunity-utils";
import { fetchOpportunity } from "@/lib/services";
import { getApiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Opportunity } from "@/types";

export const Route = createFileRoute("/opportunities/$id")({
  head: () => ({
    meta: [
      { title: "Opportunity — Intelligent University Observatory" },
      { name: "description", content: "Detailed view of an academic opportunity." },
    ],
  }),
  component: OpportunityDetailPage,
});

function OpportunityDetailPage() {
  const { id } = Route.useParams();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchOpportunity(id);
      setOpportunity(data);
    } catch (e) {
      setError(getApiErrorMessage(e, "Could not load this opportunity."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const share = async () => {
    const url = typeof window !== "undefined" ? window.location.href : "";
    try {
      if (navigator.share && opportunity) {
        await navigator.share({ title: opportunity.title, url });
      } else {
        await navigator.clipboard.writeText(url);
        toast.success("Link copied to clipboard");
      }
    } catch {
      /* user canceled */
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="h-6 w-32 animate-pulse rounded bg-muted" />
        <div className="mt-6 h-10 w-3/4 animate-pulse rounded bg-muted" />
        <div className="mt-8 grid gap-8 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <div className="h-32 animate-pulse rounded-xl bg-card" />
            <div className="h-64 animate-pulse rounded-xl bg-card" />
          </div>
          <div className="h-72 animate-pulse rounded-xl bg-card" />
        </div>
      </div>
    );
  }

  if (error || !opportunity) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
        <ErrorState message={error ?? "Opportunity not found."} onRetry={load} />
      </div>
    );
  }

  const days = getDaysUntil(opportunity.deadline);
  const urgent = days >= 0 && days <= 7;
  const expired = days < 0;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <Button variant="ghost" size="sm" asChild className="mb-4">
        <Link to="/opportunities">
          <ArrowLeft className="mr-1 h-4 w-4" /> All opportunities
        </Link>
      </Button>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge className={cn("border-0", getTypeBadgeClasses(opportunity.type))}>
              {getTypeLabel(opportunity.type)}
            </Badge>
            <Badge variant="outline">{getCategoryLabel(opportunity.category)}</Badge>
            {opportunity.cluster_label && (
              <Badge variant="outline" className="gap-1">
                <Layers className="h-3 w-3" /> {opportunity.cluster_label}
              </Badge>
            )}
          </div>

          <h1 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">
            {opportunity.title}
          </h1>

          <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <MapPin className="h-4 w-4" />
              {opportunity.location || "Remote / N/A"}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Users className="h-4 w-4" />
              Source: {opportunity.source}
            </span>
          </div>

          <section className="mt-8 rounded-xl border border-border bg-card p-6 shadow-card">
            <h2 className="text-lg font-semibold">About this opportunity</h2>
            <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-foreground/80">
              {opportunity.description}
            </p>
          </section>

          {opportunity.skills_required.length > 0 && (
            <section className="mt-6 rounded-xl border border-border bg-card p-6 shadow-card">
              <h2 className="text-lg font-semibold">Skills required</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {opportunity.skills_required.map((s) => (
                  <span
                    key={s}
                    className="rounded-md bg-secondary px-2.5 py-1 text-sm text-secondary-foreground"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </section>
          )}

          {opportunity.eligibility && (
            <section className="mt-6 rounded-xl border border-border bg-card p-6 shadow-card">
              <h2 className="text-lg font-semibold">Eligibility</h2>
              <p className="mt-3 text-sm text-foreground/80">{opportunity.eligibility}</p>
            </section>
          )}
        </div>

        <aside className="space-y-4">
          <div
            className={cn(
              "rounded-xl border p-5 shadow-card",
              urgent && !expired
                ? "border-destructive/30 bg-destructive/5"
                : "border-border bg-card",
            )}
          >
            <div className="flex items-center gap-2 text-sm font-medium">
              <CalendarClock className={cn("h-4 w-4", urgent && !expired && "text-destructive")} />
              Application deadline
            </div>
            <p className="mt-2 font-display text-2xl font-bold">{formatDeadline(opportunity.deadline)}</p>
            <p
              className={cn(
                "mt-1 text-sm",
                expired
                  ? "text-muted-foreground"
                  : urgent
                    ? "font-medium text-destructive"
                    : "text-muted-foreground",
              )}
            >
              {expired
                ? "This opportunity has closed."
                : days === 0
                  ? "Closes today"
                  : `${days} day${days === 1 ? "" : "s"} remaining`}
            </p>
            {urgent && !expired && (
              <div className="mt-3 flex items-start gap-2 rounded-md bg-destructive/10 p-2 text-xs text-destructive">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                <span>Urgent — apply soon to secure your application.</span>
              </div>
            )}
          </div>

          <div className="space-y-2 rounded-xl border border-border bg-card p-5 shadow-card">
            <p className="text-sm font-medium">Take action</p>
            {opportunity.url && (
              <Button asChild className="w-full gradient-brand text-primary-foreground hover:opacity-95">
                <a href={opportunity.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Visit source
                </a>
              </Button>
            )}
            <Button variant="outline" className="w-full" onClick={share}>
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
          </div>
        </aside>
      </div>
    </div>
  );
}
