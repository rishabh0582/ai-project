import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from collections import defaultdict

from graph import NODES, all_edges, get_neighbors

C = {
    "bg":          "#0f1117",
    "grid":        "#1e2230",
    "edge":        "#2e3555",
    "edge_path":   "#f0a500",
    "edge_expand": "#3a7bd5",
    "node":        "#2e3555",
    "node_normal": "#3a4060",
    "node_expand": "#3a7bd5",
    "node_path":   "#f0a500",
    "node_src":    "#2ecc71",
    "node_dst":    "#e74c3c",
    "node_wp":     "#9b59b6",
    "label":       "#c8cfe8",
    "label_hi":    "#ffffff",
    "title":       "#f0a500",
    "text":        "#a0a8c8",
}

MAX_Y = max(y for _, y in NODES.values())

def _coord(node):
    x, y = NODES[node]
    return x, MAX_Y - y


def _draw_base_graph(ax, expanded_nodes=None, path_edges=None,
                     source=None, destination=None, waypoints=None):
    ax.set_facecolor(C["bg"])

    expanded_set = set(expanded_nodes or [])
    path_set     = set()
    if path_edges:
        path_set = set(path_edges)

    waypoints = set(waypoints or [])

    for a, b, w in all_edges():
        xa, ya = _coord(a)
        xb, yb = _coord(b)
        key = tuple(sorted([a, b]))
        if key in path_set:
            color, lw, zorder, alpha = C["edge_path"], 3.5, 4, 1.0
        elif a in expanded_set or b in expanded_set:
            color, lw, zorder, alpha = C["edge_expand"], 1.2, 3, 0.5
        else:
            color, lw, zorder, alpha = C["edge"], 0.8, 2, 0.35
        ax.plot([xa, xb], [ya, yb], color=color, lw=lw,
                zorder=zorder, alpha=alpha, solid_capstyle="round")

    for node in NODES:
        x, y = _coord(node)

        if node == source:
            color, size, zorder = C["node_src"], 140, 8
        elif node == destination:
            color, size, zorder = C["node_dst"], 140, 8
        elif node in waypoints:
            color, size, zorder = C["node_wp"], 120, 7
        elif node in expanded_set:
            color, size, zorder = C["node_expand"], 90, 6
        else:
            color, size, zorder = C["node_normal"], 60, 5

        ax.scatter(x, y, c=color, s=size, zorder=zorder,
                   edgecolors="#ffffff22", linewidths=0.5)

        label_color = C["label_hi"] if node in (
            {source, destination} | waypoints
        ) else C["label"]
        fontsize   = 6.5 if node not in ({source, destination} | waypoints) else 7.5
        fontweight = "bold" if node in ({source, destination} | waypoints) else "normal"

        ax.annotate(
            node, (x, y),
            textcoords="offset points", xytext=(0, 7),
            fontsize=fontsize, color=label_color,
            fontweight=fontweight, ha="center",
            zorder=9,
            path_effects=[pe.withStroke(linewidth=1.5, foreground=C["bg"])]
        )


def _path_edges(path):
    edges = set()
    for i in range(len(path) - 1):
        edges.add(tuple(sorted([path[i], path[i+1]])))
    return edges


def draw_search_result(result, source, destination, waypoints,
                       heuristic_name="none", save_path="result.png"):

    fig, axes = plt.subplots(1, 2, figsize=(20, 10), facecolor=C["bg"])
    fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.06, wspace=0.06)

    ax_search, ax_path = axes

    ax_search.set_facecolor(C["bg"])
    ax_search.set_aspect("equal")
    ax_search.axis("off")
    ax_search.set_title("Search Expansion", color=C["title"],
                        fontsize=13, fontweight="bold", pad=10)

    _draw_base_graph(ax_search,
                     expanded_nodes=result.frontier_history,
                     source=source, destination=destination,
                     waypoints=waypoints)

    for rank, node in enumerate(result.frontier_history[:20], 1):
        x, y = _coord(node)
        ax_search.annotate(
            str(rank), (x, y),
            textcoords="offset points", xytext=(5, -8),
            fontsize=5.5, color=C["node_expand"], zorder=10,
            path_effects=[pe.withStroke(linewidth=1.2, foreground=C["bg"])]
        )

    ax_path.set_facecolor(C["bg"])
    ax_path.set_aspect("equal")
    ax_path.axis("off")
    ax_path.set_title("Optimal Path Found", color=C["title"],
                      fontsize=13, fontweight="bold", pad=10)

    p_edges = _path_edges(result.path) if result.success else set()
    _draw_base_graph(ax_path,
                     expanded_nodes=result.frontier_history,
                     path_edges=p_edges,
                     source=source, destination=destination,
                     waypoints=waypoints)

    if result.success:
        for step, node in enumerate(result.path, 1):
            x, y = _coord(node)
            ax_path.annotate(
                str(step), (x, y),
                textcoords="offset points", xytext=(6, 6),
                fontsize=6, color=C["edge_path"], fontweight="bold",
                zorder=11,
                path_effects=[pe.withStroke(linewidth=1.5, foreground=C["bg"])]
            )

    legend_items = [
        mpatches.Patch(color=C["node_src"],    label=f"Source: {source}"),
        mpatches.Patch(color=C["node_dst"],    label=f"Destination: {destination}"),
        mpatches.Patch(color=C["node_wp"],     label=f"Waypoints: {', '.join(waypoints) if waypoints else 'none'}"),
        mpatches.Patch(color=C["node_expand"], label=f"Expanded nodes: {result.nodes_expanded}"),
        mpatches.Patch(color=C["edge_path"],   label=f"Path ({len(result.path)} nodes, cost={result.cost:.1f})"),
    ]
    fig.legend(handles=legend_items, loc="lower center",
               ncol=5, fontsize=8, framealpha=0.15,
               facecolor=C["grid"], edgecolor="#ffffff22",
               labelcolor=C["text"])

    h_str  = f" [{heuristic_name}]" if heuristic_name != "none" else ""
    status = "Path Found" if result.success else "No Path"
    title  = (f"{result.algorithm}{h_str}  |  {status}  |  "
              f"Expanded: {result.nodes_expanded}  |  "
              f"Generated: {result.nodes_generated}  |  "
              f"Cost: {result.cost:.1f}")
    fig.suptitle(title, color=C["title"], fontsize=14, fontweight="bold", y=0.95)

    plt.savefig(save_path, dpi=150, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {save_path}")


def draw_comparison(results, source, destination, waypoints, save_path="comparison.png"):

    fig = plt.figure(figsize=(22, 18), facecolor=C["bg"])
    fig.subplots_adjust(left=0.04, right=0.96, top=0.88,
                        bottom=0.14, wspace=0.06, hspace=0.22)

    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.45])
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

    for idx, result in enumerate(results):
        row, col = positions[idx]
        ax = fig.add_subplot(gs[row, col])
        ax.set_facecolor(C["bg"])
        ax.set_aspect("equal")
        ax.axis("off")

        h_str  = f" [{result.heuristic}]" if result.heuristic != "none" else ""
        status = "Yes" if result.success else "No"
        ax.set_title(
            f"{status} {result.algorithm}{h_str}  |  "
            f"Expanded: {result.nodes_expanded}  |  Cost: {result.cost:.1f}",
            color=C["title"], fontsize=10, fontweight="bold", pad=6
        )

        p_edges = _path_edges(result.path) if result.success else set()
        _draw_base_graph(ax,
                         expanded_nodes=result.frontier_history,
                         path_edges=p_edges,
                         source=source, destination=destination,
                         waypoints=waypoints)

    ax_bar = fig.add_subplot(gs[2, :])
    ax_bar.set_facecolor(C["grid"])
    ax_bar.spines[:].set_color(C["edge"])

    labels         = [f"{r.algorithm}\n[{r.heuristic}]" for r in results]
    expanded_vals  = [r.nodes_expanded  for r in results]
    generated_vals = [r.nodes_generated for r in results]

    x = np.arange(len(labels))
    w = 0.35
    bars1 = ax_bar.bar(x - w/2, expanded_vals,  w, label="Nodes Expanded",
                       color=C["node_expand"], alpha=0.85)
    bars2 = ax_bar.bar(x + w/2, generated_vals, w, label="Nodes Generated",
                       color=C["node_wp"],     alpha=0.85)

    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width()/2, h + 0.5,
                    str(int(h)), ha="center", va="bottom",
                    fontsize=9, color=C["label_hi"], fontweight="bold")

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(labels, color=C["label"], fontsize=10)
    ax_bar.tick_params(axis="y", colors=C["text"])
    ax_bar.set_ylabel("Count", color=C["text"], fontsize=10)
    ax_bar.set_title("Algorithm Efficiency Comparison - Empirical Node Counts",
                     color=C["title"], fontsize=11, fontweight="bold")
    ax_bar.legend(fontsize=9, framealpha=0.3, facecolor=C["grid"],
                  labelcolor=C["text"])
    ax_bar.set_facecolor(C["grid"])

    legend_items = [
        mpatches.Patch(color=C["node_src"],    label=f"Source: {source}"),
        mpatches.Patch(color=C["node_dst"],    label=f"Destination: {destination}"),
        mpatches.Patch(color=C["node_wp"],     label=f"Waypoints: {', '.join(waypoints) if waypoints else 'none'}"),
        mpatches.Patch(color=C["node_expand"], label="Expanded nodes"),
        mpatches.Patch(color=C["edge_path"],   label="Final path"),
    ]
    fig.legend(handles=legend_items, loc="upper right",
               fontsize=8.5, framealpha=0.2,
               facecolor=C["grid"], edgecolor="#ffffff22",
               labelcolor=C["text"])

    wp_str = ", ".join(waypoints) if waypoints else "none"
    fig.suptitle(
        f"Route Planner - Algorithm Comparison\n"
        f"Source: {source}  ->  Waypoints: [{wp_str}]  ->  Destination: {destination}",
        color=C["title"], fontsize=14, fontweight="bold", y=0.94
    )

    plt.savefig(save_path, dpi=150, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {save_path}")


def draw_campus_map(save_path="campus_map.png"):
    fig, ax = plt.subplots(figsize=(18, 12), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("BITS Pilani Campus - Road Network Graph",
                 color=C["title"], fontsize=15, fontweight="bold", pad=14)

    _draw_base_graph(ax)

    for a, b, w in all_edges():
        xa, ya = _coord(a)
        xb, yb = _coord(b)
        if w > 80:
            mx, my = (xa+xb)/2, (ya+yb)/2
            ax.text(mx, my, f"{w:.0f}", fontsize=4.5, color=C["text"],
                    ha="center", va="center", zorder=6,
                    path_effects=[pe.withStroke(linewidth=1, foreground=C["bg"])])

    fig.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {save_path}")


if __name__ == "__main__":
    draw_campus_map("outputs/campus_map.png")
    print("Campus map saved.")
