# EPA133a – Assignment 2

## Data-Driven Transport Simulation for Bridge Failures in Bangladesh

**Created by: EPA133a Team 14**


| Name                 | Student Number |
| -------------------- | -------------- |
| Bayu Jamalullael     | 6367984        |
| Brenda Escobar       | 6512191        |
| Brian Parsaoran      | 6147674        |
| Taufik Muhamad Yusup | 6378056        |
| Zhafran Sidik        | 565841         |

---

# Project Overview

This project implements a **data-driven agent-based simulation model** using **Mesa 2.1.4** to study the impact of **bridge failures and maintenance conditions on freight travel time** along the **N1 highway between Chittagong and Dhaka, Bangladesh**.

The model automatically generates a road network from processed infrastructure data and simulates trucks traveling along the highway. Bridge breakdown probabilities are varied across scenarios to analyze their effects on **average travel time**.

The simulation runs multiple scenarios and exports results that are later analyzed and visualized.

---

# Project Structure

```
EPA133a-G14-A2
│
├── data
│   ├── _roads3.csv
│   ├── BMMS_overview.xlsx
│   ├── demo-1.csv
│   ├── demo-2.csv
│   ├── demo-3.csv
│   ├── df_road_file.csv          # Generated input file for the model
│   └── README.md
│
├── experiment
│
├── img
│
├── model
│   ├── components.py
│   ├── model.py
│   ├── model_run.py
│   ├── model_viz.py
│   └── ContinuousSpace/
│
├── notebook
│   ├── clean_roads_and_bridges.ipynb
│   └── data_analysis_visualization.ipynb
│
├── report
│
└── README.md
```

---

# How to Reproduce the Results

The workflow consists of **three main steps**.

## 1. Generate the Model Input Data

Run the notebook:

```
notebook/clean_roads_and_bridges.ipynb
```

This notebook processes the raw road and bridge dataset and generates the file:

```
data/df_road_file.csv
```

This file contains the cleaned infrastructure data used to automatically generate the simulation model.

---

## 2. Run the Simulation Experiments

Run the script:

```
model/model_run.py
```

This script:

* builds the Mesa simulation model
* runs the experiments for **Scenario 0 – Scenario 8**
* performs **10 replications per scenario**
* exports results to the folder:

```
experiment/
```

Output files include:

```
scenario0.csv
scenario1.csv
...
scenario8.csv

bonus-scenario0.csv
bonus-scenario1.csv
...
bonus-scenario8.csv
```

Each file contains the recorded travel times for trucks in that scenario and also for the bonus question 1.

---

## 3. Analyze and Visualize Results

Run the notebook:

```
notebook/data_analysis_visualization.ipynb
```

This notebook:

* loads the simulation output files
* generates plots comparing the scenarios
* produces the figures used in the final report

---

# Running the Model with Visualization (Optional)

The visualization interface can be launched using:

```
model/model_viz.py
```

This opens a browser-based Mesa visualization showing trucks moving through the generated road network.

Note: Visualization is **not used during the experiments**, since experiments are run in batch mode using `model_run.py`.

---

# Simulation Description

* Trucks are generated **every 5 minutes**
* Each simulation tick represents **1 minute**
* Trucks travel from **Chittagong to Dhaka**
* Average speed is **48 km/h**
* Bridge delays occur when bridges break down according to scenario probabilities

Bridge delay distributions depend on bridge length:

| Bridge Length | Delay Distribution      |
| ------------- | ----------------------- |
| > 200 m       | Triangular(1,2,4) hours |
| 50–200 m      | Uniform(45,90) minutes  |
| 10–50 m       | Uniform(15,60) minutes  |
| < 10 m        | Uniform(10,20) minutes  |

---

# Output

The primary model output is:

**Truck travel time from Chittagong to Dhaka**

Results are stored in:

```
experiment/scenarioX.csv
experiment/bonus-scenarioX.csv
```

These files are used for statistical analysis and comparison across scenarios.

---

# Dependencies

The project was developed using:

* Python **3.11**
* Mesa **2.1.4**

Install dependencies using:

```
pip install -r requirements.txt
```

---

# Acknowledgements

This project was developed as part of the **EPA133a Advanced Simulation course**.

AI tools were used to assist with documentation and debugging during development. All modeling decisions, implementation, and analysis were performed by the group members.

---

If you want, I can also help you make a **much stronger README that TAs love (with badges, reproducibility section, and clearer instructions)** — it can easily bump the rubric score.
