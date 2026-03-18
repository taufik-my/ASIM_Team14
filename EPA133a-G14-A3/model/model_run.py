"""
    Experiment runner for Assignment 3
    Runs 5 scenarios with 10 replications each (different seeds).
    Each replication has different bridges breaking down.
    Output CSV files are saved to the experiment/ folder.
"""

from model import BangladeshModel
from components import Source
import pandas as pd
import time
import os

# ---------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------

# 5 x 24 hours; 1 tick = 1 minute
RUN_LENGTH = 5 * 24 * 60  # 7200 ticks

# Number of replications per scenario (different seeds = different bridge breakdowns)
NUM_REPLICATIONS = 10

# Base seeds for replications (each gives different bridge breakdowns)
SEEDS = [1234567, 2345678, 3456789, 4567890, 5678901,
         6789012, 7890123, 8901234, 9012345, 1357924]

# Scenario definitions: {scenario_name: {condition: breakdown_probability}}
SCENARIOS = {
    'scenario 0': {'A': 0.00, 'B': 0.00, 'C': 0.00, 'D': 0.00},
    'scenario 1': {'A': 0.00, 'B': 0.00, 'C': 0.00, 'D': 0.05},
    'scenario 2': {'A': 0.00, 'B': 0.00, 'C': 0.05, 'D': 0.10},
    'scenario 3': {'A': 0.00, 'B': 0.05, 'C': 0.10, 'D': 0.20},
    'scenario 4': {'A': 0.05, 'B': 0.10, 'C': 0.20, 'D': 0.40},
}

OUTPUT_DIR = '../experiment'

# ---------------------------------------------------------------
# Run experiments
# ---------------------------------------------------------------

def run_single(seed, breakdown_probs, run_length):
    """Run a single simulation and return trip data DataFrame."""
    Source.truck_counter = 0
    model = BangladeshModel(seed=seed, breakdown_probs=breakdown_probs)

    for _ in range(run_length):
        model.step()

    return pd.DataFrame(model.trip_data)


def run_experiments():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for scenario_name, probs in SCENARIOS.items():
        print(f'\n{"="*60}')
        print(f'Running {scenario_name}: {probs}')
        print(f'{"="*60}')

        all_trips = []
        for rep in range(NUM_REPLICATIONS):
            seed = SEEDS[rep]
            t0 = time.time()

            df_trips = run_single(seed, probs, RUN_LENGTH)
            df_trips['replication'] = rep + 1
            df_trips['seed'] = seed
            df_trips['scenario'] = scenario_name
            all_trips.append(df_trips)

            elapsed = time.time() - t0
            print(f'  Replication {rep+1}/{NUM_REPLICATIONS} (seed={seed}): '
                  f'{len(df_trips)} trips, '
                  f'mean travel={df_trips["travel_time"].mean():.0f} min, '
                  f'mean wait={df_trips["total_waiting_time"].mean():.1f} min, '
                  f'({elapsed:.1f}s)')

        # Combine all replications and save
        df_scenario = pd.concat(all_trips, ignore_index=True)
        output_path = os.path.join(OUTPUT_DIR, f'{scenario_name}.csv')
        df_scenario.to_csv(output_path, index=False)
        print(f'  -> Saved {len(df_scenario)} trips to {output_path}')


if __name__ == '__main__':
    total_start = time.time()
    run_experiments()
    total_elapsed = time.time() - total_start
    print(f'\nAll experiments completed in {total_elapsed/60:.1f} minutes')
