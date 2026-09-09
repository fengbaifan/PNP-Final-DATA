---
name: inspector
kind: leaf
triggers:
  - inspector
  - 当前健康状态
description: >
  系统健康检查技能。以 audit_repo.py 和 current-health.json 为事实入口，
  区分结构门禁、证据链完整性、知识成熟度、研究债务与候选机会。
---

# inspector v5.0

## 目的

Inspector 报告仓库当前状态与下一可执行边界，不重写规则，也不把机械分数当作语义验收。

## 输入

- `scripts/audit_repo.py`: read-only live audit.
- `06-runtime/state/current-health.json`: generated snapshot.
- `06-runtime/governance/governance-backlog.md`: categorized derived backlog.
- `06-runtime/state/discovery-manifest.json`: active candidate baseline.

## 必须区分

1. `structural_health` is a 130-point contract and workflow gate score.
2. `knowledge_structure_quality` is a 65-point schema/state integrity score.
3. `evidence_quality` is a 55-point evidence-chain integrity score.
4. `knowledge_maturity` is unscored. Report its source-count, confidence, consensus, evidence-status, isolation, and candidate distributions directly.
5. Research debt is not a system defect. Candidate opportunity is not accepted knowledge.

## 执行

```powershell
python scripts/audit_repo.py --summary
```

Run `python scripts/write_current_health.py` only when the task authorizes refreshing generated state. Read `governance-backlog.md` after refresh and keep these sections separate:

- System defects P0/P1/P2;
- research debt;
- candidate opportunities;
- completed mechanical signals.

## 报告格式

```markdown
# 健康检查 - YYYY-MM-DD

## 阻断性系统缺陷
- ...

## 研究债务
- ...

## 候选机会
- ...

## 指标
- Structural health: N/130
- Knowledge structure integrity: N/65
- Evidence-chain integrity: N/55
- Single-source units: N
- Tentative units: N
- Isolated units: N
- Candidates needing evidence: N
```

不得从满分结构健康推导发布就绪或语义成熟。
