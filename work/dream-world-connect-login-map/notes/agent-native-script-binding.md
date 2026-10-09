# Native Event -> Python Script Binding Audit

- Case: `dream-world-connect-login-map`
- Scope: `0x2714 -> OnServerCmd(int) -> entry 516 candidate methods`
- Date: 2026-10-09 Asia/Shanghai
- Analyst role: native event/script binding
- Analysis mode: read-only static analysis
- Main sample: `D:\Lager\夢想世界\mx.exe`
- Main sample SHA-256: `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05036fdccdDF52FBE424D`
- IDA Pro: `D:\IDA Professional 9.4`
- IDA MCP: local HTTP server on `127.0.0.1:13337`
- IDA session: `c3546ce9`
- Ghidra source bundle: `evidence/rea-ghidra-mx-exe-20261009-1229.json`
- Script payload examined: `notes/entry516-expanded.bin`, 17,234 bytes

## Executive Result

The native side is independently confirmed:

```text
event 0x2714
  -> sub_4AC590(param_1, param_2)
  -> case 10004
  -> sub_4AC030(param_2)
  -> IMP_ReadUInt16(param_2)
  -> zero-extend returned uint16
  -> generic Python method bridge sub_4576B0(..., "OnServerCmd", ..., value)
```

`sub_4AC030` also stores the original event argument at `this+0x0c`. The bridge receives the 16-bit value as one integer argument using the format-string data at `0x6BB1C4` and the method name at `0x6BB1C8`.

The script side remains only partially connected. Existing handoff evidence reports that FLS entry 516 contains a Python 2.7 marshal tree with `CMXNet.OnServerCmd`, `ProcessServerCmd`, and `C2STransferServer`. The native bridge does not directly reference the `ProcessServerCmd` string at `0x6B4C74`; IDA's xref query returns no code xref for that string. Therefore the current evidence proves the native callback name and argument shape, but does not prove that entry 516's `ProcessServerCmd` is the callback implementation, nor which command value causes the login-page transition.

## Evidence -> Finding -> Path

### EF-NSB-001: Event dispatcher maps `0x2714` to the server-command helper

**Evidence**

- Ghidra function record for `FUN_004ac590` in `E-REA-003` / `rea-ghidra-mx-exe-20261009-1229.json`.
- Independent IDA Pro decompilation of `sub_4AC590` at `0x004AC590`, IDA session `c3546ce9`.
- IDA recovered switch cases:
  - `10001` (`0x2711`) -> method `OnConnected`
  - `10002` (`0x2712`) -> method `OnError`
  - `10003` (`0x2713`) -> conditional indirect callback
  - `10004` (`0x2714`) -> `sub_4AC030(param_2)`

**Finding**

The client statically separates connection-success handling from server-command handling. `0x2714` is not the `OnConnected` path; it is a distinct event branch that forwards its second argument to `sub_4AC030`.

**Path**

```text
sub_4AC590(param_1, param_2)
  switch (param_1)
    case 0x2714:
      sub_4AC030(param_2)
```

**Confidence**: high, observed independently in Ghidra and IDA.

### EF-NSB-002: `sub_4AC030` reads one 16-bit value and calls native method bridge

**Evidence**

- IDA decompilation and assembly for `sub_4AC030` at `0x004AC030`.
- IDA import query reports `IMP_ReadUInt16` at `0x00E1B288` in module `IMProtocol`.
- IAT slot used by the function is `dword_6B020C` at `0x006B020C`.
- Existing `E-REA-004` records the static slot-to-`IMP_ReadUInt16` mapping and the same instruction sequence.

**Finding**

The helper consumes the event argument as a protocol reader/context, invokes the imported 16-bit reader, and zero-extends the returned `AX` value to a 32-bit integer before entering the Python bridge. The callback's effective script argument is therefore:

```text
OnServerCmd(uint16_value_as_int)
```

The exact wire command value is not recovered here.

**Path**

IDA assembly at `0x004AC030`:

```text
004AC038  push esi
004AC039  mov  edi, ecx
004AC03B  call ds:dword_6B020C
004AC041  movzx eax, ax
004AC044  push eax
004AC045  push offset unk_6BB1C4
004AC04A  push 0
004AC04C  push offset unk_6BB1A6
004AC051  push offset aOnservercmd_0
004AC056  push dword ptr [edi+4]
004AC059  mov  [edi+0Ch], esi
004AC05C  call sub_4576B0
```

IDA pseudocode:

```c
int __thiscall sub_4AC030(_DWORD *this, int a2)
{
  char v3;
  int v5;

  v3 = MEMORY[0x3D81AE](a1: a2);
  v5 = *(this + 1);
  *(this + 3) = a2;
  return sub_4576B0(
      a1: v5,
      a2: "OnServerCmd",
      a3: &unk_6BB1A6,
      a4: 0,
      a5: &unk_6BB1C4,
      a6: v3);
}
```

The pseudocode's `MEMORY[0x3D81AE]` is IDA's unresolved display of the imported function pointer. Existing PE/import evidence identifies the slot as `IMP_ReadUInt16`; the displayed immediate address itself is not a mapped image address and must not be treated as a direct code address.

**Confidence**: high for the read/zero-extension/bridge sequence; medium-high for the import name because the slot mapping is static rather than observed at runtime.

### EF-NSB-003: `sub_4576B0` is a generic Python method lookup/invocation bridge

**Evidence**

- IDA decompilation of `sub_4576B0` at `0x004576B0`.
- IDA caller list includes `sub_4AC030` at call site `0x004AC05C`.
- The function calls `sub_4D7240` to obtain a method/object handle, then `sub_457E60` to invoke it. On failure it emits `Can't get method:{}` and returns `-1`.
- Existing `E-REA-004` identifies this as the generic Python-method dispatcher.

**Finding**

`sub_4AC030` does not call a statically named Python function such as `ProcessServerCmd`. It supplies the literal method name `OnServerCmd` to a generic lookup/dispatch routine. The actual Python object and method resolution occur through the object handle at `this+4` and the helpers below `sub_4576B0`.

**Path**

```text
sub_4AC030
  -> sub_4576B0(object_handle, "OnServerCmd", arg-format/context, int_value)
     -> sub_4D7240(object_handle, method_name)
     -> sub_457E60(method_handle, ...)
```

IDA's recovered variadic prototype is:

```text
int sub_4576B0(int object_handle, ...)
```

The call convention and variadic argument interpretation are decompiler artifacts; the method name and caller/callee addresses are directly observed.

**Confidence**: high for generic lookup/invocation behavior; exact Python object identity remains unresolved.

### EF-NSB-004: Native string references identify `OnServerCmd`, but not `ProcessServerCmd`

**Evidence**

- IDA string query:
  - `0x006BB138`: `OnServerCmd`
  - `0x006BB1C8`: `OnServerCmd`
  - `0x006B4C74`: `ProcessServerCmd`
- IDA xrefs:
  - `0x006BB1C8` <- data reference at `0x004AC051` in `sub_4AC030`
  - `0x006BB1A6` <- data reference at `0x004AC04C` in `sub_4AC030`
  - `0x006BB1C4` <- data reference at `0x004AC045` in `sub_4AC030`
  - `0x006B4C74` -> no cross-references returned by IDA
- Ghidra independently reports no direct xref to the `ProcessServerCmd` string; see `E-REA-003` and `E-REA-006`.

**Finding**

The native callback is proven to pass the literal name `OnServerCmd` at `0x006BB1C8`. `ProcessServerCmd` is only a string object in the native image according to current xref analysis. The shared names in the native binary and script payload are insufficient to establish aliasing, wrapper order, or implementation identity.

**Path**

```text
native literal @ 0x6BB1C8 ("OnServerCmd")
  -> sub_4AC030 @ 0x4AC051
  -> generic Python lookup

native literal @ 0x6B4C74 ("ProcessServerCmd")
  -> no direct xref observed
```

**Confidence**: high for the xref result; negative xref is bounded by the analyzed IDA/Ghidra databases and does not exclude generated strings, indirect references, or data outside the analyzed image.

### EF-NSB-005: Entry 516 contains a candidate script module, but the binding is not independently proven

**Evidence**

- `E-REA-008` reports a five-layer XOR/decode result yielding a Python 2.7 marshal tree with 59 code objects, including:
  - `CMXNet.OnServerCmd`
  - `ProcessServerCmd`
  - `C2STransferServer`
- `E-REA-006` records entry index 516, record ID `0x183e0854`, module marker `SCRIPT|LOGIN|NETSERVER`, and nearby names `ReselectServerConnect`, `DgwConnectTest`, `ProcessServerCmd`, `serverid`, and `pwd`.
- Local artifact `notes/entry516-expanded.bin` is 17,234 bytes and starts with transformed/obfuscated bytes. A direct ASCII scan of this expanded artifact did not find the plain method names, which is consistent with the unresolved second-layer encoding and does not contradict the handoff's decoded-tree report.
- `E-REA-008` explicitly labels the script-tree result as user-provided handoff evidence and states that the non-standard `co_code` encoding and pre-execution conversion layer remain unresolved.

**Finding**

Entry 516 is a strong candidate for the login/server-selection script module, and its reported code-object names are relevant to the native callback. However, no current evidence links the native object's `OnServerCmd` lookup to the specific code object named `CMXNet.OnServerCmd`, and no evidence proves that `CMXNet.OnServerCmd` immediately calls the code object named `ProcessServerCmd`.

The strongest present statement is:

```text
native callback name == "OnServerCmd"
entry 516 reportedly contains a method named "CMXNet.OnServerCmd"
entry 516 reportedly contains a function named "ProcessServerCmd"
binding and call relationship remain unproven
```

**Confidence**: high for the native callback name; medium for entry 516 contents because the decode report was not independently reproduced in this task; low for the cross-layer binding.

## Recovered Native Object/Argument Model

The native helper uses the following fields on its `this` object:

| Field | Use | Evidence |
|---|---|---|
| `this+0x04` | Python object/receiver handle passed to `sub_4576B0` | `sub_4AC030` at `0x4AC056`; IDA/Ghidra |
| `this+0x08` | Connection/error state byte used by `0x2712` and `0x2713` branches | `sub_4AC590` at `0x4AC5E8`, `0x4AC5FC` |
| `this+0x0C` | Stores original `0x2714` event argument/context | `sub_4AC030` at `0x4AC059` |

The callback argument is not the original context pointer. It is the 16-bit value returned by `IMP_ReadUInt16`, converted to a 32-bit Python integer by `MOVZX EAX, AX`.

## What This Changes for Protocol Reconstruction

The first server-command response needed to drive the script layer must provide a readable 16-bit field at the reader position represented by the `param_2` context passed into `sub_4AC030`. The value is then delivered to `OnServerCmd(int)`.

This does not yet determine:

- the outer frame length or encryption state;
- the reader cursor before the 16-bit command field;
- the command value used for server selection/login;
- additional fields consumed before or after `OnServerCmd`;
- whether `CMXNet.OnServerCmd` dispatches to `ProcessServerCmd`;
- the condition that changes the connecting dialog to the account-login page;
- the response sequence required for character/world/map entry.

The native helper stores the original reader/context argument after reading the command, so subsequent script/native code may retain a handle to the packet reader or event object. The current static evidence does not show whether that stored field is read by the script callback or by another native path.

## Unconfirmed Points and Required Verification

1. **Import-slot runtime binding**
   - Static mapping: `dword_6B020C` -> `IMP_ReadUInt16`.
   - Runtime invocation has not been observed.

2. **Python receiver identity**
   - `this+4` is passed to the generic bridge.
   - The exact Python object/class/module registration site is not located.

3. **Entry 516 loader and transform**
   - The FLS index/decompression layer is validated elsewhere.
   - The five-layer XOR/marshal-tree result is recorded from `E-REA-008`.
   - The non-standard `co_code` conversion layer and code-resource loader remain unresolved.

4. **`CMXNet.OnServerCmd` versus `ProcessServerCmd`**
   - The names coexist in the reported entry-516 tree.
   - No recovered call edge or bytecode control flow currently proves their relationship.

5. **Command semantics**
   - No command value from the 16-bit field is confirmed.
   - `0x2714` is a native event ID, not the inner server-command value.

6. **UI transition**
   - The native branch only proves dispatch to `OnServerCmd`.
   - It does not prove the account-login transition or entry into a map.

## Recommended Next Static/Dynamic Handoff

The next investigation should target the generic bridge and script registration boundary, in this order:

1. Analyze `sub_4D7240` and `sub_457E60` to recover how the receiver object and method name are resolved.
2. Trace writes/initialization of the object field at `this+4`, looking for the module/class registration that loads the login script object.
3. Recover the custom `co_code` conversion layer for entry 516, then map `CMXNet.OnServerCmd` bytecode to its constants and calls.
4. Identify whether `CMXNet.OnServerCmd` invokes `ProcessServerCmd`, and record the exact integer comparisons or dispatch table.
5. Only after the command value and reader position are known, build a local responder test that returns a structurally valid frame and records the resulting callback/UI state.

## Bottom Line

The native half of the requested chain is now independently verified in IDA and Ghidra:

```text
0x2714
  -> sub_4AC590
  -> sub_4AC030
  -> IMP_ReadUInt16
  -> OnServerCmd(int)
```

The script half is a well-supported candidate, not a completed binding:

```text
entry 516 reportedly contains CMXNet.OnServerCmd / ProcessServerCmd / C2STransferServer
  but native registration, method-object identity, call edge, command values,
  and login/map transition remain unresolved
```

No guessed TCP response or command value should be promoted from this analysis.
