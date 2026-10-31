# 私人工作区与记录流程

共享仓库保存框架、公共资料和空白模板；私人工作区保存当前使用者的履历、简历、联系人和投递进展。每个使用者只维护一套个人档案。

## Fork 用户：创建本地工作区

在克隆的仓库根目录执行：

```bash
python3 skills/setup-workspace/scripts/init_local.py
python3 skills/setup-workspace/scripts/workspace.py --json
```

初始化创建被忽略的 `workspace/`，重复运行不覆盖已有文件，不从其他目录推断或导入个人事实：

```text
workspace/
  AGENTS.md
  README.md
  profile.md
  preferences.md
  resume/
  drafts/
  applications/
    AGENTS.md
    README.md
    <organization-id>/log.md    有实际任务时才创建
    inbox/done/
    archive/
    headhunters/
```

Fork 的 GitHub 内容只包含框架和空白模板，私人工作区由使用者的 Agent 在本地创建。公开公司、招聘渠道与岗位研究不必初始化或填写个人信息，核实后直接维护共享 `data/companies/`，不经过私人 inbox。

## 已有私人工作区：只绑定，不复制

已有工作区至少应包含 `profile.md` 和 `preferences.md`：

```bash
python3 skills/setup-workspace/scripts/init_local.py --workspace ../my-private-workspace --use-existing
```

此命令只保存被忽略的 `workspace.local.json`；不创建内部 `workspace/`，不改原有个人文件。Agent 每次通过 `skills/setup-workspace/scripts/workspace.py --json` 读取有效位置，遵循该工作区自己的 `AGENTS.md` 和文件组织。个人工作区不能指向仓库本身、其父目录或仓库中的共享目录。

如旧版本已存在 `local/`、根目录 `applications/`，先核对和归拢已有资料，再绑定；初始化会阻止在这些旧目录旁悄悄新建第二套空白工作区。用户用云端 Agent 时，应把同一工作区放在其账号下的私有持久存储；Git 忽略本身不提供跨会话备份。

## 每次个人任务

1. 读共享仓库 [AGENTS.md](../../../AGENTS.md)，解析有效工作区，再读本人事实、偏好与既有规则。只询问当前任务缺少的信息，不要求先补全所有字段。
2. 读工作区的投递总览、归档和目标组织日志，检查已有联系人及不再接触要求，避免重复联系。
3. 按需读取公共索引和单条 JSON。公共核查日期不代表岗位今天仍开放；准备联系时实际重查渠道，不猜邮箱。
4. 一家组织一个稳定目录；优先沿用既有目录名，新目录可采用公开资料 ID。每个岗位或联系人设置独立联系线。
5. 草稿放 `drafts/` 或组织目录；简历代码与附件放 `resume/`。实际发送、投递或预约依照使用者明确授权范围执行；仓库和模板本身不授权。
6. 真实动作或新回复到达后，追加组织日志并同步总览。保留实际日期、时区、记录日期、渠道、联系人、岗位、依据和下一步。补录不改写事件日期，不把猜测写成承诺。
7. 一个联系人结束只关闭该联系线；全部结束或使用者明确决定后可归档，保留原因和历史。

新记录使用 [日志模板](../assets/templates/application-log.md)、[沟通模板](../assets/templates/communication-note.md) 或 [草稿模板](../assets/templates/outreach-draft.md)。保留原始材料作为事实依据，处理完成的 inbox 记录移到 `inbox/done/`，不重复生成同一进展。

## 多 Agent 与同步

个人投递与沟通由协调 Agent 按组织分工，同一组织的个人进展补充写入私人 `applications/inbox/` 后合并。公开公司、招聘渠道和岗位研究直接更新共享仓库 `data/companies/`，不走私人 inbox，也无需初始化私人工作区；按公司分配一个写入者，避免并发覆盖。从个人沟通获知的未公开事实留在私人工作区。原文、附件、薪酬、凭据与授权记录不得复制到共享文件和远端讨论。共享提交见 [../../../tools/README.md](../../../tools/README.md)。
