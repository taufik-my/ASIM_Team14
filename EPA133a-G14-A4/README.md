# EPA133a-G14-A4: Network Analysis

## Assignment 4 — Vulnerability and Criticality Analysis of Bangladesh's N1/N2 Transport Network

### Overview
This project analyses the vulnerability and criticality of Bangladesh's N1/N2 road network using Mesa agent-based simulation and NetworkX shortest-path routing. It builds on the Assignment 3 model with:
- Data-driven bridge failure probabilities (condition × disaster exposure)
- Per-source truck generation rates (from RMMS AADT data)
- Bridge removal experiments for criticality analysis
- Iterative experiment design (4 rounds)

### Project Structure
```
EPA133a-G14-A4/
├── data/
│   ├── raw/                     # Original data files
│   │   ├── network_data.csv     # Road network components
│   │   └── BMMS_overview.xlsx   # Bridge condition data
│   └── processed/               # Enriched data with failure probabilities
├── model/                       # Simulation model (Mesa + NetworkX)
│   ├── model.py                 # BangladeshModel
│   ├── components.py            # Agent classes (Bridge, Vehicle, Source, etc.)
│   ├── model_run.py             # Experiment runner
│   └── model_viz.py             # Mesa visualisation server
├── experiment/                  # Experiment output CSVs
│   ├── round1_baseline/
│   ├── round2_bridge_removal/
│   ├── round3_stochastic_failure/
│   └── round4_combined_analysis/
├── notebook/                    # Jupyter notebooks for analysis
├── img/                         # Generated visualisation images
├── report/                      # Final report PDF
└── requirements.txt
```

### How to Run

#### Prerequisites
```bash
pip install -r requirements.txt
```

#### Run the simulation (from model/ directory)
```bash
cd model
python model_run.py
```

#### Run with visualisation
```bash
cd model
python model_viz.py
```

#### Run analysis notebooks
```bash
jupyter notebook notebook/
```

### Team
Group 14 — EPA133a Advanced Simulation, TU Delft
