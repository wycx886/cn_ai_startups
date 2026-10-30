# 本地个人工作流

cn_ai_startups 分享规则、模板和公共资料。每个使用者的个人事实、简历、联系人和投递进展属于自己的本地工作区。

## 初始化

在仓库根目录运行：

```bash
python3 scripts/init_local.py
```

初始化只复制空白模板，重复运行保留已有内容。它不会读取其他职业资料库，也不会迁移个人记录。初始化后目录如下；这些目录全部被 `.gitignore` 排除：

```text
local/
  README.md
  profile.md          本人的事实基准
  preferences.md      本人的方向、约束与授权
  resumes/            本人简历及附件
  drafts/             本人材料草稿
applications/
  AGENTS.md           本地记录规则
  README.md           进度总览
  <organization-id>/
    log.md            有实际任务时才创建
  inbox/              待核实或待合并的补充
  archive/            已结束的记录
  headhunters/        本人的猎头沟通记录
```

这些路径不会出现在 GitHub；仓库中只保留 [空白模板](../templates/README.md)。只研究公司时可以不初始化；需要个人任务时补充所需字段即可，不要求一次填完整份履历。

## 每次任务

1. 读根目录 [AGENTS.md](../AGENTS.md)，以及本人 `local/profile.md`、`local/preferences.md`。个人事实以使用者提供的材料为准；发现冲突时保留原文并核实，不选择对自己更有利的版本。
2. 读本地 `applications/README.md` 和相关组织日志，检查归档、“不再接触”、已有联系人及岗位，避免重复投递。缺少组织身份时先记 `inbox/`。
3. 按需查公共索引与单条 JSON。公共公司的核查日期不等于岗位今天仍开放；需要联系或投递时重查对应渠道，不猜邮箱。
4. 新组织优先用公共资料 `id` 作为稳定目录名；库外组织另设稳定名称。复制 [application-log.md](../templates/application-log.md) 到 `applications/<organization-id>/log.md`。每个联系人或岗位设置独立联系线。
5. 仅生成材料时，使用 [outreach-draft.md](../templates/outreach-draft.md)，保存在 `local/drafts/` 或组织目录，状态为草稿。实际发送、平台操作或预约须在已有明确授权范围内执行；模板和仓库不自动授权。已有授权可以继续使用。
6. 真实动作、使用者确认或新回复到达后，追加日志并同步本地总览。每条包含实际发生日期、时区、渠道、联系人、岗位、事实依据、下一步及期限；补录时另写记录日期。不把推测写成承诺，不把草稿写成已投递。
7. 某一联系线结束只关闭该联系线；全部结束后可归档，保留结果与原因。保留历史记录，不靠删除历史来清理总览。

有新的沟通原文时，可先用 [communication-note.md](../templates/communication-note.md) 记录，再合并事实。没有明确的跟进授权时，只给建议或准备草稿。日历和提醒需要使用者提出相应需求。

## 多 Agent 协作

协调 Agent 先分配组织范围。不同组织可并行整理；同一组织的补充先分别新建 `applications/inbox/<日期>-<agent>-<主题>.md`，保留来源与实际时间，再由协调 Agent 核实、合并到公司日志和总览。不要同时编辑同一份日志，也不要用另一个 Agent 的推测作为事实依据。

公共研究可以独立贡献到 `data/`；从个人沟通中得知的未公开信息留在本地。私人简历、原文、附件、薪酬、账号信息和授权记录不得复制到公共文件或远端讨论。同步方式见 [git-sync.md](git-sync.md)。
