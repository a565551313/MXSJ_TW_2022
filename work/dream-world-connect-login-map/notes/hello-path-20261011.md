# Path from server selection to the account login page (static analysis, 2026-10-11)

Conclusion: after selecting a server, the client connects and **sends nothing first**. It waits for the server to send `GS2C_HELLO` (cmd=1). Once it receives the hello, it switches to the account login page. Earlier loopback tests had 0 bytes because **our server never sent this hello**. That is normal behavior, not a client failure.

Status: static evidence chain is closed. **Not yet verified on Windows.** Tool: `tools/hello_server.py`.

## Evidence chain

| # | Fact | Basis |
|---|---|---|
| 1 | After selecting a server, `selectserver.Connect()` runs: `netobj = CMXNet(ip, port)` → `m_Hello=False` → `netobj.Connect()` (direct connection, no bytes sent first) → `net.g_Net = netobj` → shows "正在連接伺服器中...." | script.fls entry 4844 `script\login\selectserver.py:225`, co_code @54–356 |
| 2 | Command number table: `GS2C_HELLO = 1`, `GS2C_SELSERVER = 47`; `C2GS_LOGIN_ACCOUNT_ENTER = 1`, `C2GS_PING = 8`, `C2GS_SELECT_SERVER = 41`, `C2GS_ANSWERHELLO = 62` … (412 entries total; also answers WI-013) | entry 3970 `script\protocol.py` ("协议号"), LOAD_CONST/STORE_NAME pairs |
| 3 | The dispatch table maps cmd → `netlogin.S2CHello` | entry 3176 = `script\net.py` (status fail but strings readable: `NET_FUNCTION_NAME`, `GetFunc`, `netlogin`, `S2CHello` …); `script\connect.py` also has `self.m_NetFunction[1] = S2CHello` |
| 4 | `netlogin.S2CHello(netobj)`: `seed=UnpackInt(4)`, `g_ServerNum=UnpackInt(2)`, `isUseCertServer=UnpackInt(1)` → `certmgr.SetIsCertLogin` → `net.g_Net.SetSeed(seed)` → `m_Hello=True` → `NakedSend(value computed from seed)` → `selectserver.Show(False)` → `commondialog.HideMessageBox()` → **`loginin.ShowLogin()`** → 9 s Ping timer | entry 4082 `script\login\netlogin.py:337`, co_code @0–530 |
| 5 | The game channel is the **native `C_net` module in `mx.exe`** (`CNetClient`/`CServerCommand`: `UnpackInt`/`NakedSend`/`SetSeed`/`SetMaxLenBytes`, etc.). It does not go through `IMProtocol.dll`, which explains why the observer saw 0 IMP hits | `mx.exe` strings at 0x6b49xx–0x6b4dxx, PyMethodDef table at 0x7e0ca0–0x7e11b8 |
| 6 | Receive framing (`0x4AB540`): read 1 byte L; if L==0xFF, read `MaxLenBytes` more bytes (default 2, constructor at `0x4AB23F`), little-endian; then read an L-byte body; `body[0]`=cmd (`GetCmd` returns the byte at `+4`), `body[1:]`=payload, cmd length = L−1 | mx.exe 0x4AB540–0x4AB712 |
| 7 | Encryption flag `+0xEA` is 0 in the constructor (`0x4AB1FC`). It is set to 1 only at the end of `SetSeed` (`0x4AB360`, `0x4AB3D2`). So **the hello is plaintext**, and encryption/decompression only starts after it | mx.exe |
| 8 | `UnpackInt(n)` = `memcpy(&int0, buf+pos, n)` → little-endian, unsigned for n<4 | mx.exe 0x4685B0 |

## Hello packet bytes

```
08 | 01 | 78 56 34 12 | 01 00 | 00
L=8  cmd  seed(LE)      servernum cert=0
```

This also explains the earlier crash when the harness sent `00 02`: L=0 means an empty body, and reading the cmd from an empty body crashes (E-IDA-DYN-004).

## Open items (needed for the next step, not for reaching the page)

- What `NakedSend` computes from the seed (constants 3227993/2562088/6636321 in S2CHello; some opcodes still unknown).
- Seed derivation `0x4ABB20` and the cipher `0x4C5590` used by `SetSeed` (in `mx.exe`, not IMProtocol). Submitting the account and password later needs these.
- Why `loginhello.py` (imported by the netserver random-connect path) does not appear in script.fls. The normal server-selection path (selectserver.Connect) does not use it.
