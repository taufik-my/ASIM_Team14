"""
    A4: Run simulation experiments for vulnerability and criticality analysis.

    Round 1: Baseline — all bridges functional, AADT-calibrated traffic.
             Ranks bridges by traffic volume + betweenness centrality.

    Round 2: Connectivity loss — for every bridge in the network, remove it
             and count how many origin-destination pairs lose all viable routes.
             Produces a full criticality ranking for all 737 bridges in minutes.
             (Jenelius et al. 2006; Jafino et al. 2020; Cats & Jenelius 2020)

    Round 3: Stochastic failure — disaster-weighted probabilities (vulnerability)
             across four seasonal scenarios using the vulnerability index.

    Round 4: Data analysis only — no simulation. Aggregates Round 3 outputs,
             normalises criticality (Round 2) and vulnerability (Round 3), and
             produces a priority matrix and ranked investment list.
             Saves intermediate CSVs to round4_combined_analysis/ for the
             companion notebook (round4_analysis.ipynb).

    Usage:
        python model_run.py round1          # Run Round 1 only
        python model_run.py round2          # Run Round 2 only
        python model_run.py round3          # Run Round 3 only
        python model_run.py round4          # Run Round 4 only
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

# A4: Number of top bridges to identify from Round 1 (by traffic + betweenness)
TOP_N_BRIDGES = 20

# A4: Failure probability bounds for Round 3 stochastic failure.
# The Vulnerability Index (VI) is a composite index in [0, 1] — not a calibrated
# failure probability. Using it directly overestimates failure rates (e.g., VI=0.75
# would imply 75% chance of failure per 5-day run, which is unrealistic).
# We instead rescale VI linearly to [FAILURE_PROB_MIN, FAILURE_PROB_MAX]:
#   prob = FAILURE_PROB_MIN + VI * (FAILURE_PROB_MAX - FAILURE_PROB_MIN)
# This preserves relative ordering between bridges while producing realistic rates.
# Bounds are based on engineering judgment for Bangladesh flood season failure rates.
FAILURE_PROB_MIN = 0.02   # least vulnerable bridge: ~2% per simulation window
FAILURE_PROB_MAX = 0.50   # most vulnerable bridge: ~50% per simulation window

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
    """Load per-bridge failure probabilities, rescaled from the Vulnerability Index.

    The VI is a composite index in [0, 1] representing relative bridge vulnerability
    — it is not a calibrated failure probability. We apply a linear rescaling:

        prob = FAILURE_PROB_MIN + VI * (FAILURE_PROB_MAX - FAILURE_PROB_MIN)

    This maps VI=0 (no vulnerability) to FAILURE_PROB_MIN and VI=1 (maximum
    vulnerability) to FAILURE_PROB_MAX, preserving relative bridge ordering while
    producing realistic per-simulation failure rates.

    Args:
        season: 'overall' (monsoon peak), 'dry_season', 'pre_monsoon', 'post_monsoon'
    Returns:
        dict mapping bridge_id -> calibrated failure probability
    """
    vi = pd.read_csv('../data/vulnerability_index.csv')
    col_map = {
        'overall': 'Vulnerability index',
        'dry_season': 'VI_dry_season',
        'pre_monsoon': 'VI_pre_monsoon',
        'post_monsoon': 'VI_post_monsoon',
    }
    col = col_map.get(season, 'Vulnerability index')

    # Rescale VI index to failure probability using configured bounds
    prob = FAILURE_PROB_MIN + vi[col] * (FAILURE_PROB_MAX - FAILURE_PROB_MIN)
    return dict(zip(vi['id'], prob))


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
        run_length=run_length,
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
    """Round 2: Connectivity loss criticality analysis for all 737 bridges.

    For each bridge in the network, removes it from the graph and counts how
    many origin-destination pairs lose all viable routes (broken_pairs).
    Bridges that sever the most OD connections are the most critical.

    This approach is appropriate for the near-linear N1/N2 corridor where
    ~98% of nodes are articulation points and alternative routes are scarce,
    meaning bridge removal typically severs connectivity rather than merely
    adding delay (Cats & Jenelius, 2020).

    Runs in minutes rather than hours, covering all bridges rather than a
    small subset, and produces a criticality ranking directly suitable for
    the Round 4 priority matrix.

    References:
        Jenelius, Petersen & Mattsson (2006), Transport. Res. Part A, 40(7)
        Jafino, Kwakkel & Verbraeck (2020), Transport Reviews, 40(2)
        Cats & Jenelius (2020), Transport. Res. Part A, 143
    """
    aadt_data = load_aadt_data()
    output_dir = os.path.join(OUTPUT_DIR, 'round2_bridge_removal')
    os.makedirs(output_dir, exist_ok=True)

    print(f'\n{"="*60}')
    print('ROUND 2: Connectivity Loss (all bridges)')
    print(f'{"="*60}', flush=True)

    # Build the model once to obtain the NetworkX graph and node lists.
    # No simulation is run — only the graph structure is needed.
    print('  Building model graph...', flush=True)
    model = BangladeshModel(seed=SEEDS[0], aadt_data=aadt_data)
    G = model.G

    # All source and sink node IDs (SourceSink nodes act as both).
    # These are the origin-destination endpoints trucks travel between.
    od_nodes = list(set(model.sources) | set(model.sinks))
    od_pairs = [(s, t) for s in od_nodes for t in od_nodes if s != t]

    # Load bridge metadata for output enrichment
    net_df = pd.read_csv('../data/network_data.csv')
    bridge_meta = net_df[net_df['model_type'] == 'bridge'][['id', 'road', 'name']].copy()
    bridge_meta['id'] = bridge_meta['id'].astype(int)

    # All bridge node IDs present in the graph
    bridge_ids = [b for b in bridge_meta['id'].tolist() if b in G]

    print(f'  OD nodes: {len(od_nodes)}  |  OD pairs: {len(od_pairs)}  '
          f'|  Bridges to test: {len(bridge_ids)}', flush=True)

    # Baseline: which OD pairs are connected on the intact network?
    baseline_connected = {(s, t) for s, t in od_pairs if nx.has_path(G, s, t)}
    print(f'  Baseline connected pairs: {len(baseline_connected)} / {len(od_pairs)}',
          flush=True)

    results = []
    t_start = time.time()

    for i, bridge_id in enumerate(bridge_ids):
        # Save incident edges, remove bridge node, test connectivity, restore
        saved_edges = list(G.edges(bridge_id, data=True))
        G.remove_node(bridge_id)

        broken = sum(
            1 for s, t in baseline_connected
            if s in G and t in G and not nx.has_path(G, s, t)
        )

        G.add_node(bridge_id)
        G.add_edges_from(saved_edges)

        results.append({
            'bridge_id': bridge_id,
            'broken_pairs': broken,
            'broken_pct': round(100 * broken / len(baseline_connected), 2)
            if baseline_connected else 0,
        })

        if (i + 1) % 50 == 0 or (i + 1) == len(bridge_ids):
            elapsed = time.time() - t_start
            print(f'  [{i+1}/{len(bridge_ids)}] ({elapsed:.0f}s elapsed)',
                  flush=True)

    # Merge with Round 1 ranking scores for a combined output
    df_results = pd.DataFrame(results)
    df_results = df_results.merge(bridge_meta, left_on='bridge_id',
                                  right_on='id', how='left').drop(columns='id')

    r1_ranking = pd.read_csv(
        os.path.join(OUTPUT_DIR, 'round1_baseline', 'bridge_ranking.csv'),
        usecols=['bridge_id', 'avg_trucks_crossed', 'betweenness', 'combined_score'],
    )
    df_results = df_results.merge(r1_ranking, on='bridge_id', how='left')

    df_results = df_results.sort_values('broken_pairs', ascending=False)
    df_results['criticality_rank'] = range(1, len(df_results) + 1)

    df_results.to_csv(os.path.join(output_dir, 'criticality_scores.csv'), index=False)

    elapsed = time.time() - t_start
    top = df_results.iloc[0]
    print(f'\n  Completed in {elapsed:.0f}s')
    print(f'  -> Saved to {output_dir}/criticality_scores.csv')
    print(f'  -> Most critical: bridge {int(top["bridge_id"])} '
          f'({top["road"]}, {top["name"]}) — '
          f'{int(top["broken_pairs"])} broken pairs '
          f'({top["broken_pct"]:.1f}%)', flush=True)


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
# Round 4: Priority Matrix (Criticality × Vulnerability)
# ---------------------------------------------------------------

def run_round4():
    """Round 4: Investment priority matrix — no simulation.

    Aggregates Round 3 stochastic failure outputs across all replications
    and scenarios, normalises Round 2 criticality and Round 3 vulnerability
    to [0, 1], and produces a composite priority score for every bridge.

    Three weight configurations are computed to test sensitivity:
        - Equal (default):          0.5 criticality + 0.5 vulnerability
        - Criticality-heavy:        0.7 criticality + 0.3 vulnerability
        - Vulnerability-heavy:      0.3 criticality + 0.7 vulnerability

    The monsoon peak scenario is used as the primary vulnerability reference,
    as it represents worst-case seasonal conditions for Bangladesh.

    Outputs saved to round4_combined_analysis/:
        vulnerability_summary.csv   Per-bridge aggregated Round 3 stats
                                    for all four seasonal scenarios.
        priority_matrix.csv         Merged criticality + vulnerability with
                                    normalised scores, priority ranks, and
                                    quadrant classification (A/B/C/D).

    The companion notebook round4_analysis.ipynb reads these CSVs for
    visualisation and narrative interpretation.

    References:
        Jenelius, Petersen & Mattsson (2006), Transport. Res. Part A, 40(7)
        Pregnolato, Ford, Wilkinson & Dawson (2017), Transport. Res. Part D, 55
        Thacker, Barr, Pant, Hall & Alderson (2017), Risk Analysis, 37(12)
        Frangopol & Liu (2007), Structure and Infrastructure Engineering, 3(1)
    """
    output_dir = os.path.join(OUTPUT_DIR, 'round4_combined_analysis')
    os.makedirs(output_dir, exist_ok=True)
    r3_dir = os.path.join(OUTPUT_DIR, 'round3_stochastic_failure')
    r2_path = os.path.join(OUTPUT_DIR, 'round2_bridge_removal', 'criticality_scores.csv')

    print(f'\n{"="*60}')
    print('ROUND 4: Priority Matrix (Criticality x Vulnerability)')
    print(f'{"="*60}', flush=True)

    # ------------------------------------------------------------------
    # Step 1: Aggregate Round 3 outputs across all replications
    # ------------------------------------------------------------------
    # Vulnerability metric: expected_delay = mean total_delay_min across ALL
    # replications (including zero-delay non-failure reps). This naturally
    # combines failure probability and per-failure severity into one number:
    #   expected_delay = failure_rate * mean_delay_when_failed
    # ------------------------------------------------------------------
    print('\n  Aggregating Round 3 outputs...', flush=True)

    scenarios = ['dry_season', 'pre_monsoon', 'post_monsoon', 'monsoon_peak']
    vuln_parts = []

    for scenario in scenarios:
        path = os.path.join(r3_dir, f'{scenario}_bridges.csv')
        df = pd.read_csv(path)

        agg = df.groupby('bridge_id').agg(
            name=('name', 'first'),
            road=('road', 'first'),
            condition=('condition', 'first'),
            length=('length', 'first'),
            failure_prob=('failure_prob', 'first'),
            failure_rate=('broken_down', 'mean'),
            expected_delay=('total_delay_min', 'mean'),
            mean_vehicles_delayed=('vehicles_delayed', 'mean'),
        ).reset_index()

        # Mean delay conditional on failure (0 if never failed)
        failed_only = df[df['broken_down']].groupby('bridge_id')['total_delay_min'].mean()
        agg['mean_delay_when_failed'] = agg['bridge_id'].map(failed_only).fillna(0)

        agg['scenario'] = scenario
        vuln_parts.append(agg)
        print(f'    {scenario}: {len(agg)} bridges aggregated', flush=True)

    vuln_all = pd.concat(vuln_parts, ignore_index=True)
    vuln_all.to_csv(os.path.join(output_dir, 'vulnerability_summary.csv'), index=False)
    print(f'  -> Saved vulnerability_summary.csv ({len(vuln_all)} rows)', flush=True)

    # ------------------------------------------------------------------
    # Step 2: Load Round 2 criticality scores
    # ------------------------------------------------------------------
    print('\n  Loading Round 2 criticality scores...', flush=True)
    r2 = pd.read_csv(r2_path, usecols=[
        'bridge_id', 'broken_pairs', 'broken_pct',
        'road', 'name', 'combined_score', 'criticality_rank',
    ])
    print(f'    {len(r2)} bridges loaded', flush=True)

    # ------------------------------------------------------------------
    # Step 3: Build priority matrix using monsoon_peak as reference
    # ------------------------------------------------------------------
    print('\n  Building priority matrix (monsoon_peak reference)...', flush=True)

    vuln_monsoon = vuln_all[vuln_all['scenario'] == 'monsoon_peak'][[
        'bridge_id', 'failure_rate', 'expected_delay',
        'mean_delay_when_failed', 'mean_vehicles_delayed',
    ]].copy()

    priority = r2.merge(vuln_monsoon, on='bridge_id', how='left')
    priority['failure_rate'] = priority['failure_rate'].fillna(0)
    priority['expected_delay'] = priority['expected_delay'].fillna(0)
    priority['mean_delay_when_failed'] = priority['mean_delay_when_failed'].fillna(0)
    priority['mean_vehicles_delayed'] = priority['mean_vehicles_delayed'].fillna(0)

    # Min-max normalise both dimensions to [0, 1]
    c_min, c_max = priority['broken_pairs'].min(), priority['broken_pairs'].max()
    v_min, v_max = priority['expected_delay'].min(), priority['expected_delay'].max()

    priority['norm_criticality'] = (
        (priority['broken_pairs'] - c_min) / (c_max - c_min)
        if c_max > c_min else 0
    )
    priority['norm_vulnerability'] = (
        (priority['expected_delay'] - v_min) / (v_max - v_min)
        if v_max > v_min else 0
    )

    # Three weight configurations for sensitivity analysis
    priority['priority_equal']      = (0.5 * priority['norm_criticality']
                                       + 0.5 * priority['norm_vulnerability'])
    priority['priority_crit_heavy'] = (0.7 * priority['norm_criticality']
                                       + 0.3 * priority['norm_vulnerability'])
    priority['priority_vuln_heavy'] = (0.3 * priority['norm_criticality']
                                       + 0.7 * priority['norm_vulnerability'])

    # Primary rank by equal-weight priority score
    priority = priority.sort_values('priority_equal', ascending=False)
    priority['priority_rank'] = range(1, len(priority) + 1)

    # Quadrant classification at median thresholds
    c_thresh = priority['norm_criticality'].median()
    v_thresh = priority['norm_vulnerability'].median()

    def _quadrant(row):
        hi_c = row['norm_criticality'] >= c_thresh
        hi_v = row['norm_vulnerability'] >= v_thresh
        if hi_c and hi_v:
            return 'A'   # High criticality + high vulnerability → urgent
        elif hi_c and not hi_v:
            return 'B'   # High criticality + low vulnerability → monitor
        elif not hi_c and hi_v:
            return 'C'   # Low criticality + high vulnerability → maintain
        else:
            return 'D'   # Low criticality + low vulnerability → routine

    priority['quadrant'] = priority.apply(_quadrant, axis=1)

    priority.to_csv(os.path.join(output_dir, 'priority_matrix.csv'), index=False)
    print(f'  -> Saved priority_matrix.csv ({len(priority)} bridges)', flush=True)

    # ------------------------------------------------------------------
    # Step 4: Print summary
    # ------------------------------------------------------------------
    quad_counts = priority['quadrant'].value_counts().sort_index()
    print(f'\n  Quadrant distribution (monsoon peak, equal weights):')
    for q, n in quad_counts.items():
        label = {'A': 'Urgent',  'B': 'Monitor',
                 'C': 'Maintain', 'D': 'Routine'}[q]
        print(f'    Quadrant {q} ({label}): {n} bridges')

    print(f'\n  Top 10 priority bridges (equal weights):')
    for _, row in priority.head(10).iterrows():
        print(f'    #{int(row["priority_rank"]):2d}  '
              f'{int(row["bridge_id"])} ({row["road"]}, {row["name"][:30]}) '
              f'| broken={int(row["broken_pairs"])} '
              f'| exp_delay={row["expected_delay"]:,.0f} min '
              f'| score={row["priority_equal"]:.3f} '
              f'| Q{row["quadrant"]}')

    print(f'\n  -> All outputs saved to {output_dir}/', flush=True)


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
    elif mode == 'round4':
        run_round4()
    elif mode == 'all':
        run_round1()
        run_round2()
        run_round3()
        run_round4()
    else:
        print(f'Unknown mode: {mode}')
        print('Usage: python model_run.py [round1|round2|round3|round4|all]')
        sys.exit(1)

    total_elapsed = time.time() - total_start
    print(f'\n{"="*60}')
    print(f'Completed in {total_elapsed/60:.1f} minutes')
    print(f'{"="*60}')
