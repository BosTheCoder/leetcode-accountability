# LeetCode Accountability

A Python package for tracking LeetCode problem-solving activity across multiple users.

## Features

- Query the LeetCode GraphQL API to fetch user submissions
- Track problems solved by difficulty level (Easy, Medium, Hard)
- View statistics for multiple users over a specified time period
- Command-line interface for quick access to statistics

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install gql typer
```

## Usage

### Command-line Interface

```bash
# Get stats for multiple users over the last 30 days (default)
python -m leetcode_accountability.cli stats user1 user2 user3

# Specify a custom number of days
python -m leetcode_accountability.cli stats user1 user2 --days 7
```

### As a Library

```python
from leetcode_accountability.client.leetcode_client import LeetCodeGraphQLClient
from leetcode_accountability.services.submission_service import UserSubmissionsService

# Initialize the client and service
leetcode_client = LeetCodeGraphQLClient()
submissions_service = UserSubmissionsService(leetcode_client)

# Get user statistics
user_stats = submissions_service.get_user_stats("username", days=30)
print(f"Total problems: {user_stats.total_questions}")
print(f"Easy: {user_stats.easy_count}")
print(f"Medium: {user_stats.medium_count}")
print(f"Hard: {user_stats.hard_count}")
```

## Project Structure

```
leetcode_accountability/
├── __init__.py                  # Makes the directory a package
├── cli.py                       # Command-line interface using Typer
├── client/
│   ├── __init__.py
│   └── leetcode_client.py       # GraphQL client for LeetCode API
├── models/
│   ├── __init__.py
│   └── entities.py              # Core data models/entities
├── services/
│   ├── __init__.py
│   └── submission_service.py    # Business logic for submissions
└── README.md                    # Project documentation
```

## License

MIT
