"use client";

import React, { useState, useEffect, useMemo, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  FileText,
  Video,
  BookOpen,
  FlaskConical,
  HelpCircle,
  ArrowRight,
  X,
  Clock,
  Sparkles,
  ExternalLink,
  Download,
  SlidersHorizontal,
  Loader2,
  FileUp,
  Layers,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";

export type FilterCategory = "all" | "notes" | "videos" | "lab_manuals" | "books" | "pyqs";

export interface RealUploadResource {
  id: string;
  subject_id: string;
  resource_type: string;
  original_name: string;
  mime_type: string;
  file_size_bytes: number | null;
  status: string;
  created_at?: string;
}

const SYSTEM_MAP: Record<string, string> = {
  "power-system": "Power System (EE-PS)",
  "power-electronics": "Power Electronics (EE-PE)",
  "machine-system": "Machine System (EE-MS)",
  "network-system": "Network System (EE-NS)",
  "control-system": "Control System (EE-CS)",
};

const CATEGORY_ITEMS: { id: FilterCategory; label: string; icon: React.ReactNode }[] = [
  { id: "all", label: "All Results", icon: <SlidersHorizontal className="h-3.5 w-3.5" /> },
  { id: "notes", label: "Notes", icon: <FileText className="h-3.5 w-3.5 text-emerald-500" /> },
  { id: "videos", label: "Videos", icon: <Video className="h-3.5 w-3.5 text-rose-500" /> },
  { id: "lab_manuals", label: "Lab Manuals", icon: <FlaskConical className="h-3.5 w-3.5 text-purple-500" /> },
  { id: "books", label: "Books", icon: <BookOpen className="h-3.5 w-3.5 text-cyan-500" /> },
  { id: "pyqs", label: "PYQs", icon: <HelpCircle className="h-3.5 w-3.5 text-amber-500" /> },
];

function formatBytes(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatRelativeTime(isoString?: string): string {
  if (!isoString) return "";
  const date = new Date(isoString);
  const now = new Date();
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 172800) return "yesterday";
  return date.toLocaleDateString();
}

interface SearchCommandProps {
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  currentSubjectId?: string;
}

export function SearchCommand({
  isOpen: externalIsOpen,
  onOpenChange,
  currentSubjectId,
}: SearchCommandProps) {
  const router = useRouter();
  const { token } = useAuth();
  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const isControlled = externalIsOpen !== undefined;
  const isOpen = isControlled ? externalIsOpen : internalIsOpen;

  const setIsOpen = (open: boolean) => {
    if (!isControlled) {
      setInternalIsOpen(open);
    }
    onOpenChange?.(open);
  };

  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<FilterCategory>("all");
  const [scopeFilter, setScopeFilter] = useState<"current" | "all">(currentSubjectId ? "current" : "all");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [resources, setResources] = useState<RealUploadResource[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";


  // Sync scope when currentSubjectId changes
  useEffect(() => {
    if (currentSubjectId) {
      setScopeFilter("current");
    } else {
      setScopeFilter("all");
    }
  }, [currentSubjectId]);

  // Fetch real uploads from API
  const fetchResources = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      let url = `${API_URL}/uploads`;
      const params = new URLSearchParams();
      if (scopeFilter === "current" && currentSubjectId) {
        params.append("subject_id", currentSubjectId);
      }
      if (activeCategory !== "all") {
        params.append("resource_type", activeCategory);
      }
      const qs = params.toString();
      if (qs) url += `?${qs}`;

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const data = await res.json();
        setResources(Array.isArray(data) ? data : []);
      } else {
        setResources([]);
      }
    } catch {
      setResources([]);
    } finally {
      setIsLoading(false);
    }
  }, [token, API_URL, scopeFilter, currentSubjectId, activeCategory]);

  // Fetch when opened or filters change
  useEffect(() => {
    if (isOpen) {
      fetchResources();
    }
  }, [isOpen, fetchResources]);

  // Global Ctrl+K / Cmd+K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsOpen(!isOpen);
      }
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Filtered results in-memory
  const filteredResults = useMemo(() => {
    return resources.filter((item) => {
      const q = query.toLowerCase().trim();
      const matchesCategory = activeCategory === "all" || item.resource_type === activeCategory;
      if (!matchesCategory) return false;

      if (!q) return true;

      const titleMatch = item.original_name.toLowerCase().includes(q);
      const subjectMatch = item.subject_id.toLowerCase().includes(q) ||
        (SYSTEM_MAP[item.subject_id] || "").toLowerCase().includes(q);
      const typeMatch = item.resource_type.toLowerCase().includes(q);

      return titleMatch || subjectMatch || typeMatch;
    });
  }, [resources, query, activeCategory]);

  // Reset index when query or category changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [query, activeCategory, scopeFilter]);

  // Keyboard navigation within modal
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < filteredResults.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : filteredResults.length - 1));
    } else if (e.key === "Enter" && filteredResults[selectedIndex]) {
      e.preventDefault();
      handleOpenItem(filteredResults[selectedIndex]);
    }
  };

  const handleOpenItem = async (item: RealUploadResource) => {
    if (query.trim() && !recentSearches.includes(query.trim())) {
      setRecentSearches((prev) => [query.trim(), ...prev.slice(0, 4)]);
    }
    setIsOpen(false);
    // Open the resource in viewer or navigate to subject
    try {
      const res = await fetch(`${API_URL}/uploads/${item.id}/view`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.url) {
          window.open(data.url, "_blank");
          return;
        }
      }
    } catch {
      // Fallback to navigate to subject
    }
    router.push(`/dashboard/subjects/${item.subject_id}`);
  };

  const handleDownload = async (e: React.MouseEvent, item: RealUploadResource) => {
    e.stopPropagation();
    try {
      const res = await fetch(`${API_URL}/uploads/${item.id}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.url) {
          const a = document.createElement("a");
          a.href = data.url;
          a.download = item.original_name;
          document.body.appendChild(a);
          a.click();
          a.remove();
        }
      }
    } catch {
      alert("Could not download file.");
    }
  };

  const getItemIcon = (resourceType: string) => {
    switch (resourceType) {
      case "notes":
        return <FileText className="h-4 w-4 text-emerald-500" />;
      case "videos":
        return <Video className="h-4 w-4 text-rose-500" />;
      case "lab_manuals":
        return <FlaskConical className="h-4 w-4 text-purple-500" />;
      case "books":
        return <BookOpen className="h-4 w-4 text-cyan-500" />;
      case "pyqs":
        return <HelpCircle className="h-4 w-4 text-amber-500" />;
      default:
        return <FileText className="h-4 w-4 text-slate-500" />;
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/65 backdrop-blur-sm p-4 pt-16 md:pt-24 animate-in fade-in duration-150"
      onClick={() => setIsOpen(false)}
    >
      <div
        className="relative w-full max-w-2xl overflow-hidden rounded-xl border border-border bg-card shadow-2xl transition-all animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        {/* Header Search Input */}
        <div className="flex items-center border-b border-border px-4 py-3 bg-muted/30">
          <Search className="h-5 w-5 text-muted-foreground mr-3 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            className="w-full bg-transparent text-sm md:text-base font-medium text-foreground placeholder:text-muted-foreground focus:outline-none"
            placeholder={
              currentSubjectId && scopeFilter === "current"
                ? `Search actual uploaded resources in ${SYSTEM_MAP[currentSubjectId] || currentSubjectId}...`
                : "Search actual uploaded notes, videos, lab manuals across all systems..."
            }
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="mr-2 p-1 text-muted-foreground hover:text-foreground rounded-md"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-2 font-mono text-[10px] font-medium text-muted-foreground">
            ESC
          </kbd>
        </div>

        {/* Scope & Category Filter Toolbar */}
        <div className="flex items-center justify-between border-b border-border bg-card px-4 py-2 text-xs">
          {/* Categories */}
          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
            {CATEGORY_ITEMS.map((cat) => {
              const isActive = activeCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-colors shrink-0 ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-sm dark:bg-indigo-500"
                      : "bg-muted/60 text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  {cat.icon}
                  <span>{cat.label}</span>
                </button>
              );
            })}
          </div>

          {/* System Scope Toggle if inside a subject */}
          {currentSubjectId && (
            <div className="flex items-center gap-1 shrink-0 ml-2 border-l border-border pl-2">
              <button
                onClick={() => setScopeFilter("current")}
                className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                  scopeFilter === "current"
                    ? "bg-primary/20 text-primary font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                This System
              </button>
              <button
                onClick={() => setScopeFilter("all")}
                className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                  scopeFilter === "all"
                    ? "bg-primary/20 text-primary font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                All Systems
              </button>
            </div>
          )}
        </div>

        {/* Results Container */}
        <div ref={resultsRef} className="max-h-[380px] overflow-y-auto p-2 scrollbar-thin">
          {/* Recent Searches */}
          {!query && recentSearches.length > 0 && (
            <div className="mb-3 px-3 pt-2">
              <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                <span className="flex items-center gap-1.5">
                  <Clock className="h-3 w-3" /> Recent Searches
                </span>
                <button
                  onClick={() => setRecentSearches([])}
                  className="hover:text-foreground text-[10px] lowercase"
                >
                  clear history
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {recentSearches.map((term, i) => (
                  <button
                    key={i}
                    onClick={() => setQuery(term)}
                    className="flex items-center gap-1.5 rounded-md bg-muted/50 px-2.5 py-1 text-xs text-foreground hover:bg-indigo-500/10 hover:text-indigo-600 dark:hover:text-indigo-400 border border-border/50"
                  >
                    <span>{term}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading ? (
            <div className="py-12 text-center">
              <Loader2 className="mx-auto h-7 w-7 text-indigo-500 animate-spin mb-2" />
              <p className="text-xs text-muted-foreground">Loading real resources...</p>
            </div>
          ) : filteredResults.length > 0 ? (
            <div className="space-y-1">
              {filteredResults.map((item, idx) => {
                const isSelected = idx === selectedIndex;
                const subjectTitle = SYSTEM_MAP[item.subject_id] || item.subject_id;
                return (
                  <div
                    key={item.id}
                    onClick={() => handleOpenItem(item)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`group relative flex items-start justify-between rounded-lg p-3 cursor-pointer transition-all ${
                      isSelected
                        ? "bg-indigo-50/80 dark:bg-indigo-950/40 border-l-4 border-indigo-600 dark:border-indigo-400 pl-3"
                        : "hover:bg-muted/50 border-l-4 border-transparent"
                    }`}
                  >
                    <div className="flex items-start gap-3 flex-1 min-w-0 pr-3">
                      <div className="mt-0.5 p-2 rounded-lg bg-background border border-border shadow-xs shrink-0">
                        {getItemIcon(item.resource_type)}
                      </div>
                      <div className="space-y-1 flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold text-foreground leading-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate max-w-[320px]">
                            {item.original_name}
                          </span>
                          <Badge variant="outline" className="text-[10px] px-1.5 py-0 uppercase font-medium">
                            {item.resource_type.replace("_", " ")}
                          </Badge>
                          {item.created_at && (
                            <span className="text-[10px] text-muted-foreground">
                              {formatRelativeTime(item.created_at)}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span className="font-medium text-foreground/80">{subjectTitle}</span>
                          <span>•</span>
                          <span>{formatBytes(item.file_size_bytes)}</span>
                          {item.status && (
                            <>
                              <span>•</span>
                              <span className="text-[10px] capitalize text-emerald-600 dark:text-emerald-400">
                                {item.status.toLowerCase()}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Action Quick Buttons */}
                    <div className="flex items-center gap-1 shrink-0 self-center">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-muted-foreground hover:text-foreground"
                        title="Download file"
                        onClick={(e) => handleDownload(e, item)}
                      >
                        <Download className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-muted-foreground hover:text-indigo-600 dark:hover:text-indigo-400"
                        title="View file"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenItem(item);
                        }}
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-12 text-center">
              <FileUp className="mx-auto h-8 w-8 text-muted-foreground/50 mb-2" />
              <p className="text-sm font-medium text-foreground">
                {query ? "No matching resources found" : "No resources uploaded yet"}
              </p>
              <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                {query
                  ? `No uploaded files matched "${query}". Try searching a different keyword or category.`
                  : scopeFilter === "current" && currentSubjectId
                  ? `No resources uploaded yet for ${SYSTEM_MAP[currentSubjectId] || currentSubjectId}. Upload notes, videos, or lab manuals in this system to see them here!`
                  : "No resources found. Upload notes, lab manuals, books or videos to search them instantly."}
              </p>
            </div>
          )}
        </div>

        {/* Footer Shortcut Bar */}
        <div className="flex items-center justify-between border-t border-border bg-muted/40 px-4 py-2.5 text-[11px] text-muted-foreground">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="rounded border border-border bg-background px-1 py-0.5 font-mono text-[10px] shadow-xs">
                ↑
              </kbd>
              <kbd className="rounded border border-border bg-background px-1 py-0.5 font-mono text-[10px] shadow-xs">
                ↓
              </kbd>
              <span>navigate</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="rounded border border-border bg-background px-1.5 py-0.5 font-mono text-[10px] shadow-xs">
                ↵
              </kbd>
              <span>open</span>
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400 font-medium">
            <Sparkles className="h-3 w-3" />
            <span>CircuitGPT Real-Time Resource Search</span>
          </div>
        </div>
      </div>
    </div>
  );
}

