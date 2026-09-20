"""
Freelance Proposal Strategist Agent Package.
"""

from proposal_agent.models import (
    Platform,
    Tone,
    ProposalInput,
    ProposalResponse,
    ProposalVariation,
    CoachingNote,
    RedFlagResult,
    AcademicLevel,
    AcademicProposalType,
    AcademicProposalInput,
    AcademicProposalResponse
)
from proposal_agent.agent import ProposalStrategistAgent
from proposal_agent.rules_linter import lint_proposal, count_words
from proposal_agent.red_flag_detector import analyze_red_flags
from proposal_agent.academic_engine import generate_academic_offline

__all__ = [
    "ProposalStrategistAgent",
    "Platform",
    "Tone",
    "ProposalInput",
    "ProposalResponse",
    "ProposalVariation",
    "CoachingNote",
    "RedFlagResult",
    "AcademicLevel",
    "AcademicProposalType",
    "AcademicProposalInput",
    "AcademicProposalResponse",
    "generate_academic_offline",
    "lint_proposal",
    "count_words",
    "analyze_red_flags",
]

