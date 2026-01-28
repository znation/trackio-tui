"""Control panel widget for chart configuration."""

from textual.app import ComposeResult
from textual.widgets import Static, Select, Label, Button, Checkbox
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual import on

from ..data.state import ChartConfig


class ChartConfigChanged(Message):
    """Posted when chart configuration changes."""

    def __init__(self, config: ChartConfig) -> None:
        self.config = config
        super().__init__()


class ControlPanel(Vertical):
    """Widget for chart configuration controls."""

    DEFAULT_CSS = """
    ControlPanel {
        width: 100%;
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    ControlPanel Label {
        width: 100%;
        margin-bottom: 1;
    }

    ControlPanel Select {
        width: 100%;
        margin-bottom: 1;
    }

    ControlPanel Horizontal {
        width: 100%;
        height: auto;
    }

    ControlPanel .smoothing-container {
        margin-bottom: 1;
    }

    ControlPanel Button {
        margin: 0 1;
    }
    """

    def __init__(self, config: ChartConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        self._config = config or ChartConfig()

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label("[b]Chart Controls[/b]")

        # X-axis selector
        yield Label("X-axis:")
        yield Select(
            options=[
                ("Step", "step"),
                ("Relative Time", "relative"),
                ("Wall Time", "wall"),
            ],
            value=self._config.x_axis,
            id="x-axis-select"
        )

        # Smoothing controls
        with Horizontal(classes="smoothing-container"):
            yield Label(f"Smoothing: {self._config.smoothing:.1f}")
            yield Button("-", id="smooth-dec", variant="primary")
            yield Button("+", id="smooth-inc", variant="primary")

        # Log scale toggles
        yield Checkbox("Log scale X", value=self._config.log_scale_x, id="log-x")
        yield Checkbox("Log scale Y", value=self._config.log_scale_y, id="log-y")

    @on(Select.Changed, "#x-axis-select")
    def on_x_axis_changed(self, event: Select.Changed) -> None:
        """Handle X-axis selection change."""
        if event.value != Select.BLANK:
            self._config.x_axis = str(event.value)
            self.post_message(ChartConfigChanged(self._config))

    @on(Button.Pressed, "#smooth-inc")
    def increase_smoothing(self) -> None:
        """Increase smoothing value."""
        self._config.smoothing = min(20.0, self._config.smoothing + 1.0)
        self._update_smoothing_label()
        self.post_message(ChartConfigChanged(self._config))

    @on(Button.Pressed, "#smooth-dec")
    def decrease_smoothing(self) -> None:
        """Decrease smoothing value."""
        self._config.smoothing = max(0.0, self._config.smoothing - 1.0)
        self._update_smoothing_label()
        self.post_message(ChartConfigChanged(self._config))

    @on(Checkbox.Changed, "#log-x")
    def on_log_x_changed(self, event: Checkbox.Changed) -> None:
        """Handle log scale X toggle."""
        self._config.log_scale_x = event.value
        self.post_message(ChartConfigChanged(self._config))

    @on(Checkbox.Changed, "#log-y")
    def on_log_y_changed(self, event: Checkbox.Changed) -> None:
        """Handle log scale Y toggle."""
        self._config.log_scale_y = event.value
        self.post_message(ChartConfigChanged(self._config))

    def _update_smoothing_label(self) -> None:
        """Update the smoothing label display."""
        labels = self.query(Label)
        for label in labels:
            if "Smoothing:" in str(label.renderable):
                label.update(f"Smoothing: {self._config.smoothing:.1f}")
                break

    def get_config(self) -> ChartConfig:
        """Get current chart configuration."""
        return self._config
