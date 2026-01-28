"""Formatting utilities for display."""

from datetime import datetime
from typing import Any
import json


def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to human-readable string."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


def format_number(value: float, precision: int = 4) -> str:
    """Format number with appropriate precision."""
    if abs(value) < 0.01 or abs(value) > 10000:
        return f"{value:.{precision}e}"
    else:
        return f"{value:.{precision}f}".rstrip('0').rstrip('.')


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as pretty JSON string."""
    return json.dumps(data, indent=indent, default=str)


def truncate_string(s: str, max_length: int = 50) -> str:
    """Truncate string with ellipsis if too long."""
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."
