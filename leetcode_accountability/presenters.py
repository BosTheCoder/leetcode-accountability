"""
Presenters for formatting and displaying LeetCode accountability data.
"""

import os
from typing import List, Optional

from .entities import UserSubmissions


class BasePresenter:
    """Base class for presenters."""

    def present_stats(
        self,
        user_stats_list: List[UserSubmissions],
        days: int,
        completion_message: Optional[str] = None,
    ) -> str:
        """
        Format and present the statistics for a list of users.

        Args:
            user_stats_list: List of UserSubmissions objects to present
            days: Number of days the stats cover
            completion_message: Optional message to display after the stats

        Returns:
            str: The formatted output
        """
        raise NotImplementedError("Subclasses must implement this method")

    def write_to_file(self, filename: str, content: str) -> None:
        """
        Write content to a file with the appropriate extension.

        Args:
            filename: Base filename without extension
            content: Content to write to the file
        """
        raise NotImplementedError("Subclasses must implement this method")


class TextPresenter(BasePresenter):
    """Presenter for plain text output."""

    def write_to_file(self, filename: str, content: str) -> None:
        """Write content to a text file."""
        # Ensure filename has .txt extension
        if not filename.endswith(".txt"):
            filename = f"{filename}.txt"

        with open(filename, "w") as f:
            f.write(content)

    def present_stats(
        self,
        user_stats_list: List[UserSubmissions],
        days: int,
        completion_message: Optional[str] = None,
    ) -> str:
        """Format and present the statistics in plain text."""
        output = []

        # Sort users by total questions in descending order
        sorted_stats = sorted(
            user_stats_list, key=lambda x: x.total_questions, reverse=True
        )

        # Add detailed submissions section
        output.append("\nDetailed Submissions by User")
        output.append("=" * 80)

        for stats in sorted_stats:
            output.append(f"\n{stats.username}'s Submissions:")
            output.append("-" * 80)

            # Combine all submissions and sort by time
            all_submissions = []
            for submission in stats.easy_submissions:
                all_submissions.append((submission, "🟢"))  # Green for Easy
            for submission in stats.medium_submissions:
                all_submissions.append((submission, "🟠"))  # Orange for Medium
            for submission in stats.hard_submissions:
                all_submissions.append((submission, "🔴"))  # Red for Hard

            # Sort all submissions by time (most recent first)
            all_submissions.sort(key=lambda x: x[0].submission_time, reverse=True)

            # Display all submissions in chronological order with difficulty emoji
            if all_submissions:
                for submission, difficulty_emoji in all_submissions:
                    submission_date = submission.submission_time.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    output.append(
                        f"  • {difficulty_emoji} {submission.name} [{submission_date}]"
                    )
            else:
                output.append("  No submissions in this period.")

            output.append("-" * 80)

        # Add footer
        output.append("-" * 80)

        # Add Footer
        output.append(f"\nLeetCode Statistics (Last {days} Days)")
        output.append("-" * 80)
        output.append(
            f"{'Username':<25} {'Total Questions':<15} {'Easy':<10} {'Medium':<10} {'Hard':<10}"
        )
        output.append("-" * 80)

        # Add rows for each user with medals for top 3
        for i, stats in enumerate(sorted_stats):
            username_display = stats.username
            if i == 0:
                username_display = f"{stats.username} 🥇"
            elif i == 1:
                username_display = f"{stats.username} 🥈"
            elif i == 2:
                username_display = f"{stats.username} 🥉"

            output.append(
                f"{username_display:<25} {stats.total_questions:<15} {stats.easy_count:<10} {stats.medium_count:<10} {stats.hard_count:<10}"
            )

        # Add completion message if provided
        if completion_message:
            output.append(completion_message)

        return "\n".join(output)


class HtmlPresenter(BasePresenter):
    """Presenter for HTML output."""

    def write_to_file(self, filename: str, content: str) -> None:
        """Write content to an HTML file."""
        # Ensure filename has .html extension
        if not filename.endswith(".html"):
            filename = f"{filename}.html"

        with open(filename, "w") as f:
            f.write(content)

    def present_stats(
        self,
        user_stats_list: List[UserSubmissions],
        days: int,
        completion_message: Optional[str] = None,
    ) -> str:
        """Format and present the statistics in HTML."""
        html_parts = []

        # Sort users by total questions in descending order
        sorted_stats = sorted(
            user_stats_list, key=lambda x: x.total_questions, reverse=True
        )

        # Add HTML header
        html_parts.extend(
            [
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
                "        .first-place { font-weight: bold; }",
                "        .medal { font-size: 1.2em; }",
                "        .user-row { cursor: pointer; }",
                "        .user-row:hover { background-color: #f0f0f0; }",
                "        .submissions-container { display: none; }",
                "        .submissions-table { width: 100%; margin: 0; background-color: #f9f9f9; }",
                "        .submissions-table td { padding: 8px 12px; }",
                "        .difficulty-easy { color: green; }",
                "        .difficulty-medium { color: orange; }",
                "        .difficulty-hard { color: red; }",
                "        .no-submissions { font-style: italic; color: #666; }",
                "        .chevron::after { content: '▼'; font-size: 0.8em; margin-left: 5px; }",
                "        .collapsed::after { content: '▶'; }",
                "    </style>",
                "    <script>",
                "        function toggleSubmissions(userId) {",
                "            const submissionsContainer = document.getElementById('submissions-' + userId);",
                "            const chevron = document.getElementById('chevron-' + userId);",
                "            if (submissionsContainer.style.display === 'none' || !submissionsContainer.style.display) {",
                "                submissionsContainer.style.display = 'table-row';",
                "                chevron.classList.remove('collapsed');",
                "            } else {",
                "                submissionsContainer.style.display = 'none';",
                "                chevron.classList.add('collapsed');",
                "            }",
                "        }",
                "    </script>",
                "</head>",
                "<body>",
            ]
        )

        # Add stats header
        html_parts.extend(
            [
                f"<h1>LeetCode Statistics (Last {days} Days)</h1>",
                "<table>",
                "    <tr>",
                "        <th>Username</th>",
                "        <th>Total Questions</th>",
                "        <th>Easy</th>",
                "        <th>Medium</th>",
                "        <th>Hard</th>",
                "    </tr>",
            ]
        )

        # Add rows for each user with medals for top 3
        for i, stats in enumerate(sorted_stats):
            username_display = stats.username
            row_class = "user-row"
            medal = ""

            if i == 0:
                row_class = 'user-row first-place'
                medal = ' <span class="medal">🥇</span>'
            elif i == 1:
                medal = ' <span class="medal">🥈</span>'
            elif i == 2:
                medal = ' <span class="medal">🥉</span>'

            # Create a unique ID for this user
            user_id = f"user-{i}"

            html_parts.extend(
                [
                    f'    <tr class="{row_class}" onclick="toggleSubmissions(\'{user_id}\')">',
                    f'        <td><span id="chevron-{user_id}" class="chevron collapsed"></span><a href="https://leetcode.com/u/{stats.username}/" target="_blank">{stats.username}</a>{medal}</td>',
                    f"        <td>{stats.total_questions}</td>",
                    f"        <td>{stats.easy_count}</td>",
                    f"        <td>{stats.medium_count}</td>",
                    f"        <td>{stats.hard_count}</td>",
                    "    </tr>",
                ]
            )

            # Add submissions details row (initially hidden)
            html_parts.append(f'    <tr id="submissions-{user_id}" class="submissions-container">')
            html_parts.append('        <td colspan="5">')
            html_parts.append('            <table class="submissions-table">')

            # Combine all submissions and sort by time
            all_submissions = []
            for submission in stats.easy_submissions:
                all_submissions.append((submission, "difficulty-easy", "🟢"))  # Green for Easy
            for submission in stats.medium_submissions:
                all_submissions.append((submission, "difficulty-medium", "🟠"))  # Orange for Medium
            for submission in stats.hard_submissions:
                all_submissions.append((submission, "difficulty-hard", "🔴"))  # Red for Hard

            # Sort all submissions by time (most recent first)
            all_submissions.sort(key=lambda x: x[0].submission_time, reverse=True)

            # Display all submissions in chronological order with difficulty emoji
            if all_submissions:
                for submission, difficulty_class, difficulty_emoji in all_submissions:
                    submission_date = submission.submission_time.strftime("%Y-%m-%d %H:%M")
                    html_parts.append(f'                <tr>')
                    html_parts.append(f'                    <td><span class="{difficulty_class}">{difficulty_emoji} {submission.name}</span> [{submission_date}]</td>')
                    html_parts.append(f'                </tr>')
            else:
                html_parts.append('                <tr><td class="no-submissions">No submissions in this period.</td></tr>')

            html_parts.append('            </table>')
            html_parts.append('        </td>')
            html_parts.append('    </tr>')

        # Close the table
        html_parts.append("</table>")

        # Add completion message if provided
        if completion_message:
            html_parts.append(f"<div class='message'>{completion_message}</div>")

        # Add HTML footer
        html_parts.extend(["</body>", "</html>"])

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
