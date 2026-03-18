import os
from typing import Optional

class SecurityGuard:
    """
    Sovereign Security Layer for Primers Intelligence.
    Enforces strict path validation and prevents command injection.
    """
    def __init__(self, safe_root: Optional[str] = None):
        # Default to the workspace root (parent of backend)
        if not safe_root:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.safe_root = os.path.abspath(os.path.join(current_dir, ".."))
        else:
            self.safe_root = os.path.abspath(safe_root)
        
        print(f"Sovereign Security Active. Safe Root: {self.safe_root}")

    def validate_path(self, target_path: str) -> str:
        """
        Ensures target_path is within the safe_root and prevents traversal.
        Returns the absolute, sanitized path.
        """
        # 1. Resolve to absolute path
        abs_target = os.path.abspath(os.path.join(self.safe_root, target_path))
        
        # 2. Check if it starts with the safe_root
        if not abs_target.startswith(self.safe_root):
            raise PermissionError(f"Security Alert: Attempted access outside safe root: {target_path}")
            
        return abs_target

    def sanitize_input(self, text: str) -> str:
        """
        Removes potentially dangerous characters or shell escapes.
        """
        # Basic sanitization: remove common shell control characters
        dangerous = [";", "&&", "||", "`", "$", "(", ")", "<", ">", "|"]
        sanitized = text
        for d in dangerous:
            sanitized = sanitized.replace(d, "")
        return sanitized.strip()
