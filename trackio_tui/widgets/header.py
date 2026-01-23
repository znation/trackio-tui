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
        padding: 0 1;
    }

    Header Label {
        width: 1fr;
        content-align: center middle;
        text-style: bold;
    }

    Header Button {
        margin: 0 1;
    }
    """

    def __init__(self, title: str = "Trackio TUI", **kwargs):
        super().__init__(**kwargs)
        self._title = title

    def compose(self) -> ComposeResult:
        """Compose the header."""
        yield Button("Metrics", id="nav-metrics", variant="primary")
        yield Button("System", id="nav-system", variant="default")
        yield Button("Runs", id="nav-runs", variant="default")
        yield Button("Media", id="nav-media", variant="default")
        yield Button("Files", id="nav-files", variant="default")
        yield Label(self._title)

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
        label = self.query_one(Label)
        label.update(title)
