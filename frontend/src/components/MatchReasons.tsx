import { Zap, GraduationCap, Clock, Target, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { getScoreColor } from "@/lib/opportunity-utils";

interface MatchReasonsProps {
  score: number;
  reasons: string[];
  size?: number;
}

function iconFor(reason: string) {
  const r = reason.toLowerCase();
  if (r.includes("skill")) return Zap;
  if (r.includes("level") || r.includes("degree")) return GraduationCap;
  if (r.includes("deadline") || r.includes("time")) return Clock;
  if (r.includes("interest") || r.includes("topic")) return Target;
  return Sparkles;
}

export function MatchReasons({ score, reasons, size = 72 }: MatchReasonsProps) {
  const pct = Math.round(Math.max(0, Math.min(1, score)) * 100);
  const color = getScoreColor(score);
  const radius = (size - 8) / 2;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (pct / 100) * circ;

  return (
    <div className="flex items-start gap-4">
      <div className="relative shrink-0" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={6}
            className="stroke-muted"
            fill="none"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={6}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            className={cn(
              "transition-[stroke-dashoffset] duration-700",
              pct >= 70 ? "stroke-success" : pct >= 40 ? "stroke-warning" : "stroke-destructive",
            )}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn("text-lg font-bold leading-none", color.text)}>{pct}</span>
          <span className="text-[10px] uppercase tracking-wide text-muted-foreground">match</span>
        </div>
      </div>
      <ul className="flex-1 space-y-1.5">
        {reasons.map((r, i) => {
          const Icon = iconFor(r);
          return (
            <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
              <Icon className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
              <span>{r}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
