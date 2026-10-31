# cn_ai_startups

面向 Agent 的 AI 机构研究与机会发现资料库。当前先圈定这一轮 AI 发展中的**新进玩家**：经营型 AI 机构与新一代投资机构都是可独立研究的目标。样本按现有证据和编辑判断选择，不代表全市场、质量排名或统一的成立年份门槛。

## 第一波从这里开始

| 需求 | 入口 |
| --- | --- |
| 第一波目标机构与待核实候选 | [第一波名单](catalog/first-wave.md) · [统一机器索引](data/targets.json) |
| 已有玩家，留待后续研究 | [后续名单](catalog/later.md) |
| 全部机构档案、赛道与统计 | [资料目录](catalog/README.md) · [分类说明](catalog/taxonomy.md) |
| Agent 阅读与更新规则 | [AGENTS.md](AGENTS.md) |
| 寻找新进机构的方法 | [find-startups](skills/find-startups/SKILL.md) |
| 从老基金／平台出来的新 VC 团队 | [新进 VC SOP](skills/find-startups/references/new-vc-spinouts.md) |
| 下一阶段的渠道核验方法 | [find-channels](skills/find-channels/SKILL.md) |
| 字段、归因与同步范围 | [数据模型](docs/data-model.md) · [VC 方法](docs/investor-methodology.md) · [Git 同步](docs/git-sync.md) |

主分类是**新进玩家／已有玩家**，经营型机构／投资机构是第二个维度。新 VC 自身有团队、策略和公开入口，与经营型 AI 机构并列成为目标。成熟科技平台及成熟投资机构的 AI 团队留待后续的 Find AI incumbents 阶段；当前不扩搜这部分，也不实际采集或执行 Layer 2／3。

`targeting` 是编辑性的寻源标记。`first` 表示第一波研究候选，`watchlist` 保留证据或定位缺口，`later` 留待后续。它不证明机构成立于某年、法律上完全独立、已获 VC 投资或具有特定投资回报。融资披露和来源限定继续逐条保留；成立年份、上市或股东背景都不单独决定是否纳入。

## data 和 catalog 的区别

- **`data/` 是正式 JSON 记录**，Agent 更新这里的公开事实、来源和标记。
- **`catalog/` 是生成的阅读版**，方便人浏览 Markdown、筛选 CSV；它不是另一份需要手动维护的数据。

例如，更新 `data/companies/hypershell.json` 后运行 `python3 scripts/build.py`，对应的 `catalog/companies/hypershell.md` 和汇总视图会一起更新。不要在两个地方分别改内容。

为兼容已有数据，经营型机构仍保存在 `data/companies/`，投资机构保存在 `data/investors/`；这只是资料字段和存储分组，主要名单统一从第一波入口读取。文件数量和最新统计以生成目录为准。

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
