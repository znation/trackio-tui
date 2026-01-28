"""Metric plot widget using PlotextPlot."""

from typing import Dict, List, Any
import math
from datetime import datetime

from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Vertical
from textual_plotext import PlotextPlot

from ..utils.smoothing import smooth_data, downsample_data
from ..utils.formatting import format_number
from ..data.state import ChartConfig


class MetricPlot(Vertical):
    """Widget for displaying a single metric plot."""

    DEFAULT_CSS = """
    MetricPlot {
        width: 1fr;
        height: auto;
        min-height: 15;
        border: solid $accent;
        padding: 1;
        margin: 1;
    }

    MetricPlot Label {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }

    MetricPlot PlotextPlot {
        width: 100%;
        height: 12;
    }
    """

    def __init__(
        self,
        metric_name: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.metric_name = metric_name
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._colors: Dict[str, str] = {}
        self._config = ChartConfig()

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label(f"[b]{self.metric_name}[/b]")
        yield PlotextPlot()

    def on_mount(self) -> None:
        """Update plot when widget is mounted."""
        if self._data:
            self._update_plot()

    def set_data(
        self,
        run_data: Dict[str, List[Dict[str, Any]]],
        colors: Dict[str, str],
        config: ChartConfig
    ):
        """
        Set plot data and update display.

        Args:
            run_data: Dict mapping run_id to list of data points
                      Each data point has: step, value, timestamp
            colors: Dict mapping run_id to color name
            config: Chart configuration
        """
        self._data = run_data
        self._colors = colors
        self._config = config
        # Only update if already mounted, otherwise on_mount will handle it
        if self.is_mounted:
            self._update_plot()

    def _update_plot(self):
        """Update the plot with current data and configuration."""
        # Check if widget is mounted and has PlotextPlot child
        if not self.is_mounted:
            return

        try:
            plt = self.query_one(PlotextPlot).plt
        except Exception:
            # Widget may have been removed from DOM
            return

        # Clear previous plot
        plt.clear_data()
        plt.clear_color()

        if not self._data:
            plt.title(f"{self.metric_name} (no data)")
            return

        # Plot each run
        for run_id, data_points in self._data.items():
            if not data_points:
                continue

            # Extract x and y values based on x-axis setting
            x_values, y_values = self._extract_values(data_points)

            if not x_values or not y_values:
                continue

            # Apply smoothing
            if self._config.smoothing > 0:
                y_values = smooth_data(y_values, self._config.smoothing)

            # Downsample if too many points
            x_values, y_values = downsample_data(x_values, y_values)

            # Get color for this run
            color = self._colors.get(run_id, "white")

            # Plot the line
            plt.plot(x_values, y_values, label=run_id, color=color)

        # Configure axes
        x_label = self._get_x_label()
        plt.xlabel(x_label)

        # Apply log scales if configured
        if self._config.log_scale_x:
            plt.xscale("log")
        if self._config.log_scale_y:
            plt.yscale("log")

        # Refresh the plot widget
        self.query_one(PlotextPlot).refresh()

    def _parse_timestamp(self, timestamp) -> float:
        """Parse timestamp to float (seconds since epoch)."""
        if isinstance(timestamp, (int, float)):
            return float(timestamp)
        elif isinstance(timestamp, str):
            # Parse ISO 8601 timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.timestamp()
            except (ValueError, AttributeError):
                return 0.0
        return 0.0

    def _extract_values(
        self,
        data_points: List[Dict[str, Any]]
    ) -> tuple[List[float], List[float]]:
        """Extract x and y values based on x-axis configuration."""
        if not data_points:
            return [], []

        # Filter data points to only include numeric values
        filtered_points = []
        for p in data_points:
            value = p.get("value", 0)
            # Skip non-numeric values (like tables, images, etc.)
            if isinstance(value, dict):
                continue
            try:
                float(value)
                filtered_points.append(p)
            except (TypeError, ValueError):
                continue

        if not filtered_points:
            return [], []

        y_values = [float(p.get("value", 0)) for p in filtered_points]

        if self._config.x_axis == "step":
            x_values = [float(p.get("step", 0)) for p in filtered_points]
        elif self._config.x_axis == "relative":
            # Relative time from first point
            first_ts = self._parse_timestamp(filtered_points[0].get("timestamp", 0))
            x_values = [
                self._parse_timestamp(p.get("timestamp", 0)) - first_ts
                for p in filtered_points
            ]
        else:  # wall time
            x_values = [self._parse_timestamp(p.get("timestamp", 0)) for p in filtered_points]

        return x_values, y_values

    def _get_x_label(self) -> str:
        """Get label for x-axis based on configuration."""
        if self._config.x_axis == "step":
            return "Step"
        elif self._config.x_axis == "relative":
            return "Time (s)"
        else:
            return "Wall Time"

    def update_config(self, config: ChartConfig):
        """Update chart configuration and refresh plot."""
        self._config = config
        self._update_plot()
