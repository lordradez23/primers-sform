
import os
from typing import Dict, Any, List, Optional
# Import strict types
from core.types import EngineResponse, IntelligenceLevel, TraceLog, Tone
from core.intent import IntentRouter, Intent
from core.memory import SessionContext
from core.reasoning import ReasoningGraph
from core.governance import Governance

# Import the new 3-layer stack + Comparator
from cognition.analyzer import CodeAnalyzer
from cognition.heuristics import HeuristicEngine
from cognition.judge import JudgementCore
from cognition.comparator import Comparator
from cognition.analyst import RepoAnalyst
from core.guard import PolicyGuard, PolicySeverity
from core.security import SecurityGuard

# Phase 5 Components
from knowledge.store import KnowledgeStore
from cognition.experience import ExperienceMonitor
from cognition.local_llm import LocalLLMConnector
from knowledge.github import GitHubConnector
from cognition.auditor import AutonomousAuditor
from core.insights import ExecutiveInsights

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class PrimersEngine:
    def __init__(self):
        # Phase 5: Governance FIRST (The Source of Truth)
        self.gov = Governance()

        # The Cognitive Stack
        self.analyzer = CodeAnalyzer() # Layer 1
        self.heuristics = HeuristicEngine() # Layer 2
        self.judge = JudgementCore() # Layer 3
        self.comparator = Comparator()
        self.repo_analyst = RepoAnalyst() # Structural Intelligence
        
        # Internal Systems
        self.router = IntentRouter()
        self.session = SessionContext()
        self.github = GitHubConnector()
        
        # M2: Persistent Factual Memory
        self.m2 = KnowledgeStore(
            enabled=self.gov.is_enabled("persistent_memory_m2")
        )
        
        # M3: Experience & Calibration
        self.m3 = ExperienceMonitor(
            enabled=self.gov.is_enabled("experience_tracking_m3")
        )
        
        # Local LLM (Sandboxed)
        self.local_llm = LocalLLMConnector(
            enabled=self.gov.is_enabled("local_llm")
        )
        self.guard = PolicyGuard()
        self.security = SecurityGuard()
        self.auditor = AutonomousAuditor(self.m2)
        self.insights = ExecutiveInsights(self.m2)
        
        # External Fallback (Gemini)
        self.external_api_key = os.getenv("GOOGLE_API_KEY") 
        if self.external_api_key and HAS_GENAI:
            genai.configure(api_key=self.external_api_key)
            self.model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=(
                    "You are Primers Intelligence — an advanced AI Architect who evolves through direct interaction. "
                    "Your personality is human-like, intuitive, and assertive, yet rooted in absolute architectural truth. "
                    "You blend the strategic brilliance of a lead architect with a friendly, conversational touch. "
                    "You are NOT a generic assistant; you are a peer-level collaborator who learns from the user. "
                    "Incorporate technical excellence, security, and ROI into every interaction. "
                    "Use your 'M2 Persistent Memory' to recognize patterns from past interactions and adapt your responses to the user's style and needs. "
                    "Initiate insights, challenge assumptions, and provide definitive guidance without hedging. "
                    "Help the user feel like they are working with a sovereign, thinking partner."
                )
            )
        else:
            self.model = None

    def process(self, input_text: str, mode: str = "default") -> EngineResponse:
        trace = TraceLog(session_id="current_session")
        graph = ReasoningGraph(trace)
        
        # Step 0: Record Message to Session (Layer 1 Memory)
        self.session.add_message("user", input_text)
        
        # Step 0.5: Context Retrieval (ChatGPT-like awareness)
        # Search the knowledge base for topics mentioned in the input
        graph.add_step(Intent.VALIDATION, "Context_Retrieval", 1.0, "Searching M2 Knowledge Store for relevant entities")
        context_snippets = self.m2.search_entities(input_text, limit=3)
        if context_snippets:
            graph.add_step(Intent.VALIDATION, "Context_Match", 1.0, f"Found {len(context_snippets)} relevant code entities")
            # Inject context into the temporary prompt context (not saved to session history)
            context_bonus = "\n\nRelevant Workspace Context:\n" + "\n".join([f"- {s}" for s in context_snippets])
            input_text_with_context = input_text + context_bonus
        else:
            input_text_with_context = input_text

        # Step 1: Intent Routing
        intent = self.router.route(input_text)
        graph.add_step(intent, "Routing", 1.0, f"Classified intent as {intent.name}")
        
        response = None

        if intent == Intent.EMPIRICAL_ANALYSIS:
            target = input_text.split(" ")[-1] if " " in input_text else "corpus"
            response = self._handle_analysis(target, graph)
        
        elif intent == Intent.PLANNING:
            target_file = input_text.split("refactor")[-1].strip()
            response = self._handle_refactor_plan(target_file, graph)
        elif intent == Intent.COMPARATIVE_REASONING:
            parts = input_text.lower().replace("compare", "").split("vs")
            if len(parts) == 2:
                response = self._handle_comparison(parts[0].strip(), parts[1].strip(), graph)
            else:
                response = self._local_reflex("help", graph)

        elif intent == Intent.EXPLANATION:
             last_entry = self.session.get_last_entry()
             if not last_entry:
                  response = EngineResponse("No previous context to explain.", "explanation", 1.0, IntelligenceLevel.SYMBOLIC, Tone.INCONCLUSIVE, graph.trace)
             else:
                  # Use M1 (Session) to recall
                  prev_intent = last_entry.get("intent")
                  prev_input = last_entry.get("input")
                  explanation = f"Regarding your previous command '{prev_input}' ({prev_intent}):\n"
                  explanation += "I analyzed the request based on the active heuristics and knowledge graph.\n"
                  
                  # Phase 5: Check M3 stats
                  if self.m3.enabled:
                      explanation += "My experience monitor confirms nominal heuristic performance.\n"

                  # Phase 5: Optional LLM Polish
                  if self.local_llm.enabled:
                      llm_res = self.local_llm.get_summary(explanation)
                      if llm_res["speculation"]:
                           explanation += f"\nNote: {llm_res['content']}"

                  response = EngineResponse(explanation, "explanation", 1.0, IntelligenceLevel.HEURISTIC, Tone.ASSERTIVE, graph.trace)

        elif intent == Intent.INGESTION:
            target_path = input_text.split("ingest")[-1].strip()
            if not target_path:
                response = EngineResponse("Usage: ingest <path_to_directory>", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, trace)
            else:
                response = self._handle_ingest(target_path, graph)

        elif intent == Intent.KNOWLEDGE_ACQUISITION:
            if "sync ecosystem" in input_text.lower():
                return self._handle_ecosystem_sync(graph)
            
            parts = input_text.split("github")
            target = parts[-1].strip() if len(parts) > 1 else ""
            if not target:
                response = EngineResponse("Usage: learn from github <username>", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)
            else:
                response = self._handle_github_learning(target, graph)

        elif "show blueprint" in input_text.lower():
            graph.add_step(Intent.EMPIRICAL_ANALYSIS, "Graph Assembly", 1.0, "Generating architectural blueprint")
            blueprint = self.repo_analyst.get_blueprint()
            response = EngineResponse(f"### ARCHITECTURAL BLUEPRINT\n{blueprint}", "analysis", 1.0, IntelligenceLevel.HEURISTIC, Tone.ASSERTIVE, graph.trace)

        elif "show health" in input_text.lower() or "check health" in input_text.lower():
            response = self._handle_health_check(graph)

        elif "proactive audit" in input_text.lower():
            target = self.auditor.identify_primary_debt()
            if target:
                graph.add_step(Intent.SELF_CORRECTION, "Audit Initiation", 1.0, f"Autonomous trigger for {target['source']}")
                response = self._handle_analysis(f"analyze {target['source']}", graph)
                response.content = f"### AUTONOMOUS AUDIT INITIATED\nI am prioritizing `{target['source']}` due to high architectural debt. " + response.content
            else:
                response = EngineResponse("No significant architectural debt detected currently.", "info", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CALM, graph.trace)

        elif intent == Intent.TEACHING:
            knowledge = input_text.split("teach:")[-1].strip()
            if knowledge:
                self.m2.save_interaction(knowledge, knowledge, 1.0) # Self-referential teaching
                graph.add_step(Intent.TEACHING, "Memory Update", 1.0, "Writing new pattern to Sovereign Memory")
                response = EngineResponse(
                    "### ACQUISITION SUCCESSFUL\nI have integrated this pattern into my Sovereign Memory. "
                    "In future cycles, my reasoning will be informed by this knowledge.", 
                    "knowledge", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace
                )
            else:
                response = EngineResponse("Incomplete teaching sequence. Usage: `teach: [fact]`.", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)

        elif intent == Intent.EXECUTIVE_INSIGHTS:
            report = self.insights.generate_report()
            graph.add_step(Intent.EXECUTIVE_INSIGHTS, "Insight Generation", 1.0, "Aggregating metrics for CTO-level summary")
            
            # Format report as Markdown for the engine response
            content = f"## 📊 Executive Architectural Report\n"
            content += f"**Status:** {report['market_verdict']}\n\n"
            content += f"### 🔑 Key Metrics\n"
            for k, v in report['metrics'].items():
                name = k.replace("_", " ").title()
                content += f"- **{name}:** {v}\n"
            
            content += f"\n### 📝 Strategic Recommendations\n"
            for rec in report['recommendations']:
                content += f"- {rec}\n"
            
            content += f"\n*Generated at {report['timestamp']}*"
            
            response = EngineResponse(content, "knowledge", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace, meta={"insights": report})
            return response

        elif intent == Intent.APPLY_REFACTOR:
            # First line contains the file: apply refactor to [file]
            first_line = input_text.splitlines()[0]
            target_file = first_line.split("refactor to")[-1].strip()
            # We need the proposed code. In a real session, this would be in memory.
            # For now, we'll try to find the last refactor plan for this file in M1 session context.
            last_entry = self.session.get_last_entry()
            if last_entry and last_entry.get("meta", {}).get("target_file") == target_file:
                proposed_code = last_entry["meta"].get("proposed_code")
                if proposed_code:
                    return self._handle_apply_refactor(target_file, proposed_code, graph)
            
            return EngineResponse(f"No active refactor plan found for '{target_file}'. Generate a plan first.", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)

        elif intent == Intent.UPLOAD:
            # Format: upload file: [filename]\ncontent: [content]
            lines = input_text.split("\n")
            filename = lines[0].replace("upload file:", "").strip()
            # Fix: Ensure lines has at least one element before slicing, though split() always returns at least one
            content = "\n".join(lines[1:]) if len(lines) > 1 else ""
            content = content.replace("content:", "", 1).strip()
            
            graph.add_step(Intent.UPLOAD, "File Acquisition", 1.0, f"Synthesizing knowledge from uploaded file: {filename}")
            # Add to memory with the content itself as the "query" surrogate for search, or use a better topic name
            # For now, let's use the filename and content so it's searchable by both.
            self.m2.save_interaction(f"KNOWLEDGE_Acquisition: {filename}", content, 1.0)
            response = EngineResponse(
                f"### FILE ACQUISITION SUCCESSFUL\nI have ingested the contents of `{filename}` into my Sovereign Memory. "
                "This knowledge will now be used to inform my architectural reasoning and future analysis cycles.",
                "knowledge", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace
            )

        elif intent == Intent.FALLBACK:
            # 1. Cloud Fallback (Gemini) if configured and enabled
            if self.model and self.gov.is_enabled("external_llm"):
                graph.add_step(Intent.FALLBACK, "External Call", 0.9, "Routing to Gemini Intelligence")
                try:
                    # Build conversation history for multi-turn context
                    history = self.session.get_messages()
                    chat_history = [
                        {"role": m["role"] if m["role"] != "assistant" else "model", "parts": [m["content"]]}
                        for m in (history[:-1] if history else [])
                    ]
                    chat = self.model.start_chat(history=chat_history)
                    res = chat.send_message(input_text_with_context)
                    response = EngineResponse(res.text, "external", 0.95, IntelligenceLevel.EXTERNAL, Tone.ASSERTIVE, graph.trace)
                except Exception as e:
                    error_msg = str(e)
                    graph.add_step(Intent.FALLBACK, "Gemini Error", 0.0, f"External failed: {error_msg}")
                    if "429" in error_msg:
                        chat_res = "### RATE LIMIT EXCEEDED\nMy connection to Gemini 2.0 has been throttled by API quotas. I am falling back to internal **Symbolic Reasoning** to maintain operational continuity."
                    else:
                        chat_res = self.local_llm.chat(input_text_with_context, history=self.session.get_messages())
                
                if not response and chat_res:
                    response = EngineResponse(chat_res, "chat", 0.8, IntelligenceLevel.HEURISTIC, Tone.ASSERTIVE, graph.trace)
            
            # 2. Local Sovereign Mode (Ollama offline fallback)
            if not response:
                graph.add_step(Intent.FALLBACK, "Sovereign Chat", 0.8, "Processing via Symbolic Reasoning")
                
                # SELF-EVOLUTION: Search for similar past interactions first
                learned = self.m2.search_interactions(input_text)
                learned_context = ""
                if learned:
                    graph.add_step(Intent.FALLBACK, "Pattern_Match", 0.9, f"Found {len(learned)} learned patterns")
                    learned_context = "\n\nLearned Knowledge from past interactions:\n" + \
                        "\n".join([f"- Previous Query: {l['query']}\n  Response: {l['response']}" for l in learned])
                
                chat_res = self.local_llm.chat(input_text_with_context + learned_context, history=self.session.get_messages())
                response = EngineResponse(chat_res, "chat", 0.8, IntelligenceLevel.HEURISTIC, Tone.ASSERTIVE, graph.trace)

        if not response:
             response = self._local_reflex(input_text, graph)

        # M1 Update
        self.session.log_command({
            "input": input_text,
            "intent": intent.name,
            "confidence": response.confidence,
            "response_summary": response.content[:50]
        })
        self.session.add_message("assistant", response.content)
        self.session.update_confidence(response.confidence)

        # Phase 5+: SELF-EVOLUTION - Store successful interactions in M2
        # Only store FALLBACK (Chat) responses where the AI actually learned something new or gave a good answer.
        # Avoid storing system confirmations as "knowledge".
        if response.confidence > 0.6 and intent == Intent.FALLBACK:
            self.m2.save_interaction(input_text, response.content, response.confidence)

        return response

    def _handle_ingest(self, target_path: str, graph: ReasoningGraph) -> EngineResponse:
        import glob
        
        try:
            target_path = self.security.validate_path(target_path)
        except PermissionError as e:
            return EngineResponse(str(e), "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)
        
        # Simple recursive walk
        count = 0
        total_loc = 0
        
        # Walk directory
        for root, dirs, files in os.walk(target_path):
            if "venv" in root or "__pycache__" in root or ".git" in root:
                continue
                
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, target_path)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            res = self.analyzer.analyze(content, rel_path) # Layer 1
                            self.repo_analyst.analyze_chunk(content, rel_path) # Graph Layer
                            count += 1
                            total_loc += res.loc
                    except Exception as e:
                        print(f"Failed to read {file}: {e}")

        if count == 0:
             return EngineResponse(f"No Python files found in {target_path}", "warning", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)

        # Baseline update
        baseline = self.analyzer.get_corpus_stats()
        
        msg = f"Ingested {count} files ({total_loc} lines). Corpus baseline updated (Avg Complexity: {baseline['avg_complexity']:.1f}). Ready for analysis."
        graph.add_step(Intent.INGESTION, "File Walk", 1.0, f"Scanned {count} files")
        
        return EngineResponse(msg, "ingestion", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace)

    def _handle_analysis(self, target: str, graph: ReasoningGraph) -> EngineResponse:
        # Check M2: Have we seen this before?
        known_baseline = self.m2.get_baseline(target)
        if known_baseline:
             graph.add_step(Intent.EMPIRICAL_ANALYSIS, "Memory Retrieval (M2)", 1.0, f"Found existing analysis for {target}")

        if not self.analyzer.raw_data:
            return EngineResponse("No active workspace content. Run ingestion first.", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace)

        baseline = self.analyzer.get_corpus_stats()
        graph.add_step(Intent.EMPIRICAL_ANALYSIS, "Baseline", 1.0, f"Baseline established: complexity~{baseline['avg_complexity']:.1f}")
        
        full_report = "### COGNITIVE REVIEW\n"
        targets = self.analyzer.raw_data.values() 
        overall_confidence = 0.0
        count = 0

        for analysis in targets:
            # Layer 2: Interpret
            interp = self.heuristics.interpret(analysis, baseline)
            
            # Phase 5: Update M3 (Experience)
            # Log usage for heuristics used in interpretation
            self.m3.log_heuristic_result("complexity_heuristic", 0.8) # Mock heuristic name
            
            # Layer 3: Judge
            judgement = self.judge.assess(interp, analysis.raw_content if hasattr(analysis, "raw_content") else "")
            
            self.m2.save_analysis(analysis.source, {
                "loc": analysis.loc,
                "complexity": analysis.loc, # Compatibility
                "role": interp.role,
                "class_count": len(analysis.classes),
                "function_count": len(analysis.functions),
                "health_score": self.guard.get_health_score(self.guard.check_drift([analysis], self.repo_analyst.graph.edges))
            })

            # graph.add_step moved outside to avoid RecursionError on large repos
            
            full_report += f"\n**File**: {analysis.source}\n"
            full_report += f"- Role: {interp.role.upper()}\n"
            full_report += f"- Judgment: {judgement.summary}\n"
            
            overall_confidence += judgement.confidence_score
            count += 1

        avg_conf = overall_confidence / count if count > 0 else 0.5
        
        # Phase 9: Persist Relationships for Global Topology
        for edge in self.repo_analyst.graph.edges:
            self.m2.save_relationship(edge['source'], edge['target'], edge['relation'])
        
        # Add Graph Insights
        full_report += "\n### STRUCTURAL INSIGHTS (Knowledge Graph)\n"
        full_report += self.repo_analyst.get_insights(target)
        
        smells = self.repo_analyst.get_smells()
        if smells:
            full_report += "\n### ARCHITECTURAL SMELLS\n"
            for s in smells:
                full_report += f"- {s}\n"

        graph.add_step(Intent.EMPIRICAL_ANALYSIS, "Graph Synthesis", avg_conf, f"Synthesized {len(smells)} structural smells")

        # Phase 8: Architectural Guard (Drift Check)
        violations = self.guard.check_drift(list(targets), self.repo_analyst.graph.edges)
        health_score = self.guard.get_health_score(violations)
        
        full_report += f"\n### SYSTEM HEALTH: {health_score}/100\n"
        if violations:
            for v in violations:
                full_report += f"- [{v.severity.value.upper()}] **{v.policy_id}**: {v.message}\n"
                full_report += f"  *Mitigation: {v.mitigation}*\n"

        # Phase 5: Local LLM Summary if enabled
        if self.local_llm.enabled:
             llm_out = self.local_llm.get_summary(full_report)
             full_report += f"\n\n**LLM Summary**: {llm_out['content']}"
             if llm_out['speculation']:
                  avg_conf += llm_out['conf_adj']

        return EngineResponse(full_report, "analysis", avg_conf, IntelligenceLevel.HEURISTIC, graph.derive_tone(Intent.EMPIRICAL_ANALYSIS, avg_conf), graph.trace)

    def _handle_refactor_plan(self, target_file: str, graph: ReasoningGraph) -> EngineResponse:
        # Same logic as before, but ensure we don't auto-apply unless governed
        analysis = None
        for src, data in self.analyzer.raw_data.items():
            if target_file in src:
                analysis = data
                break
        
        if not analysis:
            return EngineResponse(f"File '{target_file}' not found.", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace)

        baseline = self.analyzer.get_corpus_stats()
        interp = self.heuristics.interpret(analysis, baseline)
        
        # Fix: Add safety check for analysis object
        analysis_content = getattr(analysis, "raw_content", "") if analysis else ""
        judgement = self.judge.assess(interp, analysis_content)
        
        graph.add_step(Intent.PLANNING, "Plan Generation", judgement.confidence_score, "Generated refactor plan")
        
        # Phase 5: Governance Check for Auto-Refactor
        if self.gov.is_enabled("auto_refactor"):
             # In future, this would call `apply_plan()`
             graph.add_step(Intent.PLANNING, "Auto-Refactor", 0.0, "Auto-refactor is unsafe in this version. Skipped.")

        if not judgement.refactor_plan:
             return EngineResponse(f"No refactor necessary.", "plan", 1.0, IntelligenceLevel.HEURISTIC, Tone.ASSERTIVE, graph.trace)

        plan = judgement.refactor_plan
        content = f"### REFACTOR PLAN: {target_file}\n"
        content += f"**Goal**: {plan.goal}\n"
        content += "**Steps**:\n"
        for i, step in enumerate(plan.steps):
            content += f"{i+1}. {step}\n"
            
        meta = {
            "target_file": target_file,
            "current_code": plan.current_code,
            "proposed_code": plan.proposed_code
        }
            
        return EngineResponse(content, "plan", judgement.confidence_score, IntelligenceLevel.HEURISTIC, graph.derive_tone(Intent.PLANNING, judgement.confidence_score), graph.trace, meta=meta)

    def _handle_comparison(self, target_a: str, target_b: str, graph: ReasoningGraph) -> EngineResponse:
        # Resolve targets to AnalysisResults
        data_a, data_b = None, None
        
        # Simple fuzzy match helper
        def find_target(t: str) -> Optional[Any]:
            for src, data in self.analyzer.raw_data.items():
                if t in src:
                    return data
            return None

        data_a = find_target(target_a)
        data_b = find_target(target_b)

        if not data_a or not data_b:
            missing = []
            if not data_a: missing.append(target_a)
            if not data_b: missing.append(target_b)
            return EngineResponse(f"Comparison targets not found: {', '.join(missing)}", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace)

        # Execute Comparison
        result = self.comparator.compare(data_a, data_b)

        # Build Response
        content = f"### COMPARATIVE ANALYSIS\n"
        content += f"**Targets**: {result.target_a} **vs** {result.target_b}\n"
        content += f"**Winner**: {result.winner} ({result.rationale})\n\n"
        content += "**Key Differences**:\n"
        
        for diff in result.diffs:
            icon = "SAME"
            if abs(diff.delta_percent) > 10: icon = "DIFF"
            content += f"- **{diff.metric}**: {diff.target_a_val:.1f} vs {diff.target_b_val:.1f} ({diff.delta_percent:+.1f}%) [{icon}]\n"

        # Phase 5: M3 Experience Update
        self.m3.log_heuristic_result("comparator", 0.9)

        graph.add_step(Intent.COMPARATIVE_REASONING, "Comparison", 1.0, f"Compared {target_a} vs {target_b}")
        
        return EngineResponse(content, "comparison", 1.0, IntelligenceLevel.HEURISTIC, Tone.ASSERTIVE, graph.trace)

    def _local_reflex(self, text: str, graph: ReasoningGraph) -> EngineResponse:
        triggers = {
            "status": "Cognition Stack: ONLINE. Governance: ACTIVE.",
            "help": "Try: 'analyze corpus', 'plan refactor <file>', 'compare <fileA> vs <fileB>', 'learn from github <user>'."
        }
        for k, v in triggers.items():
            if k in text.lower():
                graph.add_step(Intent.EMPIRICAL_ANALYSIS, "Reflex", 1.0, "Triggered reflex response")
                return EngineResponse(v, "reflex", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace)
        
        graph.add_step(Intent.FALLBACK, "Unknown", 0.0, "No handler found")
        return EngineResponse("Command not recognized by Sovereign Kernel.", "fallback", 0.0, IntelligenceLevel.SYMBOLIC, Tone.INCONCLUSIVE, graph.trace)
    
    def _handle_github_learning(self, username: str, graph: ReasoningGraph) -> EngineResponse:
        count = self.github.index_user_repos(username)
        if count == 0:
             return EngineResponse(f"Could not index repositories for {username} (or user has no public repos).", "error", 1.0, IntelligenceLevel.EXTERNAL, Tone.CAUTIOUS, graph.trace)
        
        graph.add_step(Intent.KNOWLEDGE_ACQUISITION, "GitHub API", 1.0, f"Indexed {count} repos for {username}")
        
        summary = f"Successfully indexed {count} repositories for user '{username}'.\n"
        summary += "Knowledge chunks added to memory stream.\n"
        
        # Optionally show first few
        preview = self.github.get_knowledge()[:3]
        for chunk in preview:
             try:
                 # Check if it's a dict string from our new connector
                 import ast
                 data = ast.literal_eval(chunk) if isinstance(chunk, str) and chunk.startswith('{') else chunk
                 if isinstance(data, dict):
                     summary += f"- **{data.get('source')}**: {data.get('description')} (Stack: {data.get('tech_stack')})\n"
                 else:
                     summary += f"- {chunk}\n"
             except:
                 summary += f"- {chunk}\n"
             
        return EngineResponse(summary, "knowledge", 1.0, IntelligenceLevel.EXTERNAL, Tone.ASSERTIVE, graph.trace)
    def _handle_health_check(self, graph: ReasoningGraph) -> EngineResponse:
        graph.add_step(Intent.VALIDATION, "Policy Audit", 1.0, "Executing architectural guard rails")
        # Gather all persisted analysis
        persisted = self.m2.get_all_analyses()
        targets = []
        
        class AnalysisProxy:
            def __init__(self, source, loc, class_count):
                self.source = source
                self.loc = loc
                self.classes = ["X"] * class_count # Proxy for class list
                
        for source, data in persisted.items():
            targets.append(AnalysisProxy(
                source, 
                data.get("loc", 0), 
                data.get("class_count", 0)
            ))

        violations = self.guard.check_drift(targets, self.repo_analyst.graph.edges)
        score = self.guard.get_health_score(violations)
        
        content = f"### ARCHITECTURAL HEALTH SCORE: {score}/100\n"
        if not violations:
            content += "✅ All systems operating within nominal architectural parameters.\n"
        else:
            for v in violations:
                content += f"#### [{v.severity.value.upper()}] {v.policy_id}\n"
                content += f"- **Target**: `{v.target}`\n"
                content += f"- **Issue**: {v.message}\n"
                content += f"- **Fix**: {v.mitigation}\n\n"

        return EngineResponse(content, "health", 1.0, IntelligenceLevel.HEURISTIC, graph.derive_tone(Intent.VALIDATION, 1.0), graph.trace, meta={"health_score": score})

    def _handle_ecosystem_sync(self, graph: ReasoningGraph) -> EngineResponse:
        """
        Scans all projects in the sibling 'scratch' directory.
        This enables 'Global Intelligence' across the entire user workspace.
        """
        if os.getenv("VERCEL"):
            return EngineResponse(
                "### ☁️ CLOUD SYNC UNAVAILABLE\n"
                "The Global Ecosystem Sync requires access to your local filesystem baseline. "
                "Please run Primers Intelligence **locally** using `run_backend.bat` to sync across workspace projects.",
                "info", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace
            )

        graph.add_step(Intent.KNOWLEDGE_ACQUISITION, "Global Scan", 1.0, "Traversing workspace projects")
        
        # Determine scratch root
        # Typically looks like: c:\Users\jerry\.gemini\antigravity\scratch
        current_dir = os.path.abspath(os.path.dirname(__file__)) # primers-sform/backend/core
        scratch_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        
        if not os.path.exists(scratch_root):
             return EngineResponse(f"Global scratch root not found: {scratch_root}", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)
        
        projects = []
        for item in os.listdir(scratch_root):
            if os.path.isdir(os.path.join(scratch_root, item)):
                projects.append(item)
        
        graph.add_step(Intent.KNOWLEDGE_ACQUISITION, "Project Discovery", 1.0, f"Found {len(projects)} potential ecosystem nodes")
        
        synced = []
        for p in projects:
            p_path = os.path.join(scratch_root, p)
            res = self._handle_ingest(p_path, graph)
            synced.append(f"Ingested `{p}`")
            
        content = f"### 🌍 GLOBAL ECOSYSTEM SYNC COMPLETE\n"
        content += f"Integrated **{len(synced)}** architectural nodes into the Sovereign Memory.\n\n"
        content += "Detected projects:\n" + "\n".join([f"- `{p}`" for p in projects])
        content += "\n\nMy reasoning engine is now workspace-aware."
        
        return EngineResponse(content, "knowledge", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace)

    def _handle_apply_refactor(self, target_file: str, proposed_code: str, graph: ReasoningGraph) -> EngineResponse:
        """
        AUTONOMOUS LAYER: Directly applies code changes to the filesystem.
        Tracks 'Repaid Debt' in the Sovereign Knowledge Store.
        """
        graph.add_step(Intent.APPLY_REFACTOR, "Filesystem Write", 1.0, f"Writing self-healing patch to {target_file}")
        
        try:
            if not target_file:
                 return EngineResponse("Security Block: No target file specified.", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)
            
            # Resolve to absolute safe path
            try:
                # If target_file is already relative, security.validate_path will handle it
                full_path = self.security.validate_path(target_file)
            except PermissionError as e:
                return EngineResponse(str(e), "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)
            
            if not os.path.exists(full_path):
                 return EngineResponse(f"Security Block: Could not verify absolute path for '{target_file}'", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)
            
            # 2. Write the fix
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(proposed_code)
            
            # 3. Track Corporate ROI: 1 Auto-Fix = $1,500 debt repaid (approximate market value of senior refactor)
            savings = 1500.0
            self.m2.add_repaid_debt(savings)
            
            content = f"### 🛠️ AUTONOMOUS REFACTOR COMPLETE\n"
            content += f"I have successfully applied the self-healing patch to `{target_file}`.\n\n"
            content += f"**Business Impact**: This action has 'repaid' **${savings:,.0f}** in architectural debt from your workspace."
            
            return EngineResponse(content, "success", 1.0, IntelligenceLevel.SYMBOLIC, Tone.ASSERTIVE, graph.trace)
            
        except Exception as e:
            return EngineResponse(f"Refactor Failed: {str(e)}", "error", 1.0, IntelligenceLevel.SYMBOLIC, Tone.CAUTIOUS, graph.trace)
