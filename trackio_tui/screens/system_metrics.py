"""System metrics screen - displays system resource metrics."""

from typing import Dict, List, Any
from collections import defaultdict

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, LoadingIndicator, DataTable
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import on, work

from ..widgets.sidebar import Sidebar, ProjectChanged
from ..widgets.run_selector import RunSelectionChanged
from ..widgets.control_panel import ChartConfigChanged
from ..widgets.metric_plot import MetricPlot
from ..widgets.header import Header
from ..data.loader import TrackioDataLoader
from ..data.state import AppState


class SystemMetricsScreen(Screen):
    """Screen for displaying system resource metrics."""

    CSS = """
    SystemMetricsScreen {
        layout: grid;
        grid-size: 1 1;
    }

    #main-content {
        width: 1fr;
        height: 100%;
        padding: 1;
    }

    .metrics-container {
        width: 100%;
        height: 100%;
    }

    LoadingIndicator {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #no-data {
        width: 100%;
        height: 100%;
        align: center middle;
        text-align: center;
    }

    .metric-group-label {
        margin-top: 1;
        margin-bottom: 1;
    }

    DataTable {
        height: auto;
        max-height: 15;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        data_loader: TrackioDataLoader,
        app_state: AppState,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._loader = data_loader
        self._state = app_state
        self._metric_plots: Dict[str, MetricPlot] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header("System Metrics")
        yield Sidebar(id="sidebar")

        with Vertical(id="main-content"):
            yield Label("Select a project and runs to view system metrics", id="no-data")

    def on_mount(self) -> None:
        """Initialize screen on mount."""
        self._load_projects()

    @work(exclusive=True)
    async def _load_projects(self) -> None:
        """Load available projects."""
        projects = await self._loader.get_projects()

        sidebar = self.query_one("#sidebar", Sidebar)

        if projects:
            # Update projects
            sidebar.update_projects(projects, projects[0] if projects else None)
            # Manually set state and load runs for initial project
            self._state.set_project(projects[0])
            self._load_runs()

    @on(ProjectChanged)
    def on_project_changed(self, event: ProjectChanged) -> None:
        """Handle project selection change."""
        self._state.set_project(event.project)
        self._load_runs()

    @work(exclusive=True)
    async def _load_runs(self) -> None:
        """Load runs for current project."""
        if not self._state.current_project:
            return

        runs = await self._loader.get_runs(self._state.current_project)

        # Select all runs by default
        self._state.selected_runs = set(runs)

        sidebar = self.query_one("#sidebar", Sidebar)
        run_selector = sidebar.get_run_selector()
        run_selector.update_runs(runs, self._state.selected_runs)

        # Trigger metrics update with all runs selected
        self._update_system_metrics()

    @on(RunSelectionChanged)
    def on_run_selection_changed(self, event: RunSelectionChanged) -> None:
        """Handle run selection change."""
        self._state.selected_runs = event.selected_runs
        self._update_system_metrics()

    @on(ChartConfigChanged)
    def on_chart_config_changed(self, event: ChartConfigChanged) -> None:
        """Handle chart configuration change."""
        self._state.chart_config = event.config
        self._update_plots_config()

    @work(exclusive=True)
    async def _update_system_metrics(self) -> None:
        """Update system metrics display based on selected runs."""
        if not self._state.current_project or not self._state.selected_runs:
            self._clear_metrics()
            return

        # Show loading
        main_content = self.query_one("#main-content", Vertical)
        main_content.remove_children()

        loading = LoadingIndicator()
        main_content.mount(loading)

        # Collect system logs for all selected runs
        all_system_data = {}
        for run_id in self._state.selected_runs:
            try:
                logs = await self._loader.get_system_logs(
                    self._state.current_project,
                    run_id
                )
                if logs:
                    all_system_data[run_id] = logs
            except Exception as e:
                # Skip runs without system logs
                pass

        # Remove loading indicator
        loading.remove()

        if not all_system_data:
            main_content.mount(
                Label("No system metrics available for selected runs", id="no-data")
            )
            return

        # Process and display system metrics
        self._display_system_metrics(all_system_data)

    def _display_system_metrics(self, all_system_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Display system metrics as plots."""
        main_content = self.query_one("#main-content", Vertical)

        # Get color manager
        sidebar = self.query_one("#sidebar", Sidebar)
        run_selector = sidebar.get_run_selector()
        color_manager = run_selector.get_color_manager()

        # Extract all unique metric keys from system logs
        all_metric_keys = set()
        for run_id, logs in all_system_data.items():
            for log in logs:
                # Skip timestamp and other metadata fields
                for key in log.keys():
                    if key not in ['timestamp', 'step', 'wall_time']:
                        all_metric_keys.add(key)

        if not all_metric_keys:
            main_content.mount(
                Label("No system metrics found in logs", id="no-data")
            )
            return

        # Create scrollable container for plots
        metrics_scroll = VerticalScroll(classes="metrics-container")
        main_content.mount(metrics_scroll)

        # Group metrics by category
        metric_groups = self._group_system_metrics(all_metric_keys)

        # Create plots for each metric
        for group_name in sorted(metric_groups.keys()):
            metrics_in_group = sorted(metric_groups[group_name])

            # Add group label
            metrics_scroll.mount(
                Label(f"[b][u]{group_name.upper()}[/u][/b]", classes="metric-group-label")
            )

            # Add plots for metrics in group
            for metric_name in metrics_in_group:
                # Prepare data for this metric
                run_data = {}

                for run_id, logs in all_system_data.items():
                    # Extract time series data for this metric
                    data_points = []
                    for log in logs:
                        if metric_name in log:
                            point = {
                                'step': log.get('step', 0),
                                'value': log.get(metric_name),
                                'timestamp': log.get('timestamp', 0),
                            }
                            # Convert wall_time if available
                            if 'wall_time' in log:
                                point['wall_time'] = log['wall_time']
                            data_points.append(point)

                    if data_points:
                        run_data[run_id] = data_points

                if run_data:
                    # Get colors for runs
                    colors = {
                        run_id: color_manager.get_color(run_id)
                        for run_id in run_data.keys()
                    }

                    # Create and mount plot
                    plot = MetricPlot(metric_name)
                    self._metric_plots[metric_name] = plot
                    metrics_scroll.mount(plot)

                    # Set data
                    plot.set_data(run_data, colors, self._state.chart_config)

    def _group_system_metrics(self, metric_keys: set) -> Dict[str, List[str]]:
        """Group system metrics by category."""
        groups = defaultdict(list)

        for key in metric_keys:
            key_lower = key.lower()

            # Categorize based on metric name
            if any(x in key_lower for x in ['cpu', 'processor']):
                groups['CPU'].append(key)
            elif any(x in key_lower for x in ['memory', 'ram', 'mem']):
                groups['Memory'].append(key)
            elif any(x in key_lower for x in ['gpu', 'cuda', 'nvidia']):
                groups['GPU'].append(key)
            elif any(x in key_lower for x in ['disk', 'io', 'storage']):
                groups['Disk'].append(key)
            elif any(x in key_lower for x in ['network', 'net', 'bandwidth']):
                groups['Network'].append(key)
            elif any(x in key_lower for x in ['temp', 'temperature']):
                groups['Temperature'].append(key)
            else:
                groups['Other'].append(key)

        # Remove empty groups
        return {k: v for k, v in groups.items() if v}

    def _update_plots_config(self) -> None:
        """Update configuration for all plots."""
        for plot in self._metric_plots.values():
            plot.update_config(self._state.chart_config)

    def _clear_metrics(self) -> None:
        """Clear all metric plots."""
        self._metric_plots.clear()
        main_content = self.query_one("#main-content", Vertical)
        main_content.remove_children()
        main_content.mount(
            Label("Select runs to view system metrics", id="no-data")
        )
