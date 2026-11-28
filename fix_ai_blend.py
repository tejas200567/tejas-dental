#!/usr/bin/env python3
"""Patch smile-design.html: never show or save the raw AI picture (it re-draws the whole face).
Only the AI teeth, blended into the patient's own photo, are shown, and that finished picture
is saved on the server next to the patient's original.

Usage (in ~/clinic):
    python3 fix_ai_blend.py smile-design.html
    git add smile-design.html && git commit -m "AI photo: patient's own face only" && git push
"""
import sys, shutil

path = sys.argv[1] if len(sys.argv) > 1 else "smile-design.html"
src = open(path, encoding="utf-8").read()

EDITS = [
    # 1. remember which saved design this is, and save the finished picture
    ("msg.textContent='';aiBlend(x.j.analysis,x.j.after,function(u){show(x.j.analysis,u)})}",
     "msg.textContent='';S.id=x.j.id||null;aiBlend(x.j.analysis,x.j.after,function(u){saveFinal(u,'main');show(x.j.analysis,u)})}"),
    # 2. helper that sends the finished (blended) picture to the server
    ("var AIC=null;",
     "var AIC=null;function saveFinal(u,k){if(!u||!S.id)return;try{post({mode:'final',id:S.id,label:k,name:f.name.value,phone:f.phone.value,consent:f.consent.checked,image:u}).catch(function(){})}catch(e){}}"),
    # 3. if the AI teeth cannot be placed on the patient's own photo, show nothing rather than the raw AI face
    ("function aiBlend(a,after,cb,shade){AIC=null;if(!after||!beforeURL){cb(after);return}",
     "function aiBlend(a,after,cb,shade){AIC=null;if(!after||!beforeURL){cb(null);return}"),
    ("var P=(LIPS&&LIPS.inner)||(a&&a.mouth_polygon);if(!P||P.length<6){cb(after);return}",
     "var P=(LIPS&&LIPS.inner)||(a&&a.mouth_polygon);if(!P||P.length<6){cb(null);return}"),
    ("}).catch(function(){cb(after)})}",
     "}).catch(function(){cb(null)})}"),
    # 4. the 3 design photos: save each finished picture
    ("aiBlend(S.a,x.j.after,function(u){PLAN.ai[op.key]=u;try{thumbs()}catch(e){}res(u)}",
     "aiBlend(S.a,x.j.after,function(u){PLAN.ai[op.key]=u;saveFinal(u,op.key.toLowerCase());try{thumbs()}catch(e){}res(u)}"),
    # 5. 'Redo AI photo': save it, and show an error instead of a raw AI face if blending fails
    ("aiBlend(S.a,x.j.after,function(u){S.after=u;S.cache={};paint()})",
     "aiBlend(S.a,x.j.after,function(u){if(!u){b.disabled=false;m.className='muted err';m.textContent='Could not place the new teeth on your photo. Please try again.';return}saveFinal(u,'redo');S.after=u;S.cache={};paint()})"),
]

bad = [old[:70] for old, _ in EDITS if src.count(old) != 1]
if bad:
    print("NOT PATCHED - these pieces were not found exactly once:")
    for b in bad:
        print("  ", b)
    sys.exit(1)

shutil.copy(path, path + ".bak2")
for old, new in EDITS:
    src = src.replace(old, new)
open(path, "w", encoding="utf-8").write(src)
print("Patched", path, "(backup:", path + ".bak2)")
