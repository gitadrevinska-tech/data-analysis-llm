from flask import Flask, jsonify, send_file, Response
import subprocess, threading, os, glob
from datetime import datetime

app = Flask(__name__)
log_lines = []
is_running = False

HTML = """<!DOCTYPE html>
<html lang="lv">
<head>
    <meta charset="UTF-8">
    <title>Datu Analīze ar LLM</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; min-height: 100vh; }
        .header { background: #1a1d2e; padding: 24px 40px; border-bottom: 1px solid #2d3148; }
        .header h1 { font-size: 22px; color: #7c8cf8; }
        .header p { font-size: 13px; color: #6b7280; margin-top: 4px; }
        .container { max-width: 1000px; margin: 40px auto; padding: 0 24px; }
        .card { background: #1a1d2e; border: 1px solid #2d3148; border-radius: 12px; padding: 28px; margin-bottom: 24px; }
        .card h2 { font-size: 13px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }
        .btn { padding: 12px 32px; border-radius: 8px; border: none; font-size: 15px; cursor: pointer; font-weight: 600; background: #7c8cf8; color: white; }
        .btn:hover { background: #6470e8; }
        .btn:disabled { background: #3d4268; color: #6b7280; cursor: not-allowed; }
        .status { display: inline-block; margin-left: 16px; font-size: 14px; color: #6b7280; vertical-align: middle; }
        .log-box { background: #0f1117; border: 1px solid #2d3148; border-radius: 8px; padding: 16px; height: 300px; overflow-y: auto; font-family: monospace; font-size: 13px; line-height: 1.6; }
        .history-table { width: 100%; border-collapse: collapse; }
        .history-table th { text-align: left; padding: 10px 16px; font-size: 12px; color: #6b7280; text-transform: uppercase; border-bottom: 1px solid #2d3148; }
        .history-table td { padding: 14px 16px; border-bottom: 1px solid #1e2235; font-size: 14px; }
        .download-btn { padding: 6px 16px; background: transparent; border: 1px solid #7c8cf8; color: #7c8cf8; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .download-btn:hover { background: #7c8cf8; color: white; }
        .empty { color: #6b7280; font-size: 14px; text-align: center; padding: 24px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Automatiska Datu Analize ar LLM</h1>
        <p>MySQL databaze -> AI analize -> PDF atskaite</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Jauna Analize</h2>
            <button class="btn" id="startBtn" onclick="startAnalysis()">Sakt Analizi</button>
            <span class="status" id="status"></span>
        </div>
        <div class="card">
            <h2>Izpildes Zurnals</h2>
            <div class="log-box" id="logBox"><div class="empty">Zurnals paradisies seit...</div></div>
        </div>
        <div class="card">
            <h2>Parskatu Vesture</h2>
            <div id="historyContainer"><div class="empty">Ielade...</div></div>
        </div>
    </div>
    <script>
        var polling = null;
        function startAnalysis() {
            fetch('/start', {method: 'POST'})
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.status === 'already_running') { alert('Analize jau notiek!'); return; }
                document.getElementById('startBtn').disabled = true;
                document.getElementById('status').innerText = 'Analize notiek...';
                document.getElementById('logBox').innerHTML = '';
                polling = setInterval(fetchLogs, 1000);
            });
        }
        function fetchLogs() {
            fetch('/logs')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var box = document.getElementById('logBox');
                box.innerHTML = data.logs.map(function(line) {
                    return '<div>' + line + '</div>';
                }).join('');
                box.scrollTop = box.scrollHeight;
                if (!data.running && data.logs.length > 0) {
                    clearInterval(polling);
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('status').innerText = 'Analize pabeigta!';
                    loadHistory();
                }
            });
        }
        function loadHistory() {
            fetch('/history')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var c = document.getElementById('historyContainer');
                if (data.runs.length === 0) { c.innerHTML = '<div class="empty">Vel nav neviens parskats</div>'; return; }
                var rows = data.runs.map(function(r, i) {
    var btn = '<button class="download-btn" onclick="download(this.dataset.name)" data-name="' + r.name + '">Lejupieladet PDF</button>';
    return '<tr><td>' + (data.runs.length - i) + '</td><td>' + r.date + '</td><td>' + btn + '</td></tr>';
}).join('');
                c.innerHTML = '<table class="history-table"><thead><tr><th>#</th><th>Datums</th><th>Lejupieladet</th></tr></thead><tbody>' + rows + '</tbody></table>';
            });
        }
        function download(name) { window.location.href = '/download/' + name; }
        loadHistory();
    </script>
</body>
</html>"""

def run_analysis():
    global log_lines, is_running
    is_running = True
    log_lines = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/app/ui/output/run_" + timestamp
    os.makedirs(output_dir + "/charts", exist_ok=True)
    env = os.environ.copy()
    env["OUTPUT_DIR"] = output_dir
    env["CHARTS_DIR"] = output_dir + "/charts"
    env["PDF_OUTPUT"] = output_dir + "/report.pdf"
    process = subprocess.Popen(["python", "/app/main.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    for line in process.stdout:
        log_lines.append(line.rstrip())
    process.wait()
    is_running = False

@app.route("/")
def index():
    return Response(HTML, mimetype='text/html')

@app.route("/start", methods=["POST"])
def start():
    global is_running
    if is_running:
        return jsonify({"status": "already_running"})
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()
    return jsonify({"status": "started"})

@app.route("/logs")
def logs():
    return jsonify({"logs": log_lines, "running": is_running})

@app.route("/history")
def history():
    runs = []
    for pdf in sorted(glob.glob("/app/ui/output/run_*/report.pdf"), reverse=True):
        run_dir = os.path.dirname(pdf)
        run_name = os.path.basename(run_dir)
        ts = run_name.replace("run_", "")
        try:
            dt = datetime.strptime(ts, "%Y%m%d_%H%M%S").strftime("%d.%m.%Y %H:%M:%S")
        except:
            dt = ts
        runs.append({"name": run_name, "date": dt})
    # Pārbaudi arī noklusējuma vietu
    if os.path.exists("/app/ui/output/report.pdf"):
        mtime = os.path.getmtime("/app/ui/output/report.pdf")
        dt = datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M:%S")
        runs.append({"name": "default", "date": dt})
    return jsonify({"runs": runs})

@app.route("/download/<run_name>")
def download(run_name):
    if run_name == "default":
        pdf_path = "/app/ui/output/report.pdf"
    else:
        pdf_path = "/app/ui/output/" + run_name + "/report.pdf"
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name="atskaite_" + run_name + ".pdf")
    return "Nav atrasts", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)