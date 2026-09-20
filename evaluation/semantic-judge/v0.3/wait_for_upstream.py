#!/usr/bin/env python3
"""Poll the opencodex proxy until upstream chat completions recover."""
import json, time, urllib.request

URL = "http://127.0.0.1:10100/v1/chat/completions"
PAYLOAD = json.dumps({
    "model": "gpt-5.5",
    "messages": [{"role": "user", "content": "ping"}],
    "max_tokens": 5,
}).encode()


def check():
    req = urllib.request.Request(URL, data=PAYLOAD, headers={
        "Authorization": "Bearer test", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.load(resp)
            return resp.status == 200 and "choices" in body, f"HTTP {resp.status}"
    except Exception as exc:
        return False, str(exc)[:120]


def main():
    while True:
        ok, info = check()
        print(f"[{time.strftime('%H:%M:%S')}] "
              f"{'HEALTHY' if ok else 'waiting'} ({info})", flush=True)
        if ok:
            print("UPSTREAM RECOVERED", flush=True)
            return
        time.sleep(120)


if __name__ == "__main__":
    main()
