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
