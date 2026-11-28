#!/usr/bin/env python3
"""Patch smile-design.html so every patient gets real AI photos in the smile report.

Usage (in your tejas-dental repo folder):
    python3 fix_ai_report.py smile-design.html
    git add smile-design.html && git commit -m "AI photos in report for everyone" && git push
"""
import sys, shutil

path = sys.argv[1] if len(sys.argv) > 1 else "smile-design.html"
src = open(path, encoding="utf-8").read()

EDITS = [
    # 1. AI-photo box in the report: show it to everyone, not only staff numbers
    ("if(isStaff())h+='<div class=\"note\" style=\"background:#fff\"><b>Clinic staff:</b>",
     "h+='<div class=\"note\" style=\"background:#fff\"><b>AI photos:</b>"),
    (">Make AI photos of the 3 designs</button>",
     ">Redo AI photos of the 3 designs</button>"),
    # 2. start the 3 AI photos automatically when the report appears
    ("var ab=document.getElementById('aib');if(ab)ab.addEventListener('click',aiPhotos)}",
     "var ab=document.getElementById('aib');if(ab){ab.addEventListener('click',aiPhotos);if(!PLAN._auto){PLAN._auto=1;aiPhotos()}}}"),
    # 3. lock the PDF button while the AI photos are being made
    ("function aiPhotos(){var b=document.getElementById('aib'),m=document.getElementById('aim'),i=0;b.disabled=true;",
     "function aiPhotos(){var b=document.getElementById('aib'),m=document.getElementById('aim'),i=0,pb=document.getElementById('pdfb');b.disabled=true;if(pb)pb.disabled=true;"),
    ("if(i>=3){b.disabled=false;m.textContent=",
     "if(i>=3){b.disabled=false;if(pb)pb.disabled=false;m.textContent="),
    ("m.textContent=(x.j&&x.j.error)||'AI photo failed.';b.disabled=false;return}",
     "m.textContent=(x.j&&x.j.error)||'AI photo failed.';b.disabled=false;if(pb)pb.disabled=false;return}"),
    (".catch(function(e){b.disabled=false;m.className='muted err';m.textContent='AI photo failed ('",
     ".catch(function(e){b.disabled=false;if(pb)pb.disabled=false;m.className='muted err';m.textContent='AI photo failed ('"),
    # 4. if a design has no AI photo yet, use the first AI photo for the recommended design instead of the drawing
    ("function optImg(o){return (PLAN.ai&&PLAN.ai[o.key])||withOpt(o,function(){return render('mockup')})}",
     "function optImg(o){if(PLAN.ai&&PLAN.ai[o.key])return PLAN.ai[o.key];if(o.key==PLAN.recommended&&S.after)return render('ai');return withOpt(o,function(){return render('mockup')})}"),
]

bad = [old[:70] for old, _ in EDITS if src.count(old) != 1]
if bad:
    print("NOT PATCHED - these pieces were not found exactly once:")
    for b in bad:
        print("  ", b)
    sys.exit(1)

shutil.copy(path, path + ".bak")
for old, new in EDITS:
    src = src.replace(old, new)
open(path, "w", encoding="utf-8").write(src)
print("Patched", path, "(backup:", path + ".bak)")
