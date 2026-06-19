"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { DashboardOverview, MoodTrends, WeeklyReport as WeeklyReportType } from "@/types";
import {
  MessageCircle, BookOpen, Smile, Heart, TrendingUp,
  TrendingDown, Minus, Flame, BarChart3,
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
} from "recharts";

export default function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [trends, setTrends] = useState<MoodTrends | null>(null);
  const [report, setReport] = useState<WeeklyReportType | null>(null);

  useEffect(() => {
    api.getDashboardOverview().then(d => setOverview(d as DashboardOverview)).catch(() => {});
    api.getMoodTrends("30d").then(d => setTrends(d as MoodTrends)).catch(() => {});
    api.getWeeklyReport().then(d => setReport(d as WeeklyReportType)).catch(() => {});
  }, []);

  const TrendIcon = overview?.recent_mood_trend === "improving" ? TrendingUp
    : overview?.recent_mood_trend === "declining" ? TrendingDown : Minus;
  const trendColor = overview?.recent_mood_trend === "improving" ? "text-success"
    : overview?.recent_mood_trend === "declining" ? "text-danger" : "text-warning";

  const stats = overview ? [
    { label: "Conversations", value: overview.total_conversations, icon: MessageCircle, color: "text-primary" },
    { label: "Journal Entries", value: overview.total_journal_entries, icon: BookOpen, color: "text-accent" },
    { label: "Mood Logs", value: overview.total_mood_logs, icon: Smile, color: "text-warning" },
    { label: "Wellness Plans", value: overview.active_wellness_plans, icon: Heart, color: "text-danger" },
  ] : [];

  // Radar chart data from report
  const radarData = report?.emotion_breakdown
    ? Object.entries(report.emotion_breakdown).map(([emotion, count]) => ({ emotion, value: count }))
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted text-sm mt-1">Your mental wellness at a glance</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(s => (
          <div key={s.label} className="glass rounded-2xl p-4 card-hover">
            <div className="flex items-center justify-between mb-3">
              <s.icon className={`w-5 h-5 ${s.color}`} />
              <span className="text-2xl font-bold">{s.value}</span>
            </div>
            <p className="text-sm text-muted">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Streak + Trend row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass rounded-2xl p-6 flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-warning/15 flex items-center justify-center">
            <Flame className="w-7 h-7 text-warning" />
          </div>
          <div>
            <p className="text-3xl font-bold">{overview?.current_streak || 0}</p>
            <p className="text-sm text-muted">Day Streak</p>
          </div>
        </div>
        <div className="glass rounded-2xl p-6 flex items-center gap-4">
          <div className={`w-14 h-14 rounded-2xl bg-primary/15 flex items-center justify-center`}>
            <TrendIcon className={`w-7 h-7 ${trendColor}`} />
          </div>
          <div>
            <p className="text-lg font-bold capitalize">{overview?.recent_mood_trend || "—"}</p>
            <p className="text-sm text-muted">Mood Trend</p>
          </div>
        </div>
        <div className="glass rounded-2xl p-6 flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-accent/15 flex items-center justify-center">
            <BarChart3 className="w-7 h-7 text-accent" />
          </div>
          <div>
            <p className="text-3xl font-bold">{overview?.avg_mood_7d?.toFixed(1) || "—"}</p>
            <p className="text-sm text-muted">Avg Mood (7d)</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mood trend chart */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4">Mood Trends (30 days)</h3>
          {trends && trends.trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={trends.trends}>
                <defs>
                  <linearGradient id="moodGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#7c3aed" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={v => v.slice(5)} stroke="var(--muted)" />
                <YAxis domain={[0, 10]} tick={{ fontSize: 11 }} stroke="var(--muted)" />
                <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border-color)", borderRadius: "12px", fontSize: "13px" }} />
                <Area type="monotone" dataKey="avg_score" stroke="#7c3aed" fill="url(#moodGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-muted text-sm">
              Log your mood to see trends here
            </div>
          )}
        </div>

        {/* Emotion radar */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4">Emotion Distribution</h3>
          {radarData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="var(--border-color)" />
                <PolarAngleAxis dataKey="emotion" tick={{ fontSize: 11 }} stroke="var(--muted)" />
                <Radar dataKey="value" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-muted text-sm">
              Chat with Helia to see emotion analytics
            </div>
          )}
        </div>
      </div>

      {/* Weekly insights */}
      {report && (
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4">Weekly Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-muted mb-2">Key Insights</h4>
              <ul className="space-y-2">
                {report.key_insights.map((insight, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-primary mt-0.5">✦</span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-muted mb-2">AI Recommendations</h4>
              <ul className="space-y-2">
                {report.ai_recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-accent mt-0.5">→</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
