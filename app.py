"""
FastAPI Web Dashboard for Senior Freelance Proposal Strategist & Academic Assistant Agent.
Includes a modern responsive UI (Tailwind CSS, Alpine.js, Lucide icons),
dual-mode support (Freelance $2M+ Pitch & Academic Bachelor's/Master's/PhD Assistant),
REST API endpoints, preset loaders, and export functionality.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from proposal_agent import (
    ProposalStrategistAgent, ProposalInput, ProposalResponse,
    Platform, Tone, lint_proposal, analyze_red_flags,
    AcademicLevel, AcademicProposalType, AcademicProposalInput, AcademicProposalResponse
)
from presets import PRESETS, ACADEMIC_PRESETS

app = FastAPI(
    title="Proposal Strategist & Academic Assistant Agent",
    description="Dual-mode AI proposal generator: Freelance ($2M+ win rate) and Academic & Professional (Bachelor's, Master's, PhD)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ProposalStrategistAgent()

class GenerateRequest(BaseModel):
    platform: Platform = Platform.UPWORK
    job_description: str
    freelancer_profile: str
    relevant_experience: str
    proposed_approach: str
    budget_range: Optional[str] = ""
    tone: Tone = Tone.PROFESSIONAL
    achievements: Optional[str] = ""
    provider: Optional[str] = "offline"
    api_key: Optional[str] = None
    model: Optional[str] = None

class AcademicGenerateRequest(BaseModel):
    academic_level: AcademicLevel = AcademicLevel.MASTERS
    proposal_type: AcademicProposalType = AcademicProposalType.EDUCATION
    topic: str
    purpose: str
    target_audience: Optional[str] = "Academic Faculty Review Committee"
    specific_requirements: Optional[str] = ""
    provider: Optional[str] = "offline"
    api_key: Optional[str] = None
    model: Optional[str] = None

class RedFlagCheckRequest(BaseModel):
    job_description: str
    budget_range: Optional[str] = ""

class LintRequest(BaseModel):
    proposal_text: str
    platform: Platform = Platform.UPWORK

@app.get("/api/presets", response_model=Dict[str, Any])
async def get_presets():
    """Return available freelance demo presets."""
    return {
        k: {
            "title": v["title"],
            "description": v["description"],
            "input": v["input"].model_dump()
        }
        for k, v in PRESETS.items()
    }

@app.get("/api/academic/presets", response_model=Dict[str, Any])
async def get_academic_presets():
    """Return available academic demo presets."""
    return {
        k: {
            "title": v["title"],
            "description": v["description"],
            "input": v["input"].model_dump()
        }
        for k, v in ACADEMIC_PRESETS.items()
    }

@app.post("/api/generate", response_model=ProposalResponse)
async def generate_proposal_endpoint(req: GenerateRequest):
    """Generate two freelance proposal variations with red flag analysis and coaching note."""
    inp = ProposalInput(
        platform=req.platform,
        job_description=req.job_description,
        freelancer_profile=req.freelancer_profile,
        relevant_experience=req.relevant_experience,
        proposed_approach=req.proposed_approach,
        budget_range=req.budget_range,
        tone=req.tone,
        achievements=req.achievements
    )
    try:
        res = agent.generate(
            inp=inp,
            provider=req.provider,
            api_key=req.api_key,
            model=req.model
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/academic/generate", response_model=AcademicProposalResponse)
async def generate_academic_proposal_endpoint(req: AcademicGenerateRequest):
    """Generate structured 7-section academic and professional proposal."""
    inp = AcademicProposalInput(
        academic_level=req.academic_level,
        proposal_type=req.proposal_type,
        topic=req.topic,
        purpose=req.purpose,
        target_audience=req.target_audience or "Academic Faculty Review Committee",
        specific_requirements=req.specific_requirements or ""
    )
    try:
        res = agent.generate_academic(
            inp=inp,
            provider=req.provider,
            api_key=req.api_key,
            model=req.model
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-red-flags")
async def check_red_flags_endpoint(req: RedFlagCheckRequest):
    """Scan job description in real-time for red flags."""
    return agent.check_red_flags(req.job_description, req.budget_range or "")

@app.post("/api/lint")
async def lint_endpoint(req: LintRequest):
    """Lint proposal text against negative rules."""
    violations = agent.lint(req.proposal_text, req.platform)
    return {
        "passed": len(violations) == 0,
        "violations": violations
    }

@app.get("/api/history")
async def get_history_endpoint():
    """Get history of generated proposals."""
    return agent.get_history()

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the complete interactive Web UI with dual-mode support."""
    html_content = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proposal Agent | Freelance & Academic Proposal Suite</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#f0fdf4',
                            100: '#dcfce7',
                            500: '#22c55e',
                            600: '#16a34a',
                            700: '#15803d',
                        }
                    }
                }
            }
        }
    </script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Alpine.js -->
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        [x-cloak] { display: none !important; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased" x-data="proposalApp()">

    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-teal-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white font-bold text-xl">
                    ⚡
                </div>
                <div>
                    <h1 class="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                        Proposal Agent
                        <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" x-text="activeMode === 'freelance' ? '$2M+ Win Engine' : 'Academic & Professional'">
                        </span>
                    </h1>
                    <p class="text-xs text-slate-400" x-text="activeMode === 'freelance' ? 'Clients hire who makes them feel most understood & confident' : 'Bachelor\'s, Master\'s, and PhD Level Structured Proposals'"></p>
                </div>
            </div>

            <!-- Mode Switcher Tabs -->
            <div class="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800">
                <button 
                    @click="setMode('freelance')"
                    :class="activeMode === 'freelance' ? 'bg-emerald-600 text-white font-semibold shadow-md' : 'text-slate-400 hover:text-slate-200'"
                    class="text-xs px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5">
                    <i data-lucide="briefcase" class="w-3.5 h-3.5"></i>
                    <span>Freelance Pitch</span>
                </button>
                <button 
                    @click="setMode('academic')"
                    :class="activeMode === 'academic' ? 'bg-indigo-600 text-white font-semibold shadow-md' : 'text-slate-400 hover:text-slate-200'"
                    class="text-xs px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5">
                    <i data-lucide="graduation-cap" class="w-3.5 h-3.5"></i>
                    <span>Academic & Professional</span>
                </button>
            </div>

            <!-- Quick Controls -->
            <div class="flex items-center space-x-2">
                <button @click="openSettings = true" class="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition border border-slate-700" title="API Settings">
                    <i data-lucide="settings" class="w-4 h-4"></i>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

        <!-- ==================== MODE 1: FREELANCE STRATEGIST ==================== -->
        <div x-show="activeMode === 'freelance'" class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- LEFT COLUMN: Freelance Form (5 cols) -->
            <div class="lg:col-span-5 space-y-4">
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                    
                    <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                        <span class="text-sm font-semibold text-white flex items-center gap-2">
                            <i data-lucide="file-edit" class="w-4 h-4 text-emerald-400"></i> Freelance Project Parameters
                        </span>
                        <span class="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700" x-text="'Target: ' + platformLengths[form.platform]"></span>
                    </div>

                    <!-- Presets Selector -->
                    <div class="flex gap-2">
                        <button type="button" @click="loadPreset('1')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700">
                            ✨ AI Full-Stack
                        </button>
                        <button type="button" @click="loadPreset('2')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700">
                            📧 CRO Direct Email
                        </button>
                        <button type="button" @click="loadPreset('3')" class="text-xs px-2.5 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30">
                            🚩 Red Flag Demo
                        </button>
                    </div>

                    <!-- Platform Selection -->
                    <div>
                        <label class="block text-xs font-medium text-slate-400 mb-1.5">1. Target Platform</label>
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
                            <template x-for="p in platforms" :key="p">
                                <button type="button" 
                                    @click="form.platform = p; checkJobRedFlags()" 
                                    :class="form.platform === p ? 'bg-emerald-600 text-white font-medium shadow-md border-emerald-500' : 'bg-slate-800/80 text-slate-400 hover:bg-slate-800 border-slate-700'"
                                    class="text-xs py-2 px-2 rounded-lg border transition text-center truncate"
                                    x-text="p">
                                </button>
                            </template>
                        </div>
                    </div>

                    <!-- Tone Selection -->
                    <div>
                        <label class="block text-xs font-medium text-slate-400 mb-1.5">2. Tone of Voice</label>
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
                            <template x-for="t in tones" :key="t">
                                <button type="button" 
                                    @click="form.tone = t" 
                                    :class="form.tone === t ? 'bg-slate-700 text-white border-slate-500 font-medium' : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800 border-slate-700/80'"
                                    class="text-xs py-1.5 px-2 rounded-lg border transition text-center truncate"
                                    x-text="t">
                                </button>
                            </template>
                        </div>
                    </div>

                    <!-- Job Description -->
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <label class="block text-xs font-medium text-slate-300">
                                3. Client's Job Post / Brief <span class="text-emerald-400">*</span>
                            </label>
                            <span class="text-[11px] text-slate-500" x-text="form.job_description.length + ' chars'"></span>
                        </div>
                        <textarea 
                            x-model="form.job_description" 
                            @input.debounce.400ms="checkJobRedFlags()"
                            rows="4" 
                            placeholder="Paste client's full post here..."
                            class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition resize-y">
                        </textarea>
                    </div>

                    <!-- Live Red Flag Pre-warning banner -->
                    <div x-show="liveRedFlag" x-cloak class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2">
                        <i data-lucide="alert-triangle" class="w-4 h-4 shrink-0 mt-0.5 text-amber-400"></i>
                        <div>
                            <span class="font-bold">Caution Detected: </span>
                            <span x-text="liveRedFlag"></span>
                        </div>
                    </div>

                    <!-- Freelancer Profile & Experience -->
                    <div class="space-y-3">
                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">4. Your Freelancer Profile / Niche</label>
                            <input type="text" x-model="form.freelancer_profile" placeholder="e.g. Senior AI Systems Engineer with 7 years experience" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">5. Relevant Experience</label>
                            <textarea rows="2" x-model="form.relevant_experience" placeholder="What relevant past project directly maps to their problem?" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 resize-y"></textarea>
                        </div>
                    </div>

                    <!-- Proposed Approach -->
                    <div>
                        <label class="block text-xs font-medium text-slate-300 mb-1">6. Proposed Approach</label>
                        <textarea rows="2" x-model="form.proposed_approach" placeholder="Your specific workflow, tools, and what you do differently" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 resize-y"></textarea>
                    </div>

                    <!-- Budget & Result -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">7. Budget / Rate</label>
                            <input type="text" x-model="form.budget_range" placeholder="e.g. $4,000 - $5,500" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">8. Quantifiable Result</label>
                            <input type="text" x-model="form.achievements" placeholder="e.g. Reduced latency by 68%" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-emerald-500">
                        </div>
                    </div>

                    <!-- Generate Button -->
                    <div class="pt-2">
                        <button 
                            @click="generateProposals()" 
                            :disabled="loading || !form.job_description.trim()"
                            class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-semibold text-sm shadow-lg shadow-emerald-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50">
                            <span x-show="!loading" class="flex items-center gap-2">
                                <i data-lucide="zap" class="w-4 h-4"></i> Generate High-Converting Proposals
                            </span>
                            <span x-show="loading" class="flex items-center gap-2">
                                <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Analyzing psychology & crafting variations...
                            </span>
                        </button>
                    </div>

                </div>
            </div>

            <!-- RIGHT COLUMN: Freelance Output (7 cols) -->
            <div class="lg:col-span-7 space-y-5">
                <div x-show="!result && !loading" class="bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl p-12 text-center flex flex-col items-center justify-center min-h-[460px]">
                    <div class="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-400 mb-4">
                        <i data-lucide="sparkles" class="w-7 h-7 text-emerald-400"></i>
                    </div>
                    <h3 class="text-base font-semibold text-slate-200 mb-1">No proposal generated yet</h3>
                    <p class="text-xs text-slate-400 max-w-sm mb-5">
                        Fill in client job details on the left, or load one of the presets to see dual variations and psychological coaching.
                    </p>
                </div>

                <div x-show="loading" x-cloak class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-pulse">
                    <div class="h-6 bg-slate-800 rounded w-1/3"></div>
                    <div class="h-24 bg-slate-800/60 rounded"></div>
                    <div class="h-28 bg-slate-800/60 rounded"></div>
                </div>

                <div x-show="result" x-cloak class="space-y-5">
                    <!-- Red Flag Alert Banner -->
                    <div x-show="result && result.red_flag_alert" class="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                        <div class="flex items-center gap-2 font-bold mb-1 text-rose-400">
                            <i data-lucide="flag" class="w-4 h-4"></i> RED FLAG ALERT
                        </div>
                        <p x-text="result ? result.red_flag_alert : ''"></p>
                    </div>

                    <!-- Variation A -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
                        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                            <div>
                                <span class="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Variation A</span>
                                <span class="text-xs text-slate-400 ml-2">Lead with Client Pain</span>
                            </div>
                            <div class="flex items-center gap-3">
                                <span class="text-xs font-mono text-slate-400" x-text="(result?.variation_a?.word_count || 0) + ' words'"></span>
                                <button @click="copyText(result?.variation_a?.text, 'a')" class="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition flex items-center gap-1 border border-slate-700">
                                    <span x-text="copiedA ? 'Copied!' : 'Copy'"></span>
                                </button>
                            </div>
                        </div>
                        <div class="text-xs text-slate-200 whitespace-pre-line leading-relaxed font-sans" x-text="result?.variation_a?.text"></div>
                    </div>

                    <!-- Variation B -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
                        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                            <div>
                                <span class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">Variation B</span>
                                <span class="text-xs text-slate-400 ml-2">Lead with Bold Result</span>
                            </div>
                            <div class="flex items-center gap-3">
                                <span class="text-xs font-mono text-slate-400" x-text="(result?.variation_b?.word_count || 0) + ' words'"></span>
                                <button @click="copyText(result?.variation_b?.text, 'b')" class="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition flex items-center gap-1 border border-slate-700">
                                    <span x-text="copiedB ? 'Copied!' : 'Copy'"></span>
                                </button>
                            </div>
                        </div>
                        <div class="text-xs text-slate-200 whitespace-pre-line leading-relaxed font-sans" x-text="result?.variation_b?.text"></div>
                    </div>

                    <!-- Coaching Note -->
                    <div class="bg-gradient-to-br from-slate-900 to-slate-900/80 border border-emerald-500/20 rounded-2xl p-5 space-y-3">
                        <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
                            <span class="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                                <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Senior Strategist Coaching Note
                            </span>
                            <button @click="downloadMarkdown()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i> Download Markdown
                            </button>
                        </div>
                        <div class="space-y-2 text-xs">
                            <p><span class="font-semibold text-slate-300">Stronger Variation:</span> <span class="text-emerald-300" x-text="result?.coaching_note?.stronger_variation"></span> — <span class="text-slate-400" x-text="result?.coaching_note?.stronger_reason"></span></p>
                            <p><span class="font-semibold text-slate-300">What to Personalize:</span> <span class="text-slate-400" x-text="result?.coaching_note?.what_to_personalize"></span></p>
                            <p><span class="font-semibold text-slate-300">Smart Question to Add:</span> <span class="text-teal-300" x-text="result?.coaching_note?.smart_question"></span></p>
                            <p><span class="font-semibold text-slate-300">Win Probability Factors:</span> <span class="text-slate-400" x-text="result?.coaching_note?.win_probability_factors"></span></p>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <!-- ==================== MODE 2: ACADEMIC & PROFESSIONAL ASSISTANT ==================== -->
        <div x-show="activeMode === 'academic'" x-cloak class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- LEFT COLUMN: Academic 4-Step Form (5 cols) -->
            <div class="lg:col-span-5 space-y-4">
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">

                    <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                        <span class="text-sm font-semibold text-white flex items-center gap-2">
                            <i data-lucide="graduation-cap" class="w-4 h-4 text-indigo-400"></i> Academic Proposal Wizard
                        </span>
                        <span class="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-mono">
                            7 Structured Sections
                        </span>
                    </div>

                    <!-- Quick Academic Presets -->
                    <div>
                        <label class="block text-xs font-medium text-slate-400 mb-1.5">Load Curated Presets</label>
                        <div class="flex flex-wrap gap-1.5">
                            <button type="button" @click="loadAcademicPreset('1')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                                🎓 Bachelor's (Education)
                            </button>
                            <button type="button" @click="loadAcademicPreset('2')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                                💼 Master's (Business)
                            </button>
                            <button type="button" @click="loadAcademicPreset('3')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                                🔬 PhD (Social Media)
                            </button>
                        </div>
                    </div>

                    <!-- STEP 1: Academic Level -->
                    <div>
                        <label class="block text-xs font-medium text-slate-300 mb-1.5">
                            STEP 1 — What is your academic level? <span class="text-indigo-400">*</span>
                        </label>
                        <div class="grid grid-cols-3 gap-2">
                            <template x-for="lvl in ['Bachelor\'s', 'Master\'s', 'PhD']" :key="lvl">
                                <button type="button"
                                    @click="academicForm.academic_level = lvl"
                                    :class="academicForm.academic_level === lvl ? 'bg-indigo-600 text-white font-semibold shadow-md shadow-indigo-600/30 border-indigo-500' : 'bg-slate-800 text-slate-400 hover:bg-slate-700 border-slate-700'"
                                    class="text-xs py-2 px-2 rounded-xl border text-center transition"
                                    x-text="lvl">
                                </button>
                            </template>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-1.5 italic" x-text="
                            academicForm.academic_level === 'Bachelor\'s' ? '• Bachelor\'s Tone: Clear, foundational, accessible, direct practical application' :
                            academicForm.academic_level === 'Master\'s' ? '• Master\'s Tone: Analytical, structured, empirical, comparative frameworks' :
                            '• PhD Tone: Advanced, scholarly, theoretical gap-focused, methodology-rich'
                        "></p>
                    </div>

                    <!-- STEP 2: Proposal Type -->
                    <div>
                        <label class="block text-xs font-medium text-slate-300 mb-1.5">
                            STEP 2 — What type of proposal would you like to write? <span class="text-indigo-400">*</span>
                        </label>
                        <div class="grid grid-cols-1 gap-1.5">
                            <template x-for="pt in ['Education Proposal', 'Business Proposal', 'Social Media Proposal']" :key="pt">
                                <button type="button"
                                    @click="academicForm.proposal_type = pt"
                                    :class="academicForm.proposal_type === pt ? 'bg-slate-800 text-indigo-400 border-indigo-500 font-semibold ring-1 ring-indigo-500/50' : 'bg-slate-950/60 text-slate-400 hover:bg-slate-800 border-slate-800'"
                                    class="text-xs py-2 px-3 rounded-xl border text-left transition flex items-center justify-between">
                                    <span x-text="pt"></span>
                                    <i data-lucide="check" class="w-3.5 h-3.5" x-show="academicForm.proposal_type === pt"></i>
                                </button>
                            </template>
                        </div>
                    </div>

                    <!-- STEP 3: Gather Details -->
                    <div class="space-y-3 pt-1 border-t border-slate-800">
                        <span class="text-xs font-semibold text-slate-300 block">STEP 3 — Proposal Details</span>

                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Topic / Idea <span class="text-indigo-400">*</span></label>
                            <input type="text" x-model="academicForm.topic" placeholder="e.g. Gamified Mobile Microlearning in STEM Education" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500">
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Purpose / Objective <span class="text-indigo-400">*</span></label>
                            <textarea rows="2" x-model="academicForm.purpose" placeholder="e.g. Evaluate whether mobile problem sets increase conceptual recall compared to traditional worksheets" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-y"></textarea>
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Target Audience</label>
                            <input type="text" x-model="academicForm.target_audience" placeholder="e.g. Academic Faculty Review Committee / Enterprise Stakeholders" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500">
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Specific Requirements / Guidelines (Optional)</label>
                            <input type="text" x-model="academicForm.specific_requirements" placeholder="e.g. APA 7th edition, 4-month classroom pilot scope" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500">
                        </div>
                    </div>

                    <!-- Generate Academic Button -->
                    <div class="pt-2">
                        <button 
                            @click="generateAcademicProposal()" 
                            :disabled="academicLoading || !academicForm.topic.trim() || !academicForm.purpose.trim()"
                            class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-teal-500 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50">
                            <span x-show="!academicLoading" class="flex items-center gap-2">
                                <i data-lucide="book-open" class="w-4 h-4"></i> Generate 7-Section Academic Proposal
                            </span>
                            <span x-show="academicLoading" class="flex items-center gap-2">
                                <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Calibrating academic rigor & synthesizing sections...
                            </span>
                        </button>
                    </div>

                </div>
            </div>

            <!-- RIGHT COLUMN: Academic Output (7 cols) -->
            <div class="lg:col-span-7 space-y-5">
                
                <!-- Placeholder -->
                <div x-show="!academicResult && !academicLoading" class="bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl p-12 text-center flex flex-col items-center justify-center min-h-[460px]">
                    <div class="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-400 mb-4">
                        <i data-lucide="graduation-cap" class="w-7 h-7 text-indigo-400"></i>
                    </div>
                    <h3 class="text-base font-semibold text-slate-200 mb-1">No academic proposal generated</h3>
                    <p class="text-xs text-slate-400 max-w-sm mb-5">
                        Select your academic level and proposal type, then fill in details to generate a comprehensive 7-section structured proposal.
                    </p>
                    <div class="flex gap-2">
                        <button @click="loadAcademicPreset('1')" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                            Bachelor's Demo
                        </button>
                        <button @click="loadAcademicPreset('2')" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                            Master's Demo
                        </button>
                        <button @click="loadAcademicPreset('3')" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                            PhD Demo
                        </button>
                    </div>
                </div>

                <!-- Loading Skeleton -->
                <div x-show="academicLoading" x-cloak class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-pulse">
                    <div class="h-6 bg-slate-800 rounded w-2/3"></div>
                    <div class="h-20 bg-slate-800/60 rounded"></div>
                    <div class="h-24 bg-slate-800/60 rounded"></div>
                    <div class="h-32 bg-slate-800/60 rounded"></div>
                </div>

                <!-- Rendered 7 Sections -->
                <div x-show="academicResult" x-cloak class="space-y-4">
                    
                    <!-- Header Card -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
                        <div class="flex items-start justify-between gap-4">
                            <div>
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" x-text="academicResult ? academicResult.academic_level : ''"></span>
                                    <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700" x-text="academicResult ? academicResult.proposal_type : ''"></span>
                                </div>
                                <h2 class="text-base font-bold text-white" x-text="academicResult ? academicResult.title : ''"></h2>
                            </div>
                            <div class="flex items-center gap-2 shrink-0">
                                <button @click="copyAcademicMarkdown()" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition flex items-center gap-1.5 border border-slate-700">
                                    <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                    <span x-text="academicCopied ? 'Copied!' : 'Copy Markdown'"></span>
                                </button>
                                <button @click="downloadAcademicMarkdown()" class="text-xs px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1.5 shadow-md shadow-indigo-600/30">
                                    <i data-lucide="download" class="w-3.5 h-3.5"></i>
                                    <span>Download .md</span>
                                </button>
                            </div>
                        </div>

                        <!-- Calibration insights -->
                        <div class="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-center justify-between">
                            <span x-text="academicResult ? academicResult.level_insights : ''"></span>
                            <span class="font-mono text-slate-400 shrink-0 ml-2" x-text="(academicResult?.word_count || 0) + ' words'"></span>
                        </div>
                    </div>

                    <!-- 7 Section Cards -->
                    <!-- 1. Title -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow space-y-1.5">
                        <span class="text-xs font-bold text-indigo-400">1. Title</span>
                        <p class="text-xs text-slate-200 font-medium" x-text="academicResult?.title"></p>
                    </div>

                    <!-- 2. Introduction / Background -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow space-y-1.5">
                        <span class="text-xs font-bold text-indigo-400">2. Introduction / Background</span>
                        <p class="text-xs text-slate-300 leading-relaxed" x-text="academicResult?.introduction_background"></p>
                    </div>

                    <!-- 3. Problem Statement -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow space-y-1.5">
                        <span class="text-xs font-bold text-indigo-400">3. Problem Statement</span>
                        <p class="text-xs text-slate-300 leading-relaxed" x-text="academicResult?.problem_statement"></p>
                    </div>

                    <!-- 4. Objectives -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow space-y-1.5">
                        <span class="text-xs font-bold text-indigo-400">4. Objectives</span>
                        <ul class="list-disc list-inside space-y-1 text-xs text-slate-300">
                            <template x-for="obj in (academicResult?.objectives || [])" :key="obj">
                                <li class="leading-relaxed" x-text="obj"></li>
                            </template>
                        </ul>
                    </div>

                    <!-- 5. Methodology or Approach -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow space-y-1.5">
                        <span class="text-xs font-bold text-indigo-400">5. Methodology or Approach</span>
                        <p class="text-xs text-slate-300 leading-relaxed" x-text="academicResult?.methodology_approach"></p>
                    </div>

                    <!-- 6. Expected Outcomes / Benefits -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow space-y-1.5">
                        <span class="text-xs font-bold text-indigo-400">6. Expected Outcomes / Benefits</span>
                        <p class="text-xs text-slate-300 leading-relaxed" x-text="academicResult?.expected_outcomes_benefits"></p>
                    </div>

                    <!-- 7. Conclusion -->
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow space-y-1.5">
                        <span class="text-xs font-bold text-indigo-400">7. Conclusion</span>
                        <p class="text-xs text-slate-300 leading-relaxed" x-text="academicResult?.conclusion"></p>
                    </div>

                </div>

            </div>

        </div>

    </main>

    <!-- Settings Modal -->
    <div x-show="openSettings" x-cloak class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
        <div @click.away="openSettings = false" class="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 class="text-sm font-semibold text-white flex items-center gap-2">
                    <i data-lucide="sliders" class="w-4 h-4 text-emerald-400"></i> AI Provider & API Settings
                </h3>
                <button @click="openSettings = false" class="text-slate-400 hover:text-white">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>

            <div class="space-y-3 text-xs">
                <div>
                    <label class="block font-medium text-slate-400 mb-1">Active AI Provider</label>
                    <select x-model="settings.provider" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-200">
                        <option value="offline">Offline Strategist Engine (Deterministic Zero-Cost)</option>
                        <option value="gemini">Google Gemini (Gemini 2.5 Flash)</option>
                        <option value="groq">Groq (Llama 3.3 70B Versatile)</option>
                        <option value="openai">OpenAI (GPT-4o Mini)</option>
                    </select>
                </div>

                <div x-show="settings.provider === 'gemini'">
                    <label class="block font-medium text-slate-400 mb-1">Google Gemini API Key</label>
                    <input type="password" x-model="settings.geminiKey" placeholder="AIzaSy..." class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-200">
                </div>

                <div x-show="settings.provider === 'groq'">
                    <label class="block font-medium text-slate-400 mb-1">Groq API Key</label>
                    <input type="password" x-model="settings.groqKey" placeholder="gsk_..." class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-200">
                </div>

                <div x-show="settings.provider === 'openai'">
                    <label class="block font-medium text-slate-400 mb-1">OpenAI API Key</label>
                    <input type="password" x-model="settings.openaiKey" placeholder="sk-..." class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-200">
                </div>
            </div>

            <div class="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button @click="openSettings = false" class="px-3 py-1.5 text-xs rounded-lg text-slate-400 hover:text-white">Cancel</button>
                <button @click="saveSettings()" class="px-4 py-1.5 text-xs rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium shadow">Save</button>
            </div>
        </div>
    </div>

    <script>
        function proposalApp() {
            return {
                activeMode: 'freelance', // 'freelance' or 'academic'
                platforms: ['Upwork', 'Direct Email', 'LinkedIn', 'Agency RFP'],
                tones: ['Professional', 'Friendly', 'Direct', 'Consultative'],
                platformLengths: {
                    'Upwork': '< 220 words (quick scan)',
                    'Direct Email': '< 300 words + subject line',
                    'LinkedIn': '100-150 words (short/chat)',
                    'Agency RFP': '< 350 words (structured)'
                },
                form: {
                    platform: 'Upwork',
                    tone: 'Professional',
                    job_description: '',
                    freelancer_profile: '',
                    relevant_experience: '',
                    proposed_approach: '',
                    budget_range: '',
                    achievements: ''
                },
                academicForm: {
                    academic_level: "Master's",
                    proposal_type: "Education Proposal",
                    topic: '',
                    purpose: '',
                    target_audience: 'Academic Faculty Review Committee',
                    specific_requirements: ''
                },
                settings: {
                    provider: localStorage.getItem('prop_provider') || 'offline',
                    geminiKey: localStorage.getItem('prop_gemini_key') || '',
                    groqKey: localStorage.getItem('prop_groq_key') || '',
                    openaiKey: localStorage.getItem('prop_openai_key') || ''
                },
                openSettings: false,
                loading: false,
                academicLoading: false,
                result: null,
                academicResult: null,
                liveRedFlag: null,
                copiedA: false,
                copiedB: false,
                academicCopied: false,

                init() {
                    lucide.createIcons();
                },

                setMode(m) {
                    this.activeMode = m;
                    setTimeout(() => lucide.createIcons(), 50);
                },

                async checkJobRedFlags() {
                    if (!this.form.job_description || this.form.job_description.length < 20) {
                        this.liveRedFlag = null;
                        return;
                    }
                    try {
                        const res = await fetch('/api/check-red-flags', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                job_description: this.form.job_description,
                                budget_range: this.form.budget_range
                            })
                        });
                        const data = await res.json();
                        this.liveRedFlag = data.has_flags ? data.alert_text : null;
                    } catch (e) {
                        console.error(e);
                    }
                },

                async loadPreset(key) {
                    try {
                        const res = await fetch('/api/presets');
                        const presets = await res.json();
                        if (presets[key]) {
                            const inp = presets[key].input;
                            this.form.platform = inp.platform;
                            this.form.tone = inp.tone;
                            this.form.job_description = inp.job_description;
                            this.form.freelancer_profile = inp.freelancer_profile;
                            this.form.relevant_experience = inp.relevant_experience;
                            this.form.proposed_approach = inp.proposed_approach;
                            this.form.budget_range = inp.budget_range || '';
                            this.form.achievements = inp.achievements || '';
                            this.checkJobRedFlags();
                        }
                    } catch (e) {
                        console.error('Error loading preset:', e);
                    }
                },

                async loadAcademicPreset(key) {
                    try {
                        const res = await fetch('/api/academic/presets');
                        const presets = await res.json();
                        if (presets[key]) {
                            const inp = presets[key].input;
                            this.academicForm.academic_level = inp.academic_level;
                            this.academicForm.proposal_type = inp.proposal_type;
                            this.academicForm.topic = inp.topic;
                            this.academicForm.purpose = inp.purpose;
                            this.academicForm.target_audience = inp.target_audience || '';
                            this.academicForm.specific_requirements = inp.specific_requirements || '';
                        }
                    } catch (e) {
                        console.error('Error loading academic preset:', e);
                    }
                },

                async generateProposals() {
                    this.loading = true;
                    this.result = null;
                    try {
                        let activeApiKey = null;
                        if (this.settings.provider === 'gemini') activeApiKey = this.settings.geminiKey;
                        else if (this.settings.provider === 'groq') activeApiKey = this.settings.groqKey;
                        else if (this.settings.provider === 'openai') activeApiKey = this.settings.openaiKey;

                        const payload = {
                            ...this.form,
                            provider: this.settings.provider,
                            api_key: activeApiKey
                        };

                        const resp = await fetch('/api/generate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(payload)
                        });

                        if (!resp.ok) {
                            const err = await resp.json();
                            alert('Generation error: ' + (err.detail || 'Failed to generate proposal'));
                            return;
                        }

                        this.result = await resp.json();
                        setTimeout(() => lucide.createIcons(), 100);
                    } catch (e) {
                        alert('Network or server error: ' + e.message);
                    } finally {
                        this.loading = false;
                    }
                },

                async generateAcademicProposal() {
                    this.academicLoading = true;
                    this.academicResult = null;
                    try {
                        let activeApiKey = null;
                        if (this.settings.provider === 'gemini') activeApiKey = this.settings.geminiKey;
                        else if (this.settings.provider === 'groq') activeApiKey = this.settings.groqKey;
                        else if (this.settings.provider === 'openai') activeApiKey = this.settings.openaiKey;

                        const payload = {
                            ...this.academicForm,
                            provider: this.settings.provider,
                            api_key: activeApiKey
                        };

                        const resp = await fetch('/api/academic/generate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(payload)
                        });

                        if (!resp.ok) {
                            const err = await resp.json();
                            alert('Generation error: ' + (err.detail || 'Failed to generate academic proposal'));
                            return;
                        }

                        this.academicResult = await resp.json();
                        setTimeout(() => lucide.createIcons(), 100);
                    } catch (e) {
                        alert('Network or server error: ' + e.message);
                    } finally {
                        this.academicLoading = false;
                    }
                },

                saveSettings() {
                    localStorage.setItem('prop_provider', this.settings.provider);
                    localStorage.setItem('prop_gemini_key', this.settings.geminiKey);
                    localStorage.setItem('prop_groq_key', this.settings.groqKey);
                    localStorage.setItem('prop_openai_key', this.settings.openaiKey);
                    this.openSettings = false;
                },

                copyText(text, type) {
                    navigator.clipboard.writeText(text).then(() => {
                        if (type === 'a') {
                            this.copiedA = true;
                            setTimeout(() => this.copiedA = false, 2000);
                        } else {
                            this.copiedB = true;
                            setTimeout(() => this.copiedB = false, 2000);
                        }
                    });
                },

                copyAcademicMarkdown() {
                    if (!this.academicResult) return;
                    navigator.clipboard.writeText(this.academicResult.raw_markdown).then(() => {
                        this.academicCopied = true;
                        setTimeout(() => this.academicCopied = false, 2000);
                    });
                },

                downloadMarkdown() {
                    if (!this.result) return;
                    const blob = new Blob([this.result.raw_formatted], { type: 'text/markdown;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `proposal_${this.form.platform.toLowerCase().replace(/\\s+/g, '_')}.md`);
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                },

                downloadAcademicMarkdown() {
                    if (!this.academicResult) return;
                    const blob = new Blob([this.academicResult.raw_markdown], { type: 'text/markdown;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `academic_proposal_${this.academicForm.academic_level.toLowerCase().replace(/[^a-z0-9]/g, '_')}.md`);
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
