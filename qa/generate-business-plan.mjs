import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const source = path.resolve('downloads/mosigo_business_plan_20261031.html');
const output = path.resolve('downloads/mosigo_business_plan_20261031.pdf');
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});
 await page.goto('file://'+source,{waitUntil:'load'});
 await page.evaluate(()=>document.fonts.ready);
 const check=await page.evaluate(()=>{
   const slides=[...document.querySelectorAll('section')];
   const issues=[];
   slides.forEach((s,i)=>{
      const footer=s.querySelector('.footer');
      const body=s.querySelector('.body');
      if(!footer||!body){issues.push('missing body or footer at '+i);return;}
      const br=body.getBoundingClientRect(),fr=footer.getBoundingClientRect();
      if(br.bottom>fr.top-8)issues.push('body runs into footer at page '+(i+1)+': '+Math.round(br.bottom-fr.top));
      for(const el of body.querySelectorAll('*')){
       const r=el.getBoundingClientRect();
       if(r.right>s.getBoundingClientRect().right+1)issues.push('horizontal overflow page '+(i+1)+' '+el.tagName);
      }
   });
   return {pages:slides.length,issues:issues.slice(0,30)};
 });
 console.log('Layout QA:',JSON.stringify(check));
 if(check.pages!==17||check.issues.length)throw new Error('Layout QA failure');
 await page.pdf({path:output,printBackground:true,preferCSSPageSize:true,width:'1280px',height:'720px',margin:{top:'0',right:'0',bottom:'0',left:'0'}});
 if(fs.statSync(output).size<25000)throw new Error('PDF unexpectedly small');
 console.log('Generated new PDF:',fs.statSync(output).size,'bytes');
}finally{await browser.close();}
