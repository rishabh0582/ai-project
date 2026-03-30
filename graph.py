import math

NODES = {
    # Gates / Entrances
    "Main Gate":        (645, 755),
    "VFAST":            (645, 635),

    # South / Central zone
    "CVR":              (750, 590),
    "Swimming Pool":    (730, 700),
    "ANC":              (570, 490),
    "Med-C Grounds":    (430, 555),
    "Med-C":            (510, 490),
    "Gym Grounds":      (555, 525),
    "Akshay":           (480, 490),
    "C-not":            (370, 525),
    "Alumni Home":      (275, 500),

    # Hostels - South row
    "Ashok":            (635, 540),
    "Rana Pratap":      (720, 540),
    "Bhagirath":        (680, 480),
    "Vishwakarma":      (750, 490),

    # Hostels - Middle row
    "Vyas":             (510, 415),
    "Shankar":          (590, 415),
    "Gandhi":           (665, 415),
    "Krishna":          (740, 415),

    # Academic / Admin - Core
    "LTC":              (1070, 600),
    "Library":          (1080, 520),
    "FD1":              (970, 530),
    "FD2":              (970, 415),
    "FD3":              (1030, 260),
    "Old Workshop":     (900, 490),
    "New Workshop":     (1085, 370),

    # Central academic strip
    "IPC":              (800, 355),
    "NAB":              (830, 305),
    "Main Audi":        (1000, 330),
    "IC":               (1055, 330),
    "SR":               (1120, 345),

    # North zone
    "SAC":              (760, 195),
    "Budh":             (800, 250),
    "Ram":              (880, 250),
    "Sky Lawns":        (1020, 185),
    "Birla Museum":     (1005, 215),
    "Sky Lab":          (1100, 215),

    # West zone
    "Meera":            (430, 195),
    "Birla Shishu Vihar": (380, 290),
    "Saraswati Mandir": (450, 335),
    "Shiv Ganga":       (310, 335),
    "South Park":       (610, 300),

    # UCO Bank / Post Office area
    "UCO Bank":         (820, 590),
}

def euclidean(a, b):
    ax, ay = NODES[a]
    bx, by = NODES[b]
    return math.hypot(bx - ax, by - ay)

_EDGE_LIST = [
    ("Main Gate",    "VFAST"),
    ("VFAST",        "CVR"),
    ("CVR",          "UCO Bank"),
    ("UCO Bank",     "Rana Pratap"),
    ("Rana Pratap",  "Vishwakarma"),
    ("Rana Pratap",  "Ashok"),
    ("Ashok",        "ANC"),
    ("ANC",          "Bhagirath"),
    ("Bhagirath",    "Vishwakarma"),
    ("CVR",          "Swimming Pool"),
    ("Swimming Pool","Main Gate"),
    ("ANC",          "Med-C"),
    ("Med-C",        "Med-C Grounds"),
    ("Med-C",        "Akshay"),
    ("Akshay",       "Med-C Grounds"),
    ("Akshay",       "C-not"),
    ("C-not",        "Alumni Home"),
    ("ANC",          "Gym Grounds"),
    ("Gym Grounds",  "Med-C Grounds"),
    ("Vyas",         "Shankar"),
    ("Shankar",      "Gandhi"),
    ("Gandhi",       "Krishna"),
    ("Krishna",      "Vishwakarma"),
    ("Vyas",         "Akshay"),
    ("Shankar",      "ANC"),
    ("Gandhi",       "Bhagirath"),
    ("South Park",   "NAB"),
    ("NAB",          "IPC"),
    ("IPC",          "Gandhi"),
    ("IPC",          "Shankar"),
    ("NAB",          "Budh"),
    ("NAB",          "Ram"),
    ("Ram",          "Main Audi"),
    ("Main Audi",    "IC"),
    ("IC",           "SR"),
    ("IC",           "FD3"),
    ("SR",           "FD3"),
    ("SR",           "New Workshop"),
    ("FD3",          "Sky Lawns"),
    ("FD3",          "Birla Museum"),
    ("Sky Lawns",    "Sky Lab"),
    ("FD2",          "FD3"),
    ("FD2",          "Main Audi"),
    ("FD2",          "Old Workshop"),
    ("FD1",          "FD2"),
    ("FD1",          "Old Workshop"),
    ("FD1",          "Library"),
    ("Library",      "LTC"),
    ("LTC",          "FD1"),
    ("New Workshop", "FD2"),
    ("SAC",          "Budh"),
    ("SAC",          "South Park"),
    ("Budh",         "Ram"),
    ("SAC",          "Meera"),
    ("South Park",   "Saraswati Mandir"),
    ("Saraswati Mandir", "Shiv Ganga"),
    ("Saraswati Mandir", "Vyas"),
    ("Shiv Ganga",   "Birla Shishu Vihar"),
    ("Birla Shishu Vihar", "Meera"),
    ("Meera",        "South Park"),
    ("LTC",          "UCO Bank"),
    ("Old Workshop", "Vishwakarma"),
    ("Vishwakarma",  "FD1"),
    ("Krishna",      "Old Workshop"),
]

def _build_graph():
    graph = {node: {} for node in NODES}
    for a, b in _EDGE_LIST:
        w = euclidean(a, b)
        graph[a][b] = w
        graph[b][a] = w
    return graph

GRAPH = _build_graph()

def get_neighbors(node):
    return list(GRAPH[node].items())

def node_coords(node):
    return NODES[node]

def all_nodes():
    return list(NODES.keys())

def all_edges():
    seen = set()
    edges = []
    for a, neighbors in GRAPH.items():
        for b, w in neighbors.items():
            key = tuple(sorted([a, b]))
            if key not in seen:
                seen.add(key)
                edges.append((a, b, w))
    return edges


if __name__ == "__main__":
    print(f"Nodes: {len(NODES)}")
    print(f"Edges: {len(all_edges())}")
    print("\nSample neighbors of 'Main Gate':")
    for nb, w in get_neighbors("Main Gate"):
        print(f"  -> {nb}: {w:.1f}")
