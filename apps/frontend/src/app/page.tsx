"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Zap, BookOpen, Cpu, MessageSquare, Folder, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HealthStatus {
  status: string;
  postgres: string;
  redis: string;
}

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
        const res = await fetch(`${apiBase}/health`);
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
        }
      } catch (err) {
        // Backend not yet reachable or offline
        console.warn("Backend health check unreachable:", err);
      }
    };
    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground font-sans antialiased flex flex-col">
      {/* Header / Navbar */}
      <header className="w-full border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Zap className="h-4 w-4" />
            </div>
            <span className="text-lg font-bold tracking-tight text-foreground">
              CircuitGPT
            </span>
          </Link>
          <nav className="flex items-center gap-6">
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Features
            </a>
            <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Login
            </Link>
            <Button size="sm" asChild>
              <Link href="/register">Sign Up</Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-card/30 to-background py-20 md:py-28">
        <div className="container mx-auto max-w-3xl px-6 text-center space-y-8">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-foreground leading-tight">
            AI-powered study workspace <br />
            for Electrical Engineering.
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-xl mx-auto font-normal">
            Understand concepts. Solve problems. Study from your own material.
          </p>
          <div className="flex items-center justify-center gap-4 pt-4">
            <Button size="lg" asChild>
              <Link href="/register">Get Started</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 md:py-28 border-b border-border bg-card/20">
        <div className="container mx-auto max-w-4xl px-6 space-y-12">
          <div className="text-center space-y-3">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight">What you can do</h2>
            <p className="text-muted-foreground text-sm">
              Tools specifically designed for the challenges of electrical engineering coursework.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2">
            {/* Feature 1 */}
            <div className="p-6 rounded-xl border border-border bg-card/50 flex gap-4 items-start">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
                <MessageSquare className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <h3 className="font-semibold text-foreground">AI Study Assistant</h3>
                <p className="text-sm text-muted-foreground">
                  Ask questions and understand complex EE concepts. Get targeted explanations for formulas and nodes.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="p-6 rounded-xl border border-border bg-card/50 flex gap-4 items-start">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
                <Folder className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <h3 className="font-semibold text-foreground">Study Materials</h3>
                <p className="text-sm text-muted-foreground">
                  Learn from notes, PDFs, and lecture slides. Import your resources to customize your learning.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-xl border border-border bg-card/50 flex gap-4 items-start">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
                <Cpu className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <h3 className="font-semibold text-foreground">Circuit & Numerical Tools</h3>
                <p className="text-sm text-muted-foreground">
                  Work through electrical engineering equations and circuit modeling exercises with step-by-step guidance.
                </p>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="p-6 rounded-xl border border-border bg-card/50 flex gap-4 items-start">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
                <BookOpen className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <h3 className="font-semibold text-foreground">Personal Workspace</h3>
                <p className="text-sm text-muted-foreground">
                  Keep your notes, AI conversations, and references structured and organized in one central place.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Built For Section */}
      <section className="py-20 md:py-28 bg-gradient-to-b from-background to-card/10">
        <div className="container mx-auto max-w-xl px-6 text-center space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-foreground">
            Built for Electrical Engineering students.
          </h2>
          <p className="text-sm text-muted-foreground">
            Join other students stabilizing their grades and mastering engineering principles.
          </p>
          <div className="pt-4">
            <Button size="lg" asChild>
              <Link href="/register">Create Account</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-border bg-card/30 py-8 text-center text-xs text-muted-foreground">
        <div className="container mx-auto max-w-5xl px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 CircuitGPT. Built for academic excellence.</p>
          {health?.status === "ok" && (
            <div className="flex items-center gap-1.5 text-emerald-500 font-mono text-[10px]">
              <CheckCircle className="h-3.5 w-3.5" />
              System Status: Connected
            </div>
          )}
        </div>
      </footer>
    </div>
  );
}
