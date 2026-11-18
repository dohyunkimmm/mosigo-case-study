/* MOSIGO v3: progressive enhancement; baseline report, PDFs and calculations remain intact. */
(() => {
"use strict";
document.documentElement.classList.add("v3-active");
const $ = selector => document.querySelector(selector);
const money = value => new Intl.NumberFormat("ko-KR").format(Math.round(value)) + "원";
const values = ["users","freq","price","cost","rate"];
const base = {users:15000,freq:1.5,price:40000,cost:30000,rate:20};
const presets = [
  {key:"conservative",label:"보수",users:8000,freq:1,price:35000,cost:30000,rate:20},
  {key:"base",label:"기준",...base},
  {key:"growth",label:"개선 시나리오",users:20000,freq:2,price:45000,cost:30000,rate:20}
];
const state = () => Object.fromEntries(values.map(id=>[id,Number(document.getElementById(id).value)]));
const annualContribution = p => p.users*p.freq*(p.price-p.cost);
const formatHundredMillion = value => (value/100000000).toFixed(2)+"억 원";
const permitted = new Set(values);
function restoreFromUrl(){
 const params = new URLSearchParams(location.search);
 let restored=false;
 for (const id of permitted) {
   const field=document.getElementById(id), raw=params.get("v_"+id);
   if (!field || raw === null || raw.trim()==="") continue;
   const number=Number(raw);
   if(!Number.isFinite(number))continue;
   const min=Number(field.min),max=Number(field.max),step=Number(field.step)||1;
   if(number<min||number>max||Math.abs((number-min)/step-Math.round((number-min)/step))>1e-6)continue;
   field.value=String(number);
   restored=true;
 }
 if(restored)document.getElementById("users").dispatchEvent(new Event("input",{bubbles:true}));
}
function setScenarioParams(url){
 const current=state();
 for(const id of values){
   if(current[id]===base[id])url.searchParams.delete("v_"+id);
   else url.searchParams.set("v_"+id,String(current[id]));
 }
}
function updateLink(){
 const url=new URL(location.href);
 setScenarioParams(url);
 history.replaceState(history.state,"",url.pathname+url.search+url.hash);
}
function renderScenario(){
 const region=$("#v3-scenario-graph"); if(!region)return;
 $("#v3-scenario-copy-status").replaceChildren();
 const current=state(),list=[...presets,{key:"custom",label:"내 입력",...current}];
 const cap=Math.max(1,...list.map(entry => Math.abs(annualContribution(entry))));
 region.replaceChildren();
 for(const entry of list){
   const contribution=annualContribution(entry);
   const col=document.createElement("div");
   col.className="v3-bar-col"+(entry.key==="custom"?" is-live":"");
   const value=document.createElement("b");value.textContent=formatHundredMillion(contribution);
   const plot=document.createElement("div");
   plot.className="review-bar-plot";
   const bar=document.createElement("span");
   bar.className="review-signed-bar"+(contribution<0?" is-negative":"");
   bar.style.width=50*Math.abs(contribution)/cap+"%";
   const label=document.createElement("small");label.textContent=entry.label;
   plot.append(bar);
   col.append(label,plot,value);
   region.append(col);
 }
 region.setAttribute("aria-label","연간 고정비 차감 전 공헌이익 비교: "+list.map(x=>x.label+" "+formatHundredMillion(annualContribution(x))).join(", "));
 for(const button of document.querySelectorAll("[data-v3-scenario]")){
   const p=presets.find(x=>x.key===button.dataset.v3Scenario);
   button.setAttribute("aria-pressed",String(!!p && values.every(id=>p[id]===current[id])));
 }
 const subtitle=$("#v3-scenario-live");
 if(subtitle)subtitle.textContent="내 입력: 연간 "+new Intl.NumberFormat("ko-KR").format(current.users*current.freq)+"건 예상 · 고정비 차감 전 "+formatHundredMillion(annualContribution(current));
}
async function copyLink(url, label, feedback){
 feedback.replaceChildren();
 try{
   if(navigator.clipboard?.writeText){
     await navigator.clipboard.writeText(url.href);
     feedback.textContent=label+" 링크를 복사했습니다.";
     return;
   }
   if(navigator.share){
     await navigator.share({title:label,url:url.href});
     return;
   }
 }catch(error){
   if(error.name==="AbortError")return;
 }
 const field=document.createElement("input");
 field.type="url";
 field.readOnly=true;
 field.value=url.href;
 field.setAttribute("aria-label",label+" 공유 주소");
 feedback.replaceChildren("아래 주소를 복사하세요.",field);
 field.focus();
 field.select();
}
function setupScenario(){
 const graph=$("#v3-scenario-graph");if(!graph)return;
 restoreFromUrl();
 for (const id of values){
   const control=document.getElementById(id);
   control.addEventListener("input",()=>{renderScenario();updateLink();});
 }
 document.getElementById("reset").addEventListener("click",()=>{renderScenario();updateLink();});
 document.querySelectorAll("[data-v3-scenario]").forEach(button=>button.addEventListener("click",()=>{
   const p=presets.find(x=>x.key===button.dataset.v3Scenario);if(!p)return;
   for(const id of values)document.getElementById(id).value=String(p[id]);
   document.getElementById("users").dispatchEvent(new Event("input",{bubbles:true}));
 }));
 const share=$("#v3-share-scenario");
 if(share)share.addEventListener("click",()=>{
   const url=new URL(location.pathname,location.origin);
   setScenarioParams(url);
   url.hash="annual-model";
   copyLink(url,"연간 시나리오",$("#v3-scenario-copy-status"));
 });
 renderScenario();
}
function setupPartnerModel() {
 const inputs = $("#partner-inputs"), results = $("#partner-results");
 if (!inputs || !results) return;
 const fields = [
   ["매니저 수", 20, 10000], ["주 가용 시간", 20, 168], ["건당 투입 시간", 4, 168, 0.1, 0.1],
   ["가동률 (%)", 65, 100], ["플랫폼 이용 비율 (%)", 80, 100],
   ["취소율 (%)", 10, 100], ["취소 제외 예약의 완료율 (%)", 98, 100],
   ["평균 결제액 (원)", 40000, 10000000], ["제휴 수수료율 (%)", 20, 100],
   ["결제 수수료율 (%)", 3, 100, 0, 0.1], ["건당 고객 지원비 (원)", 1200, 10000000],
   ["건당 시스템 비용 (원)", 100, 10000000], ["신규 고객 비중 (%)", 60, 100],
   ["신규 고객 획득비 (원)", 3000, 10000000], ["월 현금 고정비 (원)", 2000000, 1000000000],
   ["월 인력 기회비용 (원)", 2000000, 1000000000]
 ];
 const coreInputs = $("#partner-core-inputs"), costInputs = $("#partner-cost-inputs");
 const costDetails = $("#partner-costs"), gap = $("#partner-gap");
 const baseline = window.MOSIGO_PARTNER_BASELINE ?? fields.map(field => field[1]);
 const controls = fields.map(([name, , max, min=0, step=1], index) => {
   const label = document.createElement("label"), input = document.createElement("input");
   label.textContent = name;
   Object.assign(input, {type:"number", min, max, step, value:baseline[index], required:true});
   input.id = `partner-field-${index}`;
   input.setAttribute("aria-label", name);
   const hint = document.createElement("small");
   hint.id = `${input.id}-hint`;
   hint.textContent = `${name}: ${min.toLocaleString("ko-KR")}~${max.toLocaleString("ko-KR")} 범위에서 ${step} 단위로 입력하세요.`;
   hint.hidden = true;
   input.setAttribute("aria-describedby", hint.id);
   label.append(input, hint);
   const group = index < 9 ? coreInputs : costInputs;
   group.append(label);
   return input;
 });
 function render() {
   for (const input of controls) {
     const invalid = !input.validity.valid;
     input.setAttribute("aria-invalid", String(invalid));
     document.getElementById(`${input.id}-hint`).hidden = !invalid;
   }
   if (controls.some(input => !input.validity.valid)) {
     gap.hidden = true;
     results.textContent = "각 입력란에 표시된 범위와 단위를 확인해 주세요.";
     return;
   }
   const [staff,hours,time,utilization,platform,cancel,completion,price,rate,fee,support,system,newShare,cac,fixed,labor] = controls.map(input => input.valueAsNumber);
   const capacity = staff*hours*4.33/time;
   const maxOrders = Math.floor(capacity);
   const expected = capacity*utilization/100*platform/100*(1-cancel/100)*completion/100;
   const orders = Math.min(maxOrders, Math.round(expected));
   // Keep thousandths of a won until display. Fee rates accept 0.1 percentage points.
   const marginMilliwon = price * (rate * 10 - Math.round(fee * 10))
     - (support + system) * 1000 - newShare * cac * 10;
   const margin = marginMilliwon / 1000;
   const breakeven = cost => marginMilliwon > 0 ? Math.ceil(cost * 1000 / marginMilliwon) : null;
   const formatOrders = count => count.toLocaleString("ko-KR")+"건";
   const formatTarget = count => count === null ? "건당 공헌이익 개선 후 산정" : formatOrders(count);
   const cashTarget = breakeven(fixed);
   const track = gap.querySelector(".partner-gap-track");
   gap.hidden = false;
   track.hidden = cashTarget === null || cashTarget === 0;
   let headline = "건당 공헌이익 개선 필요";
   let detail = "건당 공헌이익이 0원 이하여서 손익분기 건수를 산정할 수 없습니다.";
   if (cashTarget !== null) {
     const difference = orders - cashTarget;
     headline = difference === 0 ? "손익분기 도달" : formatOrders(Math.abs(difference)) + (difference < 0 ? " 부족" : " 초과");
     detail = "월 예상 완료 " + formatOrders(orders) + " / 현금 손익분기 " + formatOrders(cashTarget);
     if (cashTarget > 0) track.firstElementChild.style.width = Math.min(100, orders / cashTarget * 100) + "%";
   }
   $("#partner-gap-value").textContent = headline;
   $("#partner-gap-detail").textContent = detail;
   const rows = [
     ["월 이론상 최대 처리", maxOrders.toLocaleString("ko-KR")+"건"],
     ["월 예상 완료", orders.toLocaleString("ko-KR")+"건"],
     ["건당 공헌이익", money(margin)], ["월 수수료 매출", money(orders*price*rate/100)],
     ["월 현금 손익", money(orders*margin-fixed)], ["월 인력 비용 포함 손익", money(orders*margin-fixed-labor)],
     ["현금 손익분기", formatTarget(cashTarget)], ["인력 비용 포함 손익분기", formatTarget(breakeven(fixed+labor))]
   ];
   results.replaceChildren(...rows.map(([name,value]) => {
     const row=document.createElement("div"), title=document.createElement("dt"), data=document.createElement("dd");
     title.textContent=name;
     data.textContent=value;
     row.append(title,data);
     return row;
   }));
 }
 costDetails.hidden = false;
 inputs.addEventListener("input",render);
 $("#partner-reset").addEventListener("click",() => {
   controls.forEach((input,i) => { input.value=baseline[i]; });
   render();
 });
 render();
}

function setupDocuments(){
 const image=$("#doc-page-img");
 if(!image)return;
 const tabs=[...document.querySelectorAll("[data-doc-preview]")];

 const sharePage=$("#doc-copy-page");
 sharePage.hidden=false;
 sharePage.addEventListener("click",()=>{
   const selected=window.MOSIGO_DOC.get();
   const url=new URL(location.pathname,location.origin);
   url.searchParams.set("document",selected.document);
   url.searchParams.set("page",selected.page);
   url.hash="attachments";
   const label=tabs.find(tab=>tab.dataset.docPreview===selected.document).textContent.trim();
   copyLink(url,label+" "+selected.page+"쪽",$("#doc-copy-status"));
 });
 const previewError=$("#doc-preview-error");
 const imageStatus=()=>{ previewError.hidden = !image.complete || image.naturalWidth > 0; };
 image.addEventListener("load", imageStatus);
 image.addEventListener("error", imageStatus);
 $("#doc-preview-retry").addEventListener("click", () => {
   const url=new URL(image.currentSrc || image.src,location.href);
   url.searchParams.set("retry",Date.now());
   image.srcset=url.href+" 800w, "+url.href+" 1400w";
   previewError.hidden=true;
 });
 imageStatus();
 const previewLink=$("#doc-page-open");
 let touchStart=null;
 previewLink.addEventListener("touchstart",event=>{
   touchStart=event.touches.length===1 ? event.touches[0] : null;
 },{passive:true});
 previewLink.addEventListener("touchcancel",()=>{touchStart=null;},{passive:true});
 previewLink.addEventListener("touchend",event=>{
   const start=touchStart;
   touchStart=null;
   if(!start || event.changedTouches.length!==1 || event.touches.length)return;
   const end=event.changedTouches[0];
   const dx=end.clientX-start.clientX,dy=end.clientY-start.clientY;
   if(Math.abs(dx)<55 || Math.abs(dx)<Math.abs(dy)*1.45)return;
   event.preventDefault();
   $(dx<0?"#doc-next":"#doc-prev").click();
 },{passive:false});
 previewLink.addEventListener("keydown",event=>{
   if(event.altKey || event.ctrlKey || event.metaKey || event.shiftKey)return;
   if(event.key!=="ArrowLeft" && event.key!=="ArrowRight")return;
   event.preventDefault();
   $(event.key==="ArrowRight"?"#doc-next":"#doc-prev").click();
 });
 const params=new URLSearchParams(location.search);
 const requestedDoc=params.get("document"), requestedPage=Number(params.get("page"));
 const requestedTab=tabs.find(tab=>tab.dataset.docPreview===requestedDoc);
 if(requestedTab){
   requestedTab.click();
   if(Number.isInteger(requestedPage) && requestedPage>0) window.MOSIGO_DOC.setPage(requestedPage);
 }

}
setupScenario();
setupDocuments();
setupPartnerModel();
function openLinkedCalculator(){
 const hash=location.hash;
 if(hash==="#annual-model" || hash==="#partner-model"){
   const model=$(hash);
   model.closest("details").open=true;
   model.scrollIntoView({behavior:"instant",block:"start"});
 }
}
openLinkedCalculator();
window.addEventListener("hashchange",openLinkedCalculator);
document.querySelectorAll('a[href="#partner-model"]').forEach(link => link.addEventListener("click", () => {
 $("#partner-model").closest("details").open=true;
}));
})();
