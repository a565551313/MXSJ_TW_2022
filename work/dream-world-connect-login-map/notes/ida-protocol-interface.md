# IDA Protocol Interface Notes

## Scope

- Case: `dream-world-connect-login-map`
- Date: 2026-10-09 Asia/Shanghai
- Inputs:
  - `D:\Lager\夢想世界\IMProtocol.dll`
  - `D:\Lager\夢想世界\mxmain.dll`
- Method: IDA Pro 9.4 through local IDA MCP, read-only analysis databases opened from temporary copies.
- Network activity: none.

## Database Survey

### IMProtocol.dll

- Architecture: 32-bit
- Image base: `0x10000000`
- Image size: `0x2e000`
- SHA-256: `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c`
- Functions: 748 total, 27 named, 444 strings
- Session used: `cb414ee4`

### mxmain.dll

- Architecture: 32-bit
- Image base: `0x00400000`
- Image size: `0xa5c000`
- SHA-256: `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`
- Functions: 12,279 total, 392 named, 17,787 strings
- Session used: `3b37c7b9`
- Notable segments: `.text`, `.rdata`, `.data`, `_dyprot0`, `_dyprot1`, `.idata`

## E-IDA-001: Protocol DLL Export Surface

`IMProtocol.dll` exports a compact binary message API:

| Address | Export | Initial interpretation |
|---|---|---|
| `0x10003000` | `IMP_ConnectNsServer` | Initializes Winsock, prepares a source string, then enters connection setup |
| `0x100030d0` | `IMP_UnConnectNsServer` | Disconnect path |
| `0x10003110` | `IMP_RefreshCryptKey` | Rebuilds or refreshes crypto-related state from a source string |
| `0x100031a0` | `IMP_DecryptBuffer` | Buffer decryption wrapper |
| `0x100031f0` | `IMP_EncryptBuffer` | Buffer encryption wrapper |
| `0x10003240` | `IMP_SendBuffer2NS` | Sends a prepared buffer to the network socket |
| `0x10003280` | `IMP_ReadUInt64` | Read unsigned 64-bit value |
| `0x100032c0` | `IMP_ReadUInt32` | Read unsigned 32-bit value |
| `0x10003330` | `IMP_ReadUInt16` | Read unsigned 16-bit value |
| `0x100033a0` | `IMP_ReadUInt8` | Read unsigned 8-bit value |
| `0x10003400` | `IMP_ReadStr` / `IMP_ReadBin` | Read a variable-size byte/string value into a caller buffer |
| `0x10003570` | `IMP_NewIMBuffWriter` | Allocates/initializes a message writer |
| `0x100035b0` | `IMP_FreeIMBuffWriter` | Frees a message writer |
| `0x10003600` | `IMP_WriteUInt64` | Write unsigned 64-bit value |
| `0x10003650` | `IMP_WriteUInt32` | Write unsigned 32-bit value |
| `0x100036c0` | `IMP_WriteUInt16` | Write unsigned 16-bit value |
| `0x10003730` | `IMP_WriteUInt8` | Write unsigned 8-bit value |
| `0x10003790` | `IMP_WriteStr` / `IMP_WriteBin` | Copies a caller buffer into the message writer |

## E-IDA-002: Connection Initialization

Decompilation of `IMP_ConnectNsServer`:

```text
WSAStartup(0x202, &WSAData)
sub_10002EB0(Source, strlen(Source))
initialize global protocol state once
return sub_10001660(a2)
```

Direct observations:

- Winsock startup is performed inside the exported connection entry.
- The first argument is treated as a NUL-terminated source string and passed with its length to `sub_10002EB0`.
- The second argument is passed to the lower-level connection routine `sub_10001660`.
- The export itself does not expose a host/port pair in the decompiler signature. The host/port may be encoded in the source string, held in global state, or consumed by `sub_10001660`.

## E-IDA-003: Crypto State Refresh

`IMP_RefreshCryptKey` calls the same string-processing helper:

```text
sub_10002EB0(Source, strlen(Source))
initialize global protocol state once
return 0
```

This is evidence that the source string used by connection setup may also seed or refresh protocol state. It is not enough to identify the algorithm or key material.

## E-IDA-004: Send Buffer Boundary

Decompilation of `IMP_SendBuffer2NS` shows:

1. A buffer object is required at `a3`.
2. The buffer pointer is read from `a3 + 0x10`.
3. The current length is read from `a3 + 0x18`.
4. The length must be greater than `2`.
5. If the first 16-bit value is zero, it is set to `htons(length)`.
6. The buffer is passed to `sub_10005F80` for transmission.
7. Invalid/empty input reports through an `IMMain.cpp` error path and returns `-1`.

This supports the following provisional frame hypothesis:

```text
offset 0x00: uint16 network-order total/current frame length, populated if zero
offset 0x02: message payload or additional header, unknown
offset 0x04+: serialized command fields, unknown
```

The `uint16` length observation is direct. Whether it includes the two-byte field itself, encryption padding, or a larger transport header remains unresolved.

## E-IDA-005: Reader/Writer Behavior

`IMP_ReadStr` / `IMP_ReadBin`:

- Requires a positive requested size and non-null destination.
- Calls `sub_10001D30` to obtain a reader/context.
- Calls `sub_10002CA0` to extract a value.
- Copies the resulting bytes into the destination with `memcpy`.
- Returns the extracted size.

`IMP_NewIMBuffWriter` delegates to `sub_10001F00`.

`IMP_WriteStr` / `IMP_WriteBin`:

- Takes a source pointer and explicit size.
- Calls `sub_10002070(Size, 0)` before copying.
- Copies exactly `Size` bytes into an internal temporary representation.
- Calls `sub_10002000`, then frees temporary storage when required.

The current evidence supports explicit-length binary fields rather than NUL-terminated strings at the transport layer. The higher-level field encoding still needs caller-side analysis.

## E-IDA-006: Imported Network APIs

The protocol DLL imports at least:

- `connect` at `0x1001f1a0`
- `send` at `0x1001f1a8`
- `WSAStartup` at `0x1001f190`
- `htons` at `0x1001f188`

The import surface is consistent with a native TCP socket protocol. Receive-side behavior is represented by internal callbacks/handlers, but the exact `recv` call site and framing loop still need xref tracing.

## Preliminary State Model

```text
endpoint/config
  -> IMP_ConnectNsServer(source, connection_arg)
  -> sub_10001660
  -> connection callback / NsServer connected callback
  -> NewIMBuffWriter
  -> WriteUInt*/WriteStr/WriteBin
  -> IMP_SendBuffer2NS
  -> server response reader
  -> DecryptBuffer if enabled
  -> ReadUInt*/ReadStr/ReadBin
  -> main-module ProcessServerCmd / OnServerCmd
  -> map id and position handling
```

This is a static candidate path, not a replay recipe. Login opcode, credentials, error codes, map id, and empty-map condition remain unknown.

## Next Static Targets

1. Trace xrefs from the `IMProtocol.dll` export table or import thunks into the main module.
2. Decompile `sub_10002EB0`, `sub_10001660`, `sub_10005F80`, `sub_10001D30`, `sub_10002CA0`, and `sub_10002070`.
3. In `mxmain.dll`, locate xrefs for `GetTargetServers`, `OnConnected`, `OnConnectFail`, `ProcessServerCmd`, and `%04d.map`.
4. Recover caller-side arguments to `IMP_ConnectNsServer` and `IMP_RefreshCryptKey`.
5. Confirm whether `203.70.8.205:3134` is used by the main game channel, the NsServer channel, or both.


## Continuation checkpoint: main-image import relation (2026-10-09)

### E-IDA-007: `mx.exe` imports the IMProtocol surface

A read-only local PE import-table check confirmed that the current `mx.exe` import descriptors include `IMProtocol.dll`. The named imports include `IMP_ConnectNsServer`, `IMP_RefreshCryptKey`, `IMP_UnConnectNsServer`, `IMP_NewIMBuffWriter`, `IMP_SendBuffer2NS`, integer/string/binary readers and writers, and encryption/decryption wrappers. The current `mx.exe` and `mxmain.dll` are byte-identical (SHA-256 `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`); `IMProtocol.dll` matches the previously surveyed digest `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c`. See [`evidence/E-IDA-007.md`](../evidence/E-IDA-007.md).

This raises confidence in a static dependency link between the main client image and the `IMProtocol.dll` API surface. It does **not** establish which functions call the imports, whether they are invoked in a real session, what arguments they receive, or whether the `NsServer` path is the main game-login channel rather than an auxiliary/IM service. No direct call-site xref is recorded from this check.

### Analysis backend status

The REA MCP tools were present, but `open_binary` could not bind the supplied PE to any native provider: Ghidra is not configured, the Hopper launcher is missing, and the IDA MCP configuration is absent. The failed open produced no function analysis; the diagnostic is recorded as [`E-REA-001`](../evidence/E-REA-001.md). Accordingly, the next function-level questions remain open: callers and actual call sites of `IMP_ConnectNsServer` / `IMP_SendBuffer2NS`, the source of endpoint and port values, and the relationship between this API and `Connect` / `PacketPrepare` / `PacketSend` in the main image.


## Ghidra continuation: NsServer connection path (2026-10-09)

REA-Ghidra is now available with Ghidra 12.1.4. The earlier `E-REA-001` provider-unavailable note is a historical diagnostic; this continuation supersedes its availability status, not its observation at the time. Detailed raw results and Evidence IDs are in [`E-REA-002`](../evidence/E-REA-002.md) and [`rea-ghidra-improtocol-20261009-1244.json`](../evidence/rea-ghidra-improtocol-20261009-1244.json).

### What the DLL establishes

Ghidra follows `IMP_ConnectNsServer` at `0x10003000` into `FUN_10001660` and `FUN_10005cb0`. The latter initializes a socket object, calls its virtual method at `+0x10` with the parsed host and forwarded connection value, and emits the format string `ConnectNsServer ip:%s, port:%d`.

The callee `FUN_10004920` has two static branches. Its numeric-address branch calls WS2_32 ordinal 11 on the host value, then—when that result is not `-1`—passes the port value to the import slot at `0x1001f188`, constructs an `AF_INET` address (`2`), and calls the import slot at `0x1001f1a0` with a 16-byte address structure. The existing interface survey maps those slots to `htons` and `connect`, respectively. This confirms the DLL's TCP connection plumbing and the port byte-order operation on the direct-address branch; it does **not** identify a client-side caller or prove this is the main game-login channel.

The hostname branch prepares a resolution buffer and passes message `0x502` to WS2_32 ordinal 103. `FUN_10004a60` separately registers async socket notifications using ordinal 101, message base `context+0x503`, and mask `0x3f`. These signatures are consistent with asynchronous hostname resolution and socket-event notification, but the current evidence does not identify the complete message dispatcher or prove the asynchronous resolution completion path.

### Main-image status and next checks

Ghidra address-xref queries against the `mx.exe` IAT slots for `IMP_ConnectNsServer`, `IMP_SendBuffer2NS`, and selected writer APIs returned no direct code references in this analysis. The import descriptors still prove a static dependency. An empty direct-xref result is not proof of no runtime use; indirect dispatch, dynamically resolved paths, or analysis coverage may be involved. Accordingly, the earlier assumption that the API is necessarily called through an obvious direct IAT call remains unverified.

Next offline targets:

1. Locate the handler for messages `0x502` and `0x503` and connect it to the socket object's completion/error callbacks.
2. Inspect main-image reads/writes and indirect-call paths involving the imported IAT slots; correlate with `server.ini` parsing and endpoint selection without attempting an external connection.
3. Trace `IMP_NewIMBuffWriter` / `IMP_Write*` / `IMP_SendBuffer2NS` through any resolved caller to distinguish server-list, login, and auxiliary `NsServer` traffic.
4. Keep login opcode, frame structure, authentication result, character/world state, and map-entry protocol unknown until direct evidence is obtained.
