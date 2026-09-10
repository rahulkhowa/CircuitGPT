"use client";

import React from "react";
import Link from "next/link";
import {
  BookOpen,
  Cpu,
  GraduationCap,
  Zap,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/context/auth-context";

interface Subject {
  id: string;
  code: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const subjects: Subject[] = [
  {
    id: "power-system",
    code: "EE-PS",
    title: "Power System",
    description: "Grid Stability, Transmission Line Modeling, Load Flow Analysis, Fault Calculation & Protection Relays.",
    icon: Zap,
  },
  {
    id: "power-electronics",
    code: "EE-PE",
    title: "Power Electronics",
    description: "AC-DC Rectifiers, DC-DC Buck/Boost Converters, Inverters, PWM Strategies & Gate Drivers.",
    icon: Cpu,
  },
  {
    id: "machine-system",
    code: "EE-MS",
    title: "Machine System",
    description: "Transformers, Synchronous Generators, DC Motors, 3-Phase Induction Motors & Magnetic Circuits.",
    icon: GraduationCap,
  },
  {
    id: "network-system",
    code: "EE-NS",
    title: "Network System",
    description: "Nodal Analysis, Thévenin & Norton Theorems, Two-Port Networks, RLC Resonant & Transient Response.",
    icon: BookOpen,
  },
  {
    id: "control-system",
    code: "EE-CS",
    title: "Control System",
    description: "Transfer Functions, Block Diagrams, Bode Plots, Nyquist Stability Criterion, PID Controllers & State Space.",
    icon: TrendingUp,
  },
];

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header and Welcome */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-lg text-muted-foreground">
          Welcome back, {user?.full_name || "Student"}! 👋
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Continue Your Learning Section */}
        <div className="md:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-2">
            <h2 className="text-xl font-bold tracking-tight">Continue your learning</h2>
            <span className="text-xs text-muted-foreground">{subjects.length} Courses Available</span>
          </div>

          <div className="space-y-3">
            {subjects.map((sub) => {
              const Icon = sub.icon;

              return (
                <Card key={sub.id} className="border-border hover:border-indigo-500/30 transition-all duration-200 bg-card/40">
                  <CardHeader className="p-4 flex flex-row items-start justify-between gap-4 space-y-0">
                    <div className="flex gap-3 items-start">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-foreground text-base leading-none">
                            {sub.title}
                          </h3>
                          <Badge variant="outline" className="font-mono text-[9px] px-1.5 py-0">
                            {sub.code}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-1">
                          {sub.description}
                        </p>
                        <div className="text-[10px] text-muted-foreground/75 font-mono pt-1">
                          Progress Tracking: <span className="text-amber-500 font-sans font-medium">Feature coming soon</span>
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" asChild className="shrink-0 text-xs font-semibold text-primary hover:text-primary/95">
                      <Link href={`/dashboard/subjects/${sub.id}`}>
                        Continue <ArrowRight className="ml-1 h-3.5 w-3.5" />
                      </Link>
                    </Button>
                  </CardHeader>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Recent Activity Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-2">
            <h2 className="text-xl font-bold tracking-tight">Recent activity</h2>
          </div>

          <Card className="border-border bg-card/25 border-dashed">
            <CardContent className="p-6 text-center space-y-3">
              <p className="text-sm text-muted-foreground font-normal">
                Activity logging is currently not connected to the database.
              </p>
              <Badge variant="secondary" className="text-[10px] font-medium">
                Activity Tracking Coming Soon
              </Badge>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
