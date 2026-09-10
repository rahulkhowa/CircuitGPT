"use client";

import React, { useState, useRef, useCallback, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  BookOpen,
  FileText,
  Video,
  FlaskConical,
  HelpCircle,
  FileCode2,
  Bot,
  Download,
  Play,
  Upload,
  ExternalLink,
  Zap,
  Cpu,
  GraduationCap,
  TrendingUp,
  Trash2,
  AlertCircle,
  Loader2,
  FileUp,
} from "lucide-react";
import { NotionNotebook } from "@/components/notion-notebook";
import { AiChatInterface } from "@/components/ai-chat-interface";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/context/auth-context";

// ─────────────────────────────────────────────
// Subject definitions (metadata only — no fake resources)
// ─────────────────────────────────────────────

const SYSTEMS_DATA: Record<
  string,
  {
    code: string;
    title: string;
    description: string;
    icon: React.ComponentType<{ className?: string }>;
  }
> = {
  "power-system": {
    code: "EE-PS",
    title: "Power System",
    description:
      "Grid Stability, Transmission Line Modeling, Load Flow Analysis, Fault Calculation & Protection Relays.",
    icon: Zap,
  },
  "power-electronics": {
    code: "EE-PE",
    title: "Power Electronics",
    description:
      "AC-DC Rectifiers, DC-DC Buck/Boost Converters, Inverters, PWM Strategies & Gate Drivers.",
    icon: Cpu,
  },
  "machine-system": {
    code: "EE-MS",
    title: "Machine System",
    description:
      "Transformers, Synchronous Generators, DC Motors, 3-Phase Induction Motors & Magnetic Circuits.",
    icon: GraduationCap,
  },
  "network-system": {
    code: "EE-NS",
    title: "Network System",
    description:
      "Nodal Analysis, Thévenin & Norton Theorems, Two-Port Networks, RLC Resonant & Transient Response.",
    icon: BookOpen,
  },
  "control-system": {
    code: "EE-CS",
    title: "Control System",
    description:
      "Transfer Functions, Block Diagrams, Bode Plots, Nyquist Stability Criterion, PID Controllers & State Space.",
    icon: TrendingUp,
  },
};

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

type ResourceType = "notes" | "videos" | "lab_manuals" | "books" | "pyqs";

interface Resource {
  id: string;
  subject_id: string;
  resource_type: ResourceType;
  original_name: string;
  mime_type: string;
  file_size_bytes: number | null;
  created_at: string;
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────

function formatBytes(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
  if (diff < 172800) return "yesterday";
  return date.toLocaleDateString();
}

const ALLOWED_ACCEPT: Record<ResourceType, string> = {
  notes: ".pdf,.doc,.docx",
  videos: ".mp4,.webm,.mkv,.mov",
  lab_manuals: ".pdf,.doc,.docx",
  books: ".pdf",
  pyqs: ".pdf",
};

// ─────────────────────────────────────────────
// Resource uploader component
// ─────────────────────────────────────────────

function ResourceUploader({
  subjectId,
  resourceType,
  label,
  token,
  onSuccess,
}: {
  subjectId: string;
  resourceType: ResourceType;
  label: string;
  token: string;
  onSuccess: () => void;
}) {
  const [state, setState] = useState<"idle" | "uploading" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost/api/v1";

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setState("uploading");
    setErrorMsg("");

    const form = new FormData();
    form.append("file", file);
    form.append("subject_id", subjectId);
    form.append("resource_type", resourceType);

    try {
      const res = await fetch(`${API_URL}/uploads`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });

      if (res.ok) {
        setState("idle");
        onSuccess();
      } else {
        const data = await res.json().catch(() => ({}));
        const msg = data?.detail || `Upload failed (${res.status})`;
        setState("error");
        setErrorMsg(typeof msg === "string" ? msg : JSON.stringify(msg));
      }
    } catch {
      setState("error");
      setErrorMsg("Network error. Check your connection.");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="flex flex-col items-end gap-1">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleChange}
        className="hidden"
        accept={ALLOWED_ACCEPT[resourceType]}
        id={`upload-${resourceType}`}
      />
      <Button
        variant="outline"
        size="sm"
        disabled={state === "uploading"}
        onClick={() => fileInputRef.current?.click()}
        className="gap-2 text-xs border-dashed border-primary/40 hover:border-primary hover:bg-primary/5"
        id={`upload-btn-${resourceType}`}
      >
        {state === "uploading" ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
        ) : (
          <Upload className="h-3.5 w-3.5" />
        )}
        {state === "uploading" ? "Uploading…" : `Upload ${label}`}
      </Button>
      {state === "error" && (
        <p className="text-xs text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" /> {errorMsg}
        </p>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────
// Resource list row
// ─────────────────────────────────────────────

function ResourceRow({
  resource,
  icon: Icon,
  token,
  onDeleted,
}: {
  resource: Resource;
  icon: React.ComponentType<{ className?: string }>;
  token: string;
  onDeleted: (id: string) => void;
}) {
  const [deleting, setDeleting] = useState(false);
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost/api/v1";

  const getUrl = async (mode: "view" | "download") => {
    const res = await fetch(`${API_URL}/uploads/${resource.id}/${mode}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Could not get file URL");
    const data = await res.json();
    return data.url as string;
  };

  const handleOpen = async () => {
    try {
      const url = await getUrl("view");
      window.open(url, "_blank");
    } catch {
      alert("Could not open file. Please try again.");
    }
  };

  const handleDownload = async () => {
    try {
      const url = await getUrl("download");
      const a = document.createElement("a");
      a.href = url;
      a.download = resource.original_name;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch {
      alert("Could not download file. Please try again.");
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${resource.original_name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      const res = await fetch(`${API_URL}/uploads/${resource.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok || res.status === 204) {
        onDeleted(resource.id);
      } else {
        alert("Delete failed. Please try again.");
      }
    } catch {
      alert("Network error. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  const isVideo = resource.resource_type === "videos";

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/40 transition group">
      <div className="flex items-center gap-3 min-w-0">
        <div className="p-2 rounded bg-primary/10 text-primary shrink-0">
          <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <div className="font-medium text-sm truncate">{resource.original_name}</div>
          <div className="text-xs text-muted-foreground">
            {formatBytes(resource.file_size_bytes)} • {formatRelativeTime(resource.created_at)}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-1 ml-3 shrink-0">
        <Button
          variant="ghost"
          size="sm"
          className="gap-1 text-xs h-8 px-2"
          onClick={handleOpen}
          title={isVideo ? "Play" : "Open"}
        >
          {isVideo ? <Play className="h-3.5 w-3.5" /> : <ExternalLink className="h-3.5 w-3.5" />}
          <span className="hidden sm:inline">{isVideo ? "Play" : "Open"}</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="gap-1 text-xs h-8 px-2"
          onClick={handleDownload}
          title="Download"
        >
          <Download className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Download</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="gap-1 text-xs h-8 px-2 text-destructive hover:text-destructive hover:bg-destructive/10"
          onClick={handleDelete}
          disabled={deleting}
          title="Delete"
        >
          {deleting ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Trash2 className="h-3.5 w-3.5" />
          )}
        </Button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Empty state component
// ─────────────────────────────────────────────

function EmptyState({
  label,
  subLabel,
  resourceType,
  subjectId,
  token,
  onSuccess,
}: {
  label: string;
  subLabel: string;
  resourceType: ResourceType;
  subjectId: string;
  token: string;
  onSuccess: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
      <div className="p-4 rounded-full bg-muted">
        <FileUp className="h-8 w-8 text-muted-foreground" />
      </div>
      <div>
        <p className="font-medium text-sm">{label}</p>
        <p className="text-xs text-muted-foreground mt-1 max-w-xs">{subLabel}</p>
      </div>
      <ResourceUploader
        subjectId={subjectId}
        resourceType={resourceType}
        label={label.replace("No ", "").replace(" uploaded yet", "")}
        token={token}
        onSuccess={onSuccess}
      />
    </div>
  );
}

// ─────────────────────────────────────────────
// Resource tab panel (generic — reused for all 5 tabs)
// ─────────────────────────────────────────────

function ResourceTabPanel({
  title,
  description,
  resourceType,
  subjectId,
  token,
  icon: Icon,
  emptyLabel,
  emptySubLabel,
  uploadLabel,
}: {
  title: string;
  description: string;
  resourceType: ResourceType;
  subjectId: string;
  token: string;
  icon: React.ComponentType<{ className?: string }>;
  emptyLabel: string;
  emptySubLabel: string;
  uploadLabel: string;
}) {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost/api/v1";

  const fetchResources = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${API_URL}/uploads?subject_id=${subjectId}&resource_type=${resourceType}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (res.ok) {
        setResources(await res.json());
      } else {
        setError(`Failed to load resources (${res.status})`);
      }
    } catch {
      setError("Network error. Could not load resources.");
    } finally {
      setLoading(false);
    }
  }, [subjectId, resourceType, token, API_URL]);

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  const handleDeleted = (id: string) => {
    setResources((prev) => prev.filter((r) => r.id !== id));
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            <span>{title}</span>
            <Badge variant="secondary">Common Resource</Badge>
          </CardTitle>
          <CardDescription className="mt-1">{description}</CardDescription>
        </div>
        {!loading && (
          <ResourceUploader
            subjectId={subjectId}
            resourceType={resourceType}
            label={uploadLabel}
            token={token}
            onSuccess={fetchResources}
          />
        )}
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="flex items-center justify-center py-12 gap-2 text-muted-foreground text-sm">
            <Loader2 className="h-5 w-5 animate-spin" />
            Loading resources…
          </div>
        )}

        {!loading && error && (
          <div className="flex items-center justify-center py-10 gap-2 text-destructive text-sm">
            <AlertCircle className="h-4 w-4" />
            {error}
            <Button variant="ghost" size="sm" onClick={fetchResources} className="text-xs ml-2">
              Retry
            </Button>
          </div>
        )}

        {!loading && !error && resources.length === 0 && (
          <EmptyState
            label={emptyLabel}
            subLabel={emptySubLabel}
            resourceType={resourceType}
            subjectId={subjectId}
            token={token}
            onSuccess={fetchResources}
          />
        )}

        {!loading && !error && resources.length > 0 && (
          <div className="space-y-2">
            {resources.map((r) => (
              <ResourceRow
                key={r.id}
                resource={r}
                icon={Icon}
                token={token}
                onDeleted={handleDeleted}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────
// Main page
// ─────────────────────────────────────────────

export default function SubjectWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const { token } = useAuth();

  const rawId = (params?.id as string)?.toLowerCase() || "power-system";
  const systemId = SYSTEMS_DATA[rawId] ? rawId : "power-system";
  const system = SYSTEMS_DATA[systemId];
  const SystemIcon = system.icon;

  const [activeTab, setActiveTab] = useState("notes");

  // If not authenticated, the protected route wrapper will redirect.
  // Fallback token guard to avoid API calls with empty token.
  const authToken = token || "";

  return (
    <div className="space-y-6 pb-12">
      {/* Subject Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-xl bg-card border p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => router.push("/dashboard")}
            className="mt-1 shrink-0"
            id="back-to-dashboard"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="font-mono text-primary bg-primary/10 border-primary/20">
                {system.code}
              </Badge>
            </div>
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <SystemIcon className="h-6 w-6 text-primary" />
              {system.title}
            </h1>
            <p className="text-sm text-muted-foreground max-w-2xl">{system.description}</p>
          </div>
        </div>
      </div>

      {/* Workspace Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 md:grid-cols-7 h-auto p-1 bg-muted/60">
          <TabsTrigger value="notes" className="gap-1.5 py-2 text-xs font-medium" id="tab-notes">
            <FileText className="h-3.5 w-3.5" /> Notes
          </TabsTrigger>
          <TabsTrigger value="videos" className="gap-1.5 py-2 text-xs font-medium" id="tab-videos">
            <Video className="h-3.5 w-3.5" /> Lab Videos
          </TabsTrigger>
          <TabsTrigger value="lab_manuals" className="gap-1.5 py-2 text-xs font-medium" id="tab-lab-manuals">
            <FlaskConical className="h-3.5 w-3.5" /> Lab Manuals
          </TabsTrigger>
          <TabsTrigger value="books" className="gap-1.5 py-2 text-xs font-medium" id="tab-books">
            <BookOpen className="h-3.5 w-3.5" /> Books
          </TabsTrigger>
          <TabsTrigger value="pyqs" className="gap-1.5 py-2 text-xs font-medium" id="tab-pyqs">
            <HelpCircle className="h-3.5 w-3.5" /> PYQs
          </TabsTrigger>
          <TabsTrigger value="notebook" className="gap-1.5 py-2 text-xs font-medium" id="tab-notebook">
            <FileCode2 className="h-3.5 w-3.5" /> Notebook
          </TabsTrigger>
          <TabsTrigger value="aichat" className="gap-1.5 py-2 text-xs font-medium text-primary" id="tab-aichat">
            <Bot className="h-3.5 w-3.5" /> AI Chat
          </TabsTrigger>
        </TabsList>

        {/* 1. NOTES */}
        <TabsContent value="notes" className="mt-4">
          <ResourceTabPanel
            title="Lecture Notes & Formula Sheets"
            description="Upload your lecture notes, derivations, and formula references."
            resourceType="notes"
            subjectId={systemId}
            token={authToken}
            icon={FileText}
            emptyLabel="No notes uploaded yet."
            emptySubLabel="Upload your lecture notes, formula sheets, or study material to get started."
            uploadLabel="Notes"
          />
        </TabsContent>

        {/* 2. LAB VIDEOS */}
        <TabsContent value="videos" className="mt-4">
          <ResourceTabPanel
            title="Lab Demonstration Videos & Lectures"
            description="Upload video walkthroughs of experiments, hardware sessions, and lectures."
            resourceType="videos"
            subjectId={systemId}
            token={authToken}
            icon={Video}
            emptyLabel="No videos uploaded yet."
            emptySubLabel="Upload lab demonstration videos, experiment recordings, or lecture videos."
            uploadLabel="Video"
          />
        </TabsContent>

        {/* 3. LAB MANUALS */}
        <TabsContent value="lab_manuals" className="mt-4">
          <ResourceTabPanel
            title="Laboratory Manuals & Procedure Guides"
            description="Upload lab manuals, experiment procedure guides, and observation tables."
            resourceType="lab_manuals"
            subjectId={systemId}
            token={authToken}
            icon={FlaskConical}
            emptyLabel="No lab manuals uploaded yet."
            emptySubLabel="Upload experiment procedure guides, safety documents, or lab manuals."
            uploadLabel="Lab Manual"
          />
        </TabsContent>

        {/* 4. BOOKS */}
        <TabsContent value="books" className="mt-4">
          <ResourceTabPanel
            title="Books & References"
            description="Upload textbooks, reference PDFs, and academic publications."
            resourceType="books"
            subjectId={systemId}
            token={authToken}
            icon={BookOpen}
            emptyLabel="No books uploaded yet."
            emptySubLabel="Upload textbooks, reference PDFs, or academic publications."
            uploadLabel="Book"
          />
        </TabsContent>

        {/* 5. PYQs */}
        <TabsContent value="pyqs" className="mt-4">
          <ResourceTabPanel
            title="Previous Year Questions"
            description="Upload previous year exam papers, test banks, and solved papers."
            resourceType="pyqs"
            subjectId={systemId}
            token={authToken}
            icon={HelpCircle}
            emptyLabel="No PYQs uploaded yet."
            emptySubLabel="Upload previous year exam papers, test banks, or solved question papers."
            uploadLabel="PYQ"
          />
        </TabsContent>

        {/* 6. PERSONAL NOTEBOOK */}
        <TabsContent value="notebook" className="space-y-4 mt-4">
          <Card className="p-4 border shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b pb-3">
              <div>
                <h3 className="font-bold text-base flex items-center gap-2">
                  <FileCode2 className="h-5 w-5 text-primary" /> Personal Editable Notebook
                </h3>
                <p className="text-xs text-muted-foreground">
                  Editable and auto-saved locally for {system.title}. Keep your personal formulas,
                  derivations, and study notes here.
                </p>
              </div>
            </div>
            <NotionNotebook
              subjectCode={system.code}
              initialTitle={`${system.title} — Personal Study Notes`}
            />
          </Card>
        </TabsContent>

        {/* 7. AI CHAT */}
        <TabsContent value="aichat" className="space-y-4 mt-4">
          <AiChatInterface
            subjectCode={system.code}
            subjectTitle={system.title}
            systemId={systemId}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
