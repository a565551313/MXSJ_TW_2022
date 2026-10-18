'use strict';
const $ = id => document.getElementById(id);
let csrf = '', state = null, logs = null, dirty = false, contentDirty = false, settingsDirty = false;
function message(text) { $('message').textContent = text; }
async function api(path, data) {
  const options = { credentials: 'same-origin', headers: {} };
  if (data !== undefined) {
    options.method = 'POST'; options.headers['Content-Type'] = 'application/json';
    options.headers['X-CSRF-Token'] = csrf; options.body = JSON.stringify(data);
  }
  const controls = data === undefined && path !== 'state' ? [] : Array.from(document.querySelectorAll('#workspace input, #workspace textarea, #workspace select, #workspace button')).map(element => [element, element.disabled]);
  controls.forEach(([element]) => element.disabled = true);
  let response, result;
  try { response = await fetch('/api/' + path, options); result = await response.json(); }
  finally { controls.forEach(([element, disabled]) => element.disabled = disabled); }
  if (!response.ok) {
    if (response.status === 401) { $('login').hidden = false; $('workspace').hidden = true; csrf = ''; }
    throw new Error(result.error || '请求失败');
  }
  return result;
}
function task(fn) { return async () => { try { await fn(); } catch (e) { message(e.message); } }; }
function row(values) {
  const tr = document.createElement('tr');
  values.forEach(value => { const td=document.createElement('td'), input=document.createElement('input'); input.value=String(value); input.addEventListener('input',()=>{dirty=true;contentDirty=true;}); td.append(input); tr.append(td); });
  const td=document.createElement('td');
  [['↑',()=>{if(tr.previousElementSibling)tr.parentNode.insertBefore(tr,tr.previousElementSibling);}],['↓',()=>{if(tr.nextElementSibling)tr.parentNode.insertBefore(tr.nextElementSibling,tr);}],['删除',()=>tr.remove()]].forEach(([label,action])=>{const b=document.createElement('button');b.textContent=label;b.onclick=()=>{action();dirty=true;contentDirty=true;};td.append(b);});
  tr.append(td); $('servers').append(tr);
}
function content() {
  const groups = new Map();
  for (const tr of $('servers').children) {
    const v=Array.from(tr.querySelectorAll('input'),i=>i.value);
    if(!groups.has(v[0]))groups.set(v[0],[]);
    groups.get(v[0]).push({name:v[1],ip:v[2],port:Number(v[3]),reserve:v[4],type:v[5]});
  }
  return {news:$('news').value,service:$('service').value,groups:Array.from(groups,([name,servers])=>({name,servers}))};
}
function paint(next) {
  state=next; dirty=false; contentDirty=false; settingsDirty=false;
  $('news').value=next.draft.news; $('service').value=next.draft.service;
  $('servers').replaceChildren();
  next.draft.groups.forEach(g=>g.servers.forEach(s=>row([g.name,s.name,s.ip,s.port,s.reserve,s.type])));
  $('settings-json').value=JSON.stringify(next.settings,null,2);
  const labels={running:'运行中',paused:'已暂停',stopped:'已停止',starting:'启动中',stopping:'停止中'};
  $('status').textContent=`公开服务：${labels[next.services.public.status]}　后台：${labels[next.services.admin.status]}　版本：${next.active || '未发布'}`;
  $('summary').textContent=JSON.stringify({services:next.services,sessions:next.sessions,log_failures:next.logging.failures,logging_degraded:next.logging.degraded},null,2);
  $('releases').replaceChildren();next.releases.forEach(r=>{const o=document.createElement('option');o.value=r.id;o.textContent=`${r.id}  ${new Date(r.created*1000).toLocaleString()}${r.id===next.active?' [当前]':''}`;$('releases').append(o);});
  document.querySelectorAll('[data-control]').forEach(b=>{const s=next.services.public.status; b.disabled=next.services.admin.status==='paused'||(b.dataset.control==='start'?s!=='stopped':b.dataset.control==='resume'?s!=='paused':b.dataset.control==='pause'?s!=='running':s==='stopped');});
  ['save','build','activate','save-settings','revoke'].forEach(id=>$(id).disabled=next.services.admin.status==='paused');
}
async function load() { paint(await api('state')); }
$('login-form').onsubmit=async e=>{e.preventDefault();try{const password=$('password').value;$('password').value='';const r=await api('login',{password});csrf=r.csrf;$('login').hidden=true;$('workspace').hidden=false;await load();message('登录成功');}catch(err){message(err.message);}};
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('.page').forEach(p=>p.hidden=p.id!==b.dataset.tab);});
$('news').oninput=$('service').oninput=()=>{dirty=true;contentDirty=true;};
$('settings-json').oninput=()=>{dirty=true;settingsDirty=true;};
$('add-server').onclick=()=>{row(['測試區','新區服','127.0.0.1',3134,'3','&']);dirty=true;contentDirty=true;};
$('reload').onclick=task(async()=>{if(!dirty||confirm('重新加载会放弃未保存修改，继续？')){await load();message('已重新加载');}});
$('save').onclick=task(async()=>{if(settingsDirty)throw new Error('请先处理未保存的设置，避免覆盖');const r=await api('draft',{content:content(),revision:state.revision});paint(r);message('草稿已保存，尚未发布');});
$('preview').onclick=task(async()=>{$('preview-output').textContent=JSON.stringify(await api('preview',{content:content()}),null,2);message('格式校验通过；并非原生界面验收');});
$('build').onclick=task(async()=>{if(dirty)throw new Error('请先保存或重新加载未保存内容');paint(await api('build',{revision:state.revision}));message('版本已生成，尚未切换');});
$('diff').onclick=task(async()=>{if(!$('releases').value)throw new Error('请选择版本');$('diff-output').textContent=JSON.stringify(await api('preview',{id:$('releases').value}),null,2);});
$('activate').onclick=task(async()=>{if(dirty)throw new Error('请先处理未保存修改');if($('releases').value&&confirm('确认切换公开内容到所选版本？')){paint(await api('activate',{id:$('releases').value,revision:state.revision}));message('已切换发布版本');}});
$('save-settings').onclick=task(async()=>{if(contentDirty)throw new Error('请先处理未保存的内容，避免覆盖');if(confirm('访问规则立即生效，可能锁住当前会话；监听地址变更需重启。确认保存？')){paint(await api('settings',{settings:JSON.parse($('settings-json').value),revision:state.revision}));message('已保存；监听变更需重启');}});
document.querySelectorAll('[data-control]').forEach(b=>b.onclick=task(async()=>{if(dirty)throw new Error('请先处理未保存修改');if(['stop','restart'].includes(b.dataset.control)&&!confirm('确认影响公开服务的现有连接？'))return;paint(await api('control',{action:b.dataset.control}));}));
$('logout').onclick=task(async()=>{await api('logout',{});csrf='';$('workspace').hidden=true;$('login').hidden=false;message('已退出');});
$('revoke').onclick=task(async()=>{if(confirm('退出全部后台会话，包括当前会话？')){await api('revoke',{});csrf='';$('workspace').hidden=true;$('login').hidden=false;}});
function filterLogs(){const text=JSON.stringify(logs,null,2);$('log-output').textContent=$('log-filter').value?text.split('\n').filter(line=>line.includes($('log-filter').value)).join('\n'):text;}
$('load-logs').onclick=task(async()=>{logs=await api('logs');filterLogs();});$('log-filter').oninput=filterLogs;
$('export-logs').onclick=task(async()=>{logs=await api('logs');const url=URL.createObjectURL(new Blob([JSON.stringify(logs,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='web-server-logs.json';a.click();URL.revokeObjectURL(url);});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
(async()=>{try{const s=await api('session');csrf=s.csrf;$('login').hidden=true;$('workspace').hidden=false;await load();}catch{message('请登录后管理');}})();
