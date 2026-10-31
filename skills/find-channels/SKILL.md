---
name: find-channels
description: Find and verify public organization channels, including official pages, BOSS Zhipin and Liepin company profiles, and professional social profiles. Use for Layer 2 research, public recruiting-channel collection, or channel-coverage audits. Write verified observations directly into the company's public data/companies record; no personal workspace, application inbox, or separate manager handoff is required. Keep personal conversations and application progress in the private applications workflow.
---

# Find Channels · 公开招聘与联系入口

这是公共研究流程，由经营型机构和投资机构共用。由任何具备相应访问与写入权限的 Agent 执行，资料归属按内容判断：公开企业主页属于公司资料，已核实后直接更新 `data/companies/<id>.json`；个人聊天、简历和投递进展才属于私人 applications。公开研究不要求读取履历、求职偏好、私人工作区配置，也不先写 inbox。

## 选择范围

先读仓库 `AGENTS.md` 和 `data/index.json`，按任务指定的公司与平台执行，复用稳定 ID。用户要求全部公司时覆盖全部，不擅自缩成第一波；只指定 BOSS 直聘和猎聘时只查这两家，不附加脉脉或 Layer 3。

| `layer` | 采集对象 |
| --- | --- |
| `official` | 官网、官方招聘或业务入口 |
| `recruitment_platform` | 任务指定平台上的公开企业主页 |
| `professional_social` | 已核实归属的机构账号或公开专业身份主页 |

可用审计工具输出覆盖情况或任务模板；模板仅在标准输出呈现，不需要保存私人批次：

```bash
python3 skills/find-channels/scripts/audit_channels.py --entity companies --wave all --summary
python3 skills/find-channels/scripts/audit_channels.py --entity companies --wave all --offset 0 --limit 20 --template
```

## 核实并直接更新公司资料

1. 核对平台页面中的机构名称、官网、地区和主体，区分同名公司、品牌、集团与子公司。复用正式记录的名称／别名；新发现的主体名称需先以公开证据确认，再补充别名，不绕过归属校验。
2. 记录稳定的企业主页，实际核查日期、证据标题与来源。招聘、BP、商务、客服等用途分开，不猜邮箱。
3. 将已核实的公开入口写入该公司 `channels`，证据写入 `sources` 并标 `scope: "channel"`。原业务 `checked_at`、其他事实与既有渠道保持原意，重复核查更新同一入口，不制造副本。
4. 未找到、访问受限或主体无法确定时，在本次研究报告中逐公司列明平台、实际检查日期与缺口，不写成 confirmed，也不创建 application 或私人 inbox 记录。有证据的部分确认入口可按现有 `channels` 契约记录 `partial`，不能伪造来源或 URL。
5. 具体公开岗位也属于公共研究，不属于个人投递记录；`channels` 专门存入口，不能用短期 JD 冒充企业主页。若任务另需逐条岗位明细，按所属公司公共数据契约记录，缺少适用字段时先补充契约，不以私人 inbox 代替公共字段。公开招聘薪资范围与个人期望薪酬分清。

字段见 [数据模型](../../data/README.md)。旧 `contacts.careers_url` 可能是历史帖子或平台页，不能统称官方官招；来源里出现某平台域名也不等于已核实机构归属。Layer 3 的专业人物主页需要公开身份依据，不能把私人 HR 联系方式或聊天上传。

## 可选的直接写入工具

采集 Agent 可直接编辑公司 JSON 后校验，也可把已经核实的公开观察 JSON 经标准输入交给 [update_layer2.py](scripts/update_layer2.py)，直接更新公司档案，不经过私人目录。已获授权的公开采集任务无需再等另一位管理 Agent 批准。

输入契约见 [channel-batch.schema.json](../../data/schemas/channel-batch.schema.json)：顶层 `schema_version: 1`、`public_only: true`、`entries`；每项包含 `entity_type`、`entity_id`、`platform`、`url`、`observed_name`、`checked_at`、`evidence_title`、`verification_status: "confirmed"`。平台值为 `boss_zhipin`、`liepin` 或任务明确要求的 `maimai`。

```bash
# 将采集程序实际观察到的 JSON 输出通过管道交给此命令，无需批次落盘：
.venv/bin/python skills/find-channels/scripts/update_layer2.py --apply
```

该命令从标准输入读取 JSON；也可传 `--batch-file PATH` 读取已有的纯公共观察文件。未带 `--apply` 时仅预览，这是本地检查选项，不是必需的人工交接。工具检查主体、平台、日期、来源和全部输入后原子写入；它不能替代真实网页核验。并行时按公司分工，避免覆盖他人的新修改。

## 完成

```bash
python3 tools/build.py
.venv/bin/python tools/validate.py --check-generated
```

汇报已更新公司／平台与未解决项，公共资料可随仓库同步 GitHub。个人筛选、投递、聊天与真实进展另按私人 applications 规则记录；公开研究不授予发消息、投递或预约权限。通用任务提示见 [执行参考](references/layer2-research.md)。
