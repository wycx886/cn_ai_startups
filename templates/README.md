# 空白模板

这里提交通用结构。使用者或 Agent 复制到被忽略的本地目录后填写，不把模板改成真实个人档案。

| 模板 | 本地用途 |
| --- | --- |
| [profile.md](profile.md) | 本人的事实基准，初始化到 `local/profile.md` |
| [preferences.md](preferences.md) | 本人的目标与约束，初始化到 `local/preferences.md` |
| [local-guide.md](local-guide.md) | 本地资料说明，初始化到 `local/README.md` |
| [applications-agent-rules.md](applications-agent-rules.md) | 初始化到 `applications/AGENTS.md` |
| [applications-index.md](applications-index.md) | 初始化到 `applications/README.md` |
| [application-log.md](application-log.md) | 有实际任务时复制到 `applications/<organization-id>/log.md` |
| [communication-note.md](communication-note.md) | 具体沟通补充，保存在组织目录或 `applications/inbox/` |
| [outreach-draft.md](outreach-draft.md) | 未发送的联系草稿，保存在 `local/drafts/` 或组织目录 |

在仓库根目录运行 `python3 scripts/init_local.py` 可初始化空白工作区；重复运行不覆盖已有记录。实际维护遵循 [Agent 规则](../AGENTS.md) 和 [本地工作流](../docs/application-workflow.md)。
