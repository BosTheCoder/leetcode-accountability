"""
Service for processing LeetCode submissions and generating statistics.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, TypedDict

from .entities import UserStats, Submission, UserSubmissions
from .leetcode_client import LeetCodeGraphQLClient, RecentSubmission, QuestionDetail


class SubmissionWithDetails(RecentSubmission, total=False):
    """TypedDict representing a submission with optional question details."""
    difficulty: str


class UserSubmissionsService:
    """
    Service for retrieving and filtering user submissions.
    """

    def __init__(self, leetcode_client: LeetCodeGraphQLClient):
        """
        Initialize the user submissions service.

        Args:
            leetcode_client: An instance of LeetCodeGraphQLClient.
        """
        self.client = leetcode_client

    def get_submissions_between_dates(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = False,
    ) -> List[SubmissionWithDetails]:
        """
        Get all accepted submissions for a user between two dates.

        Args:
            username: The LeetCode username.
            start_date: The start date for filtering submissions.
            end_date: The end date for filtering submissions.
            include_details: Whether to include question details like difficulty.

        Returns:
            A list of submission dictionaries with timestamps between the specified dates.
        """
        # Get a large number of submissions to ensure we cover the date range
        # LeetCode might limit this, so we'll take a reasonable limit
        submissions = self.client.get_recent_accepted_submissions(username, limit=20)

        # Filter submissions by date range
        filtered_submissions = []
        for submission in submissions:
            # Convert timestamp to datetime
            submission_date = datetime.fromtimestamp(int(submission["timestamp"]))

            # Check if the submission is within the date range
            if start_date <= submission_date <= end_date:
                # Optionally fetch question details
                if include_details:
                    question_details = self.client.get_question_detail(
                        submission["titleSlug"]
                    )
                    submission["difficulty"] = question_details["difficulty"]

                # Add to filtered list
                filtered_submissions.append(submission)

        return filtered_submissions

    def get_unique_questions_between_dates(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = False,
    ) -> List[SubmissionWithDetails]:
        """
        Get unique questions solved by a user between two dates.

        Args:
            username: The LeetCode username.
            start_date: The start date for filtering submissions.
            end_date: The end date for filtering submissions.
            include_details: Whether to include question details like difficulty.

        Returns:
            A list of unique questions solved between the specified dates.
        """
        submissions = self.get_submissions_between_dates(
            username, start_date, end_date, include_details
        )

        # Use a dictionary to track unique questions by title_slug
        unique_questions = {}
        for submission in submissions:
            title_slug = submission["titleSlug"]
            if title_slug not in unique_questions:
                unique_questions[title_slug] = submission

        return list(unique_questions.values())

    def get_user_stats(self, username: str, days: int) -> UserStats:
        """
        Get statistics for a user's submissions over the past number of days.

        Args:
            username: The LeetCode username.
            days: Number of days to look back.

        Returns:
            A UserStats object with submission statistics.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        questions = self.get_unique_questions_between_dates(
            username, start_date, end_date, include_details=True
        )

        # Create and populate stats object
        stats = UserStats(username=username)

        for question in questions:
            if "difficulty" in question:
                stats.add_question(question["difficulty"])

        return stats

    def get_user_detailed_submissions(self, username: str, days: int) -> UserSubmissions:
        """
        Get detailed submission data for a user over the past number of days.

        Args:
            username: The LeetCode username.
            days: Number of days to look back.

        Returns:
            A UserSubmissions object with lists of submission objects by difficulty.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        questions = self.get_unique_questions_between_dates(
            username, start_date, end_date, include_details=True
        )

        # Create user submissions object
        user_submissions = UserSubmissions(username=username)

        for question in questions:
            # Create a submission object
            submission = Submission(
                name=question["title"],
                submission_time=datetime.fromtimestamp(int(question["timestamp"])),
                difficulty=question["difficulty"]
            )
            # Add to the appropriate list
            user_submissions.add_submission(submission)

        return user_submissions
