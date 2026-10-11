import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, TypedDict


class RetrievalArgs(TypedDict):
    index_path: str
    repo_root: str
    rules_path: str
    access_profile: dict[str, Any]


class SyntheticCorpus:
    def __init__(self, test):
        parent = Path(__file__).resolve().parents[3] / "outputs" / "runtime-synthetic"
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        test.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = []
        self.profile: dict[str, Any] = {"version": "knowledge-access/v1", "documents": {}}
        self.index = self.root / "index.json"
        self.rules = self.root / "rules.json"
        self.rules.write_text('{"rules": []}', encoding="utf-8")
        self.profile["rules"] = {"path": "rules.json", "permission": "GENERAL_APPROVED",
                                 "sha256": hashlib.sha256(self.rules.read_bytes()).hexdigest()}
        self.save_index()

    def add_doc(self, doc_id="public", text="bolig contact information", *,
                path=None, doc_class="DECISION_SUPPORT", permission="GENERAL_APPROVED",
                domain="housing", freshness="CURRENT", **metadata):
        relative = path or doc_id + ".md"
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode()).hexdigest()
        entry = {"id": doc_id, "path": relative, "sha256": digest, "class": doc_class,
                 "domains": [domain], "freshness_class": freshness, **metadata}
        self.docs.append(entry)
        self.profile["documents"][doc_id] = {"path": relative, "permission": permission,
                                             "sha256": digest, "class": doc_class,
                                             "domains": list(entry["domains"]), "freshness_class": freshness,
                                             "verified_date": entry.get("verified_date")}
        self.save_index()
        return entry

    def save_index(self):
        self.index.write_text(json.dumps({"docs": self.docs}), encoding="utf-8")

    def retrieval_args(self) -> RetrievalArgs:
        return {"index_path": str(self.index), "repo_root": str(self.root),
                "rules_path": str(self.rules), "access_profile": self.profile}
