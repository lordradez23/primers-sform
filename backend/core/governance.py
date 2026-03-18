
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Capability:
    name: str
    enabled: bool
    description: str
    version: str = "1.0"

class Governance:
    """
    PHASE 5: GOVERNANCE LAYER
    Controls what the engine is ALLOWED to do.
    """
    def __init__(self):
        # Default Safe Configuration
        self.capabilities: Dict[str, Capability] = {
            "local_llm": Capability("local_llm", True, "Connect to local LLM (e.g. llama.cpp)"),
            "persistent_memory_m2": Capability("persistent_memory_m2", True, "Read/Write to SQLite Knowledge Store"),
            "experience_tracking_m3": Capability("experience_tracking_m3", True, "Update heuristic statistics"),
            "auto_refactor": Capability("auto_refactor", False, "Automatically apply refactor plans (unsafe)"),
            "external_llm": Capability("external_llm", True, "Fallback to cloud LLM (Gemini) if local is offline"),
        }
        self.version = "3.0.0-alpha"
        self._load_env_overrides()

    def _load_env_overrides(self):
        if os.getenv("PRIMERS_ENABLE_LLM") == "1":
            self.capabilities["local_llm"].enabled = True
        if os.getenv("PRIMERS_DISABLE_M2") == "1":
            self.capabilities["persistent_memory_m2"].enabled = False

    def is_enabled(self, cap_name: str) -> bool:
        cap = self.capabilities.get(cap_name)
        return cap.enabled if cap else False

    def get_status(self) -> Dict[str, str]:
        return {k: ("ENABLED" if v.enabled else "DISABLED") for k, v in self.capabilities.items()}
