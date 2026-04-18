import { useEffect, useState, type KeyboardEvent } from "react";
import { X, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

interface TagInputProps {
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
  maxTags?: number;
  id?: string;
  ariaLabel?: string;
  suggestions?: string[];
}

export function TagInput({
  value,
  onChange,
  placeholder = "Type and press Enter…",
  maxTags = 20,
  id,
  ariaLabel,
  suggestions,
}: TagInputProps) {
  const [draft, setDraft] = useState("");
  const [internalValue, setInternalValue] = useState<string[]>(value);

  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  const addTag = (raw: string) => {
    const tag = raw.trim();
    if (!tag) return;
    if (internalValue.length >= maxTags) return;
    if (internalValue.some((t) => t.toLowerCase() === tag.toLowerCase())) {
      setDraft("");
      return;
    }
    const next = [...internalValue, tag];
    setInternalValue(next);
    onChange(next);
    setDraft("");
  };

  const removeTag = (idx: number) => {
    const next = internalValue.filter((_, i) => i !== idx);
    setInternalValue(next);
    onChange(next);
  };

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(draft);
    } else if (e.key === "Backspace" && !draft && internalValue.length) {
      removeTag(internalValue.length - 1);
    }
  };

  return (
    <div className="space-y-2">
      <div
        className={cn(
          "flex flex-wrap items-center gap-2 rounded-lg border border-input bg-background p-2 min-h-11 focus-within:ring-2 focus-within:ring-ring focus-within:border-ring transition",
        )}
      >
        {internalValue.map((tag, i) => (
          <span
            key={`${tag}-${i}`}
            className="inline-flex items-center gap-1 rounded-md bg-secondary px-2 py-1 text-sm text-secondary-foreground"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(i)}
              aria-label={`Remove ${tag}`}
              className="rounded p-0.5 hover:bg-background/60"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        <input
          id={id}
          aria-label={ariaLabel}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          onBlur={() => draft && addTag(draft)}
          placeholder={internalValue.length === 0 ? placeholder : ""}
          className="flex-1 min-w-[8rem] bg-transparent text-sm outline-none placeholder:text-muted-foreground"
        />
      </div>
      {suggestions && suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {suggestions
            .filter((s) => !internalValue.some((t) => t.toLowerCase() === s.toLowerCase()))
            .slice(0, 8)
            .map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => addTag(s)}
                className="inline-flex items-center gap-1 rounded-full border border-dashed border-border px-2 py-0.5 text-xs text-muted-foreground hover:border-primary hover:text-primary transition"
              >
                <Plus className="h-3 w-3" />
                {s}
              </button>
            ))}
        </div>
      )}
      <p className="text-xs text-muted-foreground">
        {internalValue.length}/{maxTags} • Press Enter or comma to add
      </p>
    </div>
  );
}
