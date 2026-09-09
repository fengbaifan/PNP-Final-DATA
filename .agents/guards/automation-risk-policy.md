# Automation Risk Policy

## Scope

`scripts/_evidence_policy.py` is the single executable definition of evidence automation risk. Both `scripts/evidence_batch_runner.py` and `scripts/verify_apply_evidence.py` use it.

The runner may parse evidence, classify risk, write non-empty queues, invoke the typed evidence apply path, and call the change-aware closure once. It does not create knowledge units, decide claim truth, select relation types, generate governance prose, or execute Git.

## Risk levels

| Level | Meaning | Automated action |
|---|---|---|
| `L1` | existing-KU, bounded evidence update | explicit dry-run; apply only with `--apply-low-risk` |
| `L2` | evidence or candidate requiring semantic review | non-empty `review_queue.jsonl` |
| `L3` | semantic boundary or unsafe state promotion | non-empty `defer_queue.jsonl` |

`L1` requires an existing `ku_path`, a controlled low-risk `claim_scope`, `strong` or `medium` match quality, and changes no stronger than `partially_verified`, `medium`, and `tentative`.

The following always route to `L3`: a proposed new KU, `externally_verified`, `confirmed`, `high`, automatic `source_count` change, an explicit blocking reason, or a deferred event boundary.

## Output contract

Every run writes `plan.json`. Queue files are materialized only when they contain records:

- `apply_candidates.jsonl`
- `no_delta_candidates.jsonl`
- `review_queue.jsonl`
- `defer_queue.jsonl`

An absent queue means zero records; the counts in `plan.json` are authoritative. Fixed empty queue fan-out is prohibited.

## Gates and closeout

`--run-gates` calls `scripts/run_sync_closure.py` once. Generated refresh, full acceptance, commit, and push remain work-package closeout actions and are not embedded in the evidence runner.
