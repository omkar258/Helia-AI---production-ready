"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { JournalEntry, JournalAnalysis } from "@/types";
import { Plus, BookOpen, Sparkles, Trash2, X } from "lucide-react";

export default function JournalPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [showEditor, setShowEditor] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [analysis, setAnalysis] = useState<JournalAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getJournalEntries().then(d => setEntries(d as JournalEntry[])).catch(() => {});
  }, []);

  const save = async () => {
    if (!content.trim()) return;
    setSaving(true);
    try {
      const entry = await api.createJournalEntry({ title: title || "Untitled Entry", content }) as JournalEntry;
      setEntries(prev => [entry, ...prev]);
      setShowEditor(false);
      setTitle(""); setContent(""); setAnalysis(null);
    } catch { /* ignore */ }
    finally { setSaving(false); }
  };

  const analyze = async () => {
    if (!content.trim() || content.length < 10) return;
    setAnalyzing(true);
    try {
      const res = await api.analyzeJournal(content) as JournalAnalysis;
      setAnalysis(res);
    } catch { /* ignore */ }
    finally { setAnalyzing(false); }
  };

  const deleteEntry = async (id: string) => {
    await api.deleteJournalEntry(id).catch(() => {});
    setEntries(prev => prev.filter(e => e.id !== id));
  };

  const emotionColors: Record<string, string> = {
    joy: "bg-success/15 text-success", sadness: "bg-blue-500/15 text-blue-500",
    anger: "bg-danger/15 text-danger", fear: "bg-warning/15 text-warning",
    neutral: "bg-muted/15 text-muted", surprise: "bg-primary/15 text-primary",
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Journal</h1>
          <p className="text-muted text-sm mt-1">Express yourself freely with AI-powered insights</p>
        </div>
        <button onClick={() => setShowEditor(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-primary to-accent text-white text-sm font-medium hover:opacity-90 transition-opacity cursor-pointer">
          <Plus className="w-4 h-4" /> New Entry
        </button>
      </div>

      {/* Editor modal */}
      {showEditor && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setShowEditor(false)}>
          <div className="w-full max-w-2xl glass-strong rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">New Journal Entry</h2>
              <button onClick={() => setShowEditor(false)} className="text-muted hover:text-foreground cursor-pointer"><X className="w-5 h-5" /></button>
            </div>
            <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Entry title (optional)"
              className="w-full px-4 py-2.5 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
            <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Write your thoughts here..."
              rows={8} className="w-full px-4 py-3 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none" />

            {analysis && (
              <div className="glass rounded-xl p-4 space-y-2">
                <h3 className="text-sm font-semibold flex items-center gap-2"><Sparkles className="w-4 h-4 text-primary" /> AI Analysis</h3>
                <p className="text-sm">{analysis.analysis}</p>
                <div className="flex gap-2 flex-wrap">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${emotionColors[analysis.detected_emotion] || "bg-muted/15 text-muted"}`}>
                    {analysis.detected_emotion}
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary/15 text-primary">{analysis.mood_tag}</span>
                </div>
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <button onClick={analyze} disabled={analyzing || content.length < 10}
                className="flex items-center gap-2 px-4 py-2 rounded-xl glass text-sm font-medium hover:bg-surface-hover transition-colors disabled:opacity-50 cursor-pointer">
                <Sparkles className="w-4 h-4" /> {analyzing ? "Analyzing..." : "AI Analyze"}
              </button>
              <button onClick={save} disabled={saving || !content.trim()}
                className="px-6 py-2 rounded-xl bg-gradient-to-r from-primary to-accent text-white text-sm font-medium hover:opacity-90 disabled:opacity-50 cursor-pointer">
                {saving ? "Saving..." : "Save Entry"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Entries list */}
      {entries.length === 0 ? (
        <div className="glass rounded-2xl p-12 text-center">
          <BookOpen className="w-12 h-12 text-muted mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No journal entries yet</h3>
          <p className="text-sm text-muted">Start writing to discover patterns in your thoughts and emotions.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {entries.map(entry => (
            <div key={entry.id} className="glass rounded-2xl p-5 card-hover group">
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-sm">{entry.title}</h3>
                <button onClick={() => deleteEntry(entry.id)}
                  className="opacity-0 group-hover:opacity-100 text-muted hover:text-danger transition-all cursor-pointer">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-muted line-clamp-3 mb-3">{entry.content}</p>
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  {entry.detected_emotion && (
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${emotionColors[entry.detected_emotion] || "bg-muted/15 text-muted"}`}>
                      {entry.detected_emotion}
                    </span>
                  )}
                </div>
                <span className="text-xs text-muted">{new Date(entry.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
