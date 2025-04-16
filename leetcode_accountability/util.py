"""
Utility functions for the LeetCode accountability system.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from leetcode_accountability.entities import User


def load_users() -> Dict[str, User]:
    """
    Load user data from the JSON file and convert it to User objects.

    Returns:
        Dict[str, User]: A dictionary of User objects with name as the key.
    """
    json_path = Path(__file__).parent / "users_data.json"

    with open(json_path, "r") as f:
        users_data = json.load(f)

    users = {}
    for name, data in users_data.items():
        # Convert is_active from int to bool
        is_active = bool(data["is_active"])

        user = User(
            name=data["name"],
            leetcode_id=data["leetcode_id"],
            splitwise_id=int(data["splitwise_id"]) if "splitwise_id" in data else None,
            splitwise_group_id=int(data["splitwise_group_id"]) if "splitwise_group_id" in data else None,
            email_address=data["email_address"] if "email_address" in data else None,
            min_questions=int(data["min_questions"]),
            is_active=is_active
        )
        users[name] = user

    return users


def get_active_users() -> List[User]:
    """
    Get a list of all active users.

    Returns:
        List[User]: A list of active User objects.
    """
    users = load_users()
    return [user for user in users.values() if user.is_active]


def get_user_by_name(name: str) -> Optional[User]:
    """
    Get a user by their name.

    Args:
        name (str): The name of the user to retrieve.

    Returns:
        Optional[User]: The User object if found, None otherwise.
    """
    users = load_users()
    return users.get(name)
