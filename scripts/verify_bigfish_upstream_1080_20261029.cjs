"use strict";
const assert=require("node:assert/strict");
const path=require("node:path");
const {shiJiaGenerate}=require(path.resolve(process.argv[2],"engines/shijia.js"));
const {chaiBuJuByGanZhi}=require(path.resolve(process.argv[2],"engines/chaibuquju.js"));
const {maoShanJu}=require(path.resolve(process.argv[2],"engines/maoshan.js"));
const {zhiRunJu}=require(path.resolve(process.argv[2],"engines/zhirun.js"));
const STEMS=[..."甲乙丙丁戊己庚辛壬癸"],BRANCHES=[..."子丑寅卯辰巳午未申酉戌亥"];
const cycle=Array.from({length:60},(_,i)=>STEMS[i%10]+BRANCHES[i%12]);
const doors=new Set(["休门","生门","伤门","杜门","景门","死门","惊门","开门"]);
const stars=new Set(["天蓬","天芮","天冲","天辅","天心","天柱","天任","天英"]);
const gods=new Set(["值符","螣蛇","腾蛇","太阴","六合","白虎","玄武","九地","九天"]);
const results={source:"perfhelf/bigfishmarquis-qimen",method:"direct_shiJiaGenerate",base_states:0,errors:[],samples:[]};
const four={year:{gan:"丙",zhi:"午"},month:{gan:"戊",zhi:"戌"},day:{gan:"庚",zhi:"午"},hour:{gan:"甲",zhi:"子"}};
const complain=(k,msg)=>{results.errors.push(k+":"+msg)};
for(const dun of ["yang","yin"])for(let ju=1;ju<=9;ju++)for(const hour of cycle){
  const key=dun+"-"+ju+"-"+hour;
  const time={...four,hour:{gan:hour[0],zhi:hour[1]}};
  try{
    const p=shiJiaGenerate(hour[0],hour[1],ju,dun,time,"霜降");
    assert.equal(p.palaces.length,9);
    assert.deepEqual(p.palaces.map(q=>q.palaceNumber).sort((a,b)=>a-b),[1,2,3,4,5,6,7,8,9]);
    const centre=p.palaces.find(q=>q.palaceNumber===5);
    assert.equal(centre.star,"天禽"); assert.equal(centre.door,""); assert.equal(centre.god,"");
    const outer=p.palaces.filter(q=>q.palaceNumber!==5);
    assert.equal(new Set(outer.map(q=>q.star)).size,8);
    assert.equal(new Set(outer.map(q=>q.door)).size,8);
    assert.equal(new Set(outer.map(q=>q.god.replace("腾蛇","螣蛇"))).size,8);
    for(const q of outer){
       assert.ok(stars.has(q.star));assert.ok(doors.has(q.door));assert.ok(gods.has(q.god));
       // Historic naming inversion is documented upstream. These fields must exist.
       assert.equal(q.skyStem.length,1);assert.equal(q.earthStem.length,1);
       if(q.star==="天芮")assert.equal(q.jiGanStem,centre.skyStem);
    }
    assert.equal(new Set(p.palaces.map(q=>q.skyStem)).size,9);
    results.base_states++;
    if(results.samples.length<5)results.samples.push({key,centre:centre.skyStem,star:p.zhiFuStar,door:p.zhiShiDoor});
  }catch(e){complain(key,String(e.message||e));}
}
try{
  const expected=chaiBuJuByGanZhi("霜降","庚","午");
  assert.equal(expected.isYangDun,false);
  assert.equal(expected.yuan,"中"); // 2026-10-23 庚午 day, preceding 己巳 -> middle yuan
  assert.equal(expected.juNumber,8); // 霜降 [5,8,2]
  const m=maoShanJu("冬至",122);
  assert.equal(m.juNumber,7); // 122h => 61 two-hour slots => middle yuan
}catch(e){complain("bureau_fixture",String(e.message||e));}
process.stdout.write(JSON.stringify(results,null,2)+"\n");
if(results.errors.length){process.stderr.write("BigFish full physical contract failures: "+results.errors.length+"\n");process.exit(1)}
