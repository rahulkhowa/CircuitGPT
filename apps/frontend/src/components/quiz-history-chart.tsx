"use client";

import React, { useMemo } from "react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export interface QuizHistoryEntry {
  id: string;
  title: string;
  courseCode: string;
  score: number;
  maxScore: number;
  date: string;
}

interface QuizHistoryChartProps {
  entries?: QuizHistoryEntry[];
  className?: string;
}

const MOCK_ENTRIES: QuizHistoryEntry[] = [
  { id: "1", title: "KCL & KVL Fundamentals", courseCode: "EE101", score: 9, maxScore: 10, date: "Aug 1" },
  { id: "2", title: "Thévenin Equivalents", courseCode: "EE101", score: 8, maxScore: 10, date: "Jul 28" },
  { id: "3", title: "Logic Gates & K-Maps", courseCode: "EE201", score: 7, maxScore: 10, date: "Jul 25" },
  { id: "4", title: "RLC Transients", courseCode: "EE101", score: 10, maxScore: 10, date: "Jul 22" },
  { id: "5", title: "Fourier Series Basics", courseCode: "EE301", score: 6, maxScore: 10, date: "Jul 18" },
  { id: "6", title: "AC Phasor Analysis", courseCode: "EE101", score: 8, maxScore: 10, date: "Jul 15" },
  { id: "7", title: "Flip-Flops & Registers", courseCode: "EE201", score: 9, maxScore: 10, date: "Jul 10" },
  { id: "8", title: "Laplace Transform Drill", courseCode: "EE301", score: 7, maxScore: 10, date: "Jul 5" },
];

function scoreColor(pct: number): string {
  if (pct >= 90) return "bg-emerald-500";
  if (pct >= 75) return "bg-indigo-500";
  if (pct >= 60) return "bg-amber-500";
  return "bg-rose-500";
}

export function QuizHistoryChart({ entries, className }: QuizHistoryChartProps) {
  const data = entries ?? MOCK_ENTRIES;
  const chartEntries = useMemo(() => [...data].reverse(), [data]);

  const avgPct = useMemo(() => {
    if (!data.length) return 0;
    const sum = data.reduce((s, e) => s + (e.score / e.maxScore) * 100, 0);
    return Math.round(sum / data.length);
  }, [data]);

  const maxBarHeight = 120;

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-2xl font-bold">{avgPct}%</p>
          <p className="text-xs text-muted-foreground">Average score across {data.length} attempts</p>
        </div>
        <Badge variant="secondary" className="font-mono text-[10px]">
          Last {data.length} quizzes
        </Badge>
      </div>

      <div className="flex items-end justify-between gap-2 h-[140px] px-1 border-b border-border pb-1">
        {chartEntries.map((entry) => {
          const pct = (entry.score / entry.maxScore) * 100;
          const h = Math.max(8, (pct / 100) * maxBarHeight);
          return (
            <div key={entry.id} className="flex flex-1 flex-col items-center gap-1 min-w-0 group">
              <span className="text-[9px] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                {entry.score}/{entry.maxScore}
              </span>
              <div
                className={cn("w-full max-w-[28px] rounded-t-md transition-all", scoreColor(pct))}
                style={{ height: `${h}px` }}
                title={`${entry.title}: ${entry.score}/${entry.maxScore}`}
              />
              <span className="text-[8px] text-muted-foreground truncate w-full text-center">{entry.date}</span>
            </div>
          );
        })}
      </div>

      <ul className="space-y-2 max-h-48 overflow-y-auto pr-1">
        {data.map((entry) => {
          const pct = Math.round((entry.score / entry.maxScore) * 100);
          return (
            <li
              key={entry.id}
              className="flex items-center justify-between gap-2 rounded-lg border border-border/60 bg-muted/20 px-3 py-2 text-xs"
            >
              <div className="min-w-0">
                <p className="font-medium truncate">{entry.title}</p>
                <p className="text-muted-foreground">{entry.courseCode}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="font-mono font-semibold">{pct}%</span>
                <div className={cn("h-2 w-2 rounded-full", scoreColor(pct))} />
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
