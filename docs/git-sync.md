# 本地 Git 与 GitHub 同步

本地克隆已经是一个 Git 仓库。保存文件只是修改本地内容；提交记录这次修改，推送才会上传到配置的 GitHub 仓库，不会每次保存自动上传。

## 分享哪些内容

| 本地修改 | 提交与推送 |
| --- | --- |
| 通用 Agent 规则、流程、空白模板、脚本与检查 | 可以，先检查差异 |
| 有出处的公开公司、机构、分类资料 | 可以，先修改 JSON，再生成阅读版 |
| 本人履历、偏好、简历和草稿 `local/` | 忽略，留在本地 |
| 投递、沟通、联系人与面试记录 `applications/` | 忽略，留在本地 |

模板保持空白；个人使用时先复制到本地工作区，再填写内容。个人进展不写入公共公司 JSON。忽略的记录也不是 GitHub 备份，若需要备份，应另行选择仅本人可访问的存储方式。

## 推荐提交方式

先查看改动，确认共享文件没有个人内容：

```bash
git status --short
git diff
```

初次准备校验环境：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

共享修改准备好后运行：

```bash
.venv/bin/python scripts/publish.py --message "更新公共资料"
```

此工具会检查已暂存的文件和历史路径，重新生成阅读版、验证数据与记录边界、运行测试，然后仅暂存共享目录中的全部修改，提交并普通推送。不会强制推送、自动合并远端冲突或上传忽略目录。只要任一检查失败，就停止后续步骤；提交信息同样不要包含个人细节。

只检查当前索引及已生成内容，不暂存、不提交、不推送：

```bash
.venv/bin/python scripts/publish.py --check-only
```

如果没有新的共享修改，正常提交工具仍会尝试推送已有的本地提交。远端有新提交而推送被拒绝时，先查看双方改动再处理，不使用强制推送覆盖他人工作。其他使用者应先 Fork 或使用自己的仓库，确认 `git remote -v` 指向自己有权维护的远端；仅克隆原仓库不会自动获得写入权限。

## 忽略与检查的边界

`.gitignore` 排除尚未被 Git 跟踪的 `applications/`、`local/`、`private/`、`resumes/`、环境文件和邮件草稿等。不要使用 `git add -f` 添加这些文件。可验证：

```bash
git check-ignore applications/README.md local/profile.md
.venv/bin/python scripts/check_public.py
```

共享检查使用明确的目录和根文件名单：`.github/`、`companies/`、`data/`、`docs/`、`exports/`、`investors/`、`schemas/`、`scripts/`、`templates/`、`tests/`，以及规则、入口和依赖文件。新增共享顶层目录时须同时审阅并调整 `scripts/check_public.py`，不要为上传私人文件放宽名单。

检查会阻止已跟踪或历史中出现的私人目录、环境文件、邮件文件，以及当前暂存内容中常见的凭据或个人电脑目录路径。它不能识别所有个人姓名、电话、履历和聊天内容；提交前仍需查看实际差异。公共资料中的公开业务邮箱属于研究数据，不应一概删除。

忽略规则不会清除已经提交的内容或历史。若检查发现历史含有私人路径，应停止推送，先确定是否已上传及需要如何清理；不要只删当前文件后继续推送，也不要未经使用者授权改写远端历史。
