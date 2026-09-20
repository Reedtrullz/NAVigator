# Cost model (spec 32)

Full run, 389 claims, iteration B configuration:

| metric | value |
|--------|-------|
| deterministic-only decisions | 121 per 389 claims = 31.1 per 100 |
| semantic review calls | 268 total = 68.9 per 100 claims |
| repeat review calls (main run) | 0 |
| total model calls | 268 |
| wall time | 956 s (about 2.5 s per call) |
| approximate tokens | about 1.0-1.5k per call, about 320-400k total |

Optional development-only stability battery (30 hardest claims x 3
runs) adds 90 calls. The main pipeline itself makes exactly one
reviewer call per gated claim; repeats are never used to force a
verdict (spec 29 disagreement policy routes wobble to
REVIEW_REQUIRED instead).

Model: openai/gpt-5.6-luna via local OpenCodex proxy, temperature 0,
max_tokens 300. Token counts are estimates from packet + prompt size
(about 0.9-1.4k in, about 60-100 out); exact usage was not recorded
by the proxy.
