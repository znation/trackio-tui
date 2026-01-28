"""Header widget with navigation and status."""

from textual.app import ComposeResult
from textual.widgets import Static, Button, Label
from textual.containers import Horizontal
from textual import on


class Header(Horizontal):
    """Header bar with navigation and status."""

    DEFAULT_CSS = """
    Header {
        width: 100%;
        height: 3;
        dock: top;
        background: $primary;
        padding: 0 1 0 36;
        layout: horizontal;
    }

    Header Button {
        width: auto;
        min-width: 15;
        margin: 0 1;
    }
    """

    def __init__(self, title: str = "Trackio VibeTUI", **kwargs):
        super().__init__(**kwargs)
        self._title = title

    def compose(self) -> ComposeResult:
        """Compose the header."""
        yield Button("Metrics", id="nav-metrics", variant="primary")
        yield Button("System Metrics", id="nav-system", variant="default")
        yield Button("Media & Tables", id="nav-media", variant="default")
        yield Button("Runs", id="nav-runs", variant="default")
        yield Button("Files", id="nav-files", variant="default")

    def set_active_screen(self, screen_name: str):
        """Highlight the active screen button."""
        # Reset all buttons
        for button in self.query(Button):
            button.variant = "default"

        # Highlight active button
        button_id = f"nav-{screen_name}"
        try:
            active_button = self.query_one(f"#{button_id}", Button)
            active_button.variant = "primary"
        except:
            pass

    def update_title(self, title: str):
        """Update the title text."""
        self._title = title
        # Label removed, title no longer displayed
