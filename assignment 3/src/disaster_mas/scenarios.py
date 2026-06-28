"""Deterministic scenario fixtures."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


SCENARIOS: dict[str, dict[str, Any]] = {
    "flood": {
        "resources": {"rescue_teams": 2, "ambulances": 1, "boats": 2, "supply_kits": 3},
        "reports": [
            {
                "location": "North Residence",
                "water_level": "rising",
                "stranded_people": 14,
                "injured_people": 3,
                "confidence": 0.82,
            },
            {
                "location": "Library Underpass",
                "water_level": "severe",
                "stranded_people": 5,
                "injured_people": 1,
                "confidence": 0.74,
            },
            {
                "location": "West Clinic",
                "water_level": "moderate",
                "stranded_people": 2,
                "injured_people": 4,
                "confidence": 0.66,
            },
        ],
        "route_status": {
            "North Residence": {
                "primary": "Pine Gate",
                "primary_blocked": False,
                "alternate": "Stadium Loop",
                "travel_minutes": 11,
            },
            "Library Underpass": {
                "primary": "Main Tunnel",
                "primary_blocked": True,
                "alternate": "Sherbrooke East",
                "travel_minutes": 19,
            },
            "West Clinic": {
                "primary": "Cedar Road",
                "primary_blocked": False,
                "alternate": "South Service Lane",
                "travel_minutes": 9,
            },
        },
    },
    "aftershock": {
        "resources": {"rescue_teams": 1, "ambulances": 1, "boats": 1, "supply_kits": 2},
        "reports": [
            {
                "location": "North Residence",
                "water_level": "severe",
                "stranded_people": 18,
                "injured_people": 5,
                "confidence": 0.78,
            },
            {
                "location": "Engineering Annex",
                "water_level": "moderate",
                "stranded_people": 6,
                "injured_people": 2,
                "confidence": 0.61,
            },
        ],
        "route_status": {
            "North Residence": {
                "primary": "Pine Gate",
                "primary_blocked": True,
                "alternate": "Stadium Loop",
                "travel_minutes": 17,
            },
            "Engineering Annex": {
                "primary": "Peel Entrance",
                "primary_blocked": False,
                "alternate": "Loading Dock",
                "travel_minutes": 8,
            },
        },
    },
    "conflicting_reports": {
        "resources": {"rescue_teams": 2, "ambulances": 1, "boats": 1, "supply_kits": 2},
        "reports": [
            {
                "location": "Library Underpass",
                "water_level": "severe",
                "stranded_people": 9,
                "injured_people": 2,
                "confidence": 0.72,
            },
            {
                "location": "Library Underpass",
                "water_level": "clear",
                "stranded_people": 0,
                "injured_people": 0,
                "confidence": 0.58,
            },
            {
                "location": "West Clinic",
                "water_level": "moderate",
                "stranded_people": 4,
                "injured_people": 5,
                "confidence": 0.69,
            },
        ],
        "route_status": {
            "Library Underpass": {
                "primary": "Main Tunnel",
                "primary_blocked": True,
                "alternate": "Sherbrooke East",
                "travel_minutes": 21,
            },
            "West Clinic": {
                "primary": "Cedar Road",
                "primary_blocked": False,
                "alternate": "South Service Lane",
                "travel_minutes": 9,
            },
        },
    },
}


def get_scenario(name: str) -> dict[str, Any]:
    if name not in SCENARIOS:
        valid = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"unknown scenario '{name}'. Valid scenarios: {valid}")
    return deepcopy(SCENARIOS[name])
