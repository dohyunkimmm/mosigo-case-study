import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const source = path.resolve('downloads/mosigo_business_plan_20261031.html');
const output = path.resolve('downloads/mosigo_business_plan_20261031.pdf');
// A PDF rebuild must not create a new publication when only volatile PDF dates change.
// Compare raw bytes after replacing exactly the two timestamp fields; all content,
// fonts, graphics and page objects must remain byte-for-byte equal.
const previousPdf = fs.existsSync(output) ? fs.readFileSync(output) : null;
function normalizePdfDates(pdf) {
 const text = pdf.toString('latin1').replace(
  /(\/(?:CreationDate|ModDate)\s*\(D:)\d{14}([+-]\d{2}'\d{2}'\))/g,
  (_match, prefix, suffix) => prefix + '00000000000000' + suffix
 );
 return Buffer.from(text, 'latin1');
}
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN||undefined,args:['--no-sandbox']});
try{
 const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});
 await page.goto('file://'+source,{waitUntil:'load'});
 // Embed the official OTF files into the PDF even if the CDN is unreachable.
 const regular=fs.readFileSync('qa-fonts/Pretendard-Regular.otf').toString('base64');
 const bold=fs.readFileSync('qa-fonts/Pretendard-Bold.otf').toString('base64');
 await page.addStyleTag({content:`@font-face{font-family:"Pretendard PDF";src:url(data:font/otf;base64,${regular}) format("opentype");font-weight:400} @font-face{font-family:"Pretendard PDF";src:url(data:font/otf;base64,${bold}) format("opentype");font-weight:700} body{font-family:"Pretendard PDF",sans-serif!important}`});
 await page.evaluate(async()=>{await document.fonts.load('400 16px "Pretendard PDF"');await document.fonts.load('700 16px "Pretendard PDF"');await document.fonts.ready;});
 const fontCheck=await page.evaluate(()=>[...document.fonts].filter(f=>f.family==='Pretendard PDF' && f.status==='loaded').map(f=>f.weight));
 assert.ok(fontCheck.includes('400') && fontCheck.includes('700'), 'Pretendard PDF fonts must be loaded');
 console.log('Font QA:',fontCheck.join(','));
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
 if(check.pages!==19||check.issues.length)throw new Error('Layout QA failure');
 await page.pdf({path:output,printBackground:true,preferCSSPageSize:true,width:'1280px',height:'720px',margin:{top:'0',right:'0',bottom:'0',left:'0'}});
 if (previousPdf && normalizePdfDates(previousPdf).equals(normalizePdfDates(fs.readFileSync(output)))) {
  fs.writeFileSync(output, previousPdf);
  console.log('No visual or document-content changes; preserved original PDF and skipped metadata-only update.');
 }
 if(fs.statSync(output).size<25000)throw new Error('PDF unexpectedly small');
 console.log('Generated new PDF:',fs.statSync(output).size,'bytes');
}finally{await browser.close();}

// Rebuild marker: regenerate the current reviewed MOSIGO PDF deliverable.
