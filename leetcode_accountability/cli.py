#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for LeetCode accountability tracking.
"""

from datetime import datetime
from typing import List

import typer

from .entities import UserStats
from .leetcode_client import LeetCodeGraphQLClient
from .submission_service import UserSubmissionsService

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



def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
