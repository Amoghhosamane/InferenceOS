import { ModelMetadata, Conversation, ChatMessage, MetricsSummary, StreamChunk } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  if (!res.ok) throw new Error("Backend offline");
  return res.json();
}

export async function fetchModels(): Promise<{ models: ModelMetadata[]; mock_mode: boolean; free_mode_only: boolean }> {
  const res = await fetch(`${API_BASE}/api/v1/models`);
  if (!res.ok) throw new Error("Failed to load models");
  return res.json();
}

export async function fetchMetrics(): Promise<MetricsSummary> {
  const res = await fetch(`${API_BASE}/api/v1/metrics`);
  if (!res.ok) throw new Error("Failed to load metrics");
  return res.json();
}

export async function fetchConversations(): Promise<Conversation[]> {
  const res = await fetch(`${API_BASE}/api/v1/conversations`);
  if (!res.ok) throw new Error("Failed to load conversations");
  return res.json();
}

export async function fetchConversationDetail(id: string): Promise<Conversation> {
  const res = await fetch(`${API_BASE}/api/v1/conversations/${id}`);
  if (!res.ok) throw new Error("Failed to load conversation details");
  return res.json();
}

export async function createConversation(title: string, model: string): Promise<Conversation> {
  const res = await fetch(`${API_BASE}/api/v1/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, model }),
  });
  if (!res.ok) throw new Error("Failed to create conversation");
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/v1/conversations/${id}`, { method: "DELETE" });
}

export async function streamChat(
  model: string,
  messages: ChatMessage[],
  onChunk: (chunk: StreamChunk) => void,
  onDone: () => void,
  onError: (err: string) => void,
  signal?: AbortSignal,
  allowFallback = true
) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model,
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        stream: true,
        allow_fallback: allowFallback,
      }),
      signal,
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({ detail: "Stream request failed" }));
      onError(errJson.detail || `Error HTTP ${res.status}`);
      return;
    }

    const reader = res.body?.getReader();
    if (!reader) {
      onError("Streaming response body unreadable");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          const dataStr = trimmed.slice(6).trim();
          if (dataStr === "[DONE]") {
            onDone();
            return;
          }
          try {
            const parsed: StreamChunk = JSON.parse(dataStr);
            onChunk(parsed);
          } catch (e) {
            console.error("Failed to parse stream chunk", e);
          }
        }
      }
    }
    onDone();
  } catch (err: unknown) {
    const error = err as { name?: string; message?: string };
    if (error.name === "AbortError") {
      onDone();
    } else {
      onError(error.message || "Network error");
    }
  }
}
