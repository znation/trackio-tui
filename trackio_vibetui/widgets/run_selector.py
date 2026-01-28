"""Run selector widget with checkboxes and filtering."""

from textual.app import ComposeResult
from textual.widgets import Static, Input, Checkbox, Label
from textual.containers import VerticalScroll, Vertical
from textual.message import Message
from textual import on

from ..utils.colors import ColorManager


class RunSelectionChanged(Message):
    """Posted when run selection changes."""

    def __init__(self, selected_runs: set[str]) -> None:
        self.selected_runs = selected_runs
        super().__init__()


class RunSelector(Vertical):
    """Widget for selecting multiple runs with checkboxes."""

    DEFAULT_CSS = """
    RunSelector {
        width: 100%;
        height: auto;
        border: solid $primary;
        padding: 0 1;
    }

    RunSelector Input {
        margin-bottom: 1;
    }

    RunSelector .run-item {
        height: auto;
        padding: 0 1;
    }

    RunSelector .run-checkbox {
        width: 100%;
    }
    """

    def __init__(
        self,
        runs: list[str] | None = None,
        selected_runs: set[str] | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._runs = runs or []
        self._selected_runs = selected_runs or set()
        self._color_manager = ColorManager()
        self._filter_text = ""
        self._updating = False

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label("Runs")
        yield Input(placeholder="Filter runs...", id="run-filter")
        # Create empty container - will be populated by update_runs()
        yield VerticalScroll(id="run-list")

    def _create_run_checkboxes(self) -> list[Checkbox]:
        """Create checkbox widgets for runs."""
        filtered_runs = self._get_filtered_runs()
        checkboxes = []

        for run in filtered_runs:
            color = self._color_manager.get_color(run)
            # Add color indicator before run name
            label = f"[{color}]●[/] {run}"
            checkbox = Checkbox(
                label,
                value=run in self._selected_runs,
                classes="run-checkbox",
                # Don't use ID - will be identified by label
            )
            # Store the run name in the checkbox for later identification
            checkbox.run_name = run
            checkboxes.append(checkbox)

        return checkboxes

    def _get_filtered_runs(self) -> list[str]:
        """Get filtered list of runs based on filter text."""
        if not self._filter_text:
            return self._runs

        filter_lower = self._filter_text.lower()
        return [r for r in self._runs if filter_lower in r.lower()]

    @on(Input.Changed, "#run-filter")
    def filter_runs(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        self._filter_text = event.value
        self._refresh_run_list()

    @on(Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox state changes."""
        # Get run name from checkbox attribute
        checkbox = event.checkbox
        if hasattr(checkbox, 'run_name'):
            run_id = checkbox.run_name

            if event.value:
                self._selected_runs.add(run_id)
            else:
                self._selected_runs.discard(run_id)

            self.post_message(RunSelectionChanged(self._selected_runs.copy()))

    def _refresh_run_list(self) -> None:
        """Refresh the run list display."""
        # Prevent concurrent updates
        if self._updating:
            return

        # Make sure we're mounted before trying to refresh
        if not self.is_mounted:
            return

        try:
            run_list = self.query_one("#run-list", VerticalScroll)
        except:
            # Widget not ready yet
            return

        self._updating = True
        try:
            # Clear all children completely
            run_list.remove_children()

            # Mount new checkboxes
            new_checkboxes = self._create_run_checkboxes()
            for checkbox in new_checkboxes:
                run_list.mount(checkbox)
        finally:
            self._updating = False

    def update_runs(self, runs: list[str], selected_runs: set[str] | None = None):
        """Update the list of runs."""
        self._runs = runs
        if selected_runs is not None:
            self._selected_runs = selected_runs
        self._refresh_run_list()

    def get_color_manager(self) -> ColorManager:
        """Get the color manager for coordinate coloring."""
        return self._color_manager
