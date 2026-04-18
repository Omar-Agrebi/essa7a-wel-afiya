import { useEffect, useState } from "react";
import { Search, X, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import type { OpportunityCategory, OpportunityFilterParams, OpportunityType } from "@/types";

interface OpportunityFiltersProps {
  value: OpportunityFilterParams;
  onChange: (next: OpportunityFilterParams) => void;
}

const TYPES: OpportunityType[] = ["internship", "scholarship", "project", "course", "postdoc"];
const CATEGORIES: OpportunityCategory[] = [
  "AI",
  "Data_Science",
  "Cybersecurity",
  "Software_Engineering",
  "Other",
];

export function OpportunityFilters({ value, onChange }: OpportunityFiltersProps) {
  const [keyword, setKeyword] = useState(value.keyword ?? "");

  useEffect(() => {
    const t = setTimeout(() => {
      if ((value.keyword ?? "") !== keyword) {
        onChange({ ...value, keyword: keyword || undefined, skip: 0 });
      }
    }, 300);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keyword]);

  const activeCount =
    (value.keyword ? 1 : 0) +
    (value.type ? 1 : 0) +
    (value.category ? 1 : 0) +
    (value.expiring_in_days ? 1 : 0);

  const clearAll = () => {
    setKeyword("");
    onChange({ skip: 0, limit: value.limit });
  };

  return (
    <div className="rounded-xl border border-border bg-card p-4 shadow-card">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-[220px] flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Search opportunities, skills, keywords…"
            aria-label="Search keyword"
            className="pl-9"
          />
        </div>

        <Select
          value={value.type ?? "all"}
          onValueChange={(v) =>
            onChange({ ...value, type: v === "all" ? undefined : (v as OpportunityType), skip: 0 })
          }
        >
          <SelectTrigger className="w-[170px]" aria-label="Filter by type">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            {TYPES.map((t) => (
              <SelectItem key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={value.category ?? "all"}
          onValueChange={(v) =>
            onChange({
              ...value,
              category: v === "all" ? undefined : (v as OpportunityCategory),
              skip: 0,
            })
          }
        >
          <SelectTrigger className="w-[200px]" aria-label="Filter by category">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {CATEGORIES.map((c) => (
              <SelectItem key={c} value={c}>
                {c.replace(/_/g, " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2 rounded-md border border-input bg-background px-3 py-2">
          <Switch
            id="expiring"
            checked={Boolean(value.expiring_in_days)}
            onCheckedChange={(checked) =>
              onChange({ ...value, expiring_in_days: checked ? 7 : undefined, skip: 0 })
            }
            aria-label="Show only expiring soon"
          />
          <Label htmlFor="expiring" className="text-sm cursor-pointer">
            Expiring in 7d
          </Label>
        </div>

        {activeCount > 0 && (
          <Button variant="ghost" size="sm" onClick={clearAll} className="ml-auto">
            <X className="mr-1 h-4 w-4" />
            Clear all
            <span className="ml-2 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1.5 text-xs font-medium text-primary-foreground">
              {activeCount}
            </span>
          </Button>
        )}
        {activeCount === 0 && (
          <span className="ml-auto inline-flex items-center gap-1 text-xs text-muted-foreground">
            <Filter className="h-3.5 w-3.5" />
            No filters
          </span>
        )}
      </div>
    </div>
  );
}
