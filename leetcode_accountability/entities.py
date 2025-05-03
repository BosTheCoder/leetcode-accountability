"""
Core entity models for the LeetCode accountability system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


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


@dataclass
class Submission:
    """Data class to represent a single LeetCode submission."""

    name: str  # Name of the problem
    submission_time: datetime  # When the submission was made
    difficulty: str  # Difficulty level of the problem (Easy, Medium, Hard)
    url: str


@dataclass
class UserSubmissions:
    """Data class to hold detailed user submission data with lists of submissions."""

    username: str
    easy_submissions: List[Submission] = field(default_factory=list)
    medium_submissions: List[Submission] = field(default_factory=list)
    hard_submissions: List[Submission] = field(default_factory=list)

    @property
    def total_questions(self) -> int:
        """Get the total number of submissions across all difficulty levels."""
        return (
            len(self.easy_submissions)
            + len(self.medium_submissions)
            + len(self.hard_submissions)
        )

    @property
    def easy_count(self) -> int:
        """Get the count of easy submissions."""
        return len(self.easy_submissions)

    @property
    def medium_count(self) -> int:
        """Get the count of medium submissions."""
        return len(self.medium_submissions)

    @property
    def hard_count(self) -> int:
        """Get the count of hard submissions."""
        return len(self.hard_submissions)

    def add_submission(self, submission: Submission):
        """Add a submission to the appropriate list based on its difficulty."""
        if submission.difficulty == Difficulty.EASY.value:
            self.easy_submissions.append(submission)
        elif submission.difficulty == Difficulty.MEDIUM.value:
            self.medium_submissions.append(submission)
        elif submission.difficulty == Difficulty.HARD.value:
            self.hard_submissions.append(submission)


@dataclass
class User:
    """Data class to represent a user in the LeetCode accountability system."""

    # TODO remove references to specific clients in this base entity class
    name: str
    leetcode_id: str
    splitwise_id: int | None
    splitwise_group_id: int | None
    email_address: str | None
    min_questions: int
    is_active: bool
