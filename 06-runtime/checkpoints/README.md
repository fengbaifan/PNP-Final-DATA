# Checkpoints — 阶段性状态快照

> 每当完成一个 Pipeline Stage，Skill 可在本目录写入 checkpoint。
> checkpoint 是一个阶段完成的断言，不是知识裁决。

## 格式

```
{stage_id}_{timestamp}.md
```

包含：
- stage_id
- completed_at
- outputs_summary
- next_stage
- open_issues

## 当前状态

暂无 checkpoint。checkpoint 在 Pipeline 执行时由对应 Skill 写入。
