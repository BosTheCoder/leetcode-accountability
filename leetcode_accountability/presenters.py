"""
Presenters for formatting and displaying LeetCode accountability data.
"""

import os
from typing import List, Optional

from .entities import UserSubmissions


class BasePresenter:
    """Base class for presenters."""

    def sort_user_stats(
        self, user_stats_list: List[UserSubmissions]
    ) -> List[UserSubmissions]:
        """
        Sort users by total questions in descending order.

        Args:
            user_stats_list: List of UserSubmissions objects to sort

        Returns:
            List[UserSubmissions]: Sorted list of UserSubmissions
        """
        return sorted(
            user_stats_list,
            key=lambda x: (
                x.total_questions,
                x.hard_count,
                x.medium_count,
                x.easy_count,
            ),
            reverse=True,
        )

    def get_summary_data(self, user_stats_list: List[UserSubmissions]) -> dict:
        """
        Get summary data for the user stats, including top performers and users with no submissions.

        Args:
            user_stats_list: List of UserSubmissions objects to analyze

        Returns:
            dict: Dictionary containing summary data
        """
        summary = {
            "top_hard": None,
            "top_hard_count": 0,
            "top_medium": None,
            "top_medium_count": 0,
            "top_easy": None,
            "top_easy_count": 0,
            "no_submissions": []
        }

        # Find top performers in each difficulty
        max_hard = 0
        max_medium = 0
        max_easy = 0

        for stats in user_stats_list:
            # Check for users with no submissions
            if stats.total_questions == 0:
                summary["no_submissions"].append(stats.username)

            # Check for top performers
            if stats.hard_count > max_hard:
                max_hard = stats.hard_count
                summary["top_hard"] = stats.username
                summary["top_hard_count"] = stats.hard_count

            if stats.medium_count > max_medium:
                max_medium = stats.medium_count
                summary["top_medium"] = stats.username
                summary["top_medium_count"] = stats.medium_count

            if stats.easy_count > max_easy:
                max_easy = stats.easy_count
                summary["top_easy"] = stats.username
                summary["top_easy_count"] = stats.easy_count

        return summary

    def present_submissions(
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

    def present_submissions(
        self,
        user_stats_list: List[UserSubmissions],
        days: int,
        completion_message: Optional[str] = None,
    ) -> str:
        """Format and present the statistics in plain text."""
        output = []

        # Sort users by total questions in descending order
        sorted_stats = self.sort_user_stats(user_stats_list)

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
                        f"  • {difficulty_emoji} {submission.name} [{submission_date}] - {submission.url}"
                    )
            else:
                output.append("  No submissions in this period.")

            output.append("-" * 80)

        # Add footer
        output.append("-" * 80)

        # Add summary section
        summary_data = self.get_summary_data(sorted_stats)

        output.append("\nSummary Achievements")
        output.append("-" * 80)

        if summary_data["top_hard"]:
            output.append(f"🔴 {summary_data['top_hard']} completed the most hard questions ({summary_data['top_hard_count']}), you're a boss!")

        if summary_data["top_medium"]:
            output.append(f"🟠 {summary_data['top_medium']} completed the most medium questions ({summary_data['top_medium_count']}), great work!")

        if summary_data["top_easy"]:
            output.append(f"🟢 {summary_data['top_easy']} completed the most easy questions ({summary_data['top_easy_count']}), keep going!")

        if summary_data["no_submissions"]:
            users_list = ", ".join(summary_data["no_submissions"])
            output.append(f"\nPlease everyone try to encourage {users_list} who didn't get any questions done 🥲")

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

    def present_submissions(
        self,
        user_stats_list: List[UserSubmissions],
        days: int,
        completion_message: Optional[str] = None,
    ) -> str:
        """Format and present the statistics in HTML."""
        html_parts = []

        # Sort users by total questions in descending order
        sorted_stats = self.sort_user_stats(user_stats_list)

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
                "        h2 { color: #555; margin-top: 30px; }",
                "        table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
                "        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }",
                "        th { background-color: #f2f2f2; }",
                "        tr:hover { background-color: #f5f5f5; }",
                "        .message { margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 5px solid #4285f4; }",
                "        .first-place { font-weight: bold; }",
                "        .medal { font-size: 1.2em; }",
                "        .user-row:hover { background-color: #f0f0f0; }",
                "        .submissions-table { width: 100%; margin: 10px 0; background-color: #f9f9f9; border: 1px solid #ddd; }",
                "        .submissions-table th { background-color: #eaeaea; }",
                "        .submissions-table td { padding: 8px 12px; }",
                "        .difficulty-easy { color: green; }",
                "        .difficulty-medium { color: orange; }",
                "        .difficulty-hard { color: red; }",
                "        .no-submissions { font-style: italic; color: #666; }",
                "        .user-submissions-section { margin-top: 40px; }",
                "        .user-submissions-header { background-color: #f2f2f2; padding: 10px; border-radius: 5px 5px 0 0; border: 1px solid #ddd; border-bottom: none; }",
                "        .summary-section { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }",
                "        .encouragement { margin-top: 15px; font-style: italic; }",
                "        .count { font-weight: bold; }",
                "    </style>",
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
            row_class = ""
            medal = ""

            if i == 0:
                row_class = "first-place"
                medal = ' <span class="medal">🥇</span>'
            elif i == 1:
                medal = ' <span class="medal">🥈</span>'
            elif i == 2:
                medal = ' <span class="medal">🥉</span>'

            html_parts.extend(
                [
                    f'    <tr class="{row_class}">',
                    f'        <td><a href="https://leetcode.com/u/{stats.username}/" target="_blank">{stats.username}</a>{medal}</td>',
                    f"        <td>{stats.total_questions}</td>",
                    f"        <td>{stats.easy_count}</td>",
                    f"        <td>{stats.medium_count}</td>",
                    f"        <td>{stats.hard_count}</td>",
                    "    </tr>",
                ]
            )

        # Close the table
        html_parts.append("</table>")

        # Add summary section
        summary_data = self.get_summary_data(sorted_stats)

        html_parts.append("<h2>Summary Achievements</h2>")
        html_parts.append("<div class='summary-section'>")

        if summary_data["top_hard"]:
            html_parts.append(f"<p><span class='difficulty-hard'>🔴</span> <strong>{summary_data['top_hard']}</strong> completed the most hard questions (<span class='count'>{summary_data['top_hard_count']}</span>), you're a boss!</p>")

        if summary_data["top_medium"]:
            html_parts.append(f"<p><span class='difficulty-medium'>🟠</span> <strong>{summary_data['top_medium']}</strong> completed the most medium questions (<span class='count'>{summary_data['top_medium_count']}</span>), great work!</p>")

        if summary_data["top_easy"]:
            html_parts.append(f"<p><span class='difficulty-easy'>🟢</span> <strong>{summary_data['top_easy']}</strong> completed the most easy questions (<span class='count'>{summary_data['top_easy_count']}</span>), keep going!</p>")

        if summary_data["no_submissions"]:
            users_list = ", ".join(summary_data["no_submissions"])
            html_parts.append(f"<p class='encouragement'>Please everyone try to encourage <strong>{users_list}</strong> who didn't get any questions done 🥲</p>")

        html_parts.append("</div>")

        # Add completion message if provided
        if completion_message:
            html_parts.append(f"<div class='message'>{completion_message}</div>")

        # Add detailed submissions section
        html_parts.append("<h2>Detailed User Submissions</h2>")

        for i, stats in enumerate(sorted_stats):
            # Create a section for each user's submissions
            html_parts.append(f"<div class='user-submissions-section'>")

            # Add user header with medal if applicable
            medal = ""
            if i == 0:
                medal = ' 🥇'
            elif i == 1:
                medal = ' 🥈'
            elif i == 2:
                medal = ' 🥉'

            html_parts.append(f"<div class='user-submissions-header'>")
            html_parts.append(f"<h3>{stats.username}{medal}'s Submissions</h3>")
            html_parts.append("</div>")

            # Add submissions table
            html_parts.append("<table class='submissions-table'>")
            html_parts.append("<tr>")
            html_parts.append("<th>Problem</th>")
            html_parts.append("<th>Difficulty</th>")
            html_parts.append("<th>Submission Time</th>")
            html_parts.append("</tr>")

            # Combine all submissions and sort by time
            all_submissions = []
            for submission in stats.easy_submissions:
                all_submissions.append(
                    (submission, "difficulty-easy", "🟢 Easy")
                )
            for submission in stats.medium_submissions:
                all_submissions.append(
                    (submission, "difficulty-medium", "🟠 Medium")
                )
            for submission in stats.hard_submissions:
                all_submissions.append(
                    (submission, "difficulty-hard", "🔴 Hard")
                )

            # Sort all submissions by time (most recent first)
            all_submissions.sort(key=lambda x: x[0].submission_time, reverse=True)

            # Display all submissions in chronological order with difficulty emoji
            if all_submissions:
                for submission, difficulty_class, difficulty_text in all_submissions:
                    submission_date = submission.submission_time.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    html_parts.append("<tr>")
                    html_parts.append(
                        f'<td><a href="{submission.url}" target="_blank">{submission.name}</a></td>'
                    )
                    html_parts.append(f'<td class="{difficulty_class}">{difficulty_text}</td>')
                    html_parts.append(f"<td>{submission_date}</td>")
                    html_parts.append("</tr>")
            else:
                html_parts.append(
                    '<tr><td colspan="3" class="no-submissions">No submissions in this period.</td></tr>'
                )

            html_parts.append("</table>")
            html_parts.append("</div>")

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
