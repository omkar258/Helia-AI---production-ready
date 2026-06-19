"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, Mail, Lock, User, Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ email: "", username: "", password: "", full_name: "" });
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (key: string, val: string) => setForm(p => ({ ...p, [key]: val }));

  const strength = (() => {
    const p = form.password;
    let s = 0;
    if (p.length >= 8) s++;
    if (/[A-Z]/.test(p)) s++;
    if (/[0-9]/.test(p)) s++;
    if (/[^A-Za-z0-9]/.test(p)) s++;
    return s;
  })();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password.length < 8) { setError("Password must be at least 8 characters"); return; }
    setLoading(true);
    try {
      await register(form.email, form.username, form.password, form.full_name || undefined);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-20 right-10 w-72 h-72 bg-accent/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 left-10 w-96 h-96 bg-primary/15 rounded-full blur-3xl animate-float-delayed" />
      </div>

      <div className="relative z-10 w-full max-w-md glass-strong rounded-3xl p-8 animate-fade-in">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold gradient-text">Join Helia AI</h1>
            <p className="text-sm text-muted">Start your wellness journey</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="full_name" className="block text-sm font-medium mb-1.5">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
              <input id="full_name" type="text" value={form.full_name} onChange={e => set("full_name", e.target.value)}
                placeholder="Jane Doe"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
            </div>
          </div>
          <div>
            <label htmlFor="username" className="block text-sm font-medium mb-1.5">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
              <input id="username" type="text" value={form.username} onChange={e => set("username", e.target.value)}
                required placeholder="janedoe" pattern="^[a-zA-Z0-9_]+$" minLength={3}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
            </div>
          </div>
          <div>
            <label htmlFor="reg-email" className="block text-sm font-medium mb-1.5">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
              <input id="reg-email" type="email" value={form.email} onChange={e => set("email", e.target.value)}
                required placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
            </div>
          </div>
          <div>
            <label htmlFor="reg-password" className="block text-sm font-medium mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
              <input id="reg-password" type={showPw ? "text" : "password"} value={form.password}
                onChange={e => set("password", e.target.value)} required placeholder="••••••••" minLength={8}
                className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted cursor-pointer">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {form.password && (
              <div className="flex gap-1 mt-2">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className={`h-1 flex-1 rounded-full transition-colors ${
                    i <= strength ? (strength <= 1 ? "bg-danger" : strength <= 2 ? "bg-warning" : "bg-success") : "bg-border"
                  }`} />
                ))}
              </div>
            )}
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-primary to-accent text-white font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50 cursor-pointer">
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Already have an account?{" "}
          <Link href="/login" className="text-primary font-medium hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
