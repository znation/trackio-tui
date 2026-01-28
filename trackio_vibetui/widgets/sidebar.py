"""Sidebar composite widget combining selectors and controls."""

from textual.app import ComposeResult
from textual.widgets import Static, Select, Label, Input
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual import on

from .run_selector import RunSelector, RunSelectionChanged
from .control_panel import ControlPanel, ChartConfigChanged
from ..data.state import ChartConfig


class ProjectChanged(Message):
    """Posted when project selection changes."""

    def __init__(self, project: str) -> None:
        self.project = project
        super().__init__()


class MetricFilterChanged(Message):
    """Posted when metric filter changes."""

    def __init__(self, filter_text: str) -> None:
        self.filter_text = filter_text
        super().__init__()


class Sidebar(Vertical):
    """Sidebar containing project selector, run selector, and controls."""

    DEFAULT_CSS = """
    Sidebar {
        width: 35;
        height: 1fr;
        dock: left;
        border-right: solid $primary;
    }

    Sidebar VerticalScroll {
        width: 100%;
        height: 1fr;
    }

    Sidebar > Label {
        width: 100%;
        padding: 1;
        background: $primary;
        color: $text;
    }

    Sidebar #project-select {
        margin: 1;
    }

    Sidebar #metric-filter {
        margin: 1;
    }
    """

    def __init__(
        self,
        projects: list[str] | None = None,
        current_project: str | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._projects = projects or []
        self._current_project = current_project

    def compose(self) -> ComposeResult:
        """Compose the sidebar."""
        yield Label("[b]Trackio VibeTUI[/b]")

        with VerticalScroll():
            # Project selector
            project_options = [(p, p) for p in self._projects]
            if project_options:
                yield Select(
                    options=project_options,
                    value=self._current_project,
                    prompt="Select project...",
                    id="project-select"
                )
            else:
                yield Label("No projects found", id="no-projects")

            # Metric filter
            yield Label("Metric Filter:")
            yield Input(placeholder="Filter metrics...", id="metric-filter")

            # Run selector
            yield RunSelector(id="run-selector")

            # Control panel
            yield ControlPanel(id="control-panel")

    @on(Select.Changed, "#project-select")
    def on_project_changed(self, event: Select.Changed) -> None:
        """Handle project selection change."""
        if event.value != Select.BLANK:
            self._current_project = str(event.value)
            self.post_message(ProjectChanged(self._current_project))

    @on(Input.Changed, "#metric-filter")
    def on_metric_filter_changed(self, event: Input.Changed) -> None:
        """Handle metric filter changes."""
        self.post_message(MetricFilterChanged(event.value))

    @on(RunSelectionChanged)
    def on_run_selection_changed(self, event: RunSelectionChanged) -> None:
        """Bubble up run selection changes."""
        # Just let it bubble up naturally
        pass

    @on(ChartConfigChanged)
    def on_chart_config_changed(self, event: ChartConfigChanged) -> None:
        """Bubble up chart config changes."""
        # Just let it bubble up naturally
        pass

    def update_projects(self, projects: list[str], current_project: str | None = None):
        """Update the project list."""
        self._projects = projects
        self._current_project = current_project

        scroll = self.query_one(VerticalScroll)

        # Try to find existing project selector or no-projects label
        try:
            old_widget = self.query_one("#project-select", Select)
        except:
            try:
                old_widget = self.query_one("#no-projects", Label)
            except:
                # Widget doesn't exist yet, nothing to replace
                return

        # Create new project selector
        project_options = [(p, p) for p in projects]
        new_select = Select(
            options=project_options,
            value=current_project,
            prompt="Select project...",
            id="project-select"
        )

        # Replace old widget with new selector
        old_widget.remove()
        scroll.mount(new_select, before=0)

    def get_run_selector(self) -> RunSelector:
        """Get the run selector widget."""
        return self.query_one("#run-selector", RunSelector)

    def get_control_panel(self) -> ControlPanel:
        """Get the control panel widget."""
        return self.query_one("#control-panel", ControlPanel)
