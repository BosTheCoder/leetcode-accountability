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
            days: Optional number of days to look back from current date.
            start_date: Optional start date for filtering submissions.
            end_date: Optional end date for filtering submissions.

        Raises:
            ValueError: If neither days nor both start_date and end_date are provided.
        """
        self.leetcode_client = leetcode_client

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
        submissions = self.leetcode_client.get_recent_accepted_submissions(
            username, limit=20
        )

        # Filter submissions by date range
        filtered_submissions = []
        for submission in submissions:
            # Convert timestamp to datetime
            submission_date = datetime.fromtimestamp(int(submission["timestamp"]))

            # Check if the submission is within the date range
            if start_date <= submission_date <= end_date:
                # Optionally fetch question details
                if include_details:
                    question_details = self.leetcode_client.get_question_detail(
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
        min_hours_between_submissions: int = 24,
    ) -> List[SubmissionWithDetails]:
        """
        Get unique questions solved by a user between two dates.

        Submissions of the same question are considered unique if they are
        separated by at least min_hours_between_submissions hours.

        Args:
            username: The LeetCode username.
            start_date: The start date for filtering submissions.
            end_date: The end date for filtering submissions.
            include_details: Whether to include question details like difficulty.
            min_hours_between_submissions: Minimum hours between submissions of the same
                question to count them as separate submissions. Default is 24 hours.

        Returns:
            A list of unique questions solved between the specified dates.
        """
        submissions = self.get_submissions_between_dates(
            username, start_date, end_date, include_details
        )

        # Sort submissions by timestamp to process them chronologically
        submissions.sort(key=lambda x: int(x["timestamp"]))

        # Track submissions by question and their timestamps
        question_submissions = {}
        unique_submissions = []

        for submission in submissions:
            title_slug = submission["titleSlug"]
            submission_time = datetime.fromtimestamp(int(submission["timestamp"]))

            if title_slug not in question_submissions:
                # First submission of this question
                question_submissions[title_slug] = [submission_time]
                unique_submissions.append(submission)
            else:
                # Check if enough time has passed since the last submission of this question
                last_submission_time = question_submissions[title_slug][-1]
                time_diff = submission_time - last_submission_time

                if time_diff >= timedelta(hours=min_hours_between_submissions):
                    # Enough time has passed, count as a new unique submission
                    question_submissions[title_slug].append(submission_time)
                    unique_submissions.append(submission)
                # If not enough time has passed, skip this submission

        return unique_submissions

    def get_user_detailed_submissions_by_date_range(
        self, username: str, start_date: datetime, end_date: datetime, min_hours_between_submissions: int = 24
    ) -> UserSubmissions:
        """
        Get detailed submission data for a user between specified start and end dates.

        Args:
            username: The LeetCode username.
            start_date: The start date for filtering submissions.
            end_date: The end date for filtering submissions.
            min_hours_between_submissions: Minimum hours between submissions of the same
                question to count them as separate submissions. Default is 24 hours.

        Returns:
            A UserSubmissions object with lists of submission objects by difficulty.
        """
        questions: SubmissionWithDetails = self.get_unique_questions_between_dates(
            username, start_date, end_date, include_details=True, min_hours_between_submissions=min_hours_between_submissions
        )

        # Create user submissions object
        user_submissions = UserSubmissions(username=username)

        for question in questions:
            # Create a submission object
            submission = Submission(
                name=question["title"],
                submission_time=datetime.fromtimestamp(int(question["timestamp"])),
                difficulty=question["difficulty"],
                url=f"https://leetcode.com/problems/{question["titleSlug"]}",
            )
            # Add to the appropriate list
            user_submissions.add_submission(submission)

        return user_submissions
