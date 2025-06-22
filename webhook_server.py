from flask import Flask, request
import requests
import json

app = Flask(__name__)

# Load config
with open("config.json") as f:
    config = json.load(f)

def trigger_shelly(ip):
    try:
        requests.get(f"http://{ip}/relay/0?turn=on")
        requests.get(f"http://{ip}/relay/0?turn=off")
    except Exception as e:
        print(f"Error triggering Shelly {ip}: {e}")

@app.route('/webhook', methods=['POST'])
def handle_stripe():
    payload = request.get_json()
    print("Received:", payload)

    if payload.get('type') == 'checkout.session.completed':
        session = payload['data']['object']
        line_items = session.get('display_items', [])
        for item in line_items:
            product_id = item['price']['product']
            for restaurant, boxes in config.items():
                for box, info in boxes.items():
                    if info['stripe_product_id'] == product_id:
                        ip = info['shelly_ip']
                        print(f"Triggering Shelly at {ip} for {restaurant} {box}")
                        trigger_shelly(ip)
                        return 'ok', 200
    return 'ignored', 200

if __name__ == '__main__':
    app.run(port=5000)