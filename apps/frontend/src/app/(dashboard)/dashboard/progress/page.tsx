"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Flame, Target, Trophy } from "lucide-react";
import { ProgressHeatmap } from "@/components/progress-heatmap";
import { QuizHistoryChart } from "@/components/quiz-history-chart";
import { useAuth } from "@/context/auth-context";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const SUBJECT_PROGRESS = [
  { code: "EE101", title: "Circuit Theory", pct: 75 },
  { code: "EE201", title: "Digital Logic", pct: 60 },
  { code: "EE301", title: "Signals & Systems", pct: 40 },
  { code: "EE401", title: "Electromagnetics", pct: 25 },
];

export default function ProgressPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-8 max-w-6xl">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-2">
          <Badge variant="outline" className="border-emerald-500/30 text-emerald-500">
            Progress Analytics
          </Badge>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
            Learning trajectory
          </h1>
          <p className="text-sm text-muted-foreground max-w-xl">
            Study consistency, quiz performance, and module mastery for{" "}
            {user?.full_name ?? "your account"}.
          </p>
        </div>
        <Button variant="outline" size="sm" asChild>
          <Link href="/dashboard">
            Back to dashboard <ArrowRight className="ml-1 h-3.5 w-3.5" />
          </Link>
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-muted-foreground flex items-center gap-2">
              <Flame className="h-4 w-4 text-orange-400" />
              Current streak
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">12 days</p>
            <p className="text-xs text-muted-foreground mt-1">Keep studying to extend</p>
          </CardContent>
        </Card>
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-muted-foreground flex items-center gap-2">
              <Trophy className="h-4 w-4 text-amber-400" />
              Quiz average
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">88.5%</p>
            <p className="text-xs text-muted-foreground mt-1">Across 18 completed quizzes</p>
          </CardContent>
        </Card>
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-muted-foreground flex items-center gap-2">
              <Target className="h-4 w-4 text-indigo-400" />
              Term goal
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">58%</p>
            <p className="text-xs text-muted-foreground mt-1">Overall mastery target: 70%</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border/60">
          <CardHeader>
            <CardTitle className="text-lg">Study activity</CardTitle>
            <CardDescription>Daily minutes logged across all subjects (mock data)</CardDescription>
          </CardHeader>
          <CardContent>
            <ProgressHeatmap weeks={26} />
          </CardContent>
        </Card>

        <Card className="border-border/60">
          <CardHeader>
            <CardTitle className="text-lg">Quiz history</CardTitle>
            <CardDescription>Recent assessment scores by attempt</CardDescription>
          </CardHeader>
          <CardContent>
            <QuizHistoryChart />
          </CardContent>
        </Card>
      </div>

      <Card className="border-border/60">
        <CardHeader>
          <CardTitle className="text-lg">Module mastery</CardTitle>
          <CardDescription>Completion by enrolled course</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {SUBJECT_PROGRESS.map((sub) => (
            <div key={sub.code} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">
                  <span className="font-mono text-muted-foreground mr-2">{sub.code}</span>
                  {sub.title}
                </span>
                <span className="text-muted-foreground">{sub.pct}%</span>
              </div>
              <Progress value={sub.pct} className="h-2" />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
