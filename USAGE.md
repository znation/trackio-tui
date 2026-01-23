# Trackio TUI Usage Guide

## Quick Start

### 1. Activate Virtual Environment

```bash
source ~/temp/venv/bin/activate
```

### 2. Generate Sample Data (First Time Only)

If you don't have any trackio data yet, generate sample data:

```bash
python generate_test_data_sqlite.py
```

This creates a sample project with 3 experiment runs and various metrics.

### 3. Run the TUI

```bash
python -m trackio_tui
```

## Using the TUI

### Main Interface

The TUI consists of:

- **Header Bar** (top): Navigation buttons for different views
- **Sidebar** (left): Project selector, run selector, and chart controls
- **Main Content Area** (right): Metric plots and visualizations

### Selecting Data

1. **Select a Project**: Use the dropdown at the top of the sidebar
2. **Filter Runs**: Type in the run filter input to search for specific runs
3. **Select Runs**: Check the boxes next to runs you want to compare
   - Each run gets a unique color shown as a colored dot (●)
4. **Filter Metrics**: Use the metric filter to search for specific metrics

### Chart Controls

In the Control Panel section of the sidebar:

- **X-axis**: Choose between Step, Relative Time, or Wall Time
- **Smoothing**: Click +/- buttons to adjust smoothing (0-20)
  - Higher values = smoother curves
  - 0 = no smoothing (raw data)
- **Log Scale X/Y**: Toggle logarithmic scales for axes

### Viewing Metrics

- Metrics are automatically grouped by prefix (e.g., `train/`, `val/`, `optimization/`)
- Each plot shows the selected runs overlaid with different colors
- Colors match the dots shown next to run names in the sidebar
- Plots update automatically when you change selections or controls

### Keyboard Shortcuts

- `q` - Quit application
- `r` - Refresh data (clears cache, reloads from disk)
- `m` - Show metrics view (current screen)
- `s` - Show system metrics view (coming soon)
- `n` - Show runs view (coming soon)
- `t` - Show media/tables view (coming soon)
- `f` - Show files view (coming soon)
- `?` - Show help message

### Navigation

- Use **mouse** to click buttons, checkboxes, and inputs
- Use **Tab** to move between widgets
- Use **Arrow keys** in dropdowns and lists
- Use **Space** or **Enter** to toggle checkboxes

## Data Location

Trackio stores data in: `~/.cache/huggingface/trackio/`

Each project has its own SQLite database:
- `sample_project.db`
- `your_project.db`

## Testing

### Test Scripts

1. **test_launch.py** - Verifies imports and initialization
   ```bash
   python test_launch.py
   ```

2. **test_data_access.py** - Tests data loading
   ```bash
   python test_data_access.py
   ```

3. **generate_test_data_sqlite.py** - Creates sample data
   ```bash
   python generate_test_data_sqlite.py
   ```

## Troubleshooting

### No Projects Found

- Make sure trackio data exists in `~/.cache/huggingface/trackio/`
- Run `generate_test_data_sqlite.py` to create sample data

### Plots Not Showing

- Select at least one run using checkboxes
- Check that the selected runs have metrics
- Try clearing cache with `r` key

### TUI Won't Start

- Make sure virtual environment is activated
- Install dependencies: `pip install textual textual-plotext`
- Check for errors in console output

## Current Limitations (Phase 1)

This is the MVP (Phase 1) implementation with the core metrics visualization.

**Not Yet Implemented:**
- System metrics view
- Runs table view
- Run details screen
- Media/tables viewer
- Files browser
- Auto-refresh
- Additional screens

These features are planned for future phases according to the implementation plan.

## Tips

1. **Comparing Runs**: Select multiple runs to see them overlaid on the same plot
2. **Finding Metrics**: Use the metric filter to quickly find specific metrics
3. **Smoothing**: Start with 0 smoothing, then increase gradually to see trends
4. **Cache**: Use `r` key to refresh if data isn't updating

## Next Steps

To add more data:
- Use trackio in your ML experiments to log metrics
- Data will automatically appear in the TUI
- Create additional projects by using different project names in trackio
