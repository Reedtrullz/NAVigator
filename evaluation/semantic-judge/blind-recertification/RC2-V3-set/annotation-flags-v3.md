# Structural Flags V3 - RC2 Blind Set Construction

Tag every case with ALL flags that apply. These feed hard CORE quotas; over-tagging is a violation, so tag only what the claim + provided sources actually exercise. Only these 11 strings are valid.

| Flag | Tag when the case requires ... |
|---|---|
| multi_span | combining information from 2+ distinct source spans (2+ source entries, or non-adjacent parts of one source) to reach the verdict |
| compound | the claim is a compound of 2+ assertions whose truth values can split (PARTIAL aggregation applies) |
| numeric | comparing, mapping, or verifying a number: amount, percentage, rate, threshold, age, count |
| temporal | a date, year, period, "fra/etter <dato>", or time-limit assertion matters to the verdict |
| actor | identifying WHO may act / who the rule applies to (parent, municipality, NAV, school, doctor...) is required |
| modality | obligation, right, prohibition, or permission ("skal", "kan", "ma", "har rett til") drives the verdict |
| cond_exc | a condition or exception ("hvis", "med mindre", "unntak", "som hovedregel") decides the verdict |
| safety | acute danger, self-harm/suicide risk, violence, or emergency procedure content |
| legal | verdict depends on statute/regulation citation or a legal-institutional procedure (klage, meldeplikt, lovparagraf) |
| locality | municipality-specific or geographically bounded provision (named place, local scheme) |
| age_legal | age thresholds interacting with legal rights/obligations (custody, consent, aldergrense for rettigheter) |

Notes: flags overlap freely. Age as a simple lookup in a rate table is numeric, not age_legal. "0-20 ar" service scope with no legal-rights interaction is numeric/temporal, not age_legal. When unsure between two flags, tag both ONLY if each genuinely applies; otherwise tag the one that decides the verdict.
