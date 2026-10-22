# 客户端伤害公式线索与解析勘误

研究：2026-10-21 四轮只读取证；整理与复核：2026-10-22。
基线提交：`3264485af763c426259c7f937d8d978d3cb2ea67`；客户端台服 v2.27.2。
本文取代会话早期报告中“这三个数据模块仍不可解析”的状态判断。

## 1. 结论与证据范围

**已找到客户端面板威力的算术及部分技能参数，尚未还原服务器最终扣血公式。**

| 已确认的范围 | 证据 | 未确认的部分 |
|---|---|---|
| 面板威力 | entry 4760 `magicinfo.GetAttackPower` 的运算、调用和取整位置 | 与正式服最终伤害是否一致 |
| 技能参数候选 | 3458：914 条；4329：六组候选均为 927 条，其中 925 条记录在六组间一致；3773：103 条 | 原生参数唯一性、常量区全部字段正确性 |
| 精修参数 | 1179 `jingxiu.allskill` 结构读出 128 条，存在具体技能 ID 和增量 | 所有调用是否使用相同加成路径 |
| 网络结果到表现 | 1406 → 697/3933 → 4279 → 4080 的 `hp_chg`、`hurt`、`resist` | 服务器如何产生这些结果 |
| 定点检索 | 第四轮解析了 `script/core/` 和指定属性/面板入口共 75 个 entry | 非全 5002 条语义检索，也未穷尽 DLL |

证据源是原包中解析的 code object 和受限字面量，不执行恢复模块或公式字符串。
操作数偏移指转换后的 Python 2.5 `co_code` 字节偏移，**不是包内偏移或运行时 VA**；
表的 `store_offset` 同样是模块 `co_code` 偏移。函数行号为 code object 自报值。

持久摘要：[client_damage_20261022.json](../docs/evidence/client_damage_20261022.json)。
它保存锁定摘要、原/候选参数、18 组尝试、样本字节、函数 flags 和指令窗口。
这里只提交小证据；完整技能表、反编译语料和原客户端材料不随本文重新入库。

## 2. 面板威力：公式和顺序

entry **4760** `script/magicinfo.py::GetAttackPower`，原始行 527：
`(magicID, magicDct, powrate, power, attackOriNum)`。

定义：P 为传入 power，L 为流派技能等级，S/C/M 分别为己方力量/魅力/魔力，
Q 为己方 `m_Magdef_All`，A 为己方 `m_Att_All`，R=`float(powrate)/100`。
L 来自 `hero.g_Skills[hero.ST_SKILL][hero.SKILLDEPEND[magicDct['type']]].m_Level`，
读取异常时回退 0。下式的 `/` 保留字节码普通除法含义，不能直接当 Python 3 `/`：

```text
物理：V = ceil(P/2 × (1 + .01L + .003S) + A + .6S + 2L + 30) × R × T(n)
法术：V = ceil(P/2 × (1 + .01L + .002M) + Q + .3C + A/4 + 2L + 30) × R × T(n)
T(n) = {1:1, 2:.65, 3:.48, 4:.40, 5:.35, 6:.31, 7:.27}，其他键默认 1
```

物理分支偏移 **289–359**，法术分支 **198–282**，目标数折减 **362–460**。
`magicDct['magicphysic'] == '法術'` 选择法术分支。Q 是己方属性；函数没有目标参数，
不能将 Q 当作已扣除的敌方法防。

`GetLinkHeroMagicDct`（原始行 570）读取 `pow`、`speed`、`powrate`，调用上述函数，
随后在 **328–343** 做 `int(attackpower)` 并写入技能字典，交给描述/提示构造路径。
原客户端使用 `eval` 的调用指令也可见；研究过程没有执行它。

### 2.1 目标数不是本次命中人数

`GetAttackNum`（原始行 452）读取 `effcount` 和 `maxeffcount`：

- 缺省 effcount 为 1，maxeffcount 为 4。
- `effcount='a,b'` 时，**108–169** 算 `floor(float(slv)/int(a))+int(b)`。
- 数字字符串走 `ceil(float(effcount))`；通常以 `min(effcount,maxeffcount)` 形成显示数字。
- **338–356** 将该数字转 int 保存为 iOriNum；异常回退 0。
- **376–464** 的精修追加目标描述只修改显示文字，不回写 iOriNum。
- 返回第三项 iOriNum，被调用方传给 GetAttackPower。

因此 T(n) 使用配置推导的基础目标数。没有在该函数读取战场实际命中人数。

### 2.2 取整的精确边界

可见顺序是：子除法 → 属性表达式 → `ceil` → 效率 R → 目标数 T → 调用方 `int`。
GetAttackPower 与 GetLinkHeroMagicDct 的 flags 均为 **0x43**，没有 Python 2 的
`CO_FUTURE_DIVISION=0x2000`；转换器给子除法的标签是 `BINARY_DIVIDE`。

**条件推断**：若定制 VM 遵循 Python 2 经典除法，且输入为整数，P/2 和 A/4 会先做整数除法；
输入为浮点时则不同。它发生在 ceil 前面。尚未用原生 VM 数值执行确认，见 §7。

固定假数据 P=51、A=101，其他相关属性和等级为 0、R=.94、T=1：按整数子除法与实数子除法，
物理结果分别为 146/147，法术为 75/76。这是算术差异示例，**不是原生测试向量**。

## 3. 技能 ID、精修及两套表的差异

以下来自 entry **4329** 六组候选一致的记录：

| ID | 名称 | pow | powrate |
|---|---|---|---|
| 1101 | 流水行雲 | `50+(slv-1)*8` | `94+(slv-1)*0` |
| 1114 | 後發制人 | `150+(slv-1)*12` | `210+(slv-1)*1` |
| 1414 | 銀河落九天 | `170+(slv-1)*13` | `113+(slv-1)*0` |
| 1620 | 百步穿楊 | `180+(slv-1)*10` | `112+(slv-1)*0` |
| 13370 | 握魂（原名含空格） | `255+(slv-1)*19` | `100+(slv-1)*0` |
| 24360 | 邪王咒 | `275+(slv-1)*20` | `100+(slv-1)*0` |

除 1114 外，这五个样本的 name/pow/powrate 与 entry 3458 一致。
**1114 的 physicsmagicdata.powrate 却是 `220+(slv-1)*1`**，两表 at 也分别为 20/18。
magicdata 还含描述用 `formula7='210+(slv-1)*1+hlv*3'`。
已追踪的 magicinfo/hero 威力路径读取 magicdata；不能混用两张表或断言另一表已废弃。

entry **1179** 的精修记录包括：1114 每级 power=15、eff=3；1414 每级 power=15、eff=1、
res_p=2；1209 每级 power=10、res_d=5；2205 每级 power=12、res_n=res_d=2.5。
字段与描述对应支持 res_p→力敌、res_n→普通、res_d→灵巧；res_m 的含义本次未坐实。

entry **3038** `hero.GetMagicPower`（原始行 1943）明确返回
`基础 pow + m_HighLv × jingxiu['power']`（无精修记录时加 0）；
这是另一条威力路径，不能把 eff 等字段擅自加进该函数的返回值。

### 数据描述线索，尚非结算代码

- 1128「人不由命」及 1230/1330/1426/1526：非战士目标伤害减半，部分描述另称结果 +40%。
- 13370「握魂」：80% 概率造成 200% 伤害，否则自身扣目标所受伤害的 150%。
- 24360「邪王咒」：类似概率描述，但自身扣血比例为 200%，另有复活当回合及血量限制。
- 4759「絕影」：分身攻击力降低、暴击几率临时提高 60%。
- entry 333 buffdata 的 19「眩晕」称防御降低 25%、灵力降低 50%；109「坚固」描述带 `$formula1%`。

技能的“200%伤害”不能推出通用暴击倍率；状态文字不能证明其在最终结算中的先后位置。
结构读出 128 条精修或 432 条 buff，也不代表所有字符串/ID 都正确，部分字段确有污染迹象。

## 4. 网络结果、目标防御、抗性和暴击

```text
1406 netwar.S2CWarWState：hp_chg←UnpackInt(4)，hurt←UnpackBit(0,4)，resist←UnpackSigned(1)
  → 697 war.GetStateInfo：m_HPChg←hp_chg [191–200]，m_Resist←resist [203–212]
  → 4279 CWarrior.BeHurt：CreateModifyHP(m_HPChg,iResist=...) [116–134]
  → 4279 CreateModifyHP：按正负号及 hurt 分流数字类型
  → 4080 mxnumbers.CNumber/AddRestrainImg：渲染数字，按 iResist 符号与己方标记选图标
```

697 `war.State` 另有直接传入 cmd.hp_chg/resist 的路径；3933 `ParserMagicState` 的新演出预加载
路径也保存服务端这些字段。上述片段没有使用目标防御/抗性再计算一次 hp_chg。
部分模块标识符解码异常，结论只覆盖明确的赋值和调用，不外推到全部分支及 DLL。

- **防御**：3038 `hero.InitItem` 将 `m_Def_All`、`m_Magdef_All` 注册为 TWORD 属性，
  CreateProp 经 item.Unpack 从网络初始化；这证明属性来源，不是减防公式。
- **抗性**：ITEM_RESIT 是仙/鬼/妖/智/念五类属性；1249 宠物面板另列力敌/灵巧/群攻/普通。
  雷达图里的 sin/cos/int 属于绘图坐标；网络战斗 resist 的已追踪用途是显示图标，
  不能当作减伤百分数再乘入伤害。
- **特殊受击**：697 模块 **528–537** 定义 HURT_NONE=0、HURT_BS=1；hurt 由回包读取，
  4279 据此选择普通/额外动画数字。BS 缩写和非零标记不够证明完整暴击含义、概率或倍率。

## 5. 随机数调用的实际用途

697 `GetHitEffectPos` **30–72** 使用 `RandInt(-10,10)` 生成 x/y 特效位置；
`Perform` **689–726** 将 `5+RandInt(0,10)` 传给 Escape 演出；SetReplayVer 还有回放相关调用。
1693 `misc.RandInt`（原始行 318）是 `random.randint(a,b) → C_sys.Record(r) → 返回 r`。
C_sys.Record 仍是未还原的原生边界；这些用途不能证明最终伤害存在 ±5% 或 ±10% 浮动。
3835 packetchk 的 CRandom/BRandom 尚未建立到伤害结算的调用关系；4207 touchgame.GetHurtHp
只是另一玩法的血量前后差。不能凭名称将它们当作主战斗算法。

## 6. 更正：解析失败、密钥与自动修复

[锁定 key DB](../tools/decompiler/script_fls_keys.json) 是保存的研究参数，不是全部经过原生确认的真值。
以下调整仅作为调用时的内存候选，**没有改 key DB、原包、转换器或正式服务端配置**。

| entry / 模块 | 早期失败 | 现已确认的范围 |
|---|---|---|
| 3458 physicsmagicdata | 模块 237 的 LOAD_NAME 不在读器语法内；DATA 从 258 起读，启用自动修复又在相对 205526 遇乘法 | 同保存参数、关闭 solve_py25_co_span 后，DATA 片段到模块尾结构通过，914 条；不是原码已证实有错误 |
| 4329 magicdata | 保存参数下，模块 73769 的 EXTENDED_ARG 后出现无参 opcode 0 | 两段密钥候选和边界调整后，DATA 从 249 起的片段可结构重建，见下文 |
| 3773 magicexdescdata | 模块 6284 的 opcode 64 不在字面量语法内 | 第一边界从 6306 调到 6307 后，完整模块结构通过，103 条 |

### 4329 的候选参数与剩余歧义

- 保存 keys：`[223,91,105,140,56]`；候选：`[223,212,230,140,56]`。
  第 2/3 段候选与保存值异或差均为 0x8f；这是重复指令结构的线索，仍需栈/索引检查。
- 保存 bounds：`[73780,147538,221279,294973]`。
- 尝试范围：第 1 项 `{73783,73784,73785}`，第 2 项 `{147538,147539,147540}`，
  第 3 项 `{221282,221283}`，第 4 项保持 294973，共 18 组；关闭 code-span 求解器。
- **6 组通过 / 12 组拒绝**。通过组第 2 项只可取 147538/147539，第 3 项固定 221283。
  被拒绝组有栈下溢或常量索引越界；不能跳过错误拼出完整表。
- 六组 DATA 各 927 条，其中 **925 条逐个原始值比较一致**；4791、2429 有歧义，排除在共识记录外。

这里的“通过”仅指指定片段的受限字面量语法、栈和索引；前缀函数定义、常量区的完整语义、
候选唯一性和原生加载未被证明。计数/顶层无重复不排除嵌套字典问题或乱码。
原生已被证实的模块名分段算法与上述历史启发式候选不是同一种验证，不能相互替代。

## 7. 更正：旧原生除法地址未被当前二进制复现

[旧 opcode 报告](opcode_mapping_and_decompilation.md) 把 **0x004E76DC** 列为 BINARY_DIVIDE。
当前 mxmain.dll SHA256=`637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`，
首选基址 **0x00400000**。从该地址静态反汇编实际以 `jne 0x4e7706` 开始，后续读取操作数、
比较 0xe3 等分支，与旧表的除法调用序列不符。

因此该地址标记需重定位，不能引用它确认当前定制 VM 的整数除法行为。
本次不据此否定整张 opcode 标签表，也不臆造新的 handler 地址；尚待解释历史映像/地址差异。
原生地址字节、文件偏移见持久证据，复核命令在下一节。

## 8. 复现（从仓库根目录）

以下两个检查只需 Python 3 标准库和仓库已有解析器；不生成游戏包或执行游戏代码。
证据 JSON 同时锁定解析器摘要，工具变化时应重新审查，不能靠修改摘要通过。

### 8.1 输入、失败基线、候选和样本复核

```bash
python3 - <<'PY'
import hashlib
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('server/tools').resolve()))
from verify_client_data_boundaries import Archive
import script_literal_reader as lit

record = json.loads(Path('docs/evidence/client_damage_20261022.json').read_text(encoding='utf-8'))
for path, digest in (record['inputs'] | record['parser_inputs']).items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
arc = Archive()

def scan(entry, start=0, **options):
    co = arc.transpile(entry, **options)
    return lit.scan_module(dict(co, code=co['code'][start:]))

def tables(entry, start=0, **options):
    result = scan(entry, start, **options)
    assert result.complete, result.first_violation
    return result

for label, entry, start, options in [
    ('3458_solver_enabled', 3458, 258, {'use_solver': True}),
    ('4329_saved', 4329, 0, {}),
    ('3773_saved', 3773, 0, {}),
]:
    assert str(scan(entry, start, **options).first_violation) == record['failed_baselines'][label]['first_violation']
variants = []
for bounds in itertools.product([73783, 73784, 73785], [147538, 147539, 147540], [221282, 221283]):
    limits = [*bounds, 294973]
    result = scan(4329, 249, keys=record['candidate_4329_keys'], bounds=limits)
    expected = next(row for row in record['candidate_audit'] if row['bounds'] == limits)
    assert result.complete == expected['pass']
    if result.complete:
        table = result.by_name(b'DATA').value
        assert len(table) == 927
        variants.append(table)
    else:
        assert str(result.first_violation) == expected['error']
assert len(variants) == 6
common = {key: value for key, value in variants[0].items() if all(t.get(key) == value for t in variants)}
assert len(common) == record['magic_consensus_count'] == 925
assert set(variants[0]) - set(common) == set(record['magic_ambiguous_ids'])
profiles = {
    3458: (258, {}),
    4329: (249, {'keys': record['candidate_4329_keys'], 'bounds': [73783, 147538, 221283, 294973]}),
    3773: (0, {'bounds': [6307, 12598, 18939, 25271]}),
    1179: (0, {}),
}
for entry, (start, options) in profiles.items():
    result = tables(entry, start, **options)
    saved = record['table_observations'][str(entry)]
    table = result.by_name(saved['table'].encode())
    assert len(table.value) == saved['count']
    assert table.store_at + start == saved['store_offset']
    assert list(table.duplicate_keys) == saved['top_level_duplicate_keys']
    for key, fields in saved['selected_rows'].items():
        for field, value in fields.items():
            actual = table.value[int(key)][field.encode()]
            assert actual == (bytes.fromhex(value['hex']) if isinstance(value, dict) else value)
print('Input hashes, failed baselines, 18 candidates and selected rows match.')
PY
```

### 8.2 指令窗口、flags 与旧地址字节复核

```bash
python3 - <<'PY'
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('server/tools').resolve()))
from verify_client_data_boundaries import Archive

record = json.loads(Path('docs/evidence/client_damage_20261022.json').read_text(encoding='utf-8'))
arc = Archive()

def walk(co, path=()):
    path = (*path, co['name'].decode('ascii', errors='backslashreplace'))
    yield path, co
    for value in co['consts']:
        if isinstance(value, dict) and 'code' in value:
            yield from walk(value, path)

for saved in record['code_observations']:
    path, co = next((p, c) for p, c in walk(arc.transpile(saved['entry'], use_solver=True)) if list(p) == saved['path'])
    assert co['flags'] == saved['flags'] and co['firstlineno'] == saved['firstlineno']
    assert hashlib.sha256(co['code']).hexdigest() == saved['code_sha256']
    for window in saved['windows']:
        assert co['code'][window['start']:window['end_exclusive']].hex() == window['hex']
raw = Path('mxmain.dll').read_bytes()
assert hashlib.sha256(raw).hexdigest() == record['inputs']['mxmain.dll']
address = record['native_address_check']
expected = bytes.fromhex(address['bytes_hex'])
assert raw[address['file_offset']:address['file_offset'] + len(expected)] == expected
print('Code windows, flags and historical-address bytes match; no native execution.')
PY
```

若要重看原生指令而非只比较字节，使用已有 pefile/capstone 环境：

```bash
python3 - <<'PY'
import capstone
import pefile

pe = pefile.PE('mxmain.dll')
va = 0x004E76DC
base = pe.OPTIONAL_HEADER.ImageBase
assert base == 0x00400000
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for insn in md.disasm(pe.get_data(va - base, 75), va):
    print(hex(insn.address), insn.mnemonic, insn.op_str)
PY
```

## 9. 未完成与后续证据

- 目标防御、抗性、状态、暴击、技能条件、保底、随机浮动在最终扣血中的组合及取整顺序未恢复。
- 需重新定位原生除法 handler，确认运行时类型和数值行为；不能以 Python 3 算术替身作为原生证明。
- 4329 的 4791/2429 与剩余常量区需跨模块核对，未确认的参数不能回写锁定库。
- 后续动态验证应固定攻击者、技能与目标，逐项改变防御/抗性/精修，记录回包及结果标记；
  自建 Mock 的数值不能证明正式服公式。本次未执行 Windows 客户端、官方连接或实机伤害采样。
