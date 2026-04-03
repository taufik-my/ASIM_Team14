# EPA133a – Assignment 4

## Network Analysis: Vulnerability and Criticality of Bangladesh's N1/N2 Transport Network

**Created by: EPA133a Team 14**

| Name                 | Student Number |
| -------------------- | -------------- |
| Bayu Jamalullael     | 6367984        |
| Brenda Escobar       | 6512191        |
| Brian Parsaoran      | 6147674        |
| Taufik Muhamad Yusup | 6378056        |
| Zhafran Sidik        | 565841         |

---

## Project Overview

This project analyses the **vulnerability and criticality** of bridges on Bangladesh's N1/N2 transport corridor using an agent-based simulation model built with **Mesa** and **NetworkX**.

Building on the Assignment 3 model, we enhance it with:
- **Real disaster data** (earthquake, flood, erosion, cyclone) combined with bridge conditions to compute per-bridge failure probabilities
- **RMMS traffic data** (AADT) for realistic per-source truck generation rates
- **Graph-based connectivity analysis** to measure network disruption when bridges are removed
- **Seasonal vulnerability scenarios** (dry season, pre-monsoon, post-monsoon, monsoon peak)

The analysis produces a **priority matrix** combining criticality and vulnerability to identify which bridges Bangladesh should prioritise for maintenance and investment.

---

## Project Structure

```
EPA133a-G14-A4
│
├── data/
│   ├── integrated_data.csv            # Network data + AADT traffic (model input)
│   ├── vulnerability_index.csv        # Per-bridge failure probabilities (model input)
│   ├── network_data.csv               # Base road network (source for data prep)
│   ├── bridges_hazard_data.csv        # Bridge + hazard layers from GIS
│   ├── bridges_flood_imputed.csv      # Flood imputation for 59 bridges from GIS
│   ├── BMMS_overview.xlsx             # Raw bridge management data
│   ├── _roads3.csv                    # Raw road dataset
│   ├── gis/                           # GIS shapefiles
│   └── rmms/                          # Raw RMMS HTML traffic files
│
├── experiment/
│   ├── round1_criticality/
│   │   ├── trips.csv                  # Baseline trip data (10 reps)
│   │   ├── bridges.csv                # Baseline bridge data (10 reps)
│   │   └── criticality_scores.csv     # All 737 bridges with criticality scores
│   │
│   ├── round2_vulnerability/
│   │   ├── dry_season_trips.csv       # Trip data: Nov-Feb scenario
│   │   ├── dry_season_bridges.csv     # Bridge data: Nov-Feb scenario
│   │   ├── pre_monsoon_trips.csv      # Trip data: Mar-May scenario
│   │   ├── pre_monsoon_bridges.csv    # Bridge data: Mar-May scenario
│   │   ├── post_monsoon_trips.csv     # Trip data: Oct scenario
│   │   ├── post_monsoon_bridges.csv   # Bridge data: Oct scenario
│   │   ├── monsoon_peak_trips.csv     # Trip data: Jun-Sep scenario
│   │   └── monsoon_peak_bridges.csv   # Bridge data: Jun-Sep scenario
│   │
│   └── round3_combined/
│       ├── vulnerability_summary.csv  # Aggregated vulnerability per bridge
│       └── priority_matrix.csv        # Final criticality × vulnerability ranking
│
├── img/                               # Generated figures for report
│
├── model/
│   ├── model.py                       # Main model (Mesa + NetworkX)
│   ├── components.py                  # Agent definitions (Bridge, Vehicle, etc.)
│   ├── model_run.py                   # Experiment runner (Round 1 + Round 2)
│   ├── model_viz.py                   # Visualisation server
│   └── ContinuousSpace/              # Custom visualisation module
│
├── notebook/
│   ├── traffic_data_preparation.ipynb      # Data prep: RMMS → integrated_data.csv
│   ├── vulnerability_index_data.ipynb      # Data prep: hazards → vulnerability_index.csv
│   └── round3_combined_analysis.ipynb      # Combined analysis + all figures
│
├── report/
│
└── README.md                          # This file
```

---

## How to Reproduce the Results

### Prerequisites

- Python **3.10+**
- Install dependencies:

```
pip install -r requirements.txt
```

### 1. Data Preparation

The input data files are already provided. To regenerate them from source:

**Traffic data:**
```
notebook/traffic_data_preparation.ipynb
```
Reads RMMS HTML files from `data/rmms/`, merges with `data/network_data.csv`, outputs `data/integrated_data.csv`.

**Vulnerability index:**
```
notebook/vulnerability_index_data.ipynb
```
Reads `data/bridges_hazard_data.csv` and `data/bridges_flood_imputed.csv`, computes per-bridge failure probabilities with seasonal multipliers, outputs `data/vulnerability_index.csv`.

### 2. Run the Experiments

From the `model/` directory:

```
cd model
python model_run.py round1    # Criticality: baseline simulation + graph analysis (~30 min)
python model_run.py round2    # Vulnerability: 4 seasonal scenarios × 10 reps (~30 min)
python model_run.py all       # Both rounds sequentially
```

Results are saved to `experiment/round1_criticality/` and `experiment/round2_vulnerability/`.

### 3. Analyse Results

Run the notebook:

```
notebook/round3_combined_analysis.ipynb
```

This:
- Aggregates vulnerability data across seasonal scenarios
- Merges criticality (Round 1) with vulnerability (Round 2) into a priority matrix
- Generates all figures for the report (saved to `img/`)
- Outputs `experiment/round3_combined/priority_matrix.csv`

### 4. Run with Visualisation (Optional)

```
python model/model_viz.py
```

Opens a browser-based visualisation at `http://localhost:8521`.

---

## Experiment Design

### Round 1: Criticality

**Step A — Baseline simulation** (10 replications, 7,200 ticks each):
- All bridges functional, AADT-calibrated truck generation
- Measures truck traffic volume per bridge

**Step B — Graph connectivity analysis** (all 737 bridges):
- For each bridge: remove from NetworkX graph, count broken OD pairs, restore
- Measures what percentage of source-sink connections are lost

**Step C — Combined criticality score:**
```
criticality = 0.7 × normalised_traffic + 0.3 × normalised_connectivity_loss
```

### Round 2: Vulnerability

Four seasonal scenarios using disaster-weighted per-bridge failure probabilities:

| Scenario | Season | Flood multiplier | Erosion multiplier |
| -------- | ------ | ---------------- | ------------------ |
| dry_season | Nov–Feb | 0.2 | 0.3 |
| pre_monsoon | Mar–May | 0.5 | 0.5 |
| post_monsoon | Oct | 0.7 | 0.8 |
| monsoon_peak | Jun–Sep | 1.0 | 1.0 |

Each scenario: 10 replications with different seeds. Vulnerability Index rescaled to failure probabilities in [0.02, 0.50].

### Round 3: Combined Analysis (notebook)

- Vulnerability metric: expected_delay = failure_rate × mean_delay_when_failed
- Priority score: 0.5 × normalised_criticality + 0.5 × normalised_vulnerability
- Quadrant classification: A (Urgent), B (Monitor), C (Maintain), D (Routine)
- Sensitivity analysis with three weight configurations

---

## Key Changes from Assignment 3

| Component | Change | Reason |
| --------- | ------ | ------ |
| `model.py` | Added `vulnerability_data` and `aadt_data` parameters | Per-bridge failure probs and per-source generation rates |
| `components.py` | Per-bridge failure probability from VI | Data-driven disaster-weighted breakdown (replaces flat condition dict) |
| `components.py` | Per-source truck generation from AADT | Realistic traffic volumes per road |
| `components.py` | `trucks_crossed` counter on Bridge | Track traffic flow per bridge |
| `model_run.py` | Round 1: simulation + graph connectivity analysis | Combined criticality score |
| `model_run.py` | Round 2: seasonal stochastic failure scenarios | Vulnerability under different disaster conditions |
| `notebook/` | Combined analysis notebook | Priority matrix and visualisations |

---

## Dependencies

- Python **3.10+**
- Mesa **2.1.4**
- NetworkX
- Pandas, NumPy, Matplotlib, Seaborn

---

## Acknowledgements

This project was developed as part of the **EPA133a Advanced Simulation course** at TU Delft.
