# 大平台项目、实验室与拆分团队 SOP

目的：核实可单独研究、pitch 或寻找机会的业务／研究单元及其平台关系。组织归属方法通用；下列中国AI平台与字节案例是当前仓库示例，其他地域或主题按任务替换寻源范围。没有独立法人或外部融资，不应使一个有明确目标的内部项目被自动漏掉。

## 1. 逐个平台排查

当前中国AI场景读取 [已有玩家／母平台机器底表](../../../data/lists/incumbents.json) 或 [阅读版](../../../data/views/incumbents.md)。逐项排查其中主要互联网／软件平台，再覆盖单独列出的云、ICT和终端集团。阿里、腾讯、百度、字节之外，也要看蚂蚁、京东、美团、PDD、快手、网易、小红书、哔哩哔哩、滴滴、旅行平台、内容／知识平台等，不能只凭熟悉程度抽取 BAT。

底表是可扩展的编辑范围，不是完整市场全集。发现遗漏的重要平台时，先核实官方身份入口再补入；访问受限保留真实状态，不冒充已读取。云业务、大型互联网平台、软件公司、电信集团不是同一个概念，不统一打 `hyperscaler` 标签，也不以该标签决定是否排查。

以任务主题替换查询词。当前AI示例可结合平台名称／历史品牌检索：`AI lab`、`AI for Science`、`生物医药`、`drug discovery`、`机器人`、`孵化`、`创新业务`、`内部创业`、`独立运营`、`拆分`、`融资`、`原团队创业`。这些是搜索主题，不预先断言其存在相应项目。

优先看官方实验室和研究页、具名项目官网、官方论文／代码组织、公司公告、监管或登记资料。报道作为补充时，明确其公开披露、记者核实或匿名消息源性质。官网不可读不等于项目不存在。

## 2. 确认单元与组织形态

先确认它叫什么、做什么、由谁运营、属于哪个母平台，以及现在是否仍在开展研究或业务。不要只凭一个模型名、论文、招聘帖子或前员工履历就断言存在独立机构。

| `organizational_context.form` | 使用口径 |
| --- | --- |
| `internal_team` | 母平台内部的具名业务或创业团队 |
| `research_lab` | 有明确归属的研究实验室；不因 Lab 名称推断独立法人 |
| `product_project` | 可识别的产品、研究或孵化项目；不是每篇论文各建一个机会对象 |
| `corporate_subsidiary` | 有证据的独立法人子公司；不等于完全独立或拆分 |
| `corporate_spinout` | 有拆分事实依据的项目／机构；保留控股、资源与资产转移的实际限定 |
| `independent_organization` | 有独立主体依据；前员工创业不等于母公司正式拆分 |
| `unresolved` | 组织边界证据不足，保留待核实 |

`parent_platform_ids` 指向底表。`relationship_status` 分别用 `confirmed`、`reported`、`unresolved`，在 `summary` 说明关系和缺口，并填写实际关系核查日期及本条来源 ID。人物曾任某大厂，不足以填写该机构为现行母公司；前员工创业背景可先写来源支持的备注，不虚构现行控制关系。

旧记录没有 `organizational_context` 表示尚未逐项标注，不表示默认独立。一个项目多个品牌先核对是否同一单元；母公司、实验室、产品、模型和新公司不应全都重复算成新机构。联合项目可关联多个有证据的平台。

## 3. 判断新进或已有，不自动继承母平台身份

成熟平台与常规业务由 [find-incumbents](../SKILL.md)研究；具备新进线索的单元由 [find-startups](../../find-startups/SKILL.md)继续判断。成熟母平台可为已有玩家；新形成、具备具体方向的项目或拆分机构仍可作为新进目标。对已经长期成熟运营的普通部门，不因其包含 AI 就自动标第一波。主体、实际活动或项目新进边界不清时留 `watchlist`，并写清待补问题。

第一波不要求融资、独立注册或固定成立年份。内部资源支持与独立股权融资分开：有明确内部单元证据时，可将独立主体融资字段标 `not_applicable`；拆分机构、子公司和前员工创业不自动适用此值。媒体报道融资仍按证据强度标记，不提升为官方披露。

## 4. 以字节案例校准口径

以下示例核查于 2026-10-31，仅说明识别方法，不表示各项都已纳入第一波：

- [Anew Labs 官网](https://anewbt.com/)确认当前 AI 药研业务；[字节官方 AnewOmni 仓库](https://github.com/bytedance/AnewOmni)支持研究来源关联。[路透原稿转载](https://www.streetinsider.com/Reuters/ByteDance%2Bcompletes%2B%24290%2Bmillion%2Bfundraising%2Bfor%2BAI%2Bdrug%2Bunit%2Bafter%2Bits%2Bspin-off%2C%2Bsources%2Bsay/27066461.html)报道拆分并称母公司仍控股，来自匿名消息源。记录为拆分机构、关系据报道；不能只据官网或官方代码库写成现行股权已获确认。[完整档案](../../../data/views/companies/anew-labs.md)。
- [ByteDance Seed](https://seed.bytedance.com/en/)是官方具名团队入口；不能把它直接改写成独立创业公司。
- [UMO 官方研究页](https://bytedance.github.io/UMO/)列出 UXO Team、Intelligent Creation Lab、ByteDance。团队、实验室和研究项目是不同层级，不能各自自动算成一家新公司。
- [Seed Edge](https://seed.bytedance.com/en/seed-edge)是 Seed 的长期研究计划；研究计划不自动是独立实验室、法人或创业团队。

## 5. 保存并交接

明确可识别的经营／研究单元仍存 `data/companies/<stable-id>.json`，类型为 `operating_organization`，以 `organizational_context` 记录形态与归属。`data/lists/incumbents.json` 只维护母平台寻源入口，不能把未核实的项目偷偷塞进它替代正式记录。

每条交接至少保留：单元 ID、名称／别名、业务目标、组织形态、母平台及关系口径、实际活动证据、第一波理由、融资适用性、来源与缺口。待核实草稿先留私人工作区；正式 JSON 经校验后生成 [大厂项目阅读版](../../../data/views/corporate-ventures.md)。本阶段不采集 Layer 2／3，不发消息或投递。
