from flask import Flask, jsonify, render_template_string
import threading, websocket, json, time

app = Flask(__name__)
last_price = {"time": 0, "value": 0}
TOKEN = "YDL6LNP2cTH4LO2"

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Duum! Dashboard</title>
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body { background: #0b0e11; color: white; margin: 0; font-family: sans-serif; overflow: hidden; }
        #chart { height: 92vh; width: 100%; }
        .header { padding: 10px 20px; background: #161a1e; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2b2f33; }
        .price-up { color: #00ff00; font-size: 1.2em; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <span>DUUM! LIVE ENGINE</span>
        <span id="price" class="price-up">Connexion...</span>
    </div>
    <div id="chart"></div>
    <script>
        const chart = LightweightCharts.createChart(document.getElementById('chart'), {
            layout: { backgroundColor: '#0b0e11', textColor: '#d1d4dc' },
            grid: { vertLines: { color: '#1f2226' }, horzLines: { color: '#1f2226' } },
            timeScale: { timeVisible: true, secondsVisible: true },
        });
        const lineSeries = chart.addLineSeries({ color: '#2962FF', lineWidth: 2 });

        async function refresh() {
            try {
                const r = await fetch('/price');
                const d = await r.json();
                if (d.value > 0) {
                    document.getElementById('price').innerText = d.value;
                    lineSeries.update({ time: d.time, value: d.value });
                }
            } catch (e) {}
        }
        setInterval(refresh, 1000);
    </script>
</body>
</html>
"""

def stream():
    global last_price
    while True:
        try:
            ws = websocket.create_connection("wss://ws.binaryws.com/websockets/v3?app_id=1089")
            ws.send(json.dumps({"authorize": TOKEN}))
            ws.send(json.dumps({"ticks": "R_75", "subscribe": 1}))
            while True:
                data = json.loads(ws.recv())
                if 'tick' in data:
                    last_price = {"time": int(time.time()), "value": data['tick']['quote']}
        except:
            time.sleep(2)

@app.route('/')
def home(): return render_template_string(INDEX_HTML)

@app.route('/price')
def get_price(): return jsonify(last_price)

if __name__ == "__main__":
    threading.Thread(target=stream, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
