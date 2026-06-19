// V5.1 Full Chinese
(function(){
console.log("V5.1 init");
var STORE={matches:null,plans:null};
var CURRENT={page:"dashboard",risk:"stable"};
function safe(o,p,d){try{return o[p]!==undefined?o[p]:d}catch(e){return d}}
function safeA(a,i,d){try{return a&&a[i]!==undefined?a[i]:d}catch(e){return d}}

// Particles
try{
var c=document.getElementById("particles");
if(c){
var ctx=c.getContext("2d"),w=c.width=window.innerWidth,h=c.height=window.innerHeight,ps=[];
window.addEventListener("resize",function(){w=c.width=window.innerWidth;h=c.height=window.innerHeight});
for(var i=0;i<40;i++)ps.push({x:Math.random()*w,y:Math.random()*h,r:Math.random()*2+1,vx:(Math.random()-0.5)*0.5,vy:(Math.random()-0.5)*0.5,o:Math.random()*0.4+0.1});
(function anim(){ctx.clearRect(0,0,w,h);
for(var i=0;i<ps.length;i++){var p=ps[i];p.x+=p.vx;p.y+=p.vy;
if(p.x<0)p.x=w;if(p.x>w)p.x=0;if(p.y<0)p.y=h;if(p.y>h)p.y=0;
ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
ctx.fillStyle="rgba(59,130,246,"+p.o+")";ctx.fill();}
requestAnimationFrame(anim);})();
}
}catch(e){console.log("Particles:",e)}

// DATA
function loadData(){
var el=document.getElementById("main-content");if(!el)return;
el.innerHTML='<div class="loading"><div class="spinner"></div><p>鍔犺浇鏁版嵁涓?..</p></div>';
var timeout=setTimeout(function(){
if(!STORE.matches)el.innerHTML='<div style="text-align:center;padding:60px"><h3 style="color:#f59e0b">杩炴帴瓒呮椂</h3><p style="color:#94a3b8">璇风‘璁ゅ凡杩愯 app.py</p><button onclick="location.reload()" style="background:#3b82f6;color:#fff;border:none;padding:10px 24px;border-radius:8px;cursor:pointer;margin-top:12px">閲嶈瘯</button></div>';
},12000);

fetch("/api/matches").then(function(r){return r.json()}).then(function(d){
clearTimeout(timeout);STORE.matches=d;console.log("鍔犺浇:",d.matches.length);
showPage("dashboard");
}).catch(function(e){
clearTimeout(timeout);console.error(e);
el.innerHTML='<div style="text-align:center;padding:60px"><h3 style="color:#ef4444">鍔犺浇澶辫触</h3><p style="color:#94a3b8">璇风‘璁?Flask 鏈嶅姟宸茶繍琛屽湪 http://127.0.0.1:5000</p><button onclick="location.reload()" style="background:#3b82f6;color:#fff;border:none;padding:10px 24px;border-radius:8px;cursor:pointer;margin-top:12px">閲嶈瘯</button></div>';
});
fetch("/api/plans").then(function(r){return r.json()}).then(function(d){STORE.plans=d}).catch(function(e){});
fetch("/api/fusion").then(function(r){return r.json()}).then(function(d){STORE.fusion=d}).catch(function(e){console.log("Fusion bg err:",e)});
}

// NAV
window.navigate=function(page){
CURRENT.page=page;
var items=document.querySelectorAll(".sidebar-item");
for(var i=0;i<items.length;i++){try{items[i].classList.toggle("active",items[i].getAttribute("data-page")===page)}catch(e){}}
showPage(page);
};

function showPage(page){
var el=document.getElementById("main-content");if(!el)return;
if(!STORE.matches){loadData();return}
var ms=(STORE.matches&&STORE.matches.matches)?STORE.matches.matches:[];
var pl=STORE.plans||{};
try{
switch(page){
case"dashboard":el.innerHTML=buildDashboard(ms,pl);bindClicks(ms);break;
case"matches":el.innerHTML=buildMatches(ms);bindClicks(ms);break;
case"liuyao":el.innerHTML=buildLiuyao(ms);bindLiuyao(ms);break;
case"plans":el.innerHTML=buildPlans();setTimeout(function(){try{if(window.genPlans)window.genPlans()}catch(e){}},300);break;
case"intel":el.innerHTML=buildIntel(ms);break;
case"multi":el.innerHTML=buildMulti();break;
case"hercules":el.innerHTML=buildHercules();loadHercules(ms);break;
case"debate":el.innerHTML=buildDebate();loadDebate(ms);break;
case"compare":el.innerHTML=buildCompare(ms);break;
case"bets":el.innerHTML=buildBets();loadBets();break;
case"postmatch":el.innerHTML=buildPostMatch(ms);break;
case"roi":el.innerHTML=buildROI();loadROI();break;
case"time":el.innerHTML=buildTimeAnalysis();loadTimeAnalysis();break;
case"news":el.innerHTML=buildNews();loadNews();break;
case"auto":el.innerHTML=buildAuto();loadAuto();break;
case"learn":el.innerHTML=buildLearn();loadLearnStats();break;
default:el.innerHTML=buildDashboard(ms,pl);bindClicks(ms);
}
}catch(e){
el.innerHTML='<div style="text-align:center;padding:40px"><h3 style="color:#ef4444">椤甸潰娓叉煋閿欒</h3><p style="color:#94a3b8">'+e.message+'</p><button onclick="window.navigate(\'dashboard\')" class="btn">杩斿洖棣栭〉</button></div>';
}
}

function bindClicks(ms){
var rows=document.querySelectorAll(".match-row");
for(var i=0;i<rows.length;i++){
(function(idx){
var mi=parseInt(rows[idx].getAttribute("data-mi"));if(isNaN(mi))mi=idx;
var m=safeA(ms,mi);if(!m)return;
rows[idx].style.cursor="pointer";
rows[idx].onclick=function(){
var detailId="detail-"+mi;var old=document.getElementById(detailId);
if(old){old.remove();return}
var div=document.createElement("div");div.id=detailId;div.className="detail-panel open";
div.innerHTML=detailHTML(m);rows[idx].after(div);
};
})(i);
}
}

function detailHTML(m){
var s="";
var hw=safe(m,"hw",0),dp=safe(m,"d_",0),aw=safe(m,"aw",0);
s+="<h4>鑳滃钩璐?/h4><div class=flex-row><span class='badge bg-green'>涓昏儨 "+hw+"%</span><span class='badge bg-yellow'>骞冲眬 "+dp+"%</span><span class='badge bg-red'>瀹㈣儨 "+aw+"%</span></div>";
s+="<div class='alert-box alert-info'>"+safe(m,"verdict","鍒嗘瀽涓?..")+" | 鏂瑰悜:"+safe(m,"dire","?")+" | 缃俊:"+safe(m,"conf","?")+"%</div>";
var scores=safe(m,"scores",[]);
s+="<h4>姣斿垎</h4><div class=score-grid>";
scores.slice(0,9).forEach(function(sc){
var p=sc.p||0,cls=p>=5?" top3":(p>=3?" top2":"");
s+="<div class='cell"+cls+"'><div class=s>"+sc.s+"</div><div class=p>"+p+"%</div></div>";
});
s+="</div>";
var tg=m.tg||[];
s+="<h4>鎬昏繘鐞?/h4><div class=flex-row style='flex-wrap:wrap;gap:4px'>";
if(tg.length){tg.forEach(function(t){s+="<span class='badge bg-blue'>"+t.g+"鐞?"+t.p+"%</span>"})}else{s+="<span class='badge'>鏃犳暟鎹?/span>"}
s+="</div>";
var hf=m.hf||[];
s+="<h4>鍗婂叏鍦?/h4><div class=flex-row style='flex-wrap:wrap;gap:4px'>";
if(hf.length){hf.forEach(function(h){s+="<span class='badge bg-purple'>"+h.r+":"+h.p+"%</span>"})}else{s+="<span class='badge'>鏃犳暟鎹?/span>"}
s+="</div>";
var hcp=safe(m,"hcp","-"),cov=safe(m,"cov",0);
s+="<h4>璁╃悆: "+hcp+"</h4><div class=prob-bar><div class=prob-bar-fill style='width:"+Math.round(cov*100)+"%;background:var(--green)'></div></div>";
var ur=safe(m,"conf",50)>=65?"浣?:(safe(m,"conf",50)>=45?"涓?:"楂?),urc=ur=="浣??"bg-green":(ur=="涓??"bg-yellow":"bg-red");
s+="<h4>鐖嗗喎椋庨櫓: <span class='badge "+urc+"'>"+ur+"</span></h4>";
// Fusion data
var fusionData=null;
if(STORE.fusion&&STORE.fusion.results){
for(var fi=0;fi<STORE.fusion.results.length;fi++){
var ff=STORE.fusion.results[fi];
if(ff.home===m.home&&ff.away===m.away){fusionData=ff;break}
}
}
if(fusionData&&fusionData.sources){
s+="<h4>澶氭簮铻嶅悎 <span class='badge bg-blue'>"+fusionData.agreement+"("+fusionData.agreement_pct+"%)</span></h4>";
s+="<div class=flex-row><span class='badge bg-green'>涓昏儨"+fusionData.win+"%</span><span class='badge bg-yellow'>骞?+fusionData.draw+"%</span><span class='badge bg-red'>瀹㈣儨"+fusionData.lose+"%</span></div>";
s+="<div class=small-text>缃俊:"+fusionData.confidence+"% | 椋庨櫓:"+fusionData.risk+" | 鎺ㄨ崘:"+(fusionData.recommended_play?fusionData.recommended_play.play:"?")+"</div>";
s+="<div class=grid-2 style='margin-top:6px'>";
["poisson","hercules","experts","liuyao"].forEach(function(sk){
var sr=fusionData.sources[sk];if(!sr)return;
var cl=sr.direction=="涓昏儨"?"bg-green":(sr.direction=="瀹㈣儨"?"bg-red":"bg-yellow");
s+="<div style='font-size:10px;padding:4px'><strong>"+sr.name+"</strong> ("+sr.weight+"%)<br><span class='badge "+cl+"'>"+sr.direction+"</span> "+sr.confidence+"%</div>";
});
s+="</div>";}
var he=m.hexp||{},ae=m.aexp||{};
s+="<div class=grid-2><div class=report-section><strong>"+safe(m,"home","?")+"</strong><br>灞傛:"+safe(he,"t","?")+" | 鏁欑粌:"+safe(he,"c","?")+"<br>"+safe(he,"f","?")+"<br>"+safe(he,"n","?")+"</div><div class=report-section><strong>"+safe(m,"away","?")+"</strong><br>灞傛:"+safe(ae,"t","?")+" | 鏁欑粌:"+safe(ae,"c","?")+"<br>"+safe(ae,"f","?")+"<br>"+safe(ae,"n","?")+"</div></div>";
return s;
}

function bindLiuyao(ms){
console.log("bindLiuyao called, ms length:",ms.length);
var rows=document.querySelectorAll(".match-row");console.log("match-row elements found:",rows.length);
for(var i=0;i<rows.length;i++){
(function(idx){
var mi=parseInt(rows[idx].getAttribute("data-mi"));if(isNaN(mi))mi=idx;
var m=safeA(ms,mi);if(!m)return;
rows[idx].style.cursor="pointer";
rows[idx].onclick=function(){
var panel=document.getElementById("hex-panel");if(!panel)return;
console.log("Liuyao click:",m.home,"vs",m.away);
panel.innerHTML="<div class=card><div class=spinner></div><p>鍗犲崪涓?..</p></div>";
fetch("/api/liuyao?home="+encodeURIComponent(m.home)+"&away="+encodeURIComponent(m.away))
.then(function(r){return r.json()}).then(function(d){
try{
var ly=d.liuyao||{},aus=ly.main_auspice||"";
var lv=aus.indexOf("澶у悏")>=0?5:aus.indexOf("鍚?)>=0?4:aus.indexOf("鍑?)>=0?1:aus.indexOf("骞?)>=0?3:2;
var stars="";for(var s=0;s<5;s++)stars+=s<lv?"鈽?:"鈽?;
var h="<div class=card><h2>鍏埢: "+d.home+" vs "+d.away+"</h2>";
h+="<div class=hex-coin>"+(ly.main_symbol||"?")+"</div>";
h+="<div class=hex-reading><h3>"+(ly.main_name||"")+"</h3><p>"+aus+"</p><p>"+(ly.main_text||"")+"</p><p style='font-size:20px'>"+stars+"</p>";
if(ly.changed_name)h+="<h4>鍙樺崷:"+ly.changed_name+"</h4><p>"+(ly.changed_auspice||"")+"</p>";
h+="<p><strong>鏂瑰悜: "+(ly.direction||"缁煎悎鍒ゆ柇")+"</strong></p>";
h+="<p style='font-size:10px;color:#94a3b8'>鑳滃钩璐? "+safe(m,"hw","?")+"% / "+safe(m,"d_","?")+"% / "+safe(m,"aw","?")+"%</p></div>";
h+=detailHTML(m);panel.innerHTML=h;
}catch(ex){panel.innerHTML="<div class='alert-box alert-danger'>"+ex.message+"</div>"}
}).catch(function(e){panel.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"});
};
})(i);
}
}

function buildMatchList(ms){
var s="";
ms.forEach(function(m,i){
// Fusion data
var fusionData=null;
if(STORE.fusion&&STORE.fusion.results){
for(var fi=0;fi<STORE.fusion.results.length;fi++){
var ff=STORE.fusion.results[fi];
if(ff.home===m.home&&ff.away===m.away){fusionData=ff;break}
}
}
if(fusionData&&fusionData.sources){
s+="<h4>澶氭簮铻嶅悎 <span class='badge bg-blue'>"+fusionData.agreement+"("+fusionData.agreement_pct+"%)</span></h4>";
s+="<div class=flex-row><span class='badge bg-green'>涓昏儨"+fusionData.win+"%</span><span class='badge bg-yellow'>骞?+fusionData.draw+"%</span><span class='badge bg-red'>瀹㈣儨"+fusionData.lose+"%</span></div>";
s+="<div class=small-text>缃俊:"+fusionData.confidence+"% | 椋庨櫓:"+fusionData.risk+" | 鎺ㄨ崘:"+(fusionData.recommended_play?fusionData.recommended_play.play:"?")+"</div>";
s+="<div class=grid-2 style='margin-top:6px'>";
["poisson","hercules","experts","liuyao"].forEach(function(sk){
var sr=fusionData.sources[sk];if(!sr)return;
var cl=sr.direction=="涓昏儨"?"bg-green":(sr.direction=="瀹㈣儨"?"bg-red":"bg-yellow");
s+="<div style='font-size:10px;padding:4px'><strong>"+sr.name+"</strong> ("+sr.weight+"%)<br><span class='badge "+cl+"'>"+sr.direction+"</span> "+sr.confidence+"%</div>";
});
s+="</div>";}
var he=m.hexp||{},ae=m.aexp||{};
var hw=safe(m,"hw",0),dp=safe(m,"d_",0),aw=safe(m,"aw",0),cf=safe(m,"conf",0);
s+="<div class='match-row' data-mi='"+i+"' style='display:flex;flex-direction:column;gap:6px'>";
s+="<div style='display:grid;grid-template-columns:1fr 120px 1fr;gap:12px;align-items:center'>";
s+="<div><div class=team-name>"+safe(m,"home","?")+"</div><div class=team-sub>"+safe(he,"t","")+"</div></div>";
s+="<div class=mid><div class=time>"+safe(m,"time","")+"</div><div class=league>"+safe(m,"lg","")+" | "+safe(m,"date","")+"</div></div>";
s+="<div><div class=team-name>"+safe(m,"away","?")+"</div><div class=team-sub>"+safe(ae,"t","")+"</div></div>";
s+="</div>";
s+="<div style='display:flex;gap:4px;font-size:10px;align-items:center;margin-top:2px'>";
s+="<span style='color:var(--green);min-width:38px;text-align:right'>涓?+hw.toFixed(0)+"%</span>";
s+="<div class='prob-bar' style='flex:1'><div class='prob-bar-fill' style='width:"+hw+"%;background:var(--green)'></div></div>";
s+="<span style='color:var(--yellow);min-width:28px;text-align:center'>骞?+dp.toFixed(0)+"%</span>";
s+="<div class='prob-bar' style='flex:1'><div class='prob-bar-fill' style='width:"+dp+"%;background:var(--yellow)'></div></div>";
s+="<span style='color:var(--red);min-width:38px'>瀹?+aw.toFixed(0)+"%</span>";
s+="<div class='prob-bar' style='flex:1'><div class='prob-bar-fill' style='width:"+aw+"%;background:var(--red)'></div></div>";
s+="<span class='badge "+(cf>=65?"bg-green":(cf>=45?"bg-yellow":"bg-red"))+"'>"+(cf>=65?"绋?:(cf>=45?"涓?:"闄?))+"</span>";
s+="</div></div>";
});
return s;
}

function buildDashboard(ms,pl){
var date=STORE.matches?safe(STORE.matches,"date",""):"";
var topConf=0,topPick="鏆傛棤",fusionDir="",fusionConf=0,fusionRisk="";
if(STORE.fusion&&STORE.fusion.results&&STORE.fusion.results.length>0){
var f0=STORE.fusion.results[0];
fusionDir=f0.direction||"";
fusionConf=f0.confidence||0;
fusionRisk=f0.risk||"涓?;
}
ms.forEach(function(m){var c=safe(m,"conf",0);if(c>topConf){topConf=c;topPick=safe(m,"dire","?")}});
var s="";
// Fusion highlight card
if(fusionDir){
var riskColor=fusionRisk=="浣??"var(--green)":(fusionRisk=="涓??"var(--accent)":"var(--red)");
s+="<div class=card style='border:2px solid var(--purple);background:linear-gradient(135deg,rgba(139,92,246,0.1),rgba(59,130,246,0.05))'>";
s+="<h2>鈿?澶氭簮铻嶅悎棰勬祴 <span class='badge bg-purple'>Poisson40%+AI25%+涓撳20%+鍏埢15%</span></h2>";
s+="<div class=dash-grid>";
s+="<div class=dash-stat><div class=num style=color:"+riskColor+">"+fusionDir+"</div><div class=lbl>铻嶅悎鏂瑰悜</div></div>";
s+="<div class=dash-stat><div class=num style=color:var(--green)>"+fusionConf+"%</div><div class=lbl>缁煎悎缃俊</div></div>";
s+="<div class=dash-stat><div class=num style=color:"+riskColor+">"+fusionRisk+"</div><div class=lbl>椋庨櫓绛夌骇</div></div>";
s+="</div></div>";
}
// Regular stats
s+="<div class=card><h2>浠婃棩姒傝 - "+date+"</h2><div class=dash-grid>";
s+="<div class=dash-stat><div class=num style=color:var(--accent)>"+ms.length+"</div><div class=lbl>姣旇禌鍦烘</div></div>";
s+="<div class=dash-stat><div class=num style=color:var(--green)>"+topPick+"</div><div class=lbl>鏈€绋?"+topConf+"%)</div></div>";
s+="<div class=dash-stat><div class=num>"+(pl.analyzed&&Array.isArray(pl.analyzed)?pl.analyzed.length:ms.length)+"</div><div class=lbl>宸插垎鏋?/div></div>";
s+="<div class=dash-stat><div class=num style=color:var(--yellow)>"+(pl.plans&&pl.plans.stable&&pl.plans.stable.singles?pl.plans.stable.singles.length:0)+"</div><div class=lbl>鏂规</div></div>";
s+="</div></div>";
s+="<div class=card><h2>蹇€熻烦杞?/h2><div style='display:flex;gap:8px;flex-wrap:wrap'>";
s+="<button class='btn btn-green' onclick=\"window.navigate('plans');setTimeout(function(){window._setRisk('stable')},400)\">绋冲畾绾㈠崟</button>";
s+="<button class=btn onclick=\"window.navigate('plans');setTimeout(function(){window._setRisk('solid')},400)\">绋冲仴鏂规</button>";
s+="<button class='btn btn-yellow' onclick=\"window.navigate('plans');setTimeout(function(){window._setRisk('aggro')},400)\">杩涘彇鏂规</button>";
s+="<button class='btn btn-red' onclick=\"window.navigate('plans');setTimeout(function(){window._setRisk('cold')},400)\">鍗氬喎鏂规</button>";
s+="<button class='btn btn-purple' onclick=\"window.navigate('multi')\">澶氭棩浠撳偍</button>";
s+="</div></div>";
s+="<div class=card><h2>浠婃棩姣旇禌</h2>"+buildMatchList(ms)+"</div>";
return s;
}
function buildMatches(ms){return "<div class=card><h2>姣旇禌鍒嗘瀽</h2>"+buildMatchList(ms)+"</div>"}
function buildLiuyao(ms){
var s="<div class=card><h2>鍏埢棰勬祴</h2><p class=small-text>鐐瑰嚮姣旇禌鍗犲崪 (鍏?+ms.length+"鍦?</p>";
ms.forEach(function(m,i){
var hw=m.hw||0,dp=m.d_||0,aw=m.aw||0;
s+="<div class='match-row' style='cursor:pointer;display:flex;flex-direction:column;gap:4px;padding:12px;margin-bottom:8px' onclick='window.doLiuyao(\""+m.home+"\",\""+m.away+"\")'>";
s+="<div style='display:flex;justify-content:space-between;align-items:center'>";
s+="<span style='font-weight:bold'>"+m.home+"</span><span style='color:var(--text2)'>vs</span><span style='font-weight:bold'>"+m.away+"</span>";
s+="<span style='font-size:10px;color:var(--text2)'>"+m.time+"</span>";
s+="</div>";
s+="<div style='display:flex;gap:4px;font-size:10px;align-items:center'>";
s+="<span style='color:var(--green)'>涓?+hw.toFixed(0)+"%</span><div class='prob-bar' style='flex:1'><div class='prob-bar-fill' style='width:"+hw+"%;background:var(--green)'></div></div>";
s+="<span style='color:var(--yellow)'>骞?+dp.toFixed(0)+"%</span><div class='prob-bar' style='flex:1'><div class='prob-bar-fill' style='width:"+dp+"%;background:var(--yellow)'></div></div>";
s+="<span style='color:var(--red)'>瀹?+aw.toFixed(0)+"%</span>";
s+="<button class='btn btn-sm'>鍗犲崪</button>";
s+="</div></div>";
});
s+="</div><div id=hex-panel></div>";
return s;
}

window.doLiuyao=function(home,away){
var panel=document.getElementById("hex-panel");
if(!panel){console.log("hex-panel not found");return;}
panel.innerHTML="<div class=card><div class=spinner></div><p>鍗犲崪涓? "+home+" vs "+away+"...</p></div>";
fetch("/api/liuyao?home="+encodeURIComponent(home)+"&away="+encodeURIComponent(away))
.then(function(r){return r.json()}).then(function(d){
try{
var ly=d.liuyao||{},aus=ly.main_auspice||"";
var lv=aus.indexOf("澶у悏")>=0?5:aus.indexOf("鍚?)>=0?4:aus.indexOf("鍑?)>=0?1:aus.indexOf("骞?)>=0?3:2;
var stars="";for(var s=0;s<5;s++)stars+=s<lv?"鈽?:"鈽?;
var h="<div class=card><h2>鍏埢: "+d.home+" vs "+d.away+"</h2>";
h+="<div style='font-size:48px;text-align:center;padding:16px'>"+(ly.main_symbol||"?")+"</div>";
h+="<div style='text-align:center'><h3>"+(ly.main_name||"")+"</h3><p style='font-size:18px'>"+aus+"</p>";
h+="<p style='font-size:24px;color:var(--yellow)'>"+stars+"</p>";
if(ly.changed_name)h+="<p>鍙樺崷: "+ly.changed_name+" - "+(ly.changed_auspice||"")+"</p>";
h+="<p style='margin-top:8px'><strong>鏂瑰悜: "+(ly.direction||"缁煎悎鍒ゆ柇")+"</strong></p>";
h+="<p style='font-size:11px;color:var(--text2)'>"+(ly.main_text||"")+"</p></div></div>";
panel.innerHTML=h;
}catch(ex){panel.innerHTML="<div class='alert-box alert-danger'>"+ex.message+"</div>"}
}).catch(function(e){panel.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"});
};

function buildPlans(){
var rn={stable:"绋冲畾绾㈠崟",solid:"绋冲仴鏂规",aggro:"杩涘彇鏂规",cold:"鍗氬喎鏂规"};
var s="<div class=card><h2>浠婃棩鎶曟敞鏂规</h2><div style='display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap'>";
["stable","solid","aggro","cold"].forEach(function(rk){
s+="<button class='risk-btn"+(CURRENT.risk===rk?" sel-"+rk:"")+"' onclick=\"window._setRisk('"+rk+"')\">"+rn[rk]+"</button>"
});
s+="</div><div class=grid-2><div><label class=small-text>鎶曞叆閲戦(鍏?</label><input type=number id=bet-amount value=100 min=2 step=10></div><div><label class=small-text>鏈熸湜鍥炴湰(鍏?</label><input type=number id=target-return value=500 min=10 step=50></div></div>";
s+="<button class='btn btn-green' onclick=window.genPlans()>鐢熸垚浠婃棩鏂规</button><div id=plan-result></div></div>";
return s;
}

window._setRisk=function(rk){CURRENT.risk=rk;showPage("plans");setTimeout(function(){try{window.genPlans()}catch(e){}},300)};

window.genPlans=function(){
var el=document.getElementById("plan-result");if(!el)return;
if(!STORE.plans){el.innerHTML="<div class='alert-box alert-warn'>鏂规鍔犺浇涓?..</div>";return}
try{
var amt=parseFloat(document.getElementById("bet-amount").value)||100;
var tgt=parseFloat(document.getElementById("target-return").value)||500;
var pl=STORE.plans;
var pdata=pl.plans||{},rp=pdata[CURRENT.risk]||{};
var singles=rp.singles||[],pairs=rp.pairs||[],triples=rp.triples||[],quads=rp.quads||[],mix=rp.mix||[];
var rn={stable:"绋冲畾绾㈠崟",solid:"绋冲仴鏂规",aggro:"杩涘彇鏂规",cold:"鍗氬喎鏂规"};
var s="<h4>"+rn[CURRENT.risk]+"</h4><div class='alert-box alert-info'>"+(rp.rec||"寤鸿:"+CURRENT.risk)+" | 鎶曞叆:"+amt+"鍏?| 鐩爣:"+tgt+"鍏?/div>";

var remAmt=amt;
s+="<div class=card><h4>7鏃ヤ粨鍌?鏈噾"+amt+")</h4><div class=multi-day-plan>";
for(var d=1;d<=7;d++){var bet=Math.min(remAmt*0.4,Math.max(2,remAmt*(0.12+d*0.01)));remAmt=Math.max(0,remAmt-bet);
s+="<div class=day-card><div class=day-num>Day "+d+"</div><div class=day-info>鎶曟敞:"+bet.toFixed(1)+"<br>鍓╀綑:"+remAmt.toFixed(0)+"</div></div>"}
s+="</div></div>";

function pi(it){
if(!it)return "<div class='plan-item small-text'>绌烘暟鎹?/div>";
var cf,pick,mn,odds;
if(it.ms&&Array.isArray(it.ms)){
cf=Math.round((it.prob||0)*100)||50;
pick=it.ms.map(function(si){return si.pick||"?"}).join("+");
mn=it.ms.map(function(si){return si.m||""}).join(" | ");
odds=it.odds||1;
}else{
cf=it.cf||it.conf||50;pick=it.pick||"?";mn=it.m||"";odds=it.odds||1;
}
var cls=cf>=60?"bg-green":(cf>=40?"bg-blue":"bg-yellow");
return "<div class=plan-item><div class=flex-row><span class='badge "+cls+"'>"+cf+"%</span><strong>"+pick+"</strong><span class='badge bg-purple'>"+mn+"</span></div><div class=small-text>璧旂巼:"+odds.toFixed(2)+" | 鍥炴湰:"+(amt*odds).toFixed(0)+"鍏?| 寤鸿"+(Math.max(1,Math.round(amt/50)))+"鍊?/div></div>";
}

var ba=Math.max(2,Math.min(amt*0.25,100));
s+="<div class=section-title>鍗曞叧</div>";
if(singles.length>0){singles.forEach(function(si){s+=pi(si)})}else{s+="<div class='plan-item small-text'>鏃犳弧瓒抽棬妲涚殑鍗曞叧鍦烘</div>"}
s+="<div class=section-title>2涓?</div>";
if(pairs.length>0){pairs.forEach(function(pa){s+=pi(pa)})}else{s+="<div class='plan-item small-text'>鏆傛棤</div>"}
s+="<div class=section-title>3涓?</div>";
if(triples.length>0){triples.forEach(function(tr){s+=pi(tr)})}else{s+="<div class='plan-item small-text'>鏆傛棤</div>"}
s+="<div class=section-title>4涓?</div>";
if(quads.length>0){quads.forEach(function(q){s+=pi(q)})}else{s+="<div class='plan-item small-text'>鏆傛棤</div>"}
if(mix.length>0){
s+="<div class=section-title>娣峰悎涓插叧 <span class=small-text>鏅鸿兘鎺ㄨ崘</span></div>";
mix.forEach(function(mx){
var label=mx.t||"娣峰悎";
var odds=mx.odds||1;
var prob=mx.prob||0;
var cls2=prob>=60?"bg-green":(prob>=40?"bg-blue":"bg-yellow");
s+="<div class=plan-item><div class=flex-row><span class='badge "+cls2+"'>"+prob+"%</span><strong>"+label+"</strong></div><div class=small-text>璧旂巼:"+odds.toFixed(2)+" | 鏈熸湜:"+(amt*odds).toFixed(0)+"鍏?/div></div>";
});
}
el.innerHTML=s;
}catch(e){
console.error(e);
el.innerHTML="<div class='alert-box alert-danger'>鐢熸垚鏂规鍑洪敊: "+e.message+"</div>";
}
};

function buildIntel(ms){
var s="<div class=card><h2>鏅鸿兘鐜╂硶鎺ㄨ崘</h2><p class=small-text>鍩轰簬娉婃澗妯″瀷鑷姩鍒嗘瀽鏈€浣崇帺娉?/p></div>";
ms.forEach(function(m){
var hw=safe(m,"hw",0),dp=safe(m,"d_",0),aw=safe(m,"aw",0);
var maxP=Math.max(hw,dp,aw),sp=maxP-Math.min(hw,dp,aw);
var best,reason;
if(maxP>=55&&sp>=20){best="鑳滃钩璐?;reason=(maxP==hw?m.home+"鑳?:(maxP==aw?m.away+"鑳?:"骞冲眬"))+" 姒傜巼"+maxP+"%"}
else if(safeA(m.tg||[],0)&&safeA(m.tg||[],0,{}).p>15){var t0=m.tg[0];best="鎬昏繘鐞?;reason=t0.g+"鐞冩鐜?+t0.p+"%"}
else{best="鍗婂叏鍦?;reason="涓嶇‘瀹氭€ч珮锛屽缓璁崐鍏ㄥ満闄嶄綆椋庨櫓"}
var ur=safe(m,"conf",50)>=65?"浣?:(safe(m,"conf",50)>=45?"涓?:"楂?),urc=ur=="浣??"bg-green":(ur=="涓??"bg-yellow":"bg-red");
var tgR=(m.tg||[]).slice(0,3).map(function(t){return t.g+"鐞?"+t.p+"%"}).join(" ");
var hfR=(m.hf||[]).slice(0,3).map(function(h){return h.r+":"+h.p+"%"}).join(" ");
s+="<div class=card style='border-left:3px solid "+(best=="鑳滃钩璐??"var(--green)":(best=="鎬昏繘鐞??"var(--accent)":"var(--purple)"))+"'>";
s+="<h3>"+safe(m,"home","?")+" vs "+safe(m,"away","?")+" <span style='font-size:12px;color:var(--text2)'>"+safe(m,"time","")+"</span></h3>";
s+="<div class=flex-row><span class='badge bg-blue'>鎺ㄨ崘:"+best+"</span><span class='badge "+urc+"'>鐖嗗喎:"+ur+"</span></div>";
s+="<p class=small-text>"+reason+"</p>";
s+="<div class=flex-row style='margin:4px 0'><span class='badge bg-green'>涓?+hw+"%</span><span class='badge bg-yellow'>骞?+dp+"%</span><span class='badge bg-red'>瀹?+aw+"%</span></div>";
s+="<div class=small-text>鎬昏繘鐞僒OP3: "+tgR+"</div>";
s+="<div class=small-text>鍗婂叏鍦篢OP3: "+hfR+"</div></div>";
});
return s;
}

function buildMulti(){
return "<div class=card><h2>澶氭棩浠撳偍</h2><div class=grid-2><div><label class=small-text>鍓╀綑閲戦(鍏?</label><input type=number id=storage-amount value=200 min=10></div><div><label class=small-text>鐩爣閲戦(鍏?</label><input type=number id=storage-target value=1000 min=20></div></div><div><label class=small-text>澶╂暟</label><select id=storage-days><option value=7>7澶?/option><option value=14>14澶?/option><option value=30>30澶?/option></select></div><button class='btn btn-green' onclick=window.genMultiPlan()>鐢熸垚璁″垝</button><div id=multi-result></div></div>";
}

window.genMultiPlan=function(){
var el=document.getElementById("multi-result");if(!el)return;
try{
var p=parseFloat(document.getElementById("storage-amount").value)||200,tgt=parseFloat(document.getElementById("storage-target").value)||1000,days=parseInt(document.getElementById("storage-days").value)||7;
var s="<div class=card><h4>浠撳偍璁″垝(鏈噾"+p+",鐩爣"+tgt+","+days+"澶?</h4><div class=multi-day-plan>";
var rem=p;
for(var d=1;d<=days;d++){
var ratio=Math.min(0.3,0.1+(d/days)*0.2);
var bet=Math.max(2,rem*ratio);
rem=Math.max(0,rem-bet+bet*0.65);
s+="<div class=day-card><div class=day-num>Day "+d+"</div><div class=day-info>鎶曟敞:"+bet.toFixed(1)+"<br>浣欓:"+rem.toFixed(0)+"</div></div>"
}
s+="</div></div>";el.innerHTML=s;
}catch(e){el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"}
};

function buildHercules(){return "<div class=card><h2>澶у姏绁炵畻</h2><div id=herc-content><div class=spinner></div><p>澶氭櫤鑳戒綋鍒嗘瀽寮曟搸杩愯涓?..</p></div></div>"}
function loadHercules(ms){
var el=document.getElementById("herc-content");if(!el)return;
var t=setTimeout(function(){el.innerHTML="<div class='alert-box alert-warn'>鍒嗘瀽瓒呮椂</div>"},20000);
fetch("/api/hercules?home="+encodeURIComponent(ms.length>0?ms[0].home:"")+"&away="+encodeURIComponent(ms.length>0?ms[0].away:"")).then(function(r){return r.json()}).then(function(d){
clearTimeout(t);
var preds=d.predictions||(d.prediction?[d.prediction]:[]);
if(!preds.length){el.innerHTML="<div class='alert-box alert-info'>澶у姏绁炵畻寰呭懡涓?/div>";return}
var s="";
preds.forEach(function(p,i){
var m=safeA(ms,i,{});
var pp=p.prediction||p;  // unwrap nested prediction
s+="<div class=card><h3>"+safe(pp,"home",safe(m,"home","?"))+" vs "+safe(pp,"away",safe(m,"away","?"))+"</h3>";
// Get win/draw/lose from match data since hercules doesn't always include it
var mhw=safe(m,"hw",0),mdp=safe(m,"d_",0),maw=safe(m,"aw",0);
if(mhw>0)s+="<div class=flex-row><span class='badge bg-green'>鑳?+mhw+"%</span><span class='badge bg-yellow'>骞?+mdp+"%</span><span class='badge bg-red'>璐?+maw+"%</span></div>";
var score=pp.final_score||pp.predicted_score||"";
if(score)s+="<p style='font-size:14px;margin-top:4px'>棰勬祴姣斿垎: <strong>"+score+"</strong></p>";
s+="<p class=small-text>鍏辫瘑: "+(pp.consensus||"?")+" | 鍚屾剰搴?"+(pp.agreement_score||"?")+"% | 鑼冨洿:"+(pp.score_range||"?")+"</p>";
// Risk summary
var risks=pp.risk_summary||[];
if(risks.length>0){
s+="<div class=small-text>椋庨櫓鍥犵礌: ";
risks.forEach(function(r){s+="<span class='badge "+(r.level=="楂??"bg-red":(r.level=="涓??"bg-yellow":"bg-green"))+"'>"+r.factor+": "+r.detail+"</span> "});
s+="</div>";}
// Agents detail
var agents=pp.agents_detail||[];
if(agents.length>0){
s+="<div style='margin:10px 0'>";
agents.forEach(function(a){
var icon=a.icon||"";
var confColor=a.confidence>=70?"var(--green)":(a.confidence>=50?"var(--accent)":"var(--yellow)");
s+="<div class=plan-item style='border-left:3px solid "+confColor+"'>";
s+="<strong>"+icon+" "+a.agent+"</strong> <span class=small-text>(淇″績:"+(a.confidence||"?")+"%)</span>";
s+="<p class=small-text>"+(a.verdict||"?")+(a.score?" | 姣斿垎:"+a.score:"")+"</p>";
var kf=a.key_findings||[];
kf.slice(0,4).forEach(function(f){if(f)s+="<p class=small-text>- "+f+"</p>"});
s+="</div>";
});
s+="</div>";}
// Model comparison
var mc=pp.model_comparison;
if(mc){
s+="<div class='alert-box alert-info'><strong>妯″瀷瀵规瘮: </strong>"+(mc.agreement||"?")+" | "+(mc.agreement_note||"")+"</div>";
}
s+="</div>";
});
el.innerHTML=s;
}).catch(function(e){clearTimeout(t);el.innerHTML}).catch(function(e){clearTimeout(t);el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"});
}

function buildDebate(){return "<div class=card><h2>涓撳杈╄</h2><div id=debate-content><div class=spinner></div><p>涓撳鍒嗘瀽涓?..</p></div></div>"}
function loadDebate(ms){
var el=document.getElementById("debate-content");if(!el)return;
var t=setTimeout(function(){el.innerHTML="<div class='alert-box alert-warn'>杈╄瓒呮椂</div>"},15000);
fetch("/api/experts?home=&away=").then(function(r){return r.json()}).then(function(d){
clearTimeout(t);
try{
var experts=d.experts||{},s="";
if(Object.keys(experts).length===0){el.innerHTML="<div class='alert-box alert-info'>涓撳绯荤粺寰呭懡涓?/div>";return}
Object.keys(experts).forEach(function(k){var ex=experts[k];var name=ex.agent||ex.name||k;
var ex=experts[k];
s+="<div class='card "+(ex.vote=="win"?"debate-win":(ex.vote=="draw"?"debate-draw":"debate-lose"))+"'>";
s+="<h4>"+name+": "+(ex.verdict||ex.vote||"?")+"</h4>";
s+="<p class=small-text><strong>"+(ex.verdict||ex.vote||"?")+"</strong></p>";
if(ex.key_findings&&ex.key_findings.length>0){
ex.key_findings.slice(0,5).forEach(function(f){if(f)s+="<p class=small-text>- "+f+"</p>"});
}
s+="</div>";
});
el.innerHTML=s;
}catch(e){el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"}
}).catch(function(e){clearTimeout(t);el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"});
}

function buildCompare(ms){
var s="<div class=card><h2>鐞冮槦瀵规瘮</h2></div>";
ms.forEach(function(m,i){
// Fusion data
var fusionData=null;
if(STORE.fusion&&STORE.fusion.results){
for(var fi=0;fi<STORE.fusion.results.length;fi++){
var ff=STORE.fusion.results[fi];
if(ff.home===m.home&&ff.away===m.away){fusionData=ff;break}
}
}
if(fusionData&&fusionData.sources){
s+="<h4>澶氭簮铻嶅悎 <span class='badge bg-blue'>"+fusionData.agreement+"("+fusionData.agreement_pct+"%)</span></h4>";
s+="<div class=flex-row><span class='badge bg-green'>涓昏儨"+fusionData.win+"%</span><span class='badge bg-yellow'>骞?+fusionData.draw+"%</span><span class='badge bg-red'>瀹㈣儨"+fusionData.lose+"%</span></div>";
s+="<div class=small-text>缃俊:"+fusionData.confidence+"% | 椋庨櫓:"+fusionData.risk+" | 鎺ㄨ崘:"+(fusionData.recommended_play?fusionData.recommended_play.play:"?")+"</div>";
s+="<div class=grid-2 style='margin-top:6px'>";
["poisson","hercules","experts","liuyao"].forEach(function(sk){
var sr=fusionData.sources[sk];if(!sr)return;
var cl=sr.direction=="涓昏儨"?"bg-green":(sr.direction=="瀹㈣儨"?"bg-red":"bg-yellow");
s+="<div style='font-size:10px;padding:4px'><strong>"+sr.name+"</strong> ("+sr.weight+"%)<br><span class='badge "+cl+"'>"+sr.direction+"</span> "+sr.confidence+"%</div>";
});
s+="</div>";}
var he=m.hexp||{},ae=m.aexp||{};
s+="<div class=card><h3>"+safe(m,"home","?")+" vs "+safe(m,"away","?")+"</h3>";
s+="<div class=grid-2><div class=report-section><strong>"+safe(m,"home","?")+"</strong><br>灞傛:"+safe(he,"t","?")+"<br>鏁欑粌:"+safe(he,"c","?")+"<br>"+safe(he,"f","?")+"<br>"+safe(he,"n","?")+"</div><div class=report-section><strong>"+safe(m,"away","?")+"</strong><br>灞傛:"+safe(ae,"t","?")+"<br>鏁欑粌:"+safe(ae,"c","?")+"<br>"+safe(ae,"f","?")+"<br>"+safe(ae,"n","?")+"</div></div>";
s+="<div class=flex-row><span class='badge bg-green'>涓昏儨"+safe(m,"hw","?")+"%</span><span class='badge bg-yellow'>骞?+safe(m,"d_","?")+"%</span><span class='badge bg-red'>瀹㈣儨"+safe(m,"aw","?")+"%</span></div>";
s+="<div class='alert-box alert-info'>"+safe(m,"verdict","")+"</div></div>";
});
return s;
}

function buildBets(){return "<div class=card><h2>鎶曟敞涓撳</h2><div id=bets-content><div class=spinner></div><p>鎶曟敞涓撳鍔犺浇涓?..</p></div></div>"}
function loadBets(){
var el=document.getElementById("bets-content");if(!el)return;
setTimeout(function(){
el.innerHTML="<div class='alert-box alert-success'>6浣嶄笓瀹跺凡灏辩华<br><br>鈽?鑳滃钩璐熶笓瀹?鈽?璁╃悆涓撳 鈽?鎬昏繘鐞冧笓瀹?br>鈽?姣斿垎涓撳 鈽?鍗婂叏鍦轰笓瀹?鈽?璧勯噾鍒嗛厤涓撳<br><br>璇锋煡鐪媆"涓撳杈╄\"鍜孿"浠婃棩鏂规\"椤佃幏鍙栬缁嗗垎鏋愩€?/div>";
},2000);
}

function buildPostMatch(ms){
var s="<div class=card><h2>璧涘悗澶嶇洏</h2><p class=small-text>杈撳叆瀹為檯姣斿垎锛孉I鍒嗘瀽棰勬祴鍑嗙‘搴?/p></div>";
ms.forEach(function(m,i){
s+="<div class=card><h3>"+safe(m,"home","?")+" vs "+safe(m,"away","?")+"</h3><div class=flex-row><span class='badge bg-green'>涓?+safe(m,"hw","?")+"%</span><span class='badge bg-yellow'>骞?+safe(m,"d_","?")+"%</span><span class='badge bg-red'>瀹?+safe(m,"aw","?")+"%</span></div>";
s+="<p><input type=text id='pm-score-"+i+"' placeholder='瀹為檯姣斿垎 濡?-1' style='width:130px;display:inline;margin-right:8px'><button class='btn btn-sm' onclick=\"window.submitPM('"+m.home+"','"+m.away+"',"+i+")\">鎻愪氦</button></p><div id='pm-result-"+i+"'></div></div>";
});
return s;
}
window.submitPM=function(h,a,i){
var v=document.getElementById("pm-score-"+i).value;if(!v)return;
var r=document.getElementById("pm-result-"+i);if(r)r.innerHTML="<div class=spinner></div>";
fetch("/api/post_match",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({home:h,away:a,prediction:"auto",actual:v})})
.then(function(res){return res.json()}).then(function(d){
if(r)r.innerHTML="<div class='alert-box alert-info'>鍑嗙‘搴?"+safe(d,"accuracy_score",0)+"/10 | "+(d.deviation_analysis||"鍒嗘瀽瀹屾垚")+"</div>";
}).catch(function(e){if(r)r.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"});
};

function buildROI(){return "<div class=card><h2>AI鎶曟敞鍥炴姤鐜?/h2><div id=roi-content><div class=spinner></div><p>鍔犺浇涓?..</p></div></div>"}
function escapeHtml(s){if(!s)return"";return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function loadROI(){
console.log("loadROI called");
var el=document.getElementById("roi-content");if(!el){console.log("roi-content missing");return;}
el.innerHTML="<div class=spinner></div><p>鍔犺浇涓?..</p>";
fetch("/api/roi").then(function(r){return r.json()}).then(function(d){
console.log("ROI data:",d.total_bets,"bets,",(d.records||[]).length,"records");
try{
var s="";
if(d&&d.total_bets>0){
s+="<div class=dash-grid><div class=dash-stat><div class=num>"+d.total_bets+"</div><div class=lbl>鎬绘姇娉?/div></div><div class=dash-stat><div class=num style=color:var(--green)>"+safe(d,"wins",0)+"</div><div class=lbl>鍛戒腑</div></div><div class=dash-stat><div class='num "+(safe(d,"roi",0)>=0?"roi-up":"roi-down")+"'>"+safe(d,"roi",0).toFixed(1)+"%</div><div class=lbl>鍥炴姤鐜?/div></div><div class=dash-stat><div class=num>CNY "+safe(d,"total_profit",0).toFixed(0)+"</div><div class=lbl>鐩堜簭</div></div></div>";
var recs=d.records||[];
if(recs.length>0){
s+="<h4 style='margin-top:16px'>鎶曟敞璁板綍 ("+recs.length+"绗?</h4>";
s+="<div style='overflow-x:auto'><table><thead><tr><th>姣旇禌</th><th>棰勬祴</th><th>绫诲瀷</th><th>閲戦</th><th>璧旂巼</th><th>鐘舵€?/th></tr></thead><tbody>";
var showRecs=recs.slice(-20).reverse();
showRecs.forEach(function(r){
var status=r.pending?"寰呯粨绠?:(r.won?"涓":"鏈腑");
var sc=r.pending?"bg-blue":(r.won?"bg-green":"bg-red");
s+="<tr><td>"+escapeHtml(r.match)+"</td><td>"+escapeHtml(r.prediction)+"</td><td>"+escapeHtml(r.bet_type)+"</td><td>"+r.bet_amount+"鍏?/td><td>"+r.odds+"</td><td><span class='badge "+sc+"'>"+status+"</span></td></tr>";
});
s+="</tbody></table></div>";
}
}else{s="<div class='alert-box alert-info'>鏆傛棤鎶曟敞璁板綍銆傜偣鍑讳笅鏂规寜閽ā鎷熸姇娉ㄣ€?/div>"}
s+="<button class=btn onclick='window.simBet()' style='margin-top:12px'>妯℃嫙浠婃棩鎶曟敞</button><div id=sim-result></div>";
el.innerHTML=s;
}catch(e){console.error("ROI render err:",e);el.innerHTML="<div class='alert-box alert-danger'>娓叉煋閿欒: "+e.message+"</div>"}
}).catch(function(e){console.error("ROI fetch err:",e);el.innerHTML="<div class='alert-box alert-danger'>鍔犺浇澶辫触: "+e.message+"</div>"});
}window.simBet=function(){
var el=document.getElementById("sim-result");if(!el)return;
el.innerHTML="<div class=spinner></div><p>AI姝ｅ湪妯℃嫙鎶曟敞...</p>";
var ms=(STORE.matches&&STORE.matches.matches)?STORE.matches.matches:[];
var fusion=STORE.fusion&&STORE.fusion.results?STORE.fusion.results:[];
var bets=[];
// For each match, find best pick from fusion
ms.forEach(function(m,i){
var ff=fusion.find(function(f){return f.home===m.home&&f.away===m.away});
var dir=ff?ff.direction:(m.hw>m.aw?"涓昏儨":"瀹㈣儨");
var conf=ff?ff.confidence:(Math.max(m.hw,m.d_,m.aw));
var score=m.scores&&m.scores.length>0?m.scores[0].s:"1-0";
var odds=conf>60?1.5:(conf>45?2.0:3.0);
var amt=Math.floor(Math.random()*50)+10; // 10-60 random
bets.push({match:m.home+" vs "+m.away,home:m.home,away:m.away,prediction:score,actual:"pending",odds:odds,bet_amount:amt,bet_type:dir});
});
// Submit all bets
var done=0,total=bets.length;
function submitNext(){
if(done>=total){
el.innerHTML="<div class='alert-box alert-success'>鉁?AI宸叉ā鎷?+total+"鍦烘姇娉紝鎬婚噾棰?"+bets.reduce(function(s,b){return s+b.bet_amount},0)+"鍏?br>姣忓満鎸夋渶楂樺噯纭巼鏂瑰悜涓嬫敞锛岃禌鍚庡埌澶嶇洏椤靛～鍏ユ瘮鍒嗙粨绠椼€?/div>";
setTimeout(function(){window.navigate("roi")},2000);
return;
}
var b=bets[done];
fetch("/api/roi/add",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)})
.then(function(r){return r.json()}).then(function(){
done++;submitNext();
}).catch(function(){
done++;submitNext();
});
}
submitNext();
};

function buildNews(){return "<div class=card><h2>涓栫晫鏉柊闂讳腑蹇?/h2><p class=small-text>澶氭簮鑱氬悎 路 titan007/鏂版氮/鐩存挱鍚?鑵捐</p><div id=news-content><div class=spinner></div></div></div>"}
function loadNews(){
var el=document.getElementById("news-content");if(!el)return;
fetch("/api/news").then(function(r){return r.json()}).then(function(d){
var s="";var items=d.items||[];
if(items.length>0){
s+="<p class=small-text>鏇存柊: "+d.updated+" | 鍏?+items.length+"鏉?/p>";
s+="<button class='btn btn-sm' onclick='loadNews()' style='margin-bottom:8px'>鍒锋柊</button>";
items.forEach(function(n){
var srcColor=n.source=="titan007"?"bg-purple":(n.source.indexOf("鏂版氮")>=0?"bg-red":"bg-blue");
s+="<div class='card' style='padding:10px;margin-bottom:6px;border-left:3px solid var(--accent)'>";
s+="<div style='display:flex;justify-content:space-between;align-items:center'>";
s+="<span style='font-size:13px'>"+n.title+"</span>";
s+="<span class='badge "+srcColor+"'>"+n.source+"</span>";
s+="</div><div class=small-text>"+n.type+" | "+n.time+"</div></div>";
});
}else{s="<div class='alert-box alert-warn'>鏆傛棤鏂伴椈銆傚叧闂瑿odex妗岄潰鍙屽嚮鍚姩鍚庡彲鑷姩鎶撳彇 titan007/鏂版氮/鐩存挱鍚?鑵捐</div>"}
el.innerHTML=s;
}).catch(function(e){el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"});
}

function buildAuto(){return "<div class=card><h2>鑷姩鍒嗘瀽甯?/h2><p class=small-text>AI鑷姩鎼滅储+鐭ヨ瘑搴撶敓鎴愭瘡鏃ユ瘮璧涘垎鏋?/p><div id=auto-content><div class=spinner></div><p>鍒嗘瀽涓?..</p></div></div>"}
function loadAuto(){
var el=document.getElementById("auto-content");if(!el)return;
el.innerHTML="<div class=spinner></div><p>AI姝ｅ湪鑷姩鍒嗘瀽姣旇禌...</p>";
fetch("/api/auto_analysis").then(function(r){return r.json()}).then(function(d){
try{
var s="";
if(d.analyses&&d.analyses.length>0){
d.analyses.forEach(function(a,i){
var m=a.match_data||{};
s+="<div class=card style='border-left:3px solid var(--accent)'>";
s+="<h3>"+(m.home||"?")+" vs "+(m.away||"?")+"</h3>";
s+="<p class=small-text>"+a.tactical_matchup+"</p>";
if(a.key_factors&&a.key_factors.length>0){
s+="<ul style='font-size:12px;margin:8px 0'>";
a.key_factors.forEach(function(k){s+="<li>"+k+"</li>"});
s+="</ul>";
}
if(a.prediction)s+="<p><strong>棰勬祴: "+a.prediction+"</strong></p>";
if(a.web_snippets&&a.web_snippets.length>0){
s+="<details><summary>缃戠粶淇℃伅 ("+a.web_snippets.length+"鏉?</summary>";
a.web_snippets.forEach(function(sn){s+="<p class=small-text style='padding:4px;background:var(--bg);border-radius:4px;margin:2px'>"+sn.substring(0,150)+"</p>"});
s+="</details>";
}
s+="</div>";
});
}
if(d.knowledge_base_stats){
var kb=d.knowledge_base_stats;
s+="<div class=card><h3>鐭ヨ瘑搴撶粺璁?/h3>";
s+="<div class=dash-grid><div class=dash-stat><div class=num>"+(kb.videos_learned||0)+"</div><div class=lbl>瀛︿範瑙嗛</div></div>";
s+="<div class=dash-stat><div class=num>"+(kb.teams_known||0)+"</div><div class=lbl>宸茬煡鐞冮槦</div></div>";
s+="<div class=dash-stat><div class=num>"+(kb.patterns||0)+"</div><div class=lbl>鎴樻湳妯″紡</div></div>";
if(kb.accuracy&&kb.accuracy.total)s+="<div class=dash-stat><div class=num style=color:var(--green)>"+(kb.accuracy.rate||0)+"%</div><div class=lbl>棰勬祴鍑嗙‘鐜?/div></div>";
s+="</div></div>";
}
el.innerHTML=s||"<div class='alert-box alert-info'>鏆傛棤鍒嗘瀽鏁版嵁</div>";
}catch(e){el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"}
}).catch(function(e){el.innerHTML="<div class='alert-box alert-danger'>鍔犺浇澶辫触: "+e.message+"</div>"});
}

function buildTimeAnalysis(){return "<div class=card><h2>鏃舵鍒嗘瀽</h2><div id=time-content><div class=spinner></div><p>鍒嗘瀽鏃╁満/涓満/鏅氬満鍐烽棬鐜?..</p></div></div>"}
function loadTimeAnalysis(){
var el=document.getElementById("time-content");if(!el)return;
var t=setTimeout(function(){el.innerHTML="<div class='alert-box alert-warn'>鍒嗘瀽瓒呮椂</div>"},10000);
fetch("/api/time_analysis").then(function(r){return r.json()}).then(function(d){
clearTimeout(t);var s="";
try{
Object.keys(d).forEach(function(seg){
var v=d[seg];
var sc=v.upset_risk=="楂??"var(--red)":(v.upset_risk=="涓??"var(--yellow)":"var(--green)");
s+="<div class=card style='border-left:4px solid "+sc+"'>";
s+="<h3>"+seg+" <span class='badge' style='background:"+sc+";color:#fff'>鍐烽棬椋庨櫓:"+(v.upset_risk||"?")+"</span></h3>";
s+="<div class=dash-grid><div class=dash-stat><div class=num>"+(v.count||0)+"</div><div class=lbl>鍦烘</div></div>";
s+="<div class=dash-stat><div class=num style=color:var(--accent)>"+(v.avg_confidence||0)+"%</div><div class=lbl>鍧囩疆淇?/div></div>";
s+="<div class=dash-stat><div class=num style=color:"+sc+">"+(v.high_risk_count||0)+"</div><div class=lbl>楂橀闄╁満</div></div></div>";
if(v.matches&&v.matches.length>0){
s+="<div style='margin-top:8px'>";
v.matches.forEach(function(m){s+="<div class='plan-item' style='display:flex;justify-content:space-between'><span>"+m.home+" vs "+m.away+"</span><span class=small-text>"+m.time+" | 缃俊:"+m.conf+"% | "+m.dire+"</span></div>"});
s+="</div>";}
s+="</div>";
});
el.innerHTML=s||"<div class='alert-box alert-info'>鏆傛棤鏁版嵁</div>";
}catch(e){el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"}
}).catch(function(e){clearTimeout(t);el.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"});
}

function buildLearn(){return "<div class=card><h2>AI鑷涔?/h2><div id=learn-stats><div class=spinner></div><p>鍔犺浇瀛︿範鏁版嵁...</p></div><div id=learn-history></div></div>"}
function loadLearnStats(){
var statsEl=document.getElementById("learn-stats");if(!statsEl)return;
fetch("/api/learn/stats").then(function(r){return r.json()}).then(function(d){
try{
var s="<div class='alert-box alert-info'>AI閫氳繃璧涘悗澶嶇洏鑷姩淇棰勬祴妯″瀷</div>";
s+="<div class=dash-grid>";
s+="<div class=dash-stat><div class=num>"+(d.total||0)+"</div><div class=lbl>鎬婚娴?/div></div>";
s+="<div class=dash-stat><div class=num style=color:var(--green)>"+(d.accuracy||0)+"%</div><div class=lbl>鏂瑰悜鍑嗙‘鐜?/div></div>";
s+="<div class=dash-stat><div class=num style=color:var(--accent)>"+(d.exact_scores||0)+"</div><div class=lbl>绮剧‘姣斿垎</div></div>";
s+="<div class=dash-stat><div class='num "+(d.bayesian_weight>=0.7?"roi-up":"roi-down")+"'>"+d.bayesian_weight+"</div><div class=lbl>璐濆彾鏂潈閲?/div></div></div>";
if(d.confidence_accuracy){
s+="<h4>鍒嗙骇鍑嗙‘鐜?/h4><div class=flex-row>";
var ca=d.confidence_accuracy;
s+="<span class='badge bg-green'>楂樼疆淇? "+ca.high+"%</span>";
s+="<span class='badge bg-yellow'>涓疆淇? "+ca.medium+"%</span>";
s+="<span class='badge bg-red'>浣庣疆淇? "+ca.low+"%</span>";
s+="</div>";}
s+="<h4>鍐烽棬妫€娴?/h4><div class=flex-row>";
s+="<span class='badge bg-green'>鎴愬姛棰勮: "+(d.upset_detected||0)+"</span>";
s+="<span class='badge bg-red'>婕忔姤: "+(d.upset_missed||0)+"</span></div>";
s+="<div class='alert-box alert-success'>璧涘悗濉叆姣斿垎鑷姩瑙﹀彂瀛︿範</div>";
statsEl.innerHTML=s;
}catch(e){statsEl.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"}
}).catch(function(e){statsEl.innerHTML="<div class='alert-box alert-warn'>鑷涔犲紩鎿庡緟鍚姩</div>"});

fetch("/api/learn/history?limit=10").then(function(r){return r.json()}).then(function(d){
var he=document.getElementById("learn-history");if(!he)return;
try{
var s="<h4>鏈€杩戣褰?/h4>";
if(!d.history||!d.history.length){he.innerHTML=s+"<div class='alert-box alert-info'>鏆傛棤棰勬祴璁板綍</div>";return}
s+="<table><tr><th>姣旇禌</th><th>棰勬祴</th><th>瀹為檯</th><th>缁撴灉</th></tr>";
d.history.reverse().forEach(function(p){
var cls=p.correct_direction?"bg-green":(p.reviewed?"bg-red":"");
s+="<tr><td>"+p.home+" vs "+p.away+"</td><td>"+p.pred_score+"</td><td>"+(p.actual_score||"?")+"</td><td><span class='badge "+cls+"'>"+(p.reviewed?(p.correct_direction?"姝ｇ‘":"閿欒"):"寰呭畾")+"</span></td></tr>";
});
s+="</table>";he.innerHTML=s;
}catch(e){he.innerHTML="<div class='alert-box alert-danger'>"+e.message+"</div>"}
}).catch(function(e){});
}

// SIDEBAR INIT
setTimeout(function(){
var items=document.querySelectorAll(".sidebar-item");
for(var i=0;i<items.length;i++){
try{
items[i].addEventListener("click",function(e){
e.preventDefault();
var page=this.getAttribute("data-page")||"dashboard";
window.navigate(page);
});
}catch(e){console.log("sidebar err:",e)}
}
},100);

window.toggleSidebar=function(){
var sb=document.getElementById("sidebar"),ov=document.getElementById("overlay");
if(sb)sb.classList.toggle("open");
if(ov)ov.classList.toggle("open");
};

console.log("V5.1 ready - Chinese OK");
loadData();
})();