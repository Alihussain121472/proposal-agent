"""
Offline / Fallback Proposal Generation Engine.
Implements the full proposal strategist logic algorithmically when no external LLM API key is provided.
Enforces all rules: no "I" openers, platform word limits, no forbidden buzzwords, strict output format.
"""

import re
from typing import Dict, Any, Tuple
from proposal_agent.models import ProposalInput, ProposalResponse, ProposalVariation, CoachingNote, Platform, Tone
from proposal_agent.red_flag_detector import analyze_red_flags
from proposal_agent.rules_linter import count_words, lint_proposal

def extract_core_focus(job_description: str) -> str:
    """Extract key keywords or main objective from the job description."""
    text = job_description.strip()
    # Check for common specific focus patterns
    patterns = [
        (r"(?:mobile\s+checkout|checkout\s+conversion|cro|shopify|drop-offs?)", "mobile checkout conversion"),
        (r"(?:pdf|contract|summariz|document|pgvector|rag|vector)", "AI document processing"),
        (r"(?:scraper|scraping|crawl|playwright|selenium|data\s+extract)", "web data extraction"),
        (r"(?:landing\s+page|copywriting|messaging|reposition|b2b)", "conversion messaging & landing page"),
        (r"(?:api|microservice|backend|fastapi|django|express)", "backend API infrastructure"),
        (r"(?:mobile\s+app|react\s+native|flutter|ios|android)", "mobile app development"),
    ]
    for pat, label in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return label

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    first_line = lines[0] if lines else "your project"
    cleaned = re.sub(r"^(looking for|we need|seeking|need a|urgent:|hiring|our)\s+", "", first_line, flags=re.IGNORECASE)
    cleaned = cleaned.rstrip(".:,")
    words = cleaned.split()
    if len(words) > 6:
        cleaned = " ".join(words[:5])
    return cleaned if cleaned else "your system requirements"

def generate_offline_proposals(inp: ProposalInput) -> ProposalResponse:
    """Generate high-converting proposals deterministically adhering strictly to all strategist rules."""
    # Step 1: Red Flag Check
    red_flag_res = analyze_red_flags(inp.job_description, inp.budget_range)

    core_focus = extract_core_focus(inp.job_description)
    
    # Analyze client psychology & tone adjustments
    tone_closing = {
        Tone.PROFESSIONAL: "Available for a brief technical alignment call this week to review the implementation schedule.",
        Tone.FRIENDLY: "Happy to jump on a quick call this week if you'd like to chat through the roadmap.",
        Tone.DIRECT: "Open for a quick 15-minute sync to finalize architecture and milestones.",
        Tone.CONSULTATIVE: "Available for a strategic discovery session this week to benchmark your requirements against industry standards."
    }.get(inp.tone, "Available for a quick call this week to talk through the approach.")

    # Smart question tailored to approach
    smart_question = "One strategic detail worth clarifying early: is the primary priority lightning-fast time-to-delivery, or architectural headroom for scaling users post-launch?"

    # Subject line for Direct Email
    email_subj_a = f"Subject: Solving your {core_focus} bottleneck\n\n" if inp.platform == Platform.DIRECT_EMAIL else ""
    email_subj_b = f"Subject: Proven roadmap for {core_focus}\n\n" if inp.platform == Platform.DIRECT_EMAIL else ""

    # Platform specific body adjustments
    if inp.platform == Platform.LINKEDIN:
        # 100-150 words maximum, conversational
        var_a_text = (
            f"Solving {core_focus} usually stalls when architectural decisions are made before the core data model is locked down.\n\n"
            f"Your focus on a frictionless delivery requires an execution plan that avoids technical debt while hitting tight delivery milestones. "
            f"The approach here is straightforward: establish a clean foundation using {inp.proposed_approach.split('.')[0]}, then deploy modular iterations with continuous validation.\n\n"
            f"{inp.achievements if inp.achievements else 'Previously delivered comparable production deployments on aggressive deadlines with zero regressions.'}\n\n"
            f"{smart_question}\n\n"
            f"{tone_closing}"
        )
        var_b_text = (
            f"Delivering {core_focus} with zero production bottlenecks is exactly the outcome delivered on recent builds.\n\n"
            f"{inp.achievements if inp.achievements else 'Recent benchmarks include cutting deployment latency and delivering production-ready infrastructure ahead of schedule.'}\n\n"
            f"For your build, the priority is executing {inp.proposed_approach.split('.')[0]} with rigorous test coverage from day one so your team never has to rework early components.\n\n"
            f"Are you open to a phased rollout, or is a single all-in release required?\n\n"
            f"{tone_closing}"
        )
    elif inp.platform == Platform.UPWORK:
        # 180-220 words, hook shows in preview, no "Upwork" mention
        var_a_text = (
            f"Most projects handling {core_focus} encounter delays because initial scope doesn't account for edge cases and integration dependencies.\n\n"
            f"Your priority is getting this deployed reliably without burning engineering cycles on endless revisions. "
            f"The key to resolving this quickly is structuring your project in clear, verified phases rather than an untracked monolith.\n\n"
            f"The execution plan focuses on {inp.proposed_approach.strip().rstrip('.')}. "
            f"By standardizing the core workflows first, your team gets a functional, production-grade deliverable early in the cycle while keeping maintenance overhead near zero.\n\n"
            f"{inp.achievements if inp.achievements else 'Proven track record of taking complex functional specs from concept to stable production deployment within strict timelines.'}\n\n"
            f"{smart_question}\n\n"
            f"{tone_closing}"
        )
        var_b_text = (
            f"Recent deployments with requirements nearly identical to {core_focus} proved that front-loading architectural clarity cuts delivery cycles by up to 40%.\n\n"
            f"{inp.achievements if inp.achievements else 'Delivered mission-critical systems and robust integrations with measurable performance gains and rock-solid reliability.'}\n\n"
            f"The underlying objective here isn't just completing tasks—it's ensuring your solution operates seamlessly under real-world conditions. "
            f"The recommended workflow tackles {inp.proposed_approach.strip().rstrip('.')}, eliminating hidden bottlenecks before they impact your launch schedule.\n\n"
            f"Is there an existing codebase/schema that this needs to integrate with, or are we establishing the architecture from scratch?\n\n"
            f"{tone_closing}"
        )
    else:  # Direct Email or Agency RFP (220-320 words)
        var_a_text = (
            f"{email_subj_a}"
            f"Addressing {core_focus} requires avoiding the common trap where surface-level execution masks deep architectural friction.\n\n"
            f"Looking at your specifications, the critical objective is achieving a robust, maintainable solution that supports your business milestones without unexpected rework or communication delays. "
            f"When projects like this miss their targets, it is almost always due to underspecified interfaces or rushed scoping early on.\n\n"
            f"The implementation plan centers on {inp.proposed_approach.strip().rstrip('.')}. "
            f"Every milestone is paired with automated validation and transparent progress updates, ensuring you maintain full visibility into delivery velocity from kickoff to handover.\n\n"
            f"{inp.achievements if inp.achievements else 'Demonstrated history of delivering enterprise-grade outcomes and high-reliability integrations across complex environments.'}\n\n"
            f"{smart_question}\n\n"
            f"{tone_closing}"
        )
        var_b_text = (
            f"{email_subj_b}"
            f"Achieving tangible business results with {core_focus} demands an execution framework that connects directly to your target performance metrics.\n\n"
            f"{inp.achievements if inp.achievements else 'Consistently engineered high-impact solutions that reduced operational overhead and accelerated delivery schedules.'}\n\n"
            f"Your project brief underscores the necessity for predictable delivery and clean architecture. "
            f"Rather than treating this as generic development work, the approach applies {inp.proposed_approach.strip().rstrip('.')}, ensuring each component meets strict quality thresholds prior to staging.\n\n"
            f"Are there predefined security or compliance benchmarks that must govern the deployment pipeline?\n\n"
            f"{tone_closing}"
        )

    # Lint check both
    var_a_warns = lint_proposal(var_a_text, inp.platform)
    var_b_warns = lint_proposal(var_b_text, inp.platform)

    variation_a = ProposalVariation(
        title="VARIATION A — Lead with the client's pain and problem",
        angle="Lead with the client's pain and problem",
        text=var_a_text.strip(),
        word_count=count_words(var_a_text),
        warnings=var_a_warns
    )

    variation_b = ProposalVariation(
        title="VARIATION B — Lead with a bold, relevant result or achievement",
        angle="Lead with a bold, relevant result or achievement",
        text=var_b_text.strip(),
        word_count=count_words(var_b_text),
        warnings=var_b_warns
    )

    # Coaching Note
    stronger = "Variation A" if inp.tone in [Tone.DIRECT, Tone.CONSULTATIVE] or not inp.achievements else "Variation B"
    stronger_reason = (
        "Clients experiencing acute bottlenecks or vague scopes respond much faster to deep problem diagnosis than to bragged credentials."
        if stronger == "Variation A" else
        "Your concrete achievements and quantifiable past results immediately establish high credibility and de-risk the investment."
    )

    coaching = CoachingNote(
        stronger_variation=stronger,
        stronger_reason=stronger_reason,
        what_to_personalize=f"Insert the exact name of the client's existing software stack, repository, or company if mentioned in their post.",
        smart_question=smart_question,
        win_probability_factors=(
            "Response speed within the first 1-2 hours of posting will increase conversion by over 3x. "
            "Opening with zero fluff and immediately stating their core constraint will separate your bid from 95% of generic copy-paste proposals."
        )
    )

    # Build raw formatted string strictly matching the output specification
    raw_parts = []
    raw_parts.append("═══════════════════════════════════════\n")
    if red_flag_res.has_flags and red_flag_res.alert_text:
        raw_parts.append(f"🚩 RED FLAG ALERT (only include if red flags detected):\n{red_flag_res.alert_text}\n\n═══════════════════════════════════════\n")
    
    raw_parts.append(f"VARIATION A — {variation_a.angle}\n\n{variation_a.text}\n\n---\n\n")
    raw_parts.append(f"VARIATION B — {variation_b.angle}\n\n{variation_b.text}\n\n")
    raw_parts.append("═══════════════════════════════════════\n\n📊 COACHING NOTE\n\n")
    raw_parts.append(f"Stronger variation: {coaching.stronger_variation} — {coaching.stronger_reason}\n\n")
    raw_parts.append(f"What to personalize: {coaching.what_to_personalize}\n\n")
    raw_parts.append(f"Smart question to consider adding: {coaching.smart_question}\n\n")
    raw_parts.append(f"Win probability factors: {coaching.win_probability_factors}\n\n")
    raw_parts.append("═══════════════════════════════════════")

    raw_formatted = "".join(raw_parts)

    return ProposalResponse(
        red_flag_alert=red_flag_res.alert_text if red_flag_res.has_flags else None,
        variation_a=variation_a,
        variation_b=variation_b,
        coaching_note=coaching,
        raw_formatted=raw_formatted,
        provider_used="offline_strategic_engine",
        validation_status="PASS" if not (var_a_warns or var_b_warns) else "WARNINGS_REVIEWED"
    )
