/* Local learning profile, derived from completed detailed solo/battle runs. */
(function(root){
'use strict';
const KEY='kokushi.review.profile.v1';
function build(runs){
 const seen=new Set(),items=new Map();let count=0;
 for(const run of [...runs].sort((a,b)=>Date.parse(a?.date||0)-Date.parse(b?.date||0))){
  if(run?.version!==4||!Array.isArray(run.records)||!run.records.length||!run.runId||seen.has(run.runId))continue;
  seen.add(run.runId);count++;
  for(const r of run.records){
   if(!r||typeof r.question!=='string'||typeof r.correct!=='string'||typeof r.ok!=='boolean')continue;
   const key=JSON.stringify([r.question,r.correct]);
   let x=items.get(key);
   if(!x){x={questionId:r.questionId||null,question:r.question,correct:r.correct,attempts:0,wrong:0,assistedCorrect:0,unassistedCorrect:0,unassistedStreak:0,lastWrong:null,lastWrongAnswer:null,lastSeen:null,recent:[]};items.set(key,x)}
   x.attempts++;x.lastSeen=run.date;
   const assist=r.assist==='repeat'||r.assist==='delay';
   const outcome=!r.ok?'wrong':assist?'assisted':r.assist===null?'independent':'unknown';
   if(!r.ok){x.wrong++;x.lastWrong=run.date;x.lastWrongAnswer=typeof r.answer==='string'?r.answer:null;x.unassistedStreak=0}
   else if(assist){x.assistedCorrect++;x.unassistedStreak=0}
   else if(outcome==='independent'){x.unassistedCorrect++;x.unassistedStreak++}
   else x.unassistedStreak=0;
   x.recent.push(outcome);if(x.recent.length>5)x.recent.shift();
  }
 }
 const questions=[...items.values()].filter(x=>x.wrong>0||x.assistedCorrect>0).map(x=>({...x,priority:x.recent.filter(v=>v==='wrong').length*3+x.recent.filter(v=>v==='assisted').length*2+(x.wrong>=2?2:0)-Math.min(x.unassistedStreak,3)*2})).sort((a,b)=>b.priority-a.priority||b.wrong-a.wrong||String(b.lastWrong).localeCompare(String(a.lastWrong)));
 return {version:1,runCount:count,questions};
}
function save(runs){const p=build(runs);try{localStorage.setItem(KEY,JSON.stringify(p))}catch{}return p}
function focus(p,limit=10){return p.questions.filter(x=>(x.wrong>=2||x.assistedCorrect>=2)&&x.unassistedStreak<3).slice(0,limit)}
root.KokushiReview={build,save,focus};
})(globalThis);
