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
function updateLink(){
 const url=new URL(location.href), current=state();
 for(const id of values){
   if(current[id]===base[id])url.searchParams.delete("v_"+id);
   else url.searchParams.set("v_"+id,String(current[id]));
 }
 history.replaceState(history.state,"",url.pathname+url.search+url.hash);
}
function renderScenario(){
 const region=$("#v3-scenario-graph"); if(!region)return;
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
async function copyUrl(button,source){
 const text=location.href;
 try{
   if(navigator.clipboard?.writeText)await navigator.clipboard.writeText(text);
   else if(navigator.share){await navigator.share({title:document.title,url:text});return;}
   else {button.textContent="주소창의 링크를 복사해 주세요";return;}
   button.textContent="링크 복사 완료";
   const message=$("#v3-scenario-copy-status");if(message)message.textContent="현재 입력 조건이 포함된 링크를 복사했습니다.";
 }catch(err){
   if(err?.name==="AbortError")return;
   button.textContent="주소창에서 링크 복사";
 }
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
 if(share)share.addEventListener("click",()=>copyUrl(share,"scenario"));
 renderScenario();
}
function setupPartnerModel() {
 const inputs = $("#partner-inputs"), results = $("#partner-results");
 if (!inputs || !results) return;
 const fields = [
   ["매니저 수", 20, 10000], ["주 가용 시간", 20, 168], ["건당 투입 시간", 4, 168, 0.1, 0.1],
   ["가동률 (%)", 65, 100], ["플랫폼 이용 비율 (%)", 80, 100],
   ["취소율 (%)", 10, 100], ["완료율 (%)", 98, 100],
   ["평균 결제액 (원)", 40000, 10000000], ["제휴 수수료율 (%)", 20, 100],
   ["결제 수수료율 (%)", 3, 100, 0, 0.1], ["건당 고객 지원비 (원)", 1200, 10000000],
   ["건당 시스템 비용 (원)", 100, 10000000], ["신규 고객 비중 (%)", 60, 100],
   ["신규 고객 획득비 (원)", 3000, 10000000], ["월 현금 고정비 (원)", 2000000, 1000000000],
   ["월 인력 기회비용 (원)", 2000000, 1000000000]
 ];
 const baseline = window.MOSIGO_PARTNER_BASELINE ?? fields.map(field => field[1]);
 const controls = fields.map(([name, , max, min=0, step=1], index) => {
   const label = document.createElement("label"), input = document.createElement("input");
   label.textContent = name;
   Object.assign(input, {type:"number", min, max, step, value:baseline[index], required:true});
   label.append(input);
   inputs.append(label);
   return input;
 });
 function render() {
   if (controls.some(input => !input.validity.valid)) {
     results.textContent = "각 입력란에 표시된 범위와 단위를 확인해 주세요.";
     return;
   }
   const [staff,hours,time,utilization,platform,cancel,completion,price,rate,fee,support,system,newShare,cac,fixed,labor] = controls.map(input => input.valueAsNumber);
   const capacity = staff*hours*4.33/time;
   const orders = Math.round(capacity*utilization/100*platform/100*(1-cancel/100)*completion/100);
   const margin = Math.round(price*(rate-fee)/100-support-system-newShare*cac/100);
   const breakeven = cost => margin > 0 ? Math.ceil(cost/margin).toLocaleString("ko-KR")+"건" : "건당 공헌이익 개선 후 산정";
   const rows = [
     ["월 이론상 최대 처리", Math.floor(capacity).toLocaleString("ko-KR")+"건"],
     ["월 예상 완료", orders.toLocaleString("ko-KR")+"건"],
     ["건당 공헌이익", money(margin)], ["월 수수료 매출", money(orders*price*rate/100)],
     ["월 현금 손익", money(orders*margin-fixed)], ["월 인력 비용 포함 손익", money(orders*margin-fixed-labor)],
     ["현금 손익분기", breakeven(fixed)], ["인력 비용 포함 손익분기", breakeven(fixed+labor)]
   ];
   results.replaceChildren(...rows.map(([name,value]) => {
     const row=document.createElement("div"), title=document.createElement("dt"), data=document.createElement("dd");
     title.textContent=name;
     data.textContent=value;
     row.append(title,data);
     return row;
   }));
 }
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
 const details={plan:{prefix:"plan",total:17,label:"사업기획서"},presentation:{prefix:"slides",total:11,label:"발표자료"},ir:{prefix:"ir",total:12,label:"IR Deck"}};
 const tabs=[...document.querySelectorAll("[data-doc-preview]")];
 const currentDoc=()=>tabs.find(x=>x.getAttribute("aria-pressed")==="true")?.dataset.docPreview||"plan";
 const fullPrev=$("#v3-full-prev"), fullNext=$("#v3-full-next");
 const previewError=$("#doc-preview-error");
 const zoom=$("#v3-doc-zoom"), zoomViewport=zoom.parentElement;
 function resetZoom(){
   zoom.setAttribute("aria-pressed","false");
   zoomViewport.scrollTo(0,0);
 }
 zoom.addEventListener("click",()=>{
   if(zoom.getAttribute("aria-pressed")==="true"){resetZoom();return;}
   zoom.setAttribute("aria-pressed","true");
   zoomViewport.scrollLeft=(zoomViewport.scrollWidth-zoomViewport.clientWidth)/2;
 });
 const imageStatus=()=>{ previewError.hidden = !image.complete || image.naturalWidth > 0; };
 image.addEventListener("load", imageStatus);
 image.addEventListener("error", imageStatus);
 $("#doc-preview-retry").addEventListener("click", () => {
   const url=new URL(image.currentSrc || image.src,location.href);
   url.searchParams.set("retry",Date.now());
   image.srcset=url.href+" 800w, "+url.href+" 1400w";
   previewError.hidden=true;
 });
 fullPrev.addEventListener("click",()=>window.MOSIGO_DOC.setPage(currentPage()-1));
 fullNext.addEventListener("click",()=>window.MOSIGO_DOC.setPage(currentPage()+1));

 let cached="";
 const currentPage=()=>{
  const found=(image.getAttribute("src")||"").match(/-(\d{2})-sm\.webp/);
  return found?Number(found[1]):1;
 };
 function refresh(){
   const key=currentDoc(),doc=details[key],page=currentPage();
   if(!doc)return;
   const next=key+":"+page;
   if(cached===next)return;
   cached=next;
   imageStatus();
   fullPrev.disabled=page===1;
   fullNext.disabled=page===doc.total;
   $("#v3-full-count").textContent=page+" / "+doc.total;
   const fullImage=$("#v3-fullscreen-img");
   if(fullImage && $("#v3-fullscreen").open) {
      resetZoom();
      fullImage.src="/downloads/previews/"+doc.prefix+"-"+String(page).padStart(2,"0")+".webp";
      fullImage.alt=doc.label+" "+page+(key==="plan"?"쪽":"장")+" 전체화면 미리보기";
   }
   const count=$("#v3-thumb-count");if(count)count.textContent=doc.label+" "+page+" / "+doc.total;
 }
 const observer=new MutationObserver(refresh);
 observer.observe(image,{attributes:true,attributeFilter:["src"]});
 for(const tab of tabs)tab.addEventListener("click",()=>requestAnimationFrame(refresh));
 const open=$("#doc-page-open"),dialog=$("#v3-fullscreen"),close=$("#v3-full-close");
 if(open&&dialog&&close){
   open.addEventListener("click",event=>{
     event.preventDefault();
     if(typeof dialog.showModal==="function"){
       dialog.showModal();
       cached="";
       refresh();
     }
     else window.open($("#doc-page-open").href,"_blank","noopener");
   });
   close.addEventListener("click",()=>dialog.close());
   dialog.addEventListener("close",()=>{resetZoom();open.focus();});
   dialog.addEventListener("keydown",event=>{
     if((event.key==="ArrowLeft" || event.key==="ArrowRight") && zoom.getAttribute("aria-pressed")!=="true"){
       event.preventDefault();
       window.MOSIGO_DOC.setPage(currentPage()+(event.key==="ArrowRight"?1:-1));
     }
   });
   dialog.addEventListener("click",event=>{if(event.target===dialog)dialog.close();});
 }
 const swipeTarget=$("#mobile-doc-viewer");
 let startX=0,startY=0;
 swipeTarget?.addEventListener("touchstart",event=>{
   if(event.touches.length!==1)return;
   startX=event.touches[0].clientX;startY=event.touches[0].clientY;
 },{passive:true});
 swipeTarget?.addEventListener("touchend",event=>{
   if(event.changedTouches.length!==1)return;
   const dx=event.changedTouches[0].clientX-startX,dy=event.changedTouches[0].clientY-startY;
   if(Math.abs(dx)<55||Math.abs(dx)<Math.abs(dy)*1.45)return;
   const button=$(dx<0?"#doc-next":"#doc-prev");
   if(button&&!button.disabled)button.click();
 },{passive:true});
 swipeTarget?.addEventListener("keydown",event=>{
   if(event.key!=="ArrowLeft"&&event.key!=="ArrowRight")return;
   if(event.target.closest("button,a"))return;
   const button=$(event.key==="ArrowRight"?"#doc-next":"#doc-prev");
   if(button&&!button.disabled){event.preventDefault();button.click();}
 });
 const params=new URLSearchParams(location.search);
 const requestedDoc=params.get("document"), requestedPage=Number(params.get("page"));
 if(Object.hasOwn(details,requestedDoc)){
   tabs.find(tab=>tab.dataset.docPreview===requestedDoc)?.click();
   if(Number.isInteger(requestedPage) && requestedPage>0) window.MOSIGO_DOC.setPage(requestedPage);
 }
 refresh();
}
setupScenario();
setupPartnerModel();
setupDocuments();
if(location.hash==="#partner-model") $("#partner-model").closest("details").open=true;
document.querySelectorAll('a[href="#partner-model"]').forEach(link => link.addEventListener("click", () => {
 $("#partner-model").closest("details").open=true;
}));
})();
