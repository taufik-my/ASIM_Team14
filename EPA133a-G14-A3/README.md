# EPA133a – Assignment 3

## Network Model Generation: Bridge Failure Impact on Bangladesh Road Network

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

This project implements a **data-driven agent-based simulation model** using **Mesa 2.1.4** and **NetworkX** to study the impact of **bridge failures on freight travel time** across a multi-road network in Bangladesh.

The model includes **9 national roads** (N1, N2, N102, N104, N105, N106, N204, N207, N208) connected via intersections. Vehicles are generated at both ends of each road and routed to a **random destination** via the **shortest path** computed by NetworkX.

Five scenarios with increasing bridge breakdown probabilities are simulated, each with 10 replications using different seeds.

---

## Project Structure

```
EPA133a-G14-A3
│
├── data/
│   ├── network_data.csv              # Input data for model generation (9 roads)
│   ├── _roads3.csv                   # Raw road dataset
│   ├── BMMS_overview.xlsx            # Bridge metadata
│   ├── gis/                          # GIS shapefiles (for bonus intersection analysis)
│   └── README.md
│
├── experiment/
│   ├── scenario 0.csv                # Baseline: no breakdowns
│   ├── scenario 1.csv                # D=5%
│   ├── scenario 2.csv                # C=5%, D=10%
│   ├── scenario 3.csv                # B=5%, C=10%, D=20%
│   ├── scenario 4.csv                # A=5%, B=10%, C=20%, D=40%
│   └── scenario N bridges.csv        # Bridge delay data per scenario
│
├── img/                              # Generated figures for report
│
├── model/
│   ├── model.py                      # Main model (Mesa + NetworkX)
│   ├── components.py                 # Agent definitions (Bridge, Vehicle, etc.)
│   ├── model_run.py                  # Experiment runner (5 scenarios x 10 reps)
│   ├── model_viz.py                  # Visualization server
│   ├── mesa_networkx_flowchart.py    # Generates MESA-NetworkX flowchart diagram
│   ├── README.md
│   └── ContinuousSpace/             # Custom visualization module
│
├── notebook/
│   ├── network_data_preparation.ipynb  # Data cleaning and preparation
│   ├── network_drawing.ipynb           # Network visualization (NetworkX)
│   └── experiment_analysis.ipynb       # Results analysis and figures
│
├── report/
│
└── README.md                         # This file
```

---

## How to Reproduce the Results

### Prerequisites

- Python **3.10+**
- Install dependencies:

```
pip install -r requirements.txt
pip install networkx
```

### 1. Data Preparation

The input data file is already prepared:

```
data/network_data.csv
```

To see how it was prepared, refer to `notebook/network_data_preparation.ipynb`.

### 2. Run the Experiments

From the `model/` directory:

```
python model_run.py
```

This runs **5 scenarios × 10 replications** (≈25 minutes) and saves results to `experiment/`.

### 3. Analyze Results

Run the notebook:

```
notebook/experiment_analysis.ipynb
```

This generates comparison plots (boxplots, histograms, bar charts) saved to `img/`.

### 4. Visualize the Network

Run the notebook:

```
notebook/network_drawing.ipynb
```

This shows the road network layout with geographic coordinates.

### 5. Run with Visualization (Optional)

```
python model/model_viz.py
```

Opens a browser-based visualization at `http://localhost:8521`. Not used during experiments.

---

## Simulation Description

- Trucks generated **every 5 minutes** from each road endpoint (18 SourceSinks)
- Each tick = **1 minute**; total runtime = **5 days** (7,200 ticks)
- Average speed: **48 km/h** (800 m/min)
- Vehicles pick a **random destination** and follow the **shortest path** via NetworkX
- Discovered paths are **cached** for performance

### Bridge Breakdown

Bridges may break down based on their condition category (A/B/C/D) and scenario probabilities. Delay depends on bridge length:

| Bridge Length | Delay Distribution        |
| ------------ | ------------------------- |
| > 200 m      | Triangular(1, 2, 4) hours |
| 50–200 m     | Uniform(45, 90) minutes   |
| 10–50 m      | Uniform(15, 60) minutes   |
| < 10 m       | Uniform(10, 20) minutes   |

### Scenarios

| Scenario | Cat A % | Cat B % | Cat C % | Cat D % |
| -------- | ------- | ------- | ------- | ------- |
| 0        | 0       | 0       | 0       | 0       |
| 1        | 0       | 0       | 0       | 5       |
| 2        | 0       | 0       | 5       | 10      |
| 3        | 0       | 5       | 10      | 20      |
| 4        | 5       | 10      | 20      | 40      |

---

## Key Changes from Demo Code

| Component        | Change                                      | Reason                                      |
| ---------------- | ------------------------------------------- | ------------------------------------------- |
| `model.py`       | NetworkX graph integration                  | Shortest-path routing across road network   |
| `model.py`       | Dynamic road reading from CSV               | Extensible to any number of roads           |
| `model.py`       | Random routing with path caching            | Vehicles drive to random destinations       |
| `model.py`       | Trip data collection and CSV export         | Measure travel time and delays              |
| `components.py`  | Condition-based bridge breakdown            | Delays depend on bridge category and length |
| `components.py`  | Vehicle tracking (waiting time, bridges)    | Per-trip statistics for analysis            |
| `model_run.py`   | Multi-scenario experiment runner            | 5 scenarios × 10 replications              |

---

## Dependencies

- Python **3.10+**
- Mesa **2.1.4**
- NetworkX
- Pandas, Matplotlib, Seaborn (for analysis)

---

## Acknowledgements

This project was developed as part of the **EPA133a Advanced Simulation course** at TU Delft.

