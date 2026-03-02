import json
from pathlib import Path


def _default_rules_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "rules.json"


def load_rules(path: Path | None = None) -> dict:
    p = path or _default_rules_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def save_rules(rules: dict, path: Path | None = None) -> Path:
    p = path or _default_rules_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rules, ensure_ascii=False, indent=2))
    return p


def apply_user_rule(normalized_merchant: str, fallback_category: str, path: Path | None = None) -> str:
    rules = load_rules(path)
    if not normalized_merchant:
        return fallback_category
    return rules.get(normalized_merchant, fallback_category)


def upsert_rule(normalized_merchant: str, category: str, path: Path | None = None) -> Path:
    rules = load_rules(path)
    rules[normalized_merchant] = category
    return save_rules(rules, path)
