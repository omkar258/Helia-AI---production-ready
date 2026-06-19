/**
 * Helia AI – TypeScript Type Definitions
 */

// --- Auth ---
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  preferences: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// --- Chat ---
export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface MessageResponse {
  conversation_id: string;
  user_message: string;
  ai_response: string;
  detected_emotion?: string;
  sentiment_score?: number;
  crisis_detected: boolean;
  crisis_resources?: string[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  detected_emotion?: string;
  sentiment_score?: number;
  crisis_flagged: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail extends ConversationSummary {
  messages: Message[];
  summary?: string;
}

// --- Journal ---
export interface JournalEntry {
  id: string;
  title: string;
  content: string;
  ai_analysis?: string;
  mood_tag?: string;
  detected_emotion?: string;
  sentiment_score?: number;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface JournalAnalysis {
  analysis: string;
  detected_emotion: string;
  mood_tag: string;
  sentiment_score: number;
  suggestions: string[];
}

// --- Mood ---
export interface MoodLog {
  id: string;
  mood_score: number;
  mood_label: string;
  primary_emotion?: string;
  contributing_factors: string[];
  notes?: string;
  logged_at: string;
}

export interface MoodTrendPoint {
  date: string;
  avg_score: number;
  dominant_emotion?: string;
  log_count: number;
}

export interface MoodTrends {
  period: string;
  trends: MoodTrendPoint[];
  overall_average: number;
  mood_distribution: Record<string, number>;
}

export interface EmotionAnalytics {
  emotions: Record<string, number>;
  top_factors: string[];
  total_logs: number;
  period: string;
}

// --- Wellness ---
export interface Recommendation {
  category: string;
  title: string;
  description: string;
  priority: string;
  estimated_duration?: string;
}

export interface WellnessPlan {
  id: string;
  plan_type: string;
  recommendations: string[];
  goals: string[];
  progress: Record<string, unknown>;
  status: string;
  start_date: string;
  end_date?: string;
  created_at: string;
}

// --- Dashboard ---
export interface DashboardOverview {
  total_conversations: number;
  total_journal_entries: number;
  total_mood_logs: number;
  current_streak: number;
  avg_mood_7d?: number;
  avg_mood_30d?: number;
  dominant_emotion?: string;
  active_wellness_plans: number;
  recent_mood_trend: string;
}

export interface WeeklyReport {
  week_start: string;
  week_end: string;
  mood_summary: Record<string, unknown>;
  emotion_breakdown: Record<string, number>;
  conversations_count: number;
  journal_entries_count: number;
  key_insights: string[];
  ai_recommendations: string[];
}
