"use client";

import { useState, useEffect, useRef } from "react";
import { api } from "@/lib/api";
import type { MessageResponse, ConversationSummary, Message } from "@/types";
import { Send, Plus, Trash2, Sparkles, AlertTriangle } from "lucide-react";

export default function ChatPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getConversations().then(d => setConversations(d as ConversationSummary[])).catch(() => {});
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const loadConversation = async (id: string) => {
    setActiveId(id);
    try {
      const c = await api.getConversation(id) as { messages: Message[] };
      setMessages(c.messages || []);
    } catch { /* ignore */ }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await api.sendMessage({
        message: text,
        conversation_id: activeId || undefined,
      }) as MessageResponse;

      setMessages(prev => [...prev, { role: "assistant", content: res.ai_response }]);

      if (!activeId) {
        setActiveId(res.conversation_id);
        api.getConversations().then(d => setConversations(d as ConversationSummary[])).catch(() => {});
      }
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Sorry, I had trouble responding. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const newChat = () => {
    setActiveId(null);
    setMessages([]);
  };

  const deleteChat = async (id: string) => {
    await api.deleteConversation(id).catch(() => {});
    setConversations(prev => prev.filter(c => c.id !== id));
    if (activeId === id) newChat();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4 animate-fade-in">
      {/* Conversation list */}
      <div className="hidden md:flex flex-col w-72 glass rounded-2xl p-3 space-y-2 overflow-auto">
        <button onClick={newChat}
          className="flex items-center gap-2 px-3 py-2.5 rounded-xl bg-primary/15 text-primary text-sm font-medium hover:bg-primary/25 transition-colors cursor-pointer w-full">
          <Plus className="w-4 h-4" /> New Chat
        </button>
        <div className="flex-1 space-y-1 overflow-auto">
          {conversations.map(c => (
            <div key={c.id} className={`group flex items-center gap-2 px-3 py-2 rounded-xl text-sm cursor-pointer transition-colors ${
              activeId === c.id ? "bg-surface-hover font-medium" : "hover:bg-surface-hover"
            }`} onClick={() => loadConversation(c.id)}>
              <span className="flex-1 truncate">{c.title}</span>
              {c.crisis_flagged && <AlertTriangle className="w-3.5 h-3.5 text-danger flex-shrink-0" />}
              <button onClick={e => { e.stopPropagation(); deleteChat(c.id); }}
                className="opacity-0 group-hover:opacity-100 text-muted hover:text-danger transition-all cursor-pointer">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col glass rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-sm">Helia AI</h2>
            <p className="text-xs text-muted">Your mental well-being companion</p>
          </div>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center animate-pulse-glow">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold">Hello! I&apos;m Helia</h3>
              <p className="text-muted max-w-md text-sm">
                I&apos;m here to listen and support you. Share whatever is on your mind — 
                there&apos;s no judgment here. How are you feeling today?
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}>
              <div className={`max-w-[75%] px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === "user" ? "chat-user" : "chat-ai"
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start animate-fade-in">
              <div className="chat-ai px-4 py-3 flex gap-1">
                <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-border">
          <div className="flex gap-3 items-end">
            <textarea
              value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKeyDown}
              placeholder="Type your message..." rows={1}
              className="flex-1 resize-none px-4 py-2.5 rounded-xl bg-surface border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 max-h-32"
            />
            <button onClick={sendMessage} disabled={!input.trim() || loading}
              className="w-10 h-10 rounded-xl bg-gradient-to-r from-primary to-accent text-white flex items-center justify-center hover:opacity-90 transition-opacity disabled:opacity-50 flex-shrink-0 cursor-pointer">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
