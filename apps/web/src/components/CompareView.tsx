"use client";

import React, { useState } from "react";
import { ModelMetadata } from "@/lib/types";
import { AlertCircle, Copy, Check, RotateCcw, Download, Plus, X } from "lucide-react";

interface CompareViewProps {
  models: ModelMetadata[];
  selectedModels: string[];
  onToggleModel: (id: string) => void;
  onAddModel: (id: string) => void;
  onRemoveModel: (id: string) => void;
  prompt: string;
  onPromptChange: (val: string) => void;
  onRunCompare: () => void;
  isComparing: boolean;
  results: Record<string, {
    content: string;
    latency_ms?: number;
    ttft_ms?: number;
    tokens?: number;
    tokens_per_sec?: number;
    error?: string;
  }>;
  onRetryModel: (modelId: string) => void;
}

export function CompareView({
  models,
  selectedModels,
  onAddModel,
  onRemoveModel,
  prompt,
  onPromptChange,
  onRunCompare,
  isComparing,
  results,
  onRetryModel,
}: CompareViewProps) {
  const [copiedModel, setCopiedModel] = useState<string | null>(null);
  const [showAddDropdown, setShowAddDropdown] = useState(false);

  // Filter selectable models that are available and not already chosen
  const availableToAdd = models.filter(m => m.is_available && !selectedModels.includes(m.id));

  const handleCopy = (modelId: string, text: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedModel(modelId);
    setTimeout(() => setCopiedModel(null), 2000);
  };

  const handleExport = () => {
    const exportPayload = {
      timestamp: new Date().toISOString(),
      prompt,
      comparisons: selectedModels.map(mId => ({
        model: mId,
        output: results[mId]?.content || "",
        latency_ms: results[mId]?.latency_ms,
        ttft_ms: results[mId]?.ttft_ms,
        error: results[mId]?.error || null,
      }))
    };
    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `inferenceos-comparison-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 max-w-6xl mx-auto w-full flex flex-col space-y-4">
      {/* Title & Subtitle */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[var(--border-subtle)] pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[var(--text-primary)]">
            Compare AI Models
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Send an identical prompt simultaneously to 2 or 3 verified models to evaluate response variation, TTFT, and generation latency.
          </p>
        </div>
        
        {/* Export action */}
        {Object.values(results).some(r => r.content) && (
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-main)] transition self-start"
            title="Export comparison results as JSON"
          >
            <Download size={13} />
            <span>Export JSON</span>
          </button>
        )}
      </div>

      {/* Model Selection Header: Two by default, up to three */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-[var(--text-secondary)] mr-1">
          Active Models ({selectedModels.length}/3):
        </span>
        {selectedModels.map((mId) => {
          const meta = models.find((m) => m.id === mId);
          return (
            <div
              key={mId}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
            >
              <span>{meta?.name || mId}</span>
              {selectedModels.length > 2 && (
                <button
                  type="button"
                  onClick={() => onRemoveModel(mId)}
                  className="hover:text-red-500 transition ml-1"
                  title="Remove from comparison"
                >
                  <X size={12} />
                </button>
              )}
            </div>
          );
        })}

        {/* Add Model Button (If < 3) */}
        {selectedModels.length < 3 && (
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowAddDropdown(!showAddDropdown)}
              className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border border-dashed border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-blue-400 transition"
            >
              <Plus size={13} />
              <span>Add Model</span>
            </button>

            {showAddDropdown && (
              <>
                <div className="fixed inset-0 z-30" onClick={() => setShowAddDropdown(false)} />
                <div className="absolute left-0 mt-2 w-64 max-h-56 overflow-y-auto rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-1.5 shadow-xl z-40 text-xs">
                  {availableToAdd.length === 0 ? (
                    <div className="p-2 text-center text-slate-400 text-[11px]">No other available models</div>
                  ) : (
                    availableToAdd.map(m => (
                      <button
                        key={m.id}
                        onClick={() => {
                          onAddModel(m.id);
                          setShowAddDropdown(false);
                        }}
                        className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-[var(--bg-main)] text-[var(--text-primary)] truncate"
                      >
                        {m.name}
                      </button>
                    ))
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Shared Prompt Composer */}
      <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-3 shadow-xs">
        <textarea
          value={prompt}
          onChange={(e) => onPromptChange(e.target.value)}
          placeholder="Enter a prompt to broadcast to all selected models..."
          rows={3}
          className="w-full resize-none bg-transparent text-sm text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none"
        />
        <div className="flex justify-between items-center pt-2 border-t border-[var(--border-subtle)]/60 mt-1">
          <span className="text-[11px] text-[var(--text-secondary)]">
            Streams concurrently via FastAPI gateway
          </span>
          <button
            type="button"
            disabled={isComparing || selectedModels.length < 2 || !prompt.trim()}
            onClick={onRunCompare}
            className="px-4 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 transition disabled:opacity-40"
          >
            {isComparing ? "Running Comparison..." : `Compare (${selectedModels.length} models)`}
          </button>
        </div>
      </div>

      {/* Responsive Response Cards Grid */}
      <div className={`grid grid-cols-1 md:grid-cols-${selectedModels.length === 3 ? "3" : "2"} gap-4 flex-1`}>
        {selectedModels.map((mId) => {
          const meta = models.find((m) => m.id === mId);
          const res = results[mId] || { content: "" };

          return (
            <div
              key={mId}
              className="flex flex-col rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 shadow-xs"
            >
              {/* Card Header */}
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border-subtle)]/60 mb-2.5">
                <div>
                  <div className="font-semibold text-xs text-[var(--text-primary)] truncate">
                    {meta?.name || mId}
                  </div>
                  <span className="text-[10px] uppercase font-bold text-[var(--text-secondary)] tracking-wider">
                    {meta?.provider || "custom"}
                  </span>
                </div>

                <div className="flex items-center gap-1">
                  {res.content && (
                    <button
                      onClick={() => handleCopy(mId, res.content)}
                      className="p-1 rounded-md text-[var(--text-secondary)] hover:bg-[var(--bg-main)] hover:text-[var(--text-primary)]"
                      title="Copy response"
                    >
                      {copiedModel === mId ? <Check size={13} className="text-emerald-500" /> : <Copy size={13} />}
                    </button>
                  )}
                  {res.error && (
                    <button
                      onClick={() => onRetryModel(mId)}
                      className="p-1 rounded-md text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-950"
                      title="Retry this model"
                    >
                      <RotateCcw size={13} />
                    </button>
                  )}
                </div>
              </div>

              {/* Response Content Area */}
              <div className="flex-1 overflow-y-auto text-xs leading-relaxed text-[var(--text-primary)] whitespace-pre-wrap min-h-[140px]">
                {res.error ? (
                  <div className="flex items-start gap-1.5 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 p-2.5 rounded-xl">
                    <AlertCircle size={15} className="shrink-0 mt-0.5" />
                    <span className="break-all">{res.error}</span>
                  </div>
                ) : res.content ? (
                  res.content
                ) : isComparing ? (
                  <span className="text-[var(--text-secondary)] animate-pulse inline-flex items-center gap-1.5">
                    Streaming tokens from {meta?.provider || "provider"}...
                  </span>
                ) : (
                  <span className="text-[var(--text-secondary)] italic">Ready for comparison broadcast</span>
                )}
              </div>

              {/* Card Footer: Metrics (TTFT, Total Latency, Tokens, Tok/s) */}
              <div className="mt-3 pt-2.5 border-t border-[var(--border-subtle)]/60 grid grid-cols-3 gap-2 text-[10px] text-[var(--text-secondary)]">
                <div>
                  <span className="block text-slate-400">Latency</span>
                  <span className="font-medium text-[var(--text-primary)]">
                    {res.latency_ms ? `${Math.round(res.latency_ms)}ms` : "—"}
                  </span>
                </div>
                <div>
                  <span className="block text-slate-400">TTFT</span>
                  <span className="font-medium text-[var(--text-primary)]">
                    {res.ttft_ms ? `${Math.round(res.ttft_ms)}ms` : "—"}
                  </span>
                </div>
                <div>
                  <span className="block text-slate-400">Tokens/s</span>
                  <span className="font-medium text-[var(--text-primary)]">
                    {res.tokens_per_sec ? `${res.tokens_per_sec.toFixed(1)}/s` : "—"}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
