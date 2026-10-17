"""Serve the campus graph frontend and Python routing APIs."""
from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import transportation_optimizer as optimizer

BASE_DIR = Path(__file__).resolve().parent
ROAD_GRAPH = optimizer.Graph.from_roads(optimizer.ROADS)
NODE_LAYOUT = {
    "Depot": {"x": 105, "y": 285},
    "Library": {"x": 270, "y": 150},
    "Engineering": {"x": 455, "y": 285},
    "Science": {"x": 665, "y": 140},
    "Cafeteria": {"x": 700, "y": 400},
    "Hostel": {"x": 455, "y": 475},
    "Admin": {"x": 250, "y": 430},
}


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/graph":
                self.send_json({
                    "nodes": [
                        {"name": name, **NODE_LAYOUT[name]}
                        for name in sorted(ROAD_GRAPH.adjacency)
                    ],
                    "roads": [
                        {"from": a, "to": b, "distance": distance}
                        for a, b, distance in optimizer.ROADS
                    ],
                })
                return

            if parsed.path == "/api/shortest-path":
                source = params.get("source", [""])[0]
                target = params.get("target", [""])[0]
                if source not in ROAD_GRAPH.adjacency or target not in ROAD_GRAPH.adjacency:
                    self.send_json({"error": "Choose valid source and destination locations."}, 400)
                    return
                distances, previous = ROAD_GRAPH.shortest_paths(source)
                path = ROAD_GRAPH.path(source, target, previous)
                self.send_json({"source": source, "target": target, "path": path, "distance": distances[target]})
                return

            if parsed.path == "/api/optimize":
                start = params.get("start", [optimizer.DEFAULT_START])[0]
                iterations = int(params.get("iterations", ["1000"])[0])
                if start not in ROAD_GRAPH.adjacency:
                    self.send_json({"error": "Choose a valid depot location."}, 400)
                    return
                if iterations < 1 or iterations > 100000:
                    self.send_json({"error": "Iterations must be between 1 and 100000."}, 400)
                    return
                nodes, costs, paths = optimizer.metric_closure(ROAD_GRAPH)
                initial = optimizer.nearest_neighbor(nodes, start, costs)
                improved = optimizer.two_opt(initial, costs, iterations)
                self.send_json({
                    "initial_route": initial,
                    "initial_distance": optimizer.route_cost(initial, costs),
                    "optimized_route": improved,
                    "optimized_distance": optimizer.route_cost(improved, costs),
                    "road_path": optimizer.expand_route(improved, paths),
                })
                return
        except (ValueError, KeyError) as exc:
            self.send_json({"error": str(exc)}, 400)
            return
        except Exception as exc:
            self.send_json({"error": f"Request failed: {exc}"}, 500)
            return

        super().do_GET()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run the transportation project web frontend and API.")
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default: localhost only)")
    parser.add_argument("--port", type=int, default=8000, help="web server port")
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), RequestHandler)
    print(f"Transportation project running at http://{args.host}:{args.port}/graph.html")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
