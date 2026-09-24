"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";

import {
  Bot,
  ArrowUp,
  Square,
  User,
  Sparkles,
  Search,
  Plus,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Cpu,
  Zap,
  Code,
  Check,
  RotateCcw,
  MessageSquare,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAuth } from "@/context/auth-context";

interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
  timestamp: string;
  citations?: Array<{ source: string; snippet?: string }>;
  codeSnippet?: string;
}

interface ChatThread {
  id: string;
  title: string;
  date: string;
  messagesCount: number;
}

interface AiChatInterfaceProps {
  subjectCode?: string;
  subjectTitle?: string;
  systemId?: string;
  resourceType?: string;
}

export function AiChatInterface({
  subjectCode = "EE-PS",
  subjectTitle = "Power System",
  systemId = "power-system",
  resourceType,
}: AiChatInterfaceProps) {
  const { token: authToken } = useAuth();
  // Clean initial state according to Update.md specifications
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string>("session-1");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedModel, setSelectedModel] = useState("nemotron-ultra");

  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const [inputMsg, setInputMsg] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

  const getEffectiveToken = () => {
    if (authToken) return authToken;
    if (typeof window !== "undefined") {
      return localStorage.getItem("circuitgpt_access_token") || localStorage.getItem("access_token");
    }
    return null;
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  };

  // System-specific prompt suggestions
  const quickPrompts = [
    "Explain transient stability.",
    "Find PYQs related to load flow.",
    "Explain this topic using my uploaded notes.",
    "Derive equal area criterion for power systems.",
  ];

  const loadConversations = useCallback(async () => {
    try {
      const token = getEffectiveToken();
      const res = await fetch(`${API_URL}/chat/conversations?system_id=${systemId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setThreads(
          data.map((c: any) => ({
            id: c.session_id,
            title: c.title,
            date: "Active",
            messagesCount: c.message_count,
          }))
        );
      }
    } catch (err) {
      console.warn("Could not load conversations:", err);
    }
  }, [systemId, API_URL, authToken]);

  // Fetch active conversations on load
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Fetch conversation messages when activeThreadId changes
  useEffect(() => {
    if (!activeThreadId) return;

    let isMounted = true;
    async function loadThreadMessages() {
      const token = getEffectiveToken();
      try {
        const res = await fetch(`${API_URL}/chat/conversations/${activeThreadId}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (res.ok && isMounted) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setMessages(
              data.map((m: any) => ({
                id: m.id,
                sender: m.role === "user" ? "user" : "ai",
                text: m.content,
                timestamp: new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                citations: m.context_source ? [{ source: m.context_source }] : undefined,
              }))
            );
          }
        }
      } catch (err) {
        console.warn("Could not load thread messages:", err);
      }
    }
    loadThreadMessages();
    return () => {
      isMounted = false;
    };
  }, [activeThreadId, API_URL]);


  // Handle message submission with streaming support
  const handleSend = async (textToSend?: string) => {
    const query = textToSend || inputMsg;
    if (!query.trim()) return;

    const userMsgId = Date.now().toString();
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMsg("");
    setIsStreaming(true);

    const token = getEffectiveToken();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: query,
          subject_code: subjectCode,
          system_id: systemId,
          session_id: activeThreadId,
          resource_type: resourceType,
        }),
      });

      if (!res.ok) throw new Error("Chat request failed");

      const data = await res.json();
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        citations: data.citations,
      };
      setMessages((prev) => [...prev, aiResponse]);
      loadConversations();
    } catch (err: any) {

      if (err.name === "AbortError") {
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: "ai",
            text: "Generation stopped by user.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ]);
      } else {
        console.warn("Chat service warning:", err);
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: "ai",
            text: "Unable to reach the AI service. Please ensure your backend is running or try again in a moment.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ]);
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };


  const handleCopyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const filteredThreads = threads.filter((t) =>
    t.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 h-[650px]">
      {/* Sidebar: System Conversations */}
      <Card className="md:col-span-1 flex flex-col h-full border shadow-sm">
        <CardHeader className="p-3 border-b space-y-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-bold flex items-center gap-1.5">
              <MessageSquare className="h-4 w-4 text-primary" /> Conversations
            </CardTitle>
            <Button
              size="sm"
              className="h-7 w-7 p-0 rounded-lg"
              onClick={() => {
                const newId = `session-${Date.now()}`;
                setActiveThreadId(newId);
                setMessages([]);
              }}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>

          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="pl-8 h-8 text-xs"
            />
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-2 space-y-1">
          {filteredThreads.length === 0 ? (
            <div className="text-center p-4 text-xs text-muted-foreground">
              No saved conversations for {subjectTitle}.
            </div>
          ) : (
            filteredThreads.map((thread) => (
              <button
                key={thread.id}
                onClick={() => setActiveThreadId(thread.id)}
                className={`w-full text-left p-2 rounded-lg text-xs transition ${
                  activeThreadId === thread.id
                    ? "bg-primary/10 border border-primary/30 font-semibold"
                    : "hover:bg-muted"
                }`}
              >
                <div className="truncate">{thread.title}</div>
              </button>
            ))
          )}
        </CardContent>
      </Card>

      {/* Main Chat Panel */}
      <Card className="md:col-span-3 flex flex-col h-full border shadow-sm">
        {/* Header */}
        <CardHeader className="p-3 border-b flex flex-row items-center justify-between space-y-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-sm flex items-center gap-2">
                <span>CircuitGPT Tutor</span>
                <Badge className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 text-[10px]">
                  {subjectTitle}
                </Badge>
              </CardTitle>
              <CardDescription className="text-xs">
                NVIDIA Nemotron Ultra + Shared System RAG
              </CardDescription>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="h-8 w-48 text-xs font-mono">
                <SelectValue placeholder="Select Model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="nemotron-ultra">NVIDIA Nemotron Ultra (550B)</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="sm"
              className="h-8 w-8 p-0"
              onClick={() => setMessages([])}
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </Button>
          </div>
        </CardHeader>

        {/* Message Stream or Empty State */}
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
              <div className="p-3 rounded-full bg-primary/10 text-primary">
                <BookOpen className="h-8 w-8" />
              </div>
              <h3 className="font-bold text-base">CircuitGPT Tutor — {subjectTitle}</h3>
              <p className="text-xs text-muted-foreground max-w-md">
                Ask questions about your course, uploaded resources, derivations, or problem sets. Every document uploaded under this subject is indexed into shared RAG.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 max-w-lg w-full">
                {quickPrompts.map((prompt, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    className="text-xs justify-start h-auto py-2.5 px-3 text-left font-normal border shadow-2xs"
                    onClick={() => handleSend(prompt)}
                  >
                    "{prompt}"
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start gap-3 ${
                  msg.sender === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`p-2 rounded-full flex-shrink-0 ${
                    msg.sender === "user" ? "bg-blue-600 text-white" : "bg-primary/20 text-primary"
                  }`}
                >
                  {msg.sender === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                <div className="max-w-[85%] space-y-2">
                  <div
                    className={`p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-primary text-primary-foreground rounded-tr-none"
                        : "bg-card border shadow-xs rounded-tl-none space-y-3"
                    }`}
                  >
                    <div className="whitespace-pre-line">{msg.text}</div>

                    {/* Citations if present */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-2 pt-2 border-t text-[11px] space-y-1 text-muted-foreground">
                        <span className="font-semibold text-primary">References:</span>
                        {msg.citations.map((c, i) => (
                          <div key={i} className="truncate italic">
                            • According to <span className="font-medium">{c.source}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {msg.sender === "ai" && (
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground px-1">
                      <span>{msg.timestamp} • NVIDIA Nemotron Ultra</span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {isStreaming && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground italic pl-11">
              <Sparkles className="h-3.5 w-3.5 animate-spin text-primary" />
              <span>CircuitGPT is reasoning and computing response...</span>
            </div>
          )}
        </CardContent>

        {/* Input Bar */}
        <div className="p-3 border-t bg-muted/20">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!isStreaming) {
                handleSend();
              }
            }}
            className="flex items-center gap-2"
          >
            <Input
              value={inputMsg}
              onChange={(e) => setInputMsg(e.target.value)}
              placeholder={`Ask CircuitGPT about ${subjectTitle} topics, formulas, or exam questions...`}
              className="text-xs sm:text-sm h-10 rounded-xl bg-background border-border/80 focus-visible:ring-1"
            />

            {isStreaming ? (
              <Button
                type="button"
                size="icon"
                onClick={handleStop}
                title="Stop generating"
                className="h-10 w-10 rounded-xl bg-foreground text-background hover:bg-foreground/90 shrink-0 transition-all flex items-center justify-center shadow-sm"
              >
                <Square className="h-3.5 w-3.5 fill-current" />
              </Button>
            ) : (
              <Button
                type="submit"
                size="icon"
                disabled={!inputMsg.trim()}
                title="Send message"
                className="h-10 w-10 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed shrink-0 transition-all flex items-center justify-center shadow-sm"
              >
                <ArrowUp className="h-4 w-4 stroke-[2.5]" />
              </Button>
            )}
          </form>
        </div>
      </Card>
    </div>
  );
}

