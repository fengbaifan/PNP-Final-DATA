# Skill Registry Snapshot Contract v4.0

Skill 注册表是可重建导航快照，不是第二份 Skill 定义。

## 唯一根与角色

仓库内唯一允许的 Skill 根为 `.agents/skills/`。其他目录出现 `SKILL.md` 必须 fail closed。

每个活跃 Skill 在 frontmatter 中显式声明，且 frontmatter 不得出现重复键：

```yaml
name: verify
kind: leaf
triggers:
  - verify
  - 验证知识元
description: ...
```

router 额外声明 `routes_to`。不得再用目录层级猜测 router/leaf；同一 trigger 只能有一个直接所有者。

## 派生字段

`06-runtime/state/skill-registry.json` 由以下磁盘事实确定性生成：

- `name`、`kind`、`description`、`triggers`、`routes_to` 来自 frontmatter；
- `path`、`category` 来自目录；
- `references` 只来自 Skill 直接声明的 Markdown reference 路径；
- `scripts` 来自 Skill 与这些 direct references 中的显式 `scripts/*.py` 引用。

相邻目录中的文件不会因为“放在 references 下”而自动成为有效合同。未被任何 Skill 直接引用的 reference、断裂 reference、间接隐藏 reference、孤立脚本引用、重复 frontmatter key 和第二 Skill 根都必须报错。reference 可以链接另一份已直接登记的 reference 作为交叉说明，但不得增加 `AGENTS -> SKILL -> direct reference` 之外的必读层级。

## 生成与校验

```powershell
python scripts/skill_registry.py --export
python scripts/skill_registry.py
```

新增、删除或转换 Skill 时只修改最近的 `SKILL.md`、分类 README 与必要路由；工作包收尾时刷新一次 JSON。禁止手工维护第二份 display name、触发词、权限或调用图。
