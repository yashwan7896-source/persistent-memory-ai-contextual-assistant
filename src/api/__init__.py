import sqlite3
import re
import time
from datetime import datetime


class Memory:
    """Handles persistent long-term facts and short-term chat logs in SQLite."""

    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._setup()

    def _setup(self):
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    category TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def save_chat(self, session_id: str, role: str, content: str):
        with self.conn:
            self.conn.execute(
                "INSERT INTO history (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def get_recent_chats(self, session_id: str, limit: int = 6):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT role, content FROM history 
            WHERE session_id = ? 
            ORDER BY id DESC LIMIT ?
            """,
            (session_id, limit),
        )
        # Reverse so they stay in chronological order
        return [dict(row) for row in reversed(cur.fetchall())]

    def set_fact(self, key: str, value: str, category: str = "general"):
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO facts (key, value, category, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value, category),
            )

    def get_relevant_facts(self, query: str):
        """Simple lexical match to pull relevant stored facts based on word overlap."""
        tokens = set(re.findall(r'\w+', query.lower()))
        if not tokens:
            return []

        cur = self.conn.cursor()
        cur.execute("SELECT key, value, category FROM facts")
        facts = [dict(row) for row in cur.fetchall()]

        matched = []
        for fact in facts:
            fact_tokens = set(re.findall(r'\w+', f"{fact['key']} {fact['value']}".lower()))
            overlap = len(tokens & fact_tokens)
            if overlap > 0:
                matched.append((overlap, fact))

        # Return facts sorted by most token matches
        matched.sort(key=lambda x: x[0], reverse=True)
        return [f[1] for f in matched[:3]]

    def all_facts(self):
        cur = self.conn.cursor()
        cur.execute("SELECT key, value, category FROM facts ORDER BY key")
        return [dict(row) for row in cur.fetchall()]


class Agent:
    def __init__(self, session_id="user_main"):
        self.session_id = session_id
        self.memory = Memory()

    def _extract_facts(self, text: str):
        """Extract basic user attributes from direct statements."""
        rules = [
            (r"my name is (\w+)", "name", "profile"),
            (r"i live in ([\w\s]+)", "location", "profile"),
            (r"i work as (?:a|an)?\s*([\w\s]+)", "job", "profile"),
            (r"i (?:like|love) ([\w\s]+)", "preference", "interest"),
        ]

        for pattern, key, category in rules:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                self.memory.set_fact(key, val, category)

    def ask(self, user_text: str) -> str:
        # 1. Update long-term facts automatically if present
        self._extract_facts(user_text)

        # 2. Fetch context
        history = self.memory.get_recent_chats(self.session_id)
        facts = self.memory.get_relevant_facts(user_text)

        # 3. Formulate response (Replace this logic block with actual LLM API call)
        response = self._respond(user_text, facts, history)

        # 4. Save interaction to short-term history
        self.memory.save_chat(self.session_id, "user", user_text)
        self.memory.save_chat(self.session_id, "assistant", response)

        return response

    def _respond(self, query: str, facts: list, history: list) -> str:
        q = query.lower()

        # Handle direct recall questions
        if "name" in q:
            for f in facts:
                if f["key"] == "name":
                    return f"You told me earlier your name is {f['value'].capitalize()}."
        if "where" in q and "live" in q:
            for f in facts:
                if f["key"] == "location":
                    return f"From what I remember, you live in {f['value'].title()}."

        # Default conversational fallthrough
        if facts:
            fact_str = ", ".join(f"{f['key']}={f['value']}" for f in facts)
            return f"Got it. (Context pulled: {fact_str})"

        return f"Understood. Noted '{query}' in chat history."


def main():
    agent = Agent()
    
    # Pre-seed some default memory
    agent.memory.set_fact("name", "David", "profile")
    agent.memory.set_fact("location", "Seattle", "profile")

    print("Agent ready. Type '/facts' to inspect memory, or 'exit' to quit.\n")

    while True:
        try:
            text = input("> ").strip()
            if not text:
                continue

            if text in ("exit", "quit"):
                break

            if text == "/facts":
                print("\nStored Facts:")
                for f in agent.memory.all_facts():
                    print(f"  - {f['key']}: {f['value']} ({f['category']})")
                print()
                continue

            reply = agent.ask(text)
            print(f"Bot: {reply}\n")

        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
