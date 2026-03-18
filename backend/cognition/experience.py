
import json
import os
from typing import Dict, Any, List

EXP_FILE = "experience_m3.json"

class ExperienceMonitor:
    """
    PHASE 5: EXPERIENCE (M3)
    Statistical feedback loop. Not narrative.
    """
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.stats: Dict[str, Dict[str, Any]] = {}
        
        # Vercel fix: Use /tmp for writeable JSON
        self.exp_file = EXP_FILE
        if os.getenv("VERCEL"):
            tmp_file = os.path.join("/tmp", EXP_FILE)
            if os.path.exists(EXP_FILE) and not os.path.exists(tmp_file):
                import shutil
                try:
                    shutil.copy2(EXP_FILE, tmp_file)
                except:
                    pass
            self.exp_file = tmp_file
            
        if self.enabled:
            self._load()

    def _load(self):
        if os.path.exists(self.exp_file):
            try:
                with open(self.exp_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                self.stats = {}

    def _save(self):
        if not self.enabled: return
        try:
            with open(self.exp_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass # Silent failure on read-only environments if /tmp fails

    def log_heuristic_result(self, heuristic_name: str, confidence: float, confirmed: bool = True):
        """
        Updates statistical priors for a heuristic.
        """
        if not self.enabled: return

        if heuristic_name not in self.stats:
            self.stats[heuristic_name] = {
                "uses": 0,
                "avg_confidence": 0.0,
                "success_rate": 1.0 # Optimistic start
            }

        entry = self.stats[heuristic_name]
        n = entry["uses"]
        
        # update running avg
        new_conf = ((entry["avg_confidence"] * n) + confidence) / (n + 1)
        
        entry["uses"] += 1
        entry["avg_confidence"] = new_conf
        
        # very basic success tracking, in real v5 confirmed comes from user feedback
        if not confirmed:
             # penalize success rate
             entry["success_rate"] = ((entry["success_rate"] * n) + 0.0) / (n + 1)
        
        self._save()

    def get_calibration(self, heuristic_name: str) -> float:
        """Returns complex calibration factor based on experience."""
        if heuristic_name not in self.stats:
             return 1.0
        
        entry = self.stats[heuristic_name]
        # If confidence is historically high but success rate is low, reduce trust
        return entry["success_rate"]
