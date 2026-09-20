#!/bin/bash
# Konsistenssjekk av kunna feilmnstre i juridisk QA (august 2026).
# Skriver "OK" hvis ingen kjente feilmnstre finnes, ellers lister treff.

cd "$(dirname "$0")/.."

PATTERNS=(
  "permisjon . 2-12"
  "trussamfunn . 2-13"
  "meklingsime"
  "(^|[^a-z])pasninger([^a-z]|$)"
  "HOTL . 3-1 tredje ledd"
  "HPL . 33 fjerde ledd"
  "kun fastlege, psykolog i kommunen/PP-tjenesten"
)

EXIT=0
for P in "${PATTERNS[@]}"; do
  # qa-log.md og QA_REPORT.md dokumenterer tidligere feil og ma sitere de gamle strengene.
  MATCHES=$(grep -rn --include='*.md' --exclude='qa-log.md' --exclude='QA_REPORT.md' -E "$P" . 2>/dev/null)
  if [ -n "$MATCHES" ]; then
    echo "FUNNET: $P"
    echo "$MATCHES"
    EXIT=1
  fi
done

if [ "$EXIT" -eq 0 ]; then
  echo "OK: ingen kjente feilmnstre funnet."
fi
exit $EXIT
