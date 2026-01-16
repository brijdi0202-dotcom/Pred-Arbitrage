import json
import time
from websocket import WebSocketApp

URL = "wss://ws.limitless.exchange/socket.io/?EIO=4&transport=websocket"
HEADERS = {
    "Origin": "https://limitless.exchange",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0",
}
MARKET_SLUG = "dollarbtc-above-dollar8777941-on-dec-25-0800-utc-1766646007739"
NS = "/markets"

YES_ID = None
NO_ID = None

def send_connect(ws):
    ws.send(f"40{NS},")

def send_subscribe(ws, market_slug):
    event = ["subscribe_market_prices", {"marketSlugs": [market_slug]}]
    ws.send(f"42{NS},{json.dumps(event, separators=(',', ':'))}")
    print("-> Subscribing...")

def on_message(ws, message):
    if message == "2":
        ws.send("3")
        return
    if message == "3":
        return

    if message.startswith(f"40{NS},"):
        return

    if message.startswith(f"42{NS},"):
        try:
            json_part = message.split(",", 1)[1]
            evt = json.loads(json_part)
            if isinstance(evt, list) and len(evt) >= 1:
                event_name = evt[0]
                event_payload = evt[1] if len(evt) > 1 else None

                if event_name == "system" and isinstance(event_payload, dict):
                    if "Successfully registered connection" in event_payload.get("message", ""):
                        time.sleep(0.1)
                        send_subscribe(ws, MARKET_SLUG)
                
                if event_name == "orderbookUpdate":
                    ob = event_payload.get("orderbook", {})
                    token_id = ob.get("tokenId")
                    asks = ob.get("asks", [])
                    bids = ob.get("bids", [])
                    
                    top_asks = asks[:3]
                    top_bids = bids[:3]
                    
                    global YES_ID, NO_ID
                    if YES_ID is None:
                        YES_ID = token_id
                    elif NO_ID is None and token_id != YES_ID:
                        NO_ID = token_id
                    
                    def format_orders(orders):
                        return [{'price': float(o.get('price')), 'size': float(o.get('size'))/1000000} for o in orders]

                    if token_id == YES_ID:
                        print(f"YES ASKS: {format_orders(top_asks)}")
                        print(f"NO ASKS: {format_orders(top_bids)}")
                    elif token_id == NO_ID:
                        print(f"YES ASKS: {format_orders(top_bids)}")
                        print(f"NO ASKS: {format_orders(top_asks)}")
                    else:
                        print(f"UNKNOWN ({token_id}) YES ASKS: {format_orders(top_asks)}")
                        print(f"UNKNOWN ({token_id}) NO ASKS: {format_orders(top_bids)}")

        except Exception:
            pass

def on_open(ws):
    print("[open]")
    send_connect(ws)

def on_error(ws, error):
    print("[error]", error)

def on_close(ws, close_status_code, close_msg):
    print("[close]")

def run():
    wsapp = WebSocketApp(
        URL,
        header=[f"{k}: {v}" for k, v in HEADERS.items()],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    wsapp.run_forever()

if __name__ == "__main__":
    run()
