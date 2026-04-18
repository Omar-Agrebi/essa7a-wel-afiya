import { differenceInCalendarDays, formatDistanceToNowStrict, parseISO } from "date-fns";
import type { OpportunityType } from "@/types";

export function getTypeLabel(type: OpportunityType): string {
  const map: Record<OpportunityType, string> = {
    internship: "Internship",
    scholarship: "Scholarship",
    project: "Research Project",
    course: "Course",
    postdoc: "Postdoc",
  };
  return map[type];
}

export function getTypeBadgeClasses(type: OpportunityType): string {
  const map: Record<OpportunityType, string> = {
    internship: "bg-type-internship text-type-internship-foreground",
    scholarship: "bg-type-scholarship text-type-scholarship-foreground",
    project: "bg-type-project text-type-project-foreground",
    course: "bg-type-course text-type-course-foreground",
    postdoc: "bg-type-postdoc text-type-postdoc-foreground",
  };
  return map[type];
}

export function getDaysUntil(deadline: string): number {
  try {
    return differenceInCalendarDays(parseISO(deadline), new Date());
  } catch {
    return Number.POSITIVE_INFINITY;
  }
}

export function formatDeadline(deadline: string): string {
  try {
    const d = parseISO(deadline);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  } catch {
    return deadline;
  }
}

export function formatRelative(date: string): string {
  try {
    return `${formatDistanceToNowStrict(parseISO(date))} ago`;
  } catch {
    return date;
  }
}

export function getScoreColor(score: number): { bar: string; text: string } {
  if (score >= 0.7) return { bar: "bg-success", text: "text-success" };
  if (score >= 0.4) return { bar: "bg-warning", text: "text-warning-foreground" };
  return { bar: "bg-destructive", text: "text-destructive" };
}

export function getCategoryLabel(category: string): string {
  return category.replace(/_/g, " ");
}
