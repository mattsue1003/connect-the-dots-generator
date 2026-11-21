const { chromium } = require('playwright');
const path=require('path'), fs=require('fs');
(async()=>{
  const a2=process.argv[2]||''; let only=null, rng=null; if(a2.includes('-')) rng=a2.split('-').map(Number); else if(a2) only=a2.split(',').map(Number);
  const out=process.argv[3]||'frames'; fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({proxy:{server:process.env.HTTPS_PROXY}, args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const ctx=await browser.newContext({viewport:{width:1280,height:720},deviceScaleFactor:1.5,ignoreHTTPSErrors:true});
  const page=await ctx.newPage();
  page.on('console',m=>{ if(m.type()==='error'||m.type()==='warning') console.log('[page]',m.text().slice(0,200)); });
  page.on('pageerror',e=>console.log('[pageerror]',e.message));
  await page.goto('file://'+path.resolve('build/index.html')+'?render=1');
  await page.evaluate(()=>window.ready);
  const N=await page.evaluate(()=>window.NFRAMES);
  let list=only||[...Array(N).keys()]; if(rng) list=list.filter(f=>f>=rng[0]&&f<rng[1]);
  const t0=Date.now();
  for(const f of list){
    const fn=path.join(out,String(f).padStart(5,'0')+'.jpg');
    if(!only && fs.existsSync(fn)) continue;
    await page.evaluate(f=>window.renderFrame(f),f);
    await page.screenshot({path:fn,type:'jpeg',quality:93});
    if(f%60===0) console.log('frame',f,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s');
  }
  await browser.close();
})();
