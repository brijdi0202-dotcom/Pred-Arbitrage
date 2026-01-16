import json
from websocket import WebSocketApp
import requests

# Replace this with any market slug you want to subscribe to:
MARKET_SLUG = "bitcoin-up-or-down-december-25-2am-et"

WSS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
GAMMA_API = "https://gamma-api.polymarket.com/markets?slug={}"

YES = { "asks": {}, "bids": {} }
NO = { "asks": {}, "bids": {} }

def on_open(ws):
    print("Connected")
    subscribe_msg = { "type": "market", "assets_ids": [TOKEN_ID] }
    ws.send(json.dumps(subscribe_msg))
    print("Subscribed to asset:", TOKEN_ID)

def on_message(ws, message):
    data = json.loads(message)
    event = data.get("event_type")
    if data.get("event_type") == "price_change":
        for change in data["price_changes"]:
            # print(change)
            if(change['asset_id'] == TOKEN_ID):
                size = float(change["size"])
                side = change["side"]
                if side == "SELL":
                    book_side = YES["asks"]
                else:
                    book_side = YES["bids"]

                price = float(change["price"])
                if size == 0:
                    book_side.pop(price, None)
                else:
                    book_side[price] = size
            else:
                size = float(change["size"])
                side = change["side"]
                if side == "SELL":
                    book_side = NO["asks"]
                else:
                    book_side = NO["bids"]

                price = float(change["price"])
                if size == 0:
                    book_side.pop(price, None)
                else:
                    book_side[price] = size
        print_top_levels()

def print_top_levels():
    asks = sorted(YES["asks"].items())[:3]
    bids = sorted(YES["bids"].items())[:3]
    print("YES ASKS:", asks)
    # print("YES BIDS:", bids)
    
    asks = sorted(NO["asks"].items())[:3]
    bids = sorted(NO["bids"].items())[:3]
    print("NO ASKS:", asks)
    # print("NO BIDS:", bids)
    print("-" * 40)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("Disconnected")

def fetch_token_ids(slug: str):
    """Call Gamma API for the slug and extract clobTokenIds as a list of strings."""
    url = GAMMA_API.format(slug)
    print(f"🔎 Fetching market data from: {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    j = resp.json()

    # The API can return various shapes. Try these strategies:
    candidates = []

    if isinstance(j, dict):
        # common shapes: {'markets': [...]} or {'data': [...]}, or the market dict itself
        for key in ("markets", "data", "results", "market", "markets_list"):
            val = j.get(key)
            if isinstance(val, list):
                candidates.extend(val)
            elif isinstance(val, dict):
                candidates.append(val)
        # as a last resort, consider the dict itself as candidate
        candidates.append(j)
    elif isinstance(j, list):
        candidates.extend(j)

    # Find first candidate that contains 'clobTokenIds' (or similar key)
    token_list = None
    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        for key in ("clobTokenIds", "clob_token_ids", "clob_tokens", "tokenIds", "token_ids"):
            if key in cand:
                raw = cand[key]
                # raw might already be a list or a JSON-stringified list
                if isinstance(raw, list):
                    token_list = [str(x) for x in raw]
                elif isinstance(raw, str):
                    # attempt to parse JSON string
                    try:
                        parsed = json.loads(raw)
                        if isinstance(parsed, list):
                            token_list = [str(x) for x in parsed]
                        else:
                            # maybe comma separated
                            token_list = [p.strip() for p in raw.strip('[]').split(',') if p.strip()]
                    except Exception:
                        # fallback to splitting
                        token_list = [p.strip().strip('\"\'') for p in raw.strip('[]').split(',') if p.strip()]
                break
        if token_list:
            break

    if not token_list:
        # As a final attempt, scan through values looking for something that looks like a token id
        for cand in candidates:
            if not isinstance(cand, dict):
                continue
            for v in cand.values():
                if isinstance(v, str) and v.startswith('[') and '"' in v and ']' in v:
                    try:
                        parsed = json.loads(v)
                        if isinstance(parsed, list):
                            token_list = [str(x) for x in parsed]
                            break
                    except Exception:
                        continue
            if token_list:
                break

    if not token_list:
        raise RuntimeError(f"clobTokenIds not found in Gamma API response for slug '{slug}'. Full response saved to 'gamma_response.json'")

    print(f"✅ Found {len(token_list)} token ids.")
    return token_list

TOKEN_ID = fetch_token_ids(MARKET_SLUG)[0]

ws = WebSocketApp(
    WSS_URL,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.run_forever()
