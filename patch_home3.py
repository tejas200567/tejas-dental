#!/usr/bin/env python3
"""Home page refresh (run inside ~/clinic):
- downloads the new checked 3D treatment pictures into images/
- makes small card pictures (needs ImageMagick 'convert' or Python Pillow; otherwise uses the originals)
- turns 'What we treat' and 'Guides and aftercare' into responsive picture cards
- puts the real treatment-room photo in 'About the clinic'
Safe to run twice."""
import os, re, shutil, subprocess, sys, urllib.request

if not os.path.exists("index.html"):
    sys.exit("Run this inside ~/clinic")

BASE = "https://arxhbdyciylznmlamvri.supabase.co/storage/v1/object/public/post-queue/site/"
NEW = ["t-root-canal", "t-wisdom", "t-scaling", "t-bridge", "t-dentures", "t-whitening", "t-filling", "t-kids"]
os.makedirs("images", exist_ok=True)
for n in NEW:
    dst = f"images/{n}.png"
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        continue
    try:
        urllib.request.urlretrieve(BASE + n + ".png", dst)
        if os.path.getsize(dst) < 10000:
            os.remove(dst)
    except Exception:
        if os.path.exists(dst):
            os.remove(dst)
print("new pictures:", [n for n in NEW if os.path.exists(f"images/{n}.png")])

TREAT = {"root-canal": "t-root-canal.png", "clear-aligners": "braces-aligner.png", "braces": "braces-metal.jpg",
         "dental-implants": "implant-fp1.jpg", "implant-overdenture": "implant-rp5lower2.png",
         "all-on-4-implants": "implant-fp3lower4.jpg", "tooth-extraction": "t-wisdom.png",
         "scaling-cleaning": "t-scaling.png", "crowns-bridges": "t-bridge.png", "dentures": "t-dentures.png",
         "teeth-whitening": "t-whitening.png", "fillings": "t-filling.png", "childrens-dentistry": "t-kids.png",
         "implant-options": "implant-fp2.jpg", "braces-comparison": "braces-ceramic.jpg",
         "post-extraction-care": "guide-post-extraction.jpg", "post-implant-care": "guide-post-implant.png",
         "brushing-technique": "brushing-bass-3d.png"}

have_convert = shutil.which("convert") is not None
try:
    from PIL import Image  # noqa
    have_pil = True
except Exception:
    have_pil = False


def card(slug):
    src = f"images/{TREAT.get(slug, '')}"
    if slug not in TREAT or not os.path.exists(src):
        return None
    dst = f"images/card-{slug}.jpg"
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    if have_convert:
        r = subprocess.run(["convert", src, "-auto-orient", "-resize", "720x540^", "-gravity", "center",
                            "-extent", "720x540", "-strip", "-quality", "80", dst])
        if r.returncode == 0:
            return dst
    if have_pil:
        im = Image.open(src).convert("RGB")
        w, h = im.size; t = 4 / 3
        if w / h > t:
            nw = int(h * t); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / t); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        im.resize((720, 540)).save(dst, "JPEG", quality=80, optimize=True)
        return dst
    return src  # no image tools: use the original picture


s = open("index.html", encoding="utf-8").read()
orig = s

CSS = """
/*home3*/
.tg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:8px}
@media(min-width:720px){.tg{grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}
@media(min-width:1080px){.tg{grid-template-columns:repeat(4,minmax(0,1fr))}}
.tg a{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden;text-decoration:none;color:var(--ink);box-shadow:0 4px 14px rgba(11,34,54,.06);transition:transform .2s,box-shadow .2s}
.tg a:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(11,34,54,.14)}
.tg .tim{display:block;aspect-ratio:4/3;background:radial-gradient(circle at 50% 40%,#1b3a57,#0b2236);overflow:hidden;position:relative}
.tg .tim img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s}
.tg a:hover .tim img{transform:scale(1.04)}
.tg .tim .ic{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) scale(1.8);color:#d9c8b8}
.tg .tb{display:block;padding:11px 12px 13px}
.tg .nm{display:block;font-size:1.05rem;line-height:1.25;color:var(--navy)}
.tg small{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;color:var(--muted);font-size:.82rem;line-height:1.4;margin-top:4px}
.tg .go{display:inline-block;margin-top:6px;font-size:.8rem;color:var(--taupe-d,#8a6f5a);font-weight:600}
@media(max-width:400px){.tg .nm{font-size:.98rem}.tg small{font-size:.78rem}}
.about.ph2{grid-template-columns:1fr}
@media(min-width:860px){.about.ph2{grid-template-columns:1fr 1.1fr;gap:48px;align-items:center}}
.about .abimg{margin:0;border-radius:18px;overflow:hidden;aspect-ratio:4/3;box-shadow:0 14px 34px rgba(11,34,54,.16)}
.about .abimg img{width:100%;height:100%;object-fit:cover;display:block}
"""

if "/*home3*/" not in s:
    s = s.replace("</style>", CSS + "</style>", 1)

ITEM = re.compile(r'<a href="([\w-]+)\.html">(<svg class="ic".*?</svg>)<div><span class="nm">(.*?)</span><small>(.*?)</small></div><span class="ar">→</span></a>', re.S)


def cardify(section_id):
    global s
    m = re.search(r'(<section[^>]*id="%s".*?<div class=")tl(">)(.*?)(</div>\s*</div></section>)' % section_id, s, re.S)
    if not m:
        print("section not found or already done:", section_id)
        return
    def rep(mm):
        slug, svg, nm, sm = mm.groups()
        c = card(slug)
        pic = f'<img src="{c}" alt="{nm}" loading="lazy" decoding="async">' if c else svg
        return (f'<a href="{slug}.html"><span class="tim">{pic}</span><span class="tb"><span class="nm">{nm}</span>'
                f'<small>{sm}</small><span class="go">Read more →</span></span></a>')
    inner = ITEM.sub(rep, m.group(3))
    s = s[:m.start()] + m.group(1) + "tg" + m.group(2) + inner + m.group(4) + s[m.end():]


cardify("services")
cardify("guides")

# real clinic photo in About (no dentist photo)
if 'class="abimg"' not in s and os.path.exists("images/treatment-room.jpg"):
    s = re.sub(r'<div class="about">\s*<div>',
               '<div class="about ph2">\n    <figure class="abimg"><img src="images/treatment-room.jpg" alt="Treatment room at Dr Tejas Pradhan\'s Dental Clinic, Jogeshwari East" loading="lazy" decoding="async"></figure>\n    <div>',
               s, count=1)

if s != orig:
    open("index.html", "w", encoding="utf-8").write(s)
    print("index.html updated")
else:
    print("index.html already up to date")

subprocess.run("git add index.html images && git commit -qm 'Home: picture cards for treatments and guides, real clinic photo' || true", shell=True)
print("Done. Now run: bash publish.sh")
