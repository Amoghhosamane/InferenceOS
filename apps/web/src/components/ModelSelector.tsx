"use client";

import React, { useState } from "react";
import { ModelMetadata } from "@/lib/types";
import { ChevronDown, Sparkles, Check, Search } from "lucide-react";

interface ModelSelectorProps {
  models: ModelMetadata[];
  selectedModel: string;
  onSelectModel: (id: string) => void;
  mockMode: boolean;
  disabled?: boolean;
}

export function ModelSelector({
  models,
  selectedModel,
  onSelectModel,
  mockMode,
  disabled,
}: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filterQuery, setFilterQuery] = useState("");

  const current = models.find((m) => m.id === selectedModel) || models[0];

  const filteredModels = models.filter((m) =>
    m.name.toLowerCase().includes(filterQuery.toLowerCase()) ||
    m.provider.toLowerCase().includes(filterQuery.toLowerCase()) ||
    m.id.toLowerCase().includes(filterQuery.toLowerCase())
  );

  // Group models by provider
  const grouped = filteredModels.reduce((acc, m) => {
    acc[m.provider] = acc[m.provider] || [];
    acc[m.provider].push(m);
    return acc;
  }, {} as Record<string, ModelMetadata[]>);

  const providerLabels: Record<string, string> = {
    mock: "Deterministic Mock (Offline / Zero-Cost)",
    groq: "Groq Cloud (GPT-OSS & Qwen Free Tiers)",
    gemini: "Google Gemini (AI Studio Free Tier)",
    openrouter: "OpenRouter (Verified Free Only)",
    inception: "Inception Labs (Mercury Promotional Trial)",
    vllm: "Local vLLM Worker (Port 8001)",
  };

  return (
    <div className="relative">
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[var(--border-subtle)] bg-[var(--bg-surface)] hover:bg-[var(--bg-main)] text-xs font-medium text-[var(--text-primary)] transition shadow-xs disabled:opacity-50"
      >
        <Sparkles size={14} className="text-blue-500" />
        <span className="max-w-[150px] sm:max-w-[220px] truncate">
          {current ? current.name : "Select AI Model"}
        </span>
        <ChevronDown size={14} className="text-[var(--text-secondary)]" />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-30"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute left-0 mt-2 w-84 max-h-[420px] overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] shadow-2xl z-40 text-xs flex flex-col">
            {/* Search filter input */}
            <div className="p-2.5 border-b border-[var(--border-subtle)] bg-[var(--bg-main)]">
              <div className="relative">
                <Search size={13} className="absolute left-2.5 top-2.5 text-[var(--text-secondary)]" />
                <input
                  type="text"
                  value={filterQuery}
                  onChange={(e) => setFilterQuery(e.target.value)}
                  placeholder="Filter models or providers..."
                  className="w-full bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-lg pl-8 pr-2.5 py-1 text-xs text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>
            </div>

            {/* Scrollable Model Tree */}
            <div className="overflow-y-auto p-2 flex-1 space-y-2">
              {Object.keys(grouped).length === 0 ? (
                <div className="py-4 text-center text-xs text-[var(--text-secondary)]">
                  No models match your search.
                </div>
              ) : (
                Object.entries(grouped).map(([provider, providerModels]) => (
                  <div key={provider} className="mb-2">
                    <div className="px-2 py-1 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)]">
                      {providerLabels[provider] || provider}
                    </div>
                    {providerModels.map((m) => {
                      const isSelected = m.id === selectedModel;
                      return (
                        <button
                          key={m.id}
                          type="button"
                          disabled={!m.is_available && !mockMode}
                          onClick={() => {
                            onSelectModel(m.id);
                            setIsOpen(false);
                          }}
                          className={`w-full text-left px-2.5 py-2 rounded-xl flex items-start justify-between transition ${
                            isSelected
                              ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-950/40 dark:text-blue-300"
                              : "hover:bg-[var(--bg-main)] text-[var(--text-primary)]"
                          } ${!m.is_available && !mockMode ? "opacity-45 cursor-not-allowed" : ""}`}
                        >
                          <div className="pr-2">
                            <div className="flex items-center gap-1.5">
                              <span>{m.name}</span>
                              <span className={`text-[9px] px-1.5 py-0.2 rounded-full ${
                                m.pricing_status === "promotional_trial"
                                  ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                                  : "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                              }`}>
                                {m.pricing_status === "promotional_trial" ? "Trial Credits" : "Free"}
                              </span>
                            </div>
                            <p className="text-[11px] text-[var(--text-secondary)] line-clamp-1 mt-0.5">
                              {m.description}
                            </p>
                          </div>
                          {isSelected && (
                            <Check size={14} className="text-blue-600 mt-1 shrink-0" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
