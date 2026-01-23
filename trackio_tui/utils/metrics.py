"""Metric grouping and organization utilities."""

from typing import Dict, List


def group_metrics(metric_names: List[str]) -> Dict[str, List[str]]:
    """
    Group metrics by prefix (before first '/').

    Args:
        metric_names: List of metric names

    Returns:
        Dictionary mapping group names to lists of metric names
    """
    groups: Dict[str, List[str]] = {}

    for metric in metric_names:
        if '/' in metric:
            group = metric.split('/')[0]
        else:
            group = 'other'

        if group not in groups:
            groups[group] = []
        groups[group].append(metric)

    # Sort metrics within each group
    for group in groups:
        groups[group].sort()

    return groups


def filter_metrics(
    metric_names: List[str],
    filter_text: str
) -> List[str]:
    """
    Filter metrics by search text.

    Args:
        metric_names: List of metric names
        filter_text: Search string (case-insensitive)

    Returns:
        Filtered list of metric names
    """
    if not filter_text:
        return metric_names

    filter_lower = filter_text.lower()
    return [m for m in metric_names if filter_lower in m.lower()]
