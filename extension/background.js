function avito(h){return h==="avito.ru"||h.endsWith(".avito.ru");}
chrome.runtime.onMessage.addListener((m,sender,reply)=>{
 if(m?.type!=="AVITO_PROCESS_MEDIA")return;
 (async()=>{try{
 const page=new URL(sender.url||sender.tab?.url||"");if(page.protocol!=="https:"||!avito(page.hostname))throw Error("Команда должна поступать со страницы Avito.");
 const sources=(m.sources||[]).slice(0,40).filter(x=>{try{const u=new URL(x.url);return u.protocol==="https:"&&!u.username&&!u.password;}catch{return false;}});
 const r=await fetch("http://127.0.0.1:8765/process",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sources,title:m.title||"Avito video",referer:page.href})}).catch(()=>{throw Error("Локальный FFmpeg-помощник не запущен. Запустите helper\\start_windows.bat.");});
 const d=await r.json().catch(()=>({}));if(!r.ok||!d.ok)throw Error(d.error||"Ошибка FFmpeg-помощника.");reply({ok:true,filename:d.filename});
 }catch(e){reply({ok:false,error:e.message});}})();return true;
});