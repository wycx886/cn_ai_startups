---
name: setup-workspace
description: Create a blank ignored private workspace or bind an existing one without copying or overwriting personal records. Use when initializing a fork, locating the active profile/preferences/applications workspace, reusing existing career files, or understanding which templates and local paths belong to a user. Keep personal data and local configuration out of the public repository.
---

# Setup Workspace · 本地私人工作区

每位使用者维护一套私人资料。先检查当前本地配置和已有资料，再选择创建空白工作区或直接绑定。只查询公共资料时，无需创建私人工作区。

## 找到有效工作区

从仓库根目录执行：

```bash
python3 skills/setup-workspace/scripts/workspace.py --json
```

解析被忽略的 `workspace.local.json`；没有配置时默认仓库内的 `workspace/`。若已有外部私人资料，保留原位置，不另建第二套履历或投递记录。私人工作区不能指向仓库本身、父目录或共享目录。

## 创建或复用

首次使用可创建空白本地工作区：

```bash
python3 skills/setup-workspace/scripts/init_local.py
```

模板来自本 Skill 的 [assets/templates](assets/templates/README.md)。重复初始化保留已有文件，真实个人事实由使用者提供，不从岗位要求或示例推断。

已有工作区至少包含 `profile.md` 和 `preferences.md`，直接绑定：

```bash
python3 skills/setup-workspace/scripts/init_local.py --workspace ../my-private-workspace --use-existing
```

`--use-existing` 只保存本地路径配置，不复制模板、不修改原有个人文件。已有旧版本个人目录时先核对整理，避免旁边新建空白档案。完整流程见 [工作区与记录说明](references/workflow.md)。

## 每次个人任务

先解析工作区，再读其 `AGENTS.md`、事实、偏好及相应任务流程；沿用本人既有简历构建与日志组织，不批量套新模板覆盖旧资料。应用日志、沟通补充和未发送草稿模板按实际任务使用。

个人联系方式、简历、薪酬、原始聊天、凭据和投递进展只保存于私人工作区；公共机构事实维护在共享 `data/`。模板本身与框架不授予发送、投递或预约权限，按本人规则和明确授权范围执行。

共享边界与 Git 同步见 [tools/README.md](../../tools/README.md)。
