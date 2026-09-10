"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { SearchCommand } from "@/components/search-command";

const SYSTEM_NAMES: Record<string, string> = {
  "power-system": "Power System (EE-PS)",
  "power-electronics": "Power Electronics (EE-PE)",
  "machine-system": "Machine System (EE-MS)",
  "network-system": "Network System (EE-NS)",
  "control-system": "Control System (EE-CS)",
};

export function DashboardHeader() {
  const pathname = usePathname();
  const [searchOpen, setSearchOpen] = React.useState(false);

  // Extract current subject id if inside a subject route
  const currentSubjectId = React.useMemo(() => {
    const match = pathname.match(/\/dashboard\/subjects\/([^\/]+)/);
    return match ? match[1] : undefined;
  }, [pathname]);

  const getBreadcrumb = () => {
    if (pathname === "/dashboard") return "Overview";
    if (pathname.includes("/progress")) return "Progress Analytics";
    if (pathname.includes("/review")) return "Faculty Review Panel";
    if (currentSubjectId && SYSTEM_NAMES[currentSubjectId]) {
      return SYSTEM_NAMES[currentSubjectId];
    }
    return "Workspace";
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-card/80 px-6 backdrop-blur-md">
      {/* Breadcrumb Title */}
      <div className="flex items-center space-x-2">
        <span className="text-sm font-medium text-muted-foreground">Dashboard</span>
        <span className="text-sm text-muted-foreground">/</span>
        <span className="text-sm font-semibold text-foreground">{getBreadcrumb()}</span>
      </div>

      {/* Action Controls */}
      <div className="flex items-center space-x-3">
        {/* Search shortcut button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setSearchOpen(true)}
          className="hidden md:flex h-9 w-64 items-center justify-between rounded-lg bg-background px-3 text-xs text-muted-foreground shadow-inner cursor-pointer hover:border-indigo-500/50 hover:bg-accent/50 transition-all"
        >
          <span className="flex items-center gap-2">
            <Search className="h-3.5 w-3.5" />
            Search notes, videos, resources...
          </span>
          <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100">
            Ctrl+K
          </kbd>
        </Button>

        <ThemeToggle />
      </div>

      {/* Command Palette Modal */}
      <SearchCommand
        isOpen={searchOpen}
        onOpenChange={setSearchOpen}
        currentSubjectId={currentSubjectId}
      />
    </header>
  );
}


