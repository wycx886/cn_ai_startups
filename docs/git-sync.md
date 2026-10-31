# 本地 Git 与共享同步

本仓库有自己的 `.git/`。保存只是本地修改，提交记录修改，推送才上传到配置的 GitHub 远端。即使本仓库放在私人父目录中，也只同步这个独立子仓库。

## 同步边界

| 内容 | 位置 | 上传 GitHub |
| --- | --- | --- |
| 通用规则、方法、空白模板、工具和检查 | 根入口、`skills/`、`docs/`、`templates/`、`scripts/`、`tests/` | 是 |
| 正式公开事实、来源、第一波标记和数据契约 | `data/`、`schemas/` | 是 |
| 由正式记录生成的阅读版和 CSV | `catalog/` | 是 |
| 本人的事实、偏好、简历、草稿、聊天与投递 | 本地 `workspace/` 或配置的外部工作区 | 否 |
| 未核实的研究候选与采集批次 | 私人 `drafts/research/`、`research/inbox/` | 否 |
| 私人工作区位置 | `workspace.local.json` | 否 |

公开 Layer 2 企业主页核实后进入所属机构的 JSON，不会因为它最初来自私人采集工作区就永远留在私人目录。只有筛选后的公开字段可晋升，私人对话和联系进展继续留在个人工作区。`data/` 是正式维护源，`catalog/` 自动生成，详见 [数据模型](data-model.md)。

## 提交前

查看实际差异，确认来源、第一波标记、日期和共享范围正确：

```bash
git status --short
git diff
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/publish.py --message "更新公共资料"
```

工具会生成阅读版和索引，校验公开数据与链接，运行测试，检查 Git 根目录及共享边界，最后仅暂存共享目录、提交和普通推送。检查失败即停止；不自动强制推送或合并远端冲突。只检查可用 `scripts/publish.py --check-only`。

其他使用者先 Fork 或使用自己的远端；克隆原仓库不自动获得写入权限。用 `git remote -v` 确认目标。提交信息、Issue 和 PR 同样不能带入个人内容。

## 忽略与检查

```bash
git check-ignore workspace/profile.md workspace.local.json
.venv/bin/python scripts/check_public.py
```

当前共享目录为 `.github/`、`catalog/`、`data/`、`docs/`、`schemas/`、`scripts/`、`skills/`、`templates/`、`tests/`，根文件以检查脚本名单为准。旧版 `companies/`、`investors/`、`exports/` 和根 `taxonomy.md` 只在历史审计中兼容。

内部 `workspace/` 整体忽略；配置的外部私人工作区不在 Git 根目录内。旧 `local/`、根 `applications/` 等忽略规则继续保留，避免旧使用者升级时误上传。不要用强制添加绕过忽略。

检查可拦住私人目录、路径配置、常见凭据和个人电脑目录，但不能识别所有姓名、电话和聊天，仍要审阅实际内容。忽略也不会清除已提交历史；发现历史私人内容时停止推送，先评估清理，不擅自改写历史。

不要在私人父目录初始化或整体推送 Git。子仓库 `.git/` 缺失而误用父仓库时，根目录检查应停止。GitHub 不备份被忽略的个人工作区；需要备份时使用本人可访问的私有持久存储。
