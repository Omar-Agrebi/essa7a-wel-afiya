import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Sparkles,
  Search,
  Target,
  Bell,
  Briefcase,
  GraduationCap,
  FlaskConical,
  BookOpen,
  Microscope,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { OpportunityCard } from "@/components/OpportunityCard";
import { CardSkeleton, EmptyState, ErrorState } from "@/components/States";
import { fetchOpportunities } from "@/lib/services";
import { getApiErrorMessage } from "@/lib/api";
import type { Opportunity, OpportunityType } from "@/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Intelligent University Observatory — Discover academic opportunities" },
      {
        name: "description",
        content:
          "AI-powered discovery of internships, scholarships, research projects, courses, and postdoc positions for students and researchers.",
      },
    ],
  }),
  component: HomePage,
});

const TYPE_META: { type: OpportunityType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { type: "internship", label: "Internships", icon: Briefcase },
  { type: "scholarship", label: "Scholarships", icon: GraduationCap },
  { type: "project", label: "Research", icon: FlaskConical },
  { type: "course", label: "Courses", icon: BookOpen },
  { type: "postdoc", label: "Postdocs", icon: Microscope },
];

function HomePage() {
  const [recent, setRecent] = useState<Opportunity[]>([]);
  const [counts, setCounts] = useState<Record<OpportunityType, number>>({
    internship: 0,
    scholarship: 0,
    project: 0,
    course: 0,
    postdoc: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [recentData, ...countsData] = await Promise.all([
        fetchOpportunities({ limit: 6 }),
        ...TYPE_META.map((m) => fetchOpportunities({ type: m.type, limit: 100 })),
      ]);
      setRecent(recentData);
      const next: Record<OpportunityType, number> = {
        internship: 0,
        scholarship: 0,
        project: 0,
        course: 0,
        postdoc: 0,
      };
      TYPE_META.forEach((m, i) => {
        next[m.type] = countsData[i].length;
      });
      setCounts(next);
    } catch (e) {
      setError(getApiErrorMessage(e, "Could not load opportunities."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 -z-10 gradient-brand-soft" />
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_color-mix(in_oklab,_var(--color-primary)_15%,_transparent),_transparent_60%)]" />
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8 lg:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-card/80 px-3 py-1 text-xs font-medium text-primary backdrop-blur">
              <Sparkles className="h-3.5 w-3.5" />
              AI-curated for your academic journey
            </span>
            <h1 className="mt-6 font-display text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Every opportunity that matches{" "}
              <span className="text-gradient-brand">your potential</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-base text-muted-foreground sm:text-lg">
              Internships, scholarships, research projects, certifications and postdoc positions —
              continuously discovered, clustered and ranked for students and researchers.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button asChild size="lg" className="gradient-brand text-primary-foreground shadow-elegant hover:opacity-95">
                <Link to="/opportunities">
                  Browse opportunities
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link to="/dashboard">Get recommendations</Link>
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="mx-auto mt-16 grid max-w-4xl grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {TYPE_META.map((m) => (
              <div
                key={m.type}
                className="rounded-xl border border-border bg-card/80 p-4 text-center shadow-card backdrop-blur"
              >
                <m.icon className="mx-auto h-5 w-5 text-primary" />
                <p className="mt-2 font-display text-2xl font-bold tabular-nums">
                  {loading ? "—" : counts[m.type]}
                </p>
                <p className="text-xs text-muted-foreground">{m.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Recent grid */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="font-display text-2xl font-bold sm:text-3xl">Latest opportunities</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Freshly discovered by our pipeline across trusted academic sources.
            </p>
          </div>
          <Button asChild variant="ghost" className="hidden sm:inline-flex">
            <Link to="/opportunities">
              View all <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
        </div>

        <div className="mt-8">
          {loading ? (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : error ? (
            <ErrorState message={error} onRetry={load} />
          ) : recent.length === 0 ? (
            <EmptyState
              icon={Search}
              title="No opportunities yet"
              message="Once your data pipeline runs, the latest openings will appear here."
              action={
                <Button asChild>
                  <Link to="/opportunities">Explore catalogue</Link>
                </Button>
              }
            />
          ) : (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {recent.map((o) => (
                <OpportunityCard key={o.id} opportunity={o} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-2xl font-bold sm:text-3xl">How it works</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Three steps from sign-up to a personalised feed of opportunities.
          </p>
        </div>
        <div className="mx-auto mt-12 grid max-w-5xl gap-6 md:grid-cols-3">
          {[
            {
              icon: GraduationCap,
              title: "Build your academic profile",
              text: "Tell us your level, skills and research interests. We use them to score every opportunity.",
            },
            {
              icon: Target,
              title: "Get matched, not flooded",
              text: "Our recommender ranks openings by relevance, deadline urgency and skill overlap.",
            },
            {
              icon: Bell,
              title: "Never miss a deadline",
              text: "Notifications keep you in sync with new matches and expiring opportunities.",
            },
          ].map((step, i) => (
            <div key={step.title} className="relative rounded-2xl border border-border bg-card p-6 shadow-card">
              <span className="absolute -top-3 left-6 rounded-full gradient-brand px-2.5 py-0.5 text-xs font-semibold text-primary-foreground">
                Step {i + 1}
              </span>
              <step.icon className="h-7 w-7 text-primary" />
              <h3 className="mt-4 text-lg font-semibold">{step.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{step.text}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
