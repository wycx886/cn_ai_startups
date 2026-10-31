---
name: find-company
description: Find and verify AI opportunity targets in China, including startups, corporate incubations, internal venture teams, research labs, subsidiaries, spinouts, and new VC managers. Use for Find company, company discovery, big-tech AI projects or labs, AI for Science and biotech teams, new VC founders, funding checks, and first-wave classification. Distinguish the specific initiative from its incumbent parent, and record its actual organization form without requiring independent incorporation, VC funding, or a fixed founding year.
---

# Find Company · AI 机构与项目寻源

本 Skill 由原 `find-startups` 扩展而来。圈定新进 AI 玩家时，独立创业机构、新一代投资机构，以及有明确业务或研究目标的大厂项目、实验室和孵化团队都可单列为机会目标。按具体单元研究，注明组织形态和母平台关系；不要求它已注册独立公司或拿到 VC 投资。本阶段不实际开展 Layer 2／3 采集或接触。

## 先读当前名单

读取仓库根目录的 `data/targets.json` 和 `catalog/first-wave.md`，再按需加载单条 JSON。所有命令从仓库根目录执行：

```bash
python3 scripts/query.py --entity organizations --wave first
python3 skills/find-company/scripts/audit_entities.py --entity organizations --wave first --summary
```

赛道边界和来源口径见 [分类与归因参考](references/taxonomy-and-vc-rubric.md)。遇到从老基金或投资平台出来的新团队，按 [新进 VC SOP](references/new-vc-spinouts.md) 单独核实。

遇到大厂实验室、内部创业、孵化业务或拆分团队，读取 [大厂项目 SOP](references/corporate-ventures.md) 和 `data/platforms.json`，按平台逐项排查。该底表分别列主要互联网平台和相关云／ICT集团，不将它们统一叫作 hyperscaler；底表出现某个平台不等于发现了项目。

```bash
python3 scripts/query.py --entity companies --parent bytedance --json
python3 scripts/query.py --entity companies --form corporate_spinout
```

## 判断第一波范围

- **新进／已有是主分类**：经营型 AI 机构与投资机构是组织类型，不是互斥的两套寻源系统。
- 不设置统一成立年份门槛。成立日期只是证据之一；上市、拿到融资或曾从某平台离职都不能单独决定分类。
- `targeting.kind` 为 `editorial_assessment`。用 `player_group` 记录 `new_entrant`／`incumbent`／`unresolved`，用 `wave` 记录 `first`／`watchlist`／`later`；写清理由与本机构来源 ID。
- 第一波是研究候选，不是质量排名、法律独立性证明或对某位使用者的适配评分。主体、存续状态或新进定位不明时保留观察，不强行纳入。
- 成熟母平台整体和常规已有业务保留后续；其具名新项目可以单独成为第一波候选。先判断具体单元是否新进，不把母平台的 `incumbent` 身份直接套到所有单元，也不把每个大厂部门自动纳入第一波。
- 将组织形态写入 `organizational_context`，关联母平台 ID 与来源。区分内部团队、研究实验室、产品项目、子公司和拆分机构；拆分不自动代表母平台不再控股，前员工创业也不自动代表原公司资产／项目转移。旧记录缺少该字段表示尚未标注。

## 研究机构与融资

确认当前主体、主要产品或策略、独立运作线索、关键团队、融资／募资披露和信息缺口。优先机构、被投企业、监管等公开一手资料；使用其他来源时说明性质和局限。

经营型机构仍保存在 `data/companies/`，投资机构在 `data/investors/`。这是字段和兼容分组，统一目标索引负责第一波入口。业务赛道读取 `data/taxonomy.json`，不要在 Skill 里复制另一套分类定义。

融资状态保留 `confirmed_disclosure`、`partial`、`not_found` 的原意。没有研究不能标成“未找到”；有机构资本不等于所有机构都获 VC 投资。对已证实的内部团队／实验室／项目可用 `not_applicable` 表示不适用独立主体股权融资，不代表没有内部资源。自筹、众筹、创始人支持、产业收购及口径冲突逐条保留，不因归入第一波提升披露核验状态。

比较分析说明具体业务边界，保留适用范围；不补造性能或收益排名。更名保持稳定 ID，避免同一机构重复建档。

## 新记录先作私人草稿

脚手架先检查 ID 和名称，默认只输出草稿；不会直接把空模板放入正式 `data/`。显式使用 `--save-draft` 才保存到已配置私人工作区的 `drafts/research/`：

```bash
python3 skills/find-company/scripts/scaffold_entity.py --entity company --id candidate-org --name "待核实机构" --category 04
```

未取得的事实和日期用 `null`，不创建假来源，也不把未研究直接写成 `not_found`。核实并完成正式字段后才晋升公共记录；发布检查会拒绝占位内容或示例网址。

## 标记与更新

`targeting.rationale` 写具体纳入／观察／留待后续的理由，`source_ids` 对应本机构的来源，`labelled_at` 仅记录编辑分类时间。它不刷新机构业务 `checked_at`。`coverage.role` 的原有范围标记与第一波标记分别维护。

VC 的 `prior_firm` 表示原机构案例，`current_firm` 表示当前机构案例，不是特定基金的归因。只有明确证据才写主导、退出或回报；成立、管理人登记、基金首关与品牌更名分开。

更新正式 JSON 后运行：

```bash
.venv/bin/python scripts/validate.py
python3 scripts/build.py
.venv/bin/python scripts/validate.py --check-generated
```

缺失证据保留待核实。仅做第一波编辑标记时，不把旧来源统一刷成今天，也不触发渠道采集或对外动作。
