"""
Core entity models for the LeetCode accountability system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class Difficulty(Enum):
    """Enum representing LeetCode problem difficulties."""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass
class UserStats:
    """Data class to hold user submission statistics."""
    username: str
    total_questions: int = 0
    easy_count: int = 0
    medium_count: int = 0
    hard_count: int = 0

    def add_question(self, difficulty: str):
        """Increment the appropriate counter for a question difficulty."""
        self.total_questions += 1
        if difficulty == Difficulty.EASY.value:
            self.easy_count += 1
        elif difficulty == Difficulty.MEDIUM.value:
            self.medium_count += 1
        elif difficulty == Difficulty.HARD.value:
            self.hard_count += 1
