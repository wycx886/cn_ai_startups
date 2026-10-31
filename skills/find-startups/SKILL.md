---
name: find-startups
description: Find, classify, and verify newly emerging AI organizations for the first prospecting wave, including operating AI organizations and new independent investment managers. Use when circling first-wave targets, researching new VC teams from established investment platforms, checking funding evidence or classification, or maintaining canonical organization records. The primary axis is new entrants versus incumbents, without a fixed founding-year cutoff.
---

# Find AI Startups · 第一波新进机构

保留 `find-startups` 名称作为兼容入口。当前任务是圈定新进 AI 玩家，经营型机构和新一代投资机构都可以成为独立研究、pitch 与机会发现对象。当前不扩搜已有大平台，也不实际开展 Layer 2／3 采集或接触。

## 先读当前名单

读取仓库根目录的 `data/targets.json` 和 `catalog/first-wave.md`，再按需加载单条 JSON。所有命令从仓库根目录执行：

```bash
python3 scripts/query.py --entity organizations --wave first
python3 skills/find-startups/scripts/audit_entities.py --entity organizations --wave first --summary
```

赛道边界和来源口径见 [分类与归因参考](references/taxonomy-and-vc-rubric.md)。遇到从老基金或投资平台出来的新团队，按 [新进 VC SOP](references/new-vc-spinouts.md) 单独核实。

## 判断第一波范围

- **新进／已有是主分类**：经营型 AI 机构与投资机构是组织类型，不是互斥的两套寻源系统。
- 不设置统一成立年份门槛。成立日期只是证据之一；上市、拿到融资或曾从某平台离职都不能单独决定分类。
- `targeting.kind` 为 `editorial_assessment`。用 `player_group` 记录 `new_entrant`／`incumbent`／`unresolved`，用 `wave` 记录 `first`／`watchlist`／`later`；写清理由与本机构来源 ID。
- 第一波是研究候选，不是质量排名、法律独立性证明或对某位使用者的适配评分。主体、存续状态或新进定位不明时保留观察，不强行纳入。
- 已有玩家保留在后续名单。未来 Find AI incumbents 可研究成熟平台的 AI 业务或投资团队，当前不因整理名单而扩搜。

## 研究机构与融资

确认当前主体、主要产品或策略、独立运作线索、关键团队、融资／募资披露和信息缺口。优先机构、被投企业、监管等公开一手资料；使用其他来源时说明性质和局限。

经营型机构仍保存在 `data/companies/`，投资机构在 `data/investors/`。这是字段和兼容分组，统一目标索引负责第一波入口。业务赛道读取 `data/taxonomy.json`，不要在 Skill 里复制另一套分类定义。

融资状态保留 `confirmed_disclosure`、`partial`、`not_found` 的原意。没有研究不能标成“未找到”；有机构资本不等于所有机构都获 VC 投资。自筹、众筹、创始人支持、产业收购及口径冲突逐条保留，不因归入第一波提升披露核验状态。

比较分析说明具体业务边界，保留适用范围；不补造性能或收益排名。更名保持稳定 ID，避免同一机构重复建档。

## 新记录先作私人草稿

脚手架先检查 ID 和名称，默认只输出草稿；不会直接把空模板放入正式 `data/`。显式使用 `--save-draft` 才保存到已配置私人工作区的 `drafts/research/`：

```bash
python3 skills/find-startups/scripts/scaffold_entity.py --entity company --id candidate-org --name "待核实机构" --category 04
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
