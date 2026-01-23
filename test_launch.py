"""Quick test to verify the TUI can import and initialize."""

import sys
import os

# Add trackio_tui to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from trackio_tui.app import TrackioTUI
    from trackio_tui.data.loader import TrackioDataLoader
    from trackio_tui.data.state import AppState

    print("✓ Imports successful")

    # Test data loader initialization
    loader = TrackioDataLoader()
    print("✓ Data loader initialized")

    # Test app state
    state = AppState()
    print("✓ App state initialized")

    # Test app initialization (without running)
    app = TrackioTUI()
    print("✓ App initialized")

    print("\nAll basic checks passed! The TUI structure is working.")
    print("\nTo run the TUI, use: python -m trackio_tui")
    print("Note: You'll need trackio data in ~/.trackio/ to see metrics.")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
