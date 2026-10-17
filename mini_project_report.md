# Campus Delivery Route Optimization

## Mini project report

**Domain:** Transportation  
**Problem:** Plan one vehicle's campus delivery tour so it starts at the depot, visits each delivery location once, and returns to the depot while minimizing total road distance.

## 1. Problem identification

Campus staff often deliver parcels or supplies to several buildings. Choosing an order by intuition can cause avoidable travel. This project models the campus roads as a graph and compares a simple feasible tour with a locally improved tour.

The example is illustrative; locations and distances are invented for demonstrating the method, not campus navigation.

## 2. Formulation

Let the road network be an undirected weighted graph (G=(V,E)), where vertices are locations and edge weights are road distances in kilometres. The depot is (s\in V); all other vertices are delivery stops. Let (d(i,j)) be the shortest road distance between stops (i) and (j).

Choose a closed tour (R=(r_0,r_1,\ldots,r_m,r_{m+1})), where (r_0=r_{m+1}=s), and every non-depot location appears exactly once. Minimize

\[
\min_R \sum_{k=0}^{m} d(r_k,r_{k+1}).
\]

**Inputs:** road edges, their positive distances, depot, and iteration limit.  
**Constraints:** visit every stop exactly once; start and end at the depot; travel along roads; distances are nonnegative and symmetric in this sample.  
**Outputs:** initial and improved stop order, distance totals, savings, and expanded road-by-road route.

This is a travelling-salesperson-style routing problem on the shortest-path metric closure of the road graph. Finding the exact optimum is computationally difficult as the number of stops grows; the project uses a heuristic.

## 3. Graph representation and concepts

The sample graph has seven vertices: Depot, Library, Engineering, Science, Cafeteria, Hostel, and Admin. Fourteen undirected road links carry distances in km.

The program uses:

1. **Weighted graph:** road lengths quantify travel cost; the optimization objective sums kilometres.
2. **Undirected graph:** each sample road is traversable in both directions at the same cost. A one-way road would require directed edges.
3. **Shortest paths:** Dijkstra's algorithm computes the least-distance road path between every pair of stops. These distances form a complete weighted graph (metric closure) for the tour optimizer.
4. **Connectivity:** the sample road network is connected, so every stop is reachable from the depot.
5. **Cycles:** the delivery tour is a closed cycle returning to the depot.

The reported stop sequence may skip intermediate road vertices. The expanded route reconstructs the actual shortest road segments between consecutive stops.

## 4. Initial solution and optimization

The initial feasible tour uses **nearest neighbor**: begin at the depot, repeatedly visit the closest unvisited stop, then return to the depot. It is quick and easy to explain, but an early choice can lead to a poor overall tour.

The improvement uses **2-opt local search**. It considers reversing portions of the tour and accepts a reversal when it reduces total distance. The depot remains fixed at the beginning and end. It stops when no improving reversal is found or the iteration cap is reached.

This is suitable for a small teaching example because it is deterministic, understandable, and produces a valid tour. It does not guarantee a globally optimal solution.

## 5. Program implementation

Run with Python 3:

```text
python transportation_optimizer.py
python transportation_optimizer.py --start Library --iterations 1000
```

The implementation uses only the Python standard library. The embedded network can be edited in `ROADS`. Dijkstra has complexity (O((|V|+|E|)\log |V|)) per source using a binary heap. The simple 2-opt scan is (O(I n^2)) in the worst case for (I) accepted-improvement passes and (n) stops (each candidate cost is recomputed), which is adequate for this small example.

## 6. Results and comparison

For the default depot and embedded sample data:

| Method | Tour length |
|---|---:|
| Nearest-neighbor initial tour | 9.30 km |
| After 2-opt | 9.30 km |

The nearest-neighbor route is already locally optimal for this particular data, so 2-opt finds no shorter reversal. A reproducible shuffled baseline is 11.20 km; 2-opt reduces it to 9.50 km (15.2%). This shows how local search can improve a different feasible starting tour, while not guaranteeing a global optimum. Use the program output as the authoritative result if the roads or start point are changed.

## 7. Analysis, interpretation, and limitations

The method guarantees a valid closed tour on a connected network. Dijkstra guarantees shortest road paths for the supplied nonnegative edge weights. The nearest-neighbor algorithm and 2-opt do **not** guarantee a globally shortest visit order. The result depends on the initial tour and local search can settle at a local optimum.

The model assumes a single vehicle, one visit per stop, fixed distances, no traffic, no delivery time windows, no vehicle-capacity limit, and no service times. It minimizes distance rather than time or cost. The sample is small and illustrative. A real deployment should use verified road data, directed edges for one-way streets, changing travel times, operational constraints, and a stronger solver or multiple starting tours for larger instances.

## 8. Conclusion

This project turns a transportation planning task into a weighted graph and route optimization problem. Dijkstra's shortest paths create realistic travel costs between delivery stops; nearest neighbor supplies a feasible tour; and 2-opt searches for shorter tours. The printed baseline and improved route make the optimization and its limitations visible.

## Demonstration and viva prompts

- Why are shortest road distances computed before the tour search?
- What does an edge weight represent, and when would the graph need to be directed?
- Why is the returned tour a cycle?
- Why can nearest neighbor make a poor choice?
- What change would model delivery time windows or vehicle capacity?
- Why does 2-opt not prove optimality?



## 9. Browser frontend and Python backend

The interactive graph page is served by the Python program in `transportation_server.py`. Run `python transportation_server.py` from this folder and open `http://127.0.0.1:8000/graph.html`. The browser uses `graph.html` for structure, `graph.css` for styling, and `graph.js` to call the backend with `fetch`.

The backend exposes `/api/graph` for node and road data, `/api/shortest-path` for Dijkstra results, and `/api/optimize` for the nearest-neighbor and 2-opt delivery tour. Thus the road weights and route calculations come from the same Python model used by the console program. The included server uses only Python's standard library and listens on localhost by default.
