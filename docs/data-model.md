# 数据字段与维护方式

本页约定共享的公开研究数据。使用者的事实、偏好和进展不加入这些 JSON，按 [本地工作流](application-workflow.md) 保存在忽略的 `local/` 与 `applications/` 中。

公司记录契约见 [company.schema.json](../schemas/company.schema.json)，分类契约见 [taxonomy.schema.json](../schemas/taxonomy.schema.json)。所有原始事实只维护在 `data/companies/*.json` 和 `data/taxonomy.json`。

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 数据格式版本，目前为 1 |
| `id` | 稳定 ASCII ID，必须等于 JSON 文件名；品牌变化时不随意修改 |
| `name` / `aliases` | 当前整理名称、历史名称与原表别名；不以原表名称证明当前运营主体 |
| `category_id` | 关联分类 JSON 的主赛道；细分业务和跨赛道属性写入 `focus`、`products` |
| `focus` / `products` | 细分方向、产品与业务描述 |
| `locations_text` | 公开城市记录；可能包含总部、团队或招聘地，保留原文限定 |
| `comparison` | 编辑分析、比较对象名称；不代表性能测试、排名或完整竞争清单 |
| `investment.summary` | 有出处的历史投资背景与未确认范围 |
| `investment.verification_status` | 摘要的披露核验状态，见下表 |
| `contacts.website` | 记录的公司或品牌网站；历史站点问题见备注 |
| `contacts.careers_url` | 官网招聘站、含投递方式的官网页面、平台公司页或历史招聘帖；类型见备注 |
| `contacts.recruitment_email` | 有公开投递依据的邮箱；可能仅适用于校招、实习或旧岗位，必须阅读备注 |
| `contacts.other_email` / `other_email_purpose` | 商务、客服、IR 等其他公开联系邮箱及用途 |
| `notes` | 主体冲突、历史渠道、日期口径、来源局限和缺失说明 |
| `checked_at` | 本条记录实际核查日期，ISO `YYYY-MM-DD`；格式迁移不更新该日期 |
| `sources` | 证据清单，每条含公司内唯一 ID、网址、标题、支持内容、公开日期与核查日期 |
| `provenance` | 导入时的原图谱名称与分类，供追溯；不等同当前分类或已确认事实 |

## 披露状态

| 状态 | 含义 |
| --- | --- |
| `confirmed_disclosure` | 当前投资摘要有可核对的公开披露；不保证最新、完整或仍持股 |
| `partial` | 部分关系可支持，另有未确认、冲突、报道或口径限制 |
| `not_found` | 本次研究未找到可靠公开披露；不能写成确定没有投资 |

缺失字段用 JSON `null`。不使用空字符串、“N/A”或猜测地址。`published_date` 可为 `YYYY`、`YYYY-MM` 或 `YYYY-MM-DD`，未知为 `null`；不能把网页抓取日期当作公告日期。来源 URL、标题和 `supports` 共同说明证据用途，不能仅因域名是官网就认定它证明全部字段。

## 变更与生成

1. 修改目标公司 JSON，补齐对应来源和真正核查过的日期；保持来源 ID 稳定，新增来源追加新 ID。
2. 运行 `.venv/bin/python scripts/validate.py`。
3. 运行 `python3 scripts/build.py` 生成公司 Markdown、赛道文档、索引与两份 CSV。
4. 运行 `.venv/bin/python scripts/validate.py --check-generated`，检查提交差异。

Agent 应从 [index.json](../data/index.json) 定位需要的记录，再读取单家公司文件。若按文本检索投资方，可以使用 `scripts/query.py --text`；投资方目前保留在有来源的叙述中，不把未经人工确认的名称提取结果当作精确股东关系。

JSON Schema 和 CI 校验结构、日期、关联 ID 和生成同步；不能验证网页当前内容、邮件可达性、招聘开放状态或披露真实性，这些需要实际重查。

## VC 机构资料

机构资料独立放在 `data/investors/*.json`，契约见 [investor.schema.json](../schemas/investor.schema.json)，筛选与归因见 [investor-methodology.md](investor-methodology.md)。机构不是被投企业，不混入原有 79 家公司数据。

机构字段包含成立年份及其口径、团队原平台、方向与阶段、原平台/本机构案例、近期活动、编辑分析、公开渠道和来源。阅读索引、机构 Markdown 和两个机构 CSV 同样由 `scripts/build.py` 自动生成。
