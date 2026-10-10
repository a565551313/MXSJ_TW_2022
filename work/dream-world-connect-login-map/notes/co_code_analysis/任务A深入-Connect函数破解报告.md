# 任务A深入 — Connect 函数破解报告

**日期**: 2026-10-10
**目标**: 破解 Connect(647B) 和 Connect(689B) 核心连接逻辑
**状态**: 核心流程已解码 ✅ | 部分细节待破解 ⏳

---

## 一、新破解的映射（4个）

| 编码 | Python 2.7 | 名称 | 字节数 | 置信度 | 证据 |
|-----|-----------|------|--------|--------|------|
| **0xE3** | 0x6F (111) | **JUMP_IF_FALSE** | 3 | ✅ 高 | `if serverlist:` 模式，相对跳转 |
| **0x58** | 0x19 (25) | **BINARY_SUBSCR** | 1 | ✅ 高 | `d['key']` 字典取值模式 |
| **0x6C** | 0x3D (61) | **GET_ITER** | 1 | 🔶 中 | 循环开始 `for x in ...:` |
| **0xD3** | 0x5D (93) | **FOR_ITER** | 3 | 🔶 中 | 循环跳转，arg为相对偏移 |

**累计映射**: 32个（表A 21 + 表B 7 + Connect新破解 4）

---

## 二、Connect 函数完整伪代码

### 2.1 CRandomConnectMgr.Connect (647B) — 随机连接

```python
def Connect(self):
    """随机连接测试服务器（测试模式）"""
    # 创建选服和登录配置
    selectserver = {'note': 'ipPort'}
    loginhello = {'note': 'ipPort'}
    
    # 获取测试服务器和代理列表
    serverlist = self.GetTestServerList()
    proxylist = self.GetTestProxyList()
    
    # 如果有测试服务器，刷新选服界面并返回
    if serverlist:
        selectserver.Refresh('ipPort')
        return 'ipPort'
    
    # 如果有测试代理，直接返回
    if proxylist:
        return 'ipPort'
    
    # === 正式连接流程 ===
    
    # 解析代理数据
    proxydata = proxylist['name']
    proxy_ip = proxydata['ip']
    proxy_port = proxydata.get('port')
    
    # 遍历服务器列表
    for d in serverlist:
        # 解包服务器信息（5个字段）
        name, ip, port, serverid, district = (
            d['b9c1b8d5b373b1b5212121'],
            d['iType'],
            d[''],
            d['...'],
            d['...']
        )
        
        # 打印日志
        LOG('b373b1b5a54eb27a2121212121', name, serverid, bool(proxy))
        
        # 创建网络对象
        netobj = CMXNet(ip, port, ':', loginhello['TEST_HELLO'], ...)
        netobj.m_Hello = False
        netobj.m_IsFail = False
        netobj.m_ProxyName = '.'
        netobj.m_SvrName = name
        netobj.m_ServerInfo = (district, name, ip, port, serverid)
        self.m_Nets.append(netobj)
        
        # 如果有代理，通过代理连接
        if proxy:
            LOG_DEBUG('...', proxy, note)
            p = proxy.find(...)
            netobj.m_Proxy = proxy
            netobj.Connect(proxy, p, ...)
        
        # 尝试连接所有IP（负载均衡）
        iplst = ip.split(...)
        for i in iplst:
            netobj.NakedSend(chr(port & 0xFF), ...)
            netobj.Connect(ip, port)
```

### 2.2 CReselectConnectMgr.Connect (689B) — 重选服务器连接

```python
def Connect(self):
    """重选服务器连接（正式模式）"""
    lst = []
    
    # 创建选服和登录配置（使用加密的key）
    selectserver = {'b1c0aff2b0cf': 'district'}
    loginhello = {'b1c0aff2b0cf': 'district'}
    
    # 获取服务器信息
    serverData = selectserver.GetServerInfo()
    
    # 第一遍：筛选目标服务器
    for _ in serverData:
        d = _
        slist = d['serverid']
        
        if slist == 'name':
            continue  # 跳过名称条目
        
        # 匹配服务器ID
        if d['ip'] == ... and slist == self.m_ServerID:
            lst.append(d)
    
    # 第二遍：连接筛选出的服务器
    for d in lst:
        # 解包服务器信息（5个字段）
        name, ip, port, serverid, district = (
            d['port'],
            d['b9c1b8d5c2e0aa41b373b1b5212121'],
            d['iType'],
            d['ip'],
            d['serverid']
        )
        
        # 创建网络对象（使用RESELECT_HELLO）
        netobj = CMXNet(ip, port, 'b373b1b5...', loginhello['RESELECT_HELLO'], ...)
        netobj.m_Hello = False
        netobj.m_IsFail = False
        netobj.m_ProxyName = ':'
        netobj.m_SvrName = name
        netobj.m_ServerInfo = (district, name, ip, port, serverid)
        netobj.m_PassPort = (self.m_Idx, self.m_Pwd)
        
        # 如果district是字符串，设置入口名称
        if isinstance(district, str):
            netobj.m_EntryName = district
        
        # 获取并设置代理
        proxy = GetProxy()
        if proxy:
            p = proxy.find(...)
            proxyName = GetProxyName()
            if isinstance(proxyName, str):
                netobj.m_ProxyName = proxyName
            netobj.Connect(proxy, p, ...)
        
        # 尝试连接所有IP（负载均衡）
        iplst = ip.split(...)  # 按'.'或其他分隔符拆分
        for i in iplst:
            # 发送端口低字节（可能是某种握手）
            netobj.NakedSend(chr(port & 0xFF), ...)
            netobj.Connect(ip, port)
        
        # 添加到网络列表
        self.m_Nets.append(netobj)
```

---

## 三、关键发现

### 3.1 CMXNet 构造函数

```python
# 构造函数签名（推测）
netobj = CMXNet(ip, port, proxy_separator, hello_config, ...)
# 参数:
#   ip: 服务器IP
#   port: 服务器端口
#   proxy_separator: 代理分隔符（':' 或 '.'）
#   hello_config: 握手配置字典（TEST_HELLO 或 RESELECT_HELLO）
```

### 3.2 网络对象属性（m_xxx）

| 属性 | 类型 | 说明 |
|-----|------|------|
| `m_Hello` | bool | 是否已发送hello |
| `m_IsFail` | bool | 连接是否失败 |
| `m_ProxyName` | str | 代理名称（':' 或 '.'） |
| `m_SvrName` | str | 服务器名称 |
| `m_ServerInfo` | tuple | (district, name, ip, port, serverid) |
| `m_PassPort` | tuple | (m_Idx, m_Pwd) 认证信息 |
| `m_EntryName` | str | 入口名称（district） |
| `m_Proxy` | object | 代理对象 |
| `m_Nets` | list | 网络对象列表（类属性） |

### 3.3 连接流程（完整）

```
1. 创建配置字典（selectserver/loginhello）
2. 获取服务器信息（GetServerInfo/GetTestServerList）
3. 筛选目标服务器（匹配m_ServerID）
4. 遍历服务器列表:
   a. 解包服务器信息（5字段元组）
   b. 创建CMXNet对象
   c. 设置网络对象属性（m_Hello, m_IsFail, m_SvrName等）
   d. 添加到self.m_Nets
   e. 如果有代理：通过代理连接
   f. 拆分IP列表（负载均衡）
   g. 对每个IP：NakedSend + Connect
```

### 3.4 NakedSend — 原始字节发送

```python
# 在连接前发送端口低字节
netobj.NakedSend(chr(port & 0xFF), ...)
# 这可能是某种握手或探测包
```

### 3.5 加密/混淆的字典Key

服务器信息字典使用混淆的key：
- `'b1c0aff2b0cf'` — 可能是 'district' 或类似字段名的混淆
- `'b9c1b8d5c2e0aa41b373b1b5212121'` — 长混淆key
- `'b373b1b5a54eb27a2121212121'` — 日志/配置key

这些可能是简单的XOR或替换加密，**下一步可破解**。

---

## 四、两种Connect的对比

| 特性 | CRandomConnectMgr (647B) | CReselectConnectMgr (689B) |
|-----|-------------------------|---------------------------|
| **用途** | 测试模式随机连接 | 正式重选服务器连接 |
| **Hello命令** | `TEST_HELLO` | `RESELECT_HELLO` |
| **配置key** | 'note', 'ipPort' | 'b1c0aff2b0cf', 'district' |
| **服务器信息** | GetTestServerList() | GetServerInfo().values() |
| **筛选逻辑** | 无（全部连接） | 匹配 m_ServerID |
| **认证信息** | 无 | m_PassPort = (m_Idx, m_Pwd) |
| **入口名称** | 无 | m_EntryName = district |
| **代理分隔符** | '.' | ':' |

---

## 五、下一步

1. ⏳ **破解参数字节编码** — 跳转目标的参数也被编码（如0x07→?）
2. ⏳ **破解加密字典key** — 'b1c0aff2b0cf' 等混淆字符串
3. ⏳ **破解剩余未知opcode** — 0xA2, 0x40, 0x12, 0x3F, 0x0E等
4. ⏳ **破解S2CServerRoleInfo** — 服务器列表响应格式
5. ⏳ **确定命令字数值** — TEST_HELLO/RESELECT_HELLO/C2GS_SELECT_SERVER的uint16值

---

## 六、输出文件

- `connect_cracked.json` — Connect函数破解结果（待生成）
- `mapping_table_v4.json` — 更新映射表（32个映射，待生成）
- 本报告 — `任务A深入-Connect函数破解报告.md`

---

**破解者**: 任务A会话（总指挥）
**日期**: 2026-10-10
