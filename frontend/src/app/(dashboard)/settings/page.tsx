"use client";

import { useAuth } from "@/context/AuthContext";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { User, Shield, Bell } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted text-sm mt-1">Manage your account and preferences</p>
      </div>

      {/* Profile */}
      <div className="glass rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-2">
          <User className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-semibold">Profile</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5 text-muted">Username</label>
            <div className="px-4 py-2.5 rounded-xl bg-surface border border-border text-sm">{user?.username || "—"}</div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5 text-muted">Email</label>
            <div className="px-4 py-2.5 rounded-xl bg-surface border border-border text-sm">{user?.email || "—"}</div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5 text-muted">Full Name</label>
            <div className="px-4 py-2.5 rounded-xl bg-surface border border-border text-sm">{user?.full_name || "—"}</div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5 text-muted">Member Since</label>
            <div className="px-4 py-2.5 rounded-xl bg-surface border border-border text-sm">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "—"}
            </div>
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Bell className="w-5 h-5 text-accent" />
          <h2 className="text-lg font-semibold">Appearance</h2>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Theme</p>
            <p className="text-xs text-muted">Switch between dark and light mode</p>
          </div>
          <ThemeToggle />
        </div>
      </div>

      {/* Privacy */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-5 h-5 text-success" />
          <h2 className="text-lg font-semibold">Privacy & Security</h2>
        </div>
        <ul className="space-y-3 text-sm">
          <li className="flex items-start gap-3">
            <span className="text-success mt-0.5">✓</span>
            <span>Your data is encrypted and stored securely</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-success mt-0.5">✓</span>
            <span>Conversations are private and not shared</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-success mt-0.5">✓</span>
            <span>AI processing happens locally via Ollama</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-success mt-0.5">✓</span>
            <span>JWT-based authentication with token refresh</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
