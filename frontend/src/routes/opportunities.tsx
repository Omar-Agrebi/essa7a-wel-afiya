import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { OpportunityFilters } from "@/components/OpportunityFilters";
import { OpportunityCard } from "@/components/OpportunityCard";
import { CardSkeleton, EmptyState, ErrorState } from "@/components/States";
import { fetchOpportunities } from "@/lib/services";
import { getApiErrorMessage } from "@/lib/api";
import type { Opportunity, OpportunityFilterParams } from "@/types";

export const Route = createFileRoute("/opportunities")({
  head: () => ({
    meta: [
      { title: "Opportunities — Intelligent University Observatory" },
      {
        name: "description",
        content:
          "Browse internships, scholarships, research projects, courses and postdoc positions. Filter by type, category and deadline.",
      },
    ],
  }),
  component: OpportunitiesPage,
});

const PAGE_SIZE = 12;

function OpportunitiesPage() {
  const [filters, setFilters] = useState<OpportunityFilterParams>({ skip: 0, limit: PAGE_SIZE });
  const [items, setItems] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const page = useMemo(() => Math.floor((filters.skip ?? 0) / PAGE_SIZE) + 1, [filters.skip]);

  const load = async (next: OpportunityFilterParams) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchOpportunities(next);
      setItems(data);
    } catch (e) {
      setError(getApiErrorMessage(e, "Could not load opportunities."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(filters);
  }, [filters]);

  const hasNext = items.length === PAGE_SIZE;
  const hasPrev = (filters.skip ?? 0) > 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <header className="mb-6">
        <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
          Opportunities
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Search and filter the live catalogue of academic opportunities.
        </p>
      </header>

      <OpportunityFilters
        value={filters}
        onChange={(next) => setFilters({ ...next, limit: PAGE_SIZE })}
      />

      <div className="mt-6 flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {loading
            ? "Loading…"
            : `${items.length} result${items.length === 1 ? "" : "s"} on page ${page}`}
        </span>
        <span>Sorted by deadline</span>
      </div>

      <div className="mt-4">
        {loading ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : error ? (
          <ErrorState message={error} onRetry={() => load(filters)} />
        ) : items.length === 0 ? (
          <EmptyState
            icon={Search}
            title="No opportunities match your filters"
            message="Try removing a filter or broadening your keyword."
            action={
              <Button onClick={() => setFilters({ skip: 0, limit: PAGE_SIZE })}>
                Reset filters
              </Button>
            }
          />
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((o) => (
              <OpportunityCard key={o.id} opportunity={o} />
            ))}
          </div>
        )}
      </div>

      {!loading && !error && items.length > 0 && (
        <div className="mt-10 flex items-center justify-between">
          <Button
            variant="outline"
            disabled={!hasPrev}
            onClick={() =>
              setFilters((f) => ({ ...f, skip: Math.max(0, (f.skip ?? 0) - PAGE_SIZE) }))
            }
            aria-label="Previous page"
          >
            <ChevronLeft className="mr-1 h-4 w-4" /> Previous
          </Button>
          <span className="text-sm text-muted-foreground">Page {page}</span>
          <Button
            variant="outline"
            disabled={!hasNext}
            onClick={() => setFilters((f) => ({ ...f, skip: (f.skip ?? 0) + PAGE_SIZE }))}
            aria-label="Next page"
          >
            Next <ChevronRight className="ml-1 h-4 w-4" />
          </Button>
        </div>
      )}

      <div className="mt-12 rounded-xl border border-dashed border-border bg-card/50 p-6 text-center text-sm text-muted-foreground">
        Looking for personalised matches?{" "}
        <Link to="/dashboard" className="font-medium text-primary hover:underline">
          Open your dashboard
        </Link>
        .
      </div>
    </div>
  );
}
