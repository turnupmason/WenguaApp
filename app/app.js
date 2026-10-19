/* WenguaApp V0.1: local-only guided experience, no fake casts or rules. */
(() => {
  "use strict";
  const main = document.querySelector("#main");
  const domains = [
    ["health","身体健康","◉"],["marriage","婚姻感情","♡"],
    ["pregnancy","怀孕分娩","✧"],["education","求学考试","文"],
    ["work","工作就业","職"],["business","经营求财","財"],
    ["travel","出行出国","↗"],["missing_person","行人走失","尋"],
    ["criminal","刑事案件","法"],["litigation","官司诉讼","訟"],
    ["sports","体育竞赛","勝"],["weather","天时气象","☼"],
    ["geography","地理环境","山"],["life","人生机遇","命"],
    ["lost_item","钱物丢失","物"]
  ];
  const relations = [
    ["self","我自己的事"],["friend","代朋友问"],["parent","代父母问"],
    ["child","父母代子女问"],["partner","代伴侣问"],["other","其他关系"]
  ];
  const palaces = ["巽四","离九","坤二","震三","中五","兑七","艮八","坎一","乾六"];
  let screen = "intro", introPage = 0, domain = "", relationship = "";
  let countdownId = null, deadline = null, castTime = null;

  function introSeen() {
    try { return localStorage.getItem("wengua_introduction_seen_v01") === "yes"; }
    catch (_) { return false; }
  }
  function markIntroSeen() {
    try { localStorage.setItem("wengua_introduction_seen_v01","yes"); } catch (_) {}
  }
  if (introSeen()) screen = "domain";
  function nav(html) { main.innerHTML = html; main.focus({preventScroll:true}); }
  function title(eyebrow,heading,description){
    return '<div class="eyebrow">'+eyebrow+'</div><h2>'+heading+'</h2><p>'+description+'</p>';
  }
  function button(text,action) {
    return '<button class="cta" type="button" data-action="'+action+'">'+text+'</button>';
  }
  function back(action) {
    return '<button type="button" class="back" data-action="'+action+'">← 返回</button>';
  }
  function showIntro(){
    if(introPage === 0){
      nav('<div class="eyebrow">WENGUA · 问卦</div>'+
        '<h1>万象有迹<br><span class="gold">静观其象</span></h1>'+
        '<p class="lead">以传统奇门为引，观时、观局、观所问。一本随身的离线古籍研究与问事工具。</p>'+
        '<div class="info"><span class="label">首次开启 · 01 / 02</span><p>简单选择问事、默念片刻，再以当刻时间起局。先从时家转盘开始。</p></div>'+
        button('了解使用方式','next-intro'));
    }else{
      nav('<div class="eyebrow">FIRST STEPS · 02 / 02</div>'+
        '<h2>问一件事<br>先静一颗心</h2>'+
        '<p class="lead">选择问事领域及与当事人的关系，静心 60 秒。完成后将记录当地时刻，未来由经过验证的起盘程序与古籍规则生成解释。</p>'+
        '<div class="info"><span class="label">项目状态</span><p>当前为交互原型：尚未接入经验证的九宫起盘与正式断词，不会假造吉凶或宫位信息。</p></div>'+
        button('开始问事','finish-intro'));
    }
  }
  function showDomains(){
    const choices=domains.map(([id,name,symbol]) =>
      '<button class="choice" type="button" data-domain="'+id+'" aria-pressed="'+(domain===id)+'"><span class="choice-icon">'+symbol+'</span>'+name+'</button>').join("");
    nav('<div class="eyebrow">01 / 03 · 选择问事</div><h2>今日，所问何事？</h2>'+
      '<p>每个领域将逐步配置独立的古籍用神规则。当前均为研究中的专题目录。</p>'+
      '<div class="grid">'+choices+'</div>'+
      '<div class="info"><span class="label">以原书为依据</span><p>V1 以《神奇之门》《开悟之门》为基础，后续古籍将通过版本升级补充。</p></div>'+
      '<button class="cta" type="button" '+(!domain?'disabled ':'')+'data-action="to-relationship">下一步 · 人物关系</button>');
  }
  function showRelations(){
    const choices=relations.map(([id,name]) =>
      '<button class="choice" type="button" data-relation="'+id+'" aria-pressed="'+(relationship===id)+'">'+name+'</button>').join("");
    nav(back("back-domain")+title("02 / 03 · 人物关系","你与此事，是什么关系？",
      "问测人与事情当事人可能不同。关系将决定哪些取用条件可以生效。")+
      '<div class="relationships">'+choices+'</div>'+
      '<div class="info"><span class="label">正在选择</span><p>'+domains.find(d=>d[0]===domain)[1]+' · '+(relations.find(r=>r[0]===relationship)?.[1] || "尚未选择")+'</p></div>'+
      '<button class="cta" type="button" '+(!relationship?'disabled ':'')+'data-action="to-ritual">下一步 · 静心起局</button>');
  }
  function showRitual(){
    nav(back("back-relation")+
      '<div class="ritual"><div class="eyebrow">03 / 03 · 一念一问</div>'+
      '<h2>静心 · 默想所问</h2>'+
      '<p>请闭上双眼，静下心来。将注意力放在这件事上，持续一分钟。</p>'+
      '<div class="orbit"><div><span class="count" id="remaining">60</span><span class="s">秒</span></div></div>'+
      '<p id="ritual-note">心诚则灵 · 作为传统仪式体验，不是科学准确性的保证。</p>'+
      '<div class="progress"><span id="progress-fill"></span></div></div>'+
      button('开始 60 秒静心','start-countdown'));
  }
  function tick() {
    if (deadline === null) return;
    const left=Math.max(0,Math.ceil((deadline-Date.now())/1000));
    const el=document.querySelector("#remaining"),bar=document.querySelector("#progress-fill");
    if(el)el.textContent=String(left).padStart(2,"0");
    if(bar)bar.style.width=(100*(60-left)/60)+"%";
    if(left === 0) {
      clearInterval(countdownId); countdownId=null; deadline=null;
      // Actual wall clock is locked at callback execution, not at page entry.
      castTime = new Date();
      screen="result"; render();
    }
  }
  function startCountdown(){
    if (countdownId !== null) return;
    deadline=Date.now()+60_000;
    document.querySelector('[data-action="start-countdown"]')?.remove();
    const note=document.querySelector("#ritual-note");
    if(note)note.textContent="静心中 · 让这一分钟属于你自己";
    tick();
    countdownId=setInterval(tick,250);
  }
  function showResult(){
    const tz=Intl.DateTimeFormat().resolvedOptions().timeZone || "设备本地时区";
    const time=castTime ? castTime.toLocaleString("zh-CN",{hour12:false}) : "时间未记录";
    nav('<div class="eyebrow">TIME RECORDED · 时刻已定</div><h2>本次问事</h2>'+
      '<div class="info"><div class="detail"><span>问事专题</span><strong>'+domains.find(d=>d[0]===domain)[1]+'</strong></div>'+
      '<div class="detail"><span>人物关系</span><strong>'+relations.find(r=>r[0]===relationship)[1]+'</strong></div>'+
      '<div class="detail"><span>记录时刻</span><strong>'+time+'</strong></div>'+
      '<div class="detail"><span>设备时区</span><span>'+tz+'</span></div></div>'+
      '<h2 style="font-size:25px;margin-top:32px">九宫 · 待核盘</h2>'+
      '<div class="palaces">'+palaces.map(x=>'<div class="palace"><strong>'+x+'</strong><span>等待验盘</span></div>').join('')+'</div>'+
      '<div class="status">尚未接入经古籍案例验证的时家转盘起盘引擎。本九宫仅展示位置名称，绝不是实际排出的盘。</div>'+
      '<div class="info"><span class="label">断案依据与规则状态</span>'+
      '<p>等待《神奇之门》和《开悟之门》的原文、案例和用神规则审核后，再生成条件化的解释、证据和引文。</p>'+
      '<p class="summary">暂不提供吉凶总结：起盘与断词尚未通过验收。</p></div>'+
      button('重新选择问事','new-question'));
  }
  function clearCountdown(){
    if(countdownId!==null)clearInterval(countdownId);
    countdownId=null;deadline=null;
  }
  function render(){
    if(screen==="intro")showIntro();
    else if(screen==="domain")showDomains();
    else if(screen==="relationship")showRelations();
    else if(screen==="ritual")showRitual();
    else if(screen==="result")showResult();
  }
  main.addEventListener("click",event=>{
    const target=event.target.closest("button");
    if(!target)return;
    if(target.dataset.domain){domain=target.dataset.domain;render();return;}
    if(target.dataset.relation){relationship=target.dataset.relation;render();return;}
    switch(target.dataset.action){
      case "next-intro":introPage=1;break;
      case "finish-intro":markIntroSeen();screen="domain";break;
      case "to-relationship":if(!domain)return;screen="relationship";break;
      case "to-ritual":if(!relationship)return;screen="ritual";break;
      case "back-domain":screen="domain";break;
      case "back-relation":clearCountdown();screen="relationship";break;
      case "start-countdown":startCountdown();return;
      case "new-question":clearCountdown();castTime=null;relationship="";domain="";screen="domain";break;
      default:return;
    }
    render();
  });
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)tick();});
  render();
  if("serviceWorker" in navigator && location.protocol!=="file:"){
    window.addEventListener("load",()=>{
      navigator.serviceWorker.register("./sw.js").catch(()=>{});
    });
  }
})();
