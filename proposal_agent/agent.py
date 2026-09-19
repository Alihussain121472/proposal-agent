"""
Main Proposal Strategist Agent class.
Unified interface for proposal generation, linting, red-flag analysis, and history tracking.
"""

import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from proposal_agent.models import (
    ProposalInput, ProposalResponse, RedFlagResult, Platform, Tone
)
from proposal_agent.red_flag_detector import analyze_red_flags
from proposal_agent.rules_linter import lint_proposal, count_words
from proposal_agent.llm_engine import generate_proposals
from proposal_agent.config import AgentConfig, get_config

class ProposalStrategistAgent:
    """
    Senior Freelance Proposal Strategist Agent.
    Helped freelancers win over $2M in contracts across Upwork, direct outreach, and agency pitches.
    """

    def __init__(self, config: Optional[AgentConfig] = None, history_file: str = "proposal_history.json"):
        self.config = config or get_config()
        self.history_file = history_file

    def generate(
        self,
        inp: ProposalInput,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> ProposalResponse:
        """
        Generate two winning proposal variations adhering strictly to client psychology,
        platform constraints, tone guidelines, and absolute rules.
        """
        response = generate_proposals(
            inp=inp,
            provider=provider,
            api_key=api_key,
            model=model,
            config=self.config
        )
        # Record in history
        self._record_history(inp, response)
        return response

    def check_red_flags(self, job_description: str, budget_range: str = "") -> RedFlagResult:
        """Scan a job description for critical red flags."""
        return analyze_red_flags(job_description, budget_range)

    def lint(self, proposal_text: str, platform: Platform = Platform.UPWORK) -> List[str]:
        """Lint a proposal text against the absolute negative rules."""
        return lint_proposal(proposal_text, platform)

    def _record_history(self, inp: ProposalInput, response: ProposalResponse):
        """Append generation result to local history JSON."""
        try:
            entries = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "platform": inp.platform.value,
                "tone": inp.tone.value,
                "job_excerpt": inp.job_description[:120] + "...",
                "red_flag": response.red_flag_alert,
                "variation_a_words": response.variation_a.word_count,
                "variation_b_words": response.variation_b.word_count,
                "provider": response.provider_used,
                "response": response.model_dump()
            }
            entries.insert(0, entry)
            # Keep last 50
            entries = entries[:50]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2)
        except Exception:
            pass  # Silent fail on history logging to avoid blocking generation

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve recent generation history."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []
