---
name: find-startups
description: Discover and verify new entrants for a specified market, including startups, new investment firms, spinouts, and genuinely new corporate ventures or research teams. Use for finding startups, emerging organizations, new GP teams, founder spinouts, or first-wave prospecting. Take geography, industry and theme from the task; AI, China, founding year, VC funding and independent incorporation are not permanent eligibility requirements. Route mature established organizations and ordinary existing business units to find-incumbents.
---

# Find Startups · 新进玩家寻源

寻找指定市场中的新进机构或新形成的业务／研究单元。地域、行业、主题、时间和用途由当前任务决定；中国和 AI 是本仓库当前资料的使用场景，不是本 Skill 的固定门槛。

## 1. 确定范围与研究单位

读取任务给定的 `geography`、`market_or_theme`、`sectors`、`as_of`、`purpose`。能够由上下文确定时直接采用并说明；关键边界缺失时简短澄清，同时整理不依赖答案的线索。

先确认研究的是集团、法人、基金管理机构、具体业务团队、实验室还是项目。新进相对于所选市场判断，不用固定成立年份、上市、有无外部融资一个条件决定。新 GP 也是机构目标，原团队案例和当前机构业绩分开。

若任务主要寻找成熟平台、既有供应商或行业运营商，转用 [find-incumbents](../find-incumbents/SKILL.md)。成熟母公司不自动决定旗下新单元的归类；对有明确新目标与活动证据的孵化团队或拆分项目，本 Skill 可继续判断，不能把每个部门或产品都算成新创业机构。

## 2. 发现并核实候选

从具名产品／研究活动、创始团队、新机构公告、孵化与拆分信息、融资或客户披露寻找线索。先查稳定 ID、历史名称与别名，避免一个品牌更名或同一项目不同阶段被重复建档。

优先官网、公告、监管／登记、原始论文与官方代码、公开产品和客户材料；再用可靠报道补足。将事实、编辑判断和未确认消息分开。成立、登记、品牌启用、基金首关、内部立项和法律拆分分别注明口径。

- 大厂项目与团队：按 [共同的组织归属 SOP](../../docs/corporate-ventures.md)，区分内部团队、实验室、产品项目、子公司、正式拆分与前员工创业。
- 新投资机构：按 [新 VC SOP](references/new-vc-spinouts.md)，核实团队原平台、当前策略、独立形成与案例归因。
- 本仓库的分类与投资归因：见 [分类参考](references/taxonomy-and-vc-rubric.md)；其 AI 赛道只是当前数据契约，不是所有行业的通用分类。

融资不是发现目标的必要条件。没有研究不能标“未找到融资”；内部资源与独立股权融资分开。只有确认内部身份且有来源时，当前契约才允许 `not_applicable`；媒体报道保留其证据强度，不能改成官方确认。

## 3. 输出候选与缺口

每项至少交接：名称／别名、稳定 ID 或待定标记、研究单位、所选市场、主要业务／目标、新进理由、团队或母平台关系、公开活动与资本口径、来源及日期、仍待核实内容。

分为可研究候选、待核实和应转交已有玩家的对象；不自行制造质量排名、个人适配评分或收益。没有可靠主体与活动证据的线索先留私人草稿。

## 4. 适配本仓库

先读 `data/targets.json`、`catalog/first-wave.md` 和 [数据模型](../../docs/data-model.md)。经营型记录与投资机构仍分别保存于 `data/companies/`、`data/investors/`；不是两套个人偏好名单。

```bash
python3 scripts/query.py --entity organizations --wave first
python3 scripts/audit_entities.py --player-group new_entrant --summary
python3 scripts/scaffold_entity.py --entity company --id candidate-org --name "待核实机构" --category 04
```

共享脚手架默认只输出未核实草稿；`--save-draft` 才保存到配置的私人工作区，不直接写入公共库。当前公共数据以中国 AI 机会为主题；若任务超出其主题或分类，先在私人工作区交付通用研究 JSON／Markdown，或按明确任务扩充契约，不强塞进某个 AI 赛道。

正式记录用 `targeting.player_group`、`wave`、理由及来源表达编辑判断。原事实核查日期、关系核查日期和分类日期分别保留；资料不足用 `unresolved`／`watchlist`，不因导入或整理提升核验状态。生成版不可手改。

```bash
.venv/bin/python scripts/validate.py
python3 scripts/build.py
.venv/bin/python scripts/validate.py --check-generated
```

研究方法与第三方参考见 [方法说明](../../docs/research-methods.md)。渠道维护交给 [find-channels](../find-channels/SKILL.md)；不因完成名单而自动采集 Layer 2／3、发消息、投递或预约。个人目的、偏好和沟通只保存在私人工作区。
