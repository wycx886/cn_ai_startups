---
name: find-channels
description: Find and verify public organization-level channels, including official websites, careers pages, public emails, and BOSS Zhipin or Liepin company profiles. Use for Step 2 of the opportunity methodology (identifying how to approach a target organization), public recruiting-channel collection, or channel-coverage audits. Route key-person and founder/partner profile discovery to find-person.
---

# Find Channels · 机构公开触达渠道

本 Skill 对应方法论的第二步（**找公司 → 找渠道 → 找核心人物**）：在确定目标机构（[find-startups](../find-startups/SKILL.md) ／ [find-incumbents](../find-incumbents/SKILL.md)）之后，核实**机构级（Organization-level）公开触达入口**。寻找具体创始人、业务负责人或 VC 合伙人的个人主页（LinkedIn / X / GitHub 等）请使用第三步 Skill：[find-person](../find-person/SKILL.md)。

公开企业主页与官方入口属于公司资料，已核实后直接更新 `data/companies/<id>.json`；个人聊天、简历和投递进展才属于私人 `applications`。公开研究不要求读取履历、求职偏好、私人工作区配置，也不先写私人 `inbox/`。

## 1. 机构公开渠道的范围（How to Approach the Organization）

先读仓库 `AGENTS.md` 和 `data/index.json`，按任务指定的公司与平台执行，复用稳定 ID。用户要求全部公司时覆盖全部，不擅自缩成第一波；只指定 BOSS 直聘和猎聘时只查这两家。

| 机构渠道类别 (`layer`) | 采集与核验对象 |
| --- | --- |
| **官方直达入口** (`official`) | 官方网站 (`website`)、官方招聘站/ATS (`careers_url`)、公开招聘邮箱 (`recruitment_email`)、BP/商务/合作邮箱 (`other_email`) |
| **招聘平台企业主页** (`recruitment_platform`) | 机构在 BOSS 直聘 (`boss_zhipin`)、猎聘 (`liepin`)、脉脉 (`maimai`) 上的公开认证企业主页（`owner.scope: "organization"`） |
| **机构官方社媒与开源主页** (`professional_social`) | 机构官方的 LinkedIn 公司页、官方 X 账号、官方 GitHub Organization（`owner.scope: "organization"`；个人主页交由 [find-person](../find-person/SKILL.md)） |

可用审计工具输出覆盖情况或任务模板：

```bash
python3 skills/find-channels/scripts/audit_channels.py --entity companies --wave all --summary
python3 skills/find-channels/scripts/audit_channels.py --entity companies --wave all --offset 0 --limit 20 --template
```

## 2. 核实并直接更新公司资料

1. **核对主体归属**：核对平台页面中的机构名称、官网、地区和工商/运营主体，区分同名公司、品牌、集团与子公司。复用正式记录的名称／别名；新发现的主体名称需先以公开证据确认，再补充别名。
2. **区分入口用途**：记录稳定的企业主页、实际核查日期、证据标题与来源。招聘、BP、商务、客服等邮箱用途严格分开，绝不按域名格式猜测邮箱。
3. **写入结构化 `channels`**：将已核实的公开入口写入该公司 `channels`，证据写入 `sources` 并标 `scope: "channel"`。原业务 `checked_at`、其他事实与既有渠道保持原意，重复核查更新同一入口，不制造副本。
4. **如实报告缺口**：未找到、访问受限或主体无法确定时，在本次研究报告中逐公司列明平台、实际检查日期与缺口，不写成 `confirmed`，也不创建私人 application 或 inbox 记录。
5. **不把短期 JD 当企业主页**：`channels` 专门存稳定的机构级入口，不能用两周就下线的单个岗位链接冒充企业主页。

`channels[]` 只记录机构网页入口，`owner.scope` 固定 `organization`。公开邮箱值仍放在 `contacts` 的相应用途字段，以实际披露页面提供证据，不把邮箱猜成招聘用途；`mailto:` 不能冒充网页 URL。个人姓名、职务、履历和主页只维护在公司 `people[]`。

字段契约详见 [数据模型](../../data/README.md)。

## 3. 批量校验与原子写入工具

采集 Agent 可直接编辑公司 JSON 后校验，也可把已经核实的招聘平台企业主页观察 JSON 经标准输入交给 [update_layer2.py](scripts/update_layer2.py)，直接更新公司档案，不经过私人目录。

输入契约见 [channel-batch.schema.json](../../data/schemas/channel-batch.schema.json)：顶层 `schema_version: 1`、`public_only: true`、`entries`；每项包含 `entity_type`、`entity_id`、`platform`、`url`、`observed_name`、`checked_at`、`evidence_title`、`verification_status: "confirmed"`。

```bash
# 将采集程序实际观察到的 JSON 输出通过管道交给此命令，直接原子更新公司档案：
.venv/bin/python skills/find-channels/scripts/update_layer2.py --apply
```

## 4. 完成校验

```bash
python3 tools/build.py
.venv/bin/python tools/validate.py --check-generated
```

汇报已更新公司／平台与未解决项，公共资料可随仓库同步 GitHub。通用采集参考见 [执行参考](references/layer2-research.md)。
