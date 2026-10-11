# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [账号安全、二次密码和异常登录保护](../../../../docs/features/account.security.md) | `request_protection_change / confirm_protection_change` |
| [登录排队](../../../../docs/features/account.login_queue.md) | `join_queue / query_queue / cancel_queue` |
| [短信验证与未成年人保护](../../../../docs/features/account.identity_protection.md) | `request_verification / verify_challenge / evaluate_login_policy` |
