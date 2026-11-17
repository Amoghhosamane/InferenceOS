"use client";

import React from "react";
import { ModelMetadata } from "@/lib/types";
import { Clock, AlertCircle, Check } from "lucide-react";

interface CompareViewProps {
  models: ModelMetadata[];
  selectedModels: string[];
  onToggleModel: (id: string) => void;
  prompt: string;
  onPromptChange: (val: string) => void;
  onRunCompare: () => void;
  isComparing: boolean;
  results: Record<string, {
    content: string;
    latency_ms?: number;
    ttft_ms?: number;
    error?: string;
  }>;
}

export function CompareView({
  models,
  selectedModels,
  onToggleModel,
  prompt,
  onPromptChange,
  onRunCompare,
  isComparing,
  results,
}: CompareViewProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 max-w-5xl mx-auto w-full flex flex-col">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">
          Side-by-Side Model Comparison
        </h2>
        <p className="text-xs text-[var(--text-secondary)] mt-0.5">
          Send the identical prompt simultaneously to 2 or 3 verified free-tier models to measure latency and output variation.
        </p>
      </div>

      {/* Model Selection Checkboxes */}
      <div className="mb-4 flex flex-wrap gap-2">
        {models.map((m) => {
          const isSelected = selectedModels.includes(m.id);
          return (
            <button
              key={m.id}
              type="button"
              onClick={() => onToggleModel(m.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition flex items-center gap-1.5 ${
                isSelected
                  ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                  : "bg-[var(--bg-surface)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:bg-[var(--bg-main)]"
              }`}
            >
              {isSelected && <Check size={12} />}
              <span>{m.name}</span>
            </button>
          );
        })}
      </div>

      {/* Prompt Composer */}
      <div className="mb-6 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-3 shadow-sm">
        <textarea
          value={prompt}
          onChange={(e) => onPromptChange(e.target.value)}
          placeholder="Enter a prompt to compare models simultaneously..."
          rows={3}
          className="w-full resize-none bg-transparent text-sm text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none"
        />
        <div className="flex justify-end pt-2 border-t border-[var(--border-subtle)]/60">
          <button
            type="button"
            disabled={isComparing || selectedModels.length < 2 || !prompt.trim()}
            onClick={onRunCompare}
            className="px-4 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-medium hover:bg-blue-700 transition disabled:opacity-40"
          >
            {isComparing ? "Running Comparison..." : `Compare (${selectedModels.length} models)`}
          </button>
        </div>
      </div>

      {/* Side-by-side Response Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 flex-1">
        {selectedModels.map((mId) => {
          const meta = models.find((m) => m.id === mId);
          const res = results[mId] || { content: "" };

          return (
            <div
              key={mId}
              className="flex flex-col rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 shadow-sm"
            >
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border-subtle)]/60 mb-3">
                <div className="font-medium text-xs text-[var(--text-primary)] truncate">
                  {meta?.name || mId}
                </div>
                <span className="text-[10px] uppercase font-semibold text-[var(--text-secondary)]">
                  {meta?.provider}
                </span>
              </div>

              <div className="flex-1 overflow-y-auto text-xs leading-relaxed text-[var(--text-primary)] whitespace-pre-wrap">
                {res.error ? (
                  <div className="flex items-center gap-1.5 text-red-500 font-medium">
                    <AlertCircle size={14} />
                    <span>{res.error}</span>
                  </div>
                ) : res.content ? (
                  res.content
                ) : isComparing ? (
                  <span className="text-[var(--text-secondary)] animate-pulse">Waiting for stream...</span>
                ) : (
                  <span className="text-[var(--text-secondary)] italic">Run comparison to see output</span>
                )}
              </div>

              <div className="mt-3 pt-2 border-t border-[var(--border-subtle)]/60 flex items-center justify-between text-[11px] text-[var(--text-secondary)]">
                {res.latency_ms ? (
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    {Math.round(res.latency_ms)}ms
                  </span>
                ) : (
                  <span>--</span>
                )}
                {res.ttft_ms && (
                  <span>TTFT: {Math.round(res.ttft_ms)}ms</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
