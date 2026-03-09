import os
import sys
import socket
from datetime import datetime, timezone
from typing import Any, Dict, List

import flask
from flask import Flask, Response, jsonify, request

APP_NAME = "python-flask-hello"
APP_VERSION = "3.2.1"
UI_BUILD_ID = "COLOR_UI_001"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def in_docker() -> bool:
    if os.path.exists("/.dockerenv"):
        return True

    cgroup = "/proc/1/cgroup"
    if os.path.exists(cgroup):
        try:
            with open(cgroup, "rt", encoding="utf-8") as f:
                data = f.read()
            return ("docker" in data) or ("kubepods" in data) or ("containerd" in data)
        except Exception:
            return False

    return False


def find_free_port(start_port: int, host: str = "127.0.0.1", tries: int = 50) -> int:
    import socket as _socket
    for p in range(start_port, start_port + tries):
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
            s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, p))
                return p
            except OSError:
                continue
    with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return int(s.getsockname()[1])


def list_routes(app: Flask) -> List[Dict[str, Any]]:
    routes: List[Dict[str, Any]] = []
    for r in app.url_map.iter_rules():
        methods = sorted(list(r.methods - {"HEAD", "OPTIONS"}))
        routes.append({"rule": r.rule, "methods": methods})
    return sorted(routes, key=lambda x: x["rule"])


def build_ui_html(hostname: str, now: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{APP_NAME} - {UI_BUILD_ID}</title>
  <style>
    body {{
      margin:0;
      font-family: Arial, Helvetica, sans-serif;
      height:100vh;
      display:grid;
      place-items:center;
      overflow:hidden;
      background: radial-gradient(circle at top left, #22c55e 0%, transparent 40%),
                  radial-gradient(circle at bottom right, #3b82f6 0%, transparent 45%),
                  linear-gradient(135deg, #0f172a 0%, #111827 100%);
      color:#f8fafc;
    }}

    .blob {{
      position:absolute;
      width:320px;
      height:320px;
      border-radius:50%;
      filter: blur(30px);
      opacity:0.45;
      animation: float 7s ease-in-out infinite;
    }}
    .blob.one {{ background:#a855f7; top:-80px; left:-80px; }}
    .blob.two {{ background:#22c55e; bottom:-110px; right:-110px; animation-delay:-2.5s; }}
    .blob.three {{ background:#3b82f6; top:40%; left:70%; width:240px; height:240px; animation-delay:-4s; }}

    @keyframes float {{
      0%,100% {{ transform: translate(0,0) scale(1); }}
      50%     {{ transform: translate(18px,-12px) scale(1.06); }}
    }}

    .card {{
      position:relative;
      width:min(820px, 92vw);
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 18px;
      padding: 26px;
      background: rgba(255,255,255,0.08);
      backdrop-filter: blur(10px);
      box-shadow: 0 24px 80px rgba(0,0,0,0.45);
    }}

    .title {{
      margin:0 0 6px 0;
      font-size:22px;
      font-weight:800;
    }}

    .sub {{
      margin:0 0 18px 0;
      font-size:14px;
      opacity:0.9;
      display:flex;
      align-items:center;
      gap:10px;
    }}

    .thumb {{
      display:inline-grid;
      place-items:center;
      width:40px;
      height:40px;
      border-radius:12px;
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.18);
      animation: pop 1.2s ease-in-out infinite;
      transform-origin:center;
      font-size:20px;
    }}
    @keyframes pop {{
      0%,100% {{ transform: scale(1); }}
      50%     {{ transform: scale(1.12) rotate(-6deg); }}
    }}

    .row {{
      display:flex;
      gap:14px;
      align-items:center;
      flex-wrap:wrap;
      margin-top:6px;
    }}

    .pill {{
      font-size:13px;
      padding:10px 12px;
      border-radius:999px;
      background: rgba(255,255,255,0.10);
      border: 1px solid rgba(255,255,255,0.18);
      white-space:nowrap;
    }}

    .progress-wrap {{
      margin-top:18px;
      padding:10px 12px;
      border-radius:14px;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.14);
    }}
    .progress-title {{
      font-size:12px;
      opacity:0.9;
      margin-bottom:8px;
    }}
    .bar {{
      height:10px;
      border-radius:999px;
      background: rgba(255,255,255,0.12);
      overflow:hidden;
      position:relative;
    }}
    .bar > span {{
      display:block;
      height:100%;
      width:35%;
      border-radius:999px;
      background: linear-gradient(90deg, #22c55e, #3b82f6, #a855f7);
      animation: load 1.8s ease-in-out infinite;
    }}
    @keyframes load {{
      0%   {{ transform: translateX(-60%); width:35%; }}
      50%  {{ transform: translateX(40%);  width:55%; }}
      100% {{ transform: translateX(160%); width:35%; }}
    }}

    code {{
      background: rgba(0,0,0,0.35);
      border: 1px solid rgba(255,255,255,0.18);
      padding: 2px 6px;
      border-radius: 8px;
    }}

    .footer {{
      margin-top:16px;
      font-size:13px;
      line-height:1.7;
      opacity:0.95;
    }}
  </style>
</head>
<body>
  <div class="blob one"></div>
  <div class="blob two"></div>
  <div class="blob three"></div>

  <div class="card">
    <div class="title">{APP_NAME} (v{APP_VERSION})</div>

    <div class="sub">
      <span class="thumb">👍</span>
      UI build: <b>{UI_BUILD_ID}</b>
    </div>

    <div class="row">
      <div class="pill"><b>Hostname:</b> {hostname}</div>
      <div class="pill"><b>UTC Time:</b> {now}</div>
      <div class="pill"><b>Status:</b> OK</div>
    </div>

    <div class="progress-wrap">
      <div class="progress-title">Container boot animation</div>
      <div class="bar"><span></span></div>
    </div>

    <div class="footer">
      JSON API: <code>GET /</code><br>
      UI Page: <code>GET /ui</code><br>
      Health: <code>GET /health</code><br>
      Debug: <code>GET /debug</code>
    </div>
  </div>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify(
            service=APP_NAME,
            version=APP_VERSION,
            ui_build_id=UI_BUILD_ID,
            message="Hello from Python (Flask) in a container!",
            hostname=socket.gethostname(),
            time=utc_now(),
            note="Open /ui in browser to see animation",
        )

    @app.route("/ui", methods=["GET"])
    def ui():
        resp = Response(build_ui_html(socket.gethostname(), utc_now()), mimetype="text/html")
        resp.headers["Cache-Control"] = "no-store, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        resp.headers["X-UI-BUILD-ID"] = UI_BUILD_ID
        resp.headers["X-APP-VERSION"] = APP_VERSION
        return resp

    @app.route("/health", methods=["GET"])
    def health():
        return "OK", 200

    @app.route("/debug", methods=["GET"])
    def debug():
        return jsonify(
            service=APP_NAME,
            version=APP_VERSION,
            ui_build_id=UI_BUILD_ID,
            time=utc_now(),
            file_path=os.path.abspath(__file__),
            cwd=os.getcwd(),
            python=sys.version.split()[0],
            flask_version=getattr(flask, "__version__", "unknown"),
            request_path=request.path,
            docker=in_docker(),
            routes=list_routes(app),
        )

    @app.errorhandler(404)
    def not_found(_: Exception):
        return jsonify(
            error="not_found",
            path=request.path,
            time=utc_now(),
            hint="Check /debug to confirm correct file + routes and correct port mapping",
        ), 404

    return app


if __name__ == "__main__":
    app = create_app()
    docker_mode = in_docker()

    if docker_mode:
        port = int(os.getenv("PORT", "8080"))
        bind_host = "0.0.0.0"
    else:
        preferred = int(os.getenv("PORT", "8085"))
        port = find_free_port(preferred, host="127.0.0.1")
        bind_host = "127.0.0.1"

    print("=== FLASK START ===")
    print("DOCKER :", docker_mode)
    print("FILE   :", os.path.abspath(__file__))
    print("CWD    :", os.getcwd())
    print("BIND   :", f"{bind_host}:{port}")
    print("OPEN   :", f"http://127.0.0.1:{port}/ui")
    print("DEBUG  :", f"http://127.0.0.1:{port}/debug")
    print("UI_ID  :", UI_BUILD_ID)
    print("===================")

    app.run(host=bind_host, port=port, debug=False, use_reloader=False)
