"""Configuration constants for Trackio TUI."""

import os
from pathlib import Path

# Data paths
TRACKIO_DIR = Path.home() / ".cache" / "huggingface" / "trackio"

# Cache settings
CACHE_TTL_SECONDS = 30
AUTO_REFRESH_INTERVAL_SECONDS = 10

# UI settings
MIN_TERMINAL_WIDTH = 120
MIN_TERMINAL_HEIGHT = 30

# Chart settings
DEFAULT_SMOOTHING = 0.0
MAX_SMOOTHING = 20
SMOOTHING_STEP = 0.1

# Plot settings
PLOT_MIN_HEIGHT = 10
PLOT_MIN_WIDTH = 40
