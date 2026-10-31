# 机构分类与案例归因参考

## 主分类与第二维度

第一波以新进玩家为主：`targeting.player_group` 为 `new_entrant`，当前候选进入 `wave: first`；资料不足的候选保留 `watchlist`。已有玩家进入后续范围，无法可靠判断时用 `unresolved` 并保留理由。

经营型机构和投资机构是第二个维度。它们分别需要产品／融资或投资策略／团队／案例字段，但共享公开渠道和后续机会记录方法。不把统一年份、上市状态或有无 VC 资金当作唯一门槛。

编辑分类不等于已核实的成立年份、当前法律独立性或投资价值结论，`labelled_at` 与原事实 `checked_at` 分开。

## 经营型机构赛道

赛道名称、边界和子类的唯一维护源是 [data/taxonomy.json](../../../data/taxonomy.json)，阅读版是 [catalog/taxonomy.md](../../../catalog/taxonomy.md)。这里不复制第二套表格，避免分类更新后分叉。

现有方法参考 Sequoia、a16z 和 HongShan 的公开材料，由本资料库编辑采用具体组织方式，不是这些机构共同发布的官方 AI 分类标准。原始观点、采用范围和局限见分类 JSON 中的 `references`、`method` 和 `caveats`。

## 投资机构归因

新团队识别见 [新进 VC SOP](new-vc-spinouts.md)，完整披露边界见 [VC 方法](../../../docs/investor-methodology.md)。

- `prior_firm`：投资人／团队在原机构的案例。原平台的知名案例不能自动记成新机构业绩，参与也不自动等于主导。
- `current_firm`：可归属于当前投资机构的案例；并不等于某一只基金的投资。
- 成立、管理人登记、首期基金设立或首关、品牌更名、独立运营各自记录口径。
- IPO、后续融资、账面估值和已实现退出分别说明；没有公开 DPI／IRR 时不推算。

现有 cohort 是历史描述性分组，由 `group`、`founded.year` 派生；它不作为第一波新进判断的年份门槛。`coverage.role` 表示主要样本、观察或相邻范围，也不是收益评级。缺少成熟退出不是新 GP 被排除的理由。
