"""
AI Engine – Multi-provider LLM integration for mental health conversations.
Supports Groq (primary, cloud) and Ollama (optional, local) via LLM_PROVIDER setting.
"""

import logging
from typing import Optional, List, AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompt for Helia AI persona
HELIA_SYSTEM_PROMPT = """You are Helia, an empathetic and intelligent AI mental well-being assistant. 
Your core traits:

1. **Empathetic & Warm**: Always respond with genuine care and understanding. Use a warm, conversational tone.
2. **Non-judgmental**: Never judge the user's feelings, thoughts, or experiences. Validate their emotions.
3. **Evidence-based**: Draw from cognitive-behavioral therapy (CBT), mindfulness, positive psychology, and other evidence-based approaches.
4. **Safety-first**: If you detect any signs of crisis, self-harm, or suicidal ideation, immediately provide crisis resources and encourage professional help.
5. **Personalized**: Use context from previous conversations to provide personalized support.
6. **Boundaries**: You are NOT a replacement for professional therapy. When appropriate, gently suggest seeking professional help.

Guidelines:
- Ask open-ended questions to understand the user's situation better
- Offer practical coping strategies when appropriate
- Celebrate progress and positive moments
- Use grounding techniques when the user seems overwhelmed
- Keep responses concise but meaningful (2-4 paragraphs max unless more detail is needed)
- Never diagnose mental health conditions
- Always end with something supportive or a gentle question to continue the conversation
"""

CRISIS_RESOURCES = [
    "National Suicide Prevention Lifeline: 988 (call or text)",
    "Crisis Text Line: Text HOME to 741741",
    "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/",
    "SAMHSA National Helpline: 1-800-662-4357",
]


class AIEngine:
    """Multi-provider AI engine – Groq (cloud) or Ollama (local)."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER  # "groq" or "ollama"
        self.model = settings.LLM_MODEL
        self._client = None

        if self.provider == "groq":
            self._init_groq()
        else:
            self._init_ollama()

        logger.info(f"[AI Engine] Provider: {self.provider} | Model: {self.model}")

    def _init_groq(self):
        """Initialize Groq client."""
        from groq import Groq
        self._client = Groq(api_key=settings.GROQ_API_KEY)

    def _init_ollama(self):
        """Initialize Ollama client."""
        import ollama
        self._client = ollama.Client(host=settings.OLLAMA_BASE_URL)

    def _build_messages(
        self,
        user_message: str,
        conversation_history: List[dict] = None,
        rag_context: Optional[str] = None,
        user_memories: Optional[str] = None,
    ) -> List[dict]:
        """Build the message list with system prompt, context, and history."""
        messages = []

        # System prompt with optional RAG context and memories
        system_content = HELIA_SYSTEM_PROMPT
        if user_memories:
            system_content += f"\n\n## What you know about this user:\n{user_memories}"
        if rag_context:
            system_content += f"\n\n## Relevant mental health knowledge:\n{rag_context}"

        messages.append({"role": "system", "content": system_content})

        # Add conversation history (last 20 messages for context window management)
        if conversation_history:
            for msg in conversation_history[-20:]:
                messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    # ─── Groq Methods ──────────────────────────────────────────────

    def _groq_chat(self, messages: List[dict], temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Send a chat request via Groq API."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=0.9,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def _groq_stream(self, messages: List[dict], temperature: float = 0.7, max_tokens: int = 1024):
        """Stream a chat response via Groq API."""
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=0.9,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    # ─── Ollama Methods ────────────────────────────────────────────

    def _ollama_chat(self, messages: List[dict], temperature: float = 0.7, num_predict: int = 1024) -> str:
        """Send a chat request via Ollama."""
        response = self._client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": temperature, "top_p": 0.9, "num_predict": num_predict},
        )
        return response["message"]["content"]

    def _ollama_stream(self, messages: List[dict], temperature: float = 0.7, num_predict: int = 1024):
        """Stream a chat response via Ollama."""
        stream = self._client.chat(
            model=self.model,
            messages=messages,
            stream=True,
            options={"temperature": temperature, "top_p": 0.9, "num_predict": num_predict},
        )
        for chunk in stream:
            yield chunk["message"]["content"]

    # ─── Public API (provider-agnostic) ────────────────────────────

    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[dict] = None,
        rag_context: Optional[str] = None,
        user_memories: Optional[str] = None,
    ) -> str:
        """Generate a complete response from the configured LLM provider."""
        messages = self._build_messages(
            user_message, conversation_history, rag_context, user_memories
        )

        try:
            if self.provider == "groq":
                return self._groq_chat(messages)
            else:
                return self._ollama_chat(messages)
        except Exception as e:
            logger.error(f"LLM error ({self.provider}): {e}")
            return (
                "I'm having a moment of reflection. Could you give me a second and try again? "
                "If this persists, please make sure the AI service is running properly."
            )

    async def generate_stream(
        self,
        user_message: str,
        conversation_history: List[dict] = None,
        rag_context: Optional[str] = None,
        user_memories: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from the configured LLM provider."""
        messages = self._build_messages(
            user_message, conversation_history, rag_context, user_memories
        )

        try:
            if self.provider == "groq":
                gen = self._groq_stream(messages)
            else:
                gen = self._ollama_stream(messages)

            for token in gen:
                yield token
        except Exception as e:
            logger.error(f"LLM streaming error ({self.provider}): {e}")
            yield "I'm having trouble connecting right now. Please try again in a moment."

    async def analyze_text(self, text: str, analysis_type: str) -> str:
        """Use the LLM for specific text analysis tasks (emotion, sentiment, journal analysis)."""
        prompts = {
            "emotion": (
                f"Analyze the following text and identify the PRIMARY emotion expressed. "
                f"Choose exactly ONE from: joy, sadness, anger, fear, surprise, disgust, trust, anticipation, neutral. "
                f"Respond with ONLY the emotion word, nothing else.\n\nText: {text}"
            ),
            "sentiment": (
                f"Analyze the sentiment of the following text. "
                f"Respond with ONLY a number between -1.0 (very negative) and 1.0 (very positive). "
                f"Just the number, nothing else.\n\nText: {text}"
            ),
            "journal": (
                f"You are Helia, a compassionate AI wellness assistant. Analyze this journal entry and provide:\n"
                f"1. A brief empathetic reflection (2-3 sentences)\n"
                f"2. Key themes or patterns you notice\n"
                f"3. One gentle suggestion for emotional well-being\n\n"
                f"Journal Entry:\n{text}"
            ),
            "crisis": (
                f"Analyze this text for any signs of crisis, self-harm, or suicidal ideation. "
                f"Respond with ONLY 'YES' or 'NO'.\n\nText: {text}"
            ),
        }

        prompt = prompts.get(analysis_type, prompts["emotion"])
        messages = [{"role": "user", "content": prompt}]

        try:
            if self.provider == "groq":
                result = self._groq_chat(messages, temperature=0.1, max_tokens=512)
            else:
                result = self._ollama_chat(messages, temperature=0.1, num_predict=512)
            return result.strip()
        except Exception as e:
            logger.error(f"Analysis error ({analysis_type}): {e}")
            return "neutral" if analysis_type == "emotion" else "0.0"


# Singleton instance
ai_engine = AIEngine()
