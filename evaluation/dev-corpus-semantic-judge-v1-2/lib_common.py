import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))


def sha256_file(rel_path):
    with open(os.path.join(BASE, rel_path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_json(name, obj):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_text(name, text):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(text)

