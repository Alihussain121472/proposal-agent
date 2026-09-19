"""
Main entry point for the Freelance Proposal Strategist Agent.
Launch either the Web Dashboard or the Interactive CLI.
"""

import sys
import argparse

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(
        description="Senior Freelance Proposal Strategist Agent ($2M+ Win Engine)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Launch the interactive terminal CLI instead of the web dashboard"
    )
    parser.add_argument(
        "--demo",
        choices=["1", "2", "3", "4"],
        help="Run an instant demo with one of the 4 curated scenarios:\n"
             "  1: Full-Stack AI SaaS Developer (Upwork, $5k)\n"
             "  2: UI/UX & CRO Specialist (Direct Email)\n"
             "  3: Python Automation (Red Flag Spec Work Test)\n"
             "  4: B2B SaaS Growth Copywriter (Agency RFP)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Web server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web server port (default: 8000)"
    )
    parser.add_argument(
        "--provider",
        choices=["offline", "gemini", "groq", "openai", "ollama"],
        default="offline",
        help="LLM provider to use for demo mode"
    )

    args = parser.parse_args()

    if args.demo:
        from presets import PRESETS
        from proposal_agent import ProposalStrategistAgent
        preset = PRESETS[args.demo]
        print(f"\n⚡ RUNNING DEMO SCENARIO {args.demo}: {preset['title']}")
        print(f"Description: {preset['description']}\n")
        agent = ProposalStrategistAgent()
        res = agent.generate(preset["input"], provider=args.provider)
        print(res.raw_formatted)
        print("\n✨ Proposal generation complete.")
        return

    if args.cli:
        from cli import run_interactive
        run_interactive()
    else:
        import uvicorn
        print("\n" + "=" * 65)
        print("  ⚡ SENIOR FREELANCE PROPOSAL STRATEGIST AGENT")
        print("  Starting interactive Web Dashboard at:")
        print(f"  👉 http://{args.host}:{args.port}")
        print("=" * 65 + "\n")
        uvicorn.run("app:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
