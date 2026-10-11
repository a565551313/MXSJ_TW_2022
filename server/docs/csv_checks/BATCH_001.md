# 第一批客户端静态目录 CSV（复核材料）

日期：2026-10-12。输出目录：[`batch_001/`](batch_001/)。

**结论：这一批可以用于人工复核、目录浏览、后续导入器开发；不是正式服务端规则表，也不是原生加载器验证结果。**
没有改动客户端、`data/script.fls`、历史密钥库或 `server/game_data/`，没有执行还原出来的游戏脚本。
文字保留繁体，ID 不重新编号，描述、颜色标记、资源公式均不解释、不执行。

## 1. 实际集成范围

先合并 #19 → #18 → #20，目标均为 `arena/b53b33e6-mxsj-tw-2022`，不是 `master`：

| PR | 集成内容 | 合并提交 |
|---|---|---|
| #19 | 公共字面量读取器、严格/部分结果契约、3205 技能复核 | `a659194` |
| #18 | 独立交叉检查、道具/宠物候选边界证据 | `d8dc169` |
| #20 | 地图/NPC 复现工具、分来源 staging 数据 | `ee11cea` |

实际合并后原有 **132 项测试通过**；本批新增 **20 项回归测试**，总计 **152 项通过**。
这只能证明当前工具与固定输入下的检查通过，不能把候选解码升级为“原生客户端已确认”。

## 2. 文件清单与数量

共 **17 个 CSV + 5 个 JSON/JSONL 文件**。数量不包括表头。

| 核心 CSV | 行数 | 内容 |
|---|---:|---|
| `items.csv` | 6,851 | 道具名称、原始描述、类别代码和图片映射 |
| `pets.csv` | 135 | 宠物主表 |
| `pet_skill_candidates.csv` | 458 | `maySkillLst` 的有序子表 |
| `pet_required_skills.csv` | 26 | 源表显式提供的 `mustSkillName` |
| `pet_aptitudes.csv` | 131 | 宠物资质，保留原始十个字段名 |
| `pet_aptitude_missing.csv` | 3 | 主表存在而 2954 资质表缺失的 ID |
| `pet_skills.csv` | 579 | 可进入本批复核 CSV 的技能记录 |
| `pet_skill_overwrites.csv` | 9 | 技能字典重复键覆盖摘要 |
| `pet_skill_name_matches.csv` | 145 | 143 个被宠物引用的技能名称的全部 ID 匹配 |

地图/NPC 在 `maps_npcs/` 中保持 E 的既有 CSV 字节和来源分离，不虚构统一地图/NPC 表：

| 文件 | 行数 | 源条目 / 表 |
|---|---:|---|
| `mapdata_scene_dictionary.csv` | 104 | 1301 / DATA |
| `mapdata_parent_scene.csv` | 6 | 1301 / MAP_ASCRIPTION |
| `sceneid2name_minimap_scenes.csv` | 57 | 400 / DATA |
| `npcname2realnamedata_alias_to_realname.csv` | 55 | 1799 / DATA |
| `npcposdata_records.csv` | 1,335 | 2601 / DATA |
| `minimapnpcpos_pos_records.csv` | 1,344 | 2804 / DATA_POS |
| `minimapnpcpos_wenzi_entries.csv` | 287 | 2804 / DATA_WENZI |
| `npc_2601_vs_2804_agreement.csv` | 677 | 两种来源的非零 NPC ID 对照 |

1,335 和 1,344 是两个来源的**记录数**，不是唯一 NPC 数，更不能直接相加后宣称 NPC 总数。

## 3. 字段与关联契约

完整列顺序、类型、记录主键、来源表、文件 SHA-256 见 [`batch_001/manifest.json`](batch_001/manifest.json)。
核心 CSV 使用 UTF-8 无 BOM、所有字段加双引号、LF 行结束；布尔值写 `true` / `false`。
CSV 本身没有类型，读入后必须按 manifest 转换，而不是靠表格软件猜测。

### 道具与宠物

- `client_shape_id`：源 DATA 字典键，是客户端显示目录 ID；**不是玩家背包实例 ID**。
- `items.name/description_raw`：1945.DATA 的原始二元组元素。
- `category_code_raw`：1945.ITEMDATABYTYPE 的原始整数；本批不替类别代码发明业务含义。
- `image_id`：显式 SHAPETABLE 映射，缺省时按客户端 Shape2Image 的规则回退至自身 shape ID。
  `image_mapping_explicit` 标出是否存在显式映射。没有验证相应图片资源一定存在。
- `pets` 的 `name/liupai_raw/attack_type_raw/carry_grade/maxskillnum_raw/address_raw`
  对应原始字段 `name/liupai/attack_type/carry_grade/maxskillnum/address`。
  尤其不把 `maxskillnum` 擅自解释为服务端硬上限。
- 技能候选子表的 `sequence` 是**从 0 开始**的源 tuple 顺序，保留重复和顺序，不代表概率。
- 必带技能子表只列原始记录中实际存在的字段；没有字段不补一个空技能或 ID 0。
- 资质十列原名保留，例如 `法力資質`、`法力資質最大值`；不重新解释为成长、实际面板或服务端上限公式。

### 技能

- `skill_id`：3205.DATA 的键。`type_code_raw` 保留原始分类。
- `description_raw/fpneed_raw/mpneed_raw/hpneed_raw` 都是原始文本；**禁止 `eval` 或执行公式**。
- 590 次字典写入得到 581 个唯一技能 ID，其中 2 条隔离，CSV 保留 579 条。
- 9 次覆盖摘要包含原写入顺序和字节码偏移；完整旧值/新值在 `overwrite_evidence.jsonl`。
  4573 从「天魔返生術」覆盖为「地魔返生術」，其余 8 次值相同；不能只导出最终值而丢掉证据。
- 宠物技能按原名精确匹配，不做简繁转换或模糊匹配：
  - `高級命中` → **229、255**；
  - `終級命中` → **329、355**。
  两个候选均保留，`match_count=2`、`ambiguous=true`。**不能默认取第一个 ID 作为正式关联。**

核心行均带 `source_entry`、`source_table` 和 `review_status`。表级候选参数、输入哈希和解释证据由 manifest 关联。

### 地图 / NPC

- 2601 记录键是 `(scene_id, record_index)`；2804 POS 记录键是
  `(scene_id, scene_display_name, record_index)`。`(scene_id, npcid)` **不是唯一主键**。
- 保留 NPC ID 为 0 的记录（分别 632、631 条）、重复记录、来源差异和记录顺序。
- `related_id_unresolved` 仍未定性；两个来源的尺寸/坐标不能未经确认合并为服务端坐标系统。
- E 的 CSV 保留其格式：UTF-8、最小引号、CRLF；不要套用核心 CSV 的全引号/LF 约定。
- E staging 的空值与空文本同写为空单元格，`field6` 可能是以 `|` 连接的序列，`shape` 可能为资源名。
  本批保持兼容，不声称它是完全无损的类型化还原格式。详细语义与限制见 [E 交接文档](AGENT_E_HANDOVER.md)。
- 导出器会先重新生成 E 的证据和 staging，再逐字节验证原文件，匹配后才复制入本批。

## 4. 隔离清单与缺失数据

`quarantine.jsonl` 保存**完整记录**，并采用带类型的 JSON 保存原字节十六进制、tuple/list 和字典键。
它保存的是**本批明确参数下读到的值**，不是声称这些值就是原生真实值。

| 源条目 | ID | 隔离原因 |
|---:|---:|---|
| 1945 | 72548 | 名称含非法 CP950 字节；保留 `c2f9a448a7a4c34dc5e9c5e784`，不替换成乱码占位符 |
| 2954 | 2800 | 保存参数下法力资质为 2130，高于对应最大值 1989；不擅自改成尚未确认的 1700 |
| 3205 | 719 | 描述边界缺少独立确认，整行隔离 |
| 3205 | 4406 | 描述边界缺少独立确认，整行隔离 |

另有宠物 **3010（未定）、4021（年獸）、4022（爆竹）** 在 2954 中没有资质记录，
放入 `pet_aptitude_missing.csv`。这与“存在但隔离”的 2800 不同；两者都不补零。

## 5. 可复现命令

在仓库根目录运行，无额外 pip 依赖：

```bash
# 只检查，不改已有文件；重新从源归档提取并比较全部 22 个文件
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check

# 如需另存，必须选择全新或空目录；已有目录不会被覆盖
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py \
  --out /home/user/mxsj-review-batch-new

# 实际集成后的全部测试
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -q
```

输入固定：

- `data/script.fls`：`8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`
- `tools/decompiler/script_fls_keys.json`：`43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`

核心参数配置在 [`batch_001_profiles.json`](batch_001_profiles.json)；地图参数及其来源也写入 manifest。
所有核心调用显式关闭自动字节码边界求解器，避免工具悄悄修边界。
生成物没有时间戳或动态 HEAD 值；工具源码、参数或证据更改都会导致 manifest 哈希变化，需要重新复核。
`--check` 不只检查行数，还检查全部输出的字节、文件集合和 E 的证据一致性。

**表格软件注意：**用“导入文本/CSV”并把原始文本列设置为文本。CSV 引号不能防止公式自动执行。
不使用会改变原值的单引号前缀或简繁替换；如需安全表格预览，应另做展示层。

## 6. 后续 PR 收口（本批未合入）

截至本批制作时，#13、#14、#15、#17 仍为 OPEN，没有把“研究报告”当作正式数据批准。
小修收口不需要重做全部大范围调查：

| PR | 保留的研究价值 | 合入前需要收口的点 |
|---|---|---|
| #13 / B | 道具、装备、商城探查 | 基线提交存在性说法需纠正；补 41052 的边界问题，并引用当前 #18 的交叉证据；72548 继续隔离 |
| #14 / D | 3205 的 152 密钥、581 条技能及 9 次覆盖证据 | 改正“转译 NOP 会缩短缓冲区”的表述：缓冲区等长，残留操作数字节会使遍历失步；实际公共接口验证以已合入 A 的严格契约测试为准 |
| #15 / C | 宠物分类、资质、图鉴及描述的调查 | 2800→1700 只能保留为假设，不能因为数值落入范围就直接采用；缺失资质不补零；本批仅采用已复核的显式参数 |
| #17 / F | 称谓、坐骑、家具字面量结果 | 修正 opcode 统计范围，只扫描真正 co_code 区间，不能把常量区字节算作未知操作码；常量池控制字符不等于 DATA 字段损坏 |

这些后续工作不阻塞使用本批作为复核材料，但**仍阻塞把其未确认结论推广到新的正式表**。
