# Algorithm Performance Analyzer

A small Flask service to benchmark simple algorithms, produce a PNG performance graph (saved to disk), and store analysis metadata in a MySQL database.

## Overview

- Benchmarks algorithms (bubble sort, linear search, binary search, nested loops)
- Saves generated graphs under the `Graphs/` directory
- Stores analysis metadata and the graph path in a MySQL table via SQLAlchemy

## Quick Start

Prerequisites:

- Python 3.7+
- MySQL server
- pip

Install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install directly:

```bash
pip install flask sqlalchemy pymysql matplotlib numpy
```

Run the app:

```bash
python3 main.py
```

The service will run on http://localhost:3000 by default.

## Endpoints

1. Analyze (generate graph)

- URL: `GET /analyze`
- Query params:
  - `algo` (bubble|linear|binary|nested) — default `bubble`
  - `n` (int) — max input size (default 100)
  - `steps` (int) — number of increments (default 10)

Example (browser or curl):

```bash
curl "http://localhost:3000/analyze?algo=bubble&n=100&steps=10"
```

Response (JSON) includes `path_to_graph`, e.g. `/Graphs/bubble_1610000000.png`.

2. Save analysis

- URL: `POST /save_analysis`
- Body: JSON with fields returned from `/analyze` plus `path_to_graph`.

Example curl:

```bash
curl -X POST http://localhost:3000/save_analysis \
  -H "Content-Type: application/json" \
  -d '{"algo":"bubble","items":100,"steps":10,"start_time":"...","end_time":"...","total_time_ms":123,"time_complexity":"O(n^2)","path_to_graph":"/Graphs/bubble_1610000000.png"}'
```

3. Retrieve analysis

- URL: `GET /retrieve_analysis?id=<id>`

Example:

```bash
curl "http://localhost:3000/retrieve_analysis?id=1"
```

Returns JSON with metadata and `path_to_graph`.

## Graph files

- Graphs are saved to the local `Graphs/` directory created at runtime.
- The database stores the file path (string), not the file binary.
- To display the PNG in a browser, either:
  - Serve the `Graphs/` directory through a static file server, or
  - Add an endpoint to serve files (e.g., `send_file`) in `main.py`.

## How it works (brief)

- The `/analyze` handler runs the selected algorithm for increasing input sizes, measures execution time, builds a matplotlib plot, writes it to `Graphs/{algo}_{timestamp}.png`, and returns analysis metadata.
- The client can then call `/save_analysis` with that metadata to persist it.

## Testing

- Use a browser to call `/analyze` (GET).
- Use curl or Postman to POST `/save_analysis` with JSON.
- Use curl or browser to GET `/retrieve_analysis?id=<id>`.

## Notes & troubleshooting

- Ensure the MySQL credentials in `main.py` match your environment.
- If `Graphs/` permission errors occur, run: `chmod 755 Graphs/`.
- If port 3000 is in use, change `app.run(... port=...)` in `main.py`.

## Minimal requirements.txt

```
flask
sqlalchemy
pymysql
matplotlib
numpy
```

---

Author: Rwigema — Last updated: Feb 2026
