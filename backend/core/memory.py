
from typing import Dict, List, Any, Optional

class SessionContext:
    def __init__(self):
        self.active_repo: Optional[str] = None
        self.history: List[Dict[str, Any]] = [] # Command metadata
        self.messages: List[Dict[str, str]] = [] # Full conversation history
        self.cached_graphs: Dict[str, Any] = {}
        self.confidence_trend: List[float] = []

    def update_confidence(self, score: float):
        self.confidence_trend.append(score)

    def log_command(self, step_data: Dict[str, Any]):
        self.history.append(step_data)

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Keep history manageable (last 20 messages)
        if len(self.messages) > 20:
            self.messages.pop(0)

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    def get_last_entry(self) -> Optional[Dict[str, Any]]:
        return self.history[-1] if self.history else None

