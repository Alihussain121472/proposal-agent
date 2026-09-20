"""
LLM Orchestration Engine for the Proposal Strategist Agent.
Supports Google Gemini, Groq, OpenAI, and Ollama with seamless offline fallback.
Parses LLM output into structured Pydantic models and runs rules linter.
"""

import os
import re
from typing import Optional, Dict, Any, Tuple
from proposal_agent.models import (
    ProposalInput, ProposalResponse, ProposalVariation,
    CoachingNote, Platform, Tone,
    AcademicLevel, AcademicProposalType, AcademicProposalInput, AcademicProposalResponse
)
from proposal_agent.prompts import (
    SYSTEM_PROMPT, USER_PROMPT_TEMPLATE,
    ACADEMIC_SYSTEM_PROMPT, ACADEMIC_USER_PROMPT_TEMPLATE
)
from proposal_agent.rules_linter import count_words, lint_proposal
from proposal_agent.red_flag_detector import analyze_red_flags
from proposal_agent.offline_engine import generate_offline_proposals
from proposal_agent.academic_engine import generate_academic_offline
from proposal_agent.config import AgentConfig, get_config


def format_user_prompt(inp: ProposalInput) -> str:
    """Format user prompt from input fields."""
    return USER_PROMPT_TEMPLATE.format(
        platform=inp.platform.value,
        job_description=inp.job_description,
        freelancer_profile=inp.freelancer_profile,
        relevant_experience=inp.relevant_experience,
        proposed_approach=inp.proposed_approach,
        budget_range=inp.budget_range or "Not specified",
        tone=inp.tone.value,
        achievements=inp.achievements or "None specified (use situational proof only)"
    )

def parse_llm_output(raw_text: str, inp: ProposalInput, provider_name: str) -> ProposalResponse:
    """Parse raw LLM response text into structured ProposalResponse."""
    # 1. Red Flag Alert parsing
    red_flag_alert = None
    red_flag_match = re.search(
        r"🚩\s*RED FLAG ALERT[^\n:]*:\s*\n(.*?)(?=\n═|\nVARIATION|$)",
        raw_text,
        re.DOTALL | re.IGNORECASE
    )
    if red_flag_match:
        alert_candidate = red_flag_match.group(1).strip()
        if alert_candidate and not alert_candidate.lower().startswith("[only include"):
            red_flag_alert = alert_candidate

    # If LLM didn't catch a red flag but rule-detector did, augment it
    detector_res = analyze_red_flags(inp.job_description, inp.budget_range)
    if not red_flag_alert and detector_res.has_flags:
        red_flag_alert = detector_res.alert_text

    # 2. Variation A parsing
    var_a_title = "VARIATION A — Lead with the client's pain and problem"
    var_a_angle = "Lead with the client's pain and problem"
    var_a_text = ""
    
    var_a_match = re.search(
        r"VARIATION A\s*[-—:]\s*([^\n]+)\n+(.*?)(?=\n---\s*\n|\nVARIATION B|$)",
        raw_text,
        re.DOTALL | re.IGNORECASE
    )
    if var_a_match:
        var_a_angle = var_a_match.group(1).strip()
        var_a_text = var_a_match.group(2).strip()

    # 3. Variation B parsing
    var_b_title = "VARIATION B — Lead with a bold, relevant result or achievement"
    var_b_angle = "Lead with a bold, relevant result or achievement"
    var_b_text = ""

    var_b_match = re.search(
        r"VARIATION B\s*[-—:]\s*([^\n]+)\n+(.*?)(?=\n═|\n📊\s*COACHING NOTE|$)",
        raw_text,
        re.DOTALL | re.IGNORECASE
    )
    if var_b_match:
        var_b_angle = var_b_match.group(1).strip()
        var_b_text = var_b_match.group(2).strip()

    # 4. Coaching Note parsing
    stronger_variation = "Variation A"
    stronger_reason = "More directly addresses the client's immediate operational friction."
    what_to_personalize = "Personalize with any specific system names, repositories, or company details mentioned."
    smart_question = "Clarify whether priority is delivery speed or architectural scalability."
    win_factors = "Speed of proposal submission and opening with immediate problem insight."

    coaching_section_match = re.search(r"📊\s*COACHING NOTE.*", raw_text, re.DOTALL | re.IGNORECASE)
    if coaching_section_match:
        coach_text = coaching_section_match.group(0)
        
        stronger_m = re.search(r"Stronger variation:\s*([^\n—\-]+)[—\-]\s*([^\n]+)", coach_text, re.IGNORECASE)
        if stronger_m:
            stronger_variation = stronger_m.group(1).strip()
            stronger_reason = stronger_m.group(2).strip()
        
        pers_m = re.search(r"What to personalize:\s*([^\n]+)", coach_text, re.IGNORECASE)
        if pers_m:
            what_to_personalize = pers_m.group(1).strip()
            
        sq_m = re.search(r"Smart question to consider adding:\s*([^\n]+)", coach_text, re.IGNORECASE)
        if sq_m:
            smart_question = sq_m.group(1).strip()

        win_m = re.search(r"Win probability factors:\s*(.*?)(?=\n═|$)", coach_text, re.DOTALL | re.IGNORECASE)
        if win_m:
            win_factors = win_m.group(1).strip()

    # If parsing failed to isolate variations (unusual LLM layout), fallback cleanly
    if not var_a_text or not var_b_text:
        return generate_offline_proposals(inp)

    # Lint check
    var_a_warns = lint_proposal(var_a_text, inp.platform)
    var_b_warns = lint_proposal(var_b_text, inp.platform)

    return ProposalResponse(
        red_flag_alert=red_flag_alert,
        variation_a=ProposalVariation(
            title=f"VARIATION A — {var_a_angle}",
            angle=var_a_angle,
            text=var_a_text,
            word_count=count_words(var_a_text),
            warnings=var_a_warns
        ),
        variation_b=ProposalVariation(
            title=f"VARIATION B — {var_b_angle}",
            angle=var_b_angle,
            text=var_b_text,
            word_count=count_words(var_b_text),
            warnings=var_b_warns
        ),
        coaching_note=CoachingNote(
            stronger_variation=stronger_variation,
            stronger_reason=stronger_reason,
            what_to_personalize=what_to_personalize,
            smart_question=smart_question,
            win_probability_factors=win_factors
        ),
        raw_formatted=raw_text.strip(),
        provider_used=provider_name,
        validation_status="PASS" if not (var_a_warns or var_b_warns) else "WARNINGS_REVIEWED"
    )

def call_gemini(user_prompt: str, api_key: str, model_name: str = "gemini-2.5-flash", system_instruction: str = SYSTEM_PROMPT) -> str:
    """Call Google Gemini API."""
    try:
        # Try google-genai first
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config={"system_instruction": system_instruction}
        )
        return response.text
    except Exception as e:
        # Fallback to google.generativeai
        try:
            import google.generativeai as gai
            gai.configure(api_key=api_key)
            model = gai.GenerativeModel(
                model_name=model_name if "gemini" in model_name else "gemini-1.5-flash",
                system_instruction=system_instruction
            )
            resp = model.generate_content(user_prompt)
            return resp.text
        except Exception as e2:
            raise RuntimeError(f"Gemini API error: {str(e2)}")

def call_openai(user_prompt: str, api_key: str, model_name: str = "gpt-4o-mini", base_url: Optional[str] = None, system_instruction: str = SYSTEM_PROMPT) -> str:
    """Call OpenAI API or compatible server (like Ollama/vLLM)."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content or ""

def call_groq(user_prompt: str, api_key: str, model_name: str = "llama-3.3-70b-versatile", system_instruction: str = SYSTEM_PROMPT) -> str:
    """Call Groq API."""
    from groq import Groq
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content or ""

def generate_proposals(
    inp: ProposalInput,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    config: Optional[AgentConfig] = None
) -> ProposalResponse:
    """
    Main proposal generation entrypoint.
    Chooses the best available provider or falls back to deterministic strategist engine.
    """
    cfg = config or get_config()
    target_provider = provider or cfg.default_provider
    user_prompt = format_user_prompt(inp)

    # 1. Google Gemini
    if target_provider == "gemini":
        key = api_key or cfg.gemini_api_key
        if not key:
            # Check env dynamically
            key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if key:
            try:
                raw = call_gemini(user_prompt, key, model or cfg.gemini_model)
                return parse_llm_output(raw, inp, f"gemini ({model or cfg.gemini_model})")
            except Exception as e:
                print(f"[Warning] Gemini API failed: {e}. Falling back to offline engine.")

    # 2. Groq
    elif target_provider == "groq":
        key = api_key or cfg.groq_api_key or os.getenv("GROQ_API_KEY")
        if key:
            try:
                raw = call_groq(user_prompt, key, model or cfg.groq_model)
                return parse_llm_output(raw, inp, f"groq ({model or cfg.groq_model})")
            except Exception as e:
                print(f"[Warning] Groq API failed: {e}. Falling back to offline engine.")

    # 3. OpenAI
    elif target_provider == "openai":
        key = api_key or cfg.openai_api_key or os.getenv("OPENAI_API_KEY")
        if key:
            try:
                raw = call_openai(user_prompt, key, model or cfg.openai_model)
                return parse_llm_output(raw, inp, f"openai ({model or cfg.openai_model})")
            except Exception as e:
                print(f"[Warning] OpenAI API failed: {e}. Falling back to offline engine.")

    # 4. Ollama / Local
    elif target_provider == "ollama":
        try:
            raw = call_openai(user_prompt, api_key="ollama", model_name=model or cfg.ollama_model, base_url=cfg.ollama_base_url)
            return parse_llm_output(raw, inp, f"ollama ({model or cfg.ollama_model})")
        except Exception as e:
            print(f"[Warning] Ollama failed: {e}. Falling back to offline engine.")

    # Default / Fallback: Offline Strategic Engine
    return generate_offline_proposals(inp)

def format_academic_user_prompt(inp: AcademicProposalInput) -> str:
    """Format user prompt for academic & professional proposals."""
    return ACADEMIC_USER_PROMPT_TEMPLATE.format(
        academic_level=inp.academic_level.value,
        proposal_type=inp.proposal_type.value,
        topic=inp.topic,
        purpose=inp.purpose,
        target_audience=inp.target_audience or "Evaluation Committee / Stakeholders",
        specific_requirements=inp.specific_requirements or "None specified"
    )

def parse_academic_llm_output(raw_text: str, inp: AcademicProposalInput, provider_name: str) -> AcademicProposalResponse:
    """Parse raw LLM response into structured AcademicProposalResponse with offline fallback for missing sections."""
    fallback = generate_academic_offline(inp)

    # 1. Title
    title = fallback.title
    title_match = re.search(r"^#\s+([^\n]+)|##\s*1\.\s*Title\s*\n+([^\n#]+)", raw_text, re.MULTILINE | re.IGNORECASE)
    if title_match:
        cand = (title_match.group(1) or title_match.group(2) or "").strip().replace("**", "").replace("*", "")
        if cand and len(cand) > 5 and not cand.lower().startswith("academic"):
            title = cand

    # 2. Introduction / Background
    intro = fallback.introduction_background
    intro_match = re.search(r"##\s*2\.\s*Introduction[^\n]*\n+(.*?)(?=\n##|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
    if intro_match and intro_match.group(1).strip():
        intro = intro_match.group(1).strip()

    # 3. Problem Statement
    prob = fallback.problem_statement
    prob_match = re.search(r"##\s*3\.\s*Problem Statement[^\n]*\n+(.*?)(?=\n##|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
    if prob_match and prob_match.group(1).strip():
        prob = prob_match.group(1).strip()

    # 4. Objectives
    objs = fallback.objectives
    objs_match = re.search(r"##\s*4\.\s*Objectives[^\n]*\n+(.*?)(?=\n##|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
    if objs_match and objs_match.group(1).strip():
        lines = [line.strip().lstrip("-*123456789. \t").strip() for line in objs_match.group(1).strip().split("\n") if line.strip()]
        valid_lines = [l for l in lines if len(l) > 5]
        if valid_lines:
            objs = valid_lines

    # 5. Methodology or Approach
    method = fallback.methodology_approach
    method_match = re.search(r"##\s*5\.\s*Methodology[^\n]*\n+(.*?)(?=\n##|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
    if method_match and method_match.group(1).strip():
        method = method_match.group(1).strip()

    # 6. Expected Outcomes / Benefits
    outcomes = fallback.expected_outcomes_benefits
    outcomes_match = re.search(r"##\s*6\.\s*Expected Outcomes[^\n]*\n+(.*?)(?=\n##|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
    if outcomes_match and outcomes_match.group(1).strip():
        outcomes = outcomes_match.group(1).strip()

    # 7. Conclusion
    conclusion = fallback.conclusion
    conclusion_match = re.search(r"##\s*7\.\s*Conclusion[^\n]*\n+(.*?)(?=\n##|---\s*\n|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
    if conclusion_match and conclusion_match.group(1).strip():
        conclusion = conclusion_match.group(1).strip()

    word_count = count_words(raw_text)

    return AcademicProposalResponse(
        title=title,
        academic_level=inp.academic_level,
        proposal_type=inp.proposal_type,
        introduction_background=intro,
        problem_statement=prob,
        objectives=objs,
        methodology_approach=method,
        expected_outcomes_benefits=outcomes,
        conclusion=conclusion,
        raw_markdown=raw_text if len(raw_text) > 100 else fallback.raw_markdown,
        word_count=word_count if word_count > 50 else fallback.word_count,
        provider_used=provider_name,
        level_insights=fallback.level_insights
    )

def generate_academic_proposal(
    inp: AcademicProposalInput,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    config: Optional[AgentConfig] = None
) -> AcademicProposalResponse:
    """
    Main academic & professional proposal generation entrypoint.
    Connects to configured LLM with strict prompt grounding or falls back to academic strategist engine.
    """
    cfg = config or get_config()
    target_provider = provider or cfg.default_provider
    user_prompt = format_academic_user_prompt(inp)

    # 1. Google Gemini
    if target_provider == "gemini":
        key = api_key or cfg.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if key:
            try:
                raw = call_gemini(user_prompt, key, model or cfg.gemini_model, system_instruction=ACADEMIC_SYSTEM_PROMPT)
                return parse_academic_llm_output(raw, inp, f"gemini ({model or cfg.gemini_model})")
            except Exception as e:
                print(f"[Warning] Gemini API failed: {e}. Falling back to offline academic engine.")

    # 2. Groq
    elif target_provider == "groq":
        key = api_key or cfg.groq_api_key or os.getenv("GROQ_API_KEY")
        if key:
            try:
                raw = call_groq(user_prompt, key, model or cfg.groq_model, system_instruction=ACADEMIC_SYSTEM_PROMPT)
                return parse_academic_llm_output(raw, inp, f"groq ({model or cfg.groq_model})")
            except Exception as e:
                print(f"[Warning] Groq API failed: {e}. Falling back to offline academic engine.")

    # 3. OpenAI
    elif target_provider == "openai":
        key = api_key or cfg.openai_api_key or os.getenv("OPENAI_API_KEY")
        if key:
            try:
                raw = call_openai(user_prompt, key, model or cfg.openai_model, system_instruction=ACADEMIC_SYSTEM_PROMPT)
                return parse_academic_llm_output(raw, inp, f"openai ({model or cfg.openai_model})")
            except Exception as e:
                print(f"[Warning] OpenAI API failed: {e}. Falling back to offline academic engine.")

    # 4. Ollama / Local
    elif target_provider == "ollama":
        try:
            raw = call_openai(user_prompt, api_key="ollama", model_name=model or cfg.ollama_model, base_url=cfg.ollama_base_url, system_instruction=ACADEMIC_SYSTEM_PROMPT)
            return parse_academic_llm_output(raw, inp, f"ollama ({model or cfg.ollama_model})")
        except Exception as e:
            print(f"[Warning] Ollama failed: {e}. Falling back to offline academic engine.")

    # Default / Fallback
    return generate_academic_offline(inp)

