"""Campus delivery route optimizer using graph algorithms and 2-opt local search.

Run: python transportation_optimizer.py
Optional: python transportation_optimizer.py --start Library --iterations 1000
Only Python's standard library is required.
"""
from __future__ import annotations

import argparse
import heapq
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Undirected road network: (location, location, distance in km).
ROADS: Tuple[Tuple[str, str, float], ...] = (
    ("Depot", "Library", 1.2),
    ("Depot", "Engineering", 2.0),
    ("Depot", "Hostel", 2.5),
    ("Library", "Engineering", 0.8),
    ("Library", "Cafeteria", 1.0),
    ("Engineering", "Science", 1.1),
    ("Engineering", "Cafeteria", 1.4),
    ("Science", "Cafeteria", 0.9),
    ("Science", "Hostel", 1.7),
    ("Cafeteria", "Hostel", 1.3),
    ("Library", "Admin", 1.5),
    ("Admin", "Engineering", 1.0),
    ("Admin", "Cafeteria", 1.2),
    ("Admin", "Hostel", 2.2),
)
DEFAULT_START = "Depot"


@dataclass
class Graph:
    adjacency: Dict[str, List[Tuple[str, float]]]

    @classmethod
    def from_roads(cls, roads: Tuple[Tuple[str, str, float], ...]) -> "Graph":
        adjacency: Dict[str, List[Tuple[str, float]]] = {}
        for a, b, distance in roads:
            if distance <= 0:
                raise ValueError("Road distances must be positive.")
            adjacency.setdefault(a, []).append((b, distance))
            adjacency.setdefault(b, []).append((a, distance))
        return cls(adjacency)

    def shortest_paths(self, source: str) -> Tuple[Dict[str, float], Dict[str, str]]:
        """Dijkstra's algorithm; returns distances and predecessor map."""
        if source not in self.adjacency:
            raise ValueError(f"Unknown location: {source}")
        distances = {node: math.inf for node in self.adjacency}
        previous: Dict[str, str] = {}
        distances[source] = 0.0
        queue = [(0.0, source)]
        while queue:
            distance, node = heapq.heappop(queue)
            if distance != distances[node]:
                continue
            for neighbor, weight in self.adjacency[node]:
                candidate = distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    previous[neighbor] = node
                    heapq.heappush(queue, (candidate, neighbor))
        return distances, previous

    def path(self, source: str, target: str, previous: Dict[str, str]) -> List[str]:
        if source == target:
            return [source]
        if target not in previous:
            raise ValueError(f"No route from {source} to {target}.")
        result = [target]
        while result[-1] != source:
            result.append(previous[result[-1]])
        return list(reversed(result))


def metric_closure(graph: Graph) -> Tuple[List[str], Dict[Tuple[str, str], float], Dict[Tuple[str, str], List[str]]]:
    """Complete weighted graph over delivery stops using road-network shortest paths."""
    nodes = sorted(graph.adjacency)
    costs: Dict[Tuple[str, str], float] = {}
    paths: Dict[Tuple[str, str], List[str]] = {}
    for source in nodes:
        distances, previous = graph.shortest_paths(source)
        for target in nodes:
            costs[source, target] = distances[target]
            paths[source, target] = graph.path(source, target, previous)
    return nodes, costs, paths


def route_cost(route: List[str], costs: Dict[Tuple[str, str], float]) -> float:
    return sum(costs[a, b] for a, b in zip(route, route[1:]))


def nearest_neighbor(nodes: List[str], start: str, costs: Dict[Tuple[str, str], float]) -> List[str]:
    unvisited = set(nodes) - {start}
    route = [start]
    while unvisited:
        current = route[-1]
        next_stop = min(unvisited, key=lambda node: (costs[current, node], node))
        route.append(next_stop)
        unvisited.remove(next_stop)
    route.append(start)
    return route


def two_opt(route: List[str], costs: Dict[Tuple[str, str], float], iterations: int) -> List[str]:
    """Improve a closed tour by reversing segments while preserving its start."""
    best = route[:]
    best_cost = route_cost(best, costs)
    for _ in range(iterations):
        improved = False
        # End index is exclusive; exclude fixed start at index 0 and final depot.
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                candidate_cost = route_cost(candidate, costs)
                if candidate_cost + 1e-9 < best_cost:
                    best, best_cost = candidate, candidate_cost
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return best


def expand_route(route: List[str], paths: Dict[Tuple[str, str], List[str]]) -> List[str]:
    expanded = []
    for a, b in zip(route, route[1:]):
        segment = paths[a, b]
        expanded.extend(segment if not expanded else segment[1:])
    return expanded


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize a campus delivery tour.")
    parser.add_argument("--start", default=DEFAULT_START, help="depot/start location (default: Depot)")
    parser.add_argument("--iterations", type=int, default=1000, help="2-opt iteration cap")
    parser.add_argument("--seed", type=int, default=7, help="seed for reproducible randomized baseline")
    args = parser.parse_args()

    graph = Graph.from_roads(ROADS)
    nodes, costs, paths = metric_closure(graph)
    if args.start not in nodes:
        parser.error(f"unknown start '{args.start}'. Choose from: {', '.join(nodes)}")
    if args.iterations < 1:
        parser.error("--iterations must be positive")

    initial = nearest_neighbor(nodes, args.start, costs)
    improved = two_opt(initial, costs, args.iterations)

    # A second, reproducible initial tour illustrates how starting order affects local search.
    stops = [n for n in nodes if n != args.start]
    random.Random(args.seed).shuffle(stops)
    randomized = [args.start, *stops, args.start]
    randomized_improved = two_opt(randomized, costs, args.iterations)

    initial_km = route_cost(initial, costs)
    improved_km = route_cost(improved, costs)
    random_km = route_cost(randomized, costs)
    random_improved_km = route_cost(randomized_improved, costs)
    saving = initial_km - improved_km
    percent = (saving / initial_km * 100.0) if initial_km else 0.0

    print("CAMPUS DELIVERY ROUTE OPTIMIZER")
    print("=" * 34)
    print(f"Locations: {len(nodes)} | Road links: {sum(map(len, graph.adjacency.values())) // 2}")
    print(f"Depot: {args.start} | Objective: minimize total distance (km)")
    print("\nNearest-neighbor initial tour:")
    print("  " + " -> ".join(initial))
    print(f"  Total: {initial_km:.2f} km")
    print("\nAfter 2-opt local search:")
    print("  " + " -> ".join(improved))
    print(f"  Total: {improved_km:.2f} km")
    print(f"  Improvement: {saving:.2f} km ({percent:.1f}%)")
    print("\nRandom-order comparison (fixed seed):")
    print(f"  Before: {random_km:.2f} km")
    print(f"  After:  {random_improved_km:.2f} km")
    print("\nExpanded road-by-road path for the improved tour:")
    print("  " + " -> ".join(expand_route(improved, paths)))
    print("\nAll-pairs shortest-path distance matrix (km):")
    print("  " + "  ".join(f"{n:>12}" for n in nodes))
    for a in nodes:
        print(f"{a:>12}  " + "  ".join(f"{costs[a, b]:12.2f}" for b in nodes))


if __name__ == "__main__":
    main()

