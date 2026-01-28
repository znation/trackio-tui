"""Metrics screen - primary view for metric visualization."""

from typing import Dict, List, Any

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, LoadingIndicator
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import on, work

from ..widgets.sidebar import Sidebar, ProjectChanged, MetricFilterChanged
from ..widgets.run_selector import RunSelectionChanged
from ..widgets.control_panel import ChartConfigChanged
from ..widgets.metric_plot import MetricPlot
from ..widgets.header import Header
from ..data.loader import TrackioDataLoader
from ..data.state import AppState
from ..utils.metrics import group_metrics, filter_metrics


class MetricsScreen(Screen):
    """Screen for displaying metrics with charts."""

    CSS = """
    MetricsScreen {
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
        yield Header("Metrics")
        yield Sidebar(id="sidebar")

        with Vertical(id="main-content"):
            yield Label("Select a project and runs to view metrics", id="no-data")

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
            # (Select widget initial value doesn't trigger Changed event)
            self._state.set_project(projects[0])
            self._load_runs()
        else:
            # Show message if no projects
            pass

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

        # Select all runs by default (like web dashboard)
        self._state.selected_runs = set(runs)

        sidebar = self.query_one("#sidebar", Sidebar)
        run_selector = sidebar.get_run_selector()
        run_selector.update_runs(runs, self._state.selected_runs)

        # Trigger metrics update with all runs selected
        self._update_metrics()

    @on(RunSelectionChanged)
    def on_run_selection_changed(self, event: RunSelectionChanged) -> None:
        """Handle run selection change."""
        self._state.selected_runs = event.selected_runs
        self._update_metrics()

    @on(ChartConfigChanged)
    def on_chart_config_changed(self, event: ChartConfigChanged) -> None:
        """Handle chart configuration change."""
        self._state.chart_config = event.config
        self._update_plots_config()

    @on(MetricFilterChanged)
    def on_metric_filter_changed(self, event: MetricFilterChanged) -> None:
        """Handle metric filter change."""
        self._state.metric_filter = event.filter_text
        self._update_metrics()

    @work(exclusive=True)
    async def _update_metrics(self) -> None:
        """Update metrics display based on selected runs."""
        if not self._state.current_project or not self._state.selected_runs:
            # Clear metrics and show message
            self._clear_metrics()
            return

        # Show loading
        main_content = self.query_one("#main-content", Vertical)
        main_content.remove_children()

        loading = LoadingIndicator()
        main_content.mount(loading)

        # Collect all metrics from selected runs
        all_metrics = set()
        for run_id in self._state.selected_runs:
            metrics = await self._loader.get_all_metrics_for_run(
                self._state.current_project,
                run_id
            )
            all_metrics.update(metrics)

        # Filter metrics
        filtered_metrics = filter_metrics(
            sorted(all_metrics),
            self._state.metric_filter
        )

        # Group metrics
        grouped_metrics = group_metrics(filtered_metrics)

        # Remove loading indicator
        loading.remove()

        # Create plots
        if not filtered_metrics:
            main_content.mount(
                Label("No metrics match the filter", id="no-data")
            )
            return

        # Create scrollable container for plots
        async with main_content.batch():
            metrics_scroll = VerticalScroll(classes="metrics-container")
            main_content.mount(metrics_scroll)

            # Create plots for each metric
            for group_name in sorted(grouped_metrics.keys()):
                metrics_in_group = grouped_metrics[group_name]

                # Add group label
                metrics_scroll.mount(
                    Label(f"[b][u]{group_name.upper()}[/u][/b]")
                )

                # Add plots for metrics in group
                for metric_name in metrics_in_group:
                    plot = MetricPlot(metric_name)
                    self._metric_plots[metric_name] = plot
                    metrics_scroll.mount(plot)

        # Load data for all plots
        self._load_plot_data()

    @work(exclusive=True)
    async def _load_plot_data(self) -> None:
        """Load data for all metric plots."""
        if not self._state.current_project or not self._state.selected_runs:
            return

        # Get color manager from run selector
        sidebar = self.query_one("#sidebar", Sidebar)
        run_selector = sidebar.get_run_selector()
        color_manager = run_selector.get_color_manager()

        # Load data for each metric
        for metric_name, plot in self._metric_plots.items():
            run_data = {}

            for run_id in self._state.selected_runs:
                try:
                    data = await self._loader.get_metric_values(
                        self._state.current_project,
                        run_id,
                        metric_name
                    )
                    if data:
                        run_data[run_id] = data
                except Exception as e:
                    # Skip runs that don't have this metric
                    pass

            # Get colors for runs
            colors = {
                run_id: color_manager.get_color(run_id)
                for run_id in run_data.keys()
            }

            # Update plot
            plot.set_data(run_data, colors, self._state.chart_config)

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
            Label("Select runs to view metrics", id="no-data")
        )
