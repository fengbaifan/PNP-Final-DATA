"""Select explicitly admitted project objects without altering historical files."""
from pathlib import Path
import yaml


def load_catalog(base: Path) -> dict[str, list[str]] | None:
    path = base / "04-knowledge" / "accepted.yml"
    if not path.exists():
        return None  # Historical/portable repositories without an admission catalog.
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or set(data) != {"units", "claims", "structure"}:
        raise ValueError("accepted.yml must declare units, claims and structure lists")
    for kind, values in data.items():
        if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values) or len(values) != len(set(values)):
            raise ValueError(f"invalid accepted {kind} list")
        if kind == "claims":
            continue
        for value in values:
            target = (base / value).resolve()
            allowed = (base / "04-knowledge" / kind).resolve()
            if not target.is_relative_to(allowed) or not target.is_file() or target.suffix != ".md":
                raise ValueError(f"invalid accepted {kind} path: {value}")
    return data


def select_paths(base: Path, kind: str, paths: list[Path]) -> list[Path]:
    catalog = load_catalog(base)
    if catalog is None:
        return paths
    accepted = {(base / value).resolve() for value in catalog[kind]}
    return [path for path in paths if path.resolve() in accepted]


def select_claims(base: Path, claims: list[dict]) -> list[dict]:
    catalog = load_catalog(base)
    if catalog is None:
        return claims
    known = {item.get("claim_id") for item in claims}
    if set(catalog["claims"]) - known:
        raise ValueError("accepted.yml references unknown claim IDs")
    return [item for item in claims if item.get("claim_id") in catalog["claims"]]
