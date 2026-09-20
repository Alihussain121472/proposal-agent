import sys
import os
import argparse
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown

from proposal_agent import (
    ProposalStrategistAgent, ProposalInput, Platform, Tone,
    AcademicLevel, AcademicProposalType, AcademicProposalInput
)
from presets import PRESETS, ACADEMIC_PRESETS

console = Console(force_terminal=True)

def display_banner():
    banner = """[bold cyan]╔══════════════════════════════════════════════════════════════════════╗
║        PROPOSAL STRATEGIST & ACADEMIC PROPOSAL AGENT                 ║
║   Freelance ($2M+ Winning Pitch) & Academic (Bachelor's, Master's, PhD)║
╚══════════════════════════════════════════════════════════════════════╝[/bold cyan]"""
    console.print(banner)

def run_academic_wizard(agent: ProposalStrategistAgent, provider: str = "offline"):
    console.print("\n[bold cyan]╔══════════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║      ACADEMIC & PROFESSIONAL PROPOSAL WRITING ASSISTANT          ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════════════════════════════╝[/bold cyan]")

    console.print("\n[yellow]Choose an academic mode:[/yellow]")
    console.print("  [bold green][1][/bold green] Load Curated Preset Scenario")
    console.print("  [bold green][2][/bold green] Follow 4-Step Interactive Wizard")
    sub_choice = Prompt.ask("Select option", choices=["1", "2"], default="1")

    if sub_choice == "1":
        console.print("\n[bold]Select an Academic Preset Scenario:[/bold]")
        for k, v in ACADEMIC_PRESETS.items():
            console.print(f"  [cyan]{k}[/cyan]: [bold]{v['title']}[/bold] - [dim]{v['description']}[/dim]")
        
        preset_choice = Prompt.ask("Choose preset", choices=list(ACADEMIC_PRESETS.keys()), default="1")
        inp = ACADEMIC_PRESETS[preset_choice]["input"]
    else:
        # STEP 1 — ASK FOR ACADEMIC LEVEL
        console.print("\n[bold cyan]STEP 1 — ASK FOR ACADEMIC LEVEL[/bold cyan]")
        console.print("  [bold green][1][/bold green] Bachelor's  (clear, simple, foundational language)")
        console.print("  [bold green][2][/bold green] Master's    (analytical, structured, research-aware language)")
        console.print("  [bold green][3][/bold green] PhD         (advanced, scholarly, gap-focused, methodology-rich)")
        lvl_choice = Prompt.ask("What is your academic level?", choices=["1", "2", "3"], default="2")
        level_map = {"1": AcademicLevel.BACHELORS, "2": AcademicLevel.MASTERS, "3": AcademicLevel.PHD}
        academic_level = level_map[lvl_choice]

        # STEP 2 — ASK FOR PROPOSAL TYPE
        console.print("\n[bold cyan]STEP 2 — ASK FOR PROPOSAL TYPE[/bold cyan]")
        console.print("  [bold green][1][/bold green] Education Proposal")
        console.print("  [bold green][2][/bold green] Business Proposal")
        console.print("  [bold green][3][/bold green] Social Media Proposal")
        type_choice = Prompt.ask("What type of proposal would you like to write?", choices=["1", "2", "3"], default="1")
        type_map = {
            "1": AcademicProposalType.EDUCATION,
            "2": AcademicProposalType.BUSINESS,
            "3": AcademicProposalType.SOCIAL_MEDIA
        }
        proposal_type = type_map[type_choice]

        # STEP 3 — GATHER DETAILS
        console.print("\n[bold cyan]STEP 3 — GATHER DETAILS[/bold cyan]")
        topic = Prompt.ask("Topic / Idea", default="Interactive Digital Media in Modern Higher Education")
        purpose = Prompt.ask("Purpose / Objective", default="Assess learner retention and satisfaction across digital instruction modules")
        audience = Prompt.ask("Target audience", default="Academic Faculty Review Committee")
        requirements = Prompt.ask("Specific requirements / guidelines (optional)", default="APA 7th edition, 1-year research horizon")

        inp = AcademicProposalInput(
            academic_level=academic_level,
            proposal_type=proposal_type,
            topic=topic,
            purpose=purpose,
            target_audience=audience,
            specific_requirements=requirements
        )

    # STEP 4 — WRITE THE PROPOSAL
    console.print(f"\n[bold yellow]Generating 7-Section Academic Proposal ({inp.academic_level.value})...[/bold yellow]")
    res = agent.generate_academic(inp, provider=provider)

    console.print(f"\n[bold green]✔ Academic Proposal Generated ({res.word_count} words, Provider: {res.provider_used})[/bold green]")
    console.print(f"[dim]{res.level_insights}[/dim]\n")

    # Display 7 structured sections in formatted panels
    console.print(Panel(f"[bold white]{res.title}[/bold white]", title="1. Title", border_style="cyan"))
    console.print(Panel(res.introduction_background, title="2. Introduction / Background", border_style="blue"))
    console.print(Panel(res.problem_statement, title="3. Problem Statement", border_style="yellow"))
    
    objs_formatted = "\n".join([f"• {obj}" for obj in res.objectives])
    console.print(Panel(objs_formatted, title="4. Objectives", border_style="green"))
    console.print(Panel(res.methodology_approach, title="5. Methodology or Approach", border_style="magenta"))
    console.print(Panel(res.expected_outcomes_benefits, title="6. Expected Outcomes / Benefits", border_style="cyan"))
    console.print(Panel(res.conclusion, title="7. Conclusion", border_style="purple"))

    if Confirm.ask("\nSave full Markdown proposal to 'academic_proposal.md'?", default=True):
        with open("academic_proposal.md", "w", encoding="utf-8") as f:
            f.write(res.raw_markdown)
        console.print("[green]Saved successfully to academic_proposal.md![/green]")

def run_freelance_wizard(agent: ProposalStrategistAgent, provider: str = "offline"):
    console.print("\n[yellow]Choose an option:[/yellow]")
    console.print("  [bold green][1][/bold green] Load Preset Demo Scenario")
    console.print("  [bold green][2][/bold green] Enter Custom Job Details")

    choice = Prompt.ask("Select option", choices=["1", "2"], default="1")

    if choice == "1":
        console.print("\n[bold]Select a Preset Scenario:[/bold]")
        for k, v in PRESETS.items():
            console.print(f"  [cyan]{k}[/cyan]: [bold]{v['title']}[/bold] - [dim]{v['description']}[/dim]")
        
        preset_choice = Prompt.ask("Choose preset", choices=list(PRESETS.keys()), default="1")
        inp = PRESETS[preset_choice]["input"]
    else:
        # Custom input collection
        console.print("\n[bold cyan]--- 1. PLATFORM ---[/bold cyan]")
        platform_str = Prompt.ask(
            "Platform",
            choices=["Upwork", "Direct Email", "LinkedIn", "Agency RFP", "Other"],
            default="Upwork"
        )
        platform = Platform(platform_str)

        console.print("\n[bold cyan]--- 2. JOB DESCRIPTION ---[/bold cyan]")
        console.print("[dim]Paste the full job post below (press Enter, then type 'DONE' on a new line):[/dim]")
        lines = []
        while True:
            line = input()
            if line.strip() == "DONE":
                break
            lines.append(line)
        job_description = "\n".join(lines).strip()
        if not job_description:
            console.print("[red]Job description cannot be empty![/red]")
            return

        console.print("\n[bold cyan]--- 3. FREELANCER PROFILE ---[/bold cyan]")
        freelancer_profile = Prompt.ask("Your background & niche", default="Senior Software Engineer with 6+ years experience.")

        console.print("\n[bold cyan]--- 4. RELEVANT EXPERIENCE ---[/bold cyan]")
        relevant_experience = Prompt.ask("Most relevant project/experience for this job", default="Built and scaled similar systems for high-growth startups.")

        console.print("\n[bold cyan]--- 5. PROPOSED APPROACH ---[/bold cyan]")
        proposed_approach = Prompt.ask("How you will tackle this specific project", default="Audit architecture, build clean modular components, deploy with test coverage.")

        console.print("\n[bold cyan]--- 6. BUDGET / RATE ---[/bold cyan]")
        budget_range = Prompt.ask("Budget range or rate", default="$3,000 - $5,000")

        console.print("\n[bold cyan]--- 7. TONE ---[/bold cyan]")
        tone_str = Prompt.ask("Tone", choices=["Professional", "Friendly", "Direct", "Consultative"], default="Professional")
        tone = Tone(tone_str)

        console.print("\n[bold cyan]--- 8. ACHIEVEMENTS / NUMBERS ---[/bold cyan]")
        achievements = Prompt.ask("Specific metrics or case results (leave blank for situational proof)", default="")

        inp = ProposalInput(
            platform=platform,
            job_description=job_description,
            freelancer_profile=freelancer_profile,
            relevant_experience=relevant_experience,
            proposed_approach=proposed_approach,
            budget_range=budget_range,
            tone=tone,
            achievements=achievements
        )

    # Pre-generation Red Flag Scan
    console.print("\n[bold yellow]Scanning for Job Red Flags...[/bold yellow]")
    red_flags = agent.check_red_flags(inp.job_description, inp.budget_range)
    if red_flags.has_flags:
        console.print(Panel(
            f"[bold red]RED FLAG ALERT:[/bold red]\n{red_flags.alert_text}\n\n[dim]Reasons: {', '.join(red_flags.reasons)}[/dim]",
            border_style="red",
            title="⚠️ Caution"
        ))
    else:
        console.print("[green]No critical red flags detected. Proceeding to generation.[/green]")

    # Generate Proposals
    console.print("\n[bold yellow]Generating Strategic Proposals...[/bold yellow]")
    res = agent.generate(inp, provider=provider)

    # Display Variations
    console.print("\n" + "═"*70)
    console.print(f"[bold green]PROPOSALS GENERATED ({res.provider_used.upper()})[/bold green]")
    console.print("═"*70 + "\n")

    if res.red_flag_alert:
        console.print(Panel(f"[bold red]{res.red_flag_alert}[/bold red]", border_style="red", title="🚩 RED FLAG ALERT"))

    # Variation A
    var_a_content = (
        f"[bold cyan]{res.variation_a.title}[/bold cyan]\n"
        f"[dim]Word count: {res.variation_a.word_count} words[/dim]\n\n"
        f"{res.variation_a.text}"
    )
    if res.variation_a.warnings:
        var_a_content += "\n\n[yellow]⚠️ Warnings: " + "; ".join(res.variation_a.warnings) + "[/yellow]"

    console.print(Panel(var_a_content, border_style="cyan", title="Variation A (Pain Lead)"))

    # Variation B
    var_b_content = (
        f"[bold magenta]{res.variation_b.title}[/bold magenta]\n"
        f"[dim]Word count: {res.variation_b.word_count} words[/dim]\n\n"
        f"{res.variation_b.text}"
    )
    if res.variation_b.warnings:
        var_b_content += "\n\n[yellow]⚠️ Warnings: " + "; ".join(res.variation_b.warnings) + "[/yellow]"

    console.print(Panel(var_b_content, border_style="magenta", title="Variation B (Result Lead)"))

    # Coaching Note
    coaching_text = (
        f"[bold]Stronger variation:[/bold] [green]{res.coaching_note.stronger_variation}[/green] — {res.coaching_note.stronger_reason}\n\n"
        f"[bold]What to personalize:[/bold] {res.coaching_note.what_to_personalize}\n\n"
        f"[bold]Smart question to consider adding:[/bold] {res.coaching_note.smart_question}\n\n"
        f"[bold]Win probability factors:[/bold] {res.coaching_note.win_probability_factors}"
    )
    console.print(Panel(coaching_text, border_style="green", title="📊 COACHING NOTE"))

    # Save prompt
    if Confirm.ask("\nSave this output to 'latest_proposal.txt'?", default=True):
        with open("latest_proposal.txt", "w", encoding="utf-8") as f:
            f.write(res.raw_formatted)
        console.print("[green]Saved successfully to latest_proposal.txt![/green]")

def run_interactive():
    display_banner()
    agent = ProposalStrategistAgent()

    console.print("\n[yellow]Select Proposal Agent Mode:[/yellow]")
    console.print("  [bold green][1][/bold green] 💼 Freelance Pitch Strategist ($2M+ Winning Contracts)")
    console.print("  [bold green][2][/bold green] 🎓 Academic & Professional Proposal Assistant (Bachelor's, Master's, PhD)")
    console.print("  [bold green][3][/bold green] 🚪 Exit")

    choice = Prompt.ask("Select option", choices=["1", "2", "3"], default="1")

    if choice == "3":
        console.print("[dim]Goodbye![/dim]")
        return
    elif choice == "2":
        run_academic_wizard(agent, provider="offline")
    else:
        run_freelance_wizard(agent, provider="offline")

def main():
    parser = argparse.ArgumentParser(description="Proposal Strategist & Academic Assistant Agent")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Run specific freelance preset demo (1, 2, 3, or 4)")
    parser.add_argument("--academic", action="store_true", help="Launch directly into Academic & Professional Proposal mode")
    parser.add_argument("--academic-preset", choices=list(ACADEMIC_PRESETS.keys()), help="Run specific academic preset demo (1, 2, or 3)")
    parser.add_argument("--provider", default="offline", choices=["offline", "gemini", "groq", "openai", "ollama"])
    args = parser.parse_args()

    agent = ProposalStrategistAgent()

    if args.academic_preset:
        display_banner()
        preset = ACADEMIC_PRESETS[args.academic_preset]
        console.print(f"[bold green]Running Academic Preset {args.academic_preset}: {preset['title']}[/bold green]\n")
        res = agent.generate_academic(preset["input"], provider=args.provider)
        console.print(res.raw_markdown)
    elif args.academic:
        display_banner()
        run_academic_wizard(agent, provider=args.provider)
    elif args.preset:
        display_banner()
        preset = PRESETS[args.preset]
        console.print(f"[bold green]Running Freelance Preset {args.preset}: {preset['title']}[/bold green]\n")
        res = agent.generate(preset["input"], provider=args.provider)
        console.print(res.raw_formatted)
    else:
        run_interactive()

if __name__ == "__main__":
    main()
