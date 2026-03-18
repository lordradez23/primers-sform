
import sqlite3
import json
import hashlib
import os
from typing import Dict, Optional, Any, List
from datetime import datetime

class KnowledgeStore:
    def __init__(self, db_path: str = "primers_knowledge.db", enabled: bool = True):
        self.enabled = enabled
        
        # Vercel fix: Use /tmp for writeable database
        if os.getenv("VERCEL"):
            import shutil
            tmp_path = os.path.join("/tmp", db_path)
            # Copy existing DB to /tmp if it exists in the repo
            if os.path.exists(db_path) and not os.path.exists(tmp_path):
                try:
                    shutil.copy2(db_path, tmp_path)
                except:
                    pass
            self.db_path = tmp_path
        else:
            # Fixed location in backend directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, db_path)
            
        if enabled:
            self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # M2 Schema: Strictly Factual
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repo_analysis (
                    repo_hash TEXT PRIMARY KEY,
                    source_name TEXT,
                    files_count INTEGER,
                    avg_complexity REAL,
                    last_analyzed TEXT,
                    analysis_blob TEXT
                )
            """)
            # M2 History: Time-series debt tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT,
                    timestamp TEXT,
                    loc INTEGER,
                    complexity REAL,
                    health_score INTEGER
                )
            """)
            # M2 Interactions: Self-Learning from User input
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    response TEXT,
                    timestamp TEXT,
                    confidence REAL
                )
            """)
            # M2 Monitoring: V4 Risk Tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    timestamp TEXT,
                    s_score REAL,
                    v_score REAL,
                    k_score REAL,
                    c_score REAL,
                    total_risk REAL,
                    classification TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    timestamp TEXT,
                    metadata TEXT
                )
            """)
            # M2 Commercial: Real-world value scaling
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commercial_metrics (
                    metric_id TEXT PRIMARY KEY,
                    value REAL
                )
            """)
            # M2 Graph: Sovereign Topology
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    target TEXT,
                    type TEXT,
                    strength REAL,
                    UNIQUE(source, target, type)
                )
            """)
            cursor.execute("INSERT OR IGNORE INTO commercial_metrics (metric_id, value) VALUES ('total_debt_repaid', 0.0)")
            conn.commit()

    def save_interaction(self, query: str, response: str, confidence: float):
        if not self.enabled: return
        timestamp = datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO interactions (query, response, timestamp, confidence)
                    VALUES (?, ?, ?, ?)
                """, (query, response, timestamp, confidence))
                conn.commit()
        except Exception as e:
            print(f"Failed to save interaction: {e}")

    def search_interactions(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        if not self.enabled: return []
        results = []
        words = [w for w in query.lower().split() if len(w) >= 3]
        if not words: return []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for word in words:
                    cursor.execute("""
                        SELECT query, response, confidence FROM interactions 
                        WHERE query LIKE ? AND confidence > 0.5
                        ORDER BY confidence DESC LIMIT ?
                    """, (f"%{word}%", limit))
                    for row in cursor.fetchall():
                        results.append({"query": row[0], "response": row[1], "confidence": row[2]})
                    if len(results) >= limit: break
        except Exception as e:
            print(f"Failed to search interactions: {e}")
        return results

    def save_analysis(self, source: str, metrics: Dict[str, Any]):
        if not self.enabled: return

        # Create deterministic ID from source name (or file content hash in real world)
        repo_hash = hashlib.sha256(source.encode()).hexdigest()
        blob = json.dumps(metrics)
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO repo_analysis 
                (repo_hash, source_name, files_count, avg_complexity, last_analyzed, analysis_blob)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (repo_hash, source, metrics.get('files', 1), metrics.get('complexity', 0), timestamp, blob))
            
            # Record historical snapshot
            cursor.execute("""
                INSERT INTO analysis_history (source_name, timestamp, loc, complexity, health_score)
                VALUES (?, ?, ?, ?, ?)
            """, (source, timestamp, metrics.get('loc', 0), metrics.get('complexity', 0), metrics.get('health_score', 100)))
            conn.commit()

    def get_history(self, source_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.enabled: return []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, loc, complexity, health_score FROM analysis_history WHERE source_name = ? ORDER BY timestamp DESC LIMIT ?", (source_name, limit))
            return [{"timestamp": r[0], "loc": r[1], "complexity": r[2], "health_score": r[3]} for r in cursor.fetchall()]

    def get_baseline(self, source_name: str) -> Optional[Dict[str, Any]]:
        if not self.enabled: return None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT analysis_blob FROM repo_analysis WHERE source_name = ?", (source_name,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def search_entities(self, query: str, limit: int = 3) -> List[str]:
        """
        Keyword-based retrieval from M2. Optimized to use SQL filters.
        """
        if not self.enabled: return []
        
        results = []
        words = [w for w in query.lower().split() if len(w) > 2] # Filter short noise words
        if not words: return []

        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                # 1. Search by source_name (file paths)
                for word in words:
                    cursor.execute(
                        "SELECT source_name, analysis_blob FROM repo_analysis WHERE source_name LIKE ? LIMIT ?", 
                        (f"%{word}%", limit)
                    )
                    for row in cursor.fetchall():
                        source, blob_str = row
                        results.append(f"Entity: {source} | Stats: {blob_str[:150]}...")
                        if len(results) >= limit: break
                    if len(results) >= limit: break
                
                # 2. Search by content (simplified) if still need more results
                if len(results) < limit:
                    for word in words:
                        cursor.execute(
                            "SELECT source_name, analysis_blob FROM repo_analysis WHERE analysis_blob LIKE ? LIMIT ?", 
                            (f"%{word}%", limit - len(results))
                        )
                        for row in cursor.fetchall():
                            source, _ = row
                            results.append(f"Context Match: Reference found in {source}")
                            if len(results) >= limit: break
                        if len(results) >= limit: break
        except Exception as e:
            print(f"Search Entities Error: {e}")
            
        return results
    def get_all_analyses(self) -> Dict[str, Any]:
        if not self.enabled: return {}
        
        results = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT source_name, analysis_blob FROM repo_analysis")
            for row in cursor.fetchall():
                results[row[0]] = json.loads(row[1])
        return results

    def get_repaid_debt(self) -> float:
        if not self.enabled: return 0.0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM commercial_metrics WHERE metric_id = 'total_debt_repaid'")
            row = cursor.fetchone()
            return row[0] if row else 0.0

    def add_repaid_debt(self, amount: float):
        if not self.enabled: return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE commercial_metrics SET value = value + ? WHERE metric_id = 'total_debt_repaid'", (amount,))
            conn.commit()

    def save_relationship(self, source: str, target: str, rel_type: str = "depends", strength: float = 1.0):
        if not self.enabled: return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO relationships (source, target, type, strength)
                VALUES (?, ?, ?, ?)
            """, (source, target, rel_type, strength))
            conn.commit()

    def get_graph(self) -> Dict[str, List[str]]:
        if not self.enabled: return {}
        graph = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT source, target FROM relationships")
            for row in cursor.fetchall():
                src, tgt = row
                if src not in graph: graph[src] = []
                graph[src].append(tgt)
        return graph

    def save_risk_snapshot(self, source: str, s: float, v: float, k: float, c: float, total: float, classification: str):
        if not self.enabled: return
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO risk_snapshots 
                (source, timestamp, s_score, v_score, k_score, c_score, total_risk, classification)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (source, timestamp, s, v, k, c, total, classification))
            conn.commit()
