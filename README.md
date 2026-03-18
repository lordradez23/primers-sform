# Primers Intelligence (S-Form V3.0)

## Overview
Primers Intelligence is a sovereign cognitive engine for code architecture, security audits, and systemic reasoning. Version 3.0 introduces a hybrid intelligence layer combining local symbolic reasoning with high-fidelity cloud models (Gemini) for a "Resident Architect" experience.

## Features
- **Hybrid Cognitive Stack**:
  - **Sovereign Mode**: Local AST-based reasoning and heuristics for role discovery.
  - **Cloud Hybrid**: Integrated Gemini 1.5 Flash for natural language processing and complex architectural judgment.
- **M2 Persistent Memory**: A self-evolving knowledge store that learns from user interactions and codebase context.
- **Executive Dashboard**: Real-time structural integrity monitoring and ROI-focused insights.
- **Neural Trace**: Transparent reasoning logs showing exactly how the AI arrived at its conclusions.

## Quick Start (Monorepo)

This project consists of a FastAPI backend and a Next.js frontend.

### 1. Environment Setup
Create a `backend/.env` file based on the provided configuration:
```env
GOOGLE_API_KEY=your_key_here
PRIMERS_LLM_MODEL=gemini-1.5-flash
```

### 2. Start Services
From the root directory:

**Backend (Port 8000):**
```bash
run_backend.bat
```

**Frontend (Port 3000):**
```bash
npm run dev:frontend
```

## Technical Architecture
- **Backend**: Python 3.10+, FastAPI, Pydantic, Google Generative AI.
- **Frontend**: Next.js 16+, Framer Motion, Tailwind CSS, Lucide React.
- **Cognition**: Layered symbolic-to-neural pipeline.

## System Commands
- `analyze corpus`: triggered deep heuristic scan.
- `show health`: interactive structural audit.
- `compare <A> vs <B>`: architectural complexity analysis.
