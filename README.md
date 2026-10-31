# cn_ai_opp

面向 Agent 的机构研究与机会发现框架。寻源分为 `find-startups` 新进玩家和 `find-incumbents` 已有玩家；主题、地域与行业由任务指定。当前公共资料聚焦中国 AI，样本不是全市场清单或质量排名。

```text
skills/   研究方法、专用脚本与空白模板
data/    正式公共 JSON、字段约束与自动生成的阅读版
tools/   共用查询、构建、校验、发布工具及测试
```

## 从这里开始

| 需求 | 入口 |
| --- | --- |
| Agent 规则与任务路由 | [AGENTS.md](AGENTS.md) |
| 寻找新进机构、创业和新孵化项目 | [find-startups](skills/find-startups/SKILL.md) |
| 寻找已有玩家及其业务团队 | [find-incumbents](skills/find-incumbents/SKILL.md) |
| 核实公开渠道 | [find-channels](skills/find-channels/SKILL.md) |
| 创建或复用私人工作区 | [setup-workspace](skills/setup-workspace/SKILL.md) |
| 公开资料 | [统一机器索引](data/index.json) · [阅读目录](data/views/README.md) · [第一波名单](data/views/first-wave.md) |
| 字段、来源与维护约定 | [data/README.md](data/README.md) |
| 查询、检查与 Git 同步 | [tools/README.md](tools/README.md) |

两条寻源路径共用同一份机构记录。Skill 保存研究方法，`data/lists/` 保存共用参考名单；VC 名单通过 ID 关联完整档案，不另建一套投资机构目录。母平台与具体单元分别判断：成熟集团的新项目可以是新进候选，成熟部门也不会因为改名自动变成 startup。具体组织关系及证据保留在档案中。

## 数据如何流转

完整公共档案统一维护在 `data/companies/`，包含经营型机构和 VC 等金融公司。参考名单在 `data/lists/vcs.json`、`data/lists/incumbents.json`，供 Skill 寻源；分类在 `data/taxonomy.json`。`data/index.json` 和 `data/views/` 自动生成，更新 JSON 后运行 `python3 tools/build.py`。

Layer 1／2／3 的正式公开入口都写在所属机构 JSON 的 `channels`，关联来源和实际核查日期。待核实批次先留私人 `research/inbox/`；核实后的公共字段进入 `data/`。公开入口不表示岗位仍开放，也不授予联系权限。

## 私人工作区

Fork 使用者可创建被 Git 忽略的本地 `workspace/`：

```bash
python3 skills/setup-workspace/scripts/init_local.py
```

已有私人资料时，直接绑定，保持一套档案：

```bash
python3 skills/setup-workspace/scripts/init_local.py --workspace ../my-private-workspace --use-existing
```

个人事实、简历、偏好、聊天和投递进展只留私人工作区；本地路径配置 `workspace.local.json` 同样不上传。空白模板随 [setup-workspace](skills/setup-workspace/assets/templates/README.md) 保存。通用 Skill 超出本库主题的研究先留私人工作区，或在明确扩充数据契约后发布。
