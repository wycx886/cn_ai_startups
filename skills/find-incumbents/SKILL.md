---
name: find-incumbents
description: Discover and verify established players in a specified market, including major platforms, software vendors, hardware and infrastructure suppliers, mature investment firms, and cross-industry operators. Use for finding incumbents, existing players, large companies, market leaders, mature AI businesses, or relevant business teams. Take geography, theme and sectors from the task, not a permanent AI or China filter. Establish market presence and topic relevance separately; do not infer leadership from size, age, listing or marketing claims. Route genuinely new ventures to find-startups.
---

# Find Incumbents · 已有玩家寻源

寻找指定市场中已经持续开展业务、有产品或交付基础的机构，并下钻到实际相关的业务单元。Incumbent 是相对市场位置，不等于互联网大厂、所有大公司或市场第一名。本方法不限 AI、互联网、中国或上市公司。

## 1. 定义任务与“头部”口径

读取 `geography`、`market_or_theme`、`sectors`、`as_of`、`purpose` 和研究单位。采用当前任务的优先级；例如本次中国 AI 研究以互联网为主，同时覆盖软件、硬件与相关行业，而不是永远只找互联网。

用户若要求“头部”，先确定细分市场和可核查标准，例如持续产品／服务、客户或装机基础、公开收入／出货、技术与研发活动。未给指标时输出“已有玩家候选”及纳入依据，不把公司规模、成立年份、上市、融资或自称领先直接转换为排名。

## 2. 按产业角色扩展候选池

从已知公司、官方行业图谱、监管与交易所资料、公开供应商／客户关系扩展，至少考虑任务相关的下列角色：

- 平台与软件：互联网、企业软件、成熟技术供应商。
- 基础设施：云、计算、芯片、服务器、网络、终端与硬件。
- 行业运营商：制造、汽车、消费、医疗、金融等已有集团和专业机构。
- 成熟投资机构：已形成持续投资业务的管理机构及相关团队。

硬件与软件可以交叉标记。厂商、基础设施供应商和将技术用于自身业务的采用者分别记录；“使用某技术”不是“在该技术领域领先”的证明。行业图谱、备案与榜单只是线索，各有收录标准和时间，不当作完整市场全集或自动能力认证。

## 3. 逐家核实两个问题

**它在哪个市场是已有玩家？** 用最新年报、公告、IR、产品与交付／客户材料核实当前持续经营与实际市场活动，保留集团、法人、品牌和业务单元的层级。

**它为什么与当前主题相关？** 核对具名产品、服务、研发单元、公开成果或具体部署。一次合作、招聘描述或营销口号可以成为线索，不能自动升级成持续能力或现行招聘机会。历史战略资料注明日期，不能代替当前状态。

优先一手资料，再用可靠报道补充；单独记录事实、推断、争议与缺口，访问失败就保留未知。市场地位、主题活动、组织归属与实际核查日期分别有依据。

## 4. 从机构下钻到具体单元

按集团 → 法人／业务群 → 产品／实验室／团队定位实际对象。集团规模不代表每个团队的业务规模或招聘状态；一个模型、实验室与品牌也不应重复计成三家公司。

组织归属遵循 [共同 SOP](references/corporate-ventures.md)。若发现有明确新目标与活动证据的新孵化项目、正式拆分或新独立机构，交给 [find-startups](../find-startups/SKILL.md) 判断新进定位；母平台和具体单元可由不同方法研究，但共享同一正式事实源，不复制两套档案。成熟常规业务继续由本 Skill 研究。

## 5. 输出与保存

每项至少包含：机构／单元、市场与地域、产业角色、已有业务依据、主题相关证据、具体组织层级、来源／公开日期／核查日期、未确认事项。按产业角色或细分市场展示；除非任务与证据支持，不强制 Top N 排名。

方法通用，输出契约由项目决定。本仓库的中国 AI 示例见 [可选附录](references/china-example.md)，第三方研究方法比较见 [方法说明](references/research-methods.md)。

在本仓库内，先读取 `data/lists/incumbents.json`、`data/views/incumbents.md` 和 `data/index.json`。研究成熟基金时也读取 `data/lists/vcs.json`，按完整档案的类型与已有玩家标记筛选。两个名单是共用数据；正式档案及来源统一在 `data/companies/`。平台底表是发现线索；底表不自动成为目标、母公司或“AI头部”证明。缺少主题证据不是证实没有相关业务。

```bash
python3 tools/query_lists.py --sector hardware
python3 tools/query_lists.py --topic AI
python3 tools/query.py --entity organizations --player-group incumbent
python3 tools/scaffold_entity.py --entity investor --id candidate-manager --name "待核实机构" --group established --player-group incumbent
```

当前公共数据契约以中国 AI 机会为主题。超出主题的任务先输出到私人研究工作区，或按明确任务扩充分类／契约，不虚构 AI 赛道。草稿不直接晋升正式记录；已有档案更新同一稳定 ID，成熟玩家使用相应编辑标记，不因换 Skill 就批量重分类或刷新旧事实日期。

```bash
.venv/bin/python tools/validate.py
python3 tools/build.py
.venv/bin/python tools/validate.py --check-generated
```

不自动采集 Layer 2／3 或触达他人。公开事实与入口可以进入公共记录；个人偏好、简历、薪酬、联系人对话与投递进展只留私人工作区。渠道维护另用 [find-channels](../find-channels/SKILL.md)。
