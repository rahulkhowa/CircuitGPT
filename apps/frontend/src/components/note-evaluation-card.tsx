"use client";

import React, { useState } from "react";
import {
  Bot,
  CheckCircle2,
  Clock,
  MessageSquare,
  Star,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export type EvaluationStatus = "pending" | "reviewed" | "flagged";

export interface NoteEvaluationItem {
  id: string;
  studentName: string;
  studentEmail: string;
  courseCode: string;
  noteTitle: string;
  submittedAt: string;
  status: EvaluationStatus;
  aiScore?: number;
  aiFeedback?: string;
  facultyScore?: number;
  facultyFeedback?: string;
  wordCount: number;
}

interface NoteEvaluationCardProps {
  item: NoteEvaluationItem;
  onSubmitReview?: (id: string, score: number, feedback: string) => void;
  className?: string;
}

const statusConfig: Record<
  EvaluationStatus,
  { label: string; variant: "default" | "secondary" | "destructive" | "outline" }
> = {
  pending: { label: "Pending Review", variant: "secondary" },
  reviewed: { label: "Reviewed", variant: "default" },
  flagged: { label: "Needs Attention", variant: "destructive" },
};

export function NoteEvaluationCard({ item, onSubmitReview, className }: NoteEvaluationCardProps) {
  const [score, setScore] = useState(item.facultyScore ?? item.aiScore ?? 7);
  const [feedback, setFeedback] = useState(item.facultyFeedback ?? "");
  const [submitted, setSubmitted] = useState(item.status === "reviewed");

  const cfg = statusConfig[item.status];

  const handleSubmit = () => {
    onSubmitReview?.(item.id, score, feedback);
    setSubmitted(true);
  };

  return (
    <Card className={cn("border-border/70 bg-card/80", className)}>
      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="space-y-1 min-w-0">
            <CardTitle className="text-base leading-snug truncate">{item.noteTitle}</CardTitle>
            <CardDescription className="flex flex-wrap items-center gap-2 text-xs">
              <Badge variant="outline" className="font-mono text-[10px]">
                {item.courseCode}
              </Badge>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {item.submittedAt}
              </span>
              <span>{item.wordCount} words</span>
            </CardDescription>
          </div>
          <Badge variant={cfg.variant}>{cfg.label}</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex items-center gap-3 rounded-lg bg-muted/30 p-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/15 text-primary text-xs font-bold uppercase">
            {item.studentName.charAt(0)}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium truncate">{item.studentName}</p>
            <p className="text-xs text-muted-foreground truncate">{item.studentEmail}</p>
          </div>
        </div>

        {item.aiFeedback && (
          <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400">
                <Bot className="h-3.5 w-3.5" />
                AI Pre-Review
              </span>
              {item.aiScore != null && (
                <span className="text-xs font-mono font-bold">{item.aiScore.toFixed(1)} / 10</span>
              )}
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">{item.aiFeedback}</p>
          </div>
        )}

        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-medium flex items-center gap-1">
              <User className="h-3.5 w-3.5" />
              Faculty score
            </span>
            <span className="font-mono font-bold">{score.toFixed(1)} / 10</span>
          </div>
          <Progress value={score * 10} className="h-1.5" />
          <input
            type="range"
            min={0}
            max={10}
            step={0.5}
            value={score}
            onChange={(e) => setScore(parseFloat(e.target.value))}
            disabled={submitted}
            className="w-full accent-primary"
            aria-label="Faculty score"
          />
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            disabled={submitted}
            placeholder="Add feedback for the student..."
            rows={3}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
      </CardContent>

      <CardFooter className="flex justify-between gap-2 border-t border-border/60 pt-4">
        <Button variant="outline" size="sm" className="text-xs gap-1">
          <MessageSquare className="h-3.5 w-3.5" />
          View full note
        </Button>
        {submitted ? (
          <span className="flex items-center gap-1 text-xs text-emerald-500 font-medium">
            <CheckCircle2 className="h-4 w-4" />
            Saved
          </span>
        ) : (
          <Button size="sm" className="text-xs gap-1" onClick={handleSubmit}>
            <Star className="h-3.5 w-3.5" />
            Submit evaluation
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
