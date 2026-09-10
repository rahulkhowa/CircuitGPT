"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAuth } from "@/context/auth-context";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate inputs client-side
    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
      
      // Derive full name from email username
      const usernamePart = email.split("@")[0] || "User";
      const derivedFullName = usernamePart.length >= 2 ? usernamePart : usernamePart + "_user";
      
      const res = await fetch(`${apiBase}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: derivedFullName,
          email,
          password,
          role: "student",
        }),
      });

      if (!res.ok) {
        if (res.status === 409) {
          throw new Error("An account with this email already exists.");
        }
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Registration failed");
      }

      // Auto-login after registration
      const loginRes = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!loginRes.ok) {
        throw new Error("Registration succeeded, but auto-login failed. Please sign in manually.");
      }

      const tokenData = await loginRes.json();
      
      // Get the profile
      const userRes = await fetch(`${apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      });
      
      if (!userRes.ok) {
        throw new Error("Failed to retrieve user profile after auto-login.");
      }
      
      const userData = await userRes.json();

      login(tokenData.access_token, tokenData.refresh_token, userData);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError((err as Error).message || "Failed to register account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-border/40 shadow-xl backdrop-blur-sm bg-card/95">
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-2xl font-bold tracking-tight">Create your account</CardTitle>
        <CardDescription>
          Get started with AI-driven Electrical Engineering learning
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
              placeholder="tesla@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm_password">Confirm Password</Label>
            <Input
              id="confirm_password"
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <Button variant="gradient" className="w-full" type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Create Account"}
          </Button>
          <p className="text-center text-xs text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </CardFooter>
      </form>
    </Card>
  );
}
