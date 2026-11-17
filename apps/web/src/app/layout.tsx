import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InferenceOS — Free-Tier Multi-Model AI Platform",
  description: "Minimalist, Gemini-inspired unified AI gateway for Groq, Gemini, and OpenRouter free-tier models.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased">{children}</body>
    </html>
  );
}
