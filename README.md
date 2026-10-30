# cn_ai_startups

面向 Agent 的职业研究与跟进框架，附带有来源的中国 AI 公司和 VC 资料。公司按业务分类，框架不预设使用者的个人背景或求职偏好。

## 从这里开始

| 需求 | 入口 |
| --- | --- |
| Agent 工作规则 | [AGENTS.md](AGENTS.md) |
| 公司、VC、分类与公开渠道 | [资料目录](catalog/README.md) |
| Agent 轻量索引 | [公司](data/index.json) · [VC](data/investor-index.json) |
| 公开事实的唯一维护源 | [data/](data/) |
| 空白个人模板 | [templates/](templates/README.md) |
| 初始化与记录流程 | [本地工作流](docs/application-workflow.md) |
| 上传范围与隐私边界 | [Git 同步](docs/git-sync.md) |
| 字段与来源口径 | [数据模型](docs/data-model.md) · [VC 方法](docs/investor-methodology.md) |
  | 逐项来源表 | [公司来源](catalog/exports/sources.csv) · [VC 来源](catalog/exports/investor-sources.csv) |

## Fork 用户的私人工作区

Fork／Clone 后先让 Agent 读 `AGENTS.md`，再运行：

```bash
python3 scripts/init_local.py
```

这会在本地建立一个被忽略的 `workspace/`，包含个人事实、偏好、简历目录、草稿和投递总览。重复运行不覆盖已有内容。个人工作区不会随普通提交上传。

如果已经有自己的私人工作区，直接绑定，不复制另一套资料：

```bash
python3 scripts/init_local.py --workspace ../my-private-workspace --use-existing
python3 scripts/workspace.py --json
```

已有工作区应包含 `profile.md` 与 `preferences.md`。路径只保存在被忽略的 `workspace.local.json`；Agent 每次先解析该配置，再读写个人资料。

## 目录职责

```text
data/        公开公司、VC、分类 JSON；索引由脚本生成
catalog/     自动生成的 Markdown、分类和 CSV
schemas/     公开数据契约
templates/   可复用的空白个人模板
docs/        字段、方法、个人工作流与同步说明
scripts/     查询、生成、初始化和提交检查
tests/       工作区与共享边界验证
workspace/   仅本地的个人资料（可改为外部工作区）
```

本 README 人工维护，不由生成脚本覆盖。`catalog/` 和机器索引由 JSON 生成，不手工编辑。

## 查询与更新公共资料

```bash
python3 scripts/query.py --text Hypershell
python3 scripts/query.py --entity investors --id qiming --json
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
python3 scripts/build.py
.venv/bin/python scripts/validate.py --check-generated
```

公开数据有来源与核查日期，但不保证招聘仍开放、邮箱仍有效或投资披露完整。框架和模板不自动授予发送、投递或联系权限。

## 同步 GitHub

检查共享修改后运行：

```bash
.venv/bin/python scripts/publish.py --message "更新公共资料"
```

工具只暂存共享目录、生成并校验阅读版、检查上传边界，再提交和普通推送。私人工作区、路径配置、简历和投递记录均排除；具体范围见 [同步说明](docs/git-sync.md)。
