# Bug Report: Anti Skill Infinite Loop

**Date**: 2026-08-21
**Reporter**: Codex Agent
**Severity**: Medium (resource waste, no data loss)
**Component**: Anti skill integration + agent polling pattern

---

## Summary

The agent entered an infinite loop attempting to poll for Anti skill consultation results, executing 100+ nearly identical shell commands with incrementing sleep timers without recognizing the polling pattern was failing.

---

## Timeline

1. **01:39:57** - Launched `anti.py consult --model sonnet` with complex Norwegian prompt
2. **01:39:57** - Anti started: `calling claude-sonnet-4-6 (1856 prompt chars)`
3. **01:40:57** - First poll attempt: `sleep 60 && cat ... 20260821T*.json` → Empty output
4. **01:42:27** - Second poll: `sleep 90` → Still empty
5. **01:43:57** - Third poll: `sleep 120` → Still empty
6. **... pattern continues ...**
7. **02:46:57** - 100th+ poll: `sleep 4380` → Still empty
8. **02:47:57** - User intervention: "it looks like you are stuck"

---

## Root Cause Analysis

### Primary Cause: Polling Without Exit Condition

The agent implemented a naive polling pattern:

```
while True:
    run(sleep N && cat output.json)
    if output exists: break
    N += 30
```

But the exit condition never triggered because:

1. **Wrong file path pattern**: The glob `20260821T*.json` may not have matched the actual output file
2. **Anti output location uncertainty**: Anti saves to `~/.codex/anti-runs/` but the exact filename/timestamp format wasn't verified
3. **No process status check**: Never verified if the anti consult process was still running vs. completed
4. **No timeout/max-iterations**: No upper bound on poll attempts

### Secondary Cause: Sleep Duration Escalation

Each iteration increased sleep by 30 seconds:
- Started at 60s
- Ended at 4380s (73 minutes)
- Total wall time wasted: ~75 minutes of polling

### Tertiary Cause: No Fallback Strategy

When polling failed, the agent should have:
1. Checked if the anti process was still running (`ps aux | grep anti.py`)
2. Looked for output in alternative locations
3. Re-run the consult with `--save-output` flag explicitly
4. Abandoned polling and reported the issue to the user

---

## Technical Details

### Command Pattern That Looped

```bash
sleep N && ls -la /Users/reidar/.codex/anti-runs/20260821T*.json 2>/dev/null | tail -3
```

### What Anti Actually Does

From the anti.py skill documentation:
- Consult results are saved to `~/.codex/anti-runs/` as JSON files
- The `--save-output summary` flag was used in the command
- Output format includes `output` field in the JSON

### Why Polling Failed

1. **File might not exist yet**: Anti consults can take 30-120 seconds
2. **Glob mismatch**: The timestamp format in filename may differ
3. **JSON parse failure**: If file exists but is malformed, `python3 -c` would fail silently
4. **Process completion race**: Anti might have completed but file wasn't flushed

---

## What Should Have Happened

### Correct Polling Pattern

```bash
# 1. Launch anti consult
anti.py consult --model sonnet --prompt "..." --save-output summary

# 2. Wait for completion (not polling)
# Use session_id from exec_command to wait

# 3. Check result
cat ~/.codex/anti-runs/LATEST.json | jq .output
```

### Better: Use exec_command's Built-in Waiting

The `exec_command` tool with `yield_time_ms` parameter should have been used to wait for completion, not manual sleep+poll.

---

## Impact

- **Resource waste**: 100+ shell commands executed
- **Time waste**: ~75 minutes of agent runtime
- **User experience**: Poor - user had to intervene
- **No data loss**: No files were corrupted

---

## Recommendations

1. **Add timeout to polling loops**: Maximum 5-10 iterations before fallback
2. **Verify file existence before glob**: Use `find` instead of shell glob
3. **Check process status**: Use `ps` to verify anti is still running
4. **Use exec_command yield**: Leverage built-in waiting mechanism
5. **Implement exponential backoff**: Start at 5s, max at 60s, total timeout 5min
6. **Add user notification**: After 3 failed polls, inform user and ask for guidance

---

## Reproduction Steps

1. Run anti consult with complex prompt
2. Attempt to poll for results using sleep+cat pattern
3. Do not implement exit condition or timeout
4. Observe infinite loop

---

## Fix Status

**Not yet fixed** - This is a behavioral pattern issue in the agent, not a code bug. The agent should recognize polling failures and adapt strategy.
