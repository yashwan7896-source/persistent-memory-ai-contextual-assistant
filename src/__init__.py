import sqlite3
import math
import re
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional


# =====================================================================
# 1. SEMANTIC VECTOR & TF-IDF ENGINE (FOR MEMORY RETRIEVAL)
# =====================================================================

class LightweightVectorEngine:
    """Computes TF-IDF embeddings and cosine similarity for memory retrieval."""
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple word tokenizer ignoring punctuation and case."""
        return re.findall(r'\w+', text.lower())

    @classmethod
    def compute_tf(cls, text: str) -> Dict[str, float]:
        tokens = cls.tokenize(text)
        if not tokens:
            return {}
        counts = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        return {word: count / len(tokens) for word, count in counts.items()}

    @classmethod
    def cosine_similarity(cls, text1: str, text2: str) -> float:
        tf1 = cls.compute_tf(text1)
        tf2 = cls.compute_tf(text2)
        
        all_words = set(tf1.keys()).union(set(tf2.keys()))
        if not all_words:
            return 0.0

        dot_product = sum(tf1.get(word, 0) * tf2.get(word, 0) for word in all_words)
        magnitude1 = math.sqrt(sum(val ** 2 for val in tf1.values()))
        magnitude2 = math.sqrt(sum(val ** 2 for val in tf2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


# =====================================================================
# 2. PERSISTENT MEMORY STORAGE MANAGER
# =====================================================================

class MemoryStore:
    """SQLite-backed dual memory store (Episodic & Semantic Fact Memory)."""

    def __init__(self, db_path: str = "ai_persistent_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize SQLite database schemas."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Short-Term / Conversation History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Semantic Long-Term Memories (Facts, User Preferences, Context)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    memory_key TEXT UNIQUE NOT NULL,
                    memory_value TEXT NOT NULL,
                    importance INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()

    # --- Short-Term Memory Operations ---

    def add_message(self, session_id: str, role: str, content: str):
        """Append a message to the active short-term context."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_history (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()

    def get_recent_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve the N most recent turns from short-term memory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content FROM conversation_history 
                WHERE session_id = ? 
                ORDER BY id DESC LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    # --- Long-Term Memory Operations ---

    def store_fact(self, key: str, value: str, category: str = "user_preference", importance: int = 1):
        """Upsert a fact into persistent semantic memory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO semantic_memories (category, memory_key, memory_value, importance, last_accessed)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(memory_key) DO UPDATE SET
                    memory_value = excluded.memory_value,
                    importance = excluded.importance,
                    last_accessed = CURRENT_TIMESTAMP
            """, (category, key, value, importance))
            conn.commit()

    def retrieve_relevant_memories(self, query: str, threshold: float = 0.15, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to the user query via semantic similarity."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, category, memory_key, memory_value, importance FROM semantic_memories")
            rows = cursor.fetchall()

        scored_memories = []
        for row in rows:
            mem_id, category, key, val, importance = row
            text_representation = f"{key}: {val}"
            similarity = LightweightVectorEngine.cosine_similarity(query, text_representation)
            
            if similarity >= threshold:
                scored_memories.append({
                    "id": mem_id,
                    "key": key,
                    "value": val,
                    "category": category,
                    "score": round(similarity, 3)
                })

        # Sort by score descending
        scored_memories.sort(key=lambda x: x["score"], reverse=True)
        
        # Update last_accessed timestamp for top memories
        top_memories = scored_memories[:top_k]
        if top_memories:
            top_ids = [m["id"] for m in top_memories]
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    "UPDATE semantic_memories SET last_accessed = CURRENT_TIMESTAMP WHERE id = ?",
                    [(id_,) for id_ in top_ids]
                )
                conn.commit()

        return top_memories

    def fetch_all_facts() -> List[Dict[str, str]]:
        """Retrieve all stored facts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT memory_key, memory_value, category FROM semantic_memories")
            return [{"key": r[0], "value": r[1], "category": r[2]} for r in cursor.fetchall()]

    def clear_all(self):
        """Reset short-term and long-term memory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversation_history")
            cursor.execute("DELETE FROM semantic_memories")
            conn.commit()


# =====================================================================
# 3. AI AGENT WITH PERSISTENT MEMORY ENGINE
# =====================================================================

class PersistentMemoryAIAgent:
    """AI Assistant integrating persistent long-term storage & short-term context."""

    def __init__(self, session_id: str = "default_user_session"):
        self.session_id = session_id
        self.memory = MemoryStore()

    def extract_and_store_facts(self, user_input: str):
        """Rule-based extractor simulating an auto-memory update loop."""
        patterns = [
            (r"my name is (\w+)", "user_name", "User's Name"),
            (r"i (?:like|love) ([\w\s]+)", "favorite_thing", "User Preference"),
            (r"i work as (?:a|an)?\s*([\w\s]+)", "occupation", "Occupation"),
            (r"i live in ([\w\s]+)", "location", "User Location"),
            (r"my goal is to ([\w\s]+)", "primary_goal", "User Goal")
        ]
        
        for pattern, key, category in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                self.memory.store_fact(key=key, value=value, category=category)

    def generate_llm_response(self, prompt: str, retrieved_facts: List[Dict[str, Any]], recent_history: List[Dict[str, str]]) -> str:
        """Simulates LLM response generation incorporating persistent memories."""
        
        # Check if memory answers direct questions
        lowered = prompt.lower()
        
        # Dynamic response synthesis based on facts
        if "what is my name" in lowered or "who am i" in lowered:
            for f in retrieved_facts:
                if f["key"] == "user_name":
                    return f"Your name is {f['value'].capitalize()}, based on what you told me earlier!"
            return "I don't have your name saved in my persistent memory yet. What is your name?"

        if "where do i live" in lowered or "my location" in lowered:
            for f in retrieved_facts:
                if f["key"] == "location":
                    return f"According to my long-term memory, you live in {f['value'].title()}."
            return "I don't recall where you live yet!"

        if "what do i work as" in lowered or "my job" in lowered:
            for f in retrieved_facts:
                if f["key"] == "occupation":
                    return f"You work as a {f['value']}."

        # General response synthesis with injected memory context
        facts_summary = ", ".join([f"{f['key']}: {f['value']}" for f in retrieved_facts]) if retrieved_facts else "None"
        
        return (
            f"I have received your message: '{prompt}'.\n"
            f"🧠 [Retrieved Long-Term Memories]: {facts_summary}\n"
            f"💬 [Short-Term Context Buffer]: Loaded {len(recent_history)} previous turn(s)."
        )

    def chat(self, user_input: str) -> str:
        """Main interaction pipeline."""
        # 1. Automatically extract & update persistent memories from input
        self.extract_and_store_facts(user_input)

        # 2. Retrieve relevant long-term memories using TF-IDF cosine similarity
        relevant_memories = self.memory.retrieve_relevant_memories(user_input)

        # 3. Retrieve short-term conversation context
        history = self.memory.get_recent_history(self.session_id, limit=6)

        # 4. Generate AI response
        response = self.generate_llm_response(user_input, relevant_memories, history)

        # 5. Save turn to short-term persistent storage
        self.memory.add_message(self.session_id, "user", user_input)
        self.memory.add_message(self.session_id, "assistant", response)

        return response


# =====================================================================
# 4. INTERACTIVE DEMO LOOP
# =====================================================================

def run_persistent_memory_demo():
    print("=" * 65)
    print("  PERSISTENT MEMORY AI AGENT DEMO (SQLite + Semantic Vector)  ")
    print("=" * 65)
    print("Commands:")
    print("  - Type any message to interact.")
    print("  - '/facts' to view all long-term stored memories.")
    print("  - '/clear' to purge database.")
    print("  - 'exit' to quit.\n")

    agent = PersistentMemoryAIAgent(session_id="user_demo_session")

    # Seed initial test facts
    agent.memory.store_fact("user_name", "Alex", "User Profile")
    agent.memory.store_fact("location", "San Francisco", "User Profile")
    agent.memory.store_fact("occupation", "Software Engineer", "User Profile")

    while True:
        try:
            user_input = input("\nUser > ").strip()
            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Exiting. Long-term memory persists in SQLite database!")
                break

            if user_input.lower() == "/facts":
                facts = agent.memory.fetch_all_facts()
                print("\n--- Current Long-Term Stored Facts ---")
                for f in facts:
                    print(f" • [{f['category']}] {f['key']}: {f['value']}")
                continue

            if user_input.lower() == "/clear":
                agent.memory.clear_all()
                print("All persistent memories wiped.")
                continue

            # Process query
            reply = agent.chat(user_input)
            print(f"\nAI > {reply}")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    run_persistent_memory_demo()
