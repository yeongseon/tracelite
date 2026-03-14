"""Embedded Tracelite dashboard served at /_tracelite."""

import json
from typing import Any, Optional

from tracelite.core.diff import diff_responses
from tracelite.core.replay import generate_curl
from tracelite.core.storage.base import ILoggerStorage

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tracelite - DevTools for your backend APIs</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #e0e0e0; }
        .header { background: #16213e; padding: 16px 24px; border-bottom: 1px solid #0f3460; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 18px; color: #e94560; }
        .header .subtitle { font-size: 12px; color: #888; }
        .toolbar { padding: 12px 24px; background: #16213e; border-bottom: 1px solid #0f3460; display: flex; gap: 12px; align-items: center; }
        .toolbar input, .toolbar select { padding: 6px 12px; background: #1a1a2e; border: 1px solid #0f3460; color: #e0e0e0; border-radius: 4px; font-size: 13px; }
        .toolbar input { flex: 1; max-width: 400px; }
        .toolbar button { padding: 6px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
        .toolbar button:hover { background: #c73e54; }
        .container { display: flex; height: calc(100vh - 100px); }
        .request-list { width: 50%; overflow-y: auto; border-right: 1px solid #0f3460; }
        .request-item { padding: 10px 24px; border-bottom: 1px solid #0f3460; cursor: pointer; display: flex; gap: 12px; align-items: center; font-size: 13px; }
        .request-item:hover { background: #16213e; }
        .request-item.selected { background: #0f3460; }
        .request-item.slow { border-left: 3px solid #fbbf24; }
        .method { font-weight: 700; min-width: 50px; }
        .method.GET { color: #4ade80; }
        .method.POST { color: #60a5fa; }
        .method.PUT { color: #fbbf24; }
        .method.DELETE { color: #f87171; }
        .method.PATCH { color: #c084fc; }
        .status { min-width: 32px; text-align: center; }
        .status.s2xx { color: #4ade80; }
        .status.s3xx { color: #60a5fa; }
        .status.s4xx { color: #fbbf24; }
        .status.s5xx { color: #f87171; }
        .path { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .duration { color: #888; min-width: 60px; text-align: right; }
        .duration.slow { color: #fbbf24; font-weight: 700; }
        .slow-icon { color: #fbbf24; font-size: 14px; min-width: 16px; }
        .timestamp { color: #666; font-size: 11px; min-width: 70px; }
        .detail-panel { width: 50%; overflow-y: auto; padding: 24px; }
        .detail-panel h2 { font-size: 16px; margin-bottom: 16px; color: #e94560; }
        .detail-section { margin-bottom: 20px; }
        .detail-section h3 { font-size: 13px; color: #888; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .detail-section pre { background: #16213e; padding: 12px; border-radius: 4px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
        .meta-row { display: flex; gap: 24px; margin-bottom: 16px; font-size: 13px; flex-wrap: wrap; }
        .meta-label { color: #888; }
        .empty-state { display: flex; align-items: center; justify-content: center; height: 100%; color: #666; font-size: 14px; }
        .badge { padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: 600; }
        .action-bar { display: flex; gap: 8px; margin-bottom: 16px; }
        .action-btn { padding: 6px 14px; background: #0f3460; color: #e0e0e0; border: 1px solid #1a3a6e; border-radius: 4px; cursor: pointer; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; }
        .action-btn:hover { background: #163a6e; }
        .action-btn.copied { background: #166534; border-color: #22c55e; }
        .diff-section { margin-bottom: 20px; }
        .diff-section .diff-add { color: #4ade80; }
        .diff-section .diff-remove { color: #f87171; }
        .diff-section .diff-path { color: #60a5fa; font-weight: 600; }
        .diff-section pre { background: #16213e; padding: 12px; border-radius: 4px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; }
        .sql-query { background: #16213e; padding: 8px 12px; border-radius: 4px; margin-bottom: 8px; font-size: 12px; border-left: 3px solid #60a5fa; }
        .sql-query .sql-text { font-family: monospace; white-space: pre-wrap; word-break: break-all; }
        .sql-query .sql-meta { color: #888; font-size: 11px; margin-top: 4px; }
        .toast { position: fixed; bottom: 24px; right: 24px; padding: 10px 20px; background: #166534; color: white; border-radius: 6px; font-size: 13px; opacity: 0; transition: opacity 0.3s; z-index: 1000; }
        .toast.show { opacity: 1; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Tracelite</h1>
            <div class="subtitle">DevTools for your backend APIs</div>
        </div>
        <div class="subtitle" id="request-count"></div>
    </div>
    <div class="toolbar">
        <input type="text" id="search" placeholder="Filter by path, method, or status..." />
        <select id="method-filter">
            <option value="">All Methods</option>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
            <option value="PATCH">PATCH</option>
        </select>
        <button onclick="refreshLogs()">Refresh</button>
    </div>
    <div class="container">
        <div class="request-list" id="request-list">
            <div class="empty-state">Loading...</div>
        </div>
        <div class="detail-panel" id="detail-panel">
            <div class="empty-state">Select a request to view details</div>
        </div>
    </div>
    <div class="toast" id="toast"></div>
    <script>
        let allLogs = [];
        let selectedId = null;
        let slowThresholdMs = 1000;

        async function fetchConfig() {
            try {
                const resp = await fetch('/_tracelite/api/config');
                const cfg = await resp.json();
                if (cfg.slow_threshold_ms != null) slowThresholdMs = cfg.slow_threshold_ms;
            } catch(e) {}
        }

        async function fetchLogs() {
            const resp = await fetch('/_tracelite/api/logs');
            allLogs = await resp.json();
            renderList();
        }

        function refreshLogs() { fetchLogs(); }

        function renderList() {
            const search = document.getElementById('search').value.toLowerCase();
            const methodFilter = document.getElementById('method-filter').value;
            const list = document.getElementById('request-list');

            let filtered = allLogs.filter(log => {
                if (methodFilter && log.method !== methodFilter) return false;
                if (search) {
                    const haystack = (log.method + ' ' + log.path + ' ' + log.status_code).toLowerCase();
                    if (!haystack.includes(search)) return false;
                }
                return true;
            });

            document.getElementById('request-count').textContent = filtered.length + ' requests';

            if (filtered.length === 0) {
                list.innerHTML = '<div class="empty-state">No requests found</div>';
                return;
            }

            list.innerHTML = filtered.map(log => {
                const statusClass = 's' + Math.floor(log.status_code / 100) + 'xx';
                const ts = log.timestamp ? log.timestamp.split('T').pop().split('.')[0] : '';
                const dur = log.duration_ms != null ? log.duration_ms.toFixed(0) + 'ms' : '';
                const sel = log.id === selectedId ? ' selected' : '';
                const isSlow = log.duration_ms != null && log.duration_ms >= slowThresholdMs;
                const slowCls = isSlow ? ' slow' : '';
                const durCls = isSlow ? ' slow' : '';
                const slowIcon = isSlow ? '<span class="slow-icon">\\u26a0</span>' : '<span class="slow-icon"></span>';
                return '<div class="request-item' + sel + slowCls + '" onclick="selectLog(' + log.id + ')">' +
                    slowIcon +
                    '<span class="method ' + log.method + '">' + log.method + '</span>' +
                    '<span class="status ' + statusClass + '">' + log.status_code + '</span>' +
                    '<span class="path">' + escHtml(log.path) + '</span>' +
                    '<span class="duration' + durCls + '">' + dur + '</span>' +
                    '<span class="timestamp">' + ts + '</span>' +
                    '</div>';
            }).join('');
        }

        function selectLog(id) {
            selectedId = id;
            const log = allLogs.find(l => l.id === id);
            if (!log) return;
            renderList();
            renderDetail(log);
        }

        function renderDetail(log) {
            const panel = document.getElementById('detail-panel');
            const statusClass = 's' + Math.floor(log.status_code / 100) + 'xx';
            const isSlow = log.duration_ms != null && log.duration_ms >= slowThresholdMs;
            const durStr = log.duration_ms != null ? log.duration_ms.toFixed(2) + 'ms' : 'N/A';
            const durHtml = isSlow
                ? '<span class="duration slow">' + durStr + ' \\u26a0</span>'
                : durStr;

            let html =
                '<h2>' + log.method + ' ' + escHtml(log.path) + '</h2>' +
                '<div class="action-bar">' +
                    '<button class="action-btn" onclick="copyCurl(' + log.id + ')" id="curl-btn-' + log.id + '">\\ud83d\\udccb Copy curl</button>' +
                    '<button class="action-btn" onclick="showDiff(' + log.id + ')" id="diff-btn-' + log.id + '">\\ud83d\\udd0d Compare</button>' +
                '</div>' +
                '<div class="meta-row">' +
                    '<div><span class="meta-label">Status: </span><span class="status ' + statusClass + '">' + log.status_code + '</span></div>' +
                    '<div><span class="meta-label">Duration: </span>' + durHtml + '</div>' +
                    '<div><span class="meta-label">Client: </span>' + escHtml(log.client_ip || '') + '</div>' +
                    '<div><span class="meta-label">Time: </span>' + escHtml(log.timestamp || '') + '</div>' +
                '</div>' +
                (log.query ? section('Query', log.query) : '') +
                section('Request Headers', formatJson(log.request_headers)) +
                (log.request_body ? section('Request Body', formatBody(log.request_body)) : '') +
                section('Response Headers', formatJson(log.response_headers)) +
                (log.response_body ? section('Response Body', formatBody(log.response_body)) : '');

            if (log.sql_queries && log.sql_queries.length > 0) {
                html += '<div class="detail-section"><h3>SQL Queries (' + log.sql_queries.length + ')</h3>';
                log.sql_queries.forEach(function(sq) {
                    html += '<div class="sql-query">' +
                        '<div class="sql-text">' + escHtml(sq.query || '') + '</div>' +
                        '<div class="sql-meta">' +
                            (sq.duration_ms != null ? sq.duration_ms.toFixed(2) + 'ms' : '') +
                            (sq.params ? ' | params: ' + escHtml(sq.params) : '') +
                        '</div></div>';
                });
                html += '</div>';
            }

            html += (log.user_agent ? section('User Agent', log.user_agent) : '') +
                '<div id="diff-result-' + log.id + '"></div>';

            panel.innerHTML = html;
        }

        async function copyCurl(id) {
            try {
                const resp = await fetch('/_tracelite/api/curl?id=' + id);
                const data = await resp.json();
                await navigator.clipboard.writeText(data.curl);
                showToast('curl command copied!');
                const btn = document.getElementById('curl-btn-' + id);
                if (btn) { btn.classList.add('copied'); btn.textContent = '\\u2713 Copied'; setTimeout(() => { btn.classList.remove('copied'); btn.textContent = '\\ud83d\\udccb Copy curl'; }, 2000); }
            } catch(e) {
                showToast('Failed to copy curl');
            }
        }

        async function showDiff(id) {
            const log = allLogs.find(l => l.id === id);
            if (!log) return;
            const container = document.getElementById('diff-result-' + id);
            if (!container) return;
            container.innerHTML = '<div class="detail-section"><h3>Loading diff...</h3></div>';
            try {
                const resp = await fetch('/_tracelite/api/diff?id=' + id);
                const data = await resp.json();
                if (data.error) { container.innerHTML = '<div class="detail-section"><h3>Diff</h3><pre>' + escHtml(data.error) + '</pre></div>'; return; }
                if (!data.diffs || data.diffs.length === 0) {
                    container.innerHTML = '<div class="detail-section"><h3>Response Diff</h3><pre>No differences found compared to previous response.</pre></div>';
                    return;
                }
                let diffHtml = '<div class="diff-section"><h3>Response Diff (vs previous)</h3><pre>';
                data.diffs.forEach(function(d) {
                    diffHtml += '<span class="diff-path">' + escHtml(d.path) + ':</span>\\n';
                    diffHtml += '<span class="diff-remove">  - ' + escHtml(String(d.old_value)) + '</span>\\n';
                    diffHtml += '<span class="diff-add">  + ' + escHtml(String(d.new_value)) + '</span>\\n';
                });
                diffHtml += '</pre></div>';
                container.innerHTML = diffHtml;
            } catch(e) {
                container.innerHTML = '<div class="detail-section"><h3>Diff</h3><pre>Error loading diff</pre></div>';
            }
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 2000);
        }

        function section(title, content) {
            return '<div class="detail-section"><h3>' + title + '</h3><pre>' + escHtml(content) + '</pre></div>';
        }

        function formatJson(val) {
            if (!val) return '';
            try {
                if (typeof val === 'string') val = JSON.parse(val);
                return JSON.stringify(val, null, 2);
            } catch {
                return String(val);
            }
        }

        function formatBody(val) {
            try {
                return JSON.stringify(JSON.parse(val), null, 2);
            } catch {
                return val || '';
            }
        }

        function escHtml(s) {
            if (!s) return '';
            return String(s)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        document.getElementById('search').addEventListener('input', renderList);
        document.getElementById('method-filter').addEventListener('change', renderList);

        fetchConfig().then(() => fetchLogs());
        setInterval(fetchLogs, 5000);
    </script>
</body>
</html>"""


def get_dashboard_html() -> str:
    """Return the dashboard HTML page."""
    return DASHBOARD_HTML


def _serialize_log_row(row: Any) -> dict[str, Any]:
    """Serialize a database row tuple to a JSON-serializable dict.

    Handles backward compatibility:
    - 14 elements: new schema with query + sql_queries
    - 13 elements: schema with query but no sql_queries
    - 12 elements: old schema without query
    """
    length = len(row)
    has_sql_queries = length > 13
    has_query_column = length > 12

    result: dict[str, Any] = {
        "id": row[0],
        "timestamp": row[1],
        "method": row[2],
        "path": row[3],
        "query": row[4] if has_query_column else None,
        "status_code": row[5] if has_query_column else row[4],
        "client_ip": row[6] if has_query_column else row[5],
        "user_agent": row[7] if has_query_column else row[6],
        "request_headers": row[8] if has_query_column else row[7],
        "request_body": row[9] if has_query_column else row[8],
        "response_headers": row[10] if has_query_column else row[9],
        "response_body": row[11] if has_query_column else row[10],
        "duration_ms": row[12] if has_query_column else row[11],
    }

    if has_sql_queries and row[13]:
        try:
            result["sql_queries"] = json.loads(row[13])
        except (json.JSONDecodeError, TypeError):
            result["sql_queries"] = []
    else:
        result["sql_queries"] = []

    return result


def get_logs_json(storage: ILoggerStorage, since_seconds: int = 3600) -> str:
    """Return recent logs as a JSON string for the API endpoint."""
    rows = storage.fetch_recent(since_seconds=since_seconds)
    logs = [_serialize_log_row(row) for row in rows]
    return json.dumps(logs)


def _get_log_by_id(storage: ILoggerStorage, log_id: int) -> Optional[dict[str, Any]]:
    """Fetch a single log by ID and serialize it."""
    rows = storage.fetch_recent(since_seconds=86400)
    for row in rows:
        if row[0] == log_id:
            return _serialize_log_row(row)
    return None


def mount_dashboard_starlette(
    app: Any,
    storage: ILoggerStorage,
    path: str = "/_tracelite",
    config: Any = None,
) -> None:
    """Mount the dashboard routes onto a Starlette/FastAPI app."""
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, JSONResponse
    from starlette.routing import Route

    async def dashboard_page(request: Request) -> HTMLResponse:
        del request
        return HTMLResponse(get_dashboard_html())

    async def api_logs(request: Request) -> JSONResponse:
        del request
        logs_json = get_logs_json(storage)
        return JSONResponse(content=json.loads(logs_json))

    async def api_config(request: Request) -> JSONResponse:
        del request
        cfg: dict[str, Any] = {"slow_threshold_ms": 1000}
        if config is not None:
            cfg["slow_threshold_ms"] = getattr(config, "slow_threshold_ms", 1000)
        return JSONResponse(content=cfg)

    async def api_curl(request: Request) -> JSONResponse:
        log_id = int(request.query_params.get("id", 0))
        log = _get_log_by_id(storage, log_id)
        if not log:
            return JSONResponse(content={"error": "Log not found"}, status_code=404)
        headers = log.get("request_headers")
        if isinstance(headers, str):
            try:
                headers = json.loads(headers)
            except (json.JSONDecodeError, TypeError):
                headers = {}
        curl_cmd = generate_curl(
            method=log["method"],
            path=log["path"],
            headers=headers,
            body=log.get("request_body"),
            query=log.get("query"),
        )
        return JSONResponse(content={"curl": curl_cmd})

    async def api_diff(request: Request) -> JSONResponse:
        log_id = int(request.query_params.get("id", 0))
        log = _get_log_by_id(storage, log_id)
        if not log:
            return JSONResponse(content={"error": "Log not found"}, status_code=404)
        prev_logs = storage.fetch_by_path(log["path"], limit=10)
        prev_body = None
        for prev_row in prev_logs:
            prev = _serialize_log_row(prev_row)
            if prev["id"] != log_id:
                prev_body = prev.get("response_body")
                break
        if prev_body is None:
            return JSONResponse(content={"error": "No previous response to compare"})
        diffs = diff_responses(prev_body, log.get("response_body"))
        return JSONResponse(content={"diffs": diffs})

    routes = [
        Route(path, dashboard_page),
        Route(f"{path}/api/logs", api_logs),
        Route(f"{path}/api/config", api_config),
        Route(f"{path}/api/curl", api_curl),
        Route(f"{path}/api/diff", api_diff),
    ]
    app.routes.extend(routes)


def mount_dashboard_flask(
    app: Any,
    storage: ILoggerStorage,
    path: str = "/_tracelite",
    config: Any = None,
) -> None:
    """Mount the dashboard routes onto a Flask app."""
    from flask import Response, jsonify
    from flask import request as flask_request

    endpoint_prefix = path.strip("/").replace("/", "_") or "tracelite"

    def dashboard_page() -> Response:
        return Response(get_dashboard_html(), mimetype="text/html")

    def api_logs() -> Any:
        logs_json = get_logs_json(storage)
        return jsonify(json.loads(logs_json))

    def api_config_view() -> Any:
        cfg: dict[str, Any] = {"slow_threshold_ms": 1000}
        if config is not None:
            cfg["slow_threshold_ms"] = getattr(config, "slow_threshold_ms", 1000)
        return jsonify(cfg)

    def api_curl_view() -> Any:
        log_id = int(flask_request.args.get("id", 0))
        log = _get_log_by_id(storage, log_id)
        if not log:
            return jsonify({"error": "Log not found"}), 404
        headers = log.get("request_headers")
        if isinstance(headers, str):
            try:
                headers = json.loads(headers)
            except (json.JSONDecodeError, TypeError):
                headers = {}
        curl_cmd = generate_curl(
            method=log["method"],
            path=log["path"],
            headers=headers,
            body=log.get("request_body"),
            query=log.get("query"),
        )
        return jsonify({"curl": curl_cmd})

    def api_diff_view() -> Any:
        log_id = int(flask_request.args.get("id", 0))
        log = _get_log_by_id(storage, log_id)
        if not log:
            return jsonify({"error": "Log not found"}), 404
        prev_logs = storage.fetch_by_path(log["path"], limit=10)
        prev_body = None
        for prev_row in prev_logs:
            prev = _serialize_log_row(prev_row)
            if prev["id"] != log_id:
                prev_body = prev.get("response_body")
                break
        if prev_body is None:
            return jsonify({"error": "No previous response to compare"})
        diffs = diff_responses(prev_body, log.get("response_body"))
        return jsonify({"diffs": diffs})

    app.add_url_rule(path, f"{endpoint_prefix}_dashboard", dashboard_page)
    app.add_url_rule(f"{path}/api/logs", f"{endpoint_prefix}_logs", api_logs)
    app.add_url_rule(f"{path}/api/config", f"{endpoint_prefix}_config", api_config_view)
    app.add_url_rule(f"{path}/api/curl", f"{endpoint_prefix}_curl", api_curl_view)
    app.add_url_rule(f"{path}/api/diff", f"{endpoint_prefix}_diff", api_diff_view)


def mount_dashboard_django(
    urlpatterns: list[Any],
    storage: ILoggerStorage,
    path: str = "/_tracelite",
    config: Any = None,
) -> None:
    """Mount the dashboard routes onto Django urlpatterns."""
    from django.http import HttpRequest, HttpResponse, JsonResponse
    from django.urls import path as django_path

    cleaned_path = path.strip("/") or "_tracelite"

    def dashboard_page(request: HttpRequest) -> HttpResponse:
        del request
        return HttpResponse(
            get_dashboard_html().encode("utf-8"), content_type="text/html"
        )

    def api_logs(request: HttpRequest) -> JsonResponse:
        del request
        logs_json = get_logs_json(storage)
        return JsonResponse(json.loads(logs_json), safe=False)

    def api_config_view(request: HttpRequest) -> JsonResponse:
        del request
        cfg: dict[str, Any] = {"slow_threshold_ms": 1000}
        if config is not None:
            cfg["slow_threshold_ms"] = getattr(config, "slow_threshold_ms", 1000)
        return JsonResponse(cfg)

    def api_curl_view(request: HttpRequest) -> JsonResponse:
        log_id = int(request.GET.get("id", 0))
        log = _get_log_by_id(storage, log_id)
        if not log:
            return JsonResponse({"error": "Log not found"}, status=404)
        headers = log.get("request_headers")
        if isinstance(headers, str):
            try:
                headers = json.loads(headers)
            except (json.JSONDecodeError, TypeError):
                headers = {}
        curl_cmd = generate_curl(
            method=log["method"],
            path=log["path"],
            headers=headers,
            body=log.get("request_body"),
            query=log.get("query"),
        )
        return JsonResponse({"curl": curl_cmd})

    def api_diff_view(request: HttpRequest) -> JsonResponse:
        log_id = int(request.GET.get("id", 0))
        log = _get_log_by_id(storage, log_id)
        if not log:
            return JsonResponse({"error": "Log not found"}, status=404)
        prev_logs = storage.fetch_by_path(log["path"], limit=10)
        prev_body = None
        for prev_row in prev_logs:
            prev = _serialize_log_row(prev_row)
            if prev["id"] != log_id:
                prev_body = prev.get("response_body")
                break
        if prev_body is None:
            return JsonResponse({"error": "No previous response to compare"})
        diffs = diff_responses(prev_body, log.get("response_body"))
        return JsonResponse({"diffs": diffs}, safe=False)

    urlpatterns.append(django_path(cleaned_path, dashboard_page))
    urlpatterns.append(django_path(f"{cleaned_path}/api/logs", api_logs))
    urlpatterns.append(django_path(f"{cleaned_path}/api/config", api_config_view))
    urlpatterns.append(django_path(f"{cleaned_path}/api/curl", api_curl_view))
    urlpatterns.append(django_path(f"{cleaned_path}/api/diff", api_diff_view))
