"""
    A4: Run simulation experiments for vulnerability and criticality analysis.

    Round 1: Baseline — all bridges functional, AADT-calibrated traffic
    Round 2: Bridge removal — remove top bridges one-by-one (criticality)
    Round 3: Stochastic failure — disaster-weighted probabilities (vulnerability)

    Round 4 is pure data analysis (done in notebooks, not here).

    Usage:
        python model_run.py round1          # Run Round 1 only
        python model_run.py round2          # Run Round 2 only (needs Round 1 results)
        python model_run.py round3          # Run Round 3 only
        python model_run.py all             # Run all rounds sequentially
        python model_run.py                 # Same as 'all'
"""

from model import BangladeshModel
from components import Source, Bridge
import pandas as pd
import numpy as np
import networkx as nx
import time
import os
import sys

# ---------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------

# 5 x 24 hours; 1 tick = 1 minute
RUN_LENGTH = 5 * 24 * 60  # 7200 ticks

# Number of replications per scenario (different seeds = different bridge breakdowns)
NUM_REPLICATIONS = 10

# Base seeds for replications
SEEDS = [1234567, 2345678, 3456789, 4567890, 5678901,
         6789012, 7890123, 8901234, 9012345, 1357924]

# A4: Number of top bridges to test in Round 2
TOP_N_BRIDGES = 20

OUTPUT_DIR = '../experiment'

# ---------------------------------------------------------------
# A4: Data loading helpers
# ---------------------------------------------------------------

def load_aadt_data():
    """Load AADT data for per-source truck generation.
    Uses (small + medium + heavy trucks) / 2 for per-direction truck count."""
    df = pd.read_csv('../data/integrated_data.csv')
    ss = df[df['model_type'].str.strip() == 'sourcesink']
    aadt_dict = {}
    for _, row in ss.iterrows():
        aadt_dict[row['id']] = (row['small_truck'] + row['medium_truck'] + row['heavy_truck']) / 2
    return aadt_dict


def load_vulnerability_data(season='overall'):
    """Load per-bridge vulnerability probabilities.

    Args:
        season: 'overall', 'dry_season', 'pre_monsoon', or 'post_monsoon'
    Returns:
        dict mapping bridge_id -> failure probability
    """
    vi = pd.read_csv('../data/vulnerability_index.csv')
    col_map = {
        'overall': 'Vulnerability index',
        'dry_season': 'VI_dry_season',
        'pre_monsoon': 'VI_pre_monsoon',
        'post_monsoon': 'VI_post_monsoon',
    }
    col = col_map.get(season, 'Vulnerability index')
    return dict(zip(vi['id'], vi[col]))


# ---------------------------------------------------------------
# Run helpers
# ---------------------------------------------------------------

def run_single(seed, run_length, aadt_data=None, vulnerability_data=None,
               breakdown_probs=None, remove_bridge_id=None):
    """Run a single simulation and return trip data DataFrame and model.

    Args:
        seed: random seed for reproducibility
        run_length: number of ticks to simulate
        aadt_data: dict of sourcesink_id -> truck AADT (per-source generation)
        vulnerability_data: dict of bridge_id -> failure probability
        breakdown_probs: dict of condition -> probability (A3-style fallback)
        remove_bridge_id: bridge ID to remove before running (Round 2)
    """
    Source.truck_counter = 0
    model = BangladeshModel(
        seed=seed,
        aadt_data=aadt_data,
        vulnerability_data=vulnerability_data,
        breakdown_probs=breakdown_probs,
    )

    # A4: remove a specific bridge for criticality testing (Round 2)
    if remove_bridge_id is not None:
        model.remove_bridge(remove_bridge_id)

    for _ in range(run_length):
        model.step()

    return pd.DataFrame(model.trip_data), model


# ---------------------------------------------------------------
# Round 1: Baseline
# ---------------------------------------------------------------

def run_round1():
    """Round 1: Baseline — all bridges functional, AADT-calibrated traffic.
    Identifies most-used bridges for Round 2."""
    aadt_data = load_aadt_data()
    output_dir = os.path.join(OUTPUT_DIR, 'round1_baseline')
    os.makedirs(output_dir, exist_ok=True)

    print(f'\n{"="*60}')
    print('ROUND 1: Baseline (no failures, AADT traffic)')
    print(f'{"="*60}')
    print(f'  Config: {RUN_LENGTH} ticks, {NUM_REPLICATIONS} reps')
    print(f'  AADT sources: {len(aadt_data)}')
    print(flush=True)

    all_trips = []
    all_bridges = []

    for rep in range(NUM_REPLICATIONS):
        seed = SEEDS[rep]
        t0 = time.time()

        df_trips, model = run_single(seed, RUN_LENGTH, aadt_data=aadt_data)
        df_trips['replication'] = rep + 1
        df_trips['seed'] = seed
        all_trips.append(df_trips)

        bridge_data = model.get_bridge_data()
        for b in bridge_data:
            b['replication'] = rep + 1
            b['seed'] = seed
        all_bridges.extend(bridge_data)

        elapsed = time.time() - t0
        completed = len(df_trips[df_trips['dest_road'] != 'stranded'])
        print(f'  Rep {rep+1}/{NUM_REPLICATIONS} (seed={seed}): '
              f'{completed} trips, '
              f'mean travel={df_trips["travel_time"].mean():.0f} min '
              f'({elapsed:.1f}s)', flush=True)

    # Save results
    df_all_trips = pd.concat(all_trips, ignore_index=True)
    df_all_trips.to_csv(os.path.join(output_dir, 'trips.csv'), index=False)

    df_all_bridges = pd.DataFrame(all_bridges)
    df_all_bridges.to_csv(os.path.join(output_dir, 'bridges.csv'), index=False)

    # A4: compute betweenness centrality from the NetworkX graph
    # Use the last model's graph (same for all reps since no bridges removed)
    centrality = nx.betweenness_centrality(model.G, weight='weight')
    bridge_ids_set = set(df_all_bridges['bridge_id'].unique())
    centrality_bridges = {k: v for k, v in centrality.items() if k in bridge_ids_set}

    # A4: combine traffic volume + betweenness for top bridge selection
    avg_traffic = df_all_bridges.groupby('bridge_id')['trucks_crossed'].mean()

    ranking_df = pd.DataFrame({
        'bridge_id': list(bridge_ids_set),
    })
    ranking_df['avg_trucks_crossed'] = ranking_df['bridge_id'].map(avg_traffic)
    ranking_df['betweenness'] = ranking_df['bridge_id'].map(centrality_bridges).fillna(0)

    # Normalise both to [0, 1] and combine with equal weights
    tc_max = ranking_df['avg_trucks_crossed'].max()
    bc_max = ranking_df['betweenness'].max()
    ranking_df['norm_traffic'] = ranking_df['avg_trucks_crossed'] / tc_max if tc_max > 0 else 0
    ranking_df['norm_betweenness'] = ranking_df['betweenness'] / bc_max if bc_max > 0 else 0
    ranking_df['combined_score'] = 0.7 * ranking_df['norm_traffic'] + 0.3 * ranking_df['norm_betweenness']

    # A4: add rank columns so we can compare different ranking strategies
    ranking_df['rank_by_traffic'] = ranking_df['avg_trucks_crossed'].rank(ascending=False).astype(int)
    ranking_df['rank_by_betweenness'] = ranking_df['betweenness'].rank(ascending=False).astype(int)
    ranking_df['rank_by_combined'] = ranking_df['combined_score'].rank(ascending=False).astype(int)

    ranking_df = ranking_df.sort_values('combined_score', ascending=False)
    top_bridge_ids = ranking_df.head(TOP_N_BRIDGES)['bridge_id'].tolist()

    # Save full ranking and top bridges
    ranking_df.to_csv(os.path.join(output_dir, 'bridge_ranking.csv'), index=False)
    ranking_df.head(TOP_N_BRIDGES).to_csv(
        os.path.join(output_dir, 'top_bridges.csv'), index=False)

    baseline_completed = df_all_trips[df_all_trips['dest_road'] != 'stranded']
    baseline_mean = baseline_completed['travel_time'].mean()

    print(f'\n  -> Saved to {output_dir}/')
    print(f'  -> Baseline mean travel time: {baseline_mean:.1f} min')
    print(f'  -> Top {TOP_N_BRIDGES} bridges by combined traffic + betweenness:')
    for _, row in ranking_df.head(5).iterrows():
        print(f'     Bridge {int(row["bridge_id"])}: '
              f'traffic={row["avg_trucks_crossed"]:.0f}, '
              f'betweenness={row["betweenness"]:.4f}, '
              f'combined={row["combined_score"]:.3f}')
    print(flush=True)


# ---------------------------------------------------------------
# Round 2: Bridge Removal (Criticality)
# ---------------------------------------------------------------

def run_round2():
    """Round 2: Remove top bridges one-by-one, measure criticality.
    Requires Round 1 results (top_bridges.csv, trips.csv)."""
    aadt_data = load_aadt_data()
    output_dir = os.path.join(OUTPUT_DIR, 'round2_bridge_removal')
    os.makedirs(output_dir, exist_ok=True)

    # Load Round 1 results
    r1_dir = os.path.join(OUTPUT_DIR, 'round1_baseline')
    if not os.path.exists(os.path.join(r1_dir, 'top_bridges.csv')):
        print('ERROR: Round 1 results not found. Run round1 first.')
        return

    top_bridges_df = pd.read_csv(os.path.join(r1_dir, 'top_bridges.csv'))
    top_bridge_ids = top_bridges_df['bridge_id'].head(TOP_N_BRIDGES).tolist()
    baseline_trips = pd.read_csv(os.path.join(r1_dir, 'trips.csv'))

    # A4: compute baseline mean travel per seed (for per-seed Δ comparison)
    baseline_completed = baseline_trips[baseline_trips['dest_road'] != 'stranded']
    baseline_per_seed = baseline_completed.groupby('seed')['travel_time'].mean()
    baseline_mean_travel = baseline_completed['travel_time'].mean()

    print(f'\n{"="*60}')
    print(f'ROUND 2: Bridge Removal ({len(top_bridge_ids)} bridges x '
          f'{NUM_REPLICATIONS} reps)')
    print(f'{"="*60}')
    print(f'  Baseline mean travel: {baseline_mean_travel:.1f} min')
    print(f'  Estimated time: ~{len(top_bridge_ids) * NUM_REPLICATIONS * 80 / 60:.0f} min')
    print(flush=True)

    results = []

    for i, bridge_id in enumerate(top_bridge_ids):
        bridge_start = time.time()
        all_trips = []

        for rep in range(NUM_REPLICATIONS):
            seed = SEEDS[rep]
            t0 = time.time()

            df_trips, model = run_single(
                seed, RUN_LENGTH,
                aadt_data=aadt_data,
                remove_bridge_id=bridge_id,
            )
            df_trips['replication'] = rep + 1
            df_trips['seed'] = seed
            df_trips['removed_bridge'] = bridge_id
            all_trips.append(df_trips)

            elapsed = time.time() - t0
            print(f'    Rep {rep+1}/{NUM_REPLICATIONS} (seed={seed}): '
                  f'{len(df_trips)} trips ({elapsed:.1f}s)', flush=True)

        df_bridge_trips = pd.concat(all_trips, ignore_index=True)

        # A4: compute per-seed Δ travel time for mean ± std
        completed = df_bridge_trips[df_bridge_trips['dest_road'] != 'stranded']
        stranded = df_bridge_trips[df_bridge_trips['dest_road'] == 'stranded']

        removal_per_seed = completed.groupby('seed')['travel_time'].mean()
        delta_per_seed = removal_per_seed - baseline_per_seed
        delta_per_seed = delta_per_seed.dropna()

        mean_delta = delta_per_seed.mean() if len(delta_per_seed) > 0 else float('inf')
        std_delta = delta_per_seed.std() if len(delta_per_seed) > 1 else 0
        total_stranded = len(stranded)

        results.append({
            'bridge_id': bridge_id,
            'mean_travel_time': completed['travel_time'].mean() if len(completed) > 0 else float('inf'),
            'delta_travel_time': mean_delta,
            'delta_std': std_delta,
            'total_stranded': total_stranded,
            'completed_trips': len(completed),
        })

        bridge_elapsed = time.time() - bridge_start
        remaining = (len(top_bridge_ids) - i - 1) * bridge_elapsed
        print(f'  [{i+1}/{len(top_bridge_ids)}] Bridge {bridge_id}: '
              f'Δ travel={mean_delta:+.1f} ± {std_delta:.1f} min, '
              f'stranded={total_stranded} '
              f'({bridge_elapsed/60:.1f} min, '
              f'~{remaining/60:.0f} min remaining)', flush=True)

        # A4: save after each bridge so progress isn't lost
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('delta_travel_time', ascending=False)
        df_results.to_csv(os.path.join(output_dir, 'criticality_scores.csv'), index=False)

    print(f'\n  -> Saved to {output_dir}/criticality_scores.csv')
    print(f'  -> Most critical: bridge {df_results.iloc[0]["bridge_id"]:.0f} '
          f'(Δ={df_results.iloc[0]["delta_travel_time"]:+.1f} min)', flush=True)


# ---------------------------------------------------------------
# Round 3: Stochastic Failure (Vulnerability)
# ---------------------------------------------------------------

def run_round3():
    """Round 3: Disaster-weighted stochastic bridge failures.
    Tests seasonal scenarios using vulnerability index."""
    aadt_data = load_aadt_data()
    output_dir = os.path.join(OUTPUT_DIR, 'round3_stochastic_failure')
    os.makedirs(output_dir, exist_ok=True)

    # A4: seasonal scenarios using vulnerability index
    # VI is a weighted composite of condition, flood, erosion, earthquake
    # "overall" = monsoon peak (Jun-Sep) when flood & erosion at full intensity
    scenarios = {
        'dry_season': 'dry_season',         # Nov-Feb: low flood/erosion
        'pre_monsoon': 'pre_monsoon',       # Mar-May: moderate flood/erosion
        'post_monsoon': 'post_monsoon',     # Oct: receding but elevated
        'monsoon_peak': 'overall',          # Jun-Sep: full intensity (highest VI)
    }

    print(f'\n{"="*60}')
    print(f'ROUND 3: Stochastic Failure ({len(scenarios)} scenarios x '
          f'{NUM_REPLICATIONS} reps)')
    print(f'{"="*60}', flush=True)

    for scenario_name, season in scenarios.items():
        print(f'\n  --- {scenario_name} ---', flush=True)

        # Load vulnerability data for this season
        vuln_data = load_vulnerability_data(season) if season else {}

        all_trips = []
        all_bridges = []

        for rep in range(NUM_REPLICATIONS):
            seed = SEEDS[rep]
            t0 = time.time()

            df_trips, model = run_single(
                seed, RUN_LENGTH,
                aadt_data=aadt_data,
                vulnerability_data=vuln_data,
            )
            df_trips['replication'] = rep + 1
            df_trips['seed'] = seed
            df_trips['scenario'] = scenario_name
            all_trips.append(df_trips)

            bridge_data = model.get_bridge_data()
            for b in bridge_data:
                b['replication'] = rep + 1
                b['seed'] = seed
                b['scenario'] = scenario_name
            all_bridges.extend(bridge_data)

            elapsed = time.time() - t0
            broken_count = sum(1 for b in bridge_data if b['broken_down'])
            completed = len(df_trips[df_trips['dest_road'] != 'stranded'])
            print(f'    Rep {rep+1}/{NUM_REPLICATIONS}: '
                  f'{broken_count} broken, '
                  f'{completed} trips, '
                  f'mean wait={df_trips["total_waiting_time"].mean():.1f} min '
                  f'({elapsed:.1f}s)', flush=True)

        # Save per-scenario results
        df_trips_all = pd.concat(all_trips, ignore_index=True)
        df_trips_all.to_csv(
            os.path.join(output_dir, f'{scenario_name}_trips.csv'), index=False)

        df_bridges_all = pd.DataFrame(all_bridges)
        df_bridges_all.to_csv(
            os.path.join(output_dir, f'{scenario_name}_bridges.csv'), index=False)

        print(f'  -> Saved {scenario_name} results', flush=True)

    print(f'\n  -> All scenarios saved to {output_dir}/', flush=True)


# ---------------------------------------------------------------
# Main: select which round(s) to run
# ---------------------------------------------------------------

if __name__ == '__main__':
    total_start = time.time()

    # Parse command line argument
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = 'all'

    if mode == 'round1':
        run_round1()
    elif mode == 'round2':
        run_round2()
    elif mode == 'round3':
        run_round3()
    elif mode == 'all':
        run_round1()
        run_round2()
        run_round3()
    else:
        print(f'Unknown mode: {mode}')
        print('Usage: python model_run.py [round1|round2|round3|all]')
        sys.exit(1)

    total_elapsed = time.time() - total_start
    print(f'\n{"="*60}')
    print(f'Completed in {total_elapsed/60:.1f} minutes')
    print(f'{"="*60}')
