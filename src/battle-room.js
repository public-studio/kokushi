import { DurableObject } from 'cloudflare:workers';
import { BattleGame } from './battle-rules.js';
function lobbyAction(state,player,cmd,t,makeRoom){
const id=player.id,name=player.name,op=cmd.action;state.online??={};state.invites??=[];state.matches??=[];
for(const [key,v] of Object.entries(state.online))if(t-v.seen>8000)delete state.online[key];
state.invites=state.invites.filter(v=>v.until>t&&state.online[v.from]&&state.online[v.to]);state.matches=state.matches.filter(v=>v.until>t);
const involves=v=>v.from===id||v.to===id,matchFor=k=>state.matches.find(v=>v.from===k||v.to===k);
const busy=k=>!!matchFor(k)||state.invites.some(v=>v.from===k||v.to===k);
let error='';
if(op==='leave'){delete state.online[id];state.invites=state.invites.filter(v=>!involves(v));state.matches=state.matches.filter(v=>!involves(v));return {ok:true};}
state.online[id]={name,seen:t};
if(op==='invite'){
const target=Object.entries(state.online).find(([k,v])=>k!==id&&v.name===cmd.target&&!busy(k));
if(busy(id))error='すでに対戦の申し込みがあります';
else if(!target||cmd.target===name)error='相手は現在対戦できません';
else state.invites.push({from:id,to:target[0],fromName:name,toName:target[1].name,until:t+30000});
}else if(op==='accept'||op==='decline'||op==='cancel'){
const v=state.invites.find(x=>op==='cancel'?x.from===id:x.to===id);
if(!v)error='申し込みは終了しました';
else{state.invites=state.invites.filter(x=>x!==v);if(op==='accept'){if(!state.online[v.from]||matchFor(v.from)||matchFor(id))error='相手は現在対戦できません';else state.matches.push({...v,room:makeRoom(),until:t+90000});}}
}else if(op!=='status')error='操作が不正です';
const invite=state.invites.find(involves),match=matchFor(id),names=['HIRO','AKI','YUU','TOMO',...Object.values(state.online).map(v=>v.name)];
return {name,players:[...new Set(names)].filter(n=>n!==name).map(n=>({name:n,online:Object.entries(state.online).some(([k,v])=>k!==id&&v.name===n&&!busy(k))})),incoming:invite?.to===id?invite.fromName:null,outgoing:invite?.from===id?invite.toName:null,room:match?.room||null,error};
}
export { lobbyAction };

export class BattleRoom extends DurableObject {
constructor(ctx,env){super(ctx,env);this.sockets=[];this.game=null;this.timer=null;this.created=Date.now();}
send(ws,data){try{ws.send(JSON.stringify(data))}catch{}}
broadcast(data){for(const s of this.sockets)if(s)this.send(s.ws,data)}
cleanup(){if(this.timer){clearInterval(this.timer);this.timer=null;}for(const s of this.sockets)if(s){try{s.ws.close(1000,'room ended')}catch{}}this.sockets=[];this.game=null;}
async lobby(player,cmd){const sql=this.ctx.storage.sql;sql.exec("CREATE TABLE IF NOT EXISTS lobby_state (id INTEGER PRIMARY KEY, data TEXT NOT NULL)");const rows=sql.exec("SELECT data FROM lobby_state WHERE id=1").toArray();const state=rows.length?JSON.parse(rows[0].data):{};const result=lobbyAction(state,player,cmd,Date.now(),()=>crypto.randomUUID().replace(/-/g,'').slice(0,10));sql.exec("INSERT INTO lobby_state(id,data) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",JSON.stringify(state));return result;}
async fetch(request){
if(request.headers.get('Upgrade')?.toLowerCase()!=='websocket')return new Response('WebSocket required',{status:426});
if(this.game||this.sockets.filter(Boolean).length>=2)return new Response('Room full',{status:409});
const u=new URL(request.url),name=u.searchParams.get('name')||'P',handicap=Number(u.searchParams.get('handicap')||1);
if(!/^[A-Z0-9]{1,4}$/.test(name)||![1,1.3,1.6,1.9,2.1].includes(handicap))return new Response('Invalid player',{status:400});
const [client,ws]=Object.values(new WebSocketPair());ws.accept();let i=this.sockets.findIndex(v=>!v);if(i<0)i=this.sockets.length;this.sockets[i]={ws,name,handicap};this.send(ws,{type:'joined',i});
const close=()=>{if(this.sockets[i]?.ws!==ws)return;this.sockets[i]=null;if(this.game&&!this.game.finished){this.game.finish('DISCONNECT',1-i);this.publish();}if(!this.sockets.some(Boolean))this.cleanup();};
ws.addEventListener('close',close);ws.addEventListener('error',close);
ws.addEventListener('message',e=>{if(typeof e.data!=='string'||e.data.length>512||this.sockets[i]?.ws!==ws)return;let m;try{m=JSON.parse(e.data)}catch{return}if(!m||typeof m!=='object')return;if(m.type==='ping'){this.send(ws,{type:'pong',echo:m.echo,now:Date.now()});return;}if(this.game&&!this.game.finished){this.game.input(i,m,Date.now());this.publish();}});
if(this.sockets.filter(Boolean).length===2){this.game=new BattleGame(this.sockets.map(x=>x.name),this.sockets.map(x=>x.handicap),Date.now()+3000);this.publish();}
else this.send(ws,{type:'waiting'});
if(!this.timer){this.created=Date.now();this.timer=setInterval(()=>{if(this.game){this.game.tick(Date.now());this.publish();}else if(Date.now()-this.created>120000){this.broadcast({type:'expired'});this.cleanup();}},100);}
return new Response(null,{status:101,webSocket:client});
}
publish(){if(!this.game)return;const t=Date.now();const events=this.game.events.splice(0);for(const e of events)this.broadcast(e);for(let i=0;i<2;i++)if(this.sockets[i])this.send(this.sockets[i].ws,this.game.snapshot(i,t));if(this.game.finished&&this.timer){clearInterval(this.timer);this.timer=null;const finishedGame=this.game;setTimeout(()=>{if(this.game===finishedGame)this.cleanup()},5000);}}
}
