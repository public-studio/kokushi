import { BANK,FIXED_SIDES } from '../public/apps/battle-bank.js';
export const RULES={
  "duration": 60000,
  "normal": 3,
  "wrong": 2,
  "feverFactor": 2,
  "feverMs": 5000,
  "charge": 5,
  "feverCharge": 10,
  "damageCharge": 0.65,
  "specialMs": 3000,
  "specialHit": 2.1,
  "tapInterval": 85,
  "reverseMs": 3500,
  "reverseThreshold": 15,
  "reverseShots": 2,
  "cycle": 1100,
  "impact": 1000,
  "perfect": 30,
  "great": 80,
  "good": 170,
  "reversePower": [
    5,
    12,
    20,
    35
  ],
  "attackTravel": 280,
  "answerInterval": 90,
  "assistMs": 3000
};
function player(name,handicap){return {name,handicap,n:0,correct:0,combo:0,maxCombo:0,until:0,fever:0,nextFever:10,g:0,action:null,reverseUsed:false,shown:0,lastAnswer:-Infinity};}
function clamp(x,min,max){return Math.min(max,Math.max(min,x))}
function comboWindow(n){return n<10?4000:n<20?3500:3000}
function gradeTiming(elapsed){const e=Math.abs(elapsed%RULES.cycle-RULES.impact);return e<=RULES.perfect?3:e<=RULES.great?2:e<=RULES.good?1:0}
export class BattleGame {
constructor(names,handicaps,start){this.start=start;this.end=start+RULES.duration;this.p=50;this.players=names.map((n,i)=>player(n,handicaps[i]));this.players.forEach(x=>x.shown=start);this.attacks=[];this.events=[];this.finished=false;this.winner=null;this.reason='';}
charge(x,v){x.g=clamp(x.g+v,0,100)}
emit(e){this.events.push(e)}
fire(i,power,t,kind){let at=Math.ceil((t+RULES.attackTravel)/100)*100;this.attacks.push({i,power,at,kind});this.emit({type:'fire',i,power,kind,at})}
leave(x,t){if(!x.action)return;const elapsed=Math.min(t-x.action.start,x.action.duration);if(x.until)x.until+=elapsed;x.shown+=elapsed;x.action=null;}
finish(reason,winner){if(this.finished)return;this.finished=true;this.reason=reason;this.winner=winner;this.attacks=[];this.emit({type:'finish',reason,winner});}
tick(t){if(this.finished||t<this.start)return;const cutoff=Math.min(t,this.end);for(const x of this.players){if(x.action&&cutoff>=x.action.start+x.action.duration)this.leave(x,x.action.start+x.action.duration);if(!x.action&&x.combo&&cutoff>=x.until){x.combo=0;x.until=0;x.nextFever=10;}}
const buckets=[...new Set(this.attacks.filter(a=>a.at<=cutoff).map(a=>a.at))].sort((a,b)=>a-b);
for(const at of buckets){const hit=this.attacks.filter(a=>a.at===at);let sums=[0,0];for(const a of hit)sums[a.i]+=a.power;let net=sums[0]-sums[1];this.attacks=this.attacks.filter(a=>a.at!==at);if(sums[0]&&sums[1])this.emit({type:'clash',power:Math.min(...sums)});if(net){let old=this.p;this.p=clamp(this.p+net,0,100);let shift=this.p-old;this.charge(this.players[shift>0?1:0],Math.abs(shift)*RULES.damageCharge);this.emit({type:'impact',i:shift>0?0:1,power:Math.abs(shift)});}if(this.p<=0||this.p>=100){this.finish('KO',this.p>=100?0:1);return;}}
if(t>=this.end)this.finish('TIME',this.p>50?0:this.p<50?1:null);
else if(this.players.every(x=>x.n>=BANK.length)&&!this.attacks.length&&!this.players.some(x=>x.action))this.finish('ALL',this.p>50?0:this.p<50?1:null);
}
input(i,m,t){this.tick(t);if(this.finished||t<this.start||t>=this.end)return false;const x=this.players[i],f=t<x.fever;
if(m.type==='answer'){if(x.action||x.n>=BANK.length||m.n!==x.n||![0,1].includes(m.choice)||t-x.lastAnswer<RULES.answerInterval)return false;const q=BANK[x.n],ok=Number(FIXED_SIDES[x.n])===m.choice;x.n++;x.shown=t;x.lastAnswer=t;if(ok){x.correct++;x.combo++;x.maxCombo=Math.max(x.maxCombo,x.combo);x.until=t+comboWindow(x.combo);this.charge(x,f?RULES.feverCharge:RULES.charge);this.fire(i,RULES.normal*x.handicap*(f?RULES.feverFactor:1),t,'normal');if(x.combo>=x.nextFever&&!f){x.fever=t+RULES.feverMs;x.nextFever=x.combo+10;this.emit({type:'fever',i});}}else{x.combo=0;x.until=0;x.nextFever=10;this.fire(1-i,RULES.wrong,t,'wrong');}this.emit({type:'answer',i,ok,id:q.id,n:x.n});return true;}
if(m.type==='special'&&!x.action&&x.g>=100){x.g=0;x.action={type:'special',start:t+250,duration:RULES.specialMs,count:0,last:-Infinity,cycle:-1};this.emit({type:'action',i,kind:'special'});return true;}
if(m.type==='reverse'&&!x.action&&!x.reverseUsed&&(i===0?this.p:100-this.p)<=RULES.reverseThreshold){x.reverseUsed=true;x.action={type:'reverse',start:t+250,duration:RULES.reverseMs,count:0,last:-Infinity,cycle:-1};this.emit({type:'action',i,kind:'reverse'});return true;}
if(m.type==='hit'&&x.action){const a=x.action;if(t<a.start||t>=a.start+a.duration)return false;if(a.type==='special'){if(t-a.last<RULES.tapInterval)return false;a.last=t;a.count++;this.fire(i,RULES.specialHit*(f?RULES.feverFactor:1),t,'special');return true;}const d=t-a.start,cycle=Math.floor(d/RULES.cycle);if(cycle===a.cycle||a.count>=RULES.reverseShots)return false;a.cycle=cycle;a.count++;const grade=gradeTiming(d);this.fire(i,RULES.reversePower[grade],t,'reverse');this.emit({type:'grade',i,grade});if(a.count>=RULES.reverseShots)this.leave(x,t);return true;}
return false;}
snapshot(i,t){const x=this.players[i];return {type:'state',now:t,start:this.start,end:this.end,p:this.p,players:this.players.map(v=>({name:v.name,handicap:v.handicap,n:v.n,correct:v.correct,combo:v.combo,maxCombo:v.maxCombo,until:v.until,fever:v.fever,nextFever:v.nextFever,g:v.g,action:v.action?{...v.action,last:undefined}:null,reverseUsed:v.reverseUsed})),hint:!x.action&&x.n<BANK.length&&t-x.shown>=RULES.assistMs?Number(FIXED_SIDES[x.n]):null,finished:this.finished,winner:this.winner,reason:this.reason};}
}
