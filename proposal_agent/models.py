"""
Data models for the Proposal Strategist & Academic Assistant Agent.
Supports both Freelance & High-Ticket Proposals and Academic/Professional Proposals (Bachelor's, Master's, PhD).
"""

from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

# ==================== Freelance Proposal Models ====================

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
    title: str
    angle: str
    text: str
    word_count: int = 0
    warnings: List[str] = Field(default_factory=list)

class CoachingNote(BaseModel):
    stronger_variation: str
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

# ==================== Academic & Professional Proposal Models ====================

class AcademicLevel(str, Enum):
    BACHELORS = "Bachelor's"
    MASTERS = "Master's"
    PHD = "PhD"

class AcademicProposalType(str, Enum):
    EDUCATION = "Education Proposal"
    BUSINESS = "Business Proposal"
    SOCIAL_MEDIA = "Social Media Proposal"

class AcademicProposalInput(BaseModel):
    academic_level: AcademicLevel = Field(
        default=AcademicLevel.MASTERS,
        description="Academic depth: Bachelor's (foundational), Master's (analytical), or PhD (scholarly gap-focused)"
    )
    proposal_type: AcademicProposalType = Field(
        default=AcademicProposalType.EDUCATION,
        description="Niche: Education Proposal, Business Proposal, or Social Media Proposal"
    )
    topic: str = Field(
        ...,
        description="Topic or central project/research idea"
    )
    purpose: str = Field(
        ...,
        description="Purpose or primary objective"
    )
    target_audience: str = Field(
        default="Academic Faculty Review Committee",
        description="Target evaluation audience (e.g., University Committee, Enterprise Board, Department Heads)"
    )
    specific_requirements: Optional[str] = Field(
        default="",
        description="Any specific guidelines, constraints, citation styles, or institutional rubrics"
    )

class AcademicProposalSection(BaseModel):
    heading: str
    content: str

class AcademicProposalResponse(BaseModel):
    title: str
    academic_level: AcademicLevel
    proposal_type: AcademicProposalType
    introduction_background: str
    problem_statement: str
    objectives: List[str]
    methodology_approach: str
    expected_outcomes_benefits: str
    conclusion: str
    raw_markdown: str
    word_count: int
    provider_used: str = "offline"
    level_insights: str
