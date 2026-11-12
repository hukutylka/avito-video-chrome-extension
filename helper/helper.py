import json,re,shutil,subprocess,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
OUT=Path(__file__).resolve().parent/"downloads";OUT.mkdir(exist_ok=True)
def safe(s):
 s=re.sub(r'[\x00-\x1f<>:"/\\|?*]',"_",str(s or "Avito-video"));return re.sub(r"\s+"," ",s).strip(" ._")[:120] or "Avito-video"
def valid(s):
 try:
  p=urlparse(s);return p.scheme=="https" and bool(p.hostname) and not p.username and not p.password
 except:return False
def streams(ffprobe,f):
 p=subprocess.run([ffprobe,"-v","error","-show_entries","stream=codec_type","-of","json",str(f)],capture_output=True,text=True,timeout=45)
 return {x.get("codec_type") for x in json.loads(p.stdout or "{}").get("streams",[])} if p.returncode==0 else set()
def process(src,title,referer):
 ff,probe=shutil.which("ffmpeg"),shutil.which("ffprobe")
 if not ff or not probe:raise RuntimeError("FFmpeg/FFprobe не найдены в PATH. Установите FFmpeg и добавьте bin в PATH.")
 urls=[]
 for x in src:
  u=x.get("url","") if isinstance(x,dict) else ""
  if valid(u) and u not in urls:urls.append(u)
 urls.sort(key=lambda u:0 if ".m3u8" in u.lower() else 1 if ".mpd" in u.lower() else 2)
 out=OUT/f"{safe(title)} [{time.strftime('%Y%m%d-%H%M%S')}].mp4";errs=[]
 for u in urls:
  cmd=[ff,"-y","-hide_banner","-loglevel","error","-user_agent","Mozilla/5.0","-headers",f"Referer: {referer}\r\n","-i",u,"-t","900","-map","0:v:0","-map","0:a?","-c","copy","-movflags","+faststart",str(out)]
  try:
   subprocess.run(cmd,check=True,timeout=240)
   st=streams(probe,out)
   if out.exists() and out.stat().st_size and {"video","audio"}.issubset(st):return out
   out.unlink(missing_ok=True)
   if "video" in st and "audio" not in st:errs.append("Источник содержит видео, но не содержит аудиодорожку.")
  except Exception as e:errs.append(str(e)[:200]);out.unlink(missing_ok=True)
 raise RuntimeError("Не найден доступный источник с видео и звуком. Если Avito отдаёт только беззвучный MP4, blob или защищённый поток, FFmpeg не сможет восстановить отсутствующую дорожку. "+" ".join(errs[-3:]))
class H(BaseHTTPRequestHandler):
 def send(self,c,d):
  b=json.dumps(d,ensure_ascii=False).encode();self.send_response(c);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Access-Control-Allow-Methods","POST, OPTIONS");self.send_header("Access-Control-Allow-Headers","Content-Type");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def do_OPTIONS(self):self.send(204,{})
 def do_POST(self):
  if self.path!="/process":return self.send(404,{"ok":False,"error":"Not found"})
  try:
   n=int(self.headers.get("Content-Length","0"))
   if not 1<=n<=100000:return self.send(400,{"ok":False,"error":"Некорректный запрос"})
   d=json.loads(self.rfile.read(n));ref=d.get("referer","");h=urlparse(ref).hostname or ""
   if urlparse(ref).scheme!="https" or not(h=="avito.ru" or h.endswith(".avito.ru")):return self.send(400,{"ok":False,"error":"Запрос не со страницы Avito"})
   f=process(d.get("sources",[])[:40],d.get("title"),ref);self.send(200,{"ok":True,"filename":f.name})
  except Exception as e:self.send(422,{"ok":False,"error":str(e)[:1400]})
 def log_message(self,*a):print("[FFmpeg helper]",*a)
if __name__=="__main__":
 print("Avito FFmpeg helper: http://127.0.0.1:8765 — оставьте окно открытым.")
 ThreadingHTTPServer(("127.0.0.1",8765),H).serve_forever()
