/* Qimen five-element style contract (V3). Color NEVER follows symbol category.
 * 八神采用此版本术数资料中的土值符、火螣蛇、金太阴、
 * 木六合、金白虎、水玄武、土九地、金九天体系。
 * Some other schools give 值符 a different element; it must be a
 * named source version change, not accidental per-UI colors.
 * These mappings apply equally to glyphs in charts AND detail sheets.
 */
(function(root){
"use strict";
const ELEMENT_COLORS={金:"#D39A19",木:"#18A557",水:"#2679E7",火:"#E34B3F",土:"#9C7447"};
const STEM={甲:"木",乙:"木",丙:"火",丁:"火",戊:"土",己:"土",庚:"金",辛:"金",壬:"水",癸:"水"};
const STAR={天蓬:"水",天任:"土",天冲:"木",天辅:"木",天英:"火",天芮:"土",天柱:"金",天心:"金",天禽:"土"};
const DOOR={休门:"水",生门:"土",伤门:"木",杜门:"木",景门:"火",死门:"土",惊门:"金",开门:"金"};
const DEITY={值符:"土",螣蛇:"火",腾蛇:"火",太阴:"金",六合:"木",白虎:"金",玄武:"水",九地:"土",九天:"金"};
const BRANCH={子:"水",亥:"水",寅:"木",卯:"木",巳:"火",午:"火",申:"金",酉:"金",丑:"土",辰:"土",未:"土",戌:"土"};
function element(type,symbol){
  const maps={stem:STEM,star:STAR,door:DOOR,deity:DEITY,branch:BRANCH};
  if(!maps[type])throw new Error("Unknown symbol layer "+type);
  const v=maps[type][symbol];
  if(!v)throw new Error("No sourced 5-element mapping for "+type+":"+symbol);
  return v;
}
function color(type,symbol){return ELEMENT_COLORS[element(type,symbol)];}
const api={ELEMENT_COLORS,STEM,STAR,DOOR,DEITY,BRANCH,element,color};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.WenguaFiveElements=api;
})(typeof globalThis!=="undefined"?globalThis:this);
