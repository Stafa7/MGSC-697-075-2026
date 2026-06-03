from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from advising_agent.advisor import advise_offline
from advising_agent.agent import DEFAULT_MODEL, run_agent
from advising_agent.fixtures import PROJECT_ROOT
from advising_agent.models import AdvisingRecommendation


def has_usable_api_key() -> bool:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return api_key.startswith("sk-") and "your_api_key_here" not in api_key


def save_transcript(request: str, output: AdvisingRecommendation, mode: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = PROJECT_ROOT / "evidence" / "run_transcripts" / f"{timestamp}_{mode}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Advising Agent Run Transcript\n\n"
        f"- Mode: `{mode}`\n"
        f"- Timestamp UTC: `{timestamp}`\n\n"
        "## User Request\n\n"
        f"{request}\n\n"
        "## Structured Output\n\n"
        "```json\n"
        f"{json.dumps(output.model_dump(), indent=2)}\n"
        "```\n",
        encoding="utf-8",
    )
    return path


def save_error_transcript(request: str, error: Exception, mode: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = PROJECT_ROOT / "evidence" / "run_transcripts" / f"{timestamp}_{mode}_error.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Advising Agent Error Transcript\n\n"
        f"- Mode: `{mode}`\n"
        f"- Timestamp UTC: `{timestamp}`\n"
        f"- Error type: `{type(error).__name__}`\n\n"
        "## User Request\n\n"
        f"{request}\n\n"
        "## Error\n\n"
        "```text\n"
        f"{error}\n"
        "```\n\n"
        "## Interpretation\n\n"
        "The SDK-backed agent attempted an OpenAI API call, but the provider returned an error. "
        "Use offline mode for deterministic local evidence if billing/quota is unavailable.\n",
        encoding="utf-8",
    )
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the McGill-style course advising agent.")
    parser.add_argument("request", nargs="*", help="Student advising request.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use deterministic fixture-backed mode instead of the OpenAI Agents SDK.",
    )
    return parser.parse_args()


async def async_main() -> None:
    load_dotenv()
    args = parse_args()
    request = " ".join(args.request).strip() or "I want to focus on AI engineering next term. Recommend 3 courses."

    use_sdk = has_usable_api_key() and not args.offline
    if use_sdk:
        try:
            print(f"Using OpenAI model: {os.getenv('OPENAI_MODEL', DEFAULT_MODEL)}", file=sys.stderr)
            output = await run_agent(request)
            mode = "sdk"
        except Exception as exc:
            transcript_path = save_error_transcript(request, exc, "sdk")
            print(f"SDK-backed run failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            print(f"Error transcript saved to: {transcript_path}", file=sys.stderr)
            print("Run with `--offline` to generate deterministic local evidence.", file=sys.stderr)
            raise SystemExit(1) from exc
    else:
        output = advise_offline(request)
        mode = "offline"

    transcript_path = save_transcript(request, output, mode)
    print(json.dumps(output.model_dump(), indent=2))
    print(f"\nTranscript saved to: {transcript_path}")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
