import argparse
import os
import sys

from graph      import all_nodes
from algorithms import run_algorithm, ALGO_MAP
from heuristics import get_heuristic
from visualizer import draw_search_result, draw_campus_map

os.makedirs("outputs", exist_ok=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Route Planner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --src "Main Gate" --dst "Library"
  python main.py --src "Main Gate" --dst "Library" --waypoints "SAC,ANC" --algo astar --heuristic h2
  python main.py --list-nodes
  python main.py --draw-map
        """
    )
    parser.add_argument("--src",        type=str, default="Main Gate",
                        help="Source node name (default: 'Main Gate')")
    parser.add_argument("--dst",        type=str, default="Library",
                        help="Destination node name (default: 'Library')")
    parser.add_argument("--waypoints",  type=str, default="",
                        help="Comma-separated waypoint names (e.g. 'SAC,ANC')")
    parser.add_argument("--algo",       type=str, default="astar",
                        choices=list(ALGO_MAP.keys()),
                        help="Algorithm to run (default: astar)")
    parser.add_argument("--heuristic",  type=str, default="h2",
                        choices=["h1", "h2"],
                        help="Heuristic for informed algorithms (default: h2)")
    parser.add_argument("--output",     type=str, default=None,
                        help="Output image path (default: outputs/<algo>_result.png)")
    parser.add_argument("--list-nodes", action="store_true",
                        help="Print all available node names and exit")
    parser.add_argument("--draw-map",   action="store_true",
                        help="Draw and save the campus road network map")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list_nodes:
        nodes = sorted(all_nodes())
        print(f"\nAvailable nodes ({len(nodes)} total):\n")
        for i, n in enumerate(nodes, 1):
            print(f"  {i:2}. {n}")
        return

    if args.draw_map:
        out = "outputs/campus_map.png"
        draw_campus_map(out)
        print(f"Campus map saved to {out}")
        return

    valid_nodes = set(all_nodes())
    src = args.src.strip()
    dst = args.dst.strip()
    wps = [w.strip() for w in args.waypoints.split(",") if w.strip()]

    errors = []
    if src not in valid_nodes:
        errors.append(f"Source '{src}' not found. Use --list-nodes to see valid names.")
    if dst not in valid_nodes:
        errors.append(f"Destination '{dst}' not found.")
    for wp in wps:
        if wp not in valid_nodes:
            errors.append(f"Waypoint '{wp}' not found.")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    h_fn   = None
    h_name = "none"
    if args.algo in ("astar", "greedy"):
        h_fn   = get_heuristic(args.heuristic)
        h_name = args.heuristic

    print(f"\nRoute Planner")
    print(f"  Algorithm   : {args.algo.upper()} {'[' + h_name + ']' if h_name != 'none' else ''}")
    print(f"  Source      : {src}")
    print(f"  Destination : {dst}")
    print(f"  Waypoints   : {wps if wps else 'none'}")
    print()

    result = run_algorithm(args.algo, src, dst, wps, h_fn)
    result.heuristic = h_name

    print(result.summary())
    if result.success:
        print(f"\nPath ({len(result.path)} nodes):")
        for i, node in enumerate(result.path):
            marker = ""
            if node == src:        marker = "  <- START"
            elif node == dst:      marker = "  <- GOAL"
            elif node in set(wps): marker = "  <- WAYPOINT"
            print(f"  {i+1:2}. {node}{marker}")
    else:
        print("No path found between the given source and destination.")

    out = args.output or f"outputs/{args.algo}_{h_name}_result.png"
    draw_search_result(result, src, dst, wps, h_name, out)
    print(f"\nVisualization saved to: {out}")


if __name__ == "__main__":
    main()
