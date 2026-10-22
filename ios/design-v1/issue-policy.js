/* Wengua issue policy V2. Browser prototype and future iOS contract.
 * One specific question, one completed casting in 15x24 hours.
 * Never store raw private questions or patient names here.
 * This alone cannot distinguish semantically paraphrased questions,
 * new devices, erased storage or malicious bypass. Native App must
 * implement a durable local equivalence ledger before release.
 */
(function(root){
"use strict";
const WINDOW_MS = 15*24*60*60*1000;
const STORAGE_PREFIX = "wengua:v2:completed:";
function canonicalQuestion(value){
  return String(value||"").normalize("NFKC").toLowerCase()
    .replace(/[\s\u3000,.，。！？?!；;：:“”"'‘’、()（）【】\[\]{}]+/g,"")
    .trim();
}
function questionIsSpecific(value){return canonicalQuestion(value).length>=4;}
function packedIssue({topic="health.severity",relation="self",subject="",question=""}={}){
  const normalized=canonicalQuestion(question);
  if(!questionIsSpecific(question))throw new Error("请用至少4个字说明同一件具体的事");
  return [canonicalQuestion(topic),canonicalQuestion(relation),
          canonicalQuestion(subject)||"同一当事人",normalized].join("|");
}
async function fingerprintIssue(issue){
  if(!root.crypto || !root.crypto.subtle)throw new Error("浏览器不支持安全本地摘要，无法实施15天限制");
  const encoded=new TextEncoder().encode("wengua-issue-v2|"+packedIssue(issue));
  const digest=await root.crypto.subtle.digest("SHA-256",encoded);
  return Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,"0")).join("");
}
function parseRecord(value){
  if(!value)return null;
  try {const o=JSON.parse(value);return Number.isFinite(o.completedAtMs)?o:null;}catch{return null;}
}
async function checkIssue(issue,store,nowMs=Date.now()){
  const digest=await fingerprintIssue(issue);
  const saved=parseRecord(store.getItem(STORAGE_PREFIX+digest));
  const expires=saved?saved.completedAtMs+WINDOW_MS:null;
  return {digest,locked:Boolean(saved&&nowMs<expires),
      lastCompletedAt:saved?.completedAtMs??null,
      nextAllowedAt:expires,remainingMs:expires?Math.max(0,expires-nowMs):0};
}
async function commitCompletedCast(issue,store,options={}){
  // Only call after the REAL on-device engine has produced and persisted
  // a valid unique board + reading. Never call when opening demo fixture.
  if(options.engineResultValidated!==true || options.persistedRecord!==true){
    throw new Error("只有真实起盘成功并保存后才能建立15天记录");
  }
  const nowMs=options.nowMs??Date.now();
  const checked=await checkIssue(issue,store,nowMs);
  if(checked.locked)throw new Error("同一件事15天内已经起过局");
  store.setItem(STORAGE_PREFIX+checked.digest,JSON.stringify({
    completedAtMs:nowMs,engineVersion:String(options.engineVersion||""),
    issueId:String(options.issueId||"")
  }));
  return {digest:checked.digest,completedAtMs:nowMs,nextAllowedAt:nowMs+WINDOW_MS};
}
const api={WINDOW_MS,STORAGE_PREFIX,canonicalQuestion,packedIssue,
  questionIsSpecific,fingerprintIssue,checkIssue,commitCompletedCast};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.WenguaIssuePolicy=api;
})(typeof globalThis!=="undefined"?globalThis:this);
