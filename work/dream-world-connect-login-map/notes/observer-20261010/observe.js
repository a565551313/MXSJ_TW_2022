// 只读观察器（Frida 脚本）。只记录调用与参数，不修改任何参数或返回值，不修改游戏文件。
// 目标：确认客户端是否调用了 IMProtocol 的发包/密钥函数，以及 ws2_32 的 connect/send。
// 草稿，尚未在 Windows 上运行验证。

const IMP_EXPORTS = [
  'IMP_ConnectNsServer',
  'IMP_SendBuffer2NS',
  'IMP_RefreshCryptKey',
  'IMP_EncryptBuffer',
  'IMP_DecryptBuffer',
  'IMP_UnConnectNsServer'
];
const DUMP_BYTES = 128;

function hexOf(p, n) {
  try {
    if (p.isNull()) return null;
    const buf = p.readByteArray(n);
    if (buf === null) return null;
    return Array.from(new Uint8Array(buf))
      .map(b => b.toString(16).padStart(2, '0')).join(' ');
  } catch (e) {
    return 'unreadable';
  }
}

function hookImp(name, addr) {
  Interceptor.attach(addr, {
    onEnter(args) {
      const rec = { event: 'enter', fn: name, tid: this.threadId, args: [] };
      for (let i = 0; i < 4; i++) {
        rec.args.push({ raw: args[i].toString(), hex: hexOf(args[i], DUMP_BYTES) });
      }
      send(rec);
    },
    onLeave(retval) {
      send({ event: 'leave', fn: name, tid: this.threadId, ret: retval.toString() });
    }
  });
}

function hookWinsock() {
  const ws2 = Process.findModuleByName('ws2_32.dll');
  const connectAddr = ws2 ? ws2.findExportByName('connect') : null;
  if (connectAddr) {
    Interceptor.attach(connectAddr, {
      onEnter(args) {
        // sockaddr_in: family(2) port(2, 大端) ip(4)
        const sa = args[1];
        let port = null, ip = null;
        try {
          const b = new Uint8Array(sa.readByteArray(8));
          port = (b[2] << 8) | b[3];
          ip = [b[4], b[5], b[6], b[7]].join('.');
        } catch (e) {}
        send({ event: 'enter', fn: 'ws2_32.connect', tid: this.threadId, ip: ip, port: port });
      }
    });
    send({ event: 'hooked', fn: 'ws2_32.connect' });
  }
  const sendAddr = ws2 ? ws2.findExportByName('send') : null;
  if (sendAddr) {
    Interceptor.attach(sendAddr, {
      onEnter(args) {
        const len = args[2].toInt32();
        send({ event: 'enter', fn: 'ws2_32.send', tid: this.threadId, len: len,
               hex: hexOf(args[1], Math.min(len, DUMP_BYTES)) });
      },
      onLeave(retval) {
        send({ event: 'leave', fn: 'ws2_32.send', tid: this.threadId, ret: retval.toInt32() });
      }
    });
    send({ event: 'hooked', fn: 'ws2_32.send' });
  }
}

let impHooked = false;
function tryHookImp() {
  if (impHooked) return;
  const m = Process.findModuleByName('IMProtocol.dll');
  if (!m) return;
  impHooked = true;
  for (const name of IMP_EXPORTS) {
    const addr = m.findExportByName(name);
    if (addr) {
      hookImp(name, addr);
      send({ event: 'hooked', fn: name, addr: addr.toString() });
    } else {
      send({ event: 'missing', fn: name });
    }
  }
}

hookWinsock();
send({ event: 'info', msg: '观察器已加载，等待 IMProtocol.dll 加载' });
setInterval(tryHookImp, 500);
