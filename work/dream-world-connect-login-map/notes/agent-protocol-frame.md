# Agent Protocol/Frame Analysis

- Case: `dream-world-connect-login-map`
- Work directory: `D:\Lager\夢想世界\work\dream-world-connect-login-map`
- Date: 2026-10-09 (Asia/Shanghai)
- Scope: offline static analysis plus a design for a loopback-only responsive TCP harness
- Modified outside this agent output: none

## Executive Summary

`IMProtocol.dll` contains a native TCP connection and message-buffer API. The
strongest static frame observation is in `IMP_SendBuffer2NS`:

1. A buffer object is expected at the third argument.
2. The data pointer is read at buffer offset `0x10`.
3. The current buffer length is read at offset `0x18`.
4. The length must be greater than `2`.
5. If the first 16-bit value in the buffer is zero, the function writes
   `htons(length)` into that first field.
6. The buffer is passed to the internal send path, which logs
   `C2NSBuffer>>> len:%d` and dispatches through a socket object's virtual
   send method.

This supports a provisional transport framing rule:

```text
uint16_be total_length
byte[total_length - 2] opaque_payload
```

The rule is provisional. Static evidence does not establish whether the
length includes the two-byte prefix in every path, whether encryption changes
the length, or how the receive path accumulates and validates frames.

## Evidence Reviewed

### `IMProtocol.dll`

- SHA-256:
  `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c`
- 32-bit PE, image base `0x10000000`.
- IDA interface notes identify exports:
  `IMP_ConnectNsServer`, `IMP_UnConnectNsServer`,
  `IMP_RefreshCryptKey`, `IMP_EncryptBuffer`, `IMP_DecryptBuffer`,
  `IMP_SendBuffer2NS`, `IMP_ReadUInt64/32/16/8`, `IMP_ReadStr/ReadBin`,
  `IMP_NewIMBuffWriter`, `IMP_FreeIMBuffWriter`,
  `IMP_WriteUInt64/32/16/8`, and `IMP_WriteStr/WriteBin`.
- Ghidra evidence `E-REA-002` confirms a static connection path:
  `IMP_ConnectNsServer -> FUN_10001660 -> FUN_10005cb0`.

### `mx.exe` / `mxmain.dll`

- Both files are byte-identical in the current tree:
  SHA-256 `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`.
- PE import evidence `E-IDA-007` lists the IMProtocol connection, send,
  reader/writer, and crypto APIs in the `mx.exe` import descriptor.
- The import table establishes a static dependency only. It does not establish
  that a particular API was executed, its arguments, call ordering, or channel
  role.

## Static Findings

### Connection path

`IMP_ConnectNsServer` performs `WSAStartup(0x202, ...)`, processes a source
string through `FUN_10002eb0`, and calls `FUN_10001660`.
`FUN_10001660` reaches `FUN_10005cb0`, which initializes a socket object and
calls a virtual connection method. The socket path logs:
`ConnectNsServer ip:%s, port:%d`.

In `FUN_10004920`, the numeric-address branch:

- calls a WS2_32 ordinal corresponding to numeric address conversion;
- passes the port through the import slot identified in the existing notes as
  `htons`;
- constructs an IPv4 `sockaddr` with address family `2`;
- calls the import slot identified as `connect` with a 16-byte address object.

The hostname branch uses asynchronous name resolution with message `0x502`.
`FUN_10004a60` registers socket event notifications with message base
`context + 0x503` and mask `0x3f`. The message dispatcher and completion
handler are not recovered here.

### Import/export surface

The IMProtocol export/import surface is consistent with a native TCP protocol
library:

| Area | Static observation | Status |
|---|---|---|
| connect | Winsock startup, address setup, `connect` path | confirmed static |
| send | send API import plus socket virtual send path | confirmed static |
| receive | reader APIs exist; exact `recv` loop not located | open |
| integer fields | 8/16/32/64-bit readers and writers | confirmed API surface |
| string/binary fields | explicit-size read/write wrappers | confirmed API surface |
| encryption | encrypt/decrypt wrappers and key-refresh entry | confirmed API surface |
| login opcode | no direct evidence in this task | unknown |
| server response | no captured application response | unknown |

### Reader/writer and field boundaries

The reader/writer wrappers use explicit sizes for binary/string operations and
copy into internal buffer representations. This favors length-delimited fields
at the serialization layer, but the exact field encoding, string length width,
endianness, and command layout require caller analysis.

The integer function names identify width, not necessarily wire endianness.
`IMP_SendBuffer2NS` directly proves network-order conversion for the first
length field only.

### Encryption

`IMP_RefreshCryptKey` and the encrypt/decrypt wrappers are statically present.
The source string used by connection setup is also fed through a shared helper,
which suggests protocol-state or key-state initialization. The algorithm,
key derivation, encrypted region, IV/nonce, and ordering relative to the
length prefix remain unconfirmed.

Do not treat the following as protocol facts:

- a guessed command value;
- `PY_CODERESOURCE=8` as a network opcode;
- a response made only from the two-byte length field;
- the presence of a crypto export as proof that the first frame is encrypted.

## Existing Capture Interpretation

`E-LOOPBACK-001` and the existing capture server establish a useful baseline:
the listener accepted TCP connections, but the recorded streams contained no
application bytes. This does not prove that the client never sends data. The
server returned no application response, so the client may have been waiting
for a server event, selecting a different channel, or closing before its first
send.

The next experiment should therefore keep the same local endpoint but make the
listener response-capable while logging every byte and every framing decision.

## Responsive Loopback Harness

Artifact:
`notes/protocol-artifacts/responsive_loopback_harness.py`

The harness:

- binds only to `127.0.0.1`;
- accepts TCP connections on port `3134` by default;
- accumulates arbitrary TCP chunks before parsing;
- interprets the first two bytes as a provisional big-endian total length;
- rejects lengths below `2` or above `65535`;
- logs raw chunks and complete candidate frames;
- saves each raw stream;
- sends no response by default;
- sends a response only when `--response-hex` is explicitly supplied.

Example capture-only run:

```powershell
python .\notes\protocol-artifacts\responsive_loopback_harness.py
```

Example with a deliberately explicit test response:

```powershell
python .\notes\protocol-artifacts\responsive_loopback_harness.py `
  --response-hex 00020000
```

The example response is a test byte sequence, not a claimed game-server
response. Replace it only after a client-generated request and a corresponding
response condition have been observed.

## Verification Plan

### Phase A: prove the harness itself

Use a synthetic local client that sends:

```text
0006 11223344
```

possibly split across multiple `send()` calls. Confirm that the harness emits
one complete frame with declared length `6`, saves the exact stream, and
returns the explicit response once.

### Phase B: client connection and first bytes

1. Use a copied client configuration pointing to `127.0.0.1:3134`.
2. Start the harness in capture-only mode.
3. Start the client and record UI/log transitions.
4. Repeat with a fixed response only after a request is observed.
5. Compare connection attempts, raw bytes, close timing, and client state.

### Phase C: separate framing from crypto

For each observed stream:

1. Check whether the first two bytes equal the observed TCP-frame length.
2. Check whether multiple frames arrive in one `recv`.
3. Check whether one frame is split across multiple `recv` calls.
4. Compare repeated requests for stable command bytes and changing fields.
5. Only then test whether `IMP_DecryptBuffer` is applied before
   `IMP_ReadUInt16`/`IMP_ReadStr`.

### Phase D: response-state mapping

Do not label a response as login-success, character-ready, or map-entry until
the client-side observable changes correlate with the sent bytes. Record:

```text
request frame hex
response frame hex
client log/UI state
socket close/reconnect behavior
candidate command field
confidence and unresolved alternatives
```

## Static Confirmation vs Runtime Verification

### Static confirmation already available

- 32-bit PE architecture and sample hashes.
- IMProtocol export surface.
- Main-image import dependency on IMProtocol.
- `IMP_ConnectNsServer` TCP setup path.
- network-order write of the provisional two-byte length in
  `IMP_SendBuffer2NS`.
- buffer pointer/length offsets used by the send wrapper.
- existence of integer, string/binary, and crypto API layers.
- local-only harness design and parser behavior.

### Requires runtime or additional caller analysis

- whether `NsServer` is the main login channel;
- actual host/port values used by the client at runtime;
- whether the client sends an application frame immediately after connect;
- exact receive loop and stream reassembly behavior;
- whether length includes the prefix after encryption;
- command/opcode and field layout;
- crypto algorithm, key material, and encrypted region;
- authentication success response;
- character/world-ready response;
- map ID and empty-map entry condition.

## Handoff Recommendations

1. Keep the current two-byte big-endian rule labeled provisional.
2. Use the responsive harness only after capturing a real client request.
3. Add a packet log with timestamps and client UI state for every test.
4. Trace `IMP_EncryptBuffer`/`IMP_DecryptBuffer` callers and the receive-side
   `recv`/buffer accumulation path before implementing a server codec.
5. Correlate `IMP_SendBuffer2NS` with the main-image `PacketPrepare`,
   `PacketAdd*`, `PacketSend`, `ProcessServerCmd`, and `OnServerCmd` paths.
6. Preserve raw captures and hashes; do not replace the original
   capture-only evidence with synthetic responses.
