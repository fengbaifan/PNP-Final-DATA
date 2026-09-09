# Batch-local Runtime State Contract v3.0

## 一、权威边界

运行状态属于 work package，不属于仓库全局单例。每个需要恢复的长任务使用自己的：

```text
06-runtime/automation/<work-package>/runner-state.json
```

短任务和 dry-run 不必生成状态文件。

## 二、最小状态

```yaml
batch_id: stable-id
status: running | completed | failed | blocked
current_stage: string
updated_at: ISO-8601
events: []
processed_items: []
failed_items: []
input_fingerprint: sha256
```

checkpoint 只在可恢复边界记录：collect 完成、已批准 change-set 固化、apply 完成和 validation 完成。不得为每个微步骤增加状态。

## 三、恢复规则

1. `--resume` 必须显式指向同一工作包的 state 文件。
2. 恢复前核对 input fingerprint；输入变化时不得跳过旧步骤。
3. 已完成对象不重跑，失败对象保留错误和最后一次尝试。
4. 不允许根据另一个批次或全局状态猜测当前任务进度。

## 四、唯一实现

- `scripts/_runtime_state.py` 只接受显式 `state_path`，新状态同时要求 `batch_id` 与 `input_fingerprint`。
- 仓库级全局状态文件和旧 agent/plan schema 已退役，不再保留兼容写入。
- `verify_apply_evidence.py --resume` 在读取任何 processed item 前必须比较 evidence 指纹；不一致直接拒绝恢复。

## 五、验收

- 两个工作包并行时状态文件互不覆盖。
- dry-run 不改变全局状态。
- completed 状态只在整批预检、原子 apply、verification log 提交和定向验证成功后写入；blocked/failed 不得先记 completed。
- 状态文件不能替代 candidate、evidence、apply plan 或知识裁决记录。
