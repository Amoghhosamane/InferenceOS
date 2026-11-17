"use client";

import React, { useRef, useEffect } from "react";
import { ArrowUp, Square } from "lucide-react";

interface ComposerProps {
  input: string;
  onChange: (val: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function Composer({
  input,
  onChange,
  onSubmit,
  onStop,
  isStreaming,
  disabled,
  placeholder = "Ask InferenceOS anything...",
}: ComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea up to max height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isStreaming && input.trim()) {
        onSubmit();
      }
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-4">
      <div className="relative rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-2 shadow-sm focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          rows={1}
          className="w-full resize-none bg-transparent px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none max-h-44 min-h-[44px]"
        />

        <div className="flex items-center justify-between pt-1 px-2 border-t border-[var(--border-subtle)]/40 mt-1">
          <div className="text-[11px] text-[var(--text-secondary)]">
            <span className="hidden sm:inline">Press Enter to send, Shift + Enter for newline</span>
          </div>

          <div>
            {isStreaming ? (
              <button
                type="button"
                onClick={onStop}
                className="flex items-center justify-center w-8 h-8 rounded-full bg-red-600 text-white hover:bg-red-700 transition shadow-sm"
                title="Stop response generation"
                aria-label="Stop generation"
              >
                <Square size={13} fill="currentColor" />
              </button>
            ) : (
              <button
                type="button"
                disabled={!input.trim() || disabled}
                onClick={onSubmit}
                className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white hover:bg-blue-700 transition disabled:opacity-40 disabled:hover:bg-blue-600 shadow-sm"
                title="Send message"
                aria-label="Send message"
              >
                <ArrowUp size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
