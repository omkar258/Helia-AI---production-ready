"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { Recommendation, WellnessPlan } from "@/types";
import { Heart, Plus, Clock, Target, CheckCircle } from "lucide-react";

const planTypes = ["Anxiety Management", "Stress Reduction", "Sleep Improvement", "Mindfulness", "Social Connection", "Self-Esteem"];

export default function WellnessPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [basedOn, setBasedOn] = useState("");
  const [plans, setPlans] = useState<WellnessPlan[]>([]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    api.getRecommendations().then((d: unknown) => {
      const data = d as { recommendations: Recommendation[]; based_on: string };
      setRecommendations(data.recommendations);
      setBasedOn(data.based_on);
    }).catch(() => {});
    api.getWellnessPlans().then(d => setPlans(d as WellnessPlan[])).catch(() => {});
  }, []);

  const createPlan = async (type: string) => {
    setCreating(true);
    try {
      const plan = await api.createWellnessPlan(type) as WellnessPlan;
      setPlans(prev => [plan, ...prev]);
    } catch { /* ignore */ }
    finally { setCreating(false); }
  };

  const priorityColors: Record<string, string> = {
    high: "bg-danger/15 text-danger", medium: "bg-warning/15 text-warning", low: "bg-success/15 text-success",
  };

  const categoryIcons: Record<string, string> = {
    mindfulness: "🧘", exercise: "🏃", social: "👥", sleep: "😴", nutrition: "🥗", lifestyle: "🌿",
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Wellness</h1>
        <p className="text-muted text-sm mt-1">Personalized recommendations for your well-being</p>
      </div>

      {/* Recommendations */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Today&apos;s Recommendations</h2>
          {basedOn && <span className="text-xs text-muted">Based on: {basedOn}</span>}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendations.map((rec, i) => (
            <div key={i} className="glass rounded-2xl p-5 card-hover">
              <div className="flex items-start justify-between mb-3">
                <span className="text-2xl">{categoryIcons[rec.category] || "💡"}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priorityColors[rec.priority] || ""}`}>
                  {rec.priority}
                </span>
              </div>
              <h3 className="font-semibold text-sm mb-1">{rec.title}</h3>
              <p className="text-xs text-muted mb-3">{rec.description}</p>
              {rec.estimated_duration && (
                <div className="flex items-center gap-1 text-xs text-muted">
                  <Clock className="w-3 h-3" /> {rec.estimated_duration}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Create plan */}
      <div className="glass rounded-2xl p-6 space-y-4">
        <h2 className="text-lg font-semibold">Start a Wellness Plan</h2>
        <div className="flex flex-wrap gap-2">
          {planTypes.map(type => (
            <button key={type} onClick={() => createPlan(type)} disabled={creating}
              className="flex items-center gap-2 px-4 py-2 rounded-xl glass text-sm font-medium hover:bg-surface-hover transition-colors disabled:opacity-50 cursor-pointer">
              <Plus className="w-3.5 h-3.5" /> {type}
            </button>
          ))}
        </div>
      </div>

      {/* Active plans */}
      {plans.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Your Plans</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plans.map(plan => (
              <div key={plan.id} className="glass rounded-2xl p-5 card-hover">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-sm">{plan.plan_type}</h3>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    plan.status === "active" ? "bg-success/15 text-success"
                    : plan.status === "completed" ? "bg-primary/15 text-primary"
                    : "bg-muted/15 text-muted"
                  }`}>{plan.status}</span>
                </div>
                {plan.goals.length > 0 && (
                  <div className="space-y-1.5 mb-3">
                    {plan.goals.slice(0, 3).map((goal, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs">
                        <Target className="w-3 h-3 text-accent mt-0.5 flex-shrink-0" />
                        <span className="text-muted">{String(goal)}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex items-center justify-between text-xs text-muted">
                  <span>Started {new Date(plan.start_date).toLocaleDateString()}</span>
                  {plan.status === "active" && <CheckCircle className="w-4 h-4 text-success cursor-pointer" />}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {plans.length === 0 && recommendations.length === 0 && (
        <div className="glass rounded-2xl p-12 text-center">
          <Heart className="w-12 h-12 text-muted mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Your wellness hub</h3>
          <p className="text-sm text-muted">Log mood and chat with Helia to get personalized recommendations.</p>
        </div>
      )}
    </div>
  );
}
