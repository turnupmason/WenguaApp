"use strict";
const assert=require("node:assert/strict");
const {test}=require("node:test");
const {webcrypto}=require("node:crypto");
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const p=require("../ios/design-v1/issue-policy.js");
const storage=()=>({
 entries:new Map(),
 getItem(key){return this.entries.has(key)?this.entries.get(key):null},
 setItem(key,value){this.entries.set(key,value)}
});
const a={topic:"health.severity",relation:"father",subject:"爸爸",question:"关于这一次的病势变化"};
test("same exact issue with Chinese full-width punctuation and whitespace hashes identically",async()=>{
 const b={...a,question:"关 于这一次的病势变化！！"};
 const c={...a,question:"关于这一次的病势变化"};
 assert.equal(await p.fingerprintIssue(b),await p.fingerprintIssue(c));
 assert.equal((await p.fingerprintIssue(a)).length,64);
});
test("one specific event per fifteen days, no locking before a validated persisted real cast",async()=>{
 const s=storage(),t=1731000000000;
 assert.equal((await p.checkIssue(a,s,t)).locked,false);
 await assert.rejects(()=>p.commitCompletedCast(a,s,{nowMs:t,engineResultValidated:false,persistedRecord:true}));
 assert.equal(s.entries.size,0);
 await assert.rejects(()=>p.commitCompletedCast(a,s,{nowMs:t,engineResultValidated:true,persistedRecord:false}));
 assert.equal(s.entries.size,0);
 const r=await p.commitCompletedCast(a,s,{nowMs:t,engineResultValidated:true,
   persistedRecord:true,engineVersion:"v3.9.1",issueId:"uuid-one"});
 assert.equal(r.nextAllowedAt-t,p.WINDOW_MS);
 assert.equal((await p.checkIssue(a,s,t+p.WINDOW_MS-1)).locked,true);
 assert.equal((await p.checkIssue(a,s,t+p.WINDOW_MS)).locked,false);
 await assert.rejects(()=>p.commitCompletedCast(a,s,{nowMs:t+10,engineResultValidated:true,
   persistedRecord:true,engineVersion:"v3.9.1",issueId:"uuid-two"}));
});
test("different specific event/relationship/subject are not globally locked as the same health category",async()=>{
 const s=storage(),t=1731000000000;
 await p.commitCompletedCast(a,s,{nowMs:t,engineResultValidated:true,persistedRecord:true});
 assert.equal((await p.checkIssue({...a,question:"是否能按计划进行康复锻炼"},s,t+1)).locked,false);
 assert.equal((await p.checkIssue({...a,relation:"mother"},s,t+1)).locked,false);
 assert.equal((await p.checkIssue({...a,subject:"另一位父亲"},s,t+1)).locked,false);
});
test("no raw question or patient label is persisted",async()=>{
 const s=storage();
 await p.commitCompletedCast(a,s,{engineResultValidated:true,persistedRecord:true,nowMs:1700000000000});
 const str=[...s.entries].map(x=>x.join(" ")).join("\n");
 assert.ok(!str.includes(a.question));
 assert.ok(!str.includes(a.subject));
 assert.match(str,/wengua:v2:completed:[0-9a-f]{64}/);
});
test("question must be specific, not general health category",async()=>{
 assert.equal(p.questionIsSpecific("身体"),false);
 assert.equal(p.questionIsSpecific("健康"),false);
 assert.equal(p.questionIsSpecific("父亲本次复查"),true);
 await assert.rejects(()=>p.fingerprintIssue({...a,question:"健康"}));
});
