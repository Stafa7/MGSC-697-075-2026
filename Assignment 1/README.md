# McGill Course Advising Agent

This repo contains a small single-agent course advising system for an AI Agents assignment. The system uses a fake McGill-style course catalog, prerequisite table, student profile, and policy rules to help a student choose courses, identify risks, and decide when human advisor approval is required.

The project is intentionally scoped. It is not official McGill advising, it does not use real student records, it does not register anyone in courses, and it does not make external side effects.

## Requirements

- Python 3.11+
- OpenAI API key for SDK-backed agent runs
- No API key needed for deterministic offline tests and evals
- Default SDK model: `gpt-5-nano`, chosen for low-cost screenshot/evidence runs

## Local Virtual Environment

Use a project-local virtual environment. This keeps dependencies inside this assignment folder:

```bash
python -m venv .venv
source .venv/bin/activate
PIP_CACHE_DIR=.pip-cache pip install -r requirements.txt
PIP_CACHE_DIR=.pip-cache pip install -e . --no-deps --no-build-isolation
```

`.venv/` and `.pip-cache/` are ignored by Git. `requirements.txt` pins the top-level package versions used for reproducible setup, and `pyproject.toml` makes the local package installable.

Create a local environment file:

```bash
cp .env.example .env
```

Then edit `.env` and set `OPENAI_API_KEY` if you want SDK-backed runs.

Do not run the API key as a standalone shell command. Either edit `.env`:

```text
OPENAI_API_KEY=sk-your-real-key
OPENAI_MODEL=gpt-5-nano
```

or export it for the current shell session:

```bash
export OPENAI_API_KEY="sk-your-real-key"
export OPENAI_MODEL="gpt-5-nano"
```

You can override `OPENAI_MODEL`, but the default is intentionally the low-cost `gpt-5-nano` model.

## Run

Offline deterministic mode, useful for reproducible grading without API calls:

```bash
python -m advising_agent.run_demo --offline "I want to focus on AI engineering next term. Recommend 3 courses."
```

SDK-backed mode, using the OpenAI Agents SDK:

```bash
python -m advising_agent.run_demo "I want to focus on AI engineering next term. Recommend 3 courses."
```

If `OPENAI_API_KEY` is missing, the demo automatically uses offline mode.

## Test And Eval

```bash
pytest
python -m evals.run_evals
```

Eval results are written to `evals/results/eval_results.json`. Case transcripts are written to `evidence/run_transcripts/`.

Final verified results:

- Unit tests: `7 passed`
- Eval cases: `6/6 passed`
- SDK-backed evidence runs: saved under `evidence/run_transcripts/*_sdk.md`
- Reflection report: `docs/reflection_report.pdf`

## Design Summary

- Agent: `CourseAdvisingAgent`
- SDK: Python OpenAI Agents SDK with `Agent`, `Runner`, `@function_tool`, structured `output_type`, and output guardrail
- Typed tools: `search_courses`, `check_prerequisites`, `flag_policy_risk`
- Structured output: `AdvisingRecommendation`
- Blocking guardrail: `MissingPrerequisiteBlocker`
- Escalation rule: `AdvisorApprovalRequired`
- State strategy: local fixtures are stored; request and profile are passed into each run; course matches, prerequisite checks, policy risks, approval requirement, and final recommendation are recomputed each run

## Repo Map

```text
data/fixtures/       Fake course, prerequisite, student, and policy data
src/advising_agent/  Agent, tools, models, guardrails, and demo runner
evals/               Eval cases and eval runner
evidence/            Saved transcripts, traces, and screenshots
docs/                Assignment instructions, prior plan, design notes, reflection
tests/               Unit and offline eval tests
```

## Known Limitations

- The catalog and policies are fake and simplified.
- The system cannot replace a human advisor.
- SDK output still depends on model behavior, so the guardrail and evals are essential.
- Offline mode is deterministic evidence of policy behavior; SDK-backed screenshots and transcripts are included as live model evidence.

## One-Minute Defense

I built a single-agent course advising assistant using the OpenAI Agents SDK. The domain is intentionally small: a fake McGill-style course catalog, prerequisite table, student profile, and policy rules. The agent uses three typed tools to search courses, check prerequisites, and flag policy risks. Its final answer is a structured recommendation object that includes course recommendations, missing prerequisites, policy risks, blocking status, and whether advisor approval is required. The main guardrail is `MissingPrerequisiteBlocker`, which prevents the agent from recommending enrollment in courses where prerequisites are missing. I evaluated the system with six cases, including missing prerequisites, credit overload, capstone approval, and unknown course codes. I also captured SDK-backed `gpt-5-nano` transcripts and screenshots showing live agent behavior.
