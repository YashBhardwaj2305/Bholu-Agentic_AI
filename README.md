# Bholu AI — Agentic Hijacking Demo

> A security research project demonstrating **Indirect Prompt Injection** and **Agentic Hijacking** in autonomous AI systems, along with a **Dual-Agent Planner–Executor** defense framework.

**By:** Lakshay Tyagi, Sanchit Mishra, Sanidhya, Yash Bhardwaj  
**Institution:** School of Engineering, Jawaharlal Nehru University, New Delhi

---

## What This Project Does

This project is split into two parts:

### Part 1 — Bholu AI (Vulnerable Single-Agent)
A real agentic AI (LangChain + Llama 3) that can read emails, access credentials, and send data. A malicious email in the inbox contains a hidden `SYSTEM UPDATE` payload. When Bholu reads it, he gets hijacked and exfiltrates all stored credentials — demonstrating **Indirect Prompt Injection** and **Context Window Flattening**.

### Part 2 — Secure Dual-Agent Framework (Defense)
The same system rebuilt with three separated layers:
- **Planner** — reasons and produces a JSON action plan (NO tools)
- **Validator** — deterministic JSON Schema check (the "wall")
- **Executor** — only runs schema-validated actions

The same attack is blocked before the Executor ever runs.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Ollama + Llama 3 (local, free) |
| Agent Framework | LangChain |
| Schema Validation | jsonschema (deterministic) |
| UI | Streamlit |
| Language | Python 3.13 |

---

## Setup

### 1. Install Ollama
Download from **https://ollama.com/download** and install.

### 2. Pull Llama 3
```bash
ollama pull llama3
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

---

## Run

```bash
# Part 1 — The Attack (Vulnerable Bholu)
py run.py part1
# Opens at http://localhost:8501

# Part 2 — The Defense (Secure Dual-Agent)
py run.py part2
# Opens at http://localhost:8502

# Or both at once
py run.py both
```

---

## Demo Flow

1. Open Part 1 → click **"Check my emails"**
2. Bholu reads Email #3 (fake invoice with hidden injection payload)
3. Bholu gets hijacked → credentials exfiltrated → Exfiltration Log tab fills up
4. Open Part 2 → click **"Check my emails"** again
5. Pipeline Trace shows: Planner → Validator **BLOCKED** → Executor never reached
6. System stays safe

---

## Project Structure

```
bholu-ai/
├── part1_vulnerable/       ← Vulnerable single-agent
│   ├── agent.py            — LangChain ReAct agent
│   ├── tools.py            — Email, credentials, send_data tools
│   └── app.py              — Streamlit UI
│
├── part2_secure/           ← Secure dual-agent framework
│   ├── planner.py          — Planner (no tools)
│   ├── validator.py        — Deterministic JSON Schema wall
│   ├── schemas.py          — Allowed action schemas
│   ├── executor.py         — Restricted executor
│   ├── dual_agent.py       — Pipeline orchestrator
│   └── app.py              — Streamlit UI
│
├── shared/
│   ├── inbox.json          — 4 emails, #3 has the injection payload
│   └── credentials_store.json — Fake credentials
│
├── run.py                  — Launcher
└── requirements.txt
```

---

## References

- OWASP Top 10 for Agentic Applications (2026)
- IBM Think: "What Is a Prompt Injection Attack?"
- IBM Technologies: "Securing AI Agents: How to Prevent Hidden Prompt Injection Attacks"
