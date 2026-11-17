"use client";

import React from "react";
import { ChatMessage } from "@/lib/types";
import { Bot, User, Clock, AlertCircle } from "lucide-react";

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent?: string;
  streamingModel?: string;
}

export function MessageList({
  messages,
  isStreaming,
  streamingContent,
  streamingModel,
}: MessageListProps) {
  const bottomRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950 flex items-center justify-center text-blue-600 dark:text-blue-400 mb-4 shadow-sm">
          <Bot size={26} />
        </div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)] tracking-tight">
          Welcome to InferenceOS
        </h2>
        <p className="text-sm text-[var(--text-secondary)] max-w-md mt-2">
          A minimalist, unified AI gateway for verified free-tier models across Groq, Gemini, and OpenRouter with real-time SSE streaming.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 max-w-3xl mx-auto w-full">
      {messages.map((m, index) => {
        const isUser = m.role === "user";
        return (
          <div
            key={m.id || index}
            className={`flex gap-3 sm:gap-4 ${isUser ? "justify-end" : "justify-start"}`}
          >
            {!isUser && (
              <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center shrink-0 text-slate-700 dark:text-slate-300 mt-0.5">
                <Bot size={15} />
              </div>
            )}

            <div
              className={`relative max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                isUser
                  ? "bg-blue-600 text-white rounded-tr-sm"
                  : "bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-[var(--text-primary)] rounded-tl-sm shadow-sm"
              }`}
            >
              {m.error ? (
                <div className="flex items-center gap-2 text-red-500 font-medium">
                  <AlertCircle size={16} />
                  <span>{m.error}</span>
                </div>
              ) : (
                <div className="whitespace-pre-wrap">{m.content}</div>
              )}

              {/* Message metadata footer */}
              {!isUser && (m.model || m.latency_ms) && (
                <div className="mt-2 pt-2 border-t border-[var(--border-subtle)]/60 flex items-center gap-3 text-[10px] text-[var(--text-secondary)]">
                  {m.model && <span className="font-medium">{m.model}</span>}
                  {m.latency_ms ? (
                    <span className="flex items-center gap-1">
                      <Clock size={11} />
                      {Math.round(m.latency_ms)}ms
                    </span>
                  ) : null}
                </div>
              )}
            </div>

            {isUser && (
              <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center shrink-0 text-blue-700 dark:text-blue-300 mt-0.5">
                <User size={15} />
              </div>
            )}
          </div>
        );
      })}

      {/* Live Streaming Message */}
      {isStreaming && (
        <div className="flex gap-3 sm:gap-4 justify-start">
          <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center shrink-0 text-slate-700 dark:text-slate-300 mt-0.5">
            <Bot size={15} />
          </div>
          <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-[var(--text-primary)] rounded-tl-sm shadow-sm">
            <div className="whitespace-pre-wrap">
              {streamingContent || (
                <span className="inline-flex items-center gap-1 text-[var(--text-secondary)] animate-pulse">
                  Streaming tokens...
                </span>
              )}
            </div>
            {streamingModel && (
              <div className="mt-2 pt-2 border-t border-[var(--border-subtle)]/60 text-[10px] text-[var(--text-secondary)] font-medium">
                {streamingModel}
              </div>
            )}
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
