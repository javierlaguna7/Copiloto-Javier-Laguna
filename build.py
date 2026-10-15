import os, json, shutil, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
rd = lambda f: open(os.path.join(SRC, f), encoding='utf-8').read()

ORDER = ['lexicon.js','lexicon2.js'] + [f'db{i}.js' for i in range(1, 30)] + [f'addenda{i}.js' for i in range(1, 6)] + [f'extra{i}.js' for i in range(1, 11)] + [f'info{i}.js' for i in range(1, 16)] + ['engine.js','safety.js','labs.js','@registerLabImaging();','lexsyn.js','@addSyn(LEX_SYN);','lexsyn2.js','@addSyn(LEX_SYN2);','qafix.js'] + sorted([f for f in os.listdir(SRC) if f.startswith('qa') and f[2:-3].isdigit()], key=lambda f:int(f[2:-3])) + ['personalize.js','labref.js','syndromes.js','cantmiss.js','calc.js','gloss1.js','gloss2.js','gloss3.js','gloss4.js','glos1.js','glos2.js','glos3.js','glossary.js','app.js']
import hashlib, datetime, subprocess, sys
KBH = hashlib.sha256(''.join(rd(f) for f in ORDER if not f.startswith('@') and f!='app.js').encode()).hexdigest()[:10]
KB_META = "const KB_META={engine:'6.0',version:'%s',hash:'%s'};\n" % (datetime.date.today().strftime('%Y.%m.%d'), KBH)
js = KB_META + 'const DB_RAW=[];const ADDENDA_RAW=[];const EXTRA_RAW=[];const GLOSS_RAW=[];const GLOS_RAW=[];\n' + '\n'.join((f[1:] if f.startswith('@') else rd(f)) for f in ORDER)
TESTS=['spec/qa/test1.js','spec/qa/test2.js','spec/qa/test3.js','spec/qa/test4.js','spec/modulos/test_calc.js','spec/modulos/test_labs.js','spec/modulos/test_cm.js','spec/safety/test_safety.js']
if '--skip-tests' not in sys.argv:
    for t in TESTS:
        tp=os.path.join(ROOT,t)
        if not os.path.exists(tp): continue
        r=subprocess.run(['node',tp],capture_output=True,text=True)
        last=(r.stdout.strip().splitlines() or [''])[-1]
        bad = r.returncode!=0 or any(x in last for x in ['FALLA','FAIL','ERROR']) or ('top3' in last and '100.0%' not in last.split('top6')[0])
        print(('OK  ' if not bad else 'FALLA ')+t+' → '+last[:120])
        if bad: sys.exit('Compilación detenida: falló una prueba de regresión clínica ('+t+')')
shell = rd('shell.html')
body = shell + '\n<script>\n' + js + '\n</script>\n'

# 1) Página para Artifact (sin doctype; el host añade el esqueleto)
os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
open(os.path.join(ROOT, 'dist', 'copiloto-clinico.html'), 'w', encoding='utf-8').write(body)

# 2) Paquete PWA instalable (para PWABuilder → APK)
pwa = os.path.join(ROOT, 'pwa')
shutil.rmtree(pwa, ignore_errors=True); os.makedirs(os.path.join(pwa, 'icons'))
head = '''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#1E6FC4"><link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon-48.png" sizes="48x48"><link rel="icon" href="icons/icon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="icons/apple-touch-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}img{max-width:100%}</style>
</head><body>'''
tail = '''<script>if('serviceWorker' in navigator){addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));}</script></body></html>'''
open(os.path.join(pwa, 'index.html'), 'w', encoding='utf-8').write(head + body + tail)

manifest = {
  "name": "Copiloto Clínico APS", "short_name": "Copiloto Clínico",
  "description": "Apoyo diagnóstico y terapéutico para medicina general: 725 patologías y condiciones, diagnóstico sindromático, no pasar por alto, escalas y calculadoras, lectura de laboratorios, historia de pacientes local.",
  "lang": "es-CO", "start_url": "./index.html", "scope": "./", "display": "standalone",
  "orientation": "portrait", "background_color": "#EEF5FB", "theme_color": "#1E6FC4",
  "categories": ["medical", "health"],
  "icons": [
    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
json.dump(manifest, open(os.path.join(pwa, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

sw = '''const C='copiloto-v4';const A=['./','./index.html','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(A)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))));self.clients.claim();});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{const cp=res.clone();caches.open(C).then(c=>c.put(e.request,cp)).catch(()=>{});return res;}).catch(()=>caches.match('./index.html'))));});
'''
open(os.path.join(pwa, 'sw.js'), 'w').write(sw)

# Íconos a partir del SVG maestro (estetoscopio + corazón + ECG sobre azul celeste)
ICON_SET=[('icon-192.png',192,False),('icon-512.png',512,False),('maskable-512.png',512,True),('apple-touch-180.png',180,True),('favicon-48.png',48,False)]
SVG = open(os.path.join(ROOT, 'assets', 'icon.svg'), encoding='utf-8').read()
def svg_variant(maskable):
    s = SVG
    if maskable:  # zona segura 80 %: fondo a sangre y glifo reducido
        s = s.replace('rx="116"', 'rx="0"').replace('transform="translate(13 -33)"', 'transform="translate(256 256) scale(.76) translate(-243 -223)"')
    return s
ICDIR=os.path.join(ROOT,'assets','icons'); os.makedirs(ICDIR, exist_ok=True)
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name, size, mk in ICON_SET:
            pg = br.new_page(viewport={'width':size,'height':size})
            pg.set_content('<html><body style="margin:0;background:transparent">'+svg_variant(mk).replace('<svg ', f'<svg width="{size}" height="{size}" ',1)+'</body></html>')
            pg.screenshot(path=os.path.join(ICDIR, name), omit_background=True); pg.close()
        br.close()
except Exception as e:
    print('Íconos: se usan los PNG ya generados en assets/icons (Playwright no disponible:', type(e).__name__, ')')
for name,_,_ in ICON_SET:
    shutil.copy(os.path.join(ICDIR,name), os.path.join(pwa,'icons',name))
shutil.copy(os.path.join(ROOT,'assets','icon.svg'), os.path.join(pwa,'icons','icon.svg'))

z = os.path.join(ROOT, 'dist', 'copiloto-clinico-pwa.zip')
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for dp, _, fs in os.walk(pwa):
        for f in fs:
            full = os.path.join(dp, f); zf.write(full, os.path.relpath(full, pwa))
# Copia para GitHub Pages (carpeta docs/)
docs=os.path.join(ROOT,'docs'); shutil.rmtree(docs, ignore_errors=True); shutil.copytree(pwa, docs)
open(os.path.join(docs,'.nojekyll'),'w').close()
print('ok', len(body)//1024, 'KB')
