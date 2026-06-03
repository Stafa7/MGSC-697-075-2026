from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from advising_agent.models import Course, StudentProfile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = PROJECT_ROOT / "data" / "fixtures"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_courses() -> list[Course]:
    return [Course.model_validate(item) for item in load_json(FIXTURE_DIR / "courses.json")]


def load_prerequisites() -> dict[str, list[str]]:
    raw = load_json(FIXTURE_DIR / "prerequisites.json")
    return {str(code): list(prereqs) for code, prereqs in raw.items()}


def load_student_profile() -> StudentProfile:
    return StudentProfile.model_validate(load_json(FIXTURE_DIR / "student_profile.json"))


def load_policies() -> dict[str, Any]:
    return dict(load_json(FIXTURE_DIR / "policies.json"))


def course_lookup() -> dict[str, Course]:
    return {course.code: course for course in load_courses()}


def normalize_course_code(raw: str) -> str:
    compact = raw.strip().upper().replace("-", " ")
    parts = compact.split()
    if len(parts) == 2 and parts[0] == "MGSC" and parts[1].isdigit():
        return f"MGSC {parts[1]}"
    if compact.startswith("MGSC") and compact[4:].strip().isdigit():
        return f"MGSC {compact[4:].strip()}"
    return compact

