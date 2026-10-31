---
name: find-channels
description: Discover and verify public organization channels across official entrypoints, recruitment-platform company pages, and professional social profiles. Use when auditing channel coverage, preparing or reviewing a Layer 2 collection batch, or maintaining sourced public channels for operating organizations and investment firms. Keep public channel records separate from personal conversations and read individual preferences only for an explicitly requested personal task.
---

# Find Channels · 三类公开入口

本方法由经营型机构和投资机构共用。Layer 1／2／3 是入口类别，不是固定优先顺序，也不预设个人岗位、城市、背景或某个采集工具。当前阶段只圈定第一波机构；除非后续任务明确要求，不自动采集 Layer 2／3 或触达他人。

| `layer` | 采集对象 |
| --- | --- |
| `official` | 官网、官方招聘或业务入口 |
| `recruitment_platform` | BOSS 直聘、猎聘、脉脉上的公开企业主页 |
| `professional_social` | 已核实归属的机构账号或公开专业身份主页 |

公开入口存于所属机构 JSON 的 `channels` 并关联 `sources`。个人聊天、HR 私人联系方式、薪酬、简历和投递状态只存私人工作区；不能从个人沟通原文直接整批入公共库。

## 审计与准备采集任务

先读 `data/targets.json`，按任务指定的范围选择机构；默认第一波方法不偏向特定赛道。命令从仓库根目录执行：

```bash
python3 skills/find-channels/scripts/audit_channels.py --entity organizations --wave first --summary
python3 skills/find-channels/scripts/audit_channels.py --entity organizations --wave first --offset 0 --limit 20 --template
```

模板是候选采集输入，不是已经核实的数据。保存到解析出的私人工作区 `research/inbox/`，使用唯一批次名，不覆盖已有候选文件。结构化渠道覆盖率与旧 `contacts`／来源网址提示分开，不把出现某个平台域名当作已经找到机构入口。

## 核对入口与归属

1. 确认机构 ID 与观察到的企业名称，核对官网、平台主体、地区或其他足以区分同名机构的信息。
2. 记录稳定公开页面，Layer 2 使用企业主页；短期具体 JD 和个人申请进展不放进这个公开入口字段。
3. 记录真实访问并确认页面的日期、证据标题与公开属性；打不开或归属不明的结果留作候选，不假装已核实。
4. 将招聘、BP、商务、客服、技术等用途分开。`hr@` 等字符串不是用途核实依据，不按邮箱格式猜地址。
5. Layer 3 的机构账号或公开专业人物主页要有归属证据。普通引用、转发或第三方 GitHub 项目不等于目标机构／负责人的联系渠道。

`channels` 的全部字段见 [数据模型](../../docs/data-model.md)。旧 `contacts` 保留兼容；其中 `careers_url` 可能是招聘平台或历史帖子，不能统称官方官招。

## Layer 2 候选批次与合并

可由任意有权限读取平台的 Agent 采集。Grok／Google Drive 等工具只是可选适配，见 [采集交接参考](references/grokbot-layer2-sop.md)，不是 Fork 使用者的依赖。

合并输入为 JSON 批次：`schema_version: 1`、`public_only: true`、`entries`。每项只有以下公开字段：

| 字段 | 含义 |
| --- | --- |
| `entity_type` | `operating_organization` 或 `investment_firm` |
| `entity_id` | 对应正式记录的稳定 ID |
| `platform` | `boss_zhipin`、`liepin` 或 `maimai` |
| `url` | 已核对的公开企业主页 |
| `observed_name` | 在该页面看到的机构名称，用于核对归属 |
| `checked_at` | 实际页面核查日期 |
| `evidence_title` | 能识别本次公开页面依据的标题 |
| `verification_status` | 合并正式数据时为 `confirmed`；不确定候选不能晋升 |

批次不带私人备注、薪酬或 HR 名单。先预览，复核后显式应用：

```bash
PRIVATE_WORKSPACE="$(python3 scripts/workspace.py)"
.venv/bin/python skills/find-channels/scripts/merge_layer2_inbox.py --inbox-file "$PRIVATE_WORKSPACE/research/inbox/layer2-batch.json"
.venv/bin/python skills/find-channels/scripts/merge_layer2_inbox.py --inbox-file "$PRIVATE_WORKSPACE/research/inbox/layer2-batch.json" --apply
```

这里的文件名是调用示例，应换成实际唯一批次文件。工具应校验机构 ID、目标目录、平台主页类型、公开字段、归属和日期；默认预览，不能用畸形 ID 走出资料目录。工具不替代实际网页核验，`confirmed` 需要采集者已有真实依据。

合并只更新该渠道与对应的渠道专用来源（`scope: "channel"`），保留原机构业务 `checked_at`。导入旧批次不把日期刷新为今天，重复导入不能增加重复入口或提升新鲜度。

## 完成与个人任务

公共更新后校验、生成阅读版并检查差异。私人机会筛选只在明确任务中读取有效工作区的 `preferences.md`，不要将这些条件回写成公共批次优先级。公开入口的存在不授予发送、投递或预约权限；有明确授权时再依照本人规则执行并在私人日志记录真实动作。
