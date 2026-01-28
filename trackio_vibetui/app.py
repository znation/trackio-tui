"""Main Trackio VibeTUI application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button
from textual import on

from .screens.metrics import MetricsScreen
from .screens.system_metrics import SystemMetricsScreen
from .data.loader import TrackioDataLoader
from .data.state import AppState


class TrackioTUI(App):
    """Terminal User Interface for Trackio ML experiment tracking."""

    CSS_PATH = "styles/main.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("m", "show_metrics", "Metrics"),
        Binding("s", "show_system", "System"),
        Binding("n", "show_runs", "Runs"),
        Binding("f", "show_files", "Files"),
        Binding("t", "show_media", "Media"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self._loader = TrackioDataLoader()
        self._state = AppState()
        self.title = "Trackio VibeTUI"
        self.sub_title = "ML Experiment Tracking"

    def on_mount(self) -> None:
        """Initialize app on mount."""
        # Install metrics screen
        self.install_screen(
            MetricsScreen(self._loader, self._state),
            name="metrics"
        )

        # Install system metrics screen
        self.install_screen(
            SystemMetricsScreen(self._loader, self._state),
            name="system_metrics"
        )

        # Switch to metrics screen
        self.push_screen("metrics")

    @on(Button.Pressed, "#nav-metrics")
    def action_show_metrics(self) -> None:
        """Switch to metrics screen."""
        self.push_screen("metrics")

    @on(Button.Pressed, "#nav-system")
    def action_show_system(self) -> None:
        """Switch to system metrics screen."""
        self.push_screen("system_metrics")

    @on(Button.Pressed, "#nav-runs")
    def action_show_runs(self) -> None:
        """Switch to runs screen."""
        self.notify("Runs view coming soon!", severity="information")

    @on(Button.Pressed, "#nav-media")
    def action_show_media(self) -> None:
        """Switch to media screen."""
        self.notify("Media view coming soon!", severity="information")

    @on(Button.Pressed, "#nav-files")
    def action_show_files(self) -> None:
        """Switch to files screen."""
        self.notify("Files view coming soon!", severity="information")

    def action_refresh(self) -> None:
        """Refresh data from disk."""
        self._loader.invalidate_cache()
        self.notify("Cache cleared, data will refresh", severity="information")

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
[b]Trackio VibeTUI - Keyboard Shortcuts[/b]

[cyan]q[/cyan] - Quit application
[cyan]r[/cyan] - Refresh data (clear cache)
[cyan]m[/cyan] - Show metrics view
[cyan]s[/cyan] - Show system metrics view
[cyan]n[/cyan] - Show runs view
[cyan]t[/cyan] - Show media/tables view
[cyan]f[/cyan] - Show files view
[cyan]?[/cyan] - Show this help

[b]Navigation:[/b]
- Use mouse or keyboard to interact with widgets
- Use tab to move between widgets
- Use arrow keys in lists and inputs
"""
        self.notify(help_text, severity="information", timeout=10)

    def on_unmount(self) -> None:
        """Cleanup on app exit."""
        self._loader.shutdown()


def main():
    """Entry point for the application."""
    app = TrackioTUI()
    app.run()


if __name__ == "__main__":
    main()
