#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for LeetCode accountability tracking.
"""

import os
from datetime import datetime
from enum import Enum
from typing import List

import typer
from dotenv import load_dotenv

from .accountability_service import CodingAccountabilityService
from .entities import UserSubmissions
from .leetcode_client import LeetCodeGraphQLClient
from .presenters import get_presenter
from .splitwise_client import SplitwiseClient
from .submission_service import UserSubmissionsService
from .util import get_active_users


# Define output type enum
class OutputType(str, Enum):
    TEXT = "text"
    HTML = "html"


# Create a Typer app instance
app = typer.Typer(help="LeetCode submission statistics CLI")


@app.command()
def stats(
    usernames: List[str] = typer.Argument(
        None,
        help="List of LeetCode usernames to analyze (defaults to active users if not provided)",
    ),
    days: int = typer.Option(7, help="Number of days to look back for submissions"),
    output_type: OutputType = typer.Option(
        OutputType.TEXT, help="Output format (text or html)"
    ),
):
    """
    Generate LeetCode submission statistics for specified users.
    If no usernames are provided, statistics for all active users will be shown.
    """
    # Load environment variables
    load_dotenv()

    # Initialize the client and service
    leetcode_client = LeetCodeGraphQLClient()
    submissions_service = UserSubmissionsService(leetcode_client)

    # Get the appropriate presenter
    presenter = get_presenter(output_type)

    # If no usernames provided, use active users
    if not usernames:
        active_users = get_active_users()
        if not active_users:
            print("No active users found.")
            return

        usernames = [user.leetcode_id for user in active_users]
        print(f"No usernames provided. Using {len(usernames)} active users.")

    print(
        f"Fetching statistics for {len(usernames)} users over the past {days} days..."
    )

    # Get stats for each user
    user_submissions_list = []
    for username in usernames:
        print(f"Fetching submissions for user [{username}]")
        user_submissions = submissions_service.get_user_detailed_submissions(
            username, days
        )
        user_submissions_list.append(user_submissions)

    # Present the stats
    output = presenter.present_submissions(user_submissions_list, days, None)
    print(output)

    # Write to file
    presenter.write_to_file("report", output)
    print(f"Report has been written to file")


@app.command()
def weekly_run(
    days: int = typer.Option(7, help="Number of days to look back for submissions"),
    cost_per_question: float = typer.Option(10.0, help="Cost per missed question"),
    output_type: OutputType = typer.Option(
        OutputType.TEXT, help="Output format (text or html)"
    ),
):
    """
    Run the weekly accountability check for all active users.
    This will charge users for missed questions and print their stats.
    """
    # Load environment variables
    load_dotenv()

    # Get active users
    active_users = get_active_users()

    # Get the appropriate presenter
    presenter = get_presenter(output_type)

    if not active_users:
        print("No active users found.")
        return

    print(
        f"Running weekly accountability check for {len(active_users)} active users..."
    )

    # Initialize services
    leetcode_client = LeetCodeGraphQLClient()
    submissions_service = UserSubmissionsService(leetcode_client)

    # Initialize Splitwise client
    api_key = os.getenv("SPLITWISE_API_KEY")
    if not api_key:
        print("Error: SPLITWISE_API_KEY environment variable not found.")
        return

    splitwise_client = SplitwiseClient(api_key)

    # Initialize accountability service
    accountability_service = CodingAccountabilityService(
        submission_service=submissions_service,
        splitwise_client=splitwise_client,
        users=active_users,
        days=days,
        cost_per_question=cost_per_question,
    )

    # Run accountability check
    print(f"Holding users accountable for the past {days} days...")
    user_submissions = accountability_service.hold_accountable()

    # Create completion message
    completion_message = f"Weekly accountability check completed. Users have been charged {cost_per_question} per missed question."

    # Present the stats
    output = presenter.present_submissions(user_submissions, days, completion_message)
    print(output)

    # Write to file
    presenter.write_to_file("report", output)
    print(f"Report has been written to file")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
