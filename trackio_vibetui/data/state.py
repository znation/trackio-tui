"""Application state management."""

from typing import List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class ChartConfig:
    """Configuration for chart display."""
    x_axis: str = "step"  # "step", "relative", or "wall"
    smoothing: float = 0.0  # 0-20
    log_scale_x: bool = False
    log_scale_y: bool = False


@dataclass
class AppState:
    """Centralized application state."""

    # Current selections
    current_project: Optional[str] = None
    selected_runs: Set[str] = field(default_factory=set)
    current_run: Optional[str] = None  # For single-run views

    # Filters
    run_filter: str = ""
    metric_filter: str = ""

    # Chart configuration
    chart_config: ChartConfig = field(default_factory=ChartConfig)

    # UI state
    auto_refresh_enabled: bool = False
    sidebar_visible: bool = True

    # Media/Tables state
    current_step: int = 0
    current_media_type: str = "images"  # images, videos, audio, tables

    def toggle_run(self, run_id: str):
        """Toggle run selection."""
        if run_id in self.selected_runs:
            self.selected_runs.remove(run_id)
        else:
            self.selected_runs.add(run_id)

    def clear_run_selection(self):
        """Clear all selected runs."""
        self.selected_runs.clear()

    def set_project(self, project: str):
        """Set current project and reset related state."""
        if self.current_project != project:
            self.current_project = project
            self.clear_run_selection()
            self.current_run = None
            self.run_filter = ""
            self.metric_filter = ""
            self.current_step = 0
