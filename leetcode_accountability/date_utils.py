from typing import Optional
import typer
from datetime import datetime

def parse_optional_datetime(value: str | None) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, str) and value.lower() in ("none", "null", ""):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise typer.BadParameter(f"Invalid datetime format: {value}")


def parse_optional_int(value: str | None) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, str) and value.lower() in ("none", "null", ""):
        return None
    try:
        return int(value)
    except ValueError:
        raise typer.BadParameter(f"Invalid integer value: {value}")
