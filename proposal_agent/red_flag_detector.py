"""
Red flag detection module.
Analyzes job descriptions for:
- Unrealistic scope for the budget mentioned
- Vague requirements with no clear deliverable
- Signs of spec work ("show us what you'd do first", unpaid tasks)
- Multiple freelancers being tested simultaneously
- Requests for free samples or trials before hiring
"""

import re
from typing import List, Tuple
from proposal_agent.models import RedFlagResult

SPEC_WORK_PATTERNS = [
    r"show (us|me) what you(?:'d| would) do",
    r"submit a (sample|test|mockup|prototype) (first|before hiring)",
    r"free (trial|test|sample|task)",
    r"unpaid (trial|test)",
    r"do a quick test (task|project)",
    r"provide a free",
    r"complete this test before",
]

MULTIPLE_FREELANCER_PATTERNS = [
    r"hiring (several|multiple|2|3|4|5|a few) freelancers",
    r"test (several|multiple) freelancers",
    r"trial run with multiple",
    r"compete against other freelancers",
    r"best one will be chosen",
    r"best submission wins",
]

VAGUE_SCOPE_PATTERNS = [
    r"need someone to help with various",
    r"general help",
    r"lots of different tasks",
    r"and whatever else comes up",
    r"ongoing random tasks",
    r"need a guru who can do everything",
    r"wear many hats",
    r"rockstar who knows everything",
]

LOW_BUDGET_HIGH_SCOPE_PATTERNS = [
    r"build (a clone of|an entire|a full) (uber|airbnb|amazon|facebook|saas|marketplace) for \$(?:[1-9][0-9]{0,2}|[1-4][0-9]{2})\b",
    r"budget is \$(?:5|10|15|20|30|50)\b.*?(?:complex|enterprise|complete platform|full stack|mobile app)",
    r"fixed price \$(?:5|10|15|20|30|50)\b.*?(?:full stack|entire website|complete app)",
    r"equity only",
    r"pay once we get funding",
    r"revenue share only",
]

def analyze_red_flags(job_description: str, budget_range: str = "") -> RedFlagResult:
    """Analyze the job post for critical red flags."""
    reasons: List[str] = []
    text = job_description.lower()
    combined_text = f"{text} {budget_range.lower()}"

    # 1. Check for Spec Work / Free Samples
    for pat in SPEC_WORK_PATTERNS:
        if re.search(pat, text):
            reasons.append("Client is soliciting free spec work or unpaid test tasks before hiring.")
            break

    # 2. Check for Multiple Freelancers being tested simultaneously
    for pat in MULTIPLE_FREELANCER_PATTERNS:
        if re.search(pat, text):
            reasons.append("Client appears to be testing multiple freelancers in parallel or running a contest.")
            break

    # 3. Check for Vague scope
    words = text.strip().split()
    if len(words) < 8 and not any(k in text for k in ["api", "bug", "fix", "audit", "script"]):
        reasons.append("Job post is extremely brief with no deliverable or scope boundaries.")
    else:
        for pat in VAGUE_SCOPE_PATTERNS:
            if re.search(pat, text):
                reasons.append("Scope is vague and broad with potential for severe scope creep.")
                break

    # 4. Check for Unrealistic scope vs budget
    for pat in LOW_BUDGET_HIGH_SCOPE_PATTERNS:
        if re.search(pat, combined_text):
            reasons.append("Budget is drastically disconnected from the requested technical scope.")
            break

    if not reasons:
        return RedFlagResult(has_flags=False, reasons=[], alert_text=None)

    # Synthesize a strict 2-sentence maximum alert
    if len(reasons) == 1:
        sentence1 = f"Watch out: {reasons[0]}"
        sentence2 = "Protect your time by defining strict deliverables and milestone payments before starting any work."
        alert_text = f"{sentence1} {sentence2}"
    else:
        sentence1 = f"Watch out: {reasons[0]}"
        sentence2 = f"Also note that {reasons[1].lower()} Require milestone escrow before commencing work."
        alert_text = f"{sentence1} {sentence2}"

    return RedFlagResult(has_flags=True, reasons=reasons, alert_text=alert_text)
