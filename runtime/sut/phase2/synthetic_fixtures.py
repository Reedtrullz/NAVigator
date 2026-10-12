import hashlib
import json
from pathlib import Path
import tempfile
from typing import TypedDict
from unittest import TestCase
from .contracts import AccessProfile


class RetrievalArgs(TypedDict):
    index_path: str
    repo_root: str
    rules_path: str
    access_profile: AccessProfile


class SyntheticCorpus:
    def __init__(self, test: TestCase) -> None:
        parent = Path(__file__).resolve().parents[3] / "outputs" / "runtime-synthetic"
        parent.mkdir(parents=True, exist_ok=True)
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(dir=parent)
        test.addCleanup(self.temp.cleanup)
        self.root: Path = Path(self.temp.name)
        self.docs: list[dict[str, object]] = []
        self.profile: AccessProfile = {"version": "knowledge-access/v1", "documents": {}, "rules": {}}
        self.index: Path = self.root / "index.json"
        self.rules: Path = self.root / "rules.json"
        _ = self.rules.write_text('{"rules": []}', encoding="utf-8")
        self.profile["rules"] = {"path": "rules.json", "permission": "GENERAL_APPROVED",
                                 "sha256": hashlib.sha256(self.rules.read_bytes()).hexdigest()}
        self.save_index()

    def add_doc(self, doc_id: str = "public", text: str = "bolig contact information", *,
                path: str | None = None, doc_class: str = "DECISION_SUPPORT", permission: str = "GENERAL_APPROVED",
                domain: str = "housing", freshness: str = "CURRENT", **metadata: object) -> dict[str, object]:
        relative = path or doc_id + ".md"
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        _ = target.write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode()).hexdigest()
        entry: dict[str, object] = {"id": doc_id, "path": relative, "sha256": digest, "class": doc_class,
                 "domains": [domain], "freshness_class": freshness, **metadata}
        self.docs.append(entry)
        self.profile["documents"][doc_id] = {"path": relative, "permission": permission,
                                             "sha256": digest, "class": doc_class,
                                             "domains": [domain], "freshness_class": freshness,
                                             "verified_date": entry.get("verified_date")}
        self.save_index()
        return entry

    def save_index(self) -> None:
        _ = self.index.write_text(json.dumps({"docs": self.docs}), encoding="utf-8")

    def retrieval_args(self) -> RetrievalArgs:
        return {"index_path": str(self.index), "repo_root": str(self.root),
                "rules_path": str(self.rules), "access_profile": self.profile}
