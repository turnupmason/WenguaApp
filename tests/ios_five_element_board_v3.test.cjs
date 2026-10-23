"use strict";
const assert=require("node:assert/strict");
const {test}=require("node:test");
require("../ios/design-v1/chart-facts-v3.js");
const {samples}=globalThis.WenguaVerifiedCharts;
const five=require("../ios/design-v1/five-element-colors.js");
const branchByPalace={1:["子"],2:["未","申"],3:["卯"],4:["辰","巳"],5:[],6:["戌","亥"],7:["酉"],8:["丑","寅"],9:["午"]};
const order=[4,9,2,3,5,7,8,1,6];
const horse={"申":"寅","子":"寅","辰":"寅","寅":"申","午":"申","戌":"申","巳":"亥","酉":"亥","丑":"亥","亥":"巳","卯":"巳","未":"巳"};
const tomb={"甲":"未","乙":"戌","丙":"戌","丁":"丑","戊":"戌","己":"丑","庚":"丑","辛":"辰","壬":"辰","癸":"未"};
test("five elements are per symbol, never per category",()=>{
 assert.equal(five.element("deity","玄武"),"水");
 assert.equal(five.element("deity","白虎"),"金");
 assert.equal(five.element("deity","九地"),"土");
 assert.equal(five.element("deity","六合"),"木");
 assert.equal(five.element("deity","螣蛇"),"火");
 assert.equal(five.element("door","杜门"),"木");
 assert.equal(five.element("door","开门"),"金");
 assert.equal(five.element("star","天心"),"金");
 assert.equal(five.element("star","天蓬"),"水");
 assert.equal(five.element("stem","辛"),"金");
 assert.equal(five.element("stem","戊"),"土");
 assert.equal(new Set(Object.values(five.ELEMENT_COLORS)).size,5);
 assert.equal(five.color("star","天心"),five.color("door","开门"));
 assert.equal(five.color("deity","玄武"),five.color("door","休门"));
 assert.notEqual(five.color("deity","九地"),five.color("star","天心"));
});
test("all four seeded source casts have real eight physical cells and correct center",()=>{
 assert.equal(samples.length,4);
 for(const x of samples){
   assert.deepEqual(x.palaces.map(c=>c.p),order);
   assert.deepEqual(x.palaces[4].heaven,[]);
   assert.equal(x.palaces[4].door,null);
   assert.equal(x.palaces[4].deity,null);
   for(const p of x.palaces.filter(p=>p.p!==5)){
      assert.deepEqual(p.branches,branchByPalace[p.p]);
      assert.ok(p.heaven.length>=1);
      for(const z of p.heaven)assert.equal(z.stages.length,p.branches.length);
      for(const layer of p.heaven){five.element("star",layer.star);five.element("stem",layer.stem);}
      five.element("stem",p.earth);five.element("deity",p.deity);five.element("door",p.door);
   }
   assert.equal(x.readingSections.length,10);
   assert.equal(x.readingSections[x.readingSections.length-1].id,"11_final");
 }
});
test("void, hour horse and both sky/ground tomb are from source branches, not frozen to Qian6",()=>{
 for(const x of samples){
   assert.ok(x.voidBranches.length===2);
   const hourBranch=x.pillars.hour[1];
   assert.equal(x.hourHorse,horse[hourBranch]);
   assert.equal(x.hourHorsePalace,x.palaces.find(p=>p.branches.includes(x.hourHorse)).p);
   for(const p of x.palaces){
     assert.deepEqual(p.void,p.branches.filter(b=>x.voidBranches.includes(b)));
     assert.equal(p.horse,p.branches.includes(x.hourHorse)?x.hourHorse:null);
     for(const t of p.tomb){
       assert.equal(tomb[t.stem],t.branch);
       assert.ok(p.branches.includes(t.branch));
       if(t.plane==="天盘")assert.ok(p.heaven.some(h=>h.stem===t.stem));
       if(t.plane==="地盘")assert.equal(p.earth,t.stem);
     }
   }
 }
 assert.deepEqual(samples[0].palaces.find(p=>p.p===4).horse,"巳");
 assert.deepEqual(samples[0].palaces.find(p=>p.p===6).void,["戌","亥"]);
 assert.ok(samples[0].palaces.find(p=>p.p===6).tomb.some(x=>x.stem==="乙"&&x.plane==="地盘"&&x.branch==="戌"));
 assert.ok(samples[0].palaces.find(p=>p.p===8).tomb.some(x=>x.stem==="丁"&&x.plane==="地盘"&&x.branch==="丑"));
 assert.ok(samples[1].palaces.find(p=>p.p===8).tomb.some(x=>x.stem==="庚"&&x.plane==="天盘"&&x.branch==="丑"));
});
test("no false automatic tomb opening without true six branch clash",()=>{
 for(const x of samples)assert.deepEqual(x.openedTombs,[]);
});

test("every actual palace retains source heaven AND earth lifecycle for all real branches",()=>{
  for(const chart of samples)for(const p of chart.palaces){
    assert.equal(p.earthStages.length,p.branches.length);
    for(const z of p.earthStages){
      assert.ok(p.branches.includes(z.branch));
      assert.ok(z.stage);
      five.element("branch",z.branch);
    }
    for(const z of p.heaven){
      assert.equal(z.stages.length,p.branches.length);
      for(const life of z.stages)assert.ok(p.branches.includes(life.branch));
    }
    if(p.p===5){
      assert.deepEqual(p.heaven,[]);
      assert.equal(p.door,null);
      assert.equal(p.deity,null);
    }
  }
  const coHosted=samples.flatMap(x=>x.palaces).filter(p=>p.heaven.length===2);
  assert.ok(coHosted.length>=4);
  for(const p of coHosted){
    assert.ok(p.heaven.some(s=>s.star==="天禽"));
    assert.ok(p.heaven.some(s=>s.star==="天芮"));
    assert.equal(p.heaven.reduce((n,h)=>n+h.stages.length,0),2*p.branches.length);
  }
});
test("opposite palace and same palace do not mean a six-branch horse versus tomb clash",()=>{
 const clash={子:"午",午:"子",丑:"未",未:"丑",寅:"申",申:"寅",卯:"酉",
  酉:"卯",辰:"戌",戌:"辰",巳:"亥",亥:"巳"};
 const opposite={1:9,9:1,2:8,8:2,3:7,7:3,4:6,6:4};
 let opposition=0;
 for(const chart of samples)for(const p of chart.palaces)for(const tomb of p.tomb){
    assert.notEqual(clash[tomb.branch],chart.hourHorse);
    if(opposite[p.p]===chart.hourHorsePalace)opposition++;
 }
 assert.ok(opposition>0,"must actually cover an opposing palace without false clash");
});
test("five-element full canonical mapping includes variants and all elements",()=>{
 for(const [name,elem] of Object.entries({甲:"木",丁:"火",戊:"土",辛:"金",壬:"水"})){
   assert.equal(five.element("stem",name),elem);
 }
 for(const [name,elem] of Object.entries({天心:"金",天芮:"土",天辅:"木",天蓬:"水",天英:"火"})){
   assert.equal(five.element("star",name),elem);
 }
 for(const [name,elem] of Object.entries({休门:"水",生门:"土",杜门:"木",景门:"火",开门:"金"})){
   assert.equal(five.element("door",name),elem);
 }
 assert.equal(five.element("deity","螣蛇"),five.element("deity","腾蛇"));
});
