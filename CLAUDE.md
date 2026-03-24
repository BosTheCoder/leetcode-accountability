# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI tool that tracks LeetCode submissions across a group of users and charges them via Splitwise for missed weekly goals. Runs as a GitHub Actions cron job every Monday and daily for stats reports, emailing results to a Google Group.

## Commands

```bash
# Install dependencies (Python 3.12, uses venv)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Get stats for all active users (last 7 days)
python -m leetcode_accountability.cli stats --days 7

# Get stats for specific users
python -m leetcode_accountability.cli stats user1 user2 --days 7

# Get stats with date range
python -m leetcode_accountability.cli stats --start-date 2025-01-01T05:00:00 --end-date 2025-01-08T05:00:00

# Run weekly accountability (charges via Splitwise, requires SPLITWISE_API_KEY in .env)
python -m leetcode_accountability.cli accountability --days 7 --cost-per-question 10.0

# Output as HTML (used by GitHub Actions for email reports)
python -m leetcode_accountability.cli stats --days 1 --output-type html
```

## Architecture

The CLI (`cli.py`) has two commands: `stats` (read-only reporting) and `accountability` (charges users via Splitwise). Both share the same data pipeline:

1. **User loading**: `user_loader_service.py` reads `users_data.json` and filters by `is_active`
2. **Data fetching**: `leetcode_client.py` queries LeetCode's GraphQL API (submissions + question details)
3. **Processing**: `submission_service.py` filters by date range, deduplicates submissions (24h window), and builds `UserSubmissions` entities
4. **Accountability** (accountability command only): `accountability_service.py` compares submissions against `min_questions` goal and creates Splitwise expenses for shortfalls
5. **Output**: `presenters.py` formats results as text or HTML; reports written to `report.txt`/`report.html`

Key design points:
- `entities.py` defines the domain models: `User`, `Submission`, `UserSubmissions`, `Difficulty`
- The Splitwise integration splits missed-question costs: the user who missed owes the full amount, other group members are credited equally
- Currency is GBP
- The weekly cycle runs Monday 5 AM to Monday 5 AM (London time)

## Configuration

- **Users**: Add/remove/deactivate users in `leetcode_accountability/users_data.json` (set `is_active` to 0/1)
- **Environment**: `SPLITWISE_API_KEY` in `.env` (required only for `accountability` command)
- **GitHub Actions secrets**: `SPLITWISE_API_KEY`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`

## No Tests

There is no test suite in this project.
