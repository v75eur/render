from flask import Flask, jsonify, render_template_string
import threading, websocket, json, time, os

app = Flask(__name__)
last_price = {"time": int(time.time()), "value": 0}
TOKEN = os.getenv("DERIV_TOKEN", "YDL6LNP2cTH4LO2")

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Duum! Dashboard</title>
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body { background: #0b0e11; color: white; margin: 0; font-family: sans-serif; }
        #chart { height: 500px; width: 100%; }
        .header { padding: 15px; background: #161a1e; display: flex; justify-content: space-between; border-bottom: 1px solid #2b2f33; }
        #price { color: #00ff00; font-weight: bold; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="header">
        <span>DUUM! V75 LIVE</span>
        <div id="price">Attente du prix...</div>
    </div>
    <div id="chart"></div>
    <script>
        const chart = LightweightCharts.createChart(document.getElementById('chart'), {
            layout: { backgroundColor: '#0b0e11', textColor: '#d1d4dc' },
            grid: { vertLines: { color: '#1f2226' }, horzLines: { color: '#1f2226' } },
            timeScale: { timeVisible: true, secondsVisible: true }
        });
        const lineSeries = chart.addLineSeries({ color: '#2962FF', lineWidth: 2 });

        async function updateChart() {
            try {
                const response = await fetch('/price');
                const data = await response.json();
                if (data.value > 0) {
                    document.getElementById('price').innerText = data.value;
                    lineSeries.update({ time: data.time, value: data.value });
                }
            } catch (e) { console.error("Erreur flux:", e); }
        }
        setInterval(updateChart, 1000);
    </script>
</body>
</html>
"""

def fetch_data():
    global last_price
    while True:
        try:
            ws = websocket.create_connection("wss://ws.binaryws.com/websockets/v3?app_id=1089")
            ws.send(json.dumps({"authorize": TOKEN}))
            ws.send(json.dumps({"ticks": "R_75", "subscribe": 1}))
            while True:
                res = json.loads(ws.recv())
                if 'tick' in res:
                    last_price = {"time": int(time.time()), "value": res['tick']['quote']}
        except:
            time.sleep(5)

@app.route('/')
def home(): return render_template_string(INDEX_HTML)

@app.route('/price')
def get_price(): return jsonify(last_price)

if __name__ == "__main__":
    threading.Thread(target=fetch_data, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
