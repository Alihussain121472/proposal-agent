# Senior Freelance Proposal Strategist Agent ⚡
> *"Clients do not hire the most qualified freelancer. They hire the freelancer who makes them feel most understood and most confident the problem will be solved."*

A battle-tested freelance proposal generation and coaching system designed to win high-ticket contracts across **Upwork**, **Direct Outreach (Cold Email)**, **LinkedIn**, and **Agency RFPs**.

---

## 🎯 What Makes This Agent Different

Most proposals fail because they sound like cover letters: listing skills, reciting résumés, and opening with *"Hi, my name is..."* or *"I am an experienced developer..."*.

This agent executes a rigorous multi-step strategy:

1. **Client Psychology Read**: Identifies the real underlying business objective, the client's biggest fear (wasted budget, missed deadlines, wrong hire), and the single trigger phrase that creates instant trust.
2. **Platform Calibration**:
   - **Upwork (180–220 words)**: High-impact hook visible in the 2-line preview cutoff. Never mentions "Upwork" inside the pitch.
   - **Direct Email (220–300 words)**: Generates a curiosity-driven subject line. Personal and consultative.
   - **LinkedIn (100–150 words)**: Conversational and ultra-concise, ending with a natural dialogue question.
   - **Agency RFP (250–350 words)**: Structured and directly addressing RFP criteria and compliance.
3. **Automated Red Flag Detection**:
   - Scans for unpaid spec work (*"show us what you'd do first"*), unrealistic budgets, vague requirements, and multi-freelancer tests.
   - Generates a concise, 2-sentence **RED FLAG ALERT** placed before the proposal so you can protect your time and avoid bad clients.
4. **Dual Strategic Variations**:
   - **VARIATION A**: Leads with the client's core pain and operational bottleneck.
   - **VARIATION B**: Leads with a bold, quantifiable result or relevant achievement.
5. **Strategic Coaching Note**:
   - Recommends the stronger variation (A vs B) for the specific job.
   - Tells you exactly what to personalize before sending.
   - Provides an intelligent follow-up question that demonstrates deep domain expertise.
   - Analyzes win probability factors.
6. **Strict Negative Rule Enforcement**:
   - **Never** opens with "I", "My name is", or freelancer job titles.
   - **Never** uses cliché buzzwords (*"passionate"*, *"detail-oriented"*, *"hardworking"*, *"team player"*, *"excited about"*, *"perfect fit"*).
   - **Never** claims *"I always deliver on time"*.
   - **Never** lists raw bullet points of skills.
   - **Never** writes generic cover letters or sycophantic praise (*"Great project!"*).

---

## 🚀 Quick Start

### 1. Interactive Web Dashboard (Recommended)
Launch the web interface:

```bash
python main.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

Features:
- Platform selector tabs with live word-budget counters.
- Tone picker (Professional, Friendly, Direct, Consultative).
- 1-click preset loaders for real-world scenarios.
- Real-time red flag detector.
- 1-click copy buttons for Variation A, Variation B, or Full Output.
- Export directly to Markdown (`.md`) or TXT.

---

### 2. Interactive Terminal CLI
Run the rich terminal CLI:

```bash
python main.py --cli
```

Follow the prompts or load presets directly in your terminal.

---

### 3. Instant Demo Runs (Zero Configuration)
Test out the agent on 4 curated scenarios immediately:

```bash
# Demo 1: Full-Stack AI SaaS Developer on Upwork ($5k project)
python main.py --demo 1

# Demo 2: UI/UX & Conversion Rate Optimization (Direct Email)
python main.py --demo 2

# Demo 3: Python Automation with Red Flag Spec Work Detection
python main.py --demo 3

# Demo 4: B2B SaaS Growth Copywriting (Agency RFP)
python main.py --demo 4
```

---

### 4. Run Automated Test Suite
Verify red flag detectors, negative rules linter, and platform calibrations:

```bash
python test_agent.py
```

All 7 unit tests validate rule compliance, length boundaries, and structure.

---

## ⚙️ LLM Providers Supported

The agent functions out of the box with zero external dependencies via its built-in **Offline Strategic Engine**.

To enable state-of-the-art LLM generation, set your API key in `.env` or in the Web Dashboard Settings:

| Provider | Supported Models | Environment Variable |
| :--- | :--- | :--- |
| **Offline Strategic Engine** | Built-in Rule & Psychology Engine | *None needed (default)* |
| **Google Gemini** | `gemini-2.5-flash`, `gemini-1.5-pro` | `GEMINI_API_KEY` |
| **Groq** | `llama-3.3-70b-versatile`, `llama-3.1-8b` | `GROQ_API_KEY` |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini` | `OPENAI_API_KEY` |
| **Ollama / Local** | `llama3`, `mistral`, `deepseek` | `http://localhost:11434/v1` |

Copy `.env.example` to `.env` to configure:
```bash
cp .env.example .env
```

---

## 📁 Project Architecture

```
porposel agent/
│
├── proposal_agent/               # Core Agent Logic
│   ├── __init__.py               # Package exports
│   ├── models.py                 # Pydantic data schemas
│   ├── config.py                 # Configuration & API keys
│   ├── prompts.py                # System prompts & meta-templates
│   ├── red_flag_detector.py      # Spec work & client risk analyzer
│   ├── rules_linter.py           # Absolute negative rules validator
│   ├── offline_engine.py         # Deterministic strategist engine
│   ├── llm_engine.py             # Gemini, Groq, OpenAI & Ollama orchestrator
│   └── agent.py                  # Unified ProposalStrategistAgent
│
├── app.py                        # FastAPI web server & interactive dashboard
├── cli.py                        # Rich interactive terminal CLI
├── main.py                       # Main launcher (Web, CLI, Demo)
├── presets.py                    # Curated real-world test scenarios
├── test_agent.py                 # Automated unit test suite
├── .env.example                  # Environment configuration template
└── README.md                     # Documentation
```

---

## 📋 Exact Output Format Generated

```
═══════════════════════════════════════

🚩 RED FLAG ALERT (only include if red flags detected):
[2 sentences maximum. What the freelancer should watch out for before sending this proposal.]

═══════════════════════════════════════

VARIATION A — [one line: the specific angle used]

[Proposal text]

---

VARIATION B — [one line: the specific angle used]

[Proposal text]

═══════════════════════════════════════

📊 COACHING NOTE

Stronger variation: [A or B] — [one sentence explaining why for this specific job]

What to personalize: [one specific thing the freelancer should manually customize before sending]

Smart question to consider adding: [one optional question if not already included above]

Win probability factors: [2–3 sentences on what will most affect whether this proposal wins — based on the job post]

═══════════════════════════════════════
```
