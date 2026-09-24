"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Cpu,
  GraduationCap,
  LayoutDashboard,
  LineChart,
  LogOut,
  FolderCheck,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useAuth } from "@/context/auth-context";

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  role?: "faculty" | "admin";
}

const mainNav: NavItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Faculty Review", href: "/dashboard/review", icon: FolderCheck, role: "faculty" },
];


const subjectNav: NavItem[] = [
  { title: "Power System", href: "/dashboard/subjects/power-system", icon: Zap },
  { title: "Power Electronics", href: "/dashboard/subjects/power-electronics", icon: Cpu },
  { title: "Machine System", href: "/dashboard/subjects/machine-system", icon: GraduationCap },
  { title: "Network System", href: "/dashboard/subjects/network-system", icon: BookOpen },
  { title: "Control System", href: "/dashboard/subjects/control-system", icon: LineChart },
];

export function DashboardSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          "relative flex flex-col border-r border-border bg-card transition-all duration-300 ease-in-out h-screen sticky top-0",
          collapsed ? "w-16" : "w-64"
        )}
      >
        {/* Logo Header */}
        <div className="flex h-16 items-center justify-between border-b border-border px-4">
          <Link href="/dashboard" className="flex items-center space-x-3 overflow-hidden">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-600 text-white shadow-md">
              <Zap className="h-5 w-5" />
            </div>
            {!collapsed && (
              <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-foreground to-indigo-400 bg-clip-text text-transparent truncate">
                CircuitGPT
              </span>
            )}
          </Link>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {/* Main Navigation */}
          <div className="space-y-1">
            {!collapsed && (
              <p className="px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Overview
              </p>
            )}
            {mainNav.map((item) => {
              if (item.role && user?.role !== item.role && user?.role !== "admin") {
                return null;
              }
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return collapsed ? (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex h-9 w-9 items-center justify-center rounded-lg transition-colors mx-auto",
                        isActive
                          ? "bg-primary text-primary-foreground font-medium shadow"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      )}
                    >
                      <Icon className="h-5 w-5" />
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">{item.title}</TooltipContent>
                </Tooltip>
              ) : (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground shadow"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.title}</span>
                </Link>
              );
            })}
          </div>

          {/* Subjects Navigation */}
          <div className="space-y-1">
            {!collapsed && (
              <p className="px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Active Modules
              </p>
            )}
            {subjectNav.map((item) => {
              const isActive = pathname.startsWith(item.href);
              const Icon = item.icon;

              return collapsed ? (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex h-9 w-9 items-center justify-center rounded-lg transition-colors mx-auto",
                        isActive
                          ? "bg-primary/20 text-primary border border-primary/30"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      )}
                    >
                      <Icon className="h-5 w-5" />
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">{item.title}</TooltipContent>
                </Tooltip>
              ) : (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/15 text-primary border border-primary/25 font-semibold"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="truncate">{item.title}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* User Footer Profile */}
        <div className="border-t border-border p-3">
          {collapsed ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={logout}
                  className="h-9 w-9 text-muted-foreground hover:text-destructive mx-auto flex"
                >
                  <LogOut className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">Sign out</TooltipContent>
            </Tooltip>
          ) : (
            <div className="flex items-center justify-between rounded-lg bg-accent/40 p-2">
              <div className="flex items-center space-x-3 overflow-hidden">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground uppercase">
                  {user?.full_name?.charAt(0) || "U"}
                </div>
                <div className="truncate">
                  <p className="text-xs font-semibold leading-none truncate">{user?.full_name || "Student User"}</p>
                  <p className="text-[10px] text-muted-foreground capitalize mt-0.5">{user?.role || "student"}</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={logout} className="h-7 w-7 text-muted-foreground hover:text-destructive">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </aside>
    </TooltipProvider>
  );
}
