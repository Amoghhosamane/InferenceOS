"use client";

import React, { useState, useEffect, useRef } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ModelSelector } from "@/components/ModelSelector";
import { Composer } from "@/components/Composer";
import { MessageList } from "@/components/MessageList";
import { CompareView } from "@/components/CompareView";
import { MetricsModal } from "@/components/MetricsModal";
import {
  fetchModels,
  fetchConversations,
  fetchConversationDetail,
  createConversation,
  deleteConversation,
  streamChat,
} from "@/lib/api";
import { ModelMetadata, Conversation, ChatMessage, StreamChunk } from "@/lib/types";

export default function Home() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isCompareMode, setIsCompareMode] = useState(false);
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);

  // Models & State
  const [models, setModels] = useState<ModelMetadata[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("mock-gpt-oss");
  const [mockMode, setMockMode] = useState(true);

  // Conversations
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Composer & Streaming
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const abortControllerRef = useRef<AbortController | null>(null);

  // Compare View state
  const [compareModels, setCompareModels] = useState<string[]>([]);
  const [comparePrompt, setComparePrompt] = useState("");
  const [isComparing, setIsComparing] = useState(false);
  const [compareResults, setCompareResults] = useState<Record<string, {
    content: string;
    latency_ms?: number;
    ttft_ms?: number;
    error?: string;
  }>>({});

  // Theme synchronization
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  // Load models and initial conversation list
  useEffect(() => {
    async function loadInitialData() {
      try {
        const modelData = await fetchModels();
        setModels(modelData.models);
        setMockMode(modelData.mock_mode);
        if (modelData.models.length > 0) {
          setSelectedModel(modelData.models[0].id);
          // Set initial compare models (up to 3)
          setCompareModels(modelData.models.slice(0, 2).map((m) => m.id));
        }

        const convs = await fetchConversations();
        setConversations(convs);
      } catch (e) {
        console.error("Failed to load backend initial data", e);
      }
    }
    loadInitialData();
  }, []);

  // Handle selecting a conversation
  const handleSelectConversation = async (id: string) => {
    setActiveConversationId(id);
    setIsCompareMode(false);
    try {
      const detail = await fetchConversationDetail(id);
      setMessages(detail.messages || []);
      if (detail.model) {
        setSelectedModel(detail.model);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Handle starting a new chat
  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setIsCompareMode(false);
    setInput("");
  };

  // Handle deleting a conversation
  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        handleNewChat();
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Submit chat prompt
  const handleSubmitPrompt = async () => {
    if (!input.trim() || isStreaming) return;

    const userText = input.trim();
    setInput("");

    const newUserMsg: ChatMessage = {
      role: "user",
      content: userText,
      created_at: Date.now(),
    };

    const newMessages = [...messages, newUserMsg];
    setMessages(newMessages);

    // If no active conversation, create one
    let convId = activeConversationId;
    if (!convId) {
      try {
        const newConv = await createConversation(userText.slice(0, 30), selectedModel);
        convId = newConv.id;
        setActiveConversationId(convId);
        setConversations((prev) => [newConv, ...prev]);
      } catch (e) {
        console.error("Failed to auto-create conversation", e);
      }
    }

    // Initiate SSE stream
    setIsStreaming(true);
    setStreamingContent("");
    const controller = new AbortController();
    abortControllerRef.current = controller;
    const startTime = performance.now();
    let accumulatedText = "";

    await streamChat(
      selectedModel,
      newMessages,
      (chunk: StreamChunk) => {
        if (chunk.error) {
          accumulatedText += `\n[Error: ${chunk.error}]`;
        } else if (chunk.delta.content) {
          accumulatedText += chunk.delta.content;
        }
        setStreamingContent(accumulatedText);
      },
      () => {
        const totalDuration = performance.now() - startTime;
        setIsStreaming(false);
        abortControllerRef.current = null;
        if (accumulatedText) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: accumulatedText,
              model: selectedModel,
              latency_ms: totalDuration,
              created_at: Date.now(),
            },
          ]);
        }
        setStreamingContent("");
      },
      (err) => {
        setIsStreaming(false);
        abortControllerRef.current = null;
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "",
            error: err,
            model: selectedModel,
            created_at: Date.now(),
          },
        ]);
        setStreamingContent("");
      },
      controller.signal
    );
  };

  // Stop generation
  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    if (streamingContent) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: streamingContent + " [Stopped by user]",
          model: selectedModel,
          created_at: Date.now(),
        },
      ]);
    }
    setStreamingContent("");
  };

  // Compare Mode: Toggle Model
  const handleToggleCompareModel = (id: string) => {
    if (compareModels.includes(id)) {
      if (compareModels.length > 2) {
        setCompareModels(compareModels.filter((m) => m !== id));
      }
    } else {
      if (compareModels.length < 3) {
        setCompareModels([...compareModels, id]);
      }
    }
  };

  // Compare Mode: Run
  const handleRunCompare = async () => {
    if (!comparePrompt.trim() || isComparing || compareModels.length < 2) return;

    setIsComparing(true);
    const initialRes: Record<string, { content: string }> = {};
    compareModels.forEach((id) => {
      initialRes[id] = { content: "" };
    });
    setCompareResults(initialRes);

    const promises = compareModels.map(async (modelId) => {
      const startTime = performance.now();
      let text = "";
      let firstTokenTime: number | undefined;

      await streamChat(
        modelId,
        [{ role: "user", content: comparePrompt }],
        (chunk: StreamChunk) => {
          if (chunk.time_to_first_token_ms && !firstTokenTime) {
            firstTokenTime = chunk.time_to_first_token_ms;
          }
          if (chunk.error) {
            text += `\n[Error: ${chunk.error}]`;
          } else if (chunk.delta.content) {
            text += chunk.delta.content;
          }
          setCompareResults((prev) => ({
            ...prev,
            [modelId]: {
              content: text,
              ttft_ms: firstTokenTime,
            },
          }));
        },
        () => {
          const lat = performance.now() - startTime;
          setCompareResults((prev) => ({
            ...prev,
            [modelId]: {
              ...prev[modelId],
              latency_ms: lat,
            },
          }));
        },
        (err) => {
          setCompareResults((prev) => ({
            ...prev,
            [modelId]: {
              content: "",
              error: err,
            },
          }));
        }
      );
    });

    await Promise.all(promises);
    setIsComparing(false);
  };

  return (
    <div className="flex h-[100dvh] w-full overflow-hidden bg-[var(--bg-main)] text-[var(--text-primary)]">
      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        activeId={activeConversationId}
        onSelect={handleSelectConversation}
        onNewChat={handleNewChat}
        onDelete={handleDeleteConversation}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        onOpenMetrics={() => setIsMetricsOpen(true)}
        isCompareMode={isCompareMode}
        onToggleCompare={() => setIsCompareMode(!isCompareMode)}
        theme={theme}
        onToggleTheme={() => setTheme(theme === "light" ? "dark" : "light")}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Navigation Bar */}
        <header className="h-14 border-b border-[var(--border-subtle)] bg-[var(--bg-surface)] px-4 sm:px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <ModelSelector
              models={models}
              selectedModel={selectedModel}
              onSelectModel={setSelectedModel}
              mockMode={mockMode}
              disabled={isStreaming || isCompareMode}
            />

            {mockMode && (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-50 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                Mock Mode (Zero-Cost / Offline)
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsCompareMode(!isCompareMode)}
              className={`text-xs px-3 py-1.5 rounded-full font-medium transition ${
                isCompareMode
                  ? "bg-blue-600 text-white"
                  : "border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:bg-[var(--bg-main)]"
              }`}
            >
              {isCompareMode ? "Exit Compare" : "Compare Mode"}
            </button>
          </div>
        </header>

        {/* Dynamic View: Compare Mode or Single Chat */}
        {isCompareMode ? (
          <CompareView
            models={models}
            selectedModels={compareModels}
            onToggleModel={handleToggleCompareModel}
            prompt={comparePrompt}
            onPromptChange={setComparePrompt}
            onRunCompare={handleRunCompare}
            isComparing={isComparing}
            results={compareResults}
          />
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            <MessageList
              messages={messages}
              isStreaming={isStreaming}
              streamingContent={streamingContent}
              streamingModel={selectedModel}
            />

            <Composer
              input={input}
              onChange={setInput}
              onSubmit={handleSubmitPrompt}
              onStop={handleStopGeneration}
              isStreaming={isStreaming}
            />
          </div>
        )}
      </main>

      {/* Observability Telemetry Modal */}
      <MetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
      />
    </div>
  );
}
