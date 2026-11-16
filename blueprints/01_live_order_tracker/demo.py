"""Runs the whole Live Order Tracker in-process (no server, no network) and narrates what happens.
Needs: pip install fastapi httpx          Run: python demo.py
"""
import app as tracker
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


def say(title):
    print(f"\n== {title}")


def main():
    with TestClient(tracker.build_app()) as client:                 # fresh in-memory database
        say("1. place an order (with an Idempotency-Key)")
        body = {"customer": "Asha", "items": ["pizza", "cola"]}
        first = client.post("/orders", json=body, headers={"Idempotency-Key": "abc-1"})
        order = first.json()
        print(first.status_code, order["id"], order["status"])

        say("2. the phone app retries the same request (bad network): no duplicate order")
        again = client.post("/orders", json=body, headers={"Idempotency-Key": "abc-1"})
        print(again.status_code, "same id?", again.json()["id"] == order["id"])

        say("3. validation at the edge")
        bad = client.post("/orders", json={"customer": "", "items": []})
        print(bad.status_code, [e["loc"][-1] for e in bad.json()["detail"]])

        say("4. a customer watches live over a WebSocket while the kitchen moves the order")
        oid = order["id"]
        with client.websocket_connect(f"/ws/orders/{oid}") as ws:
            snap = ws.receive_json()
            print("snapshot:", snap["type"], snap["order"]["status"], "| history:", [h["status"] for h in snap["history"]])
            for nxt in ("accepted", "preparing", "out_for_delivery", "delivered"):
                r = client.post(f"/orders/{oid}/status", json={"status": nxt})      # the kitchen / driver app
                pushed = ws.receive_json()                                         # ...and the customer sees it instantly
                print(f"  kitchen -> {nxt:<17} http {r.status_code}   customer screen got: {pushed['order']['status']}")
            try:
                ws.receive_json()
            except WebSocketDisconnect:
                print("  server closed the socket after the final state (no leaked connection)")

        say("5. illegal moves are refused by the state machine")
        r = client.post(f"/orders/{oid}/status", json={"status": "preparing"})
        print(r.status_code, r.json()["detail"])
        r = client.post(f"/orders/{oid}/status", json={"status": "teleported"})
        print(r.status_code, "(unknown status rejected by the Enum)")

        say("6. the audit trail comes for free")
        final = client.get(f"/orders/{oid}").json()
        print(" -> ".join(h["status"] for h in final["history"]))

        say("7. the single-page front end is served too")
        html = client.get("/").text
        print("GET / ->", len(html), "bytes of HTML, opens a WebSocket:", "new WebSocket" in html)


if __name__ == "__main__":
    main()
