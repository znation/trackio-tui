"""Generate sample trackio data for testing the TUI."""

import math
import random
import time
import trackio as tr

def create_sample_project():
    """Create a sample project with multiple runs and metrics."""

    project = "sample_project"

    # Create 3 different runs
    runs = [
        {"name": "experiment_1", "learning_rate": 0.001, "batch_size": 32},
        {"name": "experiment_2", "learning_rate": 0.01, "batch_size": 64},
        {"name": "experiment_3", "learning_rate": 0.0001, "batch_size": 32},
    ]

    for run_config in runs:
        run_name = run_config["name"]
        print(f"\nCreating run: {run_name}")

        with tr.Run(project=project, name=run_name, config=run_config):
            # Log some training metrics
            for step in range(100):
                # Simulate training loss (decreasing with noise)
                base_loss = 2.0 * math.exp(-step / 20)
                noise = random.gauss(0, 0.1)
                loss = base_loss + noise + (0.01 if run_config["learning_rate"] == 0.0001 else 0)

                # Simulate accuracy (increasing with noise)
                base_acc = 1.0 - math.exp(-step / 30)
                acc_noise = random.gauss(0, 0.02)
                accuracy = min(0.99, base_acc + acc_noise)

                # Simulate validation metrics (logged less frequently)
                if step % 10 == 0:
                    val_loss = loss * 1.2 + random.gauss(0, 0.05)
                    val_acc = accuracy * 0.95 + random.gauss(0, 0.01)
                    tr.log({"val/loss": val_loss, "val/accuracy": val_acc}, step=step)

                # Log training metrics
                tr.log({
                    "train/loss": loss,
                    "train/accuracy": accuracy,
                    "train/learning_rate": run_config["learning_rate"],
                }, step=step)

                # Simulate some other metrics
                if step % 5 == 0:
                    gradient_norm = random.uniform(0.5, 2.0) * math.exp(-step / 40)
                    tr.log({"optimization/gradient_norm": gradient_norm}, step=step)

                # Small delay to simulate real training
                time.sleep(0.01)

        print(f"  ✓ Created {run_name} with 100 steps")

    print(f"\n✓ Sample project '{project}' created successfully!")
    print(f"  Location: ~/.trackio/{project}.db")
    print(f"\nYou can now run the TUI: python -m trackio_tui")

if __name__ == "__main__":
    print("Generating sample trackio data...")
    create_sample_project()
