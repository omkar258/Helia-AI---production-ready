"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, MessageCircle, BookOpen, Smile,
  Heart, Settings, LogOut, Menu, X, Sparkles,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { ThemeToggle } from "./ThemeToggle";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "Chat with Helia", icon: MessageCircle },
  { href: "/journal", label: "Journal", icon: BookOpen },
  { href: "/mood", label: "Mood Tracker", icon: Smile },
  { href: "/wellness", label: "Wellness", icon: Heart },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const NavContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <div>
            <h1 className="text-lg font-bold gradient-text">Helia AI</h1>
            <p className="text-xs text-muted">Well-being Assistant</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                active
                  ? "bg-primary/15 text-primary font-medium"
                  : "text-muted hover:text-foreground hover:bg-surface-hover"
              }`}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 ${active ? "text-primary" : "group-hover:text-primary"}`} />
              {!collapsed && <span className="text-sm">{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="px-3 pb-4 space-y-3">
        <ThemeToggle />
        {user && !collapsed && (
          <div className="glass rounded-xl p-3">
            <p className="text-sm font-medium truncate">{user.full_name || user.username}</p>
            <p className="text-xs text-muted truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-muted hover:text-danger transition-colors w-full cursor-pointer"
        >
          <LogOut className="w-5 h-5" />
          {!collapsed && <span className="text-sm">Logout</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden w-10 h-10 rounded-xl glass flex items-center justify-center cursor-pointer"
      >
        {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      {/* Mobile sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 glass-strong z-40 transform transition-transform lg:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <NavContent />
      </aside>

      {/* Desktop sidebar */}
      <aside
        className={`hidden lg:flex flex-col h-screen sticky top-0 glass-strong transition-all duration-300 ${
          collapsed ? "w-20" : "w-64"
        }`}
      >
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-8 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs cursor-pointer hover:scale-110 transition-transform"
        >
          {collapsed ? "→" : "←"}
        </button>
        <NavContent />
      </aside>
    </>
  );
}
