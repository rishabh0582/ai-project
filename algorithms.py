import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional, Callable, FrozenSet

from graph import get_neighbors, all_nodes


@dataclass
class SearchResult:
    path: List[str]
    cost: float
    nodes_expanded: int
    nodes_generated: int
    frontier_history: List[str]
    algorithm: str = ""
    heuristic: str  = "none"
    success: bool   = True

    def summary(self):
        status = "Found" if self.success else "No path"
        return (
            f"[{self.algorithm}] {status} | "
            f"Cost: {self.cost:.1f} | "
            f"Path length: {len(self.path)} nodes | "
            f"Expanded: {self.nodes_expanded} | "
            f"Generated: {self.nodes_generated}"
        )


_FAILURE = SearchResult(
    path=[], cost=float('inf'),
    nodes_expanded=0, nodes_generated=0,
    frontier_history=[], success=False
)


def _reconstruct(came_from, state):
    path_nodes = []
    while state is not None:
        node, _ = state
        path_nodes.append(node)
        state = came_from[state]
    path_nodes.reverse()
    return path_nodes


def _is_goal(node, visited_wps, destination, required_wps):
    return node == destination and visited_wps == required_wps


def _next_visited(node, visited_wps, required_wps):
    if node in required_wps:
        return visited_wps | frozenset([node])
    return visited_wps


def bfs(source: str, destination: str, waypoints: List[str],
        heuristic_fn=None) -> SearchResult:

    required_wps = frozenset(waypoints)
    init_state   = (source, frozenset())

    if _is_goal(source, frozenset(), destination, required_wps):
        return SearchResult([source], 0.0, 0, 1, [source], "BFS", "none")

    frontier    = deque([(init_state, 0.0)])
    came_from   = {init_state: None}
    cost_so_far = {init_state: 0.0}
    expanded    = 0
    generated   = 1
    history     = []

    while frontier:
        (node, visited_wps), cost = frontier.popleft()
        expanded += 1
        history.append(node)

        for neighbor, edge_w in get_neighbors(node):
            new_visited = _next_visited(neighbor, visited_wps, required_wps)
            new_state   = (neighbor, new_visited)

            if new_state not in came_from:
                came_from[new_state]   = (node, visited_wps)
                new_cost               = cost + edge_w
                cost_so_far[new_state] = new_cost
                generated += 1

                if _is_goal(neighbor, new_visited, destination, required_wps):
                    path = _reconstruct(came_from, new_state)
                    return SearchResult(
                        path, new_cost, expanded, generated, history, "BFS", "none"
                    )
                frontier.append((new_state, new_cost))

    result = SearchResult.__new__(SearchResult)
    result.__dict__.update(_FAILURE.__dict__)
    result.nodes_expanded  = expanded
    result.nodes_generated = generated
    result.algorithm       = "BFS"
    return result


def ucs(source: str, destination: str, waypoints: List[str],
        heuristic_fn=None) -> SearchResult:

    required_wps = frozenset(waypoints)
    init_state   = (source, frozenset())

    counter     = 0
    frontier    = [(0.0, counter, init_state)]
    came_from   = {init_state: None}
    cost_so_far = {init_state: 0.0}
    expanded    = 0
    generated   = 1
    history     = []

    while frontier:
        g, _, (node, visited_wps) = heapq.heappop(frontier)
        state = (node, visited_wps)

        if g > cost_so_far.get(state, float('inf')):
            continue

        expanded += 1
        history.append(node)

        if _is_goal(node, visited_wps, destination, required_wps):
            path = _reconstruct(came_from, state)
            return SearchResult(
                path, g, expanded, generated, history, "UCS", "none"
            )

        for neighbor, edge_w in get_neighbors(node):
            new_visited = _next_visited(neighbor, visited_wps, required_wps)
            new_state   = (neighbor, new_visited)
            new_cost    = g + edge_w

            if new_cost < cost_so_far.get(new_state, float('inf')):
                cost_so_far[new_state] = new_cost
                came_from[new_state]   = state
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, new_state))
                generated += 1

    result = SearchResult.__new__(SearchResult)
    result.__dict__.update(_FAILURE.__dict__)
    result.nodes_expanded  = expanded
    result.nodes_generated = generated
    result.algorithm       = "UCS"
    return result


def astar(source: str, destination: str, waypoints: List[str],
          heuristic_fn: Callable) -> SearchResult:

    required_wps  = frozenset(waypoints)
    unvisited_now = required_wps
    init_state    = (source, frozenset())

    h_init = heuristic_fn(source, destination, unvisited_now)

    counter     = 0
    frontier    = [(h_init, counter, 0.0, init_state)]
    came_from   = {init_state: None}
    cost_so_far = {init_state: 0.0}
    expanded    = 0
    generated   = 1
    history     = []

    while frontier:
        f, _, g, (node, visited_wps) = heapq.heappop(frontier)
        state = (node, visited_wps)

        if g > cost_so_far.get(state, float('inf')):
            continue

        expanded += 1
        history.append(node)

        if _is_goal(node, visited_wps, destination, required_wps):
            path = _reconstruct(came_from, state)
            return SearchResult(
                path, g, expanded, generated, history,
                "A*", getattr(heuristic_fn, '__name__', 'h')
            )

        for neighbor, edge_w in get_neighbors(node):
            new_visited   = _next_visited(neighbor, visited_wps, required_wps)
            new_state     = (neighbor, new_visited)
            new_g         = g + edge_w
            unvisited_rem = required_wps - new_visited

            if new_g < cost_so_far.get(new_state, float('inf')):
                cost_so_far[new_state] = new_g
                came_from[new_state]   = state
                h_val = heuristic_fn(neighbor, destination, unvisited_rem)
                f_val = new_g + h_val
                counter += 1
                heapq.heappush(frontier, (f_val, counter, new_g, new_state))
                generated += 1

    result = SearchResult.__new__(SearchResult)
    result.__dict__.update(_FAILURE.__dict__)
    result.nodes_expanded  = expanded
    result.nodes_generated = generated
    result.algorithm       = "A*"
    return result


def greedy(source: str, destination: str, waypoints: List[str],
           heuristic_fn: Callable) -> SearchResult:

    required_wps  = frozenset(waypoints)
    init_state    = (source, frozenset())
    unvisited_now = required_wps

    h_init = heuristic_fn(source, destination, unvisited_now)

    counter      = 0
    frontier     = [(h_init, counter, 0.0, init_state)]
    came_from    = {init_state: None}
    cost_tracker = {init_state: 0.0}
    explored     = set()
    expanded     = 0
    generated    = 1
    history      = []

    while frontier:
        h, _, g, (node, visited_wps) = heapq.heappop(frontier)
        state = (node, visited_wps)

        if state in explored:
            continue
        explored.add(state)

        expanded += 1
        history.append(node)

        if _is_goal(node, visited_wps, destination, required_wps):
            path = _reconstruct(came_from, state)
            return SearchResult(
                path, g, expanded, generated, history,
                "Greedy", getattr(heuristic_fn, '__name__', 'h')
            )

        for neighbor, edge_w in get_neighbors(node):
            new_visited   = _next_visited(neighbor, visited_wps, required_wps)
            new_state     = (neighbor, new_visited)
            unvisited_rem = required_wps - new_visited

            if new_state not in explored:
                new_g = g + edge_w
                if new_state not in came_from:
                    came_from[new_state]    = state
                    cost_tracker[new_state] = new_g
                h_val = heuristic_fn(neighbor, destination, unvisited_rem)
                counter += 1
                heapq.heappush(frontier, (h_val, counter, new_g, new_state))
                generated += 1

    result = SearchResult.__new__(SearchResult)
    result.__dict__.update(_FAILURE.__dict__)
    result.nodes_expanded  = expanded
    result.nodes_generated = generated
    result.algorithm       = "Greedy"
    return result


ALGO_MAP = {
    "bfs":    bfs,
    "ucs":    ucs,
    "astar":  astar,
    "greedy": greedy,
}

def run_algorithm(name: str, source: str, destination: str,
                  waypoints: List[str], heuristic_fn=None) -> SearchResult:
    fn = ALGO_MAP.get(name.lower())
    if fn is None:
        raise ValueError(f"Unknown algorithm '{name}'. Choose from {list(ALGO_MAP)}")
    return fn(source, destination, waypoints, heuristic_fn)


if __name__ == "__main__":
    from heuristics import h1, h2

    src, dst = "Main Gate", "Library"
    wps = ["SAC", "ANC"]

    for algo_name, algo_fn in [("bfs", bfs), ("ucs", ucs)]:
        r = algo_fn(src, dst, wps)
        print(r.summary())
        print(f"  Path: {' -> '.join(r.path)}\n")

    for algo_name, algo_fn, h_fn, h_name in [
        ("astar",  astar,  h1, "h1"),
        ("astar",  astar,  h2, "h2"),
        ("greedy", greedy, h1, "h1"),
        ("greedy", greedy, h2, "h2"),
    ]:
        r = algo_fn(src, dst, wps, h_fn)
        r.heuristic = h_name
        print(r.summary())
        print(f"  Path: {' -> '.join(r.path)}\n")
