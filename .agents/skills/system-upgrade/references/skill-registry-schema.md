# Skill Registry Snapshot Contract

Skill 注册表是可重建导航快照，不是第二份 Skill 定义。

## 唯一根与角色

仓库内唯一允许的 Skill 根为 `.agents/skills/`，固定路径为 `.agents/skills/<skill-name>/SKILL.md`。其他根或历史阶段分类路径出现 `SKILL.md` 必须报错。

每个活跃 Skill 在 frontmatter 中显式声明，且 frontmatter 不得出现重复键：

```yaml
name: verify
kind: leaf
phase: current
triggers:
  - verify
  - 验证知识元
description: ...
```

phase 为 current（第一部分）、later（后续部分）或 support（按需支持），阶段适用范围必须明确。

router 额外声明 `routes_to`。不得再用目录层级猜测 router/leaf；同一 trigger 只能有一个直接所有者。

## 派生字段

`06-runtime/state/skill-registry.json` 由以下磁盘事实确定性生成：

- `name`、`kind`、`phase`、`description`、`triggers`、`routes_to` 来自 frontmatter；
- `path` 来自目录，不再派生冗余 category；适用部分由 phase 表达；
- `references` 只来自 Skill 直接声明的 Markdown reference 路径；
- `scripts` 来自 Skill 与这些 direct references 中的显式 `scripts/*.py` 引用。

相邻目录中的文件不会因为“放在 references 下”而自动成为有效合同。未被任何 Skill 直接引用的 reference、断裂 reference、间接隐藏 reference、孤立脚本引用、重复 frontmatter key 和第二 Skill 根都必须报错。reference 可以链接另一份已直接登记的 reference 作为交叉说明，但不得增加 `AGENTS -> SKILL -> direct reference` 之外的必读层级。

直接登记表示路径可发现，不表示每次使用 Skill 都全文读取所有参考。清单注明适用情境，按当前问题选择；跨 Skill 的共享契约使用完整仓库路径。注册表不替代各任务当前 results，也不收纳用户原话或过程正文。

## 生成与校验

```powershell
python scripts/skill_registry.py --export
python scripts/skill_registry.py
```

新增、删除或转换 Skill 时只修改最近的 `SKILL.md` 与必要调用引用；工作包收尾时刷新一次 JSON。禁止手工维护第二份 display name、触发词、权限或调用图。
