/**
 * API Client – centralized fetch wrapper for backend communication.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      // Try refresh
      const refreshed = await this.refreshToken();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${this.getToken()}`;
        const retry = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        if (!retry.ok) throw new Error(await retry.text());
        return retry.json();
      }
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
      throw new Error("Unauthorized");
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }

    if (res.status === 204) return {} as T;
    return res.json();
  }

  private async refreshToken(): Promise<boolean> {
    const refresh = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
    if (!refresh) return false;
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // Auth
  register(data: { email: string; username: string; password: string; full_name?: string }) {
    return this.request("/auth/register", { method: "POST", body: JSON.stringify(data) });
  }

  login(data: { email: string; password: string }) {
    return this.request("/auth/login", { method: "POST", body: JSON.stringify(data) });
  }

  getMe() {
    return this.request("/auth/me");
  }

  // Chat
  sendMessage(data: { message: string; conversation_id?: string }) {
    return this.request("/chat/message", { method: "POST", body: JSON.stringify(data) });
  }

  getConversations() {
    return this.request("/chat/conversations");
  }

  getConversation(id: string) {
    return this.request(`/chat/conversations/${id}`);
  }

  deleteConversation(id: string) {
    return this.request(`/chat/conversations/${id}`, { method: "DELETE" });
  }

  // Journal
  createJournalEntry(data: { title: string; content: string; tags?: string[] }) {
    return this.request("/journal/entries", { method: "POST", body: JSON.stringify(data) });
  }

  getJournalEntries() {
    return this.request("/journal/entries");
  }

  getJournalEntry(id: string) {
    return this.request(`/journal/entries/${id}`);
  }

  updateJournalEntry(id: string, data: { title?: string; content?: string; tags?: string[] }) {
    return this.request(`/journal/entries/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  deleteJournalEntry(id: string) {
    return this.request(`/journal/entries/${id}`, { method: "DELETE" });
  }

  analyzeJournal(content: string) {
    return this.request("/journal/analyze", { method: "POST", body: JSON.stringify({ content }) });
  }

  // Mood
  logMood(data: { mood_score: number; mood_label: string; primary_emotion?: string; contributing_factors?: string[]; notes?: string }) {
    return this.request("/mood/log", { method: "POST", body: JSON.stringify(data) });
  }

  getMoodLogs() {
    return this.request("/mood/logs");
  }

  getMoodTrends(period: string = "7d") {
    return this.request(`/mood/trends?period=${period}`);
  }

  getEmotionAnalytics(period: string = "30d") {
    return this.request(`/mood/analytics?period=${period}`);
  }

  // Wellness
  getRecommendations() {
    return this.request("/wellness/recommendations");
  }

  createWellnessPlan(plan_type: string) {
    return this.request("/wellness/plans", { method: "POST", body: JSON.stringify({ plan_type }) });
  }

  getWellnessPlans() {
    return this.request("/wellness/plans");
  }

  updateWellnessPlan(id: string, data: { progress?: Record<string, unknown>; status?: string }) {
    return this.request(`/wellness/plans/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  // Dashboard
  getDashboardOverview() {
    return this.request("/dashboard/overview");
  }

  getWeeklyReport() {
    return this.request("/dashboard/weekly-report");
  }

  getProgress() {
    return this.request("/dashboard/progress");
  }
}

export const api = new ApiClient();
