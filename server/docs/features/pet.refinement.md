# 炼妖、合宠、还童与预览

工作包：`pet.refinement`；当前归口：`pet`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`preview_refinement / refine_pet / combine_pet / confirm_pet_result`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 584 | `script/mxgame/pet/lianyao/book/dlgrecommendbook.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 823 | `script/mxgame/pet/lianyao/talent/dlgsummontalenttarget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 945 | `script/mxgame/pet/lianyao/book/dlglearnbook.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1305 | `script/mxgame/pet/lianyao/talent/summontalentdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1533 | `script/mxgame/pet/lianyao/book/dlgrecommenditems.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1578 | `script/mxgame/pet/lianyao/dlglianyao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1599 | `script/netpet.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CSummonInfo, S2CSpecialSummonInfo, S2CSummonSkill, S2CSummEquip, S2CSummAllInfo, S2CSummonDel |
| 2192 | `script/mxgame/pet/lianyao/talent/dlgsummontalentresult.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2208 | `script/mxgame/pet/lianyao/mdlianyao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2363 | `script/mxgame/pet/lianyao/reset/dgtpetreset.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2530 | `script/mxgame/pet/lianyao/book/mdlearnbook.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2609 | `script/mxgame/pet/lianyao/color/dgtpetcolor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2611 | `script/mxgame/pet/lianyao/talent/dgtsummontalenttarget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3031 | `script/mxgame/pet/lianyao/book/dgtrecommendbook.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3168 | `script/mxgame/pet/lianyao/talent/dlgsummontemptalent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3307 | `script/mxgame/pet/lianyao/color/mdpetcolor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3345 | `script/mxgame/pet/lianyao/book/petskillbooksubpanel.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3347 | `script/mxgame/pet/lianyao/talent/mdsummontalent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3491 | `script/mxgame/pet/lianyao/talent/summontalentutil.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3582 | `script/mxgame/pet/lianyao/lianyaodefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3708 | `script/mxgame/pet/lianyao/reset/mdpetreset.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3966 | `script/mxgame/pet/lianyao/book/mdrecommendbook.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3969 | `script/mxgame/pet/lianyao/reset/dlgpetreset.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4163 | `script/mxgame/pet/lianyao/color/dlgpetcolor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4321 | `script/mxgame/pet/lianyao/book/dgtlearnbook.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4345 | `script/mxgame/pet/lianyao/talent/netsummontalent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSGetTalentCase, C2GSLearnTalent, C2GSResetTalent, C2GSSaveTalent, C2GSOpenTalentTarget, C2GSSetTalentTarget |
| 4497 | `script/mxgame/pet/lianyao/dgtlianyao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4681 | `script/mxgame/pet/lianyao/talent/dlgsummontalent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4817 | `script/mxgame/pet/lianyao/talent/dgtsummontalent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
