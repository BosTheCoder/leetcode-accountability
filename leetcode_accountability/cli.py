#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for LeetCode accountability tracking.
"""

from datetime import datetime
from typing import List
import os

import typer
from dotenv import load_dotenv

from .entities import UserStats
from .leetcode_client import LeetCodeGraphQLClient
from .submission_service import UserSubmissionsService
from .accountability_service import CodingAccountabilityService
from .splitwise_client import SplitwiseClient
from .util import get_active_users

# Create a Typer app instance
app = typer.Typer(help="LeetCode submission statistics CLI")


def print_table_header(days: int):
    """Print the table header."""
    print(f"\nLeetCode Statistics (Last {days} Days)")
    print("-" * 80)
    print(
        f"{'Username':<20} {'Total Questions':<15} {'Easy':<10} {'Medium':<10} {'Hard':<10}"
    )
    print("-" * 80)


def print_table_row(stats: UserStats):
    """Print a row of the table."""
    print(
        f"{stats.username:<20} {stats.total_questions:<15} {stats.easy_count:<10} {stats.medium_count:<10} {stats.hard_count:<10}"
    )


@app.command()
def stats(
    usernames: List[str] = typer.Argument(
        ..., help="List of LeetCode usernames to analyze"
    ),
    days: int = typer.Option(7, help="Number of days to look back for submissions"),
):
    """
    Generate LeetCode submission statistics for specified users.
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize the client and service
    leetcode_client = LeetCodeGraphQLClient()
    submissions_service = UserSubmissionsService(leetcode_client)

    print(
        f"Fetching statistics for {len(usernames)} users over the past {days} days..."
    )

    # Print the table header
    print_table_header(days)

    # Get stats for each user
    for username in usernames:
        print(f"Processing {username}...")
        user_stats = submissions_service.get_user_stats(username, days)

        # Print the stats
        print_table_row(user_stats)

    print("-" * 80)


@app.command()
def weekly_run(
    days: int = typer.Option(7, help="Number of days to look back for submissions"),
    cost_per_question: float = typer.Option(10.0, help="Cost per missed question"),
):
    """
    Run the weekly accountability check for all active users.
    This will charge users for missed questions and print their stats.
    """
    # Load environment variables
    load_dotenv()

    # Get active users
    active_users = get_active_users()

    if not active_users:
        print("No active users found.")
        return

    print(f"Running weekly accountability check for {len(active_users)} active users...")

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
        cost_per_question=cost_per_question
    )

    # Run accountability check
    print(f"Holding users accountable for the past {days} days...")
    user_stats = accountability_service.hold_accountable()

    # Print stats for each user
    print_table_header(days)
    for stats in user_stats:
        print_table_row(stats)

    print("-" * 80)
    print(f"Weekly accountability check completed. Users have been charged {cost_per_question} per missed question.")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
