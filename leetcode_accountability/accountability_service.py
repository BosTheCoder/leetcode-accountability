
from leetcode_accountability.entities import Payment, User, UserStats
from leetcode_accountability.splitwise_client import SplitwiseClient, SplitwiseExpenseData, UserShare
from .submission_service import UserSubmissionsService

class CodingAccountabilityService:

    def __init__(self, submission_service: UserSubmissionsService,splitwise_client: SplitwiseClient, users: list[User], days: int = 7, cost_per_question: float = 10):
        """Initialize the AccountabilityService."""
        self.submission_service = submission_service
        self.splitwise_client = splitwise_client
        self.users = users
        self.days = days
        self.cost_per_question = cost_per_question


    def hold_accountable(self) -> None
        for user in self.users:
            user_stats = self.submission_service.get_user_stats(user.leetcode_id, self.days)

            num_missed_questions = user.min_questions - user_stats.total_questions
            cost = num_missed_questions * self.cost_per_question
            expense_data = SplitwiseExpenseData(
                amount=cost,
                group_id=user.splitwise_group_id,
                user_id=user.splitwise_id,
                description=f"Missed {num_missed_questions} questions in the last {self.days} days.",
                users=[
                    UserShare(
                        user_id=user.splitwise_id,
                        paid_share=0.0,
                        owed_share=cost
                    )
                ]
            )
            other_users = [
                other_user for other_user in self.users if other_user != user
            ]

            for other_user in other_users:
                expense_data.users.append(
                    UserShare(
                        user_id=other_user.splitwise_id,
                        paid_share=cost/len(other_users),
                        owed_share=0.0
                    )
                )

            self.splitwise_client.create_expense(expense_data)
