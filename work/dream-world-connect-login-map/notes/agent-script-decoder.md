# Agent Script Decoder: `data/script.fls` Entry 516

## Scope

This note records a read-only reproduction of the `data/script.fls` entry 516
decode. The original client files were only read. Generated files are confined
to `notes/decoder-artifacts/`. This task did not write
`report/analysis.md`, `timeline.md`, or `workitems.md`.

Reproduction command from `D:\Lager\夢想世界`:

```powershell
python .\work\dream-world-connect-login-map\notes\decoder-artifacts\decode_entry516.py `
  > .\work\dream-world-connect-login-map\notes\decoder-artifacts\run-output.json
```

The command exited with status `0`.

## Independently Confirmed

### FLS and zlib

| Item | Result |
|---|---|
| Input | `data/script.fls` |
| SHA-256 | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` |
| Size | `24,454,082` bytes |
| Magic | `0SLF` |
| Entry count | `5,002` |
| Index offset | `0x173EB22` (`24,374,050`) |
| Full-directory zlib check | All `5,002` records passed |
| Total expanded size | `61,940,973` bytes |
| Entry index | `516` |
| Entry ID | `0x183E0854` |
| Raw index-record offset | `0x1740B62` |
| Decoded compressed data offset | `0xF90AFA` (`16,321,274`) |
| Compressed length | `7,690` bytes |
| Expanded length | `17,234` bytes |
| Expanded SHA-256 | `4aa8589ab9e13e7e69b6fd1e498db32c1d0aaf45d2e6a204d6804a743ccc1810` |

The script validates the archive hash, header, final fixed-size directory
layout, all 5,002 record payload bounds, and `zlib.decompress()` results. The
compressed payload begins with the expected zlib bytes `78 DA`.

The directory transform reproduced by the script is:

```text
f1 = ((i * 0x0E7C83D2 + entry_id) mod 2^32) XOR raw1
f2 = ((raw1 * entry_id + 0x0DF25E) mod 2^32) XOR raw2
f3 = ((raw2 * i * 0x00F718FE + 0x0D59D16C) mod 2^32) XOR raw3
```

In the implementation, the third expression is represented with the
equivalent 32-bit arithmetic used by the existing E-REA-007 material:

```python
f3 = (((raw2 * i * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ raw3)
```

For entry 516 this yields decoded fields `field1=0`, compressed length
`7690`, and data offset `16321274`.

### Five XOR layers

The independently reproducible transform is byte-wise XOR over these half-open
ranges:

| Range | Key |
|---|---|
| `[0x0000, 0x0D84)` | `0xB1` |
| `[0x0D84, 0x1B4D)` | `0x44` |
| `[0x1B4D, 0x28F5)` | `0x30` |
| `[0x28F5, 0x367C)` | `0x41` |
| `[0x367C, 0x4352)` | `0x20` |

The transformed payload is `17,234` bytes and has SHA-256
`956b10875b586d47810315a489c7a43afcaee9f29d0864fbde2354306877b736`.

An important correction emerged during independent replay: using coarse
boundaries `0x28F7` and `0x367D` causes marshal parsing to stop around
`0x28F7`. The exact byte boundaries above are required for a complete parse.
The generated decoder records the exact ranges it uses.

### Python 2.7 marshal tree

The local Python 2.7-compatible marshal reader parsed the transformed payload
as a dictionary root and consumed all `17,234` bytes with no trailing data.
It counted **59 code objects**.

The recovered code-object names are:

```text
ModuleReset, SetPlayerID, GetPlayerID, getMsg, RefreshServerInfo,
GetErrorAnsMsg, SetUnEnterServerList, GetUnEnterServerList,
ClearUnEnterServerList, IsSelectServerOver, SetSelectServerOver,
SetConnectedProxy, GetConnectedProxy, GetProxy, SetProxy, GetProxyName,
SetProxyName, GetProxyNameByProxy, SetServerRoleInfo, GetServerRoleInfo,
SetLoginServerIPPort, GetLoginServeIPPort, GetLoginServer, TransferServer,
showlogin, ShowConnectingDlg, S2CServerRoleInfo, C2STransferServer,
__init__, PacketPrepare, OnServerCmd, OnConnectFail, OnError, CMXNet,
__init__, Connect, ConnectTestFail, OnSocketConnectFail, OnSocketError,
IsConnectTestFail, CConnectMgr, __init__, GetServerInfo, GetTestProxyList,
GetTestServerList, Connect, nexttest, SetTimeOutCmd, ConnectTestFail,
CRandomConnectMgr, __init__, Connect, CReselectConnectMgr, RandomConnect,
ReselectServerConnect, DgwReselectServerConnect,
NormalReselectServerConnect, ProcessServerCmd, <module>
```

The key strings requested by the task are independently present in the
decoded tree:

```text
CMXNet
OnServerCmd
ProcessServerCmd
C2STransferServer
ReselectServerConnect
S2CServerRoleInfo
ModuleReset
RefreshServerInfo
Connect
RandomConnect
```

The optional `xdis` Python 2.7 unmarshaller was also run against the same
transformed bytes; it reached offset `17234` and reported 59 code objects,
with root type `Code2` for its top-level code representation. The checked-in
decoder does not require `xdis`; it contains the small reader used for the
reproduction.

## Still Unresolved

The following are not established by this decode alone:

1. The client's runtime loader and the exact pre-execution conversion for the
   non-standard-looking `co_code` bytes.
2. Whether the native `0x2714 -> OnServerCmd(int)` bridge invokes this entry's
   `ProcessServerCmd`, despite both names appearing in the recovered material.
3. The command value, branch predicate, packet contents, or server response
   that drives the selected-server/login transition.
4. The runtime UI transition from server selection/connecting to the account
   login page.
5. Any network behavior or server-side interpretation. No response bytes are
   inferred from the script names.

These remain the boundary between this independently reproduced static result
and the user-provided E-REA-008 handoff. E-REA-008's claim that the tree
contains `CMXNet.OnServerCmd`, `ProcessServerCmd`, and
`C2STransferServer` is now independently supported. Its claims about runtime
binding, opcode conversion, command semantics, and UI behavior remain
handoff/unresolved.

## Artifacts

| File | Purpose |
|---|---|
| `notes/decoder-artifacts/decode_entry516.py` | Read-only FLS, zlib, XOR, and marshal decoder |
| `notes/decoder-artifacts/run-output.json` | Complete stdout from the successful run |
| `notes/decoder-artifacts/entry516-result.json` | Machine-readable summary |
| `notes/decoder-artifacts/entry516-expanded.bin` | zlib-expanded entry 516 payload |
| `notes/decoder-artifacts/entry516-five-xor-marshal.bin` | Five-XOR transformed marshal payload |

Artifact hashes:

```text
entry516-expanded.bin
  4aa8589ab9e13e7e69b6fd1e498db32c1d0aaf45d2e6a204d6804a743ccc1810

entry516-five-xor-marshal.bin
  956b10875b586d47810315a489c7a43afcaee9f29d0864fbde2354306877b736

entry516-result.json
  e4dea0fbca4da168d971665eaca5ff0bc95cf76d743b22890e008c1fa15ba367
```
