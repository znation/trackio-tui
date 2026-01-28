"""Test that the data loader can access the test data."""

import asyncio
from trackio_vibetui.data.loader import TrackioDataLoader

async def test_data_access():
    """Test data loading from the sample project."""
    loader = TrackioDataLoader()

    print("Testing data access...")

    # Get projects
    projects = await loader.get_projects()
    print(f"\n✓ Found {len(projects)} project(s): {projects}")

    if "sample_project" in projects:
        # Get runs
        runs = await loader.get_runs("sample_project")
        print(f"\n✓ Found {len(runs)} run(s): {runs}")

        # Get configs
        configs = await loader.get_all_run_configs("sample_project")
        print(f"\n✓ Found configs for {len(configs)} run(s)")
        for run_id, config in configs.items():
            print(f"  - {run_id}: {config}")

        # Get metrics for first run
        if runs:
            first_run = runs[0]
            metrics = await loader.get_all_metrics_for_run("sample_project", first_run)
            print(f"\n✓ Found {len(metrics)} metric(s) for {first_run}:")
            for metric in sorted(metrics):
                print(f"  - {metric}")

            # Get sample metric values
            if metrics:
                first_metric = sorted(metrics)[0]
                values = await loader.get_metric_values("sample_project", first_run, first_metric)
                print(f"\n✓ {first_metric} has {len(values)} data points")
                if values:
                    print(f"  First point: step={values[0].get('step')}, value={values[0].get('value'):.4f}")
                    print(f"  Last point: step={values[-1].get('step')}, value={values[-1].get('value'):.4f}")

    loader.shutdown()
    print("\n✓ All data access tests passed!")

if __name__ == "__main__":
    asyncio.run(test_data_access())
