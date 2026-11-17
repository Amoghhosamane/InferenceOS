export interface ModelMetadata {
  id: string;
  name: string;
  provider: "groq" | "gemini" | "openrouter" | "inception" | "vllm" | "mock";
  free_tier: boolean;
  context_length: number;
  description: string;
  is_available: boolean;
  pricing_status: "verified_free" | "promotional_trial" | "unknown" | "paid";
}

export interface ChatMessage {
  id?: string;
  role: "system" | "user" | "assistant";
  content: string;
  model?: string;
  provider?: string;
  latency_ms?: number;
  time_to_first_token_ms?: number;
  created_at?: number;
  error?: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: number;
  updated_at: number;
  model: string;
  messages?: ChatMessage[];
}

export interface StreamChunk {
  id: string;
  model: string;
  provider: string;
  delta: {
    content?: string;
    finish_reason?: string;
  };
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
  time_to_first_token_ms?: number;
  error?: string;
  fallback_used?: boolean;
  original_model?: string;
}

export interface MetricsSummary {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p50_ttft_ms: number;
  provider_breakdown: Record<string, {
    requests: number;
    errors: number;
    avg_latency_ms: number;
  }>;
  active_mock_mode: boolean;
  sample_size: number;
  timeframe: string;
}
