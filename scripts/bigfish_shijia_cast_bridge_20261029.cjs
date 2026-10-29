"use strict";
// BigFish upstream TypeScript is compiled from pinned original SHA by workflow.
// This adapter calls the REAL shiJiaGenerate. Do not use engine.ts metadata-only
// MaoShan/ZhiRun baseChart branches as if they had recalculated the nine palaces.
const fs=require("node:fs"),path=require("node:path");
const compiled=path.resolve(process.argv[2]);
const original=require(path.join(compiled,"engines/shijia.js"));
const bureau=require(path.join(compiled,"engines/chaibuquju.js"));
try{
  const data=JSON.parse(fs.readFileSync(0,"utf8"));
  const {pillars:p,term}=data;
  if(!p||!term)throw new Error("Missing true four pillars / solar term");
  const gz=s=>{if(typeof s!=="string"||s.length!==2)throw new Error("Invalid Ganzhi "+s);return {gan:s[0],zhi:s[1]}};
  const four={year:gz(p.year),month:gz(p.month),day:gz(p.day),hour:gz(p.hour)};
  const b=bureau.chaiBuJuByGanZhi(term,four.day.gan,four.day.zhi);
  const c=original.shiJiaGenerate(four.hour.gan,four.hour.zhi,b.juNumber,b.isYangDun?"yang":"yin",four,term);
  c.juMethod="chaibu";c.yuan=b.yuan;
  process.stdout.write(JSON.stringify({source:"perfhelf/bigfishmarquis-qimen",method:"chaibu",bureau:b,chart:c})+"\n");
}catch(e){console.error(e.stack||e);process.exit(1)}
