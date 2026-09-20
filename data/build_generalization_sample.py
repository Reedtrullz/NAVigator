import json
selection = [
    {"kommune": "Rælingen", "kommunenummer": "3224", "fylke": "Akershus", "klasse": 1},
    {"kommune": "Drammen", "kommunenummer": "3301", "fylke": "Buskerud", "klasse": 2},
    {"kommune": "Fredrikstad", "kommunenummer": "3107", "fylke": "Østfold", "klasse": 2},
    {"kommune": "Askøy", "kommunenummer": "4627", "fylke": "Vestland", "klasse": 3},
    {"kommune": "Bamble", "kommunenummer": "4012", "fylke": "Telemark", "klasse": 3},
    {"kommune": "Birkenes", "kommunenummer": "4216", "fylke": "Agder", "klasse": 4},
    {"kommune": "Bjerkreim", "kommunenummer": "1114", "fylke": "Rogaland", "klasse": 4},
    {"kommune": "Alstahaug", "kommunenummer": "1820", "fylke": "Nordland", "klasse": 5},
    {"kommune": "Etnedal", "kommunenummer": "3450", "fylke": "Innlandet", "klasse": 5},
    {"kommune": "Aure", "kommunenummer": "1576", "fylke": "Møre og Romsdal", "klasse": 6},
    {"kommune": "Balsfjord", "kommunenummer": "5532", "fylke": "Troms", "klasse": 6},
]
freshness = {m["kommune"]: ("INCIDENTAL_MENTION_ONLY" if m["kommune"] == "Drammen" else "UNSEEN") for m in selection}
out = {
    "task_id": "NAV-EXPLORE-LOCAL-DISCOVERY-GENERALIZATION-V1",
    "created_at": "2026-09-09",
    "frozen_before_research": True,
    "sample_type": "fresh_municipal_generalization_holdout",
    "centrality": {
        "source": "SSB KLASS 128/131 correspondence 131->128",
        "valid_from": "2024-01-01",
        "note": "Same source as Municipal Sample V1. 2026 correspondence not yet published at retrieval; 2025 correspondence identical to 2024 (verified via KLASS API).",
    },
    "deviation": {
        "spec": "12 kommuner, 2 per sentralitetsklasse 1-6",
        "actual": "11 kommuner: 1 x klasse 1, 2 x klasse 2-6",
        "code": "SAMPLE_DEVIATION_KLASSE1_POOL_EXHAUSTED",
        "reason": "Nationally only 5 municipalities are sentralitetsklasse 1 (Oslo, Baerum, Lillestrom, Loerenskog, Raelingen per KLASS 2024/2025). Four were used in Municipal Sample V1, leaving only Raelingen as a fresh klasse-1 candidate. Exhaustive pool, not a selection choice.",
    },
    "exclusion_basis": {
        "sample_v1_24": ["Alta","Arendal","Askvoll","Bergen","Bodo","Bykle","Baerum","Farsund","Gjovik","Hamar","Hasvik","Haugesund","Lillestrom","Loerenskog","Osen","Oslo","Sauda","Stavanger","Steinkjer","Sor-Varanger","Trondheim","Tynset","Ulstein","Orland"],
        "deep_dive_12": ["Alta","Askvoll","Bykle","Farsund","Hasvik","Osen","Sauda","Steinkjer","Sor-Varanger","Tynset","Ulstein","Orland"],
        "previously_researched_replacements": [
            {"out": "Alvdal", "reason": "PREVIOUSLY_RESEARCHED: FARTT (Folldal/Alvdal/Rendalen/Tynset/Tolga) interkommunal kommunepsykolog documented in data/18-23-local-routing-gap-v1.json (Tynset entry)", "in": "Etnedal", "replacement_freshness": "UNSEEN"},
        ],
    },
    "freshness_audit": {
        "method": "Project-wide rg search per municipality name and kommunenummer, excluding .git/.venv/evaluation machine artifacts and sealed blobs; manual context inspection of all name hits",
        "results": freshness,
        "notes": [
            "Drammen: INCIDENTAL_MENTION_ONLY (RPH contact line in 16-livssituasjoner/05-voksnes-psykiske-helse.md; not municipal service research). Allowed per spec.",
            "Case-insensitive substring hits in .venv (e.g. 'Laurent') and numeric hits in hashes/sealed blobs are machine noise, not research.",
        ],
    },
    "municipality_count": 11,
    "centralitetsklasse_distribution": {"1": 1, "2": 2, "3": 2, "4": 2, "5": 2, "6": 2},
    "municipalities": [
        {**m, "freshness": freshness[m["kommune"]], "scenarios": {
            "C": {"age": 19, "situation": "moderate psykiske plager, ikke akutt"},
            "D": {"age": 22, "situation": "onsker rask/lavterskel psykisk helsehjelp, ikke akutt"},
        }} for m in selection
    ],
}
json.dump(out, open("data/local-discovery-generalization-sample-v1.json", "w"), ensure_ascii=False, indent=1)
print("sample frozen:", out["municipality_count"], "municipalities")
