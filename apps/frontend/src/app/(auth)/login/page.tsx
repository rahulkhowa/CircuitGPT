"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/context/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
      const res = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        if (res.status === 401) {
          throw new Error("Invalid email or password.");
        }
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Login failed");
      }

      const tokenData = await res.json();
      
      // Fetch current user details
      const userRes = await fetch(`${apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      });
      
      if (!userRes.ok) {
        throw new Error("Failed to fetch user profile after successful authentication.");
      }

      const userData = await userRes.json();

      login(tokenData.access_token, tokenData.refresh_token, userData);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError((err as Error).message || "Failed to log in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-border/40 shadow-xl backdrop-blur-sm bg-card/95">
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-2xl font-bold tracking-tight">Welcome back</CardTitle>
        <CardDescription>
          Enter your credentials to access your CircuitGPT workspace
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {error && (
            <div className="rounded-md bg-destructive/15 p-3 text-xs text-destructive">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="email">Username (Email)</Label>
            <Input
              id="email"
              type="email"
              placeholder="student@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
              <Link href="#" className="text-xs text-primary hover:underline">
                Forgot password?
              </Link>
            </div>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <Button variant="gradient" className="w-full" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </Button>
          <p className="text-center text-xs text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="font-semibold text-primary hover:underline">
              Create account
            </Link>
          </p>
        </CardFooter>
      </form>
    </Card>
  );
}
