# cn_ai_opp

面向 Agent 的机构研究与机会发现框架，当前公共资料聚焦中国 AI 领域（China AI Opportunities，简称 `cn_ai_opp`）。寻源方法拆为 **`find-startups` 新进玩家**与 **`find-incumbents` 已有玩家**，两者都由任务指定主题、地域和行业，不将 AI 或中国写成永久筛选条件。公共样本按证据和编辑判断选择，不代表全市场、质量排名或统一的成立年份门槛。

## 从两条寻源路径开始

| 需求 | 入口 |
| --- | --- |
| 第一波目标机构与待核实候选 | [第一波名单](catalog/first-wave.md) · [统一机器索引](data/targets.json) |
| 已有玩家及具体业务单元 | [find-incumbents](skills/find-incumbents/SKILL.md) · [已有资料登记](catalog/later.md) |
| 全部机构档案、赛道与统计 | [资料目录](catalog/README.md) · [分类说明](catalog/taxonomy.md) |
| Agent 阅读与更新规则 | [AGENTS.md](AGENTS.md) |
| 寻找新进机构与创业项目 | [find-startups](skills/find-startups/SKILL.md) |
| 通用研究方法与第三方 Skill 参考 | [研究方法](docs/research-methods.md) |
| 大厂项目、实验室与拆分机构 | [已建档项目](catalog/corporate-ventures.md) · [识别 SOP](docs/corporate-ventures.md) |
| 当前中国 AI 已有玩家候选池 | [平台清单](catalog/platforms.md) · [机器底表](data/platforms.json) · [中国研究示例](skills/find-incumbents/references/china-example.md) |
| 从老基金／平台出来的新 VC 团队 | [新进 VC SOP](skills/find-startups/references/new-vc-spinouts.md) |
| 下一阶段的渠道核验方法 | [find-channels](skills/find-channels/SKILL.md) |
| 字段、归因与同步范围 | [数据模型](docs/data-model.md) · [VC 方法](docs/investor-methodology.md) · [Git 同步](docs/git-sync.md) |

主分类是**新进玩家／已有玩家**，经营型机构／投资机构是第二个维度。`find-startups` 寻找创业机构、新进 GP 和有明确边界的新孵化／拆分项目；`find-incumbents` 寻找在目标市场已有实质业务的成熟平台、软件或硬件厂商、行业经营者及投资机构，再定位相关业务和团队。已有玩家按具体市场中的业务证据判断，不仅看规模、年份或上市状态，也不把各行业的大公司一律叫作 hyperscaler。

母平台是已有玩家，不妨碍其真正的新项目成为新进候选；成熟部门也不会仅因新命名自动变成 startup。两条路径共享同一份正式机构记录，按单元和关系交叉引用，避免重复建档。当前不实际采集或执行 Layer 2／3。

`targeting` 是编辑性的寻源标记。`first` 表示第一波研究候选，`watchlist` 保留证据或定位缺口，`later` 保留已有玩家资料批次，不表示禁止研究或价值较低。它不证明机构成立于某年、法律上完全独立、已获 VC 投资或具有特定投资回报。融资披露和来源限定继续逐条保留；成立年份、上市或股东背景都不单独决定是否纳入。

大厂关联项目另用 `organizational_context` 标记组织形式、母平台关系及证据状态。内部项目不要求已获外部融资；离职员工创业、母公司孵化、控股子公司和正式拆分分别核实，不能互相替代。缺少这个字段也不表示已确认独立。

## data 和 catalog 的区别

- **`data/` 是正式 JSON 记录**，Agent 更新这里的公开事实、来源和标记。
- **`catalog/` 是生成的阅读版**，方便人浏览 Markdown、筛选 CSV；它不是另一份需要手动维护的数据。

例如，更新 `data/companies/hypershell.json` 后运行 `python3 scripts/build.py`，对应的 `catalog/companies/hypershell.md` 和汇总视图会一起更新。不要在两个地方分别改内容。

为兼容已有数据，经营型机构仍保存在 `data/companies/`，投资机构保存在 `data/investors/`；这只是资料字段和存储分组，主要名单统一从第一波入口读取。文件数量和最新统计以生成目录为准。

`data/platforms.json` 是当前中国 AI 研究的**已有玩家／母平台寻源底表**，分组覆盖互联网平台、云与 ICT、软件与 AI、硬件与半导体，以及其他行业经营者。可按行业标签和有来源的主题证据筛选；它不是正式目标档案或排名，也不证明某平台已有可投递项目。官网身份核对、具体业务研究、内部项目识别和法律拆分核实分别进行。

通用 Skill 可研究其他主题或地域，但当前公共数据契约仍服务于本仓库的中国 AI 资料。超出既有分类的结果先留在私人工作区 `research/`，或在明确扩展分类与 schema 后发布，不将非 AI 机构强塞进 AI 赛道。

## 公开渠道与个人记录

| 渠道类别 | 可写入对应机构 JSON 的公开信息 |
| --- | --- |
| Layer 1 `official` | 经核实的官网、官方招聘或业务入口；公开邮箱按原用途记录 |
| Layer 2 `recruitment_platform` | 经核实属于该机构的 BOSS 直聘、猎聘、脉脉企业主页 |
| Layer 3 `professional_social` | 经核实归属的机构账号或公开专业身份主页 |

这些公开入口写进机构的 `channels`，通过 `source_ids` 对应证据。当前 `contacts` 保留为既有公开入口；来源里出现某个网站域名不等于已经找到该机构的渠道。公开入口也不表示正在招聘或获得了联系授权。

个人聊天、招聘者私人信息、薪酬、简历与投递进展只写私人工作区。待核实的采集结果先存私人 `research/inbox/`，复核后才进入公共 `data/`。

## Fork 用户的私人工作区

先让 Agent 读 `AGENTS.md`，再初始化：

```bash
python3 scripts/init_local.py
python3 scripts/workspace.py --json
```

默认在本地创建被忽略的 `workspace/`。已有私人资料时直接绑定，不复制第二套档案：

```bash
python3 scripts/init_local.py --workspace ../my-private-workspace --use-existing
```

工作区应有 `profile.md`、`preferences.md`；路径只保存在被忽略的 `workspace.local.json`。个人方向从这个工作区读取，不由公共 SOP 预设城市、岗位或背景。详见 [本地工作流](docs/application-workflow.md) 和 [空白模板](templates/README.md)。

## 查询与维护

```bash
python3 scripts/query.py --entity organizations --wave first
python3 scripts/query.py --entity investors --id monolith --json
python3 scripts/query.py --player-group incumbent
python3 scripts/query_platforms.py --id huawei
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
python3 scripts/build.py
.venv/bin/python scripts/validate.py --check-generated
```

`README.md`、规则、方法和模板人工维护；`catalog/` 和机器索引由脚本生成。草稿先留在私人工作区；正式记录缺少证据或仍含占位内容时不能发布。

查看差异并确认共享范围后，可运行：

```bash
.venv/bin/python scripts/publish.py --message "更新公共资料"
```

只有这个独立 Git 仓库的共享文件会被提交；私人工作区、路径配置和个人投递记录排除在外。
