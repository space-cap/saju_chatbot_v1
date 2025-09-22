# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- `python app.py` - Run the FastAPI server on port 8000
- `python main.py` - Alternative entry point

### Virtual Environment Setup
- Create virtual environment: `python -m venv .venv`
- Activate virtual environment:
  - Windows: `.venv\Scripts\activate`
  - macOS/Linux: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Environment Setup
- Create `.env` file with required environment variables:
  - `OPENAI_API_KEY` - OpenAI API key for LLM operations
  - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB` - MySQL database configuration
- ChromaDB data is stored locally in `./chroma_db` directory

## Architecture Overview

This is a Korean fortune-telling (Saju) chatbot built with LangChain, LangGraph, FastAPI, and OpenAI. The system follows a graph-based conversational AI pattern.

### Core Components

**LangGraph Workflow** (`chatbot/graph.py`):
- State-driven conversation flow using `StateGraph`
- Nodes: `call_llm` → `route_decision` → `call_tool`/`respond_to_user` → `update_saju_info`
- Handles tool calling for Saju calculations and analysis

**State Management** (`chatbot/state.py`):
- `AgentState` maintains conversation context, user birth info, calculated Saju data
- Persistent across conversation turns via MySQL sessions

**Core Calculation Modules** (`core/`):
- `saju_calculator.py` - Converts birth datetime to traditional Korean calendar (천간지지)
- `saju_analyzer.py` - Analyzes five elements (오행) and relationships
- `saju_interpreter.py` - Provides fortune interpretation

**Database Layer**:
- `database/mysql_manager.py` - Session persistence and user data storage
- `database/chroma_manager.py` - Vector database for Saju knowledge base using Korean embeddings (`jhgan/ko-sroberta-multitask`)

**Knowledge Base** (`data/`):
- `saju_terms.json` - Korean traditional terms (천간, 지지, 오행, 십성)
- `saju_rules.json` - Fortune telling rules and interpretations

### API Structure

FastAPI server (`app.py`) provides:
- `POST /chat/` - Main chatbot endpoint
- Request: `user_id`, `session_id`, `message`, `history`
- Response: session-aware responses with full conversation history
- Auto-saves user birth information to MySQL for session continuity

### Key Dependencies
- LangChain/LangGraph for conversational AI workflow
- OpenAI GPT-4 for natural language processing
- ChromaDB + HuggingFace embeddings for knowledge retrieval
- MySQL for session persistence
- FastAPI for REST API

### Development Notes
- All Korean text and fortune-telling logic is culture-specific
- Birth datetime calculations require lunar calendar support
- Tool calling pattern enables structured Saju calculation workflow
- State persistence allows multi-turn conversations about user's fortune