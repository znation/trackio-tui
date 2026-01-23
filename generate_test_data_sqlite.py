"""Generate sample trackio data using SQLiteStorage directly."""

import math
import random
import time
from trackio.sqlite_storage import SQLiteStorage

def create_sample_project():
    """Create a sample project with multiple runs and metrics using SQLiteStorage."""

    project = "sample_project"

    # Create 3 different runs
    runs = [
        {"run_id": "experiment_1", "config": {"learning_rate": 0.001, "batch_size": 32, "group": "baseline"}},
        {"run_id": "experiment_2", "config": {"learning_rate": 0.01, "batch_size": 64, "group": "high_lr"}},
        {"run_id": "experiment_3", "config": {"learning_rate": 0.0001, "batch_size": 32, "group": "low_lr"}},
    ]

    for run_info in runs:
        run_id = run_info["run_id"]
        config = run_info["config"]
        print(f"\nCreating run: {run_id}")

        # Store run config
        SQLiteStorage.store_config(project, run_id, config)

        # Log some training metrics
        for step in range(100):
            # Simulate training loss (decreasing with noise)
            base_loss = 2.0 * math.exp(-step / 20)
            noise = random.gauss(0, 0.1)
            loss = base_loss + noise + (0.01 if config["learning_rate"] == 0.0001 else 0)

            # Simulate accuracy (increasing with noise)
            base_acc = 1.0 - math.exp(-step / 30)
            acc_noise = random.gauss(0, 0.02)
            accuracy = min(0.99, base_acc + acc_noise)

            # Get current timestamp
            timestamp = time.time()

            # Build metrics dict for this step
            metrics = {
                "train/loss": loss,
                "train/accuracy": accuracy,
                "train/learning_rate": config["learning_rate"],
            }

            # Simulate validation metrics (logged less frequently)
            if step % 10 == 0:
                val_loss = loss * 1.2 + random.gauss(0, 0.05)
                val_acc = accuracy * 0.95 + random.gauss(0, 0.01)
                metrics["val/loss"] = val_loss
                metrics["val/accuracy"] = val_acc

            # Simulate some other metrics
            if step % 5 == 0:
                gradient_norm = random.uniform(0.5, 2.0) * math.exp(-step / 40)
                metrics["optimization/gradient_norm"] = gradient_norm

            # Log all metrics for this step
            SQLiteStorage.log(project, run_id, metrics, step)

        print(f"  ✓ Created {run_id} with 100 steps")

    print(f"\n✓ Sample project '{project}' created successfully!")
    print(f"  Location: ~/.trackio/{project}.db")
    print(f"\nYou can now run the TUI: python -m trackio_tui")

if __name__ == "__main__":
    print("Generating sample trackio data...")
    create_sample_project()
