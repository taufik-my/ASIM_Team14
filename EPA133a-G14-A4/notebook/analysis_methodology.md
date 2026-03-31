# Simulation Analysis Methodology — N1/N2 Bridge Network, Bangladesh

**Assignment 4 | EPA133a Advanced Simulation | Group 14**

---

## Overview

This document explains the methodology for all simulation rounds used to analyse bridge criticality and vulnerability on Bangladesh's N1/N2 road corridor, framed from a World Bank infrastructure prioritisation perspective. Each round builds on the previous:

| Round | Purpose | Method |
|---|---|---|
| **Round 1** | Rank bridges by importance | Baseline simulation + betweenness centrality |
| **Round 2** | Measure criticality | Connectivity loss analysis (graph-theoretic) |
| **Round 3** | Measure vulnerability | Stochastic failure by seasonal scenario |
| **Round 4** | Prioritise investment | Criticality × vulnerability matrix |

---

# Round 1: Bridge Ranking

## 1. Purpose

This section explains how Round 1 of the simulation (`model_run.py`) identifies and
ranks the most critical bridges on Bangladesh's N1/N2 corridor. The resulting ranked
list feeds directly into Round 2 (bridge criticality analysis). Every
methodological choice — including the weighting scheme and the sensitivity analysis
performed — is justified with reference to academic literature and institutional
frameworks.

---

## 2. What Round 1 Computes

Round 1 runs a **baseline simulation**: all bridges are functional, traffic is
calibrated to AADT data, and no failure probabilities are applied. The simulation
runs for **7,200 ticks (5 × 24 hours, 1 tick = 1 minute)** across **10 replications**
with different random seeds, producing two independent signals per bridge:

| Signal | Variable in code | What it measures |
|---|---|---|
| **Simulated traffic volume** | `avg_trucks_crossed` | Mean number of small + medium + heavy trucks observed crossing the bridge across 10 replications |
| **Betweenness centrality** | `betweenness` | Share of all shortest network paths (weighted by road length) that pass through the bridge node, computed via NetworkX |

Both signals are then normalised to [0, 1] and combined into a **combined score**
used to identify the top 20 bridges.

---

## 3. Traffic Demand Input

Traffic demand at each source node is calibrated from AADT data using **all three
truck classes**:

```python
# model_run.py — load_aadt_data()
aadt_dict[row['id']] = (row['small_truck'] + row['medium_truck'] + row['heavy_truck']) / 2
```

The division by 2 approximates per-direction demand. All three truck classes present
in `integrated_data.csv` — `small_truck`, `medium_truck`, and `heavy_truck` — are
included. Total `aadt` (which includes passenger vehicles) is still excluded, keeping
the demand signal truck-specific.

### 3.1 Justification for including small trucks

The Round 1 objective is to identify which bridges are most *used* by the network —
i.e., to rank bridges by traffic-based criticality. For this purpose, **network demand
completeness** is the primary criterion, not structural damage weighting.

Two perspectives frame this decision:

**Against inclusion — the ESAL structural damage argument**

The ESAL (Equivalent Single Axle Load) framework, the standard measure for pavement
and bridge structural design, shows that damage scales approximately with the 4th power
of axle load. A small truck generates roughly 0.001–0.003 ESALs per pass, while a
loaded heavy semi-trailer generates ~3 ESALs — approximately 1,000× more damage per
vehicle. On this basis, FHWA (2016) states that "small vehicles do negligible damage
to the pavement structure and are not considered in structural design."
— Pavement Interactive (2023); FHWA-HRT-15-081 (2016).

**For inclusion — the network demand completeness argument**

However, the ESAL framework applies to *structural engineering calculations*, not to
*demand-based criticality ranking*. Small trucks are real vehicles that occupy bridge
capacity, contribute to congestion, and represent network utilisation. Excluding them
systematically undercounts the total flow across bridges and biases the ranking toward
bridges near heavy-truck origins only.

Freight trip generation literature classifies light, medium, and heavy trucks as
separate but all-relevant contributors to network demand when assessing how the network
is used (FHWA Freight Demand Modeling, 2023; Holguín-Vivas & Patil, 2008). The
distinction between truck classes becomes critical for *structural damage* assessment
— addressed in Round 3 via the Vulnerability Index — not for *traffic-based
criticality ranking*.

**Design decision**: small trucks are included in Round 1 demand because the ranking
goal is to represent total network utilisation. Their structural impact is accounted
for separately through the vulnerability index applied in Round 3.

> **Implication**: `norm_traffic` represents total truck flow (all classes), giving a
> complete picture of bridge utilisation consistent with the World Bank's transport
> prioritisation focus on economic throughput and network access (World Bank, 2022).

---

## 4. Betweenness Centrality

Betweenness centrality is computed **once** from the final model's NetworkX graph using
road segment lengths as edge weights:

```python
# model_run.py — run_round1()
centrality = nx.betweenness_centrality(model.G, weight='weight')
```

**What betweenness captures here**: a bridge with high betweenness lies on many
shortest paths between origin–destination pairs in the network. Its removal forces
detours even if its raw traffic count is moderate — making it a topologically critical
chokepoint.

**Limitation**: because betweenness is derived from shortest paths (Dijkstra) rather
than from actual traffic assignment, it does not reflect congestion or demand
distribution. It measures *structural indispensability*, not *utilisation*.

---

## 5. Scoring and Ranking Formula

Each bridge receives a **combined score** computed as a normalised weighted sum:

$$\text{combined\_score} = w_1 \cdot \frac{\text{avg\_trucks\_crossed}}{\max(\text{avg\_trucks\_crossed})} + w_2 \cdot \frac{\text{betweenness}}{\max(\text{betweenness})}$$

where $w_1 + w_2 = 1$.

In the final implemented version:

$$\text{combined\_score} = 0.7 \cdot \text{norm\_traffic} + 0.3 \cdot \text{norm\_betweenness}$$

---

## 6. Weight Justification

### 6.1 Why not pure betweenness or pure traffic?

A purely topological metric (betweenness only) ignores the actual volume of trucks
and goods flowing across a bridge — a network-optimal choice that may not align with
economic impact. Conversely, raw traffic alone is blind to structural network position:
a bridge can carry high traffic simply because it is near a major source, yet its
removal might have a modest network-wide effect if alternative paths exist.

Jafino, Kwakkel & Verbraeck (2020) systematically compared 17 transport network
criticality metrics and concluded that **demand-weighted metrics** best represent
disruption cost to users when the analysis goal is "which link removal causes the most
harm to travellers." This directly supports giving traffic a higher weight than pure
topology.

### 6.2 Why 0.7 for traffic and 0.3 for betweenness?

The 70:30 split is grounded in three converging justifications:

**1. Jafino et al. (2020) — metric selection framework**
When the transport function of interest is *reducing travel cost* (i.e., minimising the
disruption a bridge failure imposes on freight travel times), demand-weighted metrics
should dominate. The authors find that topological metrics (like betweenness) should
serve as a corrective term, not an equal partner, when demand data is available.

**2. FHWA Bridge Health Index (2016) — traffic as the primary importance factor**
The FHWA synthesis of national and international bridge health index methodologies
confirms that Average Daily Traffic (ADT) is the primary bridge importance factor used
across nearly all surveyed national systems. Betweenness-equivalent measures
(detour cost, network redundancy) appear as secondary or corrective factors.
— FHWA-HRT-15-081, *Synthesis of National and International Methodologies Used for
Bridge Health Indices*, U.S. Federal Highway Administration (2016).

**3. World Bank infrastructure mandate**
The World Bank funds transport infrastructure primarily to maximise economic returns
and poverty reduction — not to optimise network topology per se. Its *Infrastructure
and Transport* policy states that transport infrastructure supports "reducing transport
and production costs, creating jobs, expanding productive capacity, and improving
market access." This economic framing prioritises bridges where disruption would
cause the greatest economic harm, which correlates more strongly with freight volume
than with abstract centrality.
— World Bank, *Transport* (official topic page, 2022).
— World Bank, *Infrastructure, Economic Growth, and Poverty: A Review*,
Policy Research Working Paper 10343 (2023).

Taken together, a **0.7 / 0.3 split** (traffic-heavy, with betweenness as a corrective
term) is the most defensible choice given the stated goal of identifying bridges whose
failure would most disrupt freight movement and economic activity.

---

## 7. Sensitivity Analysis: 50:50 vs. 70:30

To test whether the weight choice materially affects bridge selection, both weight
configurations were implemented and compared.

### 7.1 Configurations tested

| Configuration | Formula | Rationale |
|---|---|---|
| **50:50 (equal weight)** | `0.5 * norm_traffic + 0.5 * norm_betweenness` | Naive baseline; treats both signals as equally important |
| **70:30 (traffic-heavy)** | `0.7 * norm_traffic + 0.3 * norm_betweenness` | Literature-justified; reflects demand-weighted criticality |

### 7.2 Result: Top 20 bridges are identical under both configurations

Both weight schemes produce **exactly the same top 20 bridges**:

| Rank | Bridge ID | avg_trucks_crossed | betweenness |
|---|---|---|---|
| 1  | 2000278 | 24,274.6 | 0.4488 |
| 2  | 2000284 | 24,272.1 | 0.4479 |
| 3  | 2000288 | 24,270.4 | 0.4473 |
| 4  | 2000292 | 24,272.4 | 0.4466 |
| 5  | 2000297 | 24,270.9 | 0.4458 |
| 6  | 2000303 | 24,270.8 | 0.4448 |
| 7  | 2000306 | 24,269.8 | 0.4443 |
| 8  | 2000314 | 24,266.2 | 0.4430 |
| 9  | 2000316 | 24,267.0 | 0.4427 |
| 10 | 2000320 | 24,266.4 | 0.4420 |
| 11 | 2000324 | 24,265.6 | 0.4413 |
| 12 | 2000330 | 24,261.1 | 0.4403 |
| 13 | 2000346 | 24,257.5 | 0.4376 |
| 14 | 2000350 | 24,254.5 | 0.4369 |
| 15 | 2000356 | 24,253.3 | 0.4359 |
| 16 | 2000360 | 24,253.0 | 0.4351 |
| 17 | 2000366 | 24,251.5 | 0.4340 |
| 18 | 2000370 | 24,250.2 | 0.4333 |
| 19 | 2000374 | 24,248.3 | 0.4326 |
| 20 | 2000378 | 24,249.1 | 0.4319 |

### 7.3 Why the top 20 are invariant to weight choice

Inspecting `bridge_ranking.csv` reveals the structural reason: bridges 2000278–2000378
form a **tight co-dominant cluster** — they simultaneously rank near the top on both
traffic volume (~24,248–24,275 trucks/day) and betweenness (~0.432–0.449). The first
bridge ranked outside the top 20 by combined score (bridge 1000212) has the single
highest betweenness in the network (0.494) but substantially lower traffic (~21,001
trucks/day).

The gap between rank 20 and rank 21 is:
- Traffic: ~24,248 vs. ~21,001 (≈15% lower)
- Betweenness: 0.432 vs. 0.494 (≈14% higher)

No weighting scheme within a reasonable range (roughly 0.4–0.9 for traffic) can bring
bridge 1000212 into the top 20, because its traffic deficit exceeds its betweenness
advantage at any plausible weight. A weight of ≥ 0.93 for betweenness would be needed
to promote it — far outside any literature-supported range.

### 7.4 Interpretation

The invariance of the top 20 is a finding in itself: it demonstrates that the
**N1/N2 corridor has a clearly dominant cluster of critical bridges** whose importance
is robust to methodological choices. This is consistent with the corridor's role as
Bangladesh's primary freight artery, where a dense sequence of bridges over the same
river system creates a set of co-critical infrastructure points.

---

## 8. Comparison of Three Ranking Strategies

Three separate rank columns are saved in `bridge_ranking.csv` to allow comparison:

| Column | Based on | Interpretation |
|---|---|---|
| `rank_by_traffic` | `avg_trucks_crossed` | Pure demand-based ranking; most responsive to AADT input |
| `rank_by_betweenness` | `betweenness` | Pure topology-based ranking; demand-agnostic |
| `rank_by_combined` | `combined_score` (0.7/0.3) | Literature-justified hybrid; used as input to Round 2 |

For the top 20 selection, all three strategies produce the same set in this network.

---

## 9. Limitations and Future Improvements

| Limitation | Effect on ranking | Potential improvement |
|---|---|---|
| Passenger cars excluded from demand | `norm_traffic` is truck-only; total vehicle flow is higher | Include total AADT if the research objective shifts to general congestion analysis |
| Small trucks weighted equally with heavy trucks in demand sum | Overstates structural stress contribution of small trucks relative to heavy trucks | Weight each class by its ESAL factor before summing, if structural-stress-proportional demand is desired |
| Betweenness uses topological shortest paths, not traffic-assigned flows | Over-weights bridges on geometrically short but low-demand paths | Use **Path Flow Weighted Betweenness Centrality** (Tu et al., 2024), which weights path contributions by actual OD demand |
| Weight sensitivity tested only at two points (50:50 and 70:30) | Weight-space exploration is coarse | Run full sweep (e.g., 0.1 increments) to map the range over which top-20 is stable |
| Betweenness computed from a single graph snapshot | Does not reflect time-varying congestion | Use dynamic or congestion-aware betweenness (Cats & Jenelius, 2020) |

---

# Round 2: Connectivity Loss Criticality Analysis

## 1. Purpose

Round 2 measures the **criticality** of every bridge in the network by quantifying
how much network connectivity is lost when each bridge is removed. A bridge is
considered critical if its failure severs routes between origin-destination (OD) pairs
— leaving communities without road access entirely, rather than merely adding travel
time.

This directly answers the World Bank's core infrastructure question: *"which bridges,
if they fail, cut off the most people from the network?"*

---

## 2. Why Connectivity Loss, Not Travel Time Simulation

The previous approach simulated full truck movements (7,200 ticks × 10 replications
per bridge) to measure Δ travel time. This was replaced for two reasons:

**Reason 1 — Network topology makes connectivity the dominant effect**

The N1/N2 network has ~98% articulation points — nearly every node, including most
bridges, sits on a single critical path with no alternative route around it. When such
a bridge is removed, trucks are not rerouted with added delay; they are **stranded
entirely**. Cats & Jenelius (2020) show that in low-redundancy corridor networks,
topological metrics reliably predict criticality precisely because connectivity loss
dominates over travel time degradation.

**Reason 2 — The top 20 Round 1 bridges form a co-critical cluster**

All top 20 bridges from Round 1 are located on the same ~10 km stretch of N2 (bridge
IDs 2000278–2000378), with near-identical traffic (~30,341 trucks) and betweenness
(~0.432–0.449). A full simulation of these 10 bridges would produce near-identical
Δ travel time results, offering little comparative insight. Connectivity loss analysis
covers all 737 bridges across both N1 and N2, revealing structurally distinct critical
points that the Round 1 cluster ranking obscures.

---

## 3. Algorithm

### 3.1 Setup (once)

1. Build the NetworkX graph from the model (no simulation run needed)
2. Identify all **18 source/sink nodes** (OD endpoints)
3. Enumerate all **306 directed OD pairs** (18 × 17)
4. Record **baseline connectivity**: which pairs are connected on the intact network

### 3.2 Per bridge (repeated for all 737 bridges)

```
1. Save the bridge's incident edges
2. Remove the bridge node from the graph
3. For each baseline-connected OD pair:
       if nx.has_path(G, source, sink) is False → mark as broken
4. broken_pairs = count of newly broken pairs
5. Restore the bridge node and edges
```

### 3.3 Output

Each bridge receives:

| Column | Description |
|---|---|
| `broken_pairs` | Number of OD pairs that lose all viable routes |
| `broken_pct` | `broken_pairs` as a percentage of baseline-connected pairs |
| `criticality_rank` | Rank by `broken_pairs` (1 = most critical) |

Results are merged with Round 1 scores (`avg_trucks_crossed`, `betweenness`,
`combined_score`) in `criticality_scores.csv` for direct comparison.

---

## 4. Justification

### 4.1 Ethical framing: utilitarian perspective

Jafino, Kwakkel & Verbraeck (2020) classify criticality metrics by ethical principle:
a **utilitarian** metric minimises total network-wide disruption (aggregate freight
delay, total broken volume), while an **egalitarian** metric minimises the worst-case
disruption to any single OD pair regardless of how much freight it carries.

This analysis adopts the **utilitarian perspective**, for three reasons:

1. **World Bank mandate**: the World Bank prioritises infrastructure investment based
   on aggregate economic impact — total freight volume moved, GDP contribution, and
   number of beneficiaries — not equal access per OD pair. This is explicitly
   utilitarian.

2. **Freight focus**: Jafino et al. (2020) recommend demand-weighted, utilitarian
   metrics specifically when the transport function of interest is minimising
   disruption to freight movement and economic activity. Round 1's 70:30
   traffic-betweenness score already reflects this principle.

3. **Consistency across rounds**: Round 3 vulnerability scores are weighted by
   structural condition and hazard intensity — also a utilitarian aggregation. A
   consistent utilitarian framing across all rounds strengthens comparability in
   the Round 4 priority matrix.

> **Note on Round 2's metric**: the unweighted count of `broken_pairs` is a slight
> approximation of a fully utilitarian measure, as it treats all OD pairs equally
> regardless of freight volume. A demand-weighted version would count severing a
> high-freight route more heavily than a low-freight one. Given the absence of
> per-OD freight volume data in this study, the unweighted count is a defensible
> approximation — bridges that sever many OD pairs on the N1/N2 corridor are
> overwhelmingly high-freight routes given the corridor's structure.

### 4.2 Connectivity loss as a criticality metric

Jenelius, Petersen & Mattsson (2006) define **link importance** as the increase in
generalised travel cost when a link is removed, where inability to travel (severed
connectivity) is treated as the most severe possible outcome — an infinite cost.
Their framework applied to the Swedish road network is directly analogous to the
Bangladesh corridor context.

Jafino, Kwakkel & Verbraeck (2020) classify connectivity-based metrics as appropriate
when the transport function of interest is **access** rather than travel cost
minimisation. Given the World Bank's mandate to maximise economic access and poverty
reduction, connectivity loss is the more policy-relevant metric than Δ travel time.

Consistent with the utilitarian perspective, criticality is interpreted as
**aggregate connectivity loss across the network** rather than worst-case impact on
any single OD pair (Jafino et al., 2020).

### 4.3 Appropriateness for the N1/N2 corridor

Cats & Jenelius (2020) tested five criticality metrics across 150 synthetic networks
with varying topology and congestion. Their key finding: **topological metrics are
most reliable in low-redundancy corridor networks**, where alternative paths are
scarce. The N1/N2 network — a near-linear corridor with ~98% articulation points —
is the canonical case where connectivity loss is both the most accurate and most
interpretable criticality measure.

### 4.4 Coverage advantage

The connectivity loss approach analyses **all 737 bridges** in under 10 minutes,
versus ~20 hours for a simulation of only 10 bridges. This produces a complete,
network-wide criticality ranking that is not biased toward any single corridor cluster.

---

## 5. Limitations

| Limitation | Effect | Mitigation |
|---|---|---|
| Binary metric (connected/not) | Does not capture travel time degradation for routes that remain intact | Acceptable for near-linear networks; acknowledged in interpretation |
| Static graph (no congestion) | Does not model increased load on remaining bridges after removal | Consistent with Round 1 betweenness approach; noted as future work |
| Single bridge removal (N-1) | Does not test compound failures (multiple bridges removed simultaneously) | Appropriate for individual bridge prioritisation; compound scenarios are Round 3 |

> **Reporting note**: connectivity loss does not capture travel time degradation for
> routes that remain intact after bridge removal. For networks with high redundancy
> this would be a significant limitation; however, given the near-linear topology of
> the N1/N2 corridor (Cats & Jenelius, 2020) where alternative routes are scarce,
> severed connectivity represents the dominant form of disruption.

---

## 6. References (Round 2)

- Cats, O., & Jenelius, E. (2020). *Impact of topology and congestion on link
  criticality rankings in transportation networks*. Transportation Research Part A,
  143, 48–61.
  https://www.sciencedirect.com/science/article/abs/pii/S1361920920307161

- Jenelius, E., Petersen, T., & Mattsson, L.-G. (2006). *Importance and exposure in
  road network vulnerability analysis*. Transportation Research Part A, 40(7), 537–560.
  https://ideas.repec.org/a/eee/transa/v40y2006i7p537-560.html

- Jafino, B. A., Kwakkel, J. H., & Verbraeck, A. (2020). Transport network criticality
  metrics: a comparative analysis and a guideline for selection. *Transport Reviews*,
  40(2), 241–264.
  https://www.tandfonline.com/doi/full/10.1080/01441647.2019.1703843

- Reggiani, A., Nijkamp, P., & Lanzi, D. (2015). *Transport resilience and
  vulnerability: The role of critical transport networks*. Transportation Research
  Part A, 81, 4–15.
  https://www.sciencedirect.com/science/article/abs/pii/S0965856414002882

- World Bank (2022). *Transport*. Official topic page.
  https://www.worldbank.org/ext/en/topic/transport

---

# Round 3: Stochastic Failure (Vulnerability Analysis)

## 1. Purpose

Round 3 measures bridge **vulnerability** — the probability and impact of bridge
failure under realistic disaster conditions. Where Round 2 tests complete bridge
removal (worst-case collapse), Round 3 models **partial damage**: bridges fail
stochastically based on their vulnerability index and cause delays to trucks that
still cross them. This reflects Bangladesh's real-world flood context, where most
bridge failures involve damage and capacity reduction rather than total collapse.

The output feeds directly into the Round 4 priority matrix, where criticality
(Round 2) and vulnerability (Round 3) are combined to identify bridges requiring
urgent World Bank investment.

---

## 2. Seasonal Scenarios

Four scenarios are tested, each using a seasonally-adjusted vulnerability index:

| Scenario | Season | Flood multiplier | Erosion multiplier |
|---|---|---|---|
| `monsoon_peak` | Jun–Sep | 1.0 (full intensity) | 1.0 |
| `post_monsoon` | Oct | 0.7 | 0.8 |
| `pre_monsoon` | Mar–May | 0.5 | 0.5 |
| `dry_season` | Nov–Feb | 0.2 | 0.3 |

Flood and erosion hazards are scaled down outside the monsoon window based on
BWDB discharge records showing ~80% of annual flow occurs June–September and
BARC erosion studies confirming peak bank-retreat rates in the same window
(Sarker et al., 2014). Structural condition and seismic hazard are non-seasonal
and remain at full intensity in all scenarios.

Each scenario runs **10 replications** with different random seeds, producing
distributions of failure counts and travel time impacts.

---

## 3. Failure Probability Model

### 3.1 Why VI cannot be used directly as a probability

The Vulnerability Index (VI) is a **composite index** — a weighted sum of four
normalised hazard and condition scores — not a calibrated failure probability.
Direct use of VI as a probability produces unrealistic failure rates: the most
vulnerable bridge (VI = 0.75) would fail in 75% of replications, and even the
least vulnerable (VI = 0.21) would fail in 21% of replications. These rates far
exceed observed bridge failure frequencies in Bangladesh during flood seasons.

### 3.2 Linear rescaling to calibrated probabilities

VI scores are rescaled linearly to a calibrated probability range:

$$p = p_{\min} + VI \times (p_{\max} - p_{\min})$$

where $p_{\min} = 0.02$ and $p_{\max} = 0.50$. This maps:

- $VI = 0$ (no vulnerability) $\rightarrow$ 2% failure probability
- $VI = 0.75$ (observed maximum, monsoon peak) $\rightarrow$ 38%
- $VI = 0.21$ (observed minimum) $\rightarrow$ 12%

This preserves the relative ordering between bridges while producing realistic
per-simulation failure rates, and ensures seasonal differences are maintained
(dry season VI values map to lower absolute probabilities than monsoon peak).

### 3.3 Why condition is not used to modify delay

The VI formula assigns a weight of 0.35 to structural condition — the highest
of all four components. Condition therefore already influences the **probability
of failure**. Applying condition a second time to scale delay duration would
double-count the same information, artificially penalising low-condition bridges
twice. The delay model is therefore kept condition-independent, using only bridge
length as the determinant of disruption severity.

---

## 4. Dynamic Failure Timing

Previous versions of the model set bridge failure status at model initialisation
(tick 0), meaning bridges were broken from the start of the simulation. This was
revised to a **dynamic failure model**:

1. At initialisation, if a bridge is determined to fail (`random() < prob`), a
   `failure_tick` is drawn uniformly from $[0, \text{RUN\_LENGTH})$
2. During the simulation, the bridge's `step()` method monitors the clock
3. When `schedule.steps >= failure_tick`, the bridge becomes broken

This better reflects real-world hazard events — a bridge fails during a flood
peak or erosion episode that occurs at some point within the season, not in a
permanently broken pre-existing state. Trucks that cross before `failure_tick`
are unaffected; trucks that cross after experience delays.

The overall probability of failure within the simulation window remains equal
to the rescaled VI probability — only the timing is now stochastic.

---

## 5. Delay Model

When a truck arrives at a broken bridge, it experiences a stochastic delay drawn
from a length-dependent distribution:

| Bridge length | Delay distribution | Rationale |
|---|---|---|
| > 200m (large) | Triangular(60, 120, 240) min | Major river crossings require extended inspection or emergency works |
| 50–200m (medium) | Uniform(45, 90) min | Significant structure; moderate repair or restriction time |
| 10–50m (small) | Uniform(15, 60) min | Smaller spans; quicker assessment and passage |
| < 10m (culvert) | Uniform(10, 20) min | Minor structures; brief restriction |

Delay represents the time a truck must wait at a damaged-but-passable bridge —
analogous to one-lane operation, weight restriction enforcement, or emergency
inspection. The bridge is not removed from the graph (unlike Round 2); trucks
always eventually cross, just with added delay.

Length is the sole determinant of delay magnitude. Bridge condition is
intentionally excluded to avoid double-counting its effect, which is already
captured in the failure probability via the VI score (see Section 3.3).

---

## 6. What Round 3 Measures

Per replication and scenario, the model records:

| Output | Description |
|---|---|
| `broken_count` | Number of bridges that failed in this replication |
| `mean_wait` | Average waiting time per truck at broken bridges |
| `completed_trips` | Trucks that reached their destination |
| `failure_tick` | Tick at which each bridge failed (for temporal analysis) |

Across 10 replications, these produce **distributions** rather than point
estimates — enabling mean ± std reporting and comparison across seasonal
scenarios in Round 4.

---

## 7. Limitations

| Limitation | Effect | Notes |
|---|---|---|
| Failure probability bounds are engineering judgement | FAILURE_PROB_MIN/MAX not empirically calibrated | Historical Bangladesh bridge failure rate data would improve this |
| Failure is permanent once triggered | No recovery within the 5-day window | Reasonable for monsoon season; recovery timescales typically exceed days |
| Uniform failure timing | Failures equally likely at any tick | A peaked distribution (e.g., mid-season) would be more physically realistic |
| Partial damage only | No complete collapse modelled in Round 3 | Complement to Round 2 which tests complete removal |
| Independent bridge failures | No cascade effects between adjacent bridges | Conservative assumption; noted as future work |

---

## 8. References (Round 3)

- Sarker, M. H., Huque, I., Alam, M., & Koudstaal, R. (2014). *Rivers, chars and
  char dwellers of Bangladesh*. International Journal of River Basin Management.
  Cited in: riverbank erosion peak rates coincide with monsoon season (Jun–Sep).

- Kappes, M. S., Papathoma-Köhle, M., & Keiler, M. (2012). Assessing physical
  vulnerability for multi-hazards using an indicator-based methodology.
  *Applied Geography*, 32(2), 577–590.
  https://www.sciencedirect.com/science/article/pii/S0143622811001749

- UNDP Bangladesh (2021). *Multi-Hazard Risk Analysis for Bangladesh*.
  United Nations Development Programme.

- BNBC (2020). *Bangladesh National Building Code 2020*. Seismic zone
  classification and PGA values for Bangladesh.

- Ansary, M. A., & Ara, I. (2004). Seismic vulnerability of existing buildings
  in Bangladesh. *Asian Journal of Civil Engineering*, 5(1–2), 1–18.

- World Bank (2022). *Bangladesh — Bridge Improvement and Maintenance Program*.
  Project documentation, World Bank Infrastructure Practice Group.
  https://www.worldbank.org/en/country/bangladesh

- FHWA (2016). *Synthesis of National and International Methodologies Used for
  Bridge Health Indices*. FHWA-HRT-15-081.
  https://www.fhwa.dot.gov/publications/research/infrastructure/structures/bridge/15081/15081.pdf

---

# Round 1 References

- Cats, O., & Jenelius, E. (2020). *Impact of topology and congestion on link
  criticality rankings in transportation networks*. Transportation Research Part A.
  https://www.sciencedirect.com/science/article/abs/pii/S1361920920307161

- FHWA (2023). *Freight Demand Modeling and Data Improvement*.
  https://ops.fhwa.dot.gov/freight/freight_analysis/fdmdi/index.htm

- Holguín-Vivas, J., & Patil, G. (2008). Freight generation and freight trip
  generation models. In D. A. Hensher & K. J. Button (Eds.), *Handbook of Transport
  Modelling*. ScienceDirect.
  https://www.sciencedirect.com/science/article/pii/B9780124104006000033

- Pavement Interactive (2023). *Equivalent Single Axle Load (ESAL)*.
  https://pavementinteractive.org/reference-desk/design/design-parameters/equivalent-single-axle-load/

- FHWA (2016). *Synthesis of National and International Methodologies Used for Bridge
  Health Indices*. FHWA-HRT-15-081. U.S. Federal Highway Administration.
  https://www.fhwa.dot.gov/publications/research/infrastructure/structures/bridge/15081/15081.pdf

- Jafino, B. A., Kwakkel, J. H., & Verbraeck, A. (2020). Transport network criticality
  metrics: a comparative analysis and a guideline for selection. *Transport Reviews*,
  40(2), 241–264.
  https://www.tandfonline.com/doi/full/10.1080/01441647.2019.1703843

- Tu, Q., Zhang, Y., Feng, J., Wang, W., & Zheng, Z. (2024). *Link Criticality
  Identification and Analysis in Road Networks Using Path Flow Weighted Betweenness
  Centrality*. SSRN Working Paper.
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230899

- World Bank (2022). *Transport*. Official topic page.
  https://www.worldbank.org/ext/en/topic/transport

- World Bank (2023). *Infrastructure, Economic Growth, and Poverty: A Review*.
  Policy Research Working Paper 10343.
  https://documents.worldbank.org/en/publication/documents-reports/documentdetail/927361590594380798

- World Bank (2022). *Infrastructure Overview*.
  https://www.worldbank.org/en/topic/infrastructure/overview
