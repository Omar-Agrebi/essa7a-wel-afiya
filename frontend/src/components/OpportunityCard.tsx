import { Link } from "@tanstack/react-router";
import { CalendarClock, MapPin, AlertTriangle, ChevronDown, ChevronUp, Sparkles, Zap, GraduationCap, Clock, Target } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  formatDeadline,
  getDaysUntil,
  getScoreColor,
  getTypeBadgeClasses,
  getTypeLabel,
} from "@/lib/opportunity-utils";
import type { Opportunity } from "@/types";

interface OpportunityCardProps {
  opportunity: Opportunity;
  matchScore?: number;
  matchReasons?: string[];
}

function reasonIcon(reason: string) {
  const r = reason.toLowerCase();
  if (r.includes("skill")) return <Zap className="h-3.5 w-3.5 text-primary" />;
  if (r.includes("level") || r.includes("degree")) return <GraduationCap className="h-3.5 w-3.5 text-primary" />;
  if (r.includes("deadline") || r.includes("time")) return <Clock className="h-3.5 w-3.5 text-primary" />;
  if (r.includes("interest") || r.includes("topic")) return <Target className="h-3.5 w-3.5 text-primary" />;
  return <Sparkles className="h-3.5 w-3.5 text-primary" />;
}

export function OpportunityCard({ opportunity, matchScore, matchReasons }: OpportunityCardProps) {
  const [expanded, setExpanded] = useState(false);
  const days = getDaysUntil(opportunity.deadline);
  const urgent = days >= 0 && days <= 7;
  const expired = days < 0;
  const visibleSkills = opportunity.skills_required.slice(0, 3);
  const overflow = opportunity.skills_required.length - visibleSkills.length;
  const score = matchScore !== undefined ? Math.max(0, Math.min(1, matchScore)) : undefined;
  const scoreColor = score !== undefined ? getScoreColor(score) : null;

  return (
    <article className="group flex h-full flex-col rounded-xl border border-border bg-card text-card-foreground shadow-card transition hover:shadow-elegant hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-3 p-5 pb-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge className={cn("font-medium border-0", getTypeBadgeClasses(opportunity.type))}>
            {getTypeLabel(opportunity.type)}
          </Badge>
          <Badge variant="outline" className="font-normal">
            {opportunity.category.replace(/_/g, " ")}
          </Badge>
        </div>
        {urgent && !expired && (
          <span className="inline-flex items-center gap-1 rounded-md bg-destructive/10 px-2 py-1 text-xs font-medium text-destructive">
            <AlertTriangle className="h-3 w-3" />
            {days === 0 ? "Today" : `${days}d left`}
          </span>
        )}
      </div>

      <div className="px-5 pb-3">
        <Link
          to="/opportunities/$id"
          params={{ id: opportunity.id }}
          className="block"
        >
          <h3 className="text-lg font-semibold leading-snug text-foreground line-clamp-2 group-hover:text-primary transition">
            {opportunity.title}
          </h3>
        </Link>
        <p className="mt-2 text-sm text-muted-foreground line-clamp-2">{opportunity.description}</p>
      </div>

      <div className="mt-auto space-y-3 px-5 pb-5">
        <div className="flex flex-wrap gap-1.5">
          {visibleSkills.map((s) => (
            <span key={s} className="rounded-md bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
              {s}
            </span>
          ))}
          {overflow > 0 && (
            <span className="rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">+{overflow}</span>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <MapPin className="h-3.5 w-3.5" />
            {opportunity.location || "Remote / N/A"}
          </span>
          <span
            className={cn(
              "inline-flex items-center gap-1",
              urgent && !expired && "text-destructive font-medium",
              expired && "text-muted-foreground line-through",
            )}
          >
            <CalendarClock className="h-3.5 w-3.5" />
            {formatDeadline(opportunity.deadline)}
          </span>
        </div>

        {score !== undefined && (
          <div className="space-y-2 rounded-lg bg-secondary/40 p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-foreground">Match score</span>
              <span className={cn("text-xs font-semibold", scoreColor?.text)}>{Math.round(score * 100)}%</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
              <div
                className={cn("h-full rounded-full transition-all", scoreColor?.bar)}
                style={{ width: `${Math.round(score * 100)}%` }}
              />
            </div>
            {matchReasons && matchReasons.length > 0 && (
              <>
                <button
                  type="button"
                  onClick={() => setExpanded((v) => !v)}
                  aria-label="Toggle match reasons"
                  className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                >
                  {expanded ? "Hide reasons" : `${matchReasons.length} match reason${matchReasons.length === 1 ? "" : "s"}`}
                  {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </button>
                {expanded && (
                  <ul className="space-y-1 pt-1">
                    {matchReasons.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-foreground/80">
                        {reasonIcon(r)}
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </article>
  );
}
