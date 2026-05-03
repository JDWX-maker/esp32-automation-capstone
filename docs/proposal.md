from machine import Pin, ADC
from time import sleep
import network
import socket
import ure
import ujson
import os

# -------------------------
# Hardware Setup
# -------------------------
ldr = ADC(Pin(1))
ldr.atten(ADC.ATTN_11DB)

green_led = Pin(4, Pin.OUT)   # Bright
red_led   = Pin(5, Pin.OUT)   # Dark

CONFIG_FILE = "config.json"
mode = "AUTO"
THRESHOLD = 800

# -------------------------
# Config Persistence
# -------------------------
def load_config():
    global THRESHOLD, mode
    if CONFIG_FILE in os.listdir():
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = ujson.load(f)
            THRESHOLD = int(cfg.get("threshold", THRESHOLD))
            mode = cfg.get("mode", mode)
        except:
            pass

def save_config():
    cfg = {
        "threshold": THRESHOLD,
        "mode": mode
    }
    try:
        with open(CONFIG_FILE, "w") as f:
            ujson.dump(cfg, f)
    except:
        pass

load_config()

# -------------------------
# WiFi Setup
# -------------------------
ssid = "CenturyLink0241"
password = "7au2pt7gb8ue2j"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    sleep(0.2)

print("Connected:", wlan.ifconfig()[0])

# -------------------------
# AUTO Mode Logic
# -------------------------
def auto_control(value):
    # Low value = dark, high value = light (matches threshold logic)
    if value < THRESHOLD:
        red_led.on()
        green_led.off()
        return "dark"
    else:
        red_led.off()
        green_led.on()
        return "light"

def get_led_states():
    return {
        "green": int(green_led.value()),
        "red": int(red_led.value())
    }

# -------------------------
# Brightness Interpretation (matches state logic)
# -------------------------
def interpret_light(value):
    # These ranges assume: low ADC = darker, high ADC = brighter
    if value > 2500:
        return "Very Bright (sunlight)"
    elif value > 1500:
        return "Bright (indoor lighting)"
    elif value > 800:
        return "Dim (evening or shaded)"
    elif value > 300:
        return "Low Light (near dark)"
    else:
        return "Dark (night or covered)"

# -------------------------
# Calibration
# -------------------------
def calibrate_threshold(samples=50, delay=0.05):
    global THRESHOLD
    vals = []
    for _ in range(samples):
        vals.append(ldr.read())
        sleep(delay)
    if vals:
        vmin = min(vals)
        vmax = max(vals)
        THRESHOLD = (vmin + vmax) // 2
        save_config()
    return THRESHOLD

# -------------------------
# Webpage Template (Style 1 Dashboard + Brightness)
# -------------------------
def webpage():
    return f"""
    <html>
    <head>
        <title>ESP32 Light Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --bg: #f4f4f4;
                --card-bg: #ffffff;
                --text: #222222;
                --accent: #0078d4;
                --accent-soft: #e1f0ff;
                --danger: #d13438;
                --success: #107c10;
            }}
            body.dark {{
                --bg: #111827;
                --card-bg: #1f2937;
                --text: #e5e7eb;
                --accent: #3b82f6;
                --accent-soft: #1e3a8a;
                --danger: #f87171;
                --success: #4ade80;
            }}
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: var(--bg);
                color: var(--text);
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                padding: 16px;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }}
            .title {{
                font-size: 1.4rem;
                font-weight: bold;
            }}
            .theme-toggle {{
                cursor: pointer;
                padding: 6px 10px;
                border-radius: 999px;
                border: 1px solid var(--accent);
                color: var(--accent);
                background: transparent;
                font-size: 0.8rem;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 12px;
            }}
            .card {{
                background: var(--card-bg);
                border-radius: 10px;
                padding: 12px 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            }}
            .card h3 {{
                margin: 0 0 8px 0;
                font-size: 1rem;
            }}
            .value {{
                font-size: 1.4rem;
                font-weight: bold;
            }}
            .icon {{
                font-size: 2.5rem;
            }}
            .badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 999px;
                font-size: 0.75rem;
                margin-left: 6px;
            }}
            .badge-auto {{
                background: var(--accent-soft);
                color: var(--accent);
            }}
            .badge-manual {{
                background: #fef3c7;
                color: #92400e;
            }}
            .badge-light {{
                background: #dcfce7;
                color: var(--success);
            }}
            .badge-dark {{
                background: #fee2e2;
                color: var(--danger);
            }}
            .led-dot {{
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 6px;
            }}
            .led-green-on {{
                background: var(--success);
            }}
            .led-green-off {{
                background: #9ca3af;
            }}
            .led-red-on {{
                background: var(--danger);
            }}
            .led-red-off {{
                background: #9ca3af;
            }}
            .controls button {{
                margin: 3px;
                padding: 6px 10px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                font-size: 0.8rem;
            }}
            .btn-primary {{
                background: var(--accent);
                color: white;
            }}
            .btn-secondary {{
                background: #e5e7eb;
                color: #111827;
            }}
            body.dark .btn-secondary {{
                background: #374151;
                color: #e5e7eb;
            }}
            .btn-danger {{
                background: var(--danger);
                color: white;
            }}
            .btn-success {{
                background: var(--success);
                color: white;
            }}
            .slider-row {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            input[type=range] {{
                width: 100%;
            }}
            #chart {{
                width: 100%;
                height: 180px;
                background: #0f172a;
                border-radius: 8px;
                position: relative;
                overflow: hidden;
            }}
            #chart canvas {{
                width: 100%;
                height: 100%;
            }}
            .status-json {{
                font-family: monospace;
                font-size: 0.75rem;
                max-height: 120px;
                overflow-y: auto;
                background: #111827;
                color: #e5e7eb;
                padding: 6px;
                border-radius: 6px;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <div class="header">
                <div class="title">ESP32 Light Sensor Dashboard</div>
                <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">Dark</button>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>Environment</h3>
                    <div class="icon" id="icon">☀️</div>
                    <div>
                        <span class="value" id="ldr">0</span>
                        <span>LDR</span>
                    </div>
                    <div>
                        <span>State:</span>
                        <span class="badge badge-light" id="stateBadge">LIGHT</span>
                    </div>
                    <div>
                        <span>Brightness:</span>
                        <span class="badge badge-light" id="brightnessBadge">Unknown</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Mode & Threshold</h3>
                    <div>
                        <span>Mode:</span>
                        <span class="badge badge-auto" id="modeBadge">AUTO</span>
                    </div>
                    <div style="margin-top:8px;">
                        <div class="slider-row">
                            <span>Threshold:</span>
                            <span class="value" id="threshold">{THRESHOLD}</span>
                        </div>
                        <input type="range" min="100" max="3000" value="{THRESHOLD}"
                               oninput="setThreshold(this.value)">
                    </div>
                    <div style="margin-top:8px;" class="controls">
                        <button class="btn-primary" onclick="setMode('AUTO')">AUTO</button>
                        <button class="btn-secondary" onclick="setMode('MANUAL')">MANUAL</button>
                        <button class="btn-success" onclick="calibrate()">Calibrate</button>
                    </div>
                </div>

                <div class="card">
                    <h3>LEDs</h3>
                    <div>
                        <div>
                            <span class="led-dot led-green-off" id="greenDot"></span>
                            <span>Green (Light)</span>
                        </div>
                        <div>
                            <span class="led-dot led-red-off" id="redDot"></span>
                            <span>Red (Dark)</span>
                        </div>
                    </div>
                    <div style="margin-top:8px;" class="controls">
                        <button class="btn-secondary" onclick="ledControl('green','on')">Green ON</button>
                        <button class="btn-secondary" onclick="ledControl('green','off')">Green OFF</button>
                        <button class="btn-secondary" onclick="ledControl('red','on')">Red ON</button>
                        <button class="btn-secondary" onclick="ledControl('red','off')">Red OFF</button>
                    </div>
                    <div style="margin-top:8px;" class="controls">
                        <button class="btn-danger" onclick="bothOff()">Both OFF</button>
                        <button class="btn-success" onclick="bothOn()">Both ON</button>
                    </div>
                </div>

                <div class="card">
                    <h3>Brightness Level</h3>
                    <div id="brightnessText">Unknown</div>
                </div>

                <div class="card">
                    <h3>Status JSON</h3>
                    <div id="statusJson" class="status-json">{{}}</div>
                </div>
            </div>

            <div class="card" style="margin-top:12px;">
                <h3>LDR History</h3>
                <div id="chart">
                    <canvas id="chartCanvas"></canvas>
                </div>
            </div>
        </div>

        <script>
            let history = [];
            const maxPoints = 60;

            function updateData() {{
                fetch('/api/status')
                .then(r => r.json())
                .then(data => {{
                    document.getElementById('ldr').innerHTML = data.value;
                    document.getElementById('threshold').innerHTML = data.threshold;

                    // Mode badge
                    const modeBadge = document.getElementById('modeBadge');
                    modeBadge.innerHTML = data.mode;
                    if (data.mode === "AUTO") {{
                        modeBadge.className = "badge badge-auto";
                    }} else {{
                        modeBadge.className = "badge badge-manual";
                    }}

                    // State badge + icon
                    const stateBadge = document.getElementById('stateBadge');
                    const icon = document.getElementById('icon');
                    if (data.state === "light") {{
                        stateBadge.innerHTML = "LIGHT";
                        stateBadge.className = "badge badge-light";
                        icon.innerHTML = "☀️";
                    }} else {{
                        stateBadge.innerHTML = "DARK";
                        stateBadge.className = "badge badge-dark";
                        icon.innerHTML = "🌙";
                    }}

                    // Brightness interpretation (kept in sync with state)
                    const brightnessBadge = document.getElementById('brightnessBadge');
                    const brightnessText = document.getElementById('brightnessText');
                    brightnessBadge.innerHTML = data.brightness;
                    brightnessText.innerHTML = data.brightness;

                    if (data.state === "light") {{
                        brightnessBadge.className = "badge badge-light";
                    }} else {{
                        brightnessBadge.className = "badge badge-dark";
                    }}

                    // LED dots
                    const greenDot = document.getElementById('greenDot');
                    const redDot = document.getElementById('redDot');
                    if (data.led.green) {{
                        greenDot.className = "led-dot led-green-on";
                    }} else {{
                        greenDot.className = "led-dot led-green-off";
                    }}
                    if (data.led.red) {{
                        redDot.className = "led-dot led-red-on";
                    }} else {{
                        redDot.className = "led-dot led-red-off";
                    }}

                    // Status JSON
                    document.getElementById('statusJson').innerText = JSON.stringify(data, null, 2);

                    // Chart
                    addToHistory(data.value);
                    drawChart();
                }})
                .catch(e => {{
                    console.log(e);
                }});
            }}

            function setThreshold(val) {{
                fetch('/set_threshold?value=' + val);
            }}

            function setMode(val) {{
                fetch('/api/mode?value=' + val);
            }}

            function ledControl(color, state) {{
                fetch('/api/led/' + color + '?state=' + state);
            }}

            function bothOff() {{
                fetch('/api/led/green?state=off');
                fetch('/api/led/red?state=off');
            }}

            function bothOn() {{
                fetch('/api/led/green?state=on');
                fetch('/api/led/red?state=on');
            }}

            function calibrate() {{
                fetch('/api/calibrate')
                .then(r => r.json())
                .then(data => {{
                    document.getElementById('threshold').innerHTML = data.threshold;
                }});
            }}

            function addToHistory(v) {{
                history.push(v);
                if (history.length > maxPoints) history.shift();
            }}

            function drawChart() {{
                const canvas = document.getElementById('chartCanvas');
                const ctx = canvas.getContext('2d');
                const w = canvas.width = canvas.offsetWidth;
                const h = canvas.height = canvas.offsetHeight;

                ctx.clearRect(0, 0, w, h);
                if (history.length < 2) return;

                const minVal = Math.min.apply(null, history);
                const maxVal = Math.max.apply(null, history);
                const span = (maxVal - minVal) || 1;

                ctx.strokeStyle = "#22c55e";
                ctx.lineWidth = 2;
                ctx.beginPath();
                history.forEach((v, i) => {{
                    const x = (i / (history.length - 1)) * w;
                    const y = h - ((v - minVal) / span) * h;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }});
                ctx.stroke();
            }}

            function toggleTheme() {{
                const body = document.body;
                const btn = document.getElementById('themeBtn');
                if (body.classList.contains('dark')) {{
                    body.classList.remove('dark');
                    btn.innerHTML = "Dark";
                    localStorage.setItem('theme', 'light');
                }} else {{
                    body.classList.add('dark');
                    btn.innerHTML = "Light";
                    localStorage.setItem('theme', 'dark');
                }}
            }}

            function initTheme() {{
                const t = localStorage.getItem('theme') || 'light';
                const body = document.body;
                const btn = document.getElementById('themeBtn');
                if (t === 'dark') {{
                    body.classList.add('dark');
                    btn.innerHTML = "Light";
                }} else {{
                    body.classList.remove('dark');
                    btn.innerHTML = "Dark";
                }}
            }}

            initTheme();
            updateData();
            setInterval(updateData, 500);
        </script>
    </body>
    </html>
    """

# -------------------------
# Web Server Setup
# -------------------------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
s.settimeout(0.01)

print("Web server running...")

# -------------------------
# Main Loop
# -------------------------
while True:
    value = ldr.read()

    if mode == "AUTO":
        state = auto_control(value)
    else:
        state = "light" if value >= THRESHOLD else "dark"

    try:
        client, addr = s.accept()
        request = client.recv(1024).decode()

        # Legacy live data endpoint
        if "/data" in request:
            resp = ujson.dumps({
                "value": value,
                "state": state,
                "mode": mode,
                "threshold": THRESHOLD
            })
            client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            client.send(resp)
            client.close()
            continue

        # Legacy threshold slider
        match = ure.search("GET /set_threshold\?value=(\d+)", request)
        if match:
            THRESHOLD = int(match.group(1))
            save_config()
            client.send("HTTP/1.1 200 OK\r\n\r\n")
            client.close()
            continue

        # REST API: status
        if "/api/status" in request:
            resp = ujson.dumps({
                "value": value,
                "state": state,
                "mode": mode,
                "threshold": THRESHOLD,
                "led": get_led_states(),
                "brightness": interpret_light(value)
            })
            client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            client.send(resp)
            client.close()
            continue

        # REST API: mode
        match = ure.search("GET /api/mode\?value=([A-Z]+)", request)
        if match:
            new_mode = match.group(1)
            if new_mode in ("AUTO", "MANUAL"):
                mode = new_mode
                save_config()
            client.send("HTTP/1.1 200 OK\r\n\r\n")
            client.close()
            continue

        # REST API: LED control
        match = ure.search("GET /api/led/(green|red)\?state=(on|off)", request)
        if match:
            color = match.group(1)
            state_req = match.group(2)
            mode = "MANUAL"
            if color == "green":
                if state_req == "on":
                    green_led.on()
                    red_led.off()
                else:
                    green_led.off()
            elif color == "red":
                if state_req == "on":
                    red_led.on()
                    green_led.off()
                else:
                    red_led.off()
            save_config()
            client.send("HTTP/1.1 200 OK\r\n\r\n")
            client.close()
            continue

        # REST API: calibrate
        if "/api/calibrate" in request:
            new_th = calibrate_threshold()
            resp = ujson.dumps({"threshold": new_th})
            client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            client.send(resp)
            client.close()
            continue

        # Legacy manual controls
        if "/green_on" in request:
            mode = "MANUAL"
            green_led.on()
            red_led.off()

        if "/green_off" in request:
            mode = "MANUAL"
            green_led.off()

        if "/red_on" in request:
            mode = "MANUAL"
            red_led.on()
            green_led.off()

        if "/red_off" in request:
            mode = "MANUAL"
            red_led.off()

        if "/auto" in request:
            mode = "AUTO"
            state = auto_control(value)
            save_config()

        # Send main webpage
        html = webpage()
        client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        client.send(html)
        client.close()

    except OSError:
        pass

    sleep(0.1)
