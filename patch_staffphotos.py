#!/usr/bin/env python3
"""smile-design.html: 'Patient photos (clinic staff)' panel. Run inside ~/clinic, then bash publish.sh.
Shows only when a clinic number is typed in the phone box. Needs the staff PIN (same as the AI usage page).
Lists every stored smile photo (newest first, search by name or number), opens Before / AI After photos,
and 'Use this photo' loads the stored Before photo back into the tool so it can be designed again,
modified or animated. Safe to run again."""
import os, subprocess, sys

P = "smile-design.html"
if not os.path.exists(P):
    sys.exit("Run this inside ~/clinic")
s = open(P, encoding="utf-8").read()
orig = s

CSS = """
/*stfp*/
#stf{display:none;margin:18px 0;border:1px solid var(--line,#ddd);border-radius:14px;padding:14px;background:#fff}
#stf h3{margin:0 0 6px}
#stf .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}
#stf input{padding:9px 10px;border:1px solid #ccc;border-radius:8px;font:inherit;min-width:0}
#stfg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}
@media(min-width:720px){#stfg{grid-template-columns:repeat(4,minmax(0,1fr))}}
#stfg .it{border:1px solid #e3ddd4;border-radius:12px;overflow:hidden;background:#faf7f2;font-size:.84rem}
#stfg .it img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block;background:#222}
#stfg .it .tx{padding:7px 8px}
#stfg .it b{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#stfg .it .bt{display:flex;gap:6px;padding:0 8px 8px}
#stfg .it button{flex:1;font:inherit;font-size:.78rem;padding:6px 4px;border-radius:7px;border:1px solid #0b2236;background:#fff;color:#0b2236}
#stfg .it button.p{background:#0b2236;color:#fff}
#stfv{margin-top:12px}
#stfv .ims{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
#stfv figure{margin:0}#stfv img{width:100%;border-radius:10px;display:block}
#stfv figcaption{font-size:.8rem;text-align:center;color:#666}
"""
HTML = ('<div id="stf"><h3>Patient photos (clinic staff)</h3>'
        '<p class="muted">Every smile photo uploaded on this page is stored privately. Enter the staff PIN to see them. '
        'Use a patient\'s photo again to redesign, modify or animate it. Faces: only with the patient\'s consent.</p>'
        '<div class="row"><input id="stfpin" type="password" inputmode="numeric" placeholder="Staff PIN" style="width:130px">'
        '<input id="stfq" type="search" placeholder="Search name or number" style="flex:1">'
        '<button type="button" class="btn" id="stfgo">Show photos</button></div>'
        '<p class="muted" id="stfm"></p><div id="stfv"></div><div id="stfg"></div>'
        '<div class="row"><button type="button" class="btn o2" id="stfmore" style="display:none">Show more</button></div></div>')
JS = r"""<script>/*stfp*/(function(){
var SAPI='https://arxhbdyciylznmlamvri.supabase.co/functions/v1/staff-photos',box=document.getElementById('stf');if(!box)return;
var fm=document.getElementById('ds'),ph=fm&&fm.querySelector('[name=phone]'),off=0;
function staff(){if(window.__staff)try{return !!window.__staff()}catch(e){}var d=(ph&&ph.value||'').replace(/\D/g,'').slice(-10);return d=='9167511565'||d=='8369187806'}
function show(){box.style.display=staff()?'block':'none'}
if(ph){ph.addEventListener('input',show);ph.addEventListener('change',show)}show();
var pin=document.getElementById('stfpin');try{pin.value=localStorage.getItem('stfpin')||''}catch(e){}
function call(b){b.phone=ph.value;b.pin=pin.value;return fetch(SAPI,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(function(r){return r.json().then(function(j){if(!r.ok||j.error)throw new Error(j.error||'Failed');return j})})}
function esc(t){return String(t==null?'':t).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function day(t){try{return new Date(t).toLocaleString('en-IN',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'})}catch(e){return''}}
var m=document.getElementById('stfm'),g=document.getElementById('stfg'),v=document.getElementById('stfv'),more=document.getElementById('stfmore');
function load(reset){if(reset){off=0;g.innerHTML='';v.innerHTML=''}m.textContent='Loading…';
 call({mode:'list',offset:off,q:document.getElementById('stfq').value}).then(function(j){try{localStorage.setItem('stfpin',pin.value)}catch(e){}
  m.textContent=(off+j.items.length)+' photo(s) shown. Links work for 1 hour.';
  j.items.forEach(function(it){var d=document.createElement('div');d.className='it';
   d.innerHTML=(it.before?'<img loading="lazy" src="'+it.before+'" alt="Before photo">':'')+'<div class="tx"><b>'+esc(it.name)+'</b>'+esc(it.phone)+' · '+day(it.at)+(it.ai?' · AI':'')+'</div><div class="bt"><button type="button" data-v="'+it.id+'">View</button><button type="button" class="p" data-u="'+it.id+'" data-n="'+esc(it.name)+'">Use this photo</button></div>';g.appendChild(d)});
  off+=j.items.length;more.style.display=j.items.length==30?'inline-block':'none'}).catch(function(e){m.textContent=e.message})}
document.getElementById('stfgo').addEventListener('click',function(){load(true)});more.addEventListener('click',function(){load(false)});
g.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
 if(b.dataset.v){m.textContent='Opening…';call({mode:'get',id:b.dataset.v}).then(function(j){var it=j.item,u=it.urls,L={before:'Before',main:'AI After','redo':'AI After (redo)',a:'Design A',b:'Design B',c:'Design C'},h='';
  Object.keys(L).forEach(function(k){if(u[k])h+='<figure><img src="'+u[k]+'" alt="'+L[k]+'"><figcaption>'+L[k]+' · <a href="'+u[k]+'" target="_blank" rel="noopener">open</a></figcaption></figure>'});
  v.innerHTML='<h4 style="margin:6px 0">'+esc(it.name)+' · '+esc(it.phone)+' · '+day(it.at)+'</h4><div class="ims">'+h+'</div>'+(it.findings&&it.findings.length?'<p class="muted">'+it.findings.map(esc).join('; ')+'</p>':'');m.textContent='';v.scrollIntoView({behavior:'smooth',block:'start'})}).catch(function(e2){m.textContent=e2.message})}
 if(b.dataset.u){m.textContent='Loading the photo into the tool…';call({mode:'get',id:b.dataset.u}).then(function(j){var u=j.item.urls.before;if(!u)throw new Error('No Before photo stored');return fetch(u).then(function(r){return r.blob()})}).then(function(bl){
   var inp=document.getElementById('dsf'),dt=new DataTransfer();dt.items.add(new File([bl],'patient.jpg',{type:'image/jpeg'}));inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
   var nm=fm.querySelector('[name=name]');if(nm&&b.dataset.n)nm.value=b.dataset.n;var c=fm.querySelector('[name=consent]');if(c)c.checked=true;
   m.textContent='Photo loaded. Check the details and tap "Design my smile". When the results come, the Animate section is below the PDF button.';fm.scrollIntoView({behavior:'smooth',block:'start'})}).catch(function(e2){m.textContent=e2.message})}});
})();</script>"""

if "/*stfp*/" not in s:
    s = s.replace("</style>", CSS + "</style>", 1)
    s = s.replace('</form><div id="dso"></div>', '</form>' + HTML + '<div id="dso"></div>', 1)
    s = s.replace("</body>", JS + "\n</body>", 1)
if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("smile-design.html updated: staff patient photos panel added")
else:
    print("already up to date")
subprocess.run("git add smile-design.html; git commit -qm 'Smile design: staff patient photos panel' || true", shell=True)
print("Done. Now run: bash publish.sh")
