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
    ProposalStrategistAgent, ProposalInput, Platform, Tone
)
from presets import PRESETS

console = Console(force_terminal=True)

def display_banner():
    banner = """[bold cyan]╔══════════════════════════════════════════════════════════════════════╗
║        SENIOR FREELANCE PROPOSAL STRATEGIST AGENT                    ║
║   "Clients hire who makes them feel most understood & confident"     ║
╚══════════════════════════════════════════════════════════════════════╝[/bold cyan]"""
    console.print(banner)

def run_interactive():
    display_banner()
    agent = ProposalStrategistAgent()

    console.print("\n[yellow]Choose an option:[/yellow]")
    console.print("  [bold green][1][/bold green] Load Preset Demo Scenario")
    console.print("  [bold green][2][/bold green] Enter Custom Job Details")
    console.print("  [bold green][3][/bold green] Exit")

    choice = Prompt.ask("Select option", choices=["1", "2", "3"], default="1")

    if choice == "3":
        console.print("[dim]Goodbye![/dim]")
        return

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

    # Provider choice
    console.print("\n[bold yellow]Select Strategy Engine / Model:[/bold yellow]")
    console.print("  [1] Offline Strategic Engine (Instant, zero API keys required)")
    console.print("  [2] Google Gemini (Uses GEMINI_API_KEY if configured)")
    console.print("  [3] Groq (Uses GROQ_API_KEY if configured)")
    console.print("  [4] OpenAI (Uses OPENAI_API_KEY if configured)")
    
    eng_choice = Prompt.ask("Engine choice", choices=["1", "2", "3", "4"], default="1")
    provider_map = {"1": "offline", "2": "gemini", "3": "groq", "4": "openai"}
    provider = provider_map[eng_choice]

    with console.status("[bold green]Analyzing psychology, calibrating platform, and crafting proposals...[/bold green]"):
        res = agent.generate(inp, provider=provider)

    # Display Results
    console.print("\n" + "=" * 60 + "\n")

    # Red flag alert
    if res.red_flag_alert:
        console.print(Panel(
            f"[bold red]🚩 RED FLAG ALERT[/bold red]\n\n{res.red_flag_alert}",
            border_style="red",
            title="Warning: Client Job Risk"
        ))

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

def main():
    parser = argparse.ArgumentParser(description="Freelance Proposal Strategist Agent")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Run specific preset demo (1, 2, 3, or 4)")
    parser.add_argument("--provider", default="offline", choices=["offline", "gemini", "groq", "openai", "ollama"])
    args = parser.parse_args()

    if args.preset:
        display_banner()
        preset = PRESETS[args.preset]
        console.print(f"[bold green]Running Preset {args.preset}: {preset['title']}[/bold green]\n")
        agent = ProposalStrategistAgent()
        res = agent.generate(preset["input"], provider=args.provider)
        console.print(res.raw_formatted)
    else:
        run_interactive()

if __name__ == "__main__":
    main()
