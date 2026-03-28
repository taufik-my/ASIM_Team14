# Transport Network Model in MESA + NetworkX

Created by: EPA133a Group 14

## Introduction

An agent-based transport simulation model using Mesa 2.1.4 and NetworkX for EPA133a Assignment 3. Simulates freight traffic across 9 national roads in Bangladesh (N1, N2, N102, N104, N105, N106, N204, N207, N208).

Vehicles are generated at both ends of each road (SourceSinks) and routed to random destinations via NetworkX shortest-path. Bridge breakdowns cause delays based on condition category and bridge length.

## How to Use

- Create and activate a virtual environment, then install dependencies:

```
pip install -r requirements.txt
pip install networkx
```

- Run the full experiments (5 scenarios × 10 replications):

```
python model_run.py
```

Results are saved to `../experiment/`.

- Launch the visualization (optional):

```
python model_viz.py
```

## Files

- [model.py](model.py): Contains `BangladeshModel`, a subclass of Mesa `Model`. Reads `network_data.csv` to generate the road network. Builds a **NetworkX graph** for cross-road shortest-path routing. Vehicles pick random destinations, and discovered paths are cached in `path_ids_dict`. Accepts `breakdown_probs` parameter for scenario-based bridge failures. Includes `record_trip()` and `export_data()` for collecting travel time statistics.

- [components.py](components.py): Contains agent definitions:
  - **Infra** — base class for all infrastructure (length, position, vehicle count)
  - **Bridge** — breaks down based on condition probability; delay varies by bridge length
  - **Link** — passive road segment
  - **Intersection** — junction connecting different roads (shared IDs)
  - **Source / Sink / SourceSink** — generate and remove vehicles
  - **Vehicle** — drives along path at 48 km/h, waits at broken bridges, tracks travel and waiting time

- [model_run.py](model_run.py): Experiment runner. Configures 5 scenarios with different bridge breakdown probabilities, runs 10 replications each with different seeds, and exports trip data CSVs.

- [model_viz.py](model_viz.py): Sets up the browser-based Mesa visualization. Not used during experiments.

- [mesa_networkx_flowchart.py](mesa_networkx_flowchart.py): Generates the MESA–NetworkX data exchange flowchart diagram. Outputs PNG and PDF to `../img/`.

- [ContinuousSpace](ContinuousSpace): Custom visualization module for continuous canvas with geographic coordinates. Editing NOT recommended.
