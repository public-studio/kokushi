import { DurableObject } from 'cloudflare:workers';
import { BattleGame } from './battle-rules.js';
export class BattleRoom extends DurableObject {
constructor(ctx,env){super(ctx,env);this.sockets=[];this.game=null;this.timer=null;this.created=Date.now();}
send(ws,data){try{ws.send(JSON.stringify(data))}catch{}}
broadcast(data){for(const s of this.sockets)if(s)this.send(s.ws,data)}
cleanup(){if(this.timer){clearInterval(this.timer);this.timer=null;}for(const s of this.sockets)if(s){try{s.ws.close(1000,'room ended')}catch{}}this.sockets=[];this.game=null;}
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
publish(){if(!this.game)return;const t=Date.now();const events=this.game.events.splice(0);for(const e of events)this.broadcast(e);for(let i=0;i<2;i++)if(this.sockets[i])this.send(this.sockets[i].ws,this.game.snapshot(i,t));if(this.game.finished&&this.timer){clearInterval(this.timer);this.timer=null;setTimeout(()=>this.cleanup(),5000);}}
}
