# 本地 Git 与共享同步

克隆目录有自己的 `.git/`。保存是本地修改，提交记录修改，推送才上传到配置的 GitHub 远端。即使仓库放在私人父目录中，上传范围也只能是这个独立仓库。

## 内容边界

| 内容 | 位置 | 同步 GitHub |
| --- | --- | --- |
| 规则、通用流程、空白模板、工具、检查 | 根目录入口、`docs/`、`templates/`、`scripts/`、`tests/` | 是 |
| 有来源的公开事实、数据契约 | `data/`、`schemas/` | 是 |
| 自动生成的阅读版与 CSV | `catalog/` | 是 |
| 本人事实、简历、草稿、沟通与投递 | 本地 `workspace/` 或配置的外部工作区 | 否 |
| 私人工作区位置 | `workspace.local.json` | 否 |

只有一套有效个人工作区；绑定方式见 [工作流](application-workflow.md)。模板始终保持空白，不把个人资料回填进去。外部个人目录不在本仓库 Git 范围内；内部 `workspace/` 整体忽略。旧版本的 `local/`、根 `applications/` 等忽略规则继续保留，避免历史使用者升级时误上传。

## 提交共享修改

先查看差异，确认没有私人内容：

```bash
git status --short
git diff
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/publish.py --message "更新公共资料"
```

工具重新生成 `catalog/` 和机器索引，校验数据与链接、运行测试、检查 Git 根目录和共享边界，仅暂存共享目录后提交并普通推送。检查失败即停止，不自动强制推送或合并冲突。只检查可使用 `scripts/publish.py --check-only`。

其他使用者先 Fork 或使用自己的远端；克隆原仓库不会自动获得写入权限。确认 `git remote -v` 指向自己有权维护的仓库。提交信息、Issue 和 PR 同样不能含有个人细节。

## 上传前检查

```bash
git check-ignore workspace/profile.md workspace.local.json
.venv/bin/python scripts/check_public.py
```

检查只允许共享根文件及 `.github/`、`catalog/`、`data/`、`docs/`、`schemas/`、`scripts/`、`templates/`、`tests/`。旧版 `companies/`、`investors/`、`exports/` 和根 `taxonomy.md` 仅在历史路径审计中兼容，不再作为当前文件入口。

私人目录、配置、环境文件、邮件草稿即使被强行加入，也会被检查拒绝。检查还识别当前暂存内容中的常见凭据与个人电脑目录，但不能识别所有姓名、电话、履历和聊天，仍需审阅实际差异。

忽略不会清除已提交的内容或历史；检查到历史私人路径时停止推送，先评估清理范围，不擅自改写历史。不要在私人父目录运行 `git init` 或整体上传；子仓库 `.git/` 缺失而误用父仓库时，根目录检查会拦截。

GitHub 不备份被忽略的个人工作区。若需要备份，应使用本人可访问的私有持久存储；不要为备份而将私人目录强行加入共享 Git。
