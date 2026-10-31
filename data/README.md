# 数据字段、第一波标记与公开渠道

公共记录是有来源的研究资料；个人偏好、简历、联系人聊天和投递状态保存在配置的私人工作区，见 [本地工作流](../skills/setup-workspace/references/workflow.md)。

## 正式记录与生成内容

`data/companies/`、`data/lists/` 和 `data/taxonomy.json` 保存正式、可维护的 JSON；`data/views/` 是由这些 JSON 生成的人类阅读版和 CSV。同一条记录不在两处分别维护。

例如修改 `data/companies/hypershell.json` 后运行 `python3 tools/build.py`，生成 `data/views/companies/hypershell.md`、汇总 CSV 与索引。生成的机构数量、分类和名单以当前 JSON 计算，README 不重复维护一份数字清单。

| 位置 | 职责 |
| --- | --- |
| `data/companies/*.json` | 所有完整公司／机构档案，包括经营型机构、投资机构及单列的研究单元 |
| `data/taxonomy.json` | 经营型机构赛道的编辑分类定义 |
| `data/lists/vcs.json` | 沿投资组合与投资公告寻找新机构的参考名单；引用 `companies/` 的稳定 ID 与来源，不复制完整档案 |
| `data/lists/incumbents.json` | 当前中国 AI 的已有玩家／母平台寻源底表、行业标签与主题证据；不计入正式机构目标 |
| `data/index.json` | 唯一自动生成的机器索引，schema version 4；`organizations` 同时收录经营型机构和投资机构 |
| `data/views/first-wave.md` | 自动生成的第一波与观察候选阅读版 |
| `data/views/incumbents.md` | 自动生成的母平台排查清单；官网身份核对不等于项目核验 |
| `data/views/corporate-ventures.md` | 已有 `organizational_context` 标注的经营型记录阅读版 |
| `data/views/later.md` | 已有玩家的现有资料登记；保留研究批次，不禁止后续研究 |
| 其他 `data/views/` 与统一机器索引 | 自动生成的明细、分类、CSV 和检索入口 |

仓库更名保留既有 schema URN 标识，兼容旧读取器；文件入口采用新名称。经营型／投资机构采用 schema version 2；契约见 [company.schema.json](schemas/company.schema.json) 和 [investor.schema.json](schemas/investor.schema.json)。分类文件保留自己的版本约定，见 [taxonomy.schema.json](schemas/taxonomy.schema.json)。


机器索引只维护 `data/index.json`。`organizations` 中的每项用 `organization_type` 区分类型，并提供稳定 ID、名称／别名、业务、标记、实际核查日期、原始 JSON 路径与阅读版路径；保留各类型的赛道、融资状态、团队、案例归因等摘要。`counts.companies` 与 `counts.organizations` 都是全部档案数，`operating_organizations`／`investment_firms` 才是类型分项；`statistics` 同样按这两种类型汇总。索引与阅读版均由 `tools/build.py` 生成，不手改，也不替代带完整来源的单条记录。

## 名单与完整档案

`data/lists/` 放可被不同 Skill 共用的发现入口；Skill 只说明查找方法与读取路径。`vcs.json` 的每个条目包含 `company_id`、`source_ids` 和 `discovery_use`，通过 `company_id` 读取 `data/companies/<id>.json` 的名称、官网、来源和真实核查日期。作为寻源入口与作为研究目标是不同用途，同一家 VC 只维护一份完整档案。条目来源必须是所引用公司的业务证据，不能只凭招聘渠道入表。

`incumbents.json` 保留已有玩家底表的 `platforms` 数组及其 ID、别名、访问范围与主题证据；这些种子不自动成为完整目标。如果需要完整研究或 Layer 2／3，为对应机构建立 `companies/` 档案，并复用可确认的稳定身份。

原来 `data/investors/<id>.json` 的完整资料现统一位于 `data/companies/<id>.json`；原 `data/platforms.json` 改为 `data/lists/incumbents.json`。Agent 先读当前 `data/index.json` 获取路径，勿拼接旧目录。索引 v4 的 `counts.companies` 从经营型数量改为全部公司数量，类型分项与 `statistics` 改用 `operating_organizations`／`investment_firms`；分项日期相应为 `latest_operating_check`／`latest_investment_firm_check`。

## 第一波与机构类型

主分类是新进玩家与已有玩家，经营型机构／投资机构是第二个维度。新进不是固定年份阈值，也不由上市状态或 VC 融资单独判断；成熟机构品牌变化不自动成为新进机构。

有明确边界的大厂内部新团队、实验室、孵化项目、子公司或正式拆分机构可以是新进候选，其母平台仍是已有玩家。离职团队创业也可研究，但不能仅凭履历认定它是母平台孵化或拆分。成熟平台和现有业务由 [find-incumbents](../skills/find-incumbents/SKILL.md) 研究；真正的新进单元交给 [find-startups](../skills/find-startups/SKILL.md)。实际边界按 [大厂项目 SOP](../skills/find-incumbents/references/corporate-ventures.md) 留存证据，两个 Skill 不复制机构记录。

`targeting` 的字段如下：

| 字段 | 含义 |
| --- | --- |
| `kind` | 固定 `editorial_assessment`，说明这是编辑性研究判断 |
| `player_group` | `new_entrant`、`incumbent`，或证据不足的 `unresolved` |
| `wave` | `first` 第一波研究候选、`watchlist` 待核实、`later` 既有玩家资料批次；不是禁止研究或优劣排序 |
| `rationale` | 纳入、观察或留待后续的具体理由，不写个人岗位偏好 |
| `source_ids` | 本条记录内支撑判断的来源 ID |
| `labelled_at` | 实际做分类标记的日期，不表示业务事实重新核查 |

第一波不是机构质量、基金收益、法律独立性或个人适配的评分。`coverage.role` 继续表示 VC 研究范围与证据口径，不能直接替代第一波标记；例如新 GP 没有成熟退出，不因此失去寻源价值。新 VC 的判断流程见 [专门 SOP](../skills/find-startups/references/new-vc-spinouts.md)。

## 机构事实与来源

| 字段 | 含义 |
| --- | --- |
| `id` | 稳定小写 ASCII ID，与 JSON 文件名一致；改品牌时保留 ID |
| `name`／`aliases` | 当前整理名称、别名及历史名称，不单凭旧名称确认运营主体 |
| `category_id`、`focus`、`products` | 经营型机构的主赛道、业务和交付方式 |
| `locations_text` | 公开城市记录，保留总部、团队或招聘地等限定 |
| `comparison` | 编辑分析和比较对象，不表示性能排名或完整竞争清单 |
| `investment` | 经营型机构的历史投资披露、未确认范围与核验状态 |
| `organizational_context` | 经营型记录可选的组织形式、母平台关系及核验信息；缺失不表示独立 |
| `founded`、`team` | 投资机构的成立口径、团队与原平台 |
| `representative_cases` | 投资机构案例；`prior_firm` 与 `current_firm` 归因分开 |
| `contacts` | 既有公开入口，保留用途与备注，兼容旧消费者 |
| `channels` | 有明确归属、用途、来源和独立核查日期的结构化公开渠道 |
| `notes` | 主体冲突、历史用途、证据缺口和口径限制 |
| `checked_at` | 业务事实实际核查日期；编辑标记、导入和格式迁移不刷新它 |
| `sources` | 来源 ID、URL、标题、支持内容、公开日期、实际核查日期；渠道专用来源可标 `scope: "channel"` |
| `provenance` | 原始图谱名称等导入信息，不等同现行分类或已核事实 |

来源的 `published_date` 可为年、年月或年月日；未知用 `null`，不能用抓取或合并日期代替。业务来源和渠道来源的核查日期分别保留，不自动为未访问的网页刷新日期。

`sources[].scope` 为 `organization` 或 `channel`；兼容旧记录时，省略表示 `organization`。仅核验渠道的新增来源写 `channel`，不能用它支撑投资案例或刷新整条机构业务资料的日期。

融资披露状态：

| 状态 | 含义 |
| --- | --- |
| `confirmed_disclosure` | 当前融资摘要有公开披露支持；不表示完整现股东名册或仍持有 |
| `partial` | 有部分支持，仍有冲突、范围限制或未确认关系 |
| `not_found` | 已开展研究但未找到可靠披露；不是未研究，也不表示零融资 |
| `not_applicable` | 有证据确认的内部团队、实验室或产品项目不适用独立机构股权融资字段；不表示没有内部经费 |

自筹、众筹、创始人支持、产业收购、国资或战略融资等限定逐条保留，不能统一标成 VC-backed。投资机构的完整字段与案例边界见 [VC 方法](../skills/find-startups/references/investment-cases.md)。

## 大厂关联项目与母平台底表

`organizational_context` 是经营型记录上的可选对象。现有记录没有这个字段时，只表示未完成该项标注，不能推断为独立机构。`form` 与第一波标记分别维护，不按母公司的 `incumbent` 身份自动决定项目归类。

| 字段 | 含义 |
| --- | --- |
| `form` | `independent_organization`、`corporate_spinout`、`corporate_subsidiary`、`internal_team`、`research_lab`、`product_project` 或 `unresolved` |
| `parent_platform_ids` | 关联 `data/lists/incumbents.json` 的有证据的当前或历史母平台 ID；仅曾雇佣创始人不构成母平台关系，具体口径由摘要说明 |
| `relationship_status` | `confirmed`、`reported` 或 `unresolved`；媒体报道不升级为官方确认 |
| `summary` | 说明组织边界、当前／历史关系及证据限制；不补造独立性或持股比例 |
| `source_ids` | 本机构记录内支撑关系判断的业务来源 ID，不能用渠道专用证据替代 |
| `checked_at` | 该项关系实际核查日期，不自动刷新其他旧业务事实 |

内部项目和实验室不以外部 VC 融资为纳入前提。融资未披露、主体不清或关系有争议时说明已核查范围；不能据此把内部预算写成融资，也不能把 `corporate_spinout` 标签当成完全脱离母公司控制的证明。

`investment.verification_status: "not_applicable"` 仅用于 `organizational_context.form` 为 `internal_team`、`research_lab` 或 `product_project`，且 `relationship_status: "confirmed"` 并有来源支持的记录。未确认的内部归属、子公司、独立机构或报道中的拆分机构不能据此跳过融资研究；原记录状态不会因整理或新增字段而批量改变。

`data/lists/incumbents.json` 保存当前中国 AI 场景的编辑性排查范围。`group` 为 `internet_platform`、`cloud_ict_adjacent`、`software_and_ai`、`hardware_and_semiconductors` 或 `industry_incumbents`；这是寻源分组，不是统一市场排名，也不将它们全部称为 hyperscaler。可选 `sectors` 为筛选标签，不替代正式档案的业务分类。

官网身份入口只支持识别候选。可选 `topic_evidence` 逐条保存 `topic`、`role`、`title`、`url`、`supports`、`published_date`、`checked_at`，说明在某个主题中的具体角色及来源；发布日期未知用 `null`，核查日期按实际访问记录。存在一项主题证据不表示已确认行业领先、母子公司关系或全部业务。没有该数组表示尚未记录主题证据，不表示确定没有相关业务。

`python3 tools/query_lists.py --list incumbents` 可用 `--sector`、`--topic`、`--group`、`--id` 筛选底表。平台进入底表不会自动进入 `data/index.json`；确定需研究的机构或具体单元后，按正式记录核验、建档和圈选。生成的 [平台清单](views/incumbents.md) 与 [大厂关联项目](views/corporate-ventures.md) 分别承担这些用途。

`python3 tools/query_lists.py --list vcs` 将 VC 名单与完整档案关联后输出；名单增删不会自动新增或删除完整公司档案，VC 名单可以为空。`views/exports/companies.csv`／`sources.csv` 为经营型资料筛选表，`investors.csv`／`investor-sources.csv` 为投资机构筛选表；它们都是统一档案的自动生成视图。

## 通用 Skill 与当前公共契约

`find-startups` 和 `find-incumbents` 的主题、地域和行业由具体任务确定；本仓库现有公共分类与 schema 则继续服务当前中国 AI 资料。通用方法不等于当前数据契约已经扩展到所有行业。超出既有分类的结果先存私人工作区 `research/`，或在明确扩展 taxonomy、schema 和生成规则后发布，不能借用一个不相符的 AI 类目来通过校验。研究流程和第三方参考见 [研究方法](../skills/find-incumbents/references/research-methods.md)。

## 三类公开渠道

三类是入口类别，不表示渠道之间有高低优先级，也不预设个人职能方向。

| `layer` | 典型信息 |
| --- | --- |
| `official` | 官网、官方招聘或业务页面等，经核实的机构正式入口 |
| `recruitment_platform` | 机构在 BOSS 直聘、猎聘、脉脉上的公开企业主页 |
| `professional_social` | 机构账号，或有公开专业身份依据的个人主页 |

每条 `channels` 记录包含：

| 字段 | 含义 |
| --- | --- |
| `id` | 本机构内稳定渠道 ID |
| `layer`／`platform` | 渠道类别及具体平台 |
| `url`／`purpose` | 公开入口及用途；招聘、BP、商务等目的分开 |
| `owner.scope`、`owner.name`、`owner.role` | 归属机构或公开专业人物；未知项不猜测 |
| `verification_status` | `confirmed`、`partial` 或 `historical`；不是招聘开放状态 |
| `checked_at` | 实际核对该页面和归属的日期 |
| `source_ids` | 本机构内对应证据来源 ID |
| `notes` | 适用范围、历史性或其他公开事实限定 |

`contacts.careers_url` 可能是官方页、招聘平台或历史帖子，不能一律计为 Layer 1。`sources` 中引用了 GitHub、X 或领英网址，也不能由域名推断它就是该机构或负责人的渠道。结构化覆盖率按已核实的 `channels` 计算，既有未结构化信息另作提示。

## 从候选到正式记录

新机构草稿先输出到标准输出，或显式保存到私人 `drafts/research/`；缺失事实和日期保留 `null`，不创建虚假的来源。核实后才写入正式 `data/`，发布检查拒绝占位内容和示例网址。

Layer 2 按 [渠道方法](../skills/find-channels/SKILL.md) 核对公开企业主页，采集 Agent 将已核实结果直接更新到 `data/companies/<id>.json` 的 `channels` 与 `sources`。可直接编辑后校验，也可将观察结果经标准输入交给 `update_layer2.py --apply`；不要求先落盘批次、私人工作区或 inbox，也不要求另一个 Agent 批准。未找到、访问受限或主体存疑在本次研究报告说明，不补造已确认记录。`applications/inbox/` 只处理个人投递、聊天和进展；原始聊天、私人联系方式、个人期望薪酬及投递状态不得进入公共资料。

每次正式变更先校验，再生成阅读版，最后检查同步与差异：

```bash
.venv/bin/python tools/validate.py
python3 tools/build.py
.venv/bin/python tools/validate.py --check-generated
```

结构与日期校验不能代替实际网页核验，也不能证明岗位仍开放、邮箱仍有效或披露完整。
