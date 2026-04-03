"""
A4: Experiment runner — generates raw simulation and analysis data.

Round 1 — Criticality: Baseline simulation (traffic volume per bridge) +
          graph-based connectivity analysis (broken OD pairs per bridge).
          Outputs a combined criticality score for all bridges.

Round 2 — Vulnerability: Seasonal stochastic failure simulations using
          disaster-weighted per-bridge failure probabilities.
          Outputs trip and bridge data for each seasonal scenario.

Combined analysis (priority matrix) is done in notebooks, not here.

Usage:
    python model_run.py round1
    python model_run.py round2
    python model_run.py all       (default)
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

RUN_LENGTH = 5 * 24 * 60          # 7200 ticks (5 days, 1 tick = 1 min)
NUM_REPLICATIONS = 10
SEEDS = [1234567, 2345678, 3456789, 4567890, 5678901,
         6789012, 7890123, 8901234, 9012345, 1357924]

# Criticality weights: how to combine traffic and connectivity loss
W_TRAFFIC = 0.7
W_CONNECTIVITY = 0.3

# Vulnerability Index -> failure probability rescaling bounds
FAILURE_PROB_MIN = 0.02
FAILURE_PROB_MAX = 0.50

OUTPUT_DIR = '../experiment'


# ---------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------

def load_aadt_data():
    """Load truck AADT per source. Uses (small+medium+heavy)/2 per direction."""
    df = pd.read_csv('../data/integrated_data.csv')
    ss = df[df['model_type'].str.strip() == 'sourcesink']
    return {
        row['id']: (row['small_truck'] + row['medium_truck'] + row['heavy_truck']) / 2
        for _, row in ss.iterrows()
    }


def load_vulnerability_data(season='overall'):
    """Load per-bridge failure probabilities, rescaled from Vulnerability Index.

    VI is in [0,1] and is rescaled linearly to [FAILURE_PROB_MIN, FAILURE_PROB_MAX].
    """
    vi = pd.read_csv('../data/vulnerability_index.csv')
    col_map = {
        'overall': 'Vulnerability index',
        'dry_season': 'VI_dry_season',
        'pre_monsoon': 'VI_pre_monsoon',
        'post_monsoon': 'VI_post_monsoon',
    }
    col = col_map.get(season, 'Vulnerability index')
    prob = FAILURE_PROB_MIN + vi[col] * (FAILURE_PROB_MAX - FAILURE_PROB_MIN)
    return dict(zip(vi['id'], prob))


def run_simulation(seed, aadt_data=None, vulnerability_data=None):
    """Run one simulation replication. Returns (trip_df, model)."""
    Source.truck_counter = 0
    model = BangladeshModel(
        seed=seed,
        aadt_data=aadt_data,
        vulnerability_data=vulnerability_data,
        run_length=RUN_LENGTH,
    )
    for _ in range(RUN_LENGTH):
        model.step()
    return pd.DataFrame(model.trip_data), model


# ---------------------------------------------------------------
# Round 1: Criticality
# ---------------------------------------------------------------

def run_round1():
    """Criticality analysis: simulation traffic + graph connectivity loss.

    Step A - Run baseline simulation to measure truck traffic per bridge.
    Step B - Graph analysis: remove each bridge, count broken OD pairs.
    Step C - Combine: criticality = 0.7*norm_traffic + 0.3*norm_broken_pct.

    Outputs -> round1_criticality/
        trips.csv, bridges.csv        (simulation data)
        criticality_scores.csv        (all 737 bridges ranked)
    """
    aadt_data = load_aadt_data()
    out = os.path.join(OUTPUT_DIR, 'round1_criticality')
    os.makedirs(out, exist_ok=True)

    # --- Step A: Baseline simulation ---
    print('\n' + '=' * 60)
    print('ROUND 1: Criticality Analysis')
    print('=' * 60)
    print('  Step A: Baseline simulation ({} reps, {} ticks)'.format(
        NUM_REPLICATIONS, RUN_LENGTH))
    sys.stdout.flush()

    all_trips, all_bridges = [], []
    for rep in range(NUM_REPLICATIONS):
        seed = SEEDS[rep]
        t0 = time.time()

        df_trips, model = run_simulation(seed, aadt_data=aadt_data)
        df_trips['replication'] = rep + 1
        df_trips['seed'] = seed
        all_trips.append(df_trips)

        bridge_data = model.get_bridge_data()
        for b in bridge_data:
            b['replication'] = rep + 1
            b['seed'] = seed
        all_bridges.extend(bridge_data)

        elapsed = time.time() - t0
        n_trips = len(df_trips[df_trips['dest_road'] != 'stranded'])
        print('    Rep {}/{} (seed={}): {} trips, mean travel={:.0f} min ({:.1f}s)'.format(
            rep + 1, NUM_REPLICATIONS, seed, n_trips,
            df_trips['travel_time'].mean(), elapsed))
        sys.stdout.flush()

    df_trips_all = pd.concat(all_trips, ignore_index=True)
    df_bridges_all = pd.DataFrame(all_bridges)
    df_trips_all.to_csv(os.path.join(out, 'trips.csv'), index=False)
    df_bridges_all.to_csv(os.path.join(out, 'bridges.csv'), index=False)

    avg_traffic = df_bridges_all.groupby('bridge_id')['trucks_crossed'].mean()

    # --- Step B: Graph-based connectivity analysis ---
    print('\n  Step B: Graph connectivity analysis (all {} bridges)'.format(
        len(avg_traffic)))
    sys.stdout.flush()

    G = model.G
    od_nodes = list(set(model.sources) | set(model.sinks))
    od_pairs = [(s, t) for s in od_nodes for t in od_nodes if s != t]
    baseline_connected = set()
    for s, t in od_pairs:
        if nx.has_path(G, s, t):
            baseline_connected.add((s, t))
    n_baseline = len(baseline_connected)

    bridge_ids = [b for b in avg_traffic.index if b in G]
    connectivity = {}
    t0 = time.time()

    for i, bid in enumerate(bridge_ids):
        edges = list(G.edges(bid, data=True))
        G.remove_node(bid)

        broken = 0
        for s, t in baseline_connected:
            if s in G and t in G and not nx.has_path(G, s, t):
                broken += 1

        connectivity[bid] = round(100 * broken / n_baseline, 2) if n_baseline else 0

        G.add_node(bid)
        G.add_edges_from(edges)

        if (i + 1) % 100 == 0:
            print('    {}/{} bridges tested ({:.0f}s)'.format(
                i + 1, len(bridge_ids), time.time() - t0))
            sys.stdout.flush()

    print('    Done: {} bridges in {:.0f}s'.format(
        len(bridge_ids), time.time() - t0))
    sys.stdout.flush()

    # --- Step C: Combined criticality score ---
    print('\n  Step C: Computing combined criticality scores')

    net_df = pd.read_csv('../data/integrated_data.csv')
    bridge_meta = net_df[net_df['model_type'].str.strip() == 'bridge'][
        ['id', 'road', 'name', 'condition', 'length', 'lat', 'lon']
    ].copy()

    scores = bridge_meta.rename(columns={'id': 'bridge_id'}).copy()
    scores['avg_trucks_crossed'] = scores['bridge_id'].map(avg_traffic).fillna(0)
    scores['broken_pct'] = scores['bridge_id'].map(connectivity).fillna(0)

    # Normalise to [0, 1]
    tc_max = scores['avg_trucks_crossed'].max()
    bp_max = scores['broken_pct'].max()
    scores['norm_traffic'] = scores['avg_trucks_crossed'] / tc_max if tc_max > 0 else 0
    scores['norm_connectivity'] = scores['broken_pct'] / bp_max if bp_max > 0 else 0

    # Combined criticality
    scores['criticality_score'] = (
        W_TRAFFIC * scores['norm_traffic'] +
        W_CONNECTIVITY * scores['norm_connectivity']
    )
    scores = scores.sort_values('criticality_score', ascending=False)
    scores['criticality_rank'] = range(1, len(scores) + 1)

    scores.to_csv(os.path.join(out, 'criticality_scores.csv'), index=False)

    baseline_mean = df_trips_all[
        df_trips_all['dest_road'] != 'stranded']['travel_time'].mean()
    n_disconnect = (scores['broken_pct'] > 0).sum()

    print('\n  Results:')
    print('    Baseline mean travel time: {:.1f} min'.format(baseline_mean))
    print('    Bridges that disconnect network: {}/{}'.format(
        n_disconnect, len(scores)))
    print('\n  Top 10 most critical bridges:')
    for _, r in scores.head(10).iterrows():
        name_str = str(r['name'])[:35] if pd.notna(r['name']) else ''
        print('    #{:3d} | {:5s} | {:35s} | traffic={:,.0f} | broken={:.1f}% | score={:.3f}'.format(
            int(r['criticality_rank']), r['road'], name_str,
            r['avg_trucks_crossed'], r['broken_pct'], r['criticality_score']))
    print('\n  -> Saved to {}/'.format(out))
    sys.stdout.flush()


# ---------------------------------------------------------------
# Round 2: Vulnerability
# ---------------------------------------------------------------

def run_round2():
    """Seasonal stochastic failure - disaster-weighted bridge failures.

    Four scenarios using the Vulnerability Index with seasonal multipliers:
        dry_season    (Nov-Feb): flood/erosion scaled down
        pre_monsoon   (Mar-May): moderate
        post_monsoon  (Oct):     receding but elevated
        monsoon_peak  (Jun-Sep): full intensity

    Outputs -> round2_vulnerability/
        {scenario}_trips.csv      trip data per scenario
        {scenario}_bridges.csv    bridge data per scenario
    """
    aadt_data = load_aadt_data()
    out = os.path.join(OUTPUT_DIR, 'round2_vulnerability')
    os.makedirs(out, exist_ok=True)

    scenarios = {
        'dry_season': 'dry_season',
        'pre_monsoon': 'pre_monsoon',
        'post_monsoon': 'post_monsoon',
        'monsoon_peak': 'overall',
    }

    print('\n' + '=' * 60)
    print('ROUND 2: Vulnerability ({} scenarios x {} reps)'.format(
        len(scenarios), NUM_REPLICATIONS))
    print('=' * 60)
    sys.stdout.flush()

    for scenario_name, season in scenarios.items():
        print('\n  --- {} ---'.format(scenario_name))
        sys.stdout.flush()
        vuln_data = load_vulnerability_data(season)

        all_trips, all_bridges = [], []
        for rep in range(NUM_REPLICATIONS):
            seed = SEEDS[rep]
            t0 = time.time()

            df_trips, model = run_simulation(seed, aadt_data, vuln_data)
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
            broken = sum(1 for b in bridge_data if b['broken_down'])
            n_trips = len(df_trips[df_trips['dest_road'] != 'stranded'])
            print('    Rep {}/{}: {} broken, {} trips, '
                  'mean wait={:.1f} min ({:.1f}s)'.format(
                      rep + 1, NUM_REPLICATIONS, broken, n_trips,
                      df_trips['total_waiting_time'].mean(), elapsed))
            sys.stdout.flush()

        pd.concat(all_trips, ignore_index=True).to_csv(
            os.path.join(out, '{}_trips.csv'.format(scenario_name)), index=False)
        pd.DataFrame(all_bridges).to_csv(
            os.path.join(out, '{}_bridges.csv'.format(scenario_name)), index=False)
        print('    -> Saved {}'.format(scenario_name))
        sys.stdout.flush()

    print('\n  -> All scenarios saved to {}/'.format(out))
    sys.stdout.flush()


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------

if __name__ == '__main__':
    total_start = time.time()
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else 'all'

    rounds = {'round1': run_round1, 'round2': run_round2}

    if mode == 'all':
        for fn in rounds.values():
            fn()
    elif mode in rounds:
        rounds[mode]()
    else:
        print('Unknown: {}'.format(mode))
        print('Usage: python model_run.py [round1|round2|all]')
        sys.exit(1)

    print('\n' + '=' * 60)
    print('Completed in {:.1f} minutes'.format((time.time() - total_start) / 60))
    print('=' * 60)
