"use client";

import React, { useEffect, useState } from "react";
import { MetricsSummary } from "@/lib/types";
import { fetchMetrics } from "@/lib/api";
import { X, Activity, RefreshCw } from "lucide-react";

interface MetricsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MetricsModal({ isOpen, onClose }: MetricsModalProps) {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const data = await fetchMetrics();
      setMetrics(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadMetrics();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="w-full max-w-xl rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-[var(--border-subtle)]">
          <div className="flex items-center gap-2">
            <Activity size={18} className="text-blue-600" />
            <h3 className="font-semibold text-sm text-[var(--text-primary)]">
              Observability & Real Latency Telemetry
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadMetrics}
              disabled={loading}
              className="p-1 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-main)]"
              title="Refresh telemetry"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            </button>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-main)]"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {metrics ? (
          <div className="mt-4 space-y-4">
            {/* Top Cards */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 rounded-xl bg-[var(--bg-main)] border border-[var(--border-subtle)]">
                <div className="text-[11px] text-[var(--text-secondary)]">Total Requests</div>
                <div className="text-xl font-bold text-[var(--text-primary)] mt-1">
                  {metrics.total_requests}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-[var(--bg-main)] border border-[var(--border-subtle)]">
                <div className="text-[11px] text-[var(--text-secondary)]">p50 Latency</div>
                <div className="text-xl font-bold text-blue-600 mt-1">
                  {metrics.p50_latency_ms}ms
                </div>
              </div>
              <div className="p-3 rounded-xl bg-[var(--bg-main)] border border-[var(--border-subtle)]">
                <div className="text-[11px] text-[var(--text-secondary)]">p95 Latency</div>
                <div className="text-xl font-bold text-amber-600 mt-1">
                  {metrics.p95_latency_ms}ms
                </div>
              </div>
            </div>

            {/* Provider Breakdown */}
            <div className="rounded-xl border border-[var(--border-subtle)] overflow-hidden text-xs">
              <div className="bg-[var(--bg-main)] px-3 py-2 font-semibold text-[var(--text-primary)] border-b border-[var(--border-subtle)]">
                Provider Breakdown
              </div>
              <div className="divide-y divide-[var(--border-subtle)]">
                {Object.entries(metrics.provider_breakdown).map(([prov, stats]) => (
                  <div key={prov} className="px-3 py-2 flex items-center justify-between">
                    <span className="capitalize font-medium text-[var(--text-primary)]">{prov}</span>
                    <div className="flex items-center gap-4 text-[var(--text-secondary)]">
                      <span>{stats.requests} requests</span>
                      <span>{stats.errors} errors</span>
                      <span className="font-mono">{stats.avg_latency_ms}ms avg</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="text-[11px] text-[var(--text-secondary)] flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>
                {metrics.active_mock_mode
                  ? "Operating in Deterministic Mock Mode (zero cost, synthetic latency recorded)"
                  : "Live Provider Gateway active"}
              </span>
            </div>
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-[var(--text-secondary)]">
            Loading metrics...
          </div>
        )}
      </div>
    </div>
  );
}
