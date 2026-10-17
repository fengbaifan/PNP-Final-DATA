from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
PROCESS_REF = "S3-family-type-closure-2026-10-16"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def group_id(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


SAME = {
    "cand-1058": (
        "units/families/foscarini-family-venice",
        "F.csv#73 is the Venice Foscarini family heading's 'wealth of' subentry at p.261. Its parent heading candidate cand-1057 is the same S3 family group and is already registered at this KU.",
    ),
    "cand-1175": (
        "units/families/del-rosso-family-florence",
        "G.csv#82 is Luca Giordano's index heading with the subentry 'and del Rosso family'; this candidate resolves to the subentry's family, not to Luca Giordano. The same book identifies the Del Rosso as a Florentine family in ch. 8, pp.211 and 241, and that family KU is already registered.",
    ),
    "cand-1658": (
        "units/families/miani-family-camerata",
        "M.csv#198 locates the Venice Miani family at p.260 n.8. The cited note names 'the Miani of Camerata'; candidate cand-8501 and the registered family KU represent that same book-local family identity.",
    ),
    "cand-4452": (
        "units/families/sacchetti-family",
        "The ch. 2 source anchor identifies Marcello and Giulio Sacchetti and says they founded their family chapel. The candidate is the same Sacchetti family represented by the existing family KU; no additional members or genealogy are inferred.",
    ),
    "cand-6499": (
        "units/families/rospigliosi-family",
        "The ch. 6 source anchor refers to Clement IX's family fearing the expense of his burial scheme. Treccani's Rospigliosi family entry identifies Giulio, who became Clement IX, as the figure who secured the family's fortune. This resolves the unnamed family reference to the existing Rospigliosi family KU.",
    ),
    "cand-7157": (
        "units/families/house-of-savoy",
        "The ch. 7 source passage names Adelaide Enrichetta 'of Savoy' immediately before saying the Wittelsbachs thereby allied with the most astute ruling family. The referent is the House of Savoy, already represented by this family KU; no marriage or membership relation is created here.",
    ),
    "cand-7998": (
        "units/families/medici-family",
        "The ch. 8 source anchor identifies the shield over the Pitti-room door as bearing the Medici arms. This is the Medici family, not a specific Medici person, and matches the existing family KU.",
    ),
    "cand-8500": (
        "units/families/pisani-di-santo-stefano",
        "Ch. 9, p.255 places the Pisani family allegory at Villa Pisani in Stra and names its youngest son Almorò; p.264 identifies the Pisani household's academy and its son with the same name (OCR spelling varies). The official Villa Pisani history identifies the family that built the villa as the Pisani di Santo Stefano branch. Reuse that branch KU; the broader Pisani family KU is not used to erase the branch distinction.",
    ),
    "cand-10972": (
        "units/families/pamphili-family",
        "The postscript, p.401, says documents from the Doria-Pamphili archives illuminate the art patronage of Innocent X and his family. Treccani identifies Giovanni Battista Pamphili as Innocent X and the family as Pamphili; this maps the family reference to the existing Pamphili family KU.",
    ),
}


NEW = {
    "cand-7729": (
        "sg3-family-buonaccorsi-family",
        "Ch. 8, pp.223 and 225 identifies Raimondo as born into the old, extended Buonaccorsi family and names its members collectively. No same-type family KU exists. Create one source-backed family identity; exact genealogy and membership remain outside this decision.",
    ),
    "cand-8169": (
        "sg3-family-barbaro-family",
        "The ch. 9 plate caption identifies portraits of the Barbaro family on the façade of S. Maria del Giglio. No same-type Barbaro family KU exists. Create a source-bounded family identity; the caption does not identify individual sitters or a branch.",
    ),
    "cand-8301": (
        "sg3-family-bon-family-venice",
        "The ch. 9 source passage names the Bon family as the sellers from whom Aurelio Rezzonico obtained the Venetian palace. No same-type Bon family KU exists. Create a source-bounded family identity; the seller passage does not name individual members.",
    ),
    "cand-8356": (
        "sg3-family-sandi-family",
        "Ch. 9, pp.255–256 names the Sandi family and continues with its ennoblement, patronage, and palace commission. No same-type Sandi family KU exists. Create this source-supported family identity without inferring individual members.",
    ),
    "cand-9572": (
        "sg3-family-bourbon-dynasty",
        "Ch. 10, p.278 explicitly names the Bourbons as one of the dynastic portrait groups at Palazzo Loredan. No same-type Bourbon family KU exists. The dynasty-level identity is clear even though the portraits and sitters are not.",
    ),
    "cand-9573": (
        "sg3-family-hapsburg-dynasty",
        "Ch. 10, p.278 explicitly names the Hapsburgs as one of the dynastic portrait groups at Palazzo Loredan. No same-type Hapsburg family KU exists. The dynasty-level identity is clear even though the portraits and sitters are not.",
    ),
    "cand-9574": (
        "sg3-family-hohenzollern-dynasty",
        "Ch. 10, p.278 explicitly names the Hohenzollerns as one of the dynastic portrait groups at Palazzo Loredan. No same-type Hohenzollern family KU exists. The dynasty-level identity is clear even though the portraits and sitters are not.",
    ),
    "cand-9999": (
        "sg3-family-guardi-brothers",
        "Ch. 13, p.336 explicitly identifies Francesco Guardi and Gian Antonio Guardi as brothers. No same-type Guardi family KU exists. Create a family identity for this source-named sibling group; painting attribution remains separate.",
    ),
}


EXCLUDED = {
    "cand-1019": (
        "F.csv#34 has the place heading Ferrara with the subentry 'Bentivoglio and' at p.48; it does not name a Ferrara family. The source describes the Bentivoglio family as originating in Ferrara, and Ferrara is separately represented by place candidate cand-1017. Exclude this row from family scope; keep the place and Bentivoglio family candidates separate.",
    )
}


PENDING_ROUTES = {
    "cand-10472": "The source leaves Andrea Memmo's patrician lineage unnamed. Keep no KU; resume only if a source names the family, and do not infer it from Memmo's surname.",
    "cand-10709": "The source names a Pellegrini patrician family but supplies no branch or member that identifies its lineage. Keep no KU and keep it separate from painter Giovanni Antonio Pellegrini; resume with a family-specific record or named member.",
    "cand-11856": "The ch. 1 passage makes a general claim about families with treasury access and names Borghese and Barberini only as examples; it does not identify the unnamed family. Keep no KU and do not map it to either example.",
    "cand-12038": "The source says Antonio Ruffo was born into an unnamed aristocratic family. Keep no KU; require a source or authoritative genealogy naming that lineage, and do not infer it from the surname Ruffo.",
    "cand-4279": "The Perugia Baglioni chapel reference is not established as the same lineage as the Venice publisher family candidate cand-7575. Keep both candidates undecided and unregistered; require genealogy or named-member evidence before either merging or splitting them as family KUs.",
    "cand-4360": "The footnote names a Strozzi chapel but does not identify the family branch or members. Keep no KU; require a family-specific archival or scholarly record tied to that chapel before registration.",
    "cand-4361": "The footnote names a Rucellai chapel but does not identify the family branch or members. Keep no KU; require a family-specific archival or scholarly record tied to that chapel before registration.",
    "cand-7170": "The source refers collectively to the Carlone as painter-craftsman families but names no branch or member. Keep no KU; require branch/member evidence before matching or registering a specific family.",
    "cand-7368": "The source names Colonnas among Naples's feudal landowning families but gives no branch and does not link them to the existing Colonna family KU. Keep no KU; require branch-specific evidence and do not merge by surname.",
    "cand-7519": "The plural Falconieri are addressees in the title of a 1747 Del Rosso genealogy; the title does not establish whether they denote a family, which branch, or which persons. Keep no family KU pending a verified title/catalog record and recipient identity.",
    "cand-7575": "The Venice publisher family is not established as the same lineage as the Perugia Baglioni family candidate cand-4279. Keep both undecided and unregistered until family-specific evidence resolves their branch relationship.",
    "cand-7694": "The source says Cardinal Tommaso Ruffo and Don Antonio Ruffo came from the same southern family but names no lineage or branch. Keep no KU and do not infer a Ruffo family from the shared surname; require a source identifying the family and the two persons' connection.",
    "cand-7959": "Ch. 8, p.235 names the Marucelli brothers collectively and identifies Francesco, but does not identify the other brother(s) or a family branch. Keep no family KU pending a named sibling or family record; the Francesco person KU remains separate.",
    "cand-8780": "The 1729 source preserves the abbreviated form 'S. Ant.o e S. Nicolò Fratelli Co:Co:Manini' without resolving the brothers' personal identities or family branch. Keep no KU; resume after checking the full record/title and identifying the family referent.",
    "cand-8868": "The passage refers to a 'new dynasty' without naming it. Keep no KU and do not infer Hanover from the Whig context; require an explicit source identification or a contextual record that uniquely identifies the dynasty.",
    "cand-9980": "The source mentions a family pamphlet whose arms are to be intertwined with those of the Zorzi, but names no Zorzi member or branch. Keep no KU; require the pamphlet or a branch-specific record before matching or registration.",
    "cand-9989": "The source names a prominent Pisani family in Albrizzi's circle but no branch/member. Keep it separate from cand-8500 and the existing Pisani family KUs; require a named member or branch before mapping.",
    "cand-12255": "The source says Teodoro Correr descended from one of Venice's oldest aristocratic families but supplies no family name. Keep no KU until a source names the lineage; do not infer it from Correr's surname.",
}


def main():
    parser = argparse.ArgumentParser(
        description="Close the current S3 family-type review while preserving genuinely unresolved branches"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_fields, manifest_rows = read_csv(TABLES / "ku-manifest.csv")
    manifest = {row["ku_id"]: row for row in manifest_rows}
    alignment_fields, alignments = read_csv(ALIGNMENT)
    decisions = decision_rows(alignments)
    decision_by_id = {row["candidate_id"]: row for row in decisions}

    before = Counter(row["decision"] for row in decisions)
    assert before == Counter(
        {"same": 1698, "new": 4988, "undecided": 5614, "excluded": 97, "conflict": 7}
    ), before
    family_before = [
        row for row in decisions if candidate_by_id[row["candidate_id"]]["suggested_type"] == "family"
    ]
    assert Counter(row["decision"] for row in family_before) == Counter(
        {"new": 86, "same": 13, "undecided": 36}
    )
    assert set(SAME) | set(NEW) | set(EXCLUDED) | set(PENDING_ROUTES) == {
        row["candidate_id"]
        for row in family_before
        if row["decision"] == "undecided"
    }
    assert len(SAME) == 9 and len(NEW) == 8 and len(EXCLUDED) == 1

    for cid, (ku_id, _) in SAME.items():
        assert cid in decision_by_id and decision_by_id[cid]["decision"] == "undecided", cid
        assert candidate_by_id[cid]["suggested_type"] == "family", cid
        assert ku_id in manifest and manifest[ku_id]["type"] == "family", (cid, ku_id)
    for cid in NEW:
        assert cid in decision_by_id and decision_by_id[cid]["decision"] == "undecided", cid
        assert candidate_by_id[cid]["suggested_type"] == "family", cid
        assert not decision_by_id[cid]["ku_id"], cid
    for cid in EXCLUDED:
        assert cid in decision_by_id and decision_by_id[cid]["decision"] == "undecided", cid
    assert "cand-1017" in candidate_by_id
    assert candidate_by_id["cand-1017"]["suggested_type"] == "place"
    assert decision_by_id["cand-1017"]["decision"] == "new"

    # Verify the decisive source anchors and the existing family identity records.
    sources = {
        path.name: path.read_text(encoding="utf-8-sig")
        for path in (ROOT / "02-sources" / "02-Markdown").glob("*.md")
    }
    assert "family chapel" in sources["02_CHP-2_sec_ii.md"]
    assert "Medici arms" in sources["08_CHP-8_sec_ii.md"]
    assert "Miani of Camerata" in sources["09_CHP-9_intro_notes_p260_visual-transcription.md"]
    assert "Pisani organised a private academy" in sources["09_CHP-9_intro.md"]
    assert "Almor" in sources["09_CHP-9_intro.md"]
    assert "portraits of Barbaro family" in sources["09_CHP-9_intro_plates_visual-transcription.md"]
    assert "Venice from the Bon family" in sources["09_CHP-9_intro.md"]
    assert "The Sandi" in sources["09_CHP-9_intro.md"]
    assert "Bourbons and Hapsburgs, Farneses and Hohenzollerns" in sources["10_CHP-10_sec_ii.md"]
    assert "Guardi brothers" in sources["13_CHP-13_intro.md"]
    assert "Raimondo" in sources["08_CHP-8_sec_ii.md"]
    assert "Adelaide Enrichetta of Savoy" in sources["07_CHP-7_sec_iv.md"]
    assert "Clement IX" in sources["06_CHP-6_sec_v.md"]
    assert "Innocent X and his family" in sources["20_CHP-20Postscript.md"]

    index_root = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
    _, family_index = read_csv(index_root / "F.csv")
    _, giordano_index = read_csv(index_root / "G.csv")
    _, miani_index = read_csv(index_root / "M.csv")
    assert candidate_by_id["cand-1058"]["index_entry_id"] == "F.csv#73"
    assert candidate_by_id["cand-1058"]["sub_entry"] == "wealth of"
    assert candidate_by_id["cand-1057"]["canonical_name"] == "Foscarini family"
    assert candidate_by_id["cand-1175"]["index_entry_id"] == "G.csv#82"
    assert candidate_by_id["cand-1175"]["sub_entry"] == "and del Rosso family"
    assert candidate_by_id["cand-1658"]["index_entry_id"] == "M.csv#198"
    assert candidate_by_id["cand-1019"]["sub_entry"] == "Bentivoglio and"
    assert candidate_by_id["cand-1019"]["canonical_name"] == "Ferrara"
    assert any(row["Main Entry"] == "Foscarini family" for row in family_index)
    assert any(row["Main Entry"] == "Giordano, Luca" and row["Sub-entry"] == "and del Rosso family" for row in giordano_index)
    assert any(row["Main Entry"] == "Miani family" for row in miani_index)

    body = sources["14_CHP-14_intro.md"]
    del body
    assert (ROOT / "04-knowledge" / "units" / "families" / "pisani-di-santo-stefano.md").read_text(
        encoding="utf-8-sig"
    ).find("villapisani.beniculturali.it") >= 0

    planned = [dict(row) for row in alignments]
    planned_decisions = {row["candidate_id"]: row for row in decision_rows(planned)}

    for cid, (ku_id, rationale) in SAME.items():
        row = planned_decisions[cid]
        prior = row["resolution_note"]
        source_ref = candidate_by_id[cid].get("candidate_source_ref") or candidate_by_id[cid].get("index_entry_id") or cid
        row["decision"] = "same"
        row["ku_id"] = ku_id
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref={source_ref}; S3 family cross-chapter/type review 2026-10-16: same -> {ku_id}. "
            f"{rationale} Prior undecided rationale retained as history: {prior}"
        )

    for cid, (group, rationale) in NEW.items():
        row = planned_decisions[cid]
        prior = row["resolution_note"]
        source_ref = candidate_by_id[cid].get("candidate_source_ref") or cid
        row["decision"] = "new"
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={group}; source_ref={source_ref}; S3 family cross-chapter/type review 2026-10-16: "
            f"undecided -> new. {rationale} Prior undecided rationale retained as history: {prior}"
        )

    for cid, rationale in EXCLUDED.items():
        row = planned_decisions[cid]
        prior = row["resolution_note"]
        row["decision"] = "excluded"
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref=F.csv#34; S3 family type-boundary review 2026-10-16: undecided -> excluded. "
            f"{rationale} Prior rationale retained as history: {prior}"
        )

    for cid, route in PENDING_ROUTES.items():
        row = planned_decisions[cid]
        prior = row["resolution_note"]
        family_group = group_id(prior) or f"sg3-family-cand-{cid.removeprefix('cand-')}"
        source_ref = candidate_by_id[cid].get("candidate_source_ref") or candidate_by_id[cid].get("index_entry_id") or cid
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={family_group}; source_ref={source_ref}; S3 family review 2026-10-16: undecided retained. "
            f"{route} Prior note retained as history: {prior}"
        )

    external_specs = [
        (
            "cand-6499",
            "units/families/rospigliosi-family",
            "Treccani DBI",
            "https://www.treccani.it/enciclopedia/rospigliosi/",
            "Treccani's Rospigliosi entry describes the family and identifies Giulio, later Pope Clement IX, as securing its fortune.",
        ),
        (
            "cand-10972",
            "units/families/pamphili-family",
            "Treccani DBI",
            "https://www.treccani.it/enciclopedia/innocenzo-x_%28Enciclopedia-dei-Papi%29/",
            "Treccani identifies Innocent X as Giovanni Battista Pamphili and describes the Pamphili family.",
        ),
    ]
    existing_external_keys = {
        (row["candidate_id"], row["external_source"]) for row in planned if row.get("external_source")
    }
    next_alignment_number = max(int(row["alignment_id"].split("-")[1]) for row in planned)
    for cid, ku_id, source, external_id, rationale in external_specs:
        assert (cid, source) not in existing_external_keys, (cid, source)
        next_alignment_number += 1
        planned.append(
            {
                "alignment_id": f"aln-{next_alignment_number:04d}",
                "candidate_id": cid,
                "ku_id": ku_id,
                "external_source": source,
                "external_id": external_id,
                "decision": "same",
                "accessed_date": "2026-10-16",
                "process_ref": PROCESS_REF,
                "legacy_ku_id": "",
                "resolution_note": f"Identity only: {rationale} Accessed 2026-10-16.",
            }
        )

    after_decisions = decision_rows(planned)
    counts = Counter(row["decision"] for row in after_decisions)
    assert counts == Counter(
        {"same": 1707, "new": 4996, "undecided": 5596, "excluded": 98, "conflict": 7}
    ), counts
    family_after = [
        row for row in after_decisions if candidate_by_id[row["candidate_id"]]["suggested_type"] == "family"
    ]
    assert Counter(row["decision"] for row in family_after) == Counter(
        {"same": 22, "new": 94, "undecided": 18, "excluded": 1}
    )
    assert {row["candidate_id"] for row in family_after if row["decision"] == "undecided"} == set(PENDING_ROUTES)
    groups = defaultdict(list)
    for row in after_decisions:
        if row["decision"] == "new":
            group = group_id(row["resolution_note"])
            assert group, row["candidate_id"]
            groups[group].append(row)
    assert len(groups) == 4827 and sum(map(len, groups.values())) == 4996
    for cid, (group, _) in NEW.items():
        assert [row["candidate_id"] for row in groups[group]] == [cid]
    assert len(planned) == 12593
    assert sum(bool(row["external_source"]) for row in planned) == 189
    assert len({row["alignment_id"] for row in planned}) == len(planned)

    if args.dry_run:
        print(
            "dry-run passed: family candidates undecided->same=9/new=8/excluded=1; "
            "18 family candidates retain explicit pending routes; family counts same=22 new=94 "
            "undecided=18 excluded=1; all S3 counts and cross-type pointers verified; "
            "new_groups=4827 new_candidates=4996; Treccani identity rows=2; no files written"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: S3 family review updated 18 decisions and clarified 18 pending routes; "
        "family counts same=22 new=94 undecided=18 excluded=1; "
        "new_groups=4827 new_candidates=4996; external records=189"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
