# Route Planner 
## Assignment D3 | Project 3 (L2) | Group 19
---

## Team Members

1. Rishabh Mohan: 2023A7PS0489P
2. Manthan Haritash: 2023A7PS0666P
3. Aryan Singh Sirohi: 2023A1PS0173P
4. Uday Singhania: 2023A3PS0371P
---

## Overview

An intelligent navigation agent that finds optimal routes in the BITS Pilani campus map implemented as a weighted undirected graph. The agent supports multi-stop route planning (L2) ie it can visit a set of required waypoints in any order before reaching the final destination. The agent determines the optimal order of visiting waypoints automatically.

### Algorithms Implemented

1. BFS: Uninformed, Not optimal, Complete
2. UCS: Uninformed, Optimal, Complete
3. A*: Informed, Optimal (admissible h), Complete
4. Greedy Best First Search: Informed, Not Optimal, Complete

### Heuristics Implemented

1. h1: Euclidean distance to goal (Admissible and Consistent)
2. h2: MST lower bound over unvisited waypoints (Admissible and Consistent)

## Setup

### Requirements
- Python 3.xx
- `matplotlib`, `numpy` libraries

### Install dependencies

pip install matplotlib numpy 


### Project structure

Folder/
├── graph.py         # Campus road network (nodes, edges, weights)
├── heuristics.py    # h1 (Euclidean) and h2 (MST lower bound)
├── algorithms.py    # BFS, UCS, A*, Greedy search implementations
├── visualizer.py    # Matplotlib based graph and result visualizations
├── main.py          # CLI 
├── README.md
└── outputs/         # Generated images saved here

---

## Usage

### List all available campus nodes
python main.py --list-nodes

### Draw the campus road network
python main.py --draw-map

### Single query (default: A* h2, Main Gate --> Library)
python main.py

### Custom query
python main.py --src "XXX" --dst "XXX" --waypoints "XXX,XXX" --algo "XXX" --heuristic "XX"

### Flags and Values

1. --src: Any node
2. --dst Any node
3. --waypoints: "Any set of nodes,seperate by commas,with no space in between"
4. --algo: `bfs`, `ucs`, `astar`, `greedy`
5. --heuristic: `h1`, `h2` (only used by astar and greedy)

---

## Campus Graph

The graph models the BITS Pilani campus with:
- 43 named nodes: hostels, academic buildings, gates, amenities
- ~60 edges: road connections with Euclidean pixel-distance weights
- Coordinates: derived from the official campus map image  

---

## State Representation

Following the D1 formulation:
state = (current_node, frozenset_of_visited_waypoints)

- Initial state: `(source, frozenset())`
- Goal test: `node == destination AND visited_waypoints == required_waypoints`
- State space size: |V| × 2^|R| where |R| = number of required waypoints

---

## Output Files

All images are saved to the `outputs/` directory:
- `campus_map.png`: Raw campus graph with all nodes and labels
- `<algo>_<heuristic>_result.png`: Individual algorithm result (expansion + path)

---

## Empirical Results vs. D2 Predictions

1. BFS:
--> O(b^d) time & space (D2 Prediction)
--> Expands nodes based on depth (ignores weights); produces non-optimal paths on weighted graphs (Empirical Observation)

2. UCS:
--> O(b^(1+C*/ε)) (D2 Prediction)
--> Returns same optimal cost as A*; expands more nodes than A* (Empirical Observation)

3. A* (h2):
--> O((b*)^d), b* < b (D2 Prediction)
--> Fewest expansions among optimal algorithms; h2 > h1 (Empirical Observation)

4. Greedy (h2):
--> O(b^m) worst case (D2 Prediction)
--> Fast but suboptimal; Often expands fewer nodes but may explore to suboptimal paths (Empirical Observation)

---

## Key Observations

- A* with h2 provides optimal solutions with significantly fewer node expansions.
- UCS and A* yield identical optimal costs.
- Greedy is faster but may produce suboptimal paths.
- BFS performs poorly on weighted graphs.

