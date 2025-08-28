
Project: Bristol Medical UAV Deliver & Charging Strategy Simulation (Python)


(1) Project Overview

This archive contains the full source code used to generate the dissertation
results on UAV routing, energy consumption, and charging-strategy comparison.

Core capabilities:
- Shortest-path search (A* / Dijkstra) on a 2D map
- Energy model (battery, payload, distance-based consumption)
- Charging strategy simulation 
- Strategy selection wrapper and batch runs
- Output of distances, flight time estimation, energy use, and charge count


(2) Directory Layout

├─ code/                          
│  ├─ main.py               # Entry script: orchestrates full simulation
│  ├─ Astart.py             # A* path planning implementation
│  ├─ Dijkstra.py           # Dijkstra shortest path implementation
│  ├─ map.py                # Map, nodes, connectivity, obstacles
│  ├─ Distance_calculate.py # Distance and cost calculation utilities
│  ├─ battery.py            # Battery model (capacity, SOC updates)
│  ├─ payload.py            # Payload model (mass and energy impact)
│  ├─ Charge.py             # Charging/swap logic and counters
│  ├─ AltaX.py              # Alta X UAV platform parameters
│  ├─ Strategy_Choose.py    # Wrapper for selecting strategy and algorithm
│  ├─ temdecrease.py        # Cooling/annealing schedule utilities
│  └─ deal.py               # Helper functions for data/results processing
├─ data/                    # (Optional) input or demo data
├─ results/                 # Outputs 



(3) Key Files

- main.py: Orchestrates end-to-end run (map, UAV, routing, charging, output).
- Astart.py: A* search algorithm.
- Dijkstra.py: Dijkstra algorithm.
- map.py: Map definition, nodes, edges, obstacles.
- Distance_calculate.py: Distance and edge-cost functions.
- battery.py: Battery capacity, SOC updates, energy consumption.
- payload.py: Payload effects on consumption.
- Charge.py: Charging/swap station logic, counts, timing.
- AltaX.py: UAV platform parameters.
- Strategy_Choose.py: Unified interface for algorithms and strategies.
- temdecrease.py: Annealing/cooling helpers.
- deal.py: Data post-processing and export.

(4) How to Run

Environment:
- Suggested dependencies: numpy, matplotlib, networkx, pandas

Common options (if defined in main.py, adjust as needed):
    --algo {astar,dijkstra}       # Path planning algorithm
    --strategy {fixed,swap,hot}   # Charging strategy
    --map <map_file>              # Map file or name
    --payload <kg>                # Payload mass
    --battery <Wh>                # Battery capacity
    --out ../results              # Output directory

Outputs:
- results/metrics.csv        # Summary of distance, time, energy, charges
- results/figures/*.png      # Plots (strategy comparison, SOC curves)
- results/logs/*.txt         # Logs


(5) Result Example 

A* and 1 - Strategy A: Return to charge after each mission, then depart with a full battery.
Return Value 2 (Total Flight Time): 699.00 minutes
Return Value 3 (Total Energy Consumed): 66.17 Ah
Return Value 4 (Total Segments): 90


A* and 2-Strategy B: Return to charge after completing two missions, then depart with a full
battery.
Return Value 2 (Total Flight Time): 463.00 minutes
Return Value 3 (Total Energy Consumed): 43.83 Ah
Return Value 4 (Total Segments): 58


Dijkstra and 1 - Strategy A: Return to charge after each mission, then depart with a full battery.
Return Value 2 (Total Flight Time): 653.00 minutes
Return Value 3 (Total Energy Consumed): 61.82 Ah
Return Value 4 (Total Segments): 91


Dijkstra and 2-Strategy B: Return to charge after completing two missions, then depart with a full
battery.
Return Value 2 (Total Flight Time): 463.00 minutes
Return Value 3 (Total Energy Consumed): 43.83 Ah
Return Value 4 (Total Segments): 58






