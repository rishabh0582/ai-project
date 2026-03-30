import math
from graph import node_coords


def euclidean(a, b):
    ax, ay = node_coords(a)
    bx, by = node_coords(b)
    return math.hypot(bx - ax, by - ay)


def h1(current, goal, unvisited_waypoints):
    return euclidean(current, goal)


def _mst_cost(nodes):
    nodes = list(nodes)
    n = len(nodes)
    if n <= 1:
        return 0.0

    in_mst = [False] * n
    key    = [math.inf] * n
    key[0] = 0.0
    total  = 0.0

    for _ in range(n):
        u = min((i for i in range(n) if not in_mst[i]), key=lambda i: key[i])
        in_mst[u] = True
        total += key[u]
        for v in range(n):
            if not in_mst[v]:
                d = euclidean(nodes[u], nodes[v])
                if d < key[v]:
                    key[v] = d

    return total


def h2(current, goal, unvisited_waypoints):
    if not unvisited_waypoints:
        return euclidean(current, goal)

    mst = _mst_cost(set(unvisited_waypoints))
    d_current_to_wp = min(euclidean(current, wp) for wp in unvisited_waypoints)
    d_goal_to_wp    = min(euclidean(goal, wp)    for wp in unvisited_waypoints)

    return mst + d_current_to_wp + d_goal_to_wp


def get_heuristic(name):
    if name == "h1":
        return h1
    elif name == "h2":
        return h2
    else:
        raise ValueError(f"Unknown heuristic '{name}'. Choose 'h1' or 'h2'.")


if __name__ == "__main__":
    current = "Main Gate"
    goal    = "Library"
    wps     = frozenset(["SAC", "ANC"])

    print(f"h1({current}, {goal}, {set(wps)}) = {h1(current, goal, wps):.2f}")
    print(f"h2({current}, {goal}, {set(wps)}) = {h2(current, goal, wps):.2f}")

