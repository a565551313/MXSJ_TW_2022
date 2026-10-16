# H独立审核区

每个实际审核JSON必须符合 `schema/contract.schema.json` 的 `$defs.review`。
`example.json.template` 是占位示例，不会被扫描为审核。H必须以被审正文**原字节SHA256**替换占位，说明接受/退回的范围；不得只改正文里的置信级别代替独立审核。

报告型证据可用UTF8 Markdown放在本目录，不能把原始游戏包、大批源码或1288内容搬入。
