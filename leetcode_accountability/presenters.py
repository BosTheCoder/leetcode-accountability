"""
Presenters for formatting and displaying LeetCode accountability data.
"""

from typing import List, Optional
from .entities import UserStats


class BasePresenter:
    """Base class for presenters."""

    def present_stats(self, user_stats_list: List[UserStats], days: int, completion_message: Optional[str] = None) -> str:
        """
        Format and present the statistics for a list of users.

        Args:
            user_stats_list: List of UserStats objects to present
            days: Number of days the stats cover
            completion_message: Optional message to display after the stats

        Returns:
            str: The formatted output
        """
        raise NotImplementedError("Subclasses must implement this method")


class TextPresenter(BasePresenter):
    """Presenter for plain text output."""

    def present_stats(self, user_stats_list: List[UserStats], days: int, completion_message: Optional[str] = None) -> str:
        """Format and present the statistics in plain text."""
        output = []

        # Add header
        output.append(f"\nLeetCode Statistics (Last {days} Days)")
        output.append("-" * 80)
        output.append(f"{'Username':<20} {'Total Questions':<15} {'Easy':<10} {'Medium':<10} {'Hard':<10}")
        output.append("-" * 80)

        # Add rows for each user
        for stats in user_stats_list:
            output.append(f"{stats.username:<20} {stats.total_questions:<15} {stats.easy_count:<10} {stats.medium_count:<10} {stats.hard_count:<10}")

        # Add footer
        output.append("-" * 80)

        # Add completion message if provided
        if completion_message:
            output.append(completion_message)

        return "\n".join(output)


class HtmlPresenter(BasePresenter):
    """Presenter for HTML output."""

    def present_stats(self, user_stats_list: List[UserStats], days: int, completion_message: Optional[str] = None) -> str:
        """Format and present the statistics in HTML."""
        html_parts = []

        # Add HTML header
        html_parts.extend([
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "    <title>LeetCode Accountability Report</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 20px; }",
            "        h1 { color: #333; }",
            "        table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
            "        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }",
            "        th { background-color: #f2f2f2; }",
            "        tr:hover { background-color: #f5f5f5; }",
            "        .message { margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 5px solid #4285f4; }",
            "    </style>",
            "</head>",
            "<body>"
        ])

        # Add stats header
        html_parts.extend([
            f"<h1>LeetCode Statistics (Last {days} Days)</h1>",
            "<table>",
            "    <tr>",
            "        <th>Username</th>",
            "        <th>Total Questions</th>",
            "        <th>Easy</th>",
            "        <th>Medium</th>",
            "        <th>Hard</th>",
            "    </tr>"
        ])

        # Add rows for each user
        for stats in user_stats_list:
            html_parts.extend([
                "    <tr>",
                f"        <td><a href=\"https://leetcode.com/u/{stats.username}/\" target=\"_blank\">{stats.username}</a></td>",
                f"        <td>{stats.total_questions}</td>",
                f"        <td>{stats.easy_count}</td>",
                f"        <td>{stats.medium_count}</td>",
                f"        <td>{stats.hard_count}</td>",
                "    </tr>"
            ])

        # Close the table
        html_parts.append("</table>")

        # Add completion message if provided
        if completion_message:
            html_parts.append(f"<div class='message'>{completion_message}</div>")

        # Add HTML footer
        html_parts.extend([
            "</body>",
            "</html>"
        ])

        return "\n".join(html_parts)


def get_presenter(output_type: str = "text") -> BasePresenter:
    """
    Factory function to get the appropriate presenter based on output type.

    Args:
        output_type (str): The type of output format ('text' or 'html').

    Returns:
        BasePresenter: An instance of the appropriate presenter.
    """
    if output_type.lower() == "html":
        return HtmlPresenter()
    return TextPresenter()
