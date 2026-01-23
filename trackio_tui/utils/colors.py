"""Color palette and management for run visualization."""

from typing import List

# Color palette for run visualization
RUN_COLORS = [
    "blue",
    "red",
    "green",
    "yellow",
    "magenta",
    "cyan",
    "bright_blue",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_magenta",
    "bright_cyan",
]


class ColorManager:
    """Manages color assignment for runs."""

    def __init__(self):
        self._run_colors: dict[str, str] = {}
        self._color_index = 0

    def get_color(self, run_id: str) -> str:
        """Get color for a run, assigning a new one if needed."""
        if run_id not in self._run_colors:
            self._run_colors[run_id] = RUN_COLORS[self._color_index % len(RUN_COLORS)]
            self._color_index += 1
        return self._run_colors[run_id]

    def get_all_colors(self) -> dict[str, str]:
        """Get all assigned run colors."""
        return self._run_colors.copy()

    def reset(self):
        """Reset color assignments."""
        self._run_colors.clear()
        self._color_index = 0
