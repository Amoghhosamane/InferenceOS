"use client";

import React from "react";
import { MessageSquarePlus, Trash2, ChevronLeft, ChevronRight, BarChart3, ShieldCheck, Moon, Sun, Layers } from "lucide-react";
import { Conversation } from "@/lib/types";

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onDelete: (id: string, e: React.MouseEvent) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  onOpenMetrics: () => void;
  isCompareMode: boolean;
  onToggleCompare: () => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
}

export function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
  isCollapsed,
  onToggleCollapse,
  onOpenMetrics,
  isCompareMode,
  onToggleCompare,
  theme,
  onToggleTheme,
}: SidebarProps) {
  return (
    <aside
      className={`relative flex flex-col border-r transition-all duration-200 z-20 ${
        isCollapsed ? "w-16" : "w-72"
      } bg-[var(--bg-surface)] border-[var(--border-subtle)] shrink-0 h-full`}
      aria-label="Conversation history"
    >
      {/* Top Header / New Chat */}
      <div className="p-3 border-b border-[var(--border-subtle)] flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center space-x-2 px-2">
            <div className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse" />
            <span className="font-semibold text-sm tracking-tight text-[var(--text-primary)]">
              InferenceOS
            </span>
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-main)] hover:text-[var(--text-primary)] transition"
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Primary Action: New Chat */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-main)] text-sm font-medium text-[var(--text-primary)] hover:border-blue-500 hover:text-blue-600 transition shadow-sm ${
            isCollapsed ? "justify-center px-0" : ""
          }`}
          title="Start new conversation"
        >
          <MessageSquarePlus size={18} />
          {!isCollapsed && <span>New Chat</span>}
        </button>
      </div>

      {/* Compare Mode Toggle */}
      <div className="px-3 pb-2">
        <button
          onClick={onToggleCompare}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition ${
            isCompareMode
              ? "bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
              : "text-[var(--text-secondary)] hover:bg-[var(--bg-main)]"
          } ${isCollapsed ? "justify-center px-0" : ""}`}
          title="Toggle Multi-Model Comparison Mode"
        >
          <Layers size={16} />
          {!isCollapsed && (
            <span>{isCompareMode ? "Compare Active (2-3 models)" : "Compare Models"}</span>
          )}
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-1">
        {!isCollapsed && conversations.length === 0 && (
          <div className="px-3 py-6 text-center text-xs text-[var(--text-secondary)]">
            No previous chats. Start a new prompt!
          </div>
        )}

        {conversations.map((c) => {
          const isActive = c.id === activeId;
          return (
            <div
              key={c.id}
              onClick={() => onSelect(c.id)}
              className={`group flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition ${
                isActive
                  ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-950/40 dark:text-blue-300"
                  : "text-[var(--text-secondary)] hover:bg-[var(--bg-main)] hover:text-[var(--text-primary)]"
              }`}
              title={c.title}
            >
              <div className="truncate flex-1">
                {isCollapsed ? c.title.slice(0, 2) : c.title}
              </div>
              {!isCollapsed && (
                <button
                  onClick={(e) => onDelete(c.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 transition"
                  aria-label="Delete chat"
                  title="Delete chat"
                >
                  <Trash2 size={13} />
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer Tools: Observability & Theme */}
      <div className="p-3 border-t border-[var(--border-subtle)] space-y-1">
        <button
          onClick={onOpenMetrics}
          className={`w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-main)] hover:text-[var(--text-primary)] transition ${
            isCollapsed ? "justify-center px-0" : ""
          }`}
          title="Telemetry & Observability Dashboard"
        >
          <BarChart3 size={16} />
          {!isCollapsed && <span>Metrics & Quotas</span>}
        </button>

        <button
          onClick={onToggleTheme}
          className={`w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-main)] hover:text-[var(--text-primary)] transition ${
            isCollapsed ? "justify-center px-0" : ""
          }`}
          title="Toggle light / dark mode"
        >
          {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
          {!isCollapsed && <span>{theme === "light" ? "Dark Mode" : "Light Mode"}</span>}
        </button>

        {!isCollapsed && (
          <div className="pt-2 px-1 flex items-center gap-1.5 text-[10px] text-emerald-600 dark:text-emerald-400">
            <ShieldCheck size={13} />
            <span>Free-Tier Safeguard Active</span>
          </div>
        )}
      </div>
    </aside>
  );
}
