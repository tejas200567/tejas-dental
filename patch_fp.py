#!/usr/bin/env python3
"""implant-options.html: adds a 'FP-1, FP-2, FP-3: know the difference' panel (dark and gold
infographic style) with the clinic's FP-1/2/3 3D pictures (images/fp1-3.jpg). Run inside ~/clinic, then bash publish.sh.
Safe to run again."""
import os, re, shutil, subprocess, sys, urllib.request

if not os.path.exists("implant-options.html"):
    sys.exit("Run this inside ~/clinic")
EXIST = {"io-fp1": "images/fp1.jpg", "io-fp2": "images/fp2.jpg", "io-fp3": "images/fp3.jpg"}
pics = {k: (v if os.path.exists(v) else None) for k, v in EXIST.items()}
print("pictures:", pics)

ROWS = [
    ("FP-1", "Fixed bridge or crowns: replaces only the crown",
     "The new teeth have normal length and come out of your own healthy gum, so they look like natural teeth. No pink material is used.",
     "Enough bone and gum are still there (little shrinkage), usually soon after the tooth was lost. Best for front teeth when the gum shows on smiling.",
     "io-fp1", "FP-1: all-white implant bridge with teeth of natural length, below four abutments"),
    ("FP-2", "Fixed bridge: replaces the crown and part of the root",
     "Some bone has shrunk, so the teeth are made a little longer near the gum to fill the space. Still tooth-coloured only, with no pink material.",
     "Moderate bone loss, and a lip line that hides the gum side of the teeth when you smile and speak.",
     "io-fp2", "FP-2: all-white implant bridge with longer teeth near the gum, below four abutments"),
    ("FP-3", "Fixed bridge with pink gum: replaces teeth and gum",
     "Pink porcelain, zirconia or acrylic replaces the gum and bone that are lost, so the teeth keep a normal length. All-on-4 and All-on-6 bridges are FP-3.",
     "Major bone loss or a full arch of missing teeth, or when the lips need support for a fuller face.",
     "io-fp3", "FP-3: implant bridge with pink gum-coloured porcelain, below four abutments"),
]

CSS = """
/*fp3panel*/
.fpk{background:radial-gradient(120% 80% at 50% 0%,#14324d 0%,#0b2236 55%,#081a2a 100%);color:#f3ede6;border:1px solid #b8975a;border-radius:18px;padding:22px 16px 18px;margin:22px 0 30px;box-shadow:0 18px 40px rgba(8,26,42,.35)}
.fpk h2{color:#e7c88d;text-align:center;margin:0 0 4px;letter-spacing:.06em}
.fpk .sub{text-align:center;font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:#cdb89a;margin:0 0 16px}
.fpr{display:grid;grid-template-columns:1fr;gap:12px;border:1px solid rgba(184,151,90,.55);border-radius:14px;padding:14px;margin-bottom:14px;background:rgba(255,255,255,.03)}
@media(min-width:760px){.fpr{grid-template-columns:1.05fr .95fr;align-items:center;padding:18px}}
.fpr .hd{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.fpr .bd{flex:0 0 auto;background:linear-gradient(180deg,#f1d79f,#b8975a);color:#0b2236;font-weight:800;font-size:1.05rem;padding:6px 10px;border-radius:8px;letter-spacing:.04em}
.fpr h3{margin:0;color:#f3ede6;font-size:1.05rem;line-height:1.3}
.fpr p{margin:0 0 10px;font-size:.92rem;line-height:1.5;color:#e4ddd3}
.fpr .ind{border-left:3px solid #e7c88d;background:rgba(231,200,141,.08);padding:8px 10px;border-radius:0 8px 8px 0;font-size:.88rem;color:#f3ede6}
.fpr .ind b{color:#e7c88d;display:block;font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;margin-bottom:2px}
.fpr figure{margin:0;border-radius:12px;overflow:hidden;border:1px solid rgba(184,151,90,.45);aspect-ratio:4/3;background:#081a2a}
.fpr figure img{width:100%;height:100%;object-fit:cover;display:block}
@media(max-width:759px){.fpr figure{order:-1}}
.fpb{display:grid;grid-template-columns:1fr;gap:12px}
@media(min-width:760px){.fpb{grid-template-columns:1fr 1fr}}
.fpb>div{border:1px solid rgba(184,151,90,.55);border-radius:14px;padding:14px;background:rgba(255,255,255,.03)}
.fpb h4{margin:0 0 8px;color:#e7c88d;letter-spacing:.12em;text-transform:uppercase;font-size:.8rem}
.fpb ul{margin:0;padding-left:18px;font-size:.88rem;line-height:1.5;color:#e4ddd3}
.fpb li{margin:3px 0}
.fpk .tag2{text-align:center;margin:14px 0 0;font-family:"Cormorant Garamond",Georgia,serif;font-style:italic;color:#e7c88d;font-size:1.15rem}
"""


def row(code, title, what, ind, key, alt):
    p = pics.get(key)
    fig = f'<figure><img src="{p}" alt="{alt}, 3D illustration" loading="lazy" decoding="async"></figure>' if p else ""
    return (f'<div class="fpr"><div><div class="hd"><span class="bd">{code}</span><h3>{title}</h3></div>'
            f'<p>{what}</p><div class="ind"><b>When it is used</b>{ind}</div></div>{fig}</div>')


panel = ('<div class="fpk" id="fp123"><h2>FP-1, FP-2, FP-3</h2><p class="sub">Know the difference · Misch classification</p>'
         + "".join(row(*r) for r in ROWS)
         + '<div class="fpb"><div><h4>How the dentist chooses</h4><ul>'
           '<li>How much bone and gum is left, checked on a 3D CBCT scan.</li>'
           '<li>Your smile line: how much gum shows when you smile.</li>'
           '<li>Lip and face support you need.</li>'
           '<li>How easily you can clean under the bridge.</li></ul></div>'
           '<div><h4>Key points</h4><ul>'
           '<li><b>FP-1</b>: crown only, looks natural, no pink.</li>'
           '<li><b>FP-2</b>: teeth a little longer near the gum, no pink.</li>'
           '<li><b>FP-3</b>: teeth plus pink gum, for bigger bone loss and full arches.</li>'
           '<li>All three are fixed: only the dentist can remove them.</li></ul></div></div>'
           '<p class="tag2">Your smile, your confidence</p></div>')

s = open("implant-options.html", encoding="utf-8").read()
orig = s
if "/*fp3panel*/" not in s:
    s = s.replace("</style>", CSS + "</style>", 1)
s = re.sub(r'<div class="fpk" id="fp123">.*?<p class="tag2">Your smile, your confidence</p></div>', "", s, count=1, flags=re.S)
anchor = "RP-4 and RP-5 describe what supports the denture.</p>"
if anchor in s:
    s = s.replace(anchor, anchor + panel, 1)
else:
    print("anchor not found; panel not added")
if s != orig:
    open("implant-options.html", "w", encoding="utf-8").write(s)
    print("implant-options.html updated")
subprocess.run("git add implant-options.html images; git commit -qm 'FP-1/2/3 know-the-difference panel' || true", shell=True)
print("Done. Now run: bash publish.sh")
