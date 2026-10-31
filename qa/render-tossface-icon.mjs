import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir, stat } from 'node:fs/promises';

const browser=await chromium.launch({headless:true});
try {
 const page=await browser.newPage({viewport:{width:240,height:240},deviceScaleFactor:2});
 await page.goto('https://mosigo-case-study.vercel.app/',{waitUntil:'load',timeout:45000});
 await page.evaluate(async()=>{
  document.body.innerHTML='<span id="tossface-graphic" aria-label="휴대전화 아이콘">📱</span>';
  document.documentElement.style.cssText='background:transparent!important;margin:0!important;padding:0!important';
  document.body.style.cssText='background:transparent!important;margin:0!important;padding:0!important';
  const el=document.getElementById('tossface-graphic');
  el.style.cssText='font-family:Tossface!important;font-size:96px!important;font-weight:400!important;line-height:1!important;position:absolute;left:8px;top:4px;white-space:nowrap';
  const loaded=await document.fonts.load('96px Tossface','📱');
  if(!loaded.length || !loaded.some(f=>f.status==='loaded'))throw new Error('Original Tossface glyph not loaded');
  await document.fonts.ready;
 });
 await mkdir('assets',{recursive:true});
 const glyph=page.locator('#tossface-graphic');
 const box=await glyph.boundingBox();
 assert.ok(box && box.width>50 && box.height>70);
 await page.screenshot({path:'assets/tossface-phone.png',type:'png',omitBackground:true,clip:{x:0,y:0,width:Math.min(150,Math.ceil(box.width+18)),height:Math.min(150,Math.ceil(box.height+8))}});
 const size=(await stat('assets/tossface-phone.png')).size;
 assert.ok(size>1000&&size<40000,'Tossface static icon size '+size);
 console.log('PASS official Tossface mobile phone icon rendered:',size,'bytes',box);
} finally {await browser.close();}
