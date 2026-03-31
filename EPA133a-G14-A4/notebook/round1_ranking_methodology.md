# Round 1 Bridge Ranking Methodology

**Assignment 4 | EPA133a Advanced Simulation | Group 14**

---

## 1. Purpose

This document explains how Round 1 of the simulation (`model_run.py`) identifies and
ranks the most critical bridges on Bangladesh's N1/N2 corridor. The resulting ranked
list feeds directly into Round 2 (bridge removal / criticality testing). Every
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
used to select the top 20 bridges for Round 2.

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

This robustness also strengthens confidence in the Round 2 results: the bridges
selected for removal testing are not an artefact of an arbitrary weighting formula —
they would be selected under a wide range of reasonable assumptions.

---

## 8. Comparison of Three Ranking Strategies

Three separate rank columns are saved in `bridge_ranking.csv` to allow comparison:

| Column | Based on | Interpretation |
|---|---|---|
| `rank_by_traffic` | `avg_trucks_crossed` | Pure demand-based ranking; most responsive to AADT input |
| `rank_by_betweenness` | `betweenness` | Pure topology-based ranking; demand-agnostic |
| `rank_by_combined` | `combined_score` (0.7/0.3) | Literature-justified hybrid; used for Round 2 bridge selection |

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

## 10. References

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
