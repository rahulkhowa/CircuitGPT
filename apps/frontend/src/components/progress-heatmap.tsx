"use client";

import React, { useMemo } from "react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export interface HeatmapDay {
  date: string;
  minutes: number;
}

interface ProgressHeatmapProps {
  data?: HeatmapDay[];
  weeks?: number;
  className?: string;
}

function hashDate(dateStr: string): number {
  let h = 0;
  for (let i = 0; i < dateStr.length; i++) h = (h * 31 + dateStr.charCodeAt(i)) >>> 0;
  return h;
}

function generateMockHeatmap(weeks: number): HeatmapDay[] {
  const days: HeatmapDay[] = [];
  const today = new Date();
  const totalDays = weeks * 7;

  for (let i = totalDays - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(0, 10);
    const dayOfWeek = d.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const seed = hashDate(dateStr);
    const base = isWeekend ? 0 : seed % 90;
    const spike = seed % 7 === 0 ? 60 + (seed % 90) : 0;
    days.push({ date: dateStr, minutes: Math.min(180, base + spike) });
  }
  return days;
}

function intensityClass(minutes: number): string {
  if (minutes === 0) return "bg-muted/40 border-border/50";
  if (minutes < 30) return "bg-emerald-500/20 border-emerald-500/30";
  if (minutes < 60) return "bg-emerald-500/40 border-emerald-500/40";
  if (minutes < 90) return "bg-emerald-500/60 border-emerald-500/50";
  return "bg-emerald-500 border-emerald-400/80";
}

const WEEKDAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""];

export function ProgressHeatmap({ data, weeks = 26, className }: ProgressHeatmapProps) {
  const days = useMemo(() => data ?? generateMockHeatmap(weeks), [data, weeks]);

  const grid = useMemo(() => {
    const cols: HeatmapDay[][] = [];
    let col: HeatmapDay[] = [];
    const first = new Date(days[0]?.date ?? Date.now());
    const pad = (first.getDay() + 6) % 7;
    for (let i = 0; i < pad; i++) {
      col.push({ date: "", minutes: -1 });
    }
    for (const day of days) {
      col.push(day);
      if (col.length === 7) {
        cols.push(col);
        col = [];
      }
    }
    if (col.length) {
      while (col.length < 7) col.push({ date: "", minutes: -1 });
      cols.push(col);
    }
    return cols;
  }, [days]);

  const totalMinutes = days.reduce((s, d) => s + d.minutes, 0);
  const activeDays = days.filter((d) => d.minutes > 0).length;

  return (
    <TooltipProvider delayDuration={100}>
      <div className={cn("space-y-4", className)}>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-2xl font-bold">{Math.round(totalMinutes / 60)}h</p>
            <p className="text-xs text-muted-foreground">Study time in the last {weeks} weeks</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold">{activeDays} active days</p>
            <p className="text-xs text-muted-foreground">Avg {activeDays ? Math.round(totalMinutes / activeDays) : 0} min/day when active</p>
          </div>
        </div>

        <div className="overflow-x-auto pb-2">
          <div className="inline-flex gap-1 min-w-0">
            <div className="flex flex-col gap-1 pr-1 pt-0.5">
              {WEEKDAY_LABELS.map((label, i) => (
                <span key={i} className="h-3 w-6 text-[9px] text-muted-foreground leading-3">
                  {label}
                </span>
              ))}
            </div>
            {grid.map((week, wi) => (
              <div key={wi} className="flex flex-col gap-1">
                {week.map((cell, di) => {
                  if (cell.minutes < 0 || !cell.date) {
                    return <div key={di} className="h-3 w-3 rounded-sm bg-transparent" />;
                  }
                  return (
                    <Tooltip key={cell.date}>
                      <TooltipTrigger asChild>
                        <div
                          className={cn(
                            "h-3 w-3 rounded-sm border transition-colors cursor-default",
                            intensityClass(cell.minutes)
                          )}
                        />
                      </TooltipTrigger>
                      <TooltipContent side="top" className="text-xs">
                        <p className="font-medium">{cell.date}</p>
                        <p className="text-muted-foreground">
                          {cell.minutes === 0 ? "No study logged" : `${cell.minutes} minutes`}
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
          <span>Less</span>
          <div className="flex gap-0.5">
            {[0, 25, 50, 75, 120].map((m) => (
              <div key={m} className={cn("h-3 w-3 rounded-sm border", intensityClass(m))} />
            ))}
          </div>
          <span>More</span>
        </div>
      </div>
    </TooltipProvider>
  );
}
