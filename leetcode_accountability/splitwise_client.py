"""
Client for Splitwise API to create expenses and manage user data.
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from typing import List

from splitwise import Splitwise
from splitwise.category import Category
from splitwise.expense import Expense
from splitwise.user import ExpenseUser

LOGGER = logging.getLogger(__name__)


@dataclass
class UserShare:
    user_id: int
    paid_share: float = 0.0
    owed_share: float = 0.0


@dataclass
class SplitwiseExpenseData:
    cost: float
    description: str
    details: str
    date: str  # ISO format: "YYYY-MM-DDTHH:MM:SSZ"
    group_id: int
    category: Category = Category().setId(2)
    repeat_interval: str = "never"
    currency_code: str = "GBP"
    users: List[UserShare] = field(default_factory=list)


class SplitwiseClient:
    def __init__(self, api_key: str):
        self.splitwise = sObj = Splitwise(
            "<consumer key>", "<consumer secret>", api_key=api_key
        )
        LOGGER.info("Splitwise client initialized with API key.")
        LOGGER.info(sObj.getCurrentUser())

    def create_expense(self, expense_data: SplitwiseExpenseData):
        LOGGER.info("Creating expense with data: %s", expense_data)
        expense = Expense()
        expense.setCost(str(expense_data.cost))
        expense.setDescription(expense_data.description)
        expense.setDetails(expense_data.details)
        expense.setDate(
            datetime.datetime.fromisoformat(expense_data.date.replace("Z", "+00:00"))
        )
        expense.setRepeatInterval(expense_data.repeat_interval)
        expense.setCurrencyCode(expense_data.currency_code)
        category_id = expense_data.category
        expense.setCategory(category_id)
        expense.setGroupId(expense_data.group_id)

        for user in expense_data.users:
            expense_user = ExpenseUser()
            expense_user.setId(user.user_id)
            expense_user.setPaidShare(str(user.paid_share))
            expense_user.setOwedShare(str(user.owed_share))
            expense.addUser(expense_user)

        created_expense = self.splitwise.createExpense(expense)
        return created_expense

    def get_current_user(self):
        return self.splitwise.getCurrentUser()


if __name__ == "__main__":
    # Example usage
    import os

    from dotenv import load_dotenv

    load_dotenv()  # Automatically loads from `.env` in current directory
    logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG for more verbosity
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Now you can use the variables
    api_key = os.getenv("SPLITWISE_API_KEY")
    group_id = int(os.getenv("SPLITWISE_GROUP_ID"))
    client = SplitwiseClient(api_key)
    expense_data = SplitwiseExpenseData(
        cost=25.0,
        description="Grocery run",
        details="Bought vegetables and snacks",
        date="2025-04-14T13:00:00Z",
        group_id=group_id,
        users=[
            UserShare(user_id=6996697, paid_share=0, owed_share=25),
            UserShare(user_id=103535402, paid_share=25, owed_share=0),
        ],
    )
    print(expense_data)
    created_expense = client.create_expense(expense_data)
    print("Expense created:", created_expense)
