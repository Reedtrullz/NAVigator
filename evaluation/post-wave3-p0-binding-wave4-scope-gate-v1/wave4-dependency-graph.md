# Wave-4 Dependency Graph

Task: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY
Basis: wave4-repair-candidates.json, route-failure-stage-classification.json (this task).

```
W4-RC-A  route-to-evidence semantic binding + structured route evaluation (coupled pair)
   |
   +--> W4-RC-B  access/condition evidence binding   (needs joined route objects from A)

W4-RC-C  independent uncertainty/failure-path repair (historical RC-04)
   - independent of A and B; deferrable without blocking the route track

W4-RC-D  route target selection continuation
   - largely folded into A (structured objects + B4 label-quality repair);
     reopen only for a quantified residual after A
```

## Order
1. W4-RC-A first: it repairs the earliest observable mechanism (serialized join shape + structured evaluation) and is the only candidate that moves route observation off the lexical dead end.
2. W4-RC-B second, strictly after A.
3. W4-RC-C independent, deferred.
4. W4-RC-D conditional, folded into A; not a separate Wave-4 workstream.
