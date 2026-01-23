"""Data smoothing algorithms for metric visualization."""

from typing import List, Tuple


def smooth_data(values: List[float], smoothing: float) -> List[float]:
    """
    Apply exponential moving average smoothing to data.

    Args:
        values: List of values to smooth
        smoothing: Smoothing factor (0-1), where 0 = no smoothing

    Returns:
        Smoothed values
    """
    if not values or smoothing == 0:
        return values

    # Convert smoothing from 0-20 scale to 0-1 scale
    alpha = min(1.0, smoothing / 20.0)

    smoothed = []
    last = values[0]
    for v in values:
        smoothed_val = last * alpha + v * (1 - alpha)
        smoothed.append(smoothed_val)
        last = smoothed_val
    return smoothed


def downsample_data(
    x_values: List[float],
    y_values: List[float],
    max_points: int = 1000
) -> Tuple[List[float], List[float]]:
    """
    Downsample data to a maximum number of points for display.

    Args:
        x_values: X-axis values
        y_values: Y-axis values
        max_points: Maximum number of points to keep

    Returns:
        Tuple of (downsampled_x, downsampled_y)
    """
    if len(x_values) <= max_points:
        return x_values, y_values

    # Simple downsampling: take every nth point
    step = len(x_values) // max_points
    return x_values[::step], y_values[::step]
