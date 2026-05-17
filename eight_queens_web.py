"""Web-based HTML interface for the Eight-Queens Puzzle.

Serves an interactive HTML page for browsing eight-queens
solutions using Python's built-in HTTP server. All puzzle
logic is delegated to eight_queens.solve_n_queens.

Usage:
    python3 eight_queens_web.py
    # Open http://localhost:8080 in a browser
"""

import http.server
import json
import urllib.parse

from eight_queens import solve_n_queens

# CSS theme constants matching the Tkinter UI colour scheme
_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #2d2d2d; color: #fff; font-family: Helvetica, Arial, sans-serif;
       display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
h1 { margin: 20px 0 5px; font-size: 28px; font-weight: bold; }
#info { font-size: 18px; margin-bottom: 15px; color: #ccc; }
#board { display: grid; gap: 2px; padding: 4px; background: #1a1a1a; border-radius: 4px; }
.cell { width: 64px; height: 64px; display: flex; align-items: center; justify-content: center;
        font-size: 36px; cursor: default; user-select: none; }
.light { background: #f0d9b5; }
.dark  { background: #b58863; }
.queen { color: #1a1a2e; }
#nav { margin: 15px 0 30px; display: flex; gap: 8px; }
#nav button { padding: 8px 20px; font-size: 15px; font-weight: bold; border: none;
              border-radius: 4px; cursor: pointer; background: #4a4a4a; color: #fff; }
#nav button:hover { background: #e94560; }
#nav button:disabled { opacity: 0.4; cursor: default; background: #4a4a4a; }
"""

_JS = """
const SOLUTIONS = __SOLUTIONS_JSON__;
const N = __BOARD_SIZE__;
let idx = 0;

function render() {
  const sol = SOLUTIONS[idx];
  const info = document.getElementById('info');
  info.textContent = SOLUTIONS.length
    ? 'Solution ' + (idx + 1) + ' / ' + SOLUTIONS.length
    : 'No solutions found';

  document.getElementById('btnFirst').disabled = (idx === 0);
  document.getElementById('btnPrev').disabled  = (idx === 0);
  document.getElementById('btnNext').disabled  = (idx >= SOLUTIONS.length - 1);
  document.getElementById('btnLast').disabled  = (idx >= SOLUTIONS.length - 1);

  const board = document.getElementById('board');
  board.style.gridTemplateColumns = 'repeat(' + N + ', 64px)';
  board.innerHTML = '';
  for (let r = 0; r < N; r++) {
    for (let c = 0; c < N; c++) {
      const div = document.createElement('div');
      div.className = 'cell ' + ((r + c) % 2 === 0 ? 'light' : 'dark');
      if (sol && sol[r] === c) {
        div.textContent = '\\u2655';
        div.classList.add('queen');
      }
      board.appendChild(div);
    }
  }
}

function go(n)  { if (n >= 0 && n < SOLUTIONS.length) { idx = n; render(); } }
function first(){ go(0); }
function prev() { go(idx - 1); }
function next() { go(idx + 1); }
function last() { go(SOLUTIONS.length - 1); }

window.onload = function () {
  const hashIdx = parseInt(window.location.hash.slice(1), 10);
  if (hashIdx >= 1 && hashIdx <= SOLUTIONS.length) idx = hashIdx - 1;
  render();
};
"""

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eight Queens Puzzle</title>
<style>{css}</style>
</head>
<body>
<h1>{board_size}-Queens Puzzle</h1>
<p id="info">Loading...</p>
<div id="board"></div>
<div id="nav">
  <button id="btnFirst" onclick="first()">|&lt; First</button>
  <button id="btnPrev"  onclick="prev()">&lt; Prev</button>
  <button id="btnNext"  onclick="next()">Next &gt;</button>
  <button id="btnLast"  onclick="last()">Last &gt;|</button>
</div>
<script>{js}</script>
</body>
</html>
"""


class WebQueensServer:
    """HTTP server that serves an interactive eight-queens web page.

    The server generates a self-contained HTML page with embedded
    CSS and JavaScript. All solving is delegated to eight_queens.

    Attributes:
        board_size: Board dimension.
        solutions: Cached list of all valid solutions.
        port: TCP port the server listens on.
    """

    def __init__(self, board_size: int = 8, port: int = 8080):
        """Initialise the web server wrapper.

        Args:
            board_size: Board size (default 8).
            port: TCP port to listen on (default 8080).

        Raises:
            ValueError: If board_size is not positive or port is out of range.
        """
        if board_size < 1:
            raise ValueError(f"Board size must be >= 1, got {board_size}")
        if port < 1 or port > 65535:
            raise ValueError(f"Port must be 1-65535, got {port}")
        self.board_size = board_size
        self.port = port
        self.solutions: "list[list[int]]" = []
        self._httpd: "http.server.HTTPServer | None" = None

    # ------------------------------------------------------------------
    # Solving (delegated)
    # ------------------------------------------------------------------

    def solve(self) -> "list[list[int]]":
        """Compute solutions via the backend solver.

        Returns:
            List of solutions, each a list of column indices.
        """
        if not self.solutions:
            self.solutions = solve_n_queens(self.board_size)
        return self.solutions

    @property
    def solution_count(self) -> int:
        """Return the total number of solutions."""
        return len(self.solutions)

    # ------------------------------------------------------------------
    # Content generation (testable without HTTP)
    # ------------------------------------------------------------------

    def build_html(self) -> str:
        """Build the full HTML page with embedded solutions.

        Returns:
            Complete HTML document as a string.
        """
        self.solve()
        js = _JS.replace("__SOLUTIONS_JSON__", json.dumps(self.solutions))
        js = js.replace("__BOARD_SIZE__", str(self.board_size))
        return _HTML_TEMPLATE.format(
            css=_CSS.strip(),
            js=js.strip(),
            board_size=self.board_size,
        )

    def build_json(self, index: int | None = None) -> str:
        """Build a JSON response for API requests.

        Args:
            index: 1-based solution index, or None for all solutions.

        Returns:
            JSON string.
        """
        self.solve()
        if index is not None:
            if 1 <= index <= len(self.solutions):
                return json.dumps({
                    "index": index,
                    "total": len(self.solutions),
                    "solution": self.solutions[index - 1],
                })
            return json.dumps({"error": "index out of range",
                               "total": len(self.solutions)})
        return json.dumps({
            "board_size": self.board_size,
            "total": len(self.solutions),
            "solutions": self.solutions,
        })

    # ------------------------------------------------------------------
    # HTTP request handler
    # ------------------------------------------------------------------

    def _make_handler(self):
        """Create a request handler class bound to this server instance."""
        server = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path.rstrip("/") or "/"

                if path == "/":
                    content = server.build_html()
                    content_type = "text/html; charset=utf-8"
                    status = 200
                elif path == "/api/solutions":
                    qs = urllib.parse.parse_qs(parsed.query)
                    idx_str = qs.get("index", [None])[0]
                    idx = int(idx_str) if idx_str else None
                    content = server.build_json(idx)
                    content_type = "application/json"
                    status = 200
                elif path.startswith("/api/solution/"):
                    try:
                        idx = int(path.rsplit("/", 1)[-1])
                    except ValueError:
                        idx = -1
                    content = server.build_json(idx)
                    content_type = "application/json"
                    status = 200
                else:
                    content = "404 Not Found"
                    content_type = "text/plain"
                    status = 404

                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))

            def log_message(self, format, *args):  # noqa: A002
                """Suppress default stderr logging for quieter tests."""
                pass

        return Handler

    # ------------------------------------------------------------------
    # Server lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the HTTP server. Blocks until shutdown.

        Call shutdown() from another thread to stop.
        """
        self.solve()
        handler = self._make_handler()
        self._httpd = http.server.HTTPServer(("", self.port), handler)
        self._httpd.serve_forever()

    def shutdown(self) -> None:
        """Stop the HTTP server if it is running."""
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

    def reset(self) -> None:
        """Clear cached solutions (useful for testing)."""
        self.solutions = []


def main() -> None:
    """Entry point: create and run the web server."""
    server = WebQueensServer(board_size=8, port=8080)
    print(f"Eight Queens Web UI → http://localhost:{server.port}")
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
