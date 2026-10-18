# 历史导出数据：不是正式游戏配置

状态：**历史复现材料**。此目录包含 equipment、scenes、npc_dialogs、reward_gifts、skills 的 CSV／JSON，以及 `game_data.sqlite`。
这些是历史提取结果，文件存在不证明字段完整、文字无损、规则正确或生产准入。

- SQLite 被 [旧浏览器](../data_browser/README.md) 的两个入口直接读取。
- [旧提取器](../data-parser/extract_game_data.py) 可输出同类文件，但本轮未重新生成或核实所有现有字节的生成来源，不能冒称全部可逐字节复现。
- 当前审核链位于 [server](../../server/README.md)；batch_001 也只是候选数据，不是本目录所有表的完整替代。
- 不手工“修好”缺值／乱码，不把这些文件复制到 `server/game_data/`，不重新导出覆盖现有证据。
- 清理前需核对消费者、来源与替代数据覆盖；本轮没有修改任何 CSV／JSON／SQLite。
