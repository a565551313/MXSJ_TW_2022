# 只读观察器的启动程序（Windows 上运行，需要 32 位 Python，因为 mx.exe 是 32 位）。
# 用法：python observe.py mx.exe
# 输出：同目录下的 observe-log.jsonl（每行一条记录）
# 草稿，尚未在 Windows 上运行验证。
import sys
import json
import time
import frida

PROC = sys.argv[1] if len(sys.argv) > 1 else 'mx.exe'
OUT = 'observe-log.jsonl'

with open('observe.js', encoding='utf-8') as fh:
    SCRIPT_SRC = fh.read()

log = open(OUT, 'a', encoding='utf-8')

def on_message(msg, data):
    if msg.get('type') == 'send':
        rec = msg['payload']
        rec['host_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        log.write(json.dumps(rec, ensure_ascii=False) + '\n')
        log.flush()
        if rec.get('event') in ('hooked', 'missing', 'info'):
            print(rec)
    else:
        print('脚本错误:', msg)

device = frida.get_local_device()
session = device.attach(PROC)
script = session.create_script(SCRIPT_SRC)
script.on('message', on_message)
script.load()
print('已挂载到', PROC, '，记录写入', OUT, '。按 Ctrl+C 停止。')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    log.close()
    print('已停止。')
