"""
LeetCode GraphQL client for interacting with the LeetCode API.
"""

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from typing import List, Dict, Any


class LeetCodeGraphQLClient:
    """
    A client for interacting with LeetCode's GraphQL API using the gql library.
    """

    def __init__(self, base_url: str = "https://leetcode.com/graphql"):
        """
        Initialize the LeetCode GraphQL client.

        Args:
            base_url: The base URL for the LeetCode GraphQL API.
        """
        # Set up transport with proper headers
        transport = RequestsHTTPTransport(
            url=base_url,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            use_json=True,
        )

        # Initialize the gql client
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=False,
        )

    def get_recent_accepted_submissions(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent accepted submissions for a user.

        Args:
            username: The LeetCode username.
            limit: Maximum number of submissions to retrieve.

        Returns:
            A list of submission dictionaries.
        """
        # Define the query within the function
        query = gql("""
        query getRecentAcceptedSubmissions($username: String!, $limit: Int!) {
          recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
          }
        }
        """)

        variables = {
            "username": username,
            "limit": limit
        }

        result = self.client.execute(query, variable_values=variables)
        return result["recentAcSubmissionList"]

    def get_question_detail(self, title_slug: str) -> Dict[str, Any]:
        """
        Get details for a specific question.

        Args:
            title_slug: The title slug of the question.

        Returns:
            Question details as a dictionary.
        """
        # Define the query within the function
        query = gql("""
        query getQuestionDetail($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            difficulty
          }
        }
        """)

        variables = {
            "titleSlug": title_slug
        }

        result = self.client.execute(query, variable_values=variables)
        return result["question"]
