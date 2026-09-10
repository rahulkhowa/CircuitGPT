"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Bold,
  Italic,
  Heading1,
  Heading2,
  Heading3,
  Code,
  Sparkles,
  Save,
  Eye,
  Edit3,
  Columns,
  Download,
  Terminal,
  Quote,
  List,
  Wand2,
  CheckCircle2,
  Copy,
  FileText,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

interface NotionNotebookProps {
  initialTitle?: string;
  initialContent?: string;
  subjectCode?: string;
}

export function NotionNotebook({
  initialTitle = "EE101 — Circuit Theory Study Notes",
  initialContent,
  subjectCode = "EE101",
}: NotionNotebookProps) {
  const defaultNote =
    initialContent ||
    `# EE101 — Circuit Theory & Network Analysis Notes

## 1. Fundamental Circuit Laws

### Kirchhoff's Current Law (KCL)
The algebraic sum of currents entering any node is equal to zero:
$$\\sum_{k=1}^n I_k = 0$$

> **Key Takeaway**: KCL is a direct statement of the conservation of electric charge.

### Kirchhoff's Voltage Law (KVL)
The algebraic sum of all voltages around any closed loop in a circuit is zero:
$$\\sum_{k=1}^n V_k = 0$$

---

## 2. Network Theorems

- **Thévenin's Theorem**: Any linear two-terminal circuit can be replaced by an equivalent circuit consisting of a voltage source $V_{th}$ in series with a resistor $R_{th}$.
- **Norton's Theorem**: Dual of Thévenin's theorem using a current source $I_N$ in parallel with $R_N$.

\`\`\`python
# Python Solver for KCL Node Voltages
import numpy as np

# Conductance Matrix G * V = I
G = np.array([[0.3, -0.1], [-0.1, 0.15]])
I = np.array([4.0, 0.0])

V = np.linalg.solve(G, I)
print(f"Node Voltages V1={V[0]:.2f}V, V2={V[1]:.2f}V")
\`\`\`

> Tip: Type \`/ai\` anywhere to ask CircuitGPT to generate derivations, formulas, or summaries inline.`;

  const [title, setTitle] = useState(initialTitle);
  const [content, setContent] = useState(defaultNote);
  const [viewMode, setViewMode] = useState<"write" | "preview" | "split">("split");
  const [isSaved, setIsSaved] = useState(true);
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [showAiModal, setShowAiModal] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [isAiGenerating, setIsAiGenerating] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-save simulation
  useEffect(() => {
    setIsSaved(false);
    const timer = setTimeout(() => {
      setIsSaved(true);
    }, 1200);
    return () => clearTimeout(timer);
  }, [content, title]);

  // Listen for slash command /
  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);

    const cursor = e.target.selectionStart;
    const textBeforeCursor = val.slice(0, cursor);
    if (textBeforeCursor.endsWith("/ai") || textBeforeCursor.endsWith("/")) {
      setShowSlashMenu(true);
    } else {
      setShowSlashMenu(false);
    }
  };

  // Insert markdown helper
  const insertText = (prefix: string, suffix: string = "") => {
    if (!textareaRef.current) return;
    const el = textareaRef.current;
    const start = el.selectionStart;
    const end = el.selectionEnd;
    const selected = content.substring(start, end);
    const replacement = `${prefix}${selected || "text"}${suffix}`;

    const newContent = content.substring(0, start) + replacement + content.substring(end);
    setContent(newContent);
    setShowSlashMenu(false);

    setTimeout(() => {
      el.focus();
      el.setSelectionRange(start + prefix.length, start + prefix.length + (selected ? selected.length : 4));
    }, 50);
  };

  // AI Prompt Generation Trigger
  const handleGenerateAi = (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiPrompt.trim()) return;

    setIsAiGenerating(true);
    setTimeout(() => {
      const generatedSnippet = `\n\n### AI Explanation: ${aiPrompt}\nFor ${subjectCode}, ${aiPrompt}: We solve the circuit by setting up nodal equations where $\\sum I_{out} = 0$. The resulting impedance matrix yields exact branch currents.\n`;
      setContent((prev) => prev + generatedSnippet);
      setIsAiGenerating(false);
      setShowAiModal(false);
      setAiPrompt("");
    }, 1000);
  };

  // Simple Markdown Parser for Preview Mode
  const renderFormattedMarkdown = (text: string) => {
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      if (line.startsWith("# ")) {
        return (
          <h1 key={idx} className="text-2xl font-bold text-primary mt-4 mb-2 pb-1 border-b">
            {line.replace("# ", "")}
          </h1>
        );
      }
      if (line.startsWith("## ")) {
        return (
          <h2 key={idx} className="text-xl font-semibold mt-4 mb-2">
            {line.replace("## ", "")}
          </h2>
        );
      }
      if (line.startsWith("### ")) {
        return (
          <h3 key={idx} className="text-lg font-medium mt-3 mb-1 text-slate-300">
            {line.replace("### ", "")}
          </h3>
        );
      }
      if (line.startsWith("> ")) {
        return (
          <blockquote
            key={idx}
            className="p-3 my-2 bg-amber-500/10 border-l-4 border-amber-500 rounded text-sm italic text-amber-600 dark:text-amber-300"
          >
            {line.replace("> ", "")}
          </blockquote>
        );
      }
      if (line.startsWith("```")) {
        return (
          <div key={idx} className="font-mono text-xs text-emerald-400 bg-slate-950 p-2 rounded my-1 border">
            {line}
          </div>
        );
      }
      if (line.startsWith("- ")) {
        return (
          <li key={idx} className="ml-5 list-disc text-sm py-0.5">
            {line.replace("- ", "")}
          </li>
        );
      }
      if (line.trim() === "---") {
        return <hr key={idx} className="my-4 border-muted" />;
      }
      if (!line.trim()) {
        return <div key={idx} className="h-2" />;
      }
      return (
        <p key={idx} className="text-sm leading-relaxed">
          {line}
        </p>
      );
    });
  };

  return (
    <Card className="w-full border shadow-sm">
      {/* Top Controls Header */}
      <CardHeader className="p-4 border-b space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="font-mono bg-primary/10 text-primary border-primary/20">
              {subjectCode}
            </Badge>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="font-bold text-lg bg-transparent border-none focus:outline-none focus:ring-1 focus:ring-primary rounded px-1"
            />
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Auto Save Status */}
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mr-2">
              {isSaved ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Saved to Cloud</span>
                </>
              ) : (
                <>
                  <Save className="h-3.5 w-3.5 animate-spin text-amber-500" />
                  <span>Saving...</span>
                </>
              )}
            </div>

            {/* View Mode Switches */}
            <div className="flex items-center bg-muted p-1 rounded-lg">
              <Button
                variant={viewMode === "write" ? "secondary" : "ghost"}
                size="sm"
                className="h-7 text-xs px-2"
                onClick={() => setViewMode("write")}
              >
                <Edit3 className="h-3.5 w-3.5 mr-1" /> Edit
              </Button>
              <Button
                variant={viewMode === "split" ? "secondary" : "ghost"}
                size="sm"
                className="h-7 text-xs px-2"
                onClick={() => setViewMode("split")}
              >
                <Columns className="h-3.5 w-3.5 mr-1" /> Split
              </Button>
              <Button
                variant={viewMode === "preview" ? "secondary" : "ghost"}
                size="sm"
                className="h-7 text-xs px-2"
                onClick={() => setViewMode("preview")}
              >
                <Eye className="h-3.5 w-3.5 mr-1" /> Preview
              </Button>
            </div>

            {/* AI Assistant Button */}
            <Button
              size="sm"
              className="h-8 gap-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-xs"
              onClick={() => setShowAiModal(true)}
            >
              <Sparkles className="h-3.5 w-3.5" /> /ai Assist
            </Button>
          </div>
        </div>

        {/* Formatting Toolbar */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 text-xs border-t pt-2">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("**", "**")}>
            <Bold className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("*", "*")}>
            <Italic className="h-3.5 w-3.5" />
          </Button>
          <div className="h-4 w-[1px] bg-border mx-1" />
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("# ")}>
            <Heading1 className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("## ")}>
            <Heading2 className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("### ")}>
            <Heading3 className="h-3.5 w-3.5" />
          </Button>
          <div className="h-4 w-[1px] bg-border mx-1" />
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("```python\n", "\n```")}>
            <Code className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("$$", "$$")}>
            <Terminal className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("> ")}>
            <Quote className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => insertText("- ")}>
            <List className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>

      {/* Editor Content Body */}
      <CardContent className="p-4 relative">
        {/* Slash Command Floating Menu */}
        {showSlashMenu && (
          <div className="absolute top-12 left-8 z-20 w-64 bg-card border rounded-xl shadow-xl p-2 space-y-1">
            <div className="text-[10px] font-bold text-muted-foreground uppercase px-2 py-1">
              Slash Commands
            </div>
            <button
              onClick={() => {
                setShowSlashMenu(false);
                setShowAiModal(true);
              }}
              className="w-full text-left flex items-center gap-2 p-2 rounded-lg hover:bg-primary/10 text-xs font-medium text-primary transition"
            >
              <Sparkles className="h-4 w-4" />
              <div>
                <div>/ai Ask CircuitGPT AI</div>
                <div className="text-[10px] text-muted-foreground">Generate formulas or derivations</div>
              </div>
            </button>
            <button
              onClick={() => insertText("## ")}
              className="w-full text-left flex items-center gap-2 p-2 rounded-lg hover:bg-muted text-xs transition"
            >
              <Heading2 className="h-4 w-4" /> /h2 Heading 2
            </button>
            <button
              onClick={() => insertText("```python\n", "\n```")}
              className="w-full text-left flex items-center gap-2 p-2 rounded-lg hover:bg-muted text-xs transition"
            >
              <Code className="h-4 w-4" /> /code Code Snippet
            </button>
          </div>
        )}

        {/* AI Assist Modal Popover */}
        {showAiModal && (
          <div className="mb-4 p-4 border rounded-xl bg-gradient-to-r from-blue-950/20 to-indigo-950/20 border-indigo-500/30 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-primary font-bold text-sm">
                <Wand2 className="h-4 w-4" /> CircuitGPT Inline AI Assistant
              </div>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={() => setShowAiModal(false)}>
                ✕
              </Button>
            </div>
            <form onSubmit={handleGenerateAi} className="flex gap-2">
              <Input
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="Ask AI to derive Thévenin voltage, write KCL equations, or summarize..."
                className="text-xs"
              />
              <Button type="submit" size="sm" disabled={isAiGenerating} className="gap-1 text-xs">
                {isAiGenerating ? <Save className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
                Generate
              </Button>
            </form>
          </div>
        )}

        {/* Split / Write / Preview Layout */}
        <div
          className={`grid gap-4 min-h-[450px] ${
            viewMode === "split" ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1"
          }`}
        >
          {/* Write Textarea */}
          {(viewMode === "write" || viewMode === "split") && (
            <textarea
              ref={textareaRef}
              value={content}
              onChange={handleTextareaChange}
              placeholder="Type markdown note here or type / for AI slash commands..."
              className="w-full h-full p-4 rounded-xl border bg-muted/20 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-y min-h-[400px]"
            />
          )}

          {/* Formatted Live Preview */}
          {(viewMode === "preview" || viewMode === "split") && (
            <div className="w-full h-full p-4 rounded-xl border bg-card/60 overflow-y-auto max-h-[500px]">
              <div className="space-y-2">{renderFormattedMarkdown(content)}</div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
