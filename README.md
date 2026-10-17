# Campus Delivery Route Optimization

A Python graph optimization mini project with a browser frontend. Python owns the road data and route algorithms; the HTML/CSS/JavaScript page requests results from Python over a local HTTP API.

## Requirements

- Python 3.9 or newer
- VS Code (recommended) or a terminal
- No third-party Python packages

## Run from VS Code

1. In VS Code, choose **File → Open Folder** and open this `transportation_mini_project` folder.
2. Open the integrated terminal (**Terminal → New Terminal**).
3. Start the frontend and Python API:

   ```powershell
   python transportation_server.py
   ```

   On Windows systems with the Python launcher, you can use `py -3 transportation_server.py` instead.

4. Open this URL in a browser:

   ```text
   http://127.0.0.1:8000/graph.html
   ```

5. Use **Show shortest path** to call Dijkstra in Python, or **Optimize delivery tour** to call nearest-neighbor plus 2-opt in Python.
6. Stop the server with **Ctrl+C** in the terminal.

You can also double-click `run_project.bat` on Windows. It opens a server console and launches the browser page.

## Console program

In a second terminal, run:

```powershell
python transportation_optimizer.py
```

Try another depot:

```powershell
python transportation_optimizer.py --start Library
```

## Project files

- `transportation_optimizer.py` — weighted graph, Dijkstra shortest paths, nearest-neighbor initial tour, and 2-opt improvement.
- `transportation_server.py` — serves the frontend and exposes `/api/graph`, `/api/shortest-path`, and `/api/optimize`.
- `graph.html`, `graph.css`, `graph.js` — interactive graph display and controls. Road weights and route calculations come from the Python API.
- `mini_project_report.md` — project formulation, graph concepts, analysis, limitations, and viva prompts.
- `transportation_project_slides.pptx` — short presentation for the demonstration.

The campus roads and distances are illustrative, not real navigation data.
