# Assignment 4 — Complete Implementation Plan

## Team 14 | Option 2b: Simulation Experiments | N1/N2 Network Analysis

---

## 1. What We're Doing

We are analysing the **vulnerability and criticality** of Bangladesh's N1/N2 transport network. We build on top of our Assignment 3 Mesa/NetworkX simulation model and enhance it with:

- **Real disaster data** combined with bridge conditions to create realistic, location-specific failure probabilities
- **Degraded bridge mode** where broken bridges cause delays to passing trucks (enhanced from A3 with data-driven probabilities)
- **Deliberate bridge removal experiments** to test what happens if a bridge is completely gone (criticality testing)
- **Iterative experiments** that build on each other to identify the most critical and vulnerable bridges

The goal is to answer: **Which bridges should Bangladesh prioritise for maintenance and investment?**

---

## 2. Definitions (Grounded in Literature)

### Criticality

> The importance of a network component (road segment or bridge) to overall transport performance. A component is critical if its removal or degradation causes a significant increase in travel cost, delay, or loss of connectivity for cargo transport.

**Source**: Jafino, Kwakkel & Verbraeck (2020) — *Transport network criticality metrics: a comparative analysis and a guideline for selection*

**How we measure it**: Remove a bridge from the network → re-run simulation → measure the **change in average travel time (Δ travel time)** compared to the baseline. Larger Δ = more critical.

This follows the "change in total travel cost" metric, which Jafino et al. classify under the **utilitarian-travel cost** dimension of criticality.

### Vulnerability

> The susceptibility of a network component to failure under hazardous conditions, combined with the severity of consequences when failure occurs. A bridge is vulnerable if it has a high probability of failure AND its failure causes significant disruption.

**Source**: Berdica (2002) — *An introduction to road vulnerability: what has been done, is done and should be done*; Mattsson & Jenelius (2015) — *Vulnerability and resilience of transport systems*

**How we measure it**: Vulnerability = P(failure) × Expected consequence

Where:
- **P(failure)** is derived from bridge condition (A/B/C/D) combined with disaster exposure (earthquake, flood, rainfall, cyclone data) — this comes from the data preparation
- **Expected consequence** is the total delay caused and vehicles affected when the bridge is broken — this comes from the simulation output

The disaster data tells us **WHO is likely to fail** (the probability). The simulation tells us **HOW BAD it is when they do** (the consequence). You need both to compute vulnerability.

---

## 3. Data-Driven Failure Probabilities

### The Problem with A3

In A3, breakdown probabilities were arbitrary flat values per condition category (e.g., all D bridges get 40%). There was no justification for these numbers and no consideration of where the bridge is located.

### Our Approach: Condition × Disaster Exposure

Each bridge gets a **unique failure probability** based on two factors:

#### Factor 1: Structural Condition (from BMMS data)

Reflects the inherent structural weakness of the bridge.

| Condition | Base Probability | Meaning |
|-----------|-----------------|---------|
| A (Good) | 0.02 | Well-maintained, unlikely to fail structurally |
| B (Fair) | 0.05 | Minor issues, low structural risk |
| C (Poor) | 0.10 | Significant degradation, moderate risk |
| D (Very Poor) | 0.20 | Severe structural problems, high risk |

#### Factor 2: Hazard Exposure (from disaster data)

Reflects how much environmental stress the bridge faces based on its geographic location.

| Hazard Type | Data Source | Scoring |
|-------------|-----------|---------|
| Earthquake zone | Seismic zone map | Zone 1 = 1.0×, Zone 2 = 1.5×, Zone 3 = 2.0× |
| Rainfall intensity | Precipitation data | Low = 1.0×, Medium = 1.3×, High = 1.8× |
| Flood risk | Flood zone maps | Low = 1.0×, Medium = 1.5×, High = 2.5× |
| Cyclone exposure | Cyclone path data | Low = 1.0×, High = 1.5× |

#### Combined Formula

```
Hazard_multiplier = w1 × Earthquake_score + w2 × Rainfall_score + w3 × Flood_score + w4 × Cyclone_score

P(failure) = min(Base_condition × Hazard_multiplier, 1.0)
```

The weights (w1–w4) reflect relative importance of each hazard for Bangladesh bridges. Flooding and rainfall would likely get higher weights since these are the primary threats to bridges in Bangladesh.

#### Example

| Bridge | Condition | Base P | Flood | Rainfall | Earthquake | Cyclone | Hazard Mult. | Final P(failure) |
|--------|-----------|--------|-------|----------|------------|---------|-------------|------------------|
| Bridge A | C | 0.10 | 2.5 (high) | 1.8 (high) | 1.0 (low) | 1.0 (low) | ~2.0 | 0.20 |
| Bridge B | C | 0.10 | 1.0 (low) | 1.0 (low) | 1.0 (low) | 1.0 (low) | ~1.0 | 0.10 |
| Bridge C | D | 0.20 | 1.5 (med) | 1.3 (med) | 1.5 (med) | 1.0 (low) | ~1.4 | 0.28 |

Same condition (C) for bridges A and B, but Bridge A is 2× more likely to fail because it's in a flood-prone, heavy-rain area.

#### Implementation

Data preparation (Jupyter notebook):
1. Load bridge data from `network_data.csv` (has lat/lon for each bridge)
2. Load disaster data (GIS layers or tabular per-district scores)
3. Spatially match each bridge to its disaster exposure scores
4. Compute `failure_prob` per bridge using the formula above
5. Save as an enriched CSV that the model reads

Code change in `components.py` (~5 lines):
```python
# Instead of:  prob = breakdown_probs.get(self.condition, 0)
# Now:         prob = row['failure_prob']  (per-bridge, pre-computed)
```

---

## 4. How Bridge Failure Works in the Simulation

### Single Failure Mode: Degraded (Enhanced from A3)

We use one failure mode — **degraded** — which works the same as A3 but with better, data-driven probabilities.

**What it represents**: Bridge is damaged and causes delays — cracks, wear, structural issues from poor maintenance or weather damage.

**How it works at t=0**:
At the start of each simulation run, every bridge gets a single coin flip based on its unique `failure_prob`:

```
Roll random number against P(failure):
  → Random < P(failure):  Bridge is BROKEN → causes delays for the entire run
  → Random ≥ P(failure):  Bridge is WORKING → no delays
```

This is decided **once per replication** and does not change during the run.

**What happens when a truck reaches a broken bridge**:
1. Truck arrives at the bridge
2. A random delay is generated based on bridge length:
   - Bridge > 200m: delay = triangular(60, 120, 240) minutes
   - Bridge 50–200m: delay = uniform(45, 90) minutes
   - Bridge 10–50m: delay = uniform(15, 60) minutes
   - Bridge < 10m: delay = uniform(10, 20) minutes
3. Truck waits for the delay, then continues through the bridge on the same route

**What the simulation records for each broken bridge**:
- `total_delay_caused` — sum of all delay minutes caused to all trucks
- `vehicles_delayed` — count of trucks that were delayed
- `trucks_crossed` — total trucks that passed through (new for A4)

**Why this is enough for vulnerability analysis**:
- The disaster-weighted probability tells us WHO is likely to fail (the input)
- The simulation tells us HOW BAD it is when they do (the output)
- Two bridges with the same P(failure) can have very different consequences:
  - A broken bridge on busy N1 near Dhaka delays 180 trucks → high consequence
  - A broken bridge on quiet N207 delays 30 trucks → low consequence
- Vulnerability = P(failure) × E(consequence) — you need the simulation to get the consequence part

### Bridge Removal: Only in Round 2 (Criticality Experiments)

Bridge removal (completely removing a bridge from the NetworkX graph) is **not** a failure mode in the regular simulation. It is a **controlled experiment** done separately in Round 2.

In Round 2, we deliberately remove one bridge at a time from the graph to answer: "What if this bridge were completely gone?" This forces trucks to reroute and reveals which bridges the network depends on most.

This is a separate experiment script — not part of the stochastic failure model. See Section 8 (Round 2) for details.

---

## 5. Rerouting in Round 2 Experiments

### The Key Insight

When we remove a bridge from the NetworkX graph in Round 2, trucks automatically reroute because `nx.shortest_path()` will find alternative paths that avoid the missing bridge. This is how we measure criticality.

### Implementation

In `model.py`, add a method for Round 2 experiments (~10 lines):

```python
def remove_bridge(self, bridge_id):
    """Remove a bridge from the network graph for criticality testing"""
    if bridge_id in self.G:
        # Save edges so we can restore later
        self.removed_bridges[bridge_id] = list(self.G.edges(bridge_id, data=True))
        self.G.remove_node(bridge_id)
        # Clear route cache — forces recalculation for all trucks
        self.path_ids_dict.clear()

def restore_bridge(self, bridge_id):
    """Restore a previously removed bridge"""
    if bridge_id in self.removed_bridges:
        self.G.add_node(bridge_id)
        self.G.add_edges_from(self.removed_bridges[bridge_id])
        del self.removed_bridges[bridge_id]
        self.path_ids_dict.clear()
```

After removal:
- New trucks call `nx.shortest_path()` → NetworkX returns a path avoiding the removed bridge
- If no alternative path exists, `nx.NetworkXNoPath` is caught → truck can't reach destination (stranded)
- Stranded trucks are counted as a metric

### Computational Cost: Negligible

- NetworkX shortest path on ~4,000 nodes: **~1 millisecond**
- Route cache means only the first truck per origin-destination pair computes the path
- No performance impact during the simulation run
- Round 2 with 30 bridges × 10 replications = 300 runs × ~30 seconds each ≈ 2-3 hours total

---

## 6. Per-Source Truck Generation (from RMMS Traffic Data)

### The Problem

In A3, every source generates 1 truck every 5 minutes — same rate everywhere. In reality, N1 near Dhaka is way busier than a side road in rural Bangladesh.

### Our Approach

Use RMMS AADT (Annual Average Daily Traffic) data for trucks to set per-source generation rates:

```
generation_frequency (minutes per truck) = (24 × 60) / truck_AADT_at_that_source
```

Example:
- Source on N1 near Dhaka: truck AADT = 2,000 → 1 truck every 0.72 min (~1 per tick)
- Source on N207 rural: truck AADT = 200 → 1 truck every 7.2 min

### Implementation

Code change in `components.py` Source class (~10 lines):
- Change `generation_frequency` from a class attribute (same for all) to an instance attribute (per source)
- Read the frequency from the CSV or pass it as a parameter during model generation

---

## 7. Enhanced Data Collection

### New Metrics to Track

In addition to A3's existing trip data and bridge data, we add:

| Metric | What It Measures | Where Tracked |
|--------|-----------------|---------------|
| Trucks per bridge | How many trucks cross each bridge | `Bridge.trucks_crossed` counter |
| Stranded trucks (Round 2 only) | Trucks that couldn't reach destination after bridge removal | `Model.stranded_count` |
| Per-bridge Δ travel time | Impact of bridge removal on travel time | Round 2 experiment output |

### Implementation

Tiny additions to existing classes (~10 lines total):
- Add `trucks_crossed` counter to `Bridge` class
- Increment it in `Vehicle.drive_to_next()` when passing a bridge
- Add stranded truck handling in `Vehicle.set_path()` for Round 2

---

## 8. Experiment Design — Four Iterative Rounds

The rubric specifically asks for an **"explorative and iterative process"** — each round teaches us something that shapes the next round.

### Round 1: Baseline — "What does normal look like?"

**Setup**: All bridges functional (no breakdowns). Per-source truck generation calibrated from RMMS data.
**Runs**: 10 replications with different seeds.
**What we measure**: Traffic flow per bridge (trucks_crossed), average travel time, route distributions.
**What we learn**: Which bridges carry the most truck traffic → initial criticality ranking by volume.
**What informs next round**: We now know the top ~20-30 most-used bridges to focus on in Round 2.

### Round 2: Bridge Removal — "What if this bridge is gone?" (Criticality)

**Purpose**: This is a **controlled, hypothetical experiment** — we deliberately remove one bridge at a time to measure how much the network depends on it.

**Setup**: For each of the top bridges from Round 1, completely remove it from the NetworkX graph and re-run the simulation. All other bridges are functional. Trucks are forced to reroute.
**Runs**: Top 20-30 bridges × 10 replications = 200-300 runs (~2-3 hours total).
**What we measure**:
- Δ average travel time (compared to Round 1 baseline)
- Number of stranded trucks (no alternative route available)
- Which alternative routes trucks take

**What we learn**: The TRUE criticality of each bridge. Some high-traffic bridges have good alternatives (low criticality despite high traffic). Others are irreplaceable chokepoints (high criticality).

**Two Criticality Metrics (reported separately, not merged)**:

| Metric | What It Captures | Unit |
|--------|-----------------|------|
| **Δ average travel time** (primary) | How much longer trips take when bridge is removed — measures efficiency loss | Minutes |
| **Stranded trucks** (supplementary) | How many trucks can't reach their destination at all — measures connectivity loss | Count |

We keep these as **two separate metrics** rather than combining into one formula, because they measure fundamentally different things (inconvenience vs impossibility). Merging them would require arbitrary weighting that's hard to justify.

**How to present**: Rank bridges by Δ travel time (primary metric), show stranded trucks as an additional column in the results table. In the Round 4 scatter plot, use dot size or color to indicate stranding.

Example results table:

| Rank | Bridge | Road | Δ Avg Travel Time | Stranded Trucks |
|------|--------|------|-------------------|-----------------|
| 1 | Bridge X | N1 | +85 min | 12 |
| 2 | Bridge Y | N2 | +62 min | 0 |
| 3 | Bridge Z | N1 | +45 min | 8 |

This tells a richer story: Bridge X causes delays AND disconnects the network. Bridge Y causes delays but alternatives exist (zero stranding). Bridge Z has moderate delays but also causes disconnection — arguably more critical than the delays suggest.

**Key insight**: This is different from Round 3. Here we ask "What IF this bridge were gone?" — a worst-case stress test. Round 3 asks "What actually happens under realistic failure conditions?"

### Round 3: Stochastic Failure — "What happens under realistic disaster conditions?" (Vulnerability)

**Purpose**: This is a **probabilistic, realistic simulation** — bridges fail (degrade) based on their data-driven failure probabilities.

**Setup**: Use disaster-weighted per-bridge failure probabilities. Bridges that fail become degraded (cause delays). Calibrated truck generation.
**Runs**: Multiple scenarios × 10 replications.

**Scenarios**:
- Scenario 0: No failures (same as Round 1 baseline)
- Scenario 1: Monsoon season (high rainfall + flood multipliers active)
- Scenario 2: Cyclone event (cyclone multiplier active for coastal bridges)
- Scenario 3: Earthquake event (earthquake multiplier active for seismic zone bridges)
- Scenario 4: Combined worst-case (all hazard multipliers at maximum)

Each scenario uses different hazard multipliers to compute the per-bridge failure probabilities, reflecting different types of natural disasters.

**What we measure per bridge (across replications)**:
- How often it breaks down (failure frequency out of 10 replications)
- Total delay caused when broken
- Number of vehicles affected when broken

**What we learn**: Vulnerability score per bridge = P(failure) × E(delay caused when broken).

Two bridges with similar failure probabilities can have very different vulnerability scores:
- Bridge X (busy road, long bridge): P=0.56, avg delay when broken=4,200 min → Vulnerability=2,352
- Bridge Z (quiet road, short bridge): P=0.50, avg delay when broken=600 min → Vulnerability=300

Bridge X is ~8× more vulnerable despite similar failure probability — **you can only discover this through simulation**.

### Round 4: Combined Analysis — "Which bridges need attention first?"

**Setup**: No new simulation runs. Pure data analysis combining Round 2 and Round 3 results.
**What we create**:

A **Criticality × Vulnerability scatter plot**:

```
             High Vulnerability
                   |
    WATCH LIST     |    🚨 TOP PRIORITY
    (fragile but   |    (fragile AND critical)
     not critical) |
                   |
    ───────────────┼───────────────
                   |
    LOW PRIORITY   |    MAINTAIN WELL
    (strong and    |    (strong but critical —
     not critical) |     keep it that way)
                   |
             Low Vulnerability
    Low Criticality ──────── High Criticality
```

Bridges in the **top-right quadrant** are the highest priority: they're both important to the network AND likely to cause problems. This is the key policy-relevant output.

**Also create**: Separate top-10 lists for most critical (by Δ travel time, with stranded trucks shown alongside) and most vulnerable bridges.

---

## 9. Visualisations

| # | Visualisation | Type | What It Shows |
|---|-------------|------|--------------|
| 1 | Traffic flow map | Geographic (geopandas) | Road segments colored by truck volume from Round 1 |
| 2 | Bridge condition + disaster exposure map | Geographic | Bridges colored by failure probability (condition × hazard) |
| 3 | Top-10 critical bridges | Bar chart | Ranked by Δ travel time when removed (Round 2) |
| 4 | Top-10 vulnerable bridges | Bar chart | Ranked by vulnerability score P(fail) × E(delay) (Round 3) |
| 5 | Criticality × Vulnerability | Scatter plot | All bridges, quadrant analysis, dot size/color = stranded trucks (Round 4) |
| 6 | Travel time distributions | Boxplots | Across disaster scenarios and replications |
| 7 | Before/after comparison | Side-by-side bar charts | Network performance with vs without key bridges |
| 8 | Iterative process diagram | Flow chart | How each round informed the next (for the report) |

Tools: Python with matplotlib, seaborn, geopandas (for maps), NetworkX (for schematic graph views).

---

## 10. Code Changes Summary

| Change | File | Lines of Code | Effort |
|--------|------|--------------|--------|
| Per-bridge failure probability from CSV | `components.py` | ~5 lines | Small |
| Bridge removal + restoration methods | `model.py` | ~15 lines | Small |
| Per-source truck generation rates | `components.py` | ~10 lines | Small |
| Per-bridge traffic counter (`trucks_crossed`) | `components.py` | ~3 lines | Tiny |
| Stranded truck handling (Round 2) | `components.py` + `model.py` | ~10 lines | Small |
| Round 2 bridge removal experiment loop | `model_run.py` | ~30 lines | Small |
| Round 3 disaster scenario definitions | `model_run.py` | ~20 lines | Small |
| **Total new/modified code** | | **~60 lines** | **Very feasible** |

---

## 11. Data Requirements

| Data | Source | Format | Status |
|------|--------|--------|--------|
| Road network + bridges | `network_data.csv` from A3 | CSV | ✅ Have it |
| Bridge conditions & details | `BMMS_overview.xlsx` | Excel | ✅ Have it |
| GIS layers (roads, admin boundaries) | `data/gis/` from A3 | Shapefiles | ✅ Have it |
| Truck AADT per road/chainage | RMMS dataset (course materials) | HTML/tables | ⚠️ Need to extract |
| Earthquake zone data | Team member's data | TBD | ⚠️ She has it |
| Rainfall intensity data | Team member's data | TBD | ⚠️ She has it |
| Flood risk zone data | Team member's data | TBD | ⚠️ She has it |
| Cyclone exposure data | Team member's data | TBD | ⚠️ She has it |

---

## 12. Project Structure

```
EPA133a-G14-A4/
├── README.md                    # Instructions for TAs to replicate results
├── requirements.txt             # Python dependencies
├── data/
│   ├── raw/                     # Original unmodified data files
│   │   ├── network_data.csv     # Road network (from A3)
│   │   ├── BMMS_overview.xlsx   # Bridge data
│   │   ├── disaster_data/       # Earthquake, flood, rainfall, cyclone data
│   │   └── traffic_data/        # RMMS AADT data
│   └── processed/
│       ├── enriched_network.csv # network_data + failure_prob + generation_freq
│       └── disaster_scores.csv  # Per-bridge hazard multipliers
├── model/
│   ├── model.py                 # Enhanced BangladeshModel
│   ├── components.py            # Enhanced agents (data-driven probs, per-source gen)
│   ├── model_run.py             # Experiment runner (4 rounds)
│   ├── model_viz.py             # Mesa visualisation (from A3)
│   └── ContinuousSpace/        # Visualisation module (from A3)
├── notebook/
│   ├── 01_data_preparation.ipynb    # Merge disaster + bridge + traffic data
│   ├── 02_experiment_analysis.ipynb # Analyse results from Rounds 1-4
│   └── 03_visualisations.ipynb      # Create all figures
├── experiment/                  # Output CSVs from all experiment rounds
│   ├── round1_baseline/
│   ├── round2_bridge_removal/
│   ├── round3_stochastic_failure/
│   └── round4_combined_analysis/
├── img/                         # Selected visualisation images for report
└── report/
    └── EPA133a_G14_A4_Report.pdf
```

---

## 13. Suggested Team Division

| Member | Responsibility | Deliverable |
|--------|---------------|-------------|
| **Member A** | Literature review + definitions + report writing | Report sections 1-3, final editing |
| **Member B** | Data preparation: merge disaster data with bridge data, extract RMMS traffic, compute failure probabilities and generation rates | `01_data_preparation.ipynb`, `enriched_network.csv` |
| **Member C** | Model adaptation: per-bridge probabilities, bridge removal methods, per-source generation, enhanced data collection | Updated `model.py`, `components.py`, `model_run.py` |
| **Member D** | Run experiments (Rounds 1-4), analysis, create all visualisations | `02_experiment_analysis.ipynb`, `03_visualisations.ipynb`, all figures |

All members contribute to report review, reflection, and the acknowledgement section.

---

## 14. Rubric Alignment

| Rubric Criterion | How We Address It |
|-----------------|-------------------|
| Clear definitions grounded in literature | Jafino et al. (2020) for criticality, Berdica (2002) for vulnerability |
| Operationalisation well-argued for | Multi-factor probability (condition × disaster), Δ travel cost metric |
| Assumptions described | Hazard weights, base probabilities, generation rate formula |
| Probabilities well-argued & referenced | Real disaster data + structural condition → per-bridge justified probabilities |
| Model runs without errors | Incremental changes on working A3 model, ~60 lines of new code |
| Explorative & iterative experimentation | 4 rounds, each building on the previous, described in report |
| Assumptions for traffic flow data well-argued | RMMS AADT → generation frequency conversion clearly explained |
| Delays and breakdowns explained & well-argued | Data-driven probabilities with clear condition × hazard justification |
| Resulting rank order critically examined | Top-10 lists + criticality×vulnerability scatter + discussion of limitations |
| Different seeds for replications | 10 replications per scenario, inherited from A3 |
| Code well-structured & documented | Modular changes, clear docstrings, Jupyter notebooks |
| Visuals with non-trivial insights | 8 targeted visualisations, each with specific analytical purpose |
| README for replication | Step-by-step instructions in README.md |
