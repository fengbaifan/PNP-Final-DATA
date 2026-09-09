#!/usr/bin/env python3
"""
plan_relation_candidates.py v2.3 — 候选关系召回
===========================================================
基于直接关系信号召回候选关系对，输出 relation-candidates.yml。

信号源:
  1. explicit relations (frontmatter)
  2. legacy related
  3. 正文 markdown 链接
  4. hierarchy primary_theme / topic_memberships
  5. claim-registry 支持关系
  6. sources / evidence_ref 共现
  7. title/name/aliases 共现
  8. 同一 structure node 仅作发现分组，不生成事实关系候选

共享年代与共享 tag 只作为弱统计信号，不进入活跃候选队列。
"""
import copy, hashlib, re, json, sys, yaml
from datetime import date
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
QUALITY = BASE / "04-knowledge" / "quality"
CLAIM_YML = QUALITY / "claim-registry.yml"
RELATION_YML = QUALITY / "relation-index.yml"
OUT = QUALITY / "relation-candidates.yml"
TODAY = date.today().isoformat()
if "-h" in sys.argv or "--help" in sys.argv:
    print("usage: plan_relation_candidates.py [--write] [--verbose]")
    print()
    print("Generate mechanical relation candidates from repository signals.")
    print("Default is read-only; --write explicitly refreshes relation-candidates.yml.")
    sys.exit(0)

DRY = "--write" not in sys.argv
VERBOSE = "--verbose" in sys.argv

def get_fm(text):
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""

def get_body(text):
    parts = text.split("---", 2)
    return parts[2] if len(parts) >= 3 else ""

def get_field(fm, field):
    m = re.search(rf"^{re.escape(field)}:\s*(.+)", fm, re.MULTILINE)
    return m.group(1).strip() if m else ""

def get_list(fm, field):
    vals = []
    in_k = False
    for line in fm.split("\n"):
        if re.match(rf"^{field}:", line.strip()):
            in_k = True
            continue
        if in_k:
            m = re.match(r"^\s*-\s+(.*)", line)
            if m:
                vals.append(m.group(1).strip())
            elif line.strip() and not line.strip().startswith("-"):
                break
    return vals

def _normalize_target(target):
    t = str(target or "").strip()
    for prefix in ["../"]:
        if t.startswith(prefix):
            parts = t[len(prefix):].split("/", 2)
            if len(parts) >= 2:
                t = "/".join(parts[-2:])
            else:
                t = parts[-1] if parts else t
    return t

# ── Build all-units registry ──
all_units = {}
unit_paths = []
for dname in ["persons","institutions","places","works","archives","terms","procedures","events"]:
    d = UNITS / dname
    if not d.exists():
        continue
    for f in sorted(d.glob("*.md")):
        rel = str(f.relative_to(UNITS)).replace("\\", "/")
        c = f.read_text(encoding="utf-8")
        fm = get_fm(c)
        body = get_body(c)
        title = get_field(fm, "title")
        name_en = get_field(fm, "name_en")
        tags = get_list(fm, "tags")
        related = get_list(fm, "related")
        try:
            frontmatter_data = yaml.safe_load(fm) or {}
        except yaml.YAMLError:
            frontmatter_data = {}
        weak_targets = []
        for item in frontmatter_data.get("weak_associations", []) or []:
            target = item.get("target") if isinstance(item, dict) else item
            target_clean = _normalize_target(target)
            if target_clean:
                weak_targets.append(target_clean)
        sources_field = []
        in_src = False
        src_entry = {}
        for line in fm.split("\n"):
            if re.match(r"^sources:", line): in_src = True; continue
            if in_src:
                m = re.match(r"^\s*-\s+citation:\s*(.+)", line)
                if m:
                    if src_entry:
                        sources_field.append(src_entry)
                    src_entry = {"citation": m.group(1).strip()}
                    continue
                m_doc = re.match(r"^\s*doc_id:\s*(.+)", line)
                if m_doc: src_entry["doc_id"] = m_doc.group(1).strip(); continue
                m_ch = re.match(r"^\s*chapter_id:\s*(.+)", line)
                if m_ch: src_entry["chapter_id"] = m_ch.group(1).strip(); continue
                if line.strip() == "" or (re.match(r"^\w+:", line.strip()) and not line.strip().startswith(("-","  "))):
                    if src_entry:
                        sources_field.append(src_entry)
                    in_src = False

        all_units[rel] = {
            "path": rel,
            "type": dname.rstrip("s"),
            "title": title,
            "name_en": name_en,
            "tags": tags,
            "related": related,
            "weak_targets": weak_targets,
            "sources": sources_field,
            "body_text": (title + " " + name_en + " " + body[:3000]).lower(),
        }
        unit_paths.append(rel)

# ── Source doc_id index ──
doc_id_map = defaultdict(list)
for rel, u in all_units.items():
    for s in u.get("sources", []):
        did = s.get("doc_id", "")
        if did:
            doc_id_map[did].append(rel)

# ── Tag/keyword co-occurrence ──
tag_index = defaultdict(list)
for rel, u in all_units.items():
    for tag in u.get("tags", []):
        tag_index[tag.lower()].append(rel)

# ── Name overlap ──
name_index = {}
for rel, u in all_units.items():
    ne = u.get("name_en", "").lower()
    if ne:
        name_index.setdefault(ne, []).append(rel)

def _materialized_structure_target(value):
    """Resolve only explicit, existing structure paths."""
    normalized = value.replace("\\", "/").strip().strip('"').strip("'")
    if normalized.startswith("structure/"):
        normalized = normalized.split("structure/", 1)[1]
    allowed = ("topics/", "themes/", "domains/", "dimensions/")
    if not normalized.startswith(allowed) or not normalized.endswith(".md"):
        return ""
    return normalized if (BASE / "04-knowledge" / "structure" / normalized).is_file() else ""


def _materialized_theme_target(theme_code):
    """Resolve a Theme code through frontmatter; never derive a filename from the code."""
    code = str(theme_code or "").strip().strip('"').strip("'")
    if not code:
        return ""
    themes = BASE / "04-knowledge" / "structure" / "themes"
    for path in sorted(themes.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        try:
            data = yaml.safe_load(get_fm(path.read_text(encoding="utf-8"))) or {}
        except yaml.YAMLError:
            continue
        if str(data.get("theme_code") or "").strip() == code:
            return f"themes/{path.name}"
    return ""

candidates = []
seen_pairs = set()

formal_pairs = set()
if RELATION_YML.exists():
    formal_relations = yaml.safe_load(RELATION_YML.read_text(encoding="utf-8")) or []
    for relation in formal_relations:
        if not isinstance(relation, dict):
            continue
        source = relation.get("source")
        target = relation.get("target")
        if source and target:
            formal_pairs.add(tuple(sorted((source, target))))

weak_pairs = {
    tuple(sorted((source, target)))
    for source, unit in all_units.items()
    for target in unit.get("weak_targets", [])
    if target in all_units and target != source
}

def add_candidate(source, target, signal, note="", confidence="medium"):
    pair = tuple(sorted((source, target)))
    if pair in formal_pairs or pair in weak_pairs or pair in seen_pairs or source == target:
        return
    seen_pairs.add(pair)
    candidate_id = "relation-" + hashlib.sha256(
        f"{pair[0]}|{pair[1]}".encode("utf-8")
    ).hexdigest()[:16]
    candidates.append({
        "candidate_id": candidate_id,
        "origin_type": "relation_graph",
        "origin_ref": f"scripts/plan_relation_candidates.py#{signal}",
        "candidate_type": "relation",
        "target_ref": target,
        "payload": {
            "source": source,
            "source_type": all_units[source]["type"] if source in all_units else "unknown",
            "target": target,
            "target_type": all_units[target]["type"] if target in all_units else "unknown",
            "signal": signal,
            "note": note,
            "signal_confidence": confidence,
        },
        "evidence_refs": [],
        "state": "needs_evidence",
        "decision": {
            "status": "pending",
            "reason": None,
            "decided_by": None,
            "decided_at": None,
        },
        "created_at": TODAY,
        "updated_at": TODAY,
    })


def semantic_candidate(candidate):
    """Return the candidate payload without generated snapshot timestamps."""
    return {
        key: value
        for key, value in candidate.items()
        if key not in {"created_at", "updated_at"}
    }


def load_previous_candidates(output=OUT):
    if not output.exists():
        return {}
    try:
        previous = yaml.safe_load(output.read_text(encoding="utf-8")) or []
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(previous, list):
        return {}
    return {
        str(candidate.get("candidate_id")): candidate
        for candidate in previous
        if isinstance(candidate, dict) and candidate.get("candidate_id")
    }


def stabilize_candidate_timestamps(current, output=OUT, today=TODAY):
    """Preserve timestamps unless a candidate is new or semantically changed."""
    previous = load_previous_candidates(output)
    stabilized = []
    for raw_candidate in current:
        candidate = copy.deepcopy(raw_candidate)
        prior = previous.get(str(candidate.get("candidate_id")))
        if prior:
            created_at = str(prior.get("created_at") or today)
            candidate["created_at"] = created_at
            if semantic_candidate(prior) == semantic_candidate(candidate):
                candidate["updated_at"] = str(prior.get("updated_at") or created_at)
            else:
                candidate["updated_at"] = today
        else:
            candidate["created_at"] = today
            candidate["updated_at"] = today
        stabilized.append(candidate)
    return stabilized


def render_relation_candidates(candidate_rows, generated):
    header = (
        "# Relation Candidates v2.1\n"
        f"# generated: {generated}\n"
        f"# total: {len(candidate_rows)}\n"
        "# excludes_formal_pairs: true\n\n"
    )
    return header + yaml.dump(
        candidate_rows,
        allow_unicode=True,
        sort_keys=False,
        width=300,
    )


def stable_generated_date(candidate_text, output=OUT, today=TODAY):
    """Preserve the prior generated date when all candidate bytes are stable."""
    if not output.exists():
        return today
    try:
        existing = output.read_text(encoding="utf-8")
    except OSError:
        return today
    match = re.search(r"^# generated: (\d{4}-\d{2}-\d{2})$", existing, re.MULTILINE)
    if not match:
        return today
    normalized_existing = re.sub(
        r"^# generated: \d{4}-\d{2}-\d{2}$",
        "# generated: <stable>",
        existing,
        count=1,
        flags=re.MULTILINE,
    )
    normalized_candidate = re.sub(
        r"^# generated: \d{4}-\d{2}-\d{2}$",
        "# generated: <stable>",
        candidate_text,
        count=1,
        flags=re.MULTILINE,
    )
    return match.group(1) if normalized_existing == normalized_candidate else today

# ── Signal 1: explicit relations field ──
for rel, u in all_units.items():
    fm = get_fm(Path(UNITS / rel).read_text(encoding="utf-8"))
    in_rel = False
    current_target = ""
    for line in fm.split("\n"):
        if re.match(r"^relations:", line.strip()): in_rel = True; continue
        if in_rel:
            m = re.match(r"^\s*target:\s*(.+)", line.strip())
            if m:
                current_target = m.group(1).strip()
                target_clean = _normalize_target(current_target)
                if target_clean in all_units:
                    add_candidate(rel, target_clean, "s1_explicit_relations", f"explicit relations field", "high")
            if line.strip() == "" or (not line.strip().startswith(("-","  ")) and re.match(r"^\w+:", line.strip())):
                in_rel = False

# ── Signal 2: legacy related ──
for rel, u in all_units.items():
    for target in u.get("related", []):
        target_clean = _normalize_target(target)
        if target_clean in all_units and target_clean != rel:
            add_candidate(rel, target_clean, "s2_legacy_related", f"legacy related: {target}", "low")

# ── Signal 3: body markdown links ──
for rel in unit_paths:
    body = get_body(Path(UNITS / rel).read_text(encoding="utf-8"))
    for m in re.finditer(r"\[([^\]]*)\]\(\.\./([^)]+)\)", body):
        link_text = m.group(1)
        link_path = m.group(2).replace("\\", "/")
        parts = link_path.split("/", 2)
        if len(parts) >= 3:
            link_norm = "/".join(parts[-2:])
            if link_norm in all_units:
                add_candidate(rel, link_norm, "s3_body_link", f"body link: {link_text}", "medium")

# ── Signal 4: five-level hierarchy memberships ──
for rel, u in all_units.items():
    fm = get_fm(Path(UNITS / rel).read_text(encoding="utf-8"))
    try:
        data = yaml.safe_load(fm) or {}
    except yaml.YAMLError:
        data = {}
    theme_target = _materialized_theme_target(data.get("primary_theme"))
    if theme_target:
        add_candidate(rel, f"structure/{theme_target}", "s4_hierarchy", "hierarchy: primary_theme", "high")
    for membership in data.get("topic_memberships", []) or []:
        if not isinstance(membership, dict):
            continue
        topic_target = _materialized_structure_target(str(membership.get("topic") or ""))
        if topic_target and topic_target.startswith("topics/") and str(membership.get("role") or "").strip():
            add_candidate(rel, f"structure/{topic_target}", "s4_hierarchy", "hierarchy: topic_memberships", "high")

# ── Signal 5: claim-registry ──
if CLAIM_YML.exists():
    claims = yaml.safe_load(CLAIM_YML.read_text(encoding="utf-8")) or {}
    if isinstance(claims, dict):
        for claim_id, claim_data in claims.items():
            if isinstance(claim_data, dict):
                for ku_path in claim_data.get("supported_by", []):
                    ku = ku_path.replace("\\", "/")
                    if "units/" in ku: ku = ku.split("units/", 1)[1]
                    for rel in unit_paths:
                        if ku in rel or rel in ku:
                            add_candidate(rel, ku if ku in all_units else rel,
                                        "s5_claim_registry", f"supports claim: {claim_id}", "high")

# ── Signal 6: source doc_id co-occurrence ──
for doc_id, paths in doc_id_map.items():
    for i in range(len(paths)):
        for j in range(i+1, len(paths)):
            add_candidate(paths[i], paths[j], "s6_source_cooccurrence",
                         f"share source: {doc_id}", "medium")

# ── Signal 7: name_en overlap ──
for name, paths in name_index.items():
    if len(name) < 5 or len(paths) <= 1:
        continue
    for i in range(len(paths)):
        for j in range(i+1, len(paths)):
            add_candidate(paths[i], paths[j], "s7_name_overlap",
                         f"shared name_en: {name}", "medium")

# 同一 Topic、Theme 或 Dimension 只证明共同研究语境。Batch 319 的分层校准中，
# 20/20 个 s8 样本均缺少成对直接证据，且已验证关系通常通过具体 work 中介。
# 因此 structure 共属不再进入活跃事实关系候选；仍可由 hierarchy/discovery 工具分组召回。

# ── Output ──
candidates = stabilize_candidate_timestamps(candidates)
signals = defaultdict(int)
for c in candidates:
    signals[c["payload"]["signal"]] += 1

print(f"plan_relation_candidates.py v2.3")
print(f"  已排除正式 relation pairs: {len(formal_pairs)}")
print(f"  已排除 weak_associations pairs: {len(weak_pairs)}")
print(f"  候选关系总数: {len(candidates)}")
for sig, cnt in sorted(signals.items()):
    print(f"  {sig}: {cnt}")

if not DRY:
    candidate_text = render_relation_candidates(candidates, TODAY)
    yaml_text = render_relation_candidates(
        candidates,
        stable_generated_date(candidate_text),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml_text, encoding="utf-8")
    print(f"  written: {OUT}")
else:
    print(f"  [DRY RUN]")
