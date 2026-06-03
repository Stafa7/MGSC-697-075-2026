from __future__ import annotations

import json
import os

from advising_agent.fixtures import load_student_profile
from advising_agent.guardrails import missing_prerequisite_blocker
from advising_agent.models import AdvisingRecommendation
from advising_agent.tools import check_prerequisites_tool, flag_policy_risk_tool, search_courses_tool


DEFAULT_MODEL = "gpt-5-nano"


AGENT_INSTRUCTIONS = """
You are CourseAdvisingAgent, a single-agent course advising assistant for an AI agents class assignment.

Operate only inside the fake fixture world provided by the tools. Do not use or claim real McGill data,
real registration authority, or official academic advising authority.

Required behavior:
- Use the course search, prerequisite, and policy tools before making course-specific recommendations.
- Return only the structured AdvisingRecommendation output type.
- If prerequisites are missing, mark that course as do_not_take and explain the missing prerequisites.
- If advisor approval is needed, set advisor_approval_required to true and include the reason.
- If the request asks for an exception or override, require advisor approval.
- Keep recommendations within the fixture data and include the fixture scope note.
"""


def build_course_advising_agent():
    try:
        from agents import Agent
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OpenAI Agents SDK is not installed. Run `python -m venv .venv`, "
            "`source .venv/bin/activate`, and `PIP_CACHE_DIR=.pip-cache pip install -e \".[dev]\"`."
        ) from exc

    return Agent(
        name="CourseAdvisingAgent",
        model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        instructions=AGENT_INSTRUCTIONS,
        tools=[search_courses_tool, check_prerequisites_tool, flag_policy_risk_tool],
        output_type=AdvisingRecommendation,
        output_guardrails=[missing_prerequisite_blocker],
    )


async def run_agent(user_request: str) -> AdvisingRecommendation:
    try:
        from agents import Runner
    except ModuleNotFoundError as exc:
        raise RuntimeError("OpenAI Agents SDK is not installed.") from exc

    agent = build_course_advising_agent()
    student_profile = load_student_profile()
    agent_input = (
        "Use this active fake student profile as passed state for the run:\n"
        f"{json.dumps(student_profile.model_dump(), indent=2)}\n\n"
        "Student request:\n"
        f"{user_request}"
    )
    result = await Runner.run(agent, agent_input)
    return result.final_output
