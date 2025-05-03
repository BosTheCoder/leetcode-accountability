from datetime import datetime

from leetcode_accountability.entities import User, UserSubmissions
from leetcode_accountability.splitwise_client import (
    SplitwiseClient,
    SplitwiseExpenseData,
    UserShare,
)

from .submission_service import UserSubmissionsService


class CodingAccountabilityService:

    def __init__(
        self,
        submission_service: UserSubmissionsService,
        splitwise_client: SplitwiseClient,
        users: list[User],
        days: int = 7,
        cost_per_question: float = 10,
    ):
        """Initialize the AccountabilityService."""
        self.submission_service = submission_service
        self.splitwise_client = splitwise_client
        self.users = users
        self.days = days
        self.cost_per_question = cost_per_question

    def hold_accountable(self) -> list[UserSubmissions]:
        """
        Hold users accountable for their LeetCode submissions.

        This method processes each user, retrieves their detailed submission data,
        and creates Splitwise expenses for users who haven't met their goals.
        """
        print("--" * 80)
        all_user_submissions = []
        for user in self.users:
            user_submissions = self.submission_service.get_user_detailed_submissions(
                user.leetcode_id, self.days
            )
            all_user_submissions.append(user_submissions)

            num_missed_questions = user.min_questions - user_submissions.total_questions

            if num_missed_questions <= 0:
                print(
                    f"{user.name.capitalize()} has met their goal of {user.min_questions} questions. Skipping user."
                )
                continue

            if not user.splitwise_id:
                print(
                    f"{user.name.capitalize()} does not have a Splitwise ID. Skipping generating expense for user."
                )
                continue

            cost = num_missed_questions * self.cost_per_question
            description = f"{user.name.capitalize()}: {user_submissions.total_questions} questions in last {self.days} days."
            details = (
                ""
                + f"{user.name.capitalize()} completed {user_submissions.total_questions} questions in the last {self.days} days.\n"
                + f"Question Distribution: Easy: {user_submissions.easy_count}, Medium: {user_submissions.medium_count}, Hard: {user_submissions.hard_count}.\n"
                + f"Meaning they missed {num_missed_questions} questions from their goal of {user.min_questions}.\n"
                + f" They have been charged a cost of £{cost} for this."
            )

            expense_data = SplitwiseExpenseData(
                cost=cost,
                group_id=user.splitwise_group_id,
                description=description,
                details=details,
                users=[
                    UserShare(
                        user_id=user.splitwise_id, paid_share=0.0, owed_share=cost
                    )
                ],
                date=datetime.now().isoformat() + "Z",  # Current date in ISO format
            )
            other_users = [
                other_user for other_user in self.users if other_user != user
            ]

            for other_user in other_users:
                expense_data.users.append(
                    UserShare(
                        user_id=other_user.splitwise_id,
                        paid_share=cost / len(other_users),
                        owed_share=0.0,
                    )
                )

            self.splitwise_client.create_expense(expense_data)

            print(
                f"Created expense for {user.name} with cost £{cost} and description: {description}"
            )
        print("--" * 80)
        return all_user_submissions
