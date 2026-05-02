from flask import Flask, jsonify, render_template_string
import threading, websocket, json, time, os

app = Flask(__name__)
last_price = {"time": 0, "value": "Attente..."}
TOKEN = os.getenv("DERIV_TOKEN", "YDL6LNP2cTH4LO2")

@app.route('/')
def home():
    return """
    <html>
        <body style="background:#000; color:#0f0; display:flex; justify-content:center; align-items:center; height:100vh; font-family:monospace;">
            <div style="text-align:center;">
                <h1>DUUM! V75 LIVE</h1>
                <div id="p" style="font-size:80px;">--</div>
            </div>
            <script>
                setInterval(async () => {
                    const r = await fetch('/price');
                    const d = await r.json();
                    document.getElementById('p').innerText = d.value;
                }, 1000);
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
                res = json.loads(ws.recv())
                if 'tick' in res:
                    last_price = {"time": int(time.time()), "value": res['tick']['quote']}
        except:
            time.sleep(2)

@app.route('/price')
def get_price(): return jsonify(last_price)

if __name__ == "__main__":
    threading.Thread(target=stream, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
