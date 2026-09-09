from datetime import datetime

from leetcode_accountability.entities import User, UserSubmissions

from .submission_service import UserSubmissionsService


class CodingAccountabilityService:

    def __init__(
        self,
        submission_service: UserSubmissionsService,
        users: list[User],
    ):
        """Initialize the AccountabilityService."""
        self.submission_service = submission_service
        self.users = users

    def hold_accountable(self, start_date: datetime, end_date: datetime, min_hours_between_submissions: int = 24) -> list[UserSubmissions]:
        """
        Hold users accountable for their LeetCode submissions.

        This method processes each user, retrieves their detailed submission data,
        and reports who has fallen short of their goal.

        Args:
            start_date: The start date for filtering submissions.
            end_date: The end date for filtering submissions.
            min_hours_between_submissions: Minimum hours between submissions of the same
                question to count them as separate submissions. Default is 24 hours.
        """
        print(f"Holding users accountable between {start_date.date()} and {end_date.date()}...")
        print("--" * 80)
        all_user_submissions = []
        for user in self.users:
            user_submissions = self.submission_service.get_user_detailed_submissions_by_date_range(
                username=user.leetcode_id, start_date=start_date, end_date=end_date, min_hours_between_submissions=min_hours_between_submissions
            )
            all_user_submissions.append(user_submissions)

            num_missed_questions = user.min_questions - user_submissions.total_questions

            if num_missed_questions <= 0:
                print(
                    f"{user.name.capitalize()} has met their goal of {user.min_questions} questions."
                )
                continue

            print(
                f"{user.name.capitalize()} completed {user_submissions.total_questions} questions between {start_date.date()} and {end_date.date()}. "
                f"Question Distribution: Easy: {user_submissions.easy_count}, Medium: {user_submissions.medium_count}, Hard: {user_submissions.hard_count}. "
                f"Meaning they missed {num_missed_questions} questions from their goal of {user.min_questions}."
            )
        print("--" * 80)
        return all_user_submissions
