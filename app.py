"""
FastAPI Web Dashboard for Senior Freelance Proposal Strategist Agent.
Includes a modern responsive UI (Tailwind CSS, Alpine.js, Lucide icons),
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
    Platform, Tone, lint_proposal, analyze_red_flags
)
from presets import PRESETS

app = FastAPI(
    title="Freelance Proposal Strategist Agent",
    description="High-converting AI proposal generation for Upwork, Direct Outreach, LinkedIn, and Agency RFPs",
    version="1.0.0"
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

class RedFlagCheckRequest(BaseModel):
    job_description: str
    budget_range: Optional[str] = ""

class LintRequest(BaseModel):
    proposal_text: str
    platform: Platform = Platform.UPWORK

@app.get("/api/presets", response_model=Dict[str, Any])
async def get_presets():
    """Return available curated demo presets."""
    return {
        k: {
            "title": v["title"],
            "description": v["description"],
            "input": v["input"].model_dump()
        }
        for k, v in PRESETS.items()
    }

@app.post("/api/generate", response_model=ProposalResponse)
async def generate_proposal_endpoint(req: GenerateRequest):
    """Generate two proposal variations with red flag analysis and coaching note."""
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
    """Serve the complete interactive Web UI."""
    html_content = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proposal Strategist | $2M+ Contract Winning Agent</title>
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
    <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white font-bold text-xl">
                    ⚡
                </div>
                <div>
                    <h1 class="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                        Proposal Strategist
                        <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            $2M+ Win Engine
                        </span>
                    </h1>
                    <p class="text-xs text-slate-400">"Clients hire who makes them feel most understood & confident"</p>
                </div>
            </div>

            <!-- Quick Controls -->
            <div class="flex items-center space-x-3">
                <button @click="loadPreset('1')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center gap-1 border border-slate-700">
                    <span>✨ Full-Stack Preset</span>
                </button>
                <button @click="loadPreset('3')" class="text-xs px-2.5 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 transition flex items-center gap-1 border border-amber-500/30">
                    <span>🚩 Red Flag Demo</span>
                </button>
                <button @click="openSettings = true" class="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition border border-slate-700" title="API Settings">
                    <i data-lucide="settings" class="w-4 h-4"></i>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- LEFT COLUMN: Form Inputs (5 cols) -->
            <div class="lg:col-span-5 space-y-4">
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                    
                    <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                        <span class="text-sm font-semibold text-white flex items-center gap-2">
                            <i data-lucide="file-edit" class="w-4 h-4 text-emerald-400"></i> Project Parameters
                        </span>
                        <!-- Platform Length Guide Badge -->
                        <span class="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700" x-text="'Target: ' + platformLengths[form.platform]"></span>
                    </div>

                    <!-- Platform Selection -->
                    <div>
                        <label class="block text-xs font-medium text-slate-400 mb-1.5">1. Target Platform</label>
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
                            <template x-for="p in platforms" :key="p">
                                <button type="button" 
                                    @click="form.platform = p; checkJobRedFlags()" 
                                    :class="form.platform === p ? 'bg-emerald-600 text-white font-medium shadow-md shadow-emerald-600/30 border-emerald-500' : 'bg-slate-800/80 text-slate-400 hover:bg-slate-800 border-slate-700'"
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
                                3. Client's Job Post / Project Brief <span class="text-emerald-400">*</span>
                            </label>
                            <span class="text-[11px] text-slate-500" x-text="form.job_description.length + ' chars'"></span>
                        </div>
                        <textarea 
                            x-model="form.job_description" 
                            @input.debounce.400ms="checkJobRedFlags()"
                            rows="4" 
                            placeholder="Paste the full client post here (specifications, requirements, constraints)..."
                            class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition resize-y">
                        </textarea>
                    </div>

                    <!-- Live Red Flag Pre-warning banner if triggered while typing -->
                    <div x-show="liveRedFlag" x-cloak class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2 animate-pulse">
                        <i data-lucide="alert-triangle" class="w-4 h-4 shrink-0 mt-0.5 text-amber-400"></i>
                        <div>
                            <span class="font-bold">Caution Detected: </span>
                            <span x-text="liveRedFlag"></span>
                        </div>
                    </div>

                    <!-- Freelancer Profile & Relevant Experience -->
                    <div class="space-y-3">
                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">
                                4. Your Freelancer Profile / Niche
                            </label>
                            <input type="text" x-model="form.freelancer_profile" placeholder="e.g. Senior AI Systems Engineer with 7 years production Python/Next.js experience" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">
                                5. Most Relevant Experience for THIS Project
                            </label>
                            <textarea rows="2" x-model="form.relevant_experience" placeholder="What relevant past project directly maps to their problem?" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 resize-y"></textarea>
                        </div>
                    </div>

                    <!-- Proposed Approach -->
                    <div>
                        <label class="block text-xs font-medium text-slate-300 mb-1">
                            6. Proposed Technical Approach
                        </label>
                        <textarea rows="2" x-model="form.proposed_approach" placeholder="Your specific workflow, tools, architecture, and what you do differently" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 resize-y"></textarea>
                    </div>

                    <!-- Budget & Achievements Grid -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">7. Budget Range / Rate</label>
                            <input type="text" x-model="form.budget_range" placeholder="e.g. $4,000 - $5,500" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">8. Quantifiable Result / Proof</label>
                            <input type="text" x-model="form.achievements" placeholder="e.g. Reduced load time by 64%" class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-emerald-500">
                        </div>
                    </div>

                    <!-- Engine Choice & Generate Button -->
                    <div class="pt-2">
                        <button 
                            @click="generateProposals()" 
                            :disabled="loading || !form.job_description.trim()"
                            class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-semibold text-sm shadow-lg shadow-emerald-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
                            <template x-if="!loading">
                                <span class="flex items-center gap-2">
                                    <i data-lucide="zap" class="w-4 h-4"></i> Generate High-Converting Proposals
                                </span>
                            </template>
                            <template x-if="loading">
                                <span class="flex items-center gap-2">
                                    <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                    Analyzing psychology & crafting variations...
                                </span>
                            </template>
                        </button>
                    </div>

                </div>
            </div>

            <!-- RIGHT COLUMN: Output & Strategic Variations (7 cols) -->
            <div class="lg:col-span-7 space-y-5">

                <!-- Placeholder State -->
                <div x-show="!result && !loading" class="bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl p-12 text-center flex flex-col items-center justify-center min-h-[460px]">
                    <div class="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-400 mb-4">
                        <i data-lucide="sparkles" class="w-7 h-7 text-emerald-400"></i>
                    </div>
                    <h3 class="text-base font-semibold text-slate-200 mb-1">No proposal generated yet</h3>
                    <p class="text-xs text-slate-400 max-w-sm mb-5">
                        Fill in your client job details on the left, or load one of the battle-tested presets to see both variations with instant coaching.
                    </p>
                    <div class="flex flex-wrap gap-2 justify-center">
                        <button @click="loadPreset('1')" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                            Load SaaS Developer Preset
                        </button>
                        <button @click="loadPreset('2')" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                            Load CRO Direct Email Preset
                        </button>
                        <button @click="loadPreset('4')" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                            Load Agency RFP Preset
                        </button>
                    </div>
                </div>

                <!-- Loading Skeleton -->
                <div x-show="loading" x-cloak class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-pulse">
                    <div class="h-6 bg-slate-800 rounded w-1/3"></div>
                    <div class="h-24 bg-slate-800/60 rounded"></div>
                    <div class="h-28 bg-slate-800/60 rounded"></div>
                </div>

                <!-- Actual Generated Results -->
                <div x-show="result && !loading" x-cloak class="space-y-5">

                    <!-- RED FLAG ALERT BANNER -->
                    <template x-if="result && result.red_flag_alert">
                        <div class="p-4 rounded-2xl bg-red-950/40 border border-red-500/40 text-red-200 text-xs shadow-lg shadow-red-950/20">
                            <div class="flex items-center gap-2 font-bold text-red-400 mb-1">
                                <i data-lucide="flag" class="w-4 h-4 text-red-500"></i>
                                🚩 RED FLAG ALERT
                            </div>
                            <p class="text-red-200/90 leading-relaxed" x-text="result.red_flag_alert"></p>
                        </div>
                    </template>

                    <!-- Top Action Bar -->
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Generated Variations</span>
                            <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" x-text="'Engine: ' + result.provider_used"></span>
                        </div>
                        <div class="flex items-center gap-2">
                            <button @click="copyText(result.raw_formatted, 'full')" class="text-xs px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1.5">
                                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                <span x-text="copiedFull ? 'Copied!' : 'Copy All'"></span>
                            </button>
                            <button @click="downloadMarkdown()" class="text-xs px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1.5">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i>
                                <span>Export .md</span>
                            </button>
                        </div>
                    </div>

                    <!-- VARIATION A CARD -->
                    <div class="bg-slate-900 border border-slate-800 hover:border-slate-700 transition rounded-2xl p-5 space-y-3 relative group shadow-xl">
                        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                            <div class="flex items-center gap-2">
                                <span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                    VARIATION A
                                </span>
                                <span class="text-xs text-slate-300 font-medium truncate" x-text="result.variation_a.angle"></span>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="text-xs font-mono text-slate-400" x-text="result.variation_a.word_count + ' words'"></span>
                                <button @click="copyText(result.variation_a.text, 'a')" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition" title="Copy Variation A">
                                    <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Warnings if any -->
                        <template x-if="result.variation_a.warnings && result.variation_a.warnings.length">
                            <div class="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300">
                                <span class="font-bold">Linter Notice: </span>
                                <span x-text="result.variation_a.warnings.join(' | ')"></span>
                            </div>
                        </template>

                        <div class="text-xs text-slate-200 leading-relaxed whitespace-pre-line font-sans" x-text="result.variation_a.text"></div>
                    </div>

                    <!-- VARIATION B CARD -->
                    <div class="bg-slate-900 border border-slate-800 hover:border-slate-700 transition rounded-2xl p-5 space-y-3 relative group shadow-xl">
                        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                            <div class="flex items-center gap-2">
                                <span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20">
                                    VARIATION B
                                </span>
                                <span class="text-xs text-slate-300 font-medium truncate" x-text="result.variation_b.angle"></span>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="text-xs font-mono text-slate-400" x-text="result.variation_b.word_count + ' words'"></span>
                                <button @click="copyText(result.variation_b.text, 'b')" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition" title="Copy Variation B">
                                    <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Warnings if any -->
                        <template x-if="result.variation_b.warnings && result.variation_b.warnings.length">
                            <div class="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300">
                                <span class="font-bold">Linter Notice: </span>
                                <span x-text="result.variation_b.warnings.join(' | ')"></span>
                            </div>
                        </template>

                        <div class="text-xs text-slate-200 leading-relaxed whitespace-pre-line font-sans" x-text="result.variation_b.text"></div>
                    </div>

                    <!-- COACHING NOTE CARD -->
                    <div class="bg-gradient-to-b from-slate-900 to-slate-950 border border-emerald-500/30 rounded-2xl p-5 shadow-xl space-y-3">
                        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                            <div class="flex items-center gap-2 font-bold text-xs text-emerald-400">
                                <i data-lucide="bar-chart-2" class="w-4 h-4"></i> 📊 COACHING NOTE
                            </div>
                            <span class="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300" x-text="'Recommended: ' + result.coaching_note.stronger_variation"></span>
                        </div>

                        <div class="grid grid-cols-1 gap-3 text-xs">
                            <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800">
                                <span class="font-semibold text-slate-300 block mb-1">🎯 Stronger Variation Rationale</span>
                                <p class="text-slate-400" x-text="result.coaching_note.stronger_reason"></p>
                            </div>

                            <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800">
                                <span class="font-semibold text-slate-300 block mb-1">✍️ What to Personalize Before Sending</span>
                                <p class="text-slate-400" x-text="result.coaching_note.what_to_personalize"></p>
                            </div>

                            <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800">
                                <span class="font-semibold text-slate-300 block mb-1">💡 Smart Question to Add</span>
                                <p class="text-slate-400 italic" x-text="'\"' + result.coaching_note.smart_question + '\"'"></p>
                            </div>

                            <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800">
                                <span class="font-semibold text-slate-300 block mb-1">🏆 Win Probability Factors</span>
                                <p class="text-slate-400" x-text="result.coaching_note.win_probability_factors"></p>
                            </div>
                        </div>
                    </div>

                </div>

            </div>

        </div>
    </main>

    <!-- Settings Modal -->
    <div x-show="openSettings" x-cloak class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl" @click.away="openSettings = false">
            <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                    <i data-lucide="sliders" class="w-4 h-4 text-emerald-400"></i> Strategy Engine & API Configuration
                </h3>
                <button @click="openSettings = false" class="text-slate-400 hover:text-white">✕</button>
            </div>

            <div class="space-y-3 text-xs">
                <div>
                    <label class="block font-medium text-slate-300 mb-1">Default Strategy Engine</label>
                    <select x-model="settings.provider" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-emerald-500">
                        <option value="offline">Offline Strategic Engine (Zero API Keys Needed)</option>
                        <option value="gemini">Google Gemini (Gemini 2.5 Flash / 1.5 Pro)</option>
                        <option value="groq">Groq (Llama 3.3 70B Versatile)</option>
                        <option value="openai">OpenAI (GPT-4o / GPT-4o Mini)</option>
                        <option value="ollama">Ollama / Local LLM (localhost:11434)</option>
                    </select>
                </div>

                <div x-show="settings.provider === 'gemini'">
                    <label class="block font-medium text-slate-300 mb-1">Gemini API Key</label>
                    <input type="password" x-model="settings.geminiKey" placeholder="AIzaSy..." class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-100">
                    <p class="text-[10px] text-slate-500 mt-1">Can also be configured via GEMINI_API_KEY environment variable.</p>
                </div>

                <div x-show="settings.provider === 'groq'">
                    <label class="block font-medium text-slate-300 mb-1">Groq API Key</label>
                    <input type="password" x-model="settings.groqKey" placeholder="gsk_..." class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-100">
                </div>

                <div x-show="settings.provider === 'openai'">
                    <label class="block font-medium text-slate-300 mb-1">OpenAI API Key</label>
                    <input type="password" x-model="settings.openaiKey" placeholder="sk-..." class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-100">
                </div>
            </div>

            <div class="pt-2 flex justify-end gap-2">
                <button @click="saveSettings()" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition">
                    Save Configuration
                </button>
            </div>
        </div>
    </div>

    <!-- Application Logic -->
    <script>
        function proposalApp() {
            return {
                platforms: ['Upwork', 'Direct Email', 'LinkedIn', 'Agency RFP', 'Other'],
                tones: ['Professional', 'Friendly', 'Direct', 'Consultative'],
                platformLengths: {
                    'Upwork': '180–220 words',
                    'Direct Email': '220–300 words',
                    'LinkedIn': '100–150 words',
                    'Agency RFP': '250–350 words',
                    'Other': '150–300 words'
                },
                form: {
                    platform: 'Upwork',
                    tone: 'Direct',
                    job_description: '',
                    freelancer_profile: '',
                    relevant_experience: '',
                    proposed_approach: '',
                    budget_range: '',
                    achievements: ''
                },
                settings: {
                    provider: localStorage.getItem('prop_provider') || 'offline',
                    geminiKey: localStorage.getItem('prop_gemini_key') || '',
                    groqKey: localStorage.getItem('prop_groq_key') || '',
                    openaiKey: localStorage.getItem('prop_openai_key') || ''
                },
                openSettings: false,
                loading: false,
                result: null,
                liveRedFlag: null,
                copiedA: false,
                copiedB: false,
                copiedFull: false,

                init() {
                    lucide.createIcons();
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
                        if (data.has_flags) {
                            this.liveRedFlag = data.alert_text;
                        } else {
                            this.liveRedFlag = null;
                        }
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
                        } else if (type === 'b') {
                            this.copiedB = true;
                            setTimeout(() => this.copiedB = false, 2000);
                        } else {
                            this.copiedFull = true;
                            setTimeout(() => this.copiedFull = false, 2000);
                        }
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
