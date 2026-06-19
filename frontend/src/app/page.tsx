"use client";

import Link from "next/link";
import { Sparkles, MessageCircle, BookOpen, BarChart3, Heart, Shield, Brain } from "lucide-react";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { motion } from "framer-motion";

const features = [
  { icon: MessageCircle, title: "AI Conversations", desc: "Chat with Helia, your empathetic AI companion trained in mental health support." },
  { icon: Brain, title: "Emotion Detection", desc: "Advanced AI detects your emotions and sentiment in real-time during conversations." },
  { icon: BookOpen, title: "AI Journaling", desc: "Write freely and receive thoughtful AI analysis of your journal entries." },
  { icon: BarChart3, title: "Mood Analytics", desc: "Track mood trends, emotion patterns, and progress with beautiful visualizations." },
  { icon: Heart, title: "Wellness Plans", desc: "Personalized wellness recommendations based on your unique emotional patterns." },
  { icon: Shield, title: "Crisis Support", desc: "Built-in crisis detection with immediate access to professional resources." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Floating orbs background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-float" />
        <div className="absolute top-60 right-20 w-96 h-96 bg-accent/15 rounded-full blur-3xl animate-float-delayed" />
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-primary-light/10 rounded-full blur-3xl animate-float" />
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 md:px-12 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold gradient-text">Helia AI</span>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link
            href="/login"
            className="px-5 py-2 text-sm font-medium text-muted hover:text-foreground transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-primary to-accent rounded-xl hover:opacity-90 transition-opacity"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero */}
      <main className="relative z-10">
        <section className="flex flex-col items-center text-center px-6 pt-20 pb-16 md:pt-32 md:pb-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-sm mb-6">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-muted">Powered by Llama 3.1 AI</span>
            </div>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 max-w-4xl leading-tight">
              Your Intelligent{" "}
              <span className="gradient-text">Mental Well-being</span>{" "}
              Assistant
            </h1>
            <p className="text-lg md:text-xl text-muted max-w-2xl mb-10">
              Helia AI combines empathetic conversation, mood tracking, and personalized wellness plans
              to support your mental health journey — all powered by advanced AI.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="px-8 py-3.5 text-base font-semibold text-white bg-gradient-to-r from-primary to-accent rounded-xl hover:opacity-90 transition-opacity animate-pulse-glow"
              >
                Start Your Journey
              </Link>
              <Link
                href="#features"
                className="px-8 py-3.5 text-base font-semibold glass rounded-xl hover:bg-surface-hover transition-colors"
              >
                Explore Features
              </Link>
            </div>
          </motion.div>
        </section>

        {/* Features */}
        <section id="features" className="px-6 md:px-12 py-16 max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Everything you need for{" "}
              <span className="gradient-text">emotional wellness</span>
            </h2>
            <p className="text-muted text-lg max-w-2xl mx-auto">
              A comprehensive suite of AI-powered tools designed to understand, support, and empower you.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="glass rounded-2xl p-6 card-hover"
              >
                <div className="w-12 h-12 rounded-xl bg-primary/15 flex items-center justify-center mb-4">
                  <f.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 py-20 text-center">
          <div className="max-w-2xl mx-auto glass-strong rounded-3xl p-12">
            <h2 className="text-3xl font-bold mb-4">Ready to begin?</h2>
            <p className="text-muted mb-8">
              Join Helia AI today and take the first step toward better mental well-being.
            </p>
            <Link
              href="/register"
              className="inline-block px-8 py-3.5 text-base font-semibold text-white bg-gradient-to-r from-primary to-accent rounded-xl hover:opacity-90 transition-opacity"
            >
              Create Free Account
            </Link>
          </div>
        </section>

        {/* Footer */}
        <footer className="px-6 py-8 text-center text-sm text-muted border-t border-border">
          <p>⚠️ Helia AI is not a substitute for professional mental health care. If you are in crisis, please contact emergency services.</p>
          <p className="mt-2">© 2025 Helia AI. Built with care.</p>
        </footer>
      </main>
    </div>
  );
}
