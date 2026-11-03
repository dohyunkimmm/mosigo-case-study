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
  {key:"growth",label:"개선 가정",users:20000,freq:2,price:45000,cost:30000,rate:20}
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
 const cap=Math.max(1,...list.map(annualContribution));
 region.replaceChildren();
 for(const entry of list){
   const contribution=annualContribution(entry);
   const col=document.createElement("div");
   col.className="v3-bar-col"+(entry.key==="custom"?" is-live":"");
   const value=document.createElement("b");value.textContent=formatHundredMillion(contribution);
   const bar=document.createElement("span");bar.className="v3-bar";
   bar.style.height=(Math.max(6,Math.abs(contribution)/Math.max(1,Math.abs(cap))*128))+"px";
   if(contribution<0)bar.style.background="#b87850";
   const label=document.createElement("small");label.textContent=entry.label;
   col.append(value,bar,label);region.append(col);
 }
 region.setAttribute("aria-label","연간 고정비 차감 전 공헌이익 비교: "+list.map(x=>x.label+" "+formatHundredMillion(annualContribution(x))).join(", "));
 for(const button of document.querySelectorAll("[data-v3-scenario]")){
   const p=presets.find(x=>x.key===button.dataset.v3Scenario);
   button.setAttribute("aria-pressed",String(!!p && values.every(id=>p[id]===current[id])));
 }
 const subtitle=$("#v3-scenario-live");
 if(subtitle)subtitle.textContent="내 입력: 연간 "+new Intl.NumberFormat("ko-KR").format(current.users*current.freq)+"건 가정 · 고정비 차감 전 "+formatHundredMillion(annualContribution(current));
}
async function copyUrl(button,source){
 const text=location.href;
 try{
   if(navigator.clipboard?.writeText)await navigator.clipboard.writeText(text);
   else if(navigator.share){await navigator.share({title:document.title,url:text});return;}
   else {button.textContent="주소창의 링크를 복사해 주세요";return;}
   button.textContent="링크 복사 완료";
   const message=$("#v3-scenario-copy-status");if(message)message.textContent="현재 가정이 포함된 링크를 복사했습니다.";
 }catch(err){
   if(err?.name==="AbortError")return;
   button.textContent="복사 불가 · 주소창에서 복사";
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
function setupDocuments(){
 const image=$("#doc-page-img"),container=$("#v3-doc-thumbs");
 if(!image||!container)return;
 const details={plan:{prefix:"plan",total:17,label:"사업기획서"},presentation:{prefix:"slides",total:11,label:"발표자료"},ir:{prefix:"ir",total:12,label:"IR Deck"}};
 const tabs=[...document.querySelectorAll("[data-doc-preview]")];
 const currentDoc=()=>tabs.find(x=>x.getAttribute("aria-pressed")==="true")?.dataset.docPreview||"plan";
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
   container.replaceChildren();
   const start=Math.max(1,Math.min(page-2,doc.total-4));
   for(let n=start;n<=Math.min(doc.total,start+4);n++){
      const button=document.createElement("button");button.type="button";
      button.setAttribute("aria-label",doc.label+" "+n+(key==="plan"?"쪽으로":"장으로")+" 이동");
      if(n===page)button.setAttribute("aria-current","page");
      const thumb=document.createElement("img");
      thumb.src="/downloads/previews/"+doc.prefix+"-"+String(n).padStart(2,"0")+"-sm.webp";
      thumb.alt="";thumb.loading="lazy";thumb.decoding="async";thumb.width=76;thumb.height=43;
      const label=document.createElement("span");label.textContent=n+(key==="plan"?"쪽":"장");
      button.append(thumb,label);
      button.addEventListener("click",()=>window.MOSIGO_DOC?.setPage(n));
      container.append(button);
   }
   const fullImage=$("#v3-fullscreen-img");
   if(fullImage) {
      fullImage.src="/downloads/previews/"+doc.prefix+"-"+String(page).padStart(2,"0")+".webp";
      fullImage.alt=doc.label+" "+page+(key==="plan"?"쪽":"장")+" 전체화면 미리보기";
   }
   const count=$("#v3-thumb-count");if(count)count.textContent=doc.label+" "+page+" / "+doc.total;
 }
 const observer=new MutationObserver(refresh);
 observer.observe(image,{attributes:true,attributeFilter:["src"]});
 for(const tab of tabs)tab.addEventListener("click",()=>requestAnimationFrame(refresh));
 const open=$("#v3-view-full"),dialog=$("#v3-fullscreen"),close=$("#v3-full-close");
 if(open&&dialog&&close){
   open.addEventListener("click",()=>{
     refresh();
     if(typeof dialog.showModal==="function")dialog.showModal();
     else window.open($("#doc-page-open").href,"_blank","noopener");
   });
   close.addEventListener("click",()=>dialog.close());
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
 refresh();
}
setupScenario();
setupDocuments();
})();
