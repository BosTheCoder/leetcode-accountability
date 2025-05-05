#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for LeetCode accountability tracking.
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

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


@dataclass
class DateRange:
    """Class to handle date range options for CLI commands."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days: Optional[int] = None

    def __post_init__(self):
        """Validate and set date range based on provided parameters."""
        if self.days is not None:
            self.end_date = datetime.now()
            self.start_date = self.end_date - timedelta(days=self.days)
        elif self.start_date is not None and self.end_date is not None:
            # Both start_date and end_date are provided, calculate days
            self.days = (self.end_date - self.start_date).days + 1
        else:
            raise ValueError("Either 'days' or both 'start_date' and 'end_date' must be provided")


# Create a Typer app instance
app = typer.Typer(help="LeetCode submission statistics CLI")


@app.command()
def stats(
    usernames: List[str] = typer.Argument(
        None,
        help="List of LeetCode usernames to analyze (defaults to active users if not provided)",
    ),
    days: int = typer.Option(None, help="Number of days to look back for submissions"),
    start_date: Optional[datetime] = typer.Option(None, help="Start date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = typer.Option(None, help="End date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)"),
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

    # Create date range from provided parameters
    try:
        date_range = DateRange(days=days, start_date=start_date, end_date=end_date)
        if days:
            print(f"Fetching statistics for {len(usernames)} users over the past {days} days...")
        else:
            print(f"Fetching statistics for {len(usernames)} users between {date_range.start_date.isoformat()} and {date_range.end_date.isoformat()}...")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Get stats for each user
    user_submissions_list = []
    for username in usernames:
        print(f"Fetching submissions for user [{username}]")
        user_submissions = submissions_service.get_user_detailed_submissions_by_date_range(
            username, date_range.start_date, date_range.end_date
        )
        user_submissions_list.append(user_submissions)

    # Present the stats
    output = presenter.present_submissions(user_submissions_list, date_range.days, None)
    print(output)

    # Write to file
    presenter.write_to_file("report", output)
    print(f"Report has been written to file")


@app.command()
def weekly_run(
    days: int = typer.Option(None, help="Number of days to look back for submissions"),
    start_date: Optional[datetime] = typer.Option(None, help="Start date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = typer.Option(None, help="End date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)"),
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

    # Create date range from provided parameters
    try:
        date_range = DateRange(days=days, start_date=start_date, end_date=end_date)
        print(f"Running weekly accountability check for {len(active_users)} active users over the past {date_range.days} days (between {date_range.start_date.isoformat()} and {date_range.end_date.isoformat()})...")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Initialize Splitwise client
    splitwise_api_key = os.environ["SPLITWISE_API_KEY"]
    splitwise_client = SplitwiseClient(splitwise_api_key)

    # Initialize accountability service
    leetcode_client = LeetCodeGraphQLClient()
    submissions_service = UserSubmissionsService(leetcode_client)
    accountability_service = CodingAccountabilityService(
        submission_service=submissions_service,
        splitwise_client=splitwise_client,
        users=active_users,
        cost_per_question=cost_per_question,
    )

    # Run accountability check
    user_submissions = accountability_service.hold_accountable(date_range.start_date, date_range.end_date)

    # Present the stats
    completion_message = f"Accountability check completed. Users have been charged {cost_per_question} per missed question."
    output = presenter.present_submissions(user_submissions, date_range.days, completion_message)
    print(output)

    # Write to file
    presenter.write_to_file("report", output)
    print(f"Report has been written to file")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
