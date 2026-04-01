# Results Discussion — N1/N2 Bridge Network, Bangladesh

**Assignment 4 | EPA133a Advanced Simulation | Group 14**

---

## Overview

This document presents and discusses the simulation results for Rounds 1 and 2
of the N1/N2 bridge criticality analysis. The analysis is conducted from a
World Bank infrastructure prioritisation perspective, aiming to identify which
bridges on Bangladesh's primary freight corridor require urgent investment based
on their importance to the network.

---

# Round 1: Bridge Ranking Results

## Key Finding: A Dominant Co-Critical Cluster on N2

Round 1 ran a baseline simulation — all bridges functional, traffic calibrated
from AADT data — across 10 replications (7,200 ticks each). Each bridge was
scored on two signals: simulated truck traffic (`avg_trucks_crossed`) and
betweenness centrality (`betweenness`), then combined as:

$$\text{combined\_score} = 0.7 \cdot \text{norm\_traffic} + 0.3 \cdot \text{norm\_betweenness}$$

The top 20 bridges by combined score are all located on the **N2 corridor**,
forming a tight geographic cluster (bridge IDs 2000278–2000378):

| Rank | Bridge ID | Name | avg_trucks_crossed | betweenness | combined_score |
|---|---|---|---|---|---|
| 1 | 2000278 | Bridge start | 30,341.1 | 0.4488 | 0.9725 |
| 2 | 2000284 | Bridge start | 30,340.6 | 0.4479 | 0.9719 |
| 3 | 2000288 | BARIUSA RCC GIDER BRIDGE | 30,339.3 | 0.4473 | 0.9715 |
| 4 | 2000292 | Bridge start | 30,341.3 | 0.4466 | 0.9711 |
| 5 | 2000297 | BARURA BOX CULVERT | 30,341.3 | 0.4458 | 0.9706 |
| 6 | 2000303 | Chatol Bridge | 30,342.5 | 0.4448 | 0.9701 |
| 7 | 2000306 | Bridge start | 30,342.6 | 0.4443 | 0.9698 |
| 8 | 2000314 | RAMPUR P C GIRDER BRIDGE | 30,342.9 | 0.4430 | 0.9690 |
| 9 | 2000316 | KATAKHALI BRIDGE | 30,344.5 | 0.4427 | 0.9688 |
| 10 | 2000320 | Khilsima Bridge | 30,344.6 | 0.4420 | 0.9684 |
| 11 | 2000324 | Bridge start | 30,344.7 | 0.4413 | 0.9680 |
| 12 | 2000330 | Bridge start | 30,345.9 | 0.4403 | 0.9674 |
| 13 | 2000346 | KHATABARI CULVERT | 30,348.8 | 0.4376 | 0.9658 |
| 14 | 2000350 | Bridge start | 30,346.7 | 0.4369 | 0.9653 |
| 15 | 2000356 | Bridge start | 30,347.9 | 0.4358 | 0.9647 |
| 16 | 2000360 | Bridge start | 30,349.1 | 0.4351 | 0.9643 |
| 17 | 2000366 | Bridge start | 30,351.0 | 0.4340 | 0.9637 |
| 18 | 2000370 | Bridge start | 30,350.6 | 0.4333 | 0.9633 |
| 19 | 2000374 | Bridge start | 30,350.7 | 0.4326 | 0.9628 |
| 20 | 2000378 | Bridge start | 30,351.6 | 0.4319 | 0.9624 |

## Discussion

### 1. The top 20 form an exceptionally tight cluster

The range of `avg_trucks_crossed` across the top 20 is only **30,339–30,352**
— a spread of just 13 trucks over a 5-day simulation. Similarly, betweenness
scores range from 0.432 to 0.449. This near-uniformity reflects that these
bridges lie on the same ~10 km stretch of N2, all serving the same
origin-destination flows on Bangladesh's primary freight artery.

### 2. Traffic and betweenness rank differently within the cluster

Despite belonging to the same cluster, the two signals disagree on internal
ordering. Bridge **2000378** ranks 1st by traffic (`rank_by_traffic = 1`) but
69th by betweenness (`rank_by_betweenness = 69`), while **2000278** ranks 18th
by traffic but 33rd by betweenness, yet leads the combined score. This
divergence illustrates why a hybrid metric is needed: pure traffic ranking
favours bridges near high-demand sources, while pure betweenness favours
topological chokepoints. The 0.7/0.3 weighting balances both, and the
sensitivity analysis confirmed the top 20 are identical under a 50/50 split.

### 3. The first bridge outside the top 20 confirms the cluster's dominance

Bridge **1000212** (TIPRA BAZAR BOX CULVERT, N1) has the **single highest
betweenness in the entire network (0.494)** but ranks 21st in combined score
due to significantly lower traffic (~25,027 trucks/day, approximately 18% lower
than the N2 cluster). Promoting it into the top 20 would require giving
betweenness a weight of ≥ 0.93 — well outside any literature-supported range.
This confirms that the top 20 selection is robust to weight choice.

### 4. Why N = 20 bridges: the score gap justifies the threshold

The choice of N = 20 bridges for downstream analysis is not arbitrary. The
combined score drops sharply after rank 20:

- Ranks 1–20 (N2 cluster): combined scores 0.962–0.972 (spread of 0.010)
- Rank 21 (bridge 1000212): combined score 0.877
- Rank 22 onwards: scores fall below 0.880

The gap of ~0.085 between rank 20 and rank 21 is roughly **8.5× larger** than
the entire spread within the top 20 (0.010). This natural elbow in the score
distribution confirms that N = 20 captures a qualitatively distinct, co-critical
cluster rather than an arbitrary cutoff.

Sensitivity to the threshold choice:

- **N = 10**: Would retain only the upper half of the N2 cluster. All ten
  retained bridges have the same betweenness structure and nearly identical
  traffic (~30,340–30,343), so the ranking is unchanged in character but
  discards co-critical bridges for which the same evidence holds equally.
- **N = 30**: Would include bridges ranked 21–30, whose combined scores fall
  in the range 0.877–0.820. These enter a different tier of the score
  distribution and include N1 bridges with lower betweenness values — a
  meaningful change in the nature of the selected set, not merely a marginal
  extension of it.

The N = 20 threshold is therefore justified by the data structure rather than
by convention. The full analysis in Round 2 and beyond covers all 737 bridges
regardless, so the N = 20 selection is only directly consequential for the
presentation of Round 1 results. See also `analysis_methodology.md`, Round 1
Section 10 for detailed sensitivity analysis.

### 5. The result reflects Bangladesh's infrastructure geography

All top 20 bridges are on N2, crossing the same river system in a dense
sequence. This is consistent with N2's role as Bangladesh's primary inland
freight corridor connecting Dhaka to Chittagong port. Their simultaneous
high traffic and high betweenness reflects the near-absence of alternative
routes — a structural property of the corridor explored further in Round 2.

---

# Round 2: Criticality Analysis Results

## Key Finding: A Tiered Criticality Structure Across the Network

Round 2 removed each of the 737 bridges one at a time and counted how many
of the 306 directed OD pairs lost all viable routes (`broken_pairs`). The
result reveals a clear **four-tier criticality hierarchy**:

| Tier | broken_pairs | broken_pct | No. of bridges | Corridor | Example bridges |
|---|---|---|---|---|---|
| 1 | 154 | 50.33% | 20 | N2 | 2000278–2000378 (Khilsima, BARIUSA, Chatol, RAMPUR...) |
| 2 | 130 | 42.48% | ~22 | N1 + N2 | 1000212, 1000243, 1000252, 1000283, 2000491–2000501 |
| 3 | 90 | 29.41% | ~40 | N1 | 1000546–1000642 (Lemua, DumGhat, MUHURI...) |
| 4 | 34 | 11.11% | ~20 | N2 | 2000965–2001020 (BOTESSOR, PULI, HORIPUR...) |
| 5 | 0 | 0% | remaining | Various | Non-critical bridges with alternative routes |

## Discussion

### 1. The N2 cluster is the single most critical tier

Every bridge in Tier 1 (all 20 N2 bridges from Round 1) severs exactly
**154 of 306 OD pairs (50.33%)** upon removal. This means that losing any
one of these bridges cuts off more than half of all origin-destination
connectivity in the entire N1/N2 network. The consistency of this figure
across all 20 bridges confirms they are genuinely co-critical — they sit
on the same single-path stretch of N2 with no alternative routes around them.

This finding is consistent with the near-linear corridor topology of the
N1/N2 network, where approximately 98% of nodes are articulation points
(Cats & Jenelius, 2020). In such networks, bridge removal does not merely
add travel time — it severs routes entirely.

### 2. Round 1 and Round 2 converge on the same top cluster

A central validation finding is that the same 20 N2 bridges that dominated
Round 1 (by traffic volume and betweenness) also form the top tier in Round 2
(by connectivity loss). This convergence across two independent metrics —
one demand-based, one topology-based — strongly supports the conclusion that
these bridges represent the most critical infrastructure on the corridor.

| Metric | Top cluster identified |
|---|---|
| Round 1 combined score (0.7 traffic + 0.3 betweenness) | 2000278–2000378 (N2) |
| Round 2 broken_pairs | 2000278–2000378 (N2) |

### 3. The Tier 2 bridges highlight a secondary critical zone on N1

Bridges in Tier 2 (130 broken pairs, 42.48%) are mostly on N1, in the
2000252–2000346 stretch and the 1000212–1000283 cluster. Notably, bridge
**1000212** (TIPRA BAZAR BOX CULVERT) — which had the highest betweenness
in Round 1 (0.494) but fell outside the top 20 — ranks 32nd in Round 2,
severing 130 OD pairs. This confirms it is genuinely critical from a
connectivity standpoint, even if its lower traffic volume placed it below
the N2 cluster in Round 1's demand-weighted ranking.

### 4. The Tier 3 bridges include structurally significant N1 spans

The 90-broken-pairs tier (29.41%) contains several named, sizeable bridges:

- **Lemua Bridge** (1000391, 99m) — criticality rank 67
- **MUHURI BRIDGE** (1000402, 192m) — criticality rank 73
- **DumGhat Bridge** (1000411, 222m) — criticality rank 68

These are among the physically largest structures on the corridor. Their
lower criticality rank relative to the N2 cluster reflects not their size
but their position in the network — further downstream on N1, where fewer
total OD pairs depend on a single crossing.

### 5. Many bridges have zero impact on connectivity

A substantial portion of the 737 bridges register `broken_pairs = 0` — their
removal does not sever any OD pair. These are typically bridges located on
network segments with alternative parallel routes, or minor structures on
branch roads that do not lie on any shortest path between source nodes. From
a connectivity-prioritisation standpoint, these bridges are non-critical,
though they may still warrant maintenance for local access reasons.

### 6. Criticality rank ties should be interpreted as tiers, not ordered ranks

All bridges within a tier share identical `broken_pairs` values. The
`criticality_rank` numbers within each tier (e.g., ranks 1–20 all having
`broken_pairs = 154`) are determined by row order after sorting and carry no
meaningful ordinality. For analytical purposes, the **tier classification**
(Tier 1 through Tier 5) is the appropriate unit of comparison.

---

## Cross-Round Summary

| Bridge cluster | Round 1 combined_score | Round 2 broken_pairs | Interpretation |
|---|---|---|---|
| N2 cluster (2000278–2000378) | 0.962–0.972 (ranks 1–20) | 154 (50.33%) — Tier 1 | Highest priority by both metrics |
| N1 upper cluster (1000212–1000299) | 0.872–0.877 (ranks ~21–40) | 130 (42.48%) — Tier 2 | High priority; confirmed by both rounds |
| N1 mid cluster (1000381–1000642) | ~0.67 (ranks ~41–80) | 90 (29.41%) — Tier 3 | Moderate priority; includes large spans |
| Lower N2 (2000965–2001020) | ~0.27 (lower ranks) | 34 (11.11%) — Tier 4 | Lower priority |

The agreement between Round 1 and Round 2 across two entirely different
methodologies — agent-based traffic simulation vs. graph-theoretic
connectivity analysis — provides a robust, methodologically diverse basis
for bridge prioritisation. Bridges that appear critical under both frameworks
present the strongest case for World Bank investment.

---

# Round 3: Stochastic Failure Results

## Key Finding: Seasonal Hazard Dramatically Amplifies Network Disruption

Round 3 ran the stochastic failure model across four seasonal scenarios, each
with 10 replications (7,200 ticks, different random seeds). Bridges failed
probabilistically based on their seasonally-adjusted Vulnerability Index (VI),
causing delays to trucks that still crossed them. The results reveal a clear
and consistent pattern: **freight disruption scales sharply with seasonal
hazard intensity**, and the monsoon peak represents a qualitatively different
risk environment compared to the dry season.

---

## 1. Seasonal Escalation in Failure Counts

The number of bridge failures per replication increases monotonically from dry
season to monsoon peak:

| Scenario | Months | Mean failures/rep | Min | Max | Std |
|---|---|---|---|---|---|
| Dry season | Nov–Feb | 114.5 | 97 | 133 | 12.5 |
| Pre-monsoon | Mar–May | 134.0 | 104 | 154 | 13.0 |
| Post-monsoon | Oct | 146.2 | 120 | 169 | 14.8 |
| Monsoon peak | Jun–Sep | **166.2** | 137 | 187 | 15.9 |

The monsoon peak generates on average **51.7 more failures per replication**
than the dry season — a 45% increase. This is driven entirely by the seasonal
multipliers applied to flood (×0.2→1.0) and erosion (×0.3→1.0) components of
the VI, while structural condition and seismic hazard remain constant. The
standard deviation also grows with the mean, reflecting that higher baseline
failure probabilities increase the variance in how many bridges cross the
failure threshold in any given replication.

Across all 10 replications, the number of unique bridges that failed at least
once also increases seasonally:

| Scenario | Unique bridges that failed (any replication) |
|---|---|
| Dry season | 592 of 737 (80.3%) |
| Pre-monsoon | 626 of 737 (84.9%) |
| Post-monsoon | 642 of 737 (87.1%) |
| Monsoon peak | **672 of 737 (91.2%)** |

This means that by monsoon peak, over 9 in 10 bridges on the N1/N2 corridor
will fail at least once across the set of 10 replications — underscoring the
systemic nature of flood-season risk in Bangladesh.

---

## 2. Freight Delay Escalates With Season

The total delay accumulated across all bridges and replications follows the
same seasonal pattern:

| Scenario | Total delay (all bridges, all reps) | Trips with delay | Mean waiting time (delayed) | Max waiting time |
|---|---|---|---|---|
| Dry season | 147,958,863 min | 660,779 (84.3%) | 197.4 min | 1,449 min (~24 hrs) |
| Pre-monsoon | 170,339,546 min | 675,134 (86.7%) | 220.2 min | 1,617 min (~27 hrs) |
| Post-monsoon | 187,142,863 min | 686,786 (88.7%) | 236.3 min | 1,630 min (~27 hrs) |
| Monsoon peak | **212,279,472 min** | 679,520 (88.7%) | **265.0 min** | **1,996 min (~33 hrs)** |

Several findings stand out:

**The monsoon premium is large.** Total network delay in monsoon peak is 43%
higher than in the dry season (212M vs 148M minutes). For a freight corridor
that serves Dhaka–Chittagong trade, this represents a substantial and
seasonally predictable disruption to supply chains.

**Most trips experience some delay in every scenario.** Even in the dry
season, 84.3% of completed trips encounter at least one failed bridge. This
reflects the sheer density of bridges on the N1/N2 corridor — each truck
passes an average of ~95 bridges per trip, and with 114 bridges failing per
replication on average, the probability of encountering at least one is very
high regardless of season.

**Mean waiting time grows non-linearly.** Average waiting time for delayed
trips rises from 197 min (dry) to 265 min (monsoon) — a 34% increase, larger
in relative terms than the 45% increase in failure count. This suggests a
compounding effect: when more bridges fail simultaneously, trucks accumulate
wait time at multiple points along their route rather than just one.

**Completed trips decrease with season.** Total completed trips fall from
783,821 (dry) to 766,390 (monsoon) — a reduction of 17,431 trips (2.2%).
This represents trucks that were either unable to complete their journey within
the simulation window or were stranded by cumulative delays.

---

## 3. Failure Probability Distribution

The VI-to-probability rescaling ($p = 0.02 + VI \times 0.48$) produces the
following failure probability ranges across the network (replication 1):

| Scenario | Min prob | Mean prob | Max prob |
|---|---|---|---|
| Dry season | 0.093 | 0.157 | 0.282 |
| Pre-monsoon | 0.104 | 0.181 | 0.314 |
| Post-monsoon | 0.111 | 0.198 | 0.337 |
| Monsoon peak | **0.122** | **0.222** | **0.380** |

The highest-vulnerability bridge in monsoon peak is **DONMIA** (bridge 1001543,
N1, condition D, 3m) with $p = 0.380$ — meaning it has a 38% chance of failing
within any given 5-day simulation window during the monsoon season. Other
high-probability bridges include ISLAM PUR BOX CULVERT (2000939, $p = 0.374$)
and UTTOR KALAPUR (7000114, condition D, $p = 0.368$). These are predominantly
short structures with poor condition ratings (grade D) situated in high-flood
or high-erosion zones.

---

## 4. Highest-Impact Bridges by Delay

The bridges causing the greatest freight disruption when they fail are not
necessarily the same bridges identified as most critical in Round 2. The
top 10 bridges by mean total delay per failure event in the monsoon peak
scenario are:

| Bridge ID | Name | Road | Condition | Length | Mean delay when failing (min) | Mean vehicles delayed |
|---|---|---|---|---|---|---|
| 1000411 | DumGhat Bridge (2 br.) | N1 | A | 222m | 1,098,904 | 8,512 |
| 2000037 | BANTI BRIDGE (2 br.) | N2 | C | 72m | 1,018,744 | 15,237 |
| 5000065 | ULAKOLA | N105 | A | 209m | 978,452 | 7,598 |
| 2000314 | RAMPUR P C GIRDER (2 br.) | N2 | C | 64m | 954,170 | 14,233 |
| 2000110 | Bala Nagar Bridge (2 br.) | N2 | A | 61m | 931,893 | 13,911 |
| 2000217 | OLD BRAMMAPULRA | N2 | C | 429m | 846,940 | 6,577 |
| 2000175 | BRIDE OVER ARIAL (2 br.) | N2 | C | 140m | 842,254 | 12,560 |
| 2000139 | Simbi Bridge (2 br.) | N2 | A | 96m | 788,358 | 11,789 |
| 2000303 | Chatol Bridge (2 br.) | N2 | A | 27m | 785,876 | 21,238 |
| 2000783 | SHALIPUR BRIDGE (2 br.) | N2 | C | 161m | 779,112 | 11,629 |

Two structural patterns dominate this list:

**Large physical spans accumulate massive delay.** DumGhat Bridge (222m) and
ULAKOLA (209m) trigger the `Triangular(60, 120, 240)` min delay distribution
for structures > 200m. When these fail early in the simulation, tens of
thousands of trucks accumulate wait times of 1–4 hours each. DumGhat Bridge
appeared in the Round 2 Tier 3 (90 broken pairs), demonstrating that a bridge
can be moderate in network criticality but extreme in disruption severity when
it does fail.

**High-traffic N2 bridges with poor condition amplify delay.** Bridges like
BANTI BRIDGE (condition C, 72m) and RAMPUR P C GIRDER (condition C, 64m) carry
the highest passenger flows on the N2 corridor (~14,000–15,000 vehicles per
failure event) even though their physical length places them in the medium delay
category. Their condition C rating increases their failure probability, and their
position on the high-demand N2 corridor means each failure is witnessed by a
disproportionately large number of trucks.

**OLD BRAMMAPULRA** (2000217, 429m) is the longest bridge on the network and
triggers the highest delay tier (`Triangular(60, 120, 240)` min), yet ranks
6th rather than 1st. This is because it fails in only 2 of 10 replications in
monsoon peak — its high physical length and condition C do elevate its VI, but
not enough to push it to a high failure frequency.

---

## 5. Condition Grade and Failure Impact

Grouping failures by bridge condition grade in the monsoon peak scenario
reveals an important asymmetry:

| Condition | Failure events (all reps) | Mean delay per event (min) |
|---|---|---|
| A (Good) | 896 | 132,839 |
| B (Fair) | 546 | 107,871 |
| C (Poor) | 201 | 165,826 |
| D (Very poor) | 19 | 54,042 |

Condition A bridges account for the **most failure events** (896), not because
they are individually more vulnerable but because they are numerically more
common in the dataset. Condition C bridges, though fewer, produce the
**highest mean delay per failure event** (165,826 min) — reflecting that
poor-condition bridges tend to be older, larger structures on high-traffic
sections, which were more likely built at historically important crossing
points. Condition D bridges fail rarely (19 events) and cause the least delay
per event — most are very short structures (culverts and small box culverts)
on lower-traffic branch roads.

---

## 6. Cross-Scenario Behaviour of Key Bridges

Some bridges show unexpected cross-scenario patterns when examined individually.
For example, **Lemua Bridge** (1000391) and **DumGhat Bridge** (1000411) both
show higher mean delay per failure in dry season or pre-monsoon than in monsoon
peak:

| Bridge | dry_season | pre_monsoon | post_monsoon | monsoon_peak |
|---|---|---|---|---|
| Lemua Bridge (1000391) | 1,032,021 | 990,200 | 636,702 | 470,967 |
| DumGhat Bridge (1000411) | 1,019,190 | 1,020,925 | 594,893 | 1,098,904 |
| MUHURI BRIDGE (1000402) | 511,470 | 409,336 | 747,414 | 510,851 |
| BANTI BRIDGE (2000037) | 453,793 | 1,162,461 | 984,576 | 1,018,744 |

These values represent mean delay **conditional on the bridge failing** —
they are not the unconditional expected delay, which increases monotonically
with season. The conditional pattern reflects the interaction of two
stochastic factors: the failure tick timing and the density of other failures
in the network. When many other bridges also fail in the same replication
(as is more common in monsoon), some trucks are delayed or stranded before
they even reach a particular bridge, reducing that bridge's observed delay
count. This is a network-level suppression effect — in high-failure
scenarios, disruption is more diffuse and no single bridge accumulates the
concentrated delay it would if it were the only failure.

---

## 7. Round 3 in Context: What Changes Compared to Rounds 1 and 2

Round 3 surfaces a different set of high-priority bridges than Rounds 1 and 2:

| Bridge | Round 1 rank | Round 2 criticality rank | Round 3 monsoon delay rank |
|---|---|---|---|
| 2000278–2000378 (N2 cluster) | Top 20 | Tier 1 (ranks 1–20) | Not consistently top-ranked |
| DumGhat Bridge (1000411) | ~rank 68 | Tier 3 (rank 68) | **#1 by mean delay** |
| BANTI BRIDGE (2000037) | Not in top 20 | Not Tier 1 | **#2 by mean delay** |
| MUHURI BRIDGE (1000402) | ~rank 73 | Tier 3 (rank 73) | Top 10 in multiple scenarios |
| Chatol Bridge (2000303) | Rank 6 | Tier 1 | Top 10 in monsoon |

The N2 cluster (top of Rounds 1 and 2) does not dominate Round 3's delay
rankings. This is because the Round 3 delay metric is sensitive to which
bridges *actually fail* in each replication — and the high-traffic N2 cluster
bridges have moderate VIs (they are structurally sound and not all in extreme
flood zones). When they do fail, they do cause significant delay (e.g. Chatol
Bridge, 2000303, rank 9 in monsoon), but their failure probability is not the
highest in the network.

This divergence is precisely why Round 4 — the combined priority matrix — is
necessary. Bridges like DumGhat and BANTI combine moderate-to-high
vulnerability (Round 3) with significant connectivity loss (Round 2 Tier 3)
and present a materially different risk profile than the pure-criticality N2
cluster.

---

## Cross-Round Summary (Updated)

| Bridge | Round 1 score | Round 2 criticality | Round 3 monsoon delay | Combined signal |
|---|---|---|---|---|
| N2 cluster (2000278–2000378) | Top 20, score 0.962–0.972 | Tier 1, 154 broken pairs | Moderate delay when failing | Very high criticality, moderate vulnerability |
| DumGhat Bridge (1000411) | Rank ~68 | Tier 3, 90 broken pairs | #1 mean delay (1,098,904 min) | Moderate criticality, very high vulnerability |
| BANTI BRIDGE (2000037) | Outside top 20 | Not in top tiers | #2 mean delay (1,018,744 min) | Lower criticality, very high vulnerability |
| Chatol Bridge (2000303) | Rank 6 | Tier 1, 154 broken pairs | Top 10 monsoon | High criticality, high vulnerability |
| MUHURI BRIDGE (1000402) | Rank ~73 | Tier 3, 90 broken pairs | Top 10 post-monsoon and dry | Moderate criticality, high vulnerability |

Bridges in the final row of the table — those that score high across
**all three rounds** — represent the most defensible candidates for immediate
World Bank investment. Chatol Bridge (2000303) stands out as the clearest
example: it ranks in the top 10 of Rounds 1, 2, and 3.

---

# Round 4: Priority Matrix Results

## Key Finding: Bridges That Are Both Critical and Vulnerable Are Concentrated in the N2 Corridor Top Tier — but N1 Bridges Command the Highest Urgency Once Vulnerability is Weighted

Round 4 combines the connectivity-loss criticality from Round 2 and the
stochastic vulnerability from Round 3 into a single priority matrix. Each of
the 737 bridges receives a normalised criticality score (based on broken OD
pairs) and a normalised vulnerability score (based on mean expected delay in the
**monsoon peak** scenario across 10 replications). The monsoon peak is used as the
reference case because it represents the worst-case seasonal hazard conditions. The
two dimensions are combined into three weighted priority scores and bridges are
assigned to one of four quadrants (A–D) at the median thresholds of both
dimensions.

---

## 1. Quadrant Distribution

| Quadrant | Definition | Count | % of network |
|---|---|---|---|
| A — High priority | High criticality AND high vulnerability | 182 | 24.7% |
| B — Monitor criticality | High criticality, low vulnerability | 227 | 30.8% |
| C — Monitor vulnerability | Low criticality, high vulnerability | 187 | 25.4% |
| D — Low priority | Low criticality AND low vulnerability | 141 | 19.1% |

The near-equal split across all four quadrants — with no single quadrant
holding a clear majority — confirms that criticality and vulnerability are
largely **independent dimensions** in this network. A bridge that disconnects
many OD pairs is not necessarily the same bridge that experiences the highest
delay when it fails, and vice versa. This independence is the central
justification for requiring both metrics: a purely criticality-based ranking
(Rounds 1–2) would systematically under-value the Quadrant C bridges, while a
purely vulnerability-based ranking (Round 3 alone) would elevate bridges with
zero network connectivity value.

Quadrant B (high criticality, low vulnerability) is the largest group, which
reflects the structure of the N2 Tier 1 cluster: many Tier 1 bridges have
maximum criticality but their expected delays are in the lower half of the
distribution, because structurally sound (condition A or B) bridges in this
group have low failure probabilities and therefore accumulate little expected
delay across replications.

**Quadrant A is dominated by N1 bridges.** Despite N2 dominating Rounds 1–3
rankings, the Quadrant A breakdown by corridor is:

| Corridor | Bridges in Quadrant A |
|---|---|
| N1 | 105 (57.7%) |
| N2 | 58 (31.9%) |
| Other (N104, N105, N106) | 19 (10.4%) |

N1 bridges qualify for Quadrant A in large numbers because the criticality
threshold (the median of `norm_criticality`) falls between `broken_pairs = 0`
and `broken_pairs = 34`. Any bridge with *any* connectivity impact — including
the Tier 4 group (34 broken pairs) that is common on N1 — already exceeds the
criticality threshold. Paired with above-median expected delay (many N1 bridges
are in flood-prone zones with moderate-to-poor condition ratings), this pushes
N1 into Quadrant A at scale.

---

## 2. Top Priority Bridges (Quadrant A, Rank 1–20)

| Rank | Bridge ID | Name | Road | Broken pairs | Expected delay (min) | norm_C | norm_V | Score (equal) |
|---|---|---|---|---|---|---|---|---|
| 1 | 2000303 | Chatol Bridge | N2 | 154 | 314,351 | 1.000 | 0.746 | 0.873 |
| 2 | 2000314 | RAMPUR P C GIRDER BRIDGE | N2 | 154 | 286,251 | 1.000 | 0.680 | 0.840 |
| 3 | 2000288 | BARIUSA RCC GIDER BRIDGE | N2 | 154 | 238,437 | 1.000 | 0.566 | 0.783 |
| 4 | 2000316 | KATAKHALI BRIDGE | N2 | 154 | 199,805 | 1.000 | 0.474 | 0.737 |
| 5 | 2000320 | Khilsima Bridge | N2 | 154 | 164,648 | 1.000 | 0.391 | 0.695 |
| 6 | 2000346 | KHATABARI CULVERT | N2 | 154 | 159,138 | 1.000 | 0.378 | 0.689 |
| 7 | 1000402 | MUHURI BRIDGE | N1 | 90 | 306,511 | 0.584 | 0.728 | 0.656 |
| 8 | 2000297 | BARURA BOX CULVERT | N2 | 154 | 111,159 | 1.000 | 0.264 | 0.632 |
| 9 | 2000491 | Bridge start (N2) | N2 | 130 | 170,944 | 0.844 | 0.406 | 0.625 |
| 10 | 2000378 | Bridge start (N2) | N2 | 154 | 98,043 | 1.000 | 0.233 | 0.616 |
| 11 | 2000330 | Bridge start (N2) | N2 | 154 | 85,313 | 1.000 | 0.203 | 0.601 |
| 12 | 2000292 | Bridge start (N2) | N2 | 154 | 83,624 | 1.000 | 0.199 | 0.599 |
| 13 | 2000366 | Bridge start (N2) | N2 | 154 | 57,361 | 1.000 | 0.136 | 0.568 |
| 14 | 2000350 | Bridge start (N2) | N2 | 154 | 51,008 | 1.000 | 0.121 | 0.561 |
| 15 | 1000411 | DumGhat Bridge (L) | N1 | 90 | 219,781 | 0.584 | 0.522 | 0.553 |
| 16 | 1000319 | BOSONTA PUR BOX CULVERT | N1 | 130 | 104,093 | 0.844 | 0.247 | 0.546 |
| 17 | 2000501 | BASHINA BOX CULVERT | N2 | 130 | 94,640 | 0.844 | 0.225 | 0.534 |
| 18 | 2000370 | Bridge start (N2) | N2 | 154 | 27,341 | 1.000 | 0.065 | 0.532 |
| 19 | 2000374 | Bridge start (N2) | N2 | 154 | 19,048 | 1.000 | 0.045 | 0.523 |
| 20 | 1000212 | TIPRA BAZAR BOX CULVERT | N1 | 130 | 77,255 | 0.844 | 0.183 | 0.514 |

The top 14 are all N2 Tier 1 bridges (154 broken pairs, `norm_C = 1.0`),
confirming that maximum network criticality is the dominant driver of the
combined score when vulnerability is non-negligible. Among these, the ordering
is determined entirely by `norm_vulnerability`: Chatol Bridge (2000303) leads
with a monsoon peak expected delay of 314,351 minutes — the highest
vulnerability of any Tier 1 bridge. Notably, Chatol registered zero expected
delay in all three non-monsoon scenarios, as it never failed in any of the 10
replications outside the peak season (see Section 5 for discussion).

The first N1 entry appears at rank 7: **MUHURI BRIDGE** (1000402, 90 broken
pairs). Despite having `norm_C = 0.584` — barely above the criticality median —
it achieves rank 7 because its expected delay (306,511 min) is among the
highest on the entire network. MUHURI BRIDGE appeared in the Round 3 top-10 in
both post-monsoon and dry-season scenarios, and is the only bridge that achieves
top-tier status across all four analytical rounds. A similar argument applies
to **DumGhat Bridge** (1000411, rank 15): it was the highest delay-causing
bridge in Round 3 monsoon (1,098,904 min/event) and remains in the top 20
despite a moderate criticality score.

---

## 3. Score Decomposition: Criticality vs. Vulnerability Contributions

The gap between criticality and vulnerability contributions reveals the
structural imbalance in the priority matrix:

| Quadrant | Mean score | Mean norm_C | Mean norm_V |
|---|---|---|---|
| A | 0.264 | 0.766 | 0.602 |
| B | 0.137 | 0.830 | 0.019 |
| C | 0.065 | 0.013 | 0.712 |
| D | 0.004 | 0.012 | 0.004 |

Quadrant B bridges have very high mean criticality (0.830) but near-zero
vulnerability (0.019), meaning they are structurally important to network
connectivity but fail rarely and cause little disruption when they do. These
bridges may not require immediate physical intervention but should be monitored
for condition deterioration — a single degradation event can shift a Quadrant B
bridge into Quadrant A.

Quadrant C bridges show the reverse: mean criticality 0.013 (effectively zero
connectivity impact) but high vulnerability (0.712). These are bridges that
fail frequently and cause significant delay in isolation, but whose failure does
not sever the network. Under a pure accessibility-maximisation objective, they
do not rank highly. However, from an asset preservation perspective — and
particularly in the context of the World Bank's interest in reducing freight
disruption costs — Quadrant C bridges represent a large pool of chronic, diffuse
risk. **BANTI BRIDGE** (2000037) is the most prominent Quadrant C bridge: it
has zero broken_pairs (it lies on a redundant section of the corridor) but
caused the second-highest mean delay per failure event in Round 3 and has the
highest sensitivity to weight configuration (rank spread of 379 positions).

---

## 4. Sensitivity Analysis: How Weight Configuration Changes Rankings

Three weight configurations were tested:

| Configuration | Criticality weight | Vulnerability weight |
|---|---|---|
| Equal (baseline) | 0.50 | 0.50 |
| Criticality-heavy | 0.70 | 0.30 |
| Vulnerability-heavy | 0.30 | 0.70 |

The top 6 bridges (all N2 Tier 1 with maximum criticality) are
**invariant to weight configuration** — they occupy the same ranks across all
three scenarios. This is because their combined score is high enough in both
dimensions that no reweighting can displace them.

Larger rank movements are observed in the middle of the distribution:

| Bridge | Equal rank | Crit-heavy rank | Vuln-heavy rank | Spread |
|---|---|---|---|---|
| MUHURI BRIDGE (1000402) | 7 | 31 | 5 | 26 |
| DumGhat Bridge (1000411) | 15 | 42 | 10 | 32 |
| BANTI BRIDGE (2000037) | 90 | 415 | 36 | 379 |
| Umarpur Bridge (2000757) | 87 | 413 | 31 | 382 |

**MUHURI BRIDGE** and **DumGhat Bridge** move substantially because they
represent the classic "moderate criticality, high vulnerability" profile.
Under the criticality-heavy configuration, their modest network impact (90
broken pairs vs 154 maximum) causes them to fall significantly in rank. Under
the vulnerability-heavy configuration, their high expected delay elevates them
close to the top.

**BANTI BRIDGE** and other Quadrant C bridges show the largest absolute rank
movement: from mid-table under equal weighting, they plummet to the bottom 5%
under criticality-heavy weighting (rank 415 of 737) but rise to the top 5%
under vulnerability-heavy weighting (rank 36). This extreme sensitivity
reflects a fundamental ambiguity: whether these bridges should be prioritised
depends entirely on the decision-maker's objective — network accessibility
versus freight disruption cost minimisation.

The sensitivity results demonstrate that the equal-weight baseline (0.5/0.5)
is a reasonable compromise for a general-purpose investment ranking, but
project-specific objectives should inform weight selection before any World
Bank investment recommendation is finalised.

---

## 5. Seasonal Vulnerability Patterns Among Top-Priority Bridges

Monsoon peak accounts for the largest share of expected delay for nearly all
top-priority bridges. The cross-seasonal progression is consistent with the
failure probability rescaling: bridges with moderate-to-high VI see their
failure probability increase substantially between dry season and monsoon peak
($p = 0.02 + VI \times 0.48$ with seasonal multipliers up to 1.0 on flood and
erosion components).

### 5.1 Zero expected delay: interpreting sparse failures

A key feature visible in the seasonal delay heatmap is that several top-priority
bridges register **zero expected delay in one or more non-monsoon scenarios**.
For example, **Chatol Bridge** (2000303, rank 1) shows:

| Scenario | Expected delay (min) | Interpretation |
|---|---|---|
| Dry season | 0 | No failures in any of the 10 replications |
| Pre-monsoon | 0 | No failures in any of the 10 replications |
| Post-monsoon | 0 | No failures in any of the 10 replications |
| Monsoon peak | 314,350 | Failed in ~4 of 10 replications (failure_rate = 0.40) |

These zeros are not a data or modelling error. They reflect the statistical
reality of running **10 replications** with a seasonally low failure probability:
when a bridge's VI is scaled by the dry-season flood multiplier (×0.2), its
failure probability drops low enough that zero failures can occur across all 10
replications — producing an expected delay of exactly zero.

The important distinction is between two metrics:

- **`expected_delay`** = mean delay over all 10 replications, including those
  where the bridge did not fail. This is the correct metric for the Round 4
  priority score because it naturally combines probability and severity. A zero
  value means "the bridge posed no measurable disruption risk in this scenario
  under 10 replications."

- **`mean_delay_when_failed`** = mean delay conditional on the bridge failing.
  For Chatol Bridge this is ~785,876 min/event in monsoon — enormous — but this
  figure cannot be computed for scenarios where the bridge never failed, and
  using it alone ignores failure frequency.

The practical interpretation: Chatol Bridge's risk is highly concentrated in
the monsoon season. Its appearance in lower-risk scenarios would require more
than 10 replications to observe statistically. This monsoon-concentration
pattern strengthens the case for pre-monsoon interventions.

### 5.2 Bridges with cross-seasonal vulnerability

Not all top-priority bridges have monsoon-only risk. **KATAKHALI BRIDGE**
(2000316, rank 4) and **MUHURI BRIDGE** (1000402, rank 7) show non-zero expected
delay across multiple scenarios:

| Bridge | Dry (min) | Pre-monsoon (min) | Post-monsoon (min) | Monsoon peak (min) |
|---|---|---|---|---|
| KATAKHALI (2000316) | 0 | 156,637 | 167,658 | 199,805 |
| MUHURI (1000402) | 153,441 | 163,735 | 373,707 | 306,511 |

KATAKHALI shows a clear seasonal escalation from pre-monsoon onward, with the
monsoon premium approximately 28% above pre-monsoon. MUHURI shows a more complex
pattern: post-monsoon delay (373,707 min) exceeds monsoon peak (306,511 min),
reflecting the network-suppression effect documented in Round 3 — in the highest-
failure monsoon scenario, trucks are frequently delayed by other bridges before
reaching MUHURI, reducing MUHURI's observed delay accumulation.

This implies that **MUHURI BRIDGE poses a year-round disruption risk**, not
a seasonally-concentrated one. From an investment planning standpoint, this
argues for intervention independent of monsoon timing — a different urgency
profile than Chatol Bridge.

The seasonal concentration of risk (monsoon-only vs. year-round) should inform
the type of intervention: monsoon-concentrated bridges (Chatol) may benefit from
seasonal flood protection and emergency preparedness, while year-round vulnerable
bridges (MUHURI) require structural reinforcement regardless of season.

---

## 6. Round 4 in Context: Cross-Round Synthesis

Two distinct priority archetypes emerge from the four-round analysis:

**Archetype 1 — Corridor Gatekeepers (Quadrant A, top 14):** N2 Tier 1 bridges
that were already dominant in Rounds 1 and 2 remain dominant in Round 4 because
their maximum criticality score prevents any reweighting from displacing them.
These bridges represent the structural spine of the Dhaka–Chittagong corridor.
Investment here targets the highest-consequence single points of failure in
terms of network accessibility.

**Archetype 2 — High-Disruption N1 Bridges (Quadrant A, rank 7–20):**
Bridges like MUHURI BRIDGE and DumGhat Bridge appear only in Round 3 and Round 4.
They are not individually decisive for network connectivity (Tier 3, 90 broken
pairs), but when they fail, they impose the largest freight delays in the entire
network. Their appearance in the top 20 of the combined matrix signals that a
pure accessibility-based framework (Rounds 1–2) would have systematically missed
these as investment priorities.

**BANTI BRIDGE** (Quadrant C) illustrates the outer limit of the priority
matrix: a bridge with enormous disruption potential but zero network criticality.
Under the World Bank's dual mandate — maximising network accessibility *and*
minimising freight disruption — it does not make the cut for the
highest-priority investment tier, but its position in Quadrant C argues for
inclusion in a secondary preventive maintenance programme.

---

## Final Investment Recommendation

Based on the combined Round 1–4 evidence, the following bridges are recommended
as the first tier of World Bank investment on the N1/N2 corridor:

**Immediate intervention (top 7 by composite evidence):**

| Priority | Bridge ID | Name | Road | Key risk |
|---|---|---|---|---|
| 1 | 2000303 | Chatol Bridge | N2 | Maximum criticality + highest Tier-1 vulnerability |
| 2 | 2000314 | RAMPUR P C GIRDER BRIDGE | N2 | Maximum criticality + second-highest vulnerability |
| 3 | 2000288 | BARIUSA RCC GIDER BRIDGE | N2 | Maximum criticality + high vulnerability |
| 4 | 1000402 | MUHURI BRIDGE | N1 | Highest network-wide expected delay (all seasons) |
| 5 | 1000411 | DumGhat Bridge (L) | N1 | Highest conditional delay in monsoon peak |
| 6 | 2000316 | KATAKHALI BRIDGE | N2 | Maximum criticality + consistently top-10 across rounds |
| 7 | 2000491 | Bridge start (N2, bp=130) | N2 | High criticality + above-median vulnerability |

Bridges 1–3 and 6 represent the clearest investment case: they appear in the
top tier of every analytical round and achieve their high Round 4 rank
independently of weight configuration. Bridges 4 and 5 require a
vulnerability-weighted objective to emerge as top priorities, but the magnitude
of their expected delay — particularly in the monsoon season — makes a strong
case for inclusion in any World Bank programme targeting freight disruption
reduction on this corridor.

---

## Cross-Round Summary (Final)

| Bridge | Round 1 score | Round 2 tier | Round 3 monsoon delay | Round 4 rank (equal) | Recommendation |
|---|---|---|---|---|---|
| Chatol Bridge (2000303) | 0.970 (rank 7) | Tier 1, 154 bp | Top 10 | **1** | Immediate intervention |
| RAMPUR P C GIRDER (2000314) | 0.969 (rank 9) | Tier 1, 154 bp | Top 5 | **2** | Immediate intervention |
| BARIUSA RCC GIDER (2000288) | 0.971 (rank 4) | Tier 1, 154 bp | Top 15 | **3** | Immediate intervention |
| KATAKHALI BRIDGE (2000316) | 0.969 (rank 10) | Tier 1, 154 bp | Top 15 | **4** | Immediate intervention |
| MUHURI BRIDGE (1000402) | rank 73 | Tier 3, 90 bp | #3 monsoon | **7** | Immediate intervention |
| DumGhat Bridge (1000411) | rank 68 | Tier 3, 90 bp | **#1** monsoon | **15** | Immediate intervention |
| BANTI BRIDGE (2000037) | outside top 20 | bp = 0 | **#2** monsoon | 90 (Quad C) | Secondary maintenance |
| N2 cluster 2000278–2000392 | Top 20 | Tier 1 | Moderate | Top 20 | Active monitoring |
