#!/usr/bin/env python3
"""One-shot synthetic diagnostic (no fixture data) for schema-failure debugging."""
import json
import urllib.request

import judge_core_v1_4 as J


def main():
    with open(J.CODEX_AUTH_JSON) as f:
        key = json.load(f)["tokens"]["access_token"]
    sysmsg = J.SYSTEM_PROMPT + "\n\n" + J.DIMENSION_INSTRUCTIONS["route_correctness"]
    body = json.dumps({
        "model": J.MODEL, "temperature": 0, "max_tokens": J.MAX_TOKENS,
        "messages": [
            {"role": "system", "content": sysmsg},
            {"role": "user", "content": J.build_user_prompt(
                "route_correctness",
                "SYNTEETISK DIAGNOSTIKK (ikke et fixture)",
                "Kriteriet krever at svaret tilbyr fastlegen som konkret inngang.",
                "Start hos fastlegen.")},
        ],
    }).encode()
    req = urllib.request.Request(
        J.PROXY_URL, data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + key}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    ch = data["choices"][0]
    print("finish:", ch.get("finish_reason"))
    print("usage:", json.dumps(data.get("usage")))
    print("RAW CONTENT (first 1500):")
    print(repr(ch["message"]["content"][:1500]))


if __name__ == "__main__":
    main()
