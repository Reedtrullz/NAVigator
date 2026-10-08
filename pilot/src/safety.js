/* Unchanged Pilot 3 signal matching; frozen vocabulary is not clinical approval. */
function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function norm(s) {
  return String(s == null ? "" : s).toLowerCase()
    .replace(/\u00e5/g, "aa")
    .replace(/\u00e6/g, "ae")
    .replace(/\u00f8/g, "o");
}

function matchSignals(text) {
  const t = norm(text);
  const neg = DATA.triage.negation_guard;
  const negPatterns = (neg.negation_patterns || []).map(p => norm(p));
  const idioms = (neg.non_negated_affirmative_idioms || []).map(p => norm(p));
  const hits = [];
  const entries = (DATA.triage.class_precedence || [])
    .map(cls => [cls, DATA.triage.class_signals[cls] || []])
    .flatMap(([cls, sigs]) => sigs.map(s => [cls, s]));
  for (const [cls, sigRaw] of entries) {
    const sig = norm(sigRaw).replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\s+/g, "\\s+");
    const re = new RegExp("(?<![a-z0-9])" + sig + "(?![a-z0-9])", "g");
    let m;
    while ((m = re.exec(t)) !== null) {
      const start = m.index;
      const phrase = norm(sigRaw);
      let guarded = false;
      const isAcute = (DATA.triage.class_collapse[cls] || {}).priority === "ACUTE_RISK_NOW";
      if (isAcute && !idioms.includes(phrase)) {
        for (const p of negPatterns) {
          const parts = p.split(/\s+/);
          if (parts.length < 2) continue;
          const obj = parts.slice(1).join(" ");
          const reNeg = new RegExp("(?<![a-z0-9])" + parts[0] + "\\s+" + obj.replace(/\s+/g, "\\s+") + "(?![a-z0-9])", "g");
          let nm;
          while ((nm = reNeg.exec(t)) !== null) {
            const objStart = nm.index + nm[0].indexOf(obj);
            const objEnd = objStart + obj.length;
            if (objStart < start + m[0].length && objEnd > start) { guarded = true; break; }
          }
          if (guarded) break;
        }
      }
      if (!guarded) hits.push({ cls, signal: sigRaw, index: start });
    }
  }
  hits.sort((a, b) => a.index - b.index);
  return hits;
}

function collapse(hits) {
  const collapsed = [...new Set(hits.map(h => DATA.triage.class_collapse[h.cls].priority))];
  const order = ["ACUTE_RISK_NOW", "URGENT_NOT_ACUTE", "NOT_ACUTE"];
  collapsed.sort((a, b) => order.indexOf(a) - order.indexOf(b));
  return collapsed[0] || null;
}
