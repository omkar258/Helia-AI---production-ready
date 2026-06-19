"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { MoodLog, MoodTrends } from "@/types";
import { Smile } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const moods = [
  { score: 1, emoji: "😢", label: "Terrible" },
  { score: 2, emoji: "😞", label: "Bad" },
  { score: 3, emoji: "😕", label: "Poor" },
  { score: 4, emoji: "😐", label: "Meh" },
  { score: 5, emoji: "🙂", label: "Okay" },
  { score: 6, emoji: "😊", label: "Good" },
  { score: 7, emoji: "😄", label: "Great" },
  { score: 8, emoji: "😁", label: "Very Good" },
  { score: 9, emoji: "🤩", label: "Amazing" },
  { score: 10, emoji: "🥳", label: "Fantastic" },
];

const emotions = ["joy", "sadness", "anger", "fear", "surprise", "neutral", "trust", "anticipation"];
const factors = ["Work", "Sleep", "Exercise", "Social", "Weather", "Health", "Family", "Finance"];

export default function MoodPage() {
  const [logs, setLogs] = useState<MoodLog[]>([]);
  const [trends, setTrends] = useState<MoodTrends | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [emotion, setEmotion] = useState("");
  const [selFactors, setSelFactors] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getMoodLogs().then(d => setLogs(d as MoodLog[])).catch(() => {});
    api.getMoodTrends("30d").then(d => setTrends(d as MoodTrends)).catch(() => {});
  }, []);

  const toggleFactor = (f: string) =>
    setSelFactors(prev => prev.includes(f) ? prev.filter(x => x !== f) : [...prev, f]);

  const logMood = async () => {
    if (selected === null) return;
    setSaving(true);
    const m = moods.find(m => m.score === selected)!;
    try {
      const log = await api.logMood({
        mood_score: selected, mood_label: m.label.toLowerCase(),
        primary_emotion: emotion || undefined,
        contributing_factors: selFactors, notes: notes || undefined,
      }) as MoodLog;
      setLogs(prev => [log, ...prev]);
      setSelected(null); setEmotion(""); setSelFactors([]); setNotes("");
      api.getMoodTrends("30d").then(d => setTrends(d as MoodTrends)).catch(() => {});
    } catch { /* ignore */ }
    finally { setSaving(false); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Mood Tracker</h1>
        <p className="text-muted text-sm mt-1">How are you feeling right now?</p>
      </div>

      {/* Mood selector */}
      <div className="glass rounded-2xl p-6 space-y-5">
        <h3 className="font-semibold">Rate Your Mood</h3>
        <div className="flex flex-wrap gap-2 justify-center">
          {moods.map(m => (
            <button key={m.score} onClick={() => setSelected(m.score)}
              className={`flex flex-col items-center gap-1 p-3 rounded-xl transition-all cursor-pointer ${
                selected === m.score ? "bg-primary/20 scale-110 ring-2 ring-primary" : "hover:bg-surface-hover"
              }`}>
              <span className="text-2xl">{m.emoji}</span>
              <span className="text-xs text-muted">{m.label}</span>
            </button>
          ))}
        </div>

        {selected && (
          <div className="space-y-4 animate-fade-in">
            <div>
              <label className="text-sm font-medium mb-2 block">Primary Emotion</label>
              <div className="flex flex-wrap gap-2">
                {emotions.map(e => (
                  <button key={e} onClick={() => setEmotion(e)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors cursor-pointer ${
                      emotion === e ? "bg-primary text-white" : "glass hover:bg-surface-hover"
                    }`}>{e}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Contributing Factors</label>
              <div className="flex flex-wrap gap-2">
                {factors.map(f => (
                  <button key={f} onClick={() => toggleFactor(f)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors cursor-pointer ${
                      selFactors.includes(f) ? "bg-accent text-white" : "glass hover:bg-surface-hover"
                    }`}>{f}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Notes (optional)</label>
              <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} placeholder="What's on your mind?"
                className="w-full px-4 py-2.5 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none" />
            </div>
            <button onClick={logMood} disabled={saving}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-primary to-accent text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 cursor-pointer">
              {saving ? "Logging..." : "Log Mood"}
            </button>
          </div>
        )}
      </div>

      {/* Trend chart */}
      <div className="glass rounded-2xl p-6">
        <h3 className="font-semibold mb-4">Mood Trends (30 days)</h3>
        {trends && trends.trends.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={trends.trends}>
              <defs>
                <linearGradient id="moodG" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#7c3aed" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={v => v.slice(5)} stroke="var(--muted)" />
              <YAxis domain={[0, 10]} tick={{ fontSize: 11 }} stroke="var(--muted)" />
              <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border-color)", borderRadius: "12px", fontSize: "13px" }} />
              <Area type="monotone" dataKey="avg_score" stroke="#7c3aed" fill="url(#moodG)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[200px] flex items-center justify-center text-muted text-sm">
            <Smile className="w-5 h-5 mr-2" /> Log your mood daily to see trends
          </div>
        )}
      </div>

      {/* Recent logs */}
      {logs.length > 0 && (
        <div className="glass rounded-2xl p-6">
          <h3 className="font-semibold mb-4">Recent Logs</h3>
          <div className="space-y-2">
            {logs.slice(0, 10).map(log => {
              const m = moods.find(m => m.score === log.mood_score);
              return (
                <div key={log.id} className="flex items-center gap-4 px-4 py-3 rounded-xl bg-surface/50">
                  <span className="text-2xl">{m?.emoji || "🙂"}</span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{m?.label || log.mood_label} · {log.primary_emotion || ""}</p>
                    {log.notes && <p className="text-xs text-muted truncate">{log.notes}</p>}
                  </div>
                  <span className="text-xs text-muted">{new Date(log.logged_at).toLocaleDateString()}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
