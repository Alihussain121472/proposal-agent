"""
Data models for the Freelance Proposal Strategist Agent.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class Platform(str, Enum):
    UPWORK = "Upwork"
    DIRECT_EMAIL = "Direct Email"
    LINKEDIN = "LinkedIn"
    AGENCY_RFP = "Agency RFP"
    OTHER = "Other"

class Tone(str, Enum):
    PROFESSIONAL = "Professional"
    FRIENDLY = "Friendly"
    DIRECT = "Direct"
    CONSULTATIVE = "Consultative"

class ProposalInput(BaseModel):
    platform: Platform = Field(
        default=Platform.UPWORK,
        description="Where this proposal is being sent (Upwork / Direct Email / LinkedIn / Agency RFP / Other)"
    )
    job_description: str = Field(
        ...,
        description="The client's full job post or project brief"
    )
    freelancer_profile: str = Field(
        ...,
        description="Background, niche, skills, experience level"
    )
    relevant_experience: str = Field(
        ...,
        description="What the freelancer considers most relevant to this specific job"
    )
    proposed_approach: str = Field(
        ...,
        description="How the freelancer plans to tackle this project"
    )
    budget_range: Optional[str] = Field(
        default="",
        description="Freelancer's rate or price range for this project"
    )
    tone: Tone = Field(
        default=Tone.PROFESSIONAL,
        description="One of: Professional / Friendly / Direct / Consultative"
    )
    achievements: Optional[str] = Field(
        default="",
        description="Specific results, numbers, or case studies to use (situational proof if none provided)"
    )

class RedFlagResult(BaseModel):
    has_flags: bool = False
    reasons: List[str] = Field(default_factory=list)
    alert_text: Optional[str] = None

class ProposalVariation(BaseModel):
    title: str  # e.g. "VARIATION A — Lead with the client's pain and problem"
    angle: str  # e.g. "Lead with the client's pain and problem"
    text: str
    word_count: int = 0
    warnings: List[str] = Field(default_factory=list)

class CoachingNote(BaseModel):
    stronger_variation: str  # "Variation A" or "Variation B"
    stronger_reason: str
    what_to_personalize: str
    smart_question: str
    win_probability_factors: str

class ProposalResponse(BaseModel):
    red_flag_alert: Optional[str] = None
    variation_a: ProposalVariation
    variation_b: ProposalVariation
    coaching_note: CoachingNote
    raw_formatted: str
    provider_used: str = "offline"
    validation_status: str = "PASS"
