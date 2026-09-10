"use client";

import React, { useMemo, useState } from "react";
import { ClipboardList, Filter } from "lucide-react";
import {
  NoteEvaluationCard,
  NoteEvaluationItem,
} from "@/components/note-evaluation-card";
import { ProtectedRoute } from "@/components/protected-route";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const MOCK_QUEUE: NoteEvaluationItem[] = [
  {
    id: "ev-1",
    studentName: "Priya Sharma",
    studentEmail: "priya.sharma@university.edu",
    courseCode: "EE101",
    noteTitle: "KCL Node Analysis — Week 3 Summary",
    submittedAt: "2 hours ago",
    status: "pending",
    aiScore: 7.5,
    aiFeedback:
      "Strong setup of nodal equations; missing unit consistency on power calculations in section 2. Recommend adding a worked example with numeric values.",
    wordCount: 842,
  },
  {
    id: "ev-2",
    studentName: "James Okonkwo",
    studentEmail: "j.okonkwo@university.edu",
    courseCode: "EE201",
    noteTitle: "K-Map Minimization Practice Notes",
    submittedAt: "Yesterday",
    status: "flagged",
    aiScore: 5.0,
    aiFeedback:
      "Several minimization steps skip intermediate terms. Flagged for faculty review — possible copy-paste from solution sheet without derivation.",
    wordCount: 412,
  },
  {
    id: "ev-3",
    studentName: "Maria Chen",
    studentEmail: "m.chen@university.edu",
    courseCode: "EE301",
    noteTitle: "Fourier Series — Orthogonality & Coefficients",
    submittedAt: "Aug 1",
    status: "reviewed",
    aiScore: 9.0,
    aiFeedback: "Excellent derivation of coefficient formulas with clear diagram references.",
    facultyScore: 9.5,
    facultyFeedback: "Outstanding work — approved for class exemplar.",
    wordCount: 1204,
  },
  {
    id: "ev-4",
    studentName: "Alex Rivera",
    studentEmail: "a.rivera@university.edu",
    courseCode: "EE101",
    noteTitle: "RLC Transient Response Cheatsheet",
    submittedAt: "Jul 30",
    status: "pending",
    aiScore: 8.0,
    aiFeedback: "Good time-constant summary; τ definitions correct. Add initial condition handling for underdamped case.",
    wordCount: 556,
  },
];

function ReviewPageContent() {
  const [courseFilter, setCourseFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filtered = useMemo(() => {
    return MOCK_QUEUE.filter((item) => {
      if (courseFilter !== "all" && item.courseCode !== courseFilter) return false;
      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      return true;
    });
  }, [courseFilter, statusFilter]);

  const pendingCount = MOCK_QUEUE.filter((i) => i.status === "pending").length;

  return (
    <div className="space-y-8 max-w-5xl">
      <div className="space-y-2">
        <Badge variant="outline" className="border-violet-500/30 text-violet-400">
          Faculty Review Panel
        </Badge>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Note evaluations</h1>
        <p className="text-sm text-muted-foreground max-w-xl">
          Review student notebook submissions with AI pre-scores. Submit final grades and feedback.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-muted-foreground">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{pendingCount}</p>
          </CardContent>
        </Card>
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-muted-foreground">In queue</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{MOCK_QUEUE.length}</p>
          </CardContent>
        </Card>
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-muted-foreground flex items-center gap-2">
              <ClipboardList className="h-4 w-4" />
              This week
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">24</p>
            <p className="text-xs text-muted-foreground">Submissions (mock)</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border/60">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Evaluation queue
            </CardTitle>
            <CardDescription>{filtered.length} submission(s) shown</CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Select value={courseFilter} onValueChange={setCourseFilter}>
              <SelectTrigger className="w-[140px] h-9 text-xs">
                <SelectValue placeholder="Course" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All courses</SelectItem>
                <SelectItem value="EE101">EE101</SelectItem>
                <SelectItem value="EE201">EE201</SelectItem>
                <SelectItem value="EE301">EE301</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px] h-9 text-xs">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="flagged">Flagged</SelectItem>
                <SelectItem value="reviewed">Reviewed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {filtered.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">No submissions match filters.</p>
          ) : (
            filtered.map((item) => (
              <NoteEvaluationCard key={item.id} item={item} />
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function FacultyReviewPage() {
  return (
    <ProtectedRoute allowedRoles={["faculty", "admin"]}>
      <ReviewPageContent />
    </ProtectedRoute>
  );
}
