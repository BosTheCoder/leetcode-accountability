#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for LeetCode accountability tracking.
"""

import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, cast
from dataclasses import dataclass

import typer
from dotenv import load_dotenv

from leetcode_accountability.config import setup_logging

from .accountability_service import CodingAccountabilityService
from .entities import UserSubmissions
from .leetcode_client import LeetCodeGraphQLClient
from .presenters import get_presenter
from .splitwise_client import SplitwiseClient
from .submission_service import UserSubmissionsService
from .user_loader_service import get_active_users
from .date_utils import parse_optional_datetime, parse_optional_int


setup_logging()
LOGGER = logging.getLogger(__name__)

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
    days: Optional[str] = typer.Option(None, help="Number of days to look back for submissions", callback=parse_optional_int),
    start_date: Optional[str] = typer.Option(None, help="Start date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)", callback=parse_optional_datetime),
    end_date: Optional[str] = typer.Option(None, help="End date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)", callback=parse_optional_datetime),
    output_type: OutputType = typer.Option(
        OutputType.TEXT, help="Output format (text or html)"
    ),
):
    """
    Generate LeetCode submission statistics for specified users.
    If no usernames are provided, statistics for all active users will be shown.
    """
    LOGGER.info("Generating LeetCode submission statistics...")

    days = cast(Optional[int], days)
    start_date = cast(Optional[datetime], start_date)
    end_date = cast(Optional[datetime], end_date)
    date_range = DateRange(days=days, start_date=start_date, end_date=end_date)
    LOGGER.info(f"Date range: {date_range.start_date} to {date_range.end_date}, {date_range.days} days")

    # Load environment variables
    load_dotenv()

    # Initialize the client and service
    leetcode_client = LeetCodeGraphQLClient()
    submissions_service = UserSubmissionsService(leetcode_client)

    # If no usernames provided, use active users
    if not usernames:
        usernames = [user.leetcode_id for user in get_active_users()]
        assert usernames, "No active users found. Please check your user data."
        LOGGER.info(f"No usernames provided. Using {len(usernames)} active users.")


    # Get stats for each user
    user_submissions_list = []
    for username in usernames:
        LOGGER.info(f"Fetching submissions for user [{username}]")
        user_submissions = submissions_service.get_user_detailed_submissions_by_date_range(
            username, date_range.start_date, date_range.end_date
        )
        user_submissions_list.append(user_submissions)

     # Get the appropriate presenter & present the stats
    presenter = get_presenter(output_type)
    output = presenter.present_submissions(user_submissions_list, date_range.days, None)
    if output_type != OutputType.TEXT:
        text_presenter = get_presenter(OutputType.TEXT)
        text_output = text_presenter.present_submissions(user_submissions_list, date_range.days, None)
        LOGGER.info(text_output)
    else:
        LOGGER.info(output)

    # Write to file
    presenter.write_to_file("report", output)
    LOGGER.info(f"Report has been written to file")


@app.command()
def accountability(
    days: Optional[str] = typer.Option(None, help="Number of days to look back for submissions", callback=parse_optional_int),
    start_date: Optional[str] = typer.Option(None, help="Start date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)", callback=parse_optional_datetime),
    end_date: Optional[str] = typer.Option(None, help="End date for filtering submissions (format: YYYY-MM-DDTHH:MM:SS)", callback=parse_optional_datetime),
    cost_per_question: float = typer.Option(10.0, help="Cost per missed question"),
    output_type: OutputType = typer.Option(
        OutputType.TEXT, help="Output format (text or html)"
    ),
):
    """
    Run the weekly accountability check for all active users.
    This will charge users for missed questions and print their stats.
    """
    LOGGER.info("Running accountability check...")

    days = cast(Optional[int], days)
    start_date = cast(Optional[datetime], start_date)
    end_date = cast(Optional[datetime], end_date)
    date_range = DateRange(days=days, start_date=start_date, end_date=end_date)
    LOGGER.info(f"Date range: {date_range.start_date} to {date_range.end_date}, {date_range.days} days")

    # Load environment variables
    load_dotenv()

    # Get active users
    active_users = get_active_users()
    assert active_users, "No active users found. Please check your user data."

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

    # Get the appropriate presenter & present the stats
    presenter = get_presenter(output_type)
    output = presenter.present_submissions(user_submissions, date_range.days, completion_message)

    if output_type != OutputType.TEXT:
        text_presenter = get_presenter(OutputType.TEXT)
        text_output = text_presenter.present_submissions(user_submissions, date_range.days, completion_message)
        LOGGER.info(text_output)
    else:
        LOGGER.info(output)

    # Write to file
    presenter.write_to_file("report", output)
    LOGGER.info(f"Report has been written to file")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
