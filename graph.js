"use strict";

// Node positions are presentation-only; road weights and route calculations come from Python.
const layout = {
  Depot: { x: 105, y: 285 }, Library: { x: 270, y: 150 },
  Engineering: { x: 455, y: 285 }, Science: { x: 665, y: 140 },
  Cafeteria: { x: 700, y: 400 }, Hostel: { x: 455, y: 475 },
  Admin: { x: 250, y: 430 },
};
const edgesLayer = document.querySelector("#edges");
const nodesLayer = document.querySelector("#nodes");
const sourceSelect = document.querySelector("#source");
const targetSelect = document.querySelector("#target");
const result = document.querySelector("#result");
const edgeElements = new Map();
let locations = [];
let roads = [];

function edgeKey(a, b) { return [a, b].sort().join("|"); }

async function api(path) {
  const response = await fetch(path, { headers: { Accept: "application/json" } });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function drawGraph() {
  for (const road of roads) {
    const start = layout[road.from];
    const end = layout[road.to];
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", start.x);
    line.setAttribute("y1", start.y);
    line.setAttribute("x2", end.x);
    line.setAttribute("y2", end.y);
    line.setAttribute("class", "edge");
    edgesLayer.append(line);
    edgeElements.set(edgeKey(road.from, road.to), line);

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", (start.x + end.x) / 2);
    label.setAttribute("y", (start.y + end.y) / 2 - 7);
    label.setAttribute("class", "edge-label");
    label.textContent = road.distance.toFixed(1);
    edgesLayer.append(label);
  }

  for (const node of locations) {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", "node");
    group.setAttribute("data-name", node.name);
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", node.x);
    circle.setAttribute("cy", node.y);
    circle.setAttribute("r", "13");
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", node.x);
    label.setAttribute("y", node.y + 34);
    label.textContent = node.name;
    group.append(circle, label);
    nodesLayer.append(group);
  }
}

function fillSelect(select) {
  for (const node of locations) {
    const option = document.createElement("option");
    option.value = node.name;
    option.textContent = node.name;
    select.append(option);
  }
}

function clearHighlights() {
  for (const edge of edgeElements.values()) edge.classList.remove("highlight", "tour");
  document.querySelectorAll(".node").forEach((node) => node.classList.remove("selected"));
}

function highlightPath(path, className = "highlight") {
  clearHighlights();
  for (let i = 0; i < path.length - 1; i++) {
    edgeElements.get(edgeKey(path[i], path[i + 1]))?.classList.add(className);
  }
  if (path.length) {
    document.querySelector(`[data-name="${path[0]}"]`)?.classList.add("selected");
    document.querySelector(`[data-name="${path[path.length - 1]}"]`)?.classList.add("selected");
  }
}

async function showShortestPath() {
  const source = sourceSelect.value;
  const target = targetSelect.value;
  try {
    const route = await api(`/api/shortest-path?source=${encodeURIComponent(source)}&target=${encodeURIComponent(target)}`);
    highlightPath(route.path);
    result.textContent = source === target
      ? `${source} to ${target}: already at the same location (0.00 km).`
      : `Shortest path: ${route.path.join(" → ")} · ${route.distance.toFixed(2)} km (computed by Python)`;
  } catch (error) {
    result.textContent = `Python API error: ${error.message}`;
  }
}

async function optimizeTour() {
  const start = sourceSelect.value;
  try {
    const route = await api(`/api/optimize?start=${encodeURIComponent(start)}`);
    highlightPath(route.road_path, "tour");
    const saving = route.initial_distance - route.optimized_distance;
    result.textContent = `Python optimized tour: ${route.optimized_route.join(" → ")} · ${route.optimized_distance.toFixed(2)} km (initial ${route.initial_distance.toFixed(2)} km, saved ${saving.toFixed(2)} km)`;
  } catch (error) {
    result.textContent = `Python API error: ${error.message}`;
  }
}

async function start() {
  try {
    const graph = await api("/api/graph");
    locations = graph.nodes;
    roads = graph.roads;
    drawGraph();
    fillSelect(sourceSelect);
    fillSelect(targetSelect);
    sourceSelect.value = "Depot";
    targetSelect.value = "Hostel";
    result.textContent = "Connected to the Python server. Choose locations, or optimize a full delivery tour.";
    document.querySelector("#findPath").addEventListener("click", showShortestPath);
    document.querySelector("#optimizeTour").addEventListener("click", optimizeTour);
    document.querySelector("#resetGraph").addEventListener("click", () => {
      clearHighlights();
      result.textContent = "Connected to Python. Choose two locations or optimize a delivery tour.";
    });
  } catch (error) {
    result.textContent = `Cannot reach the Python server. Run “python transportation_server.py”, then open http://127.0.0.1:8000/graph.html. (${error.message})`;
  }
}

start();
