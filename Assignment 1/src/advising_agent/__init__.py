"""McGill-style single-agent course advising assignment package."""

from advising_agent.advisor import advise_offline
from advising_agent.models import AdvisingRecommendation

__all__ = ["AdvisingRecommendation", "advise_offline"]

