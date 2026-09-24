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

      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-border pb-2">
          <h2 className="text-xl font-bold tracking-tight">Active Modules</h2>
          <span className="text-xs text-muted-foreground">{subjects.length} Subjects Available</span>
        </div>

        <div className="grid gap-3">
          {subjects.map((sub) => {
            const Icon = sub.icon;

            return (
              <Card key={sub.id} className="border-border hover:border-indigo-500/30 transition-all duration-200 bg-card/40">
                <CardHeader className="p-4 flex flex-row items-center justify-between gap-4 space-y-0">
                  <div className="flex gap-3.5 items-center min-w-0">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-foreground text-base leading-none">
                          {sub.title}
                        </h3>
                        <Badge variant="outline" className="font-mono text-[10px] px-1.5 py-0">
                          {sub.code}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-1">
                        {sub.description}
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" asChild className="shrink-0 text-xs font-semibold text-primary hover:text-primary/95">
                    <Link href={`/dashboard/subjects/${sub.id}`}>
                      Open Workspace <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </div>

    </div>
  );
}
