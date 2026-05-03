import requests
import time
import json
from datetime import datetime

ESP32_IP = "http://192.168.0.39"   # ← update to your ESP32 IP
LOG_FILE = "esp32_data_log.jsonl"

def get_status():
    try:
        r = requests.get(f"{ESP32_IP}/api/status", timeout=3)
        return r.json()
    except Exception as e:
        print("Error contacting ESP32:", e)
        return None

def log_status(data):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "ldr": data["value"],
        "brightness": data["brightness"],
        "state": data["state"],
        "threshold": data["threshold"],
        "mode": data["mode"],
        "led": data["led"]
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    print("ESP32 Data Logger Running...")
    print("Press CTRL+C to stop.\n")

    while True:
        data = get_status()
        if data:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"LDR={data['value']}  Brightness={data['brightness']}  State={data['state']}")
            log_status(data)

        time.sleep(2)

if __name__ == "__main__":
    main()
