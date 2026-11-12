(() => {
if (window.__avitoVideoSaverLoaded) return;
window.__avitoVideoSaverLoaded = true;
const b=document.createElement("button"); b.id="avito-video-saver-button"; b.textContent="⬇ Скачать видео со звуком";
Object.assign(b.style,{position:"fixed",right:"22px",bottom:"22px",zIndex:"2147483647",padding:"13px 18px",border:"0",borderRadius:"12px",background:"#2563eb",color:"#fff",font:"600 14px Arial",boxShadow:"0 4px 18px #0003",cursor:"pointer"});
document.documentElement.appendChild(b);
function collect(){
 const a=[]; const add=(url,kind)=>{if(!url||typeof url!=="string"||url.startsWith("blob:"))return;try{const u=new URL(url,location.href);if(u.protocol==="https:"&&!a.some(x=>x.url===u.href))a.push({url:u.href,kind});}catch{}};
 document.querySelectorAll("video").forEach(v=>{add(v.currentSrc,"video");add(v.src,"video");v.querySelectorAll("source").forEach(s=>add(s.src,"source"));});
 ['meta[property="og:video"]','meta[property="og:video:url"]','meta[name="twitter:player:stream"]'].forEach(s=>{const n=document.querySelector(s);if(n)add(n.content,"meta");});
 performance.getEntriesByType("resource").forEach(e=>{const u=e.name||"";if(/\.(m3u8|mpd|mp4|m4v|webm)(?:[?#]|$)/i.test(u)||/(video|stream|media|playlist)/i.test(u))add(u,"network");});
 const title=(document.querySelector("h1")?.innerText||document.title||"Avito video").replace(/\s+/g," ").trim().slice(0,180);
 return {sources:a,title};
}
b.addEventListener("click",async()=>{const old=b.textContent;b.disabled=true;b.textContent="Ищу видео и аудио…";try{
 const {sources,title}=collect();if(!sources.length)throw Error("Медиассылки не найдены. Дождитесь загрузки объявления и запустите видео.");
 const r=await chrome.runtime.sendMessage({type:"AVITO_PROCESS_MEDIA",sources,title});
 if(!r?.ok)throw Error(r?.error||"Не удалось обработать видео.");alert("Готово! Файл сохранён:\n"+r.filename);
 }catch(e){alert(e.message);}finally{b.disabled=false;b.textContent=old;}});
})();