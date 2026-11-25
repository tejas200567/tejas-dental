"""Build the whole clinic website (homepage + treatment pages + sitemap + llms.txt).

Usage:  python build.py <site_folder>
Photos: put JPG/PNG/WebP files in <site_folder>/images/ using these names:
    front, reception, treatment-room, equipment, doctor, team   (add -2, -3 ... for more)
Optional images/captions.txt, one line per photo:  reception: Waiting area with seating for patients
Pages use only photos that exist, so the site is complete with or without photos.
Edit RATING / REVIEWS below when your Google numbers change.
"""
import html, json, re, sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent))
from content import PAGES

OUT = Path(sys.argv[1]).resolve()
BASE = "https://SITE_URL"
CLINIC = "Dr Tejas Pradhan's Dental Clinic"
PHONE = "+91 83691 87806"
PHONE2 = "+91 91675 11565"
RATING, REVIEWS = "4.9", "82"          # Google rating shown on the homepage
ADDR = ("Shop No. A-19, Aareshwar Society, Opp. Dheeraj Darshan, Kokan Nagar Road, "
        "Near Kokan Hospital, Jogeshwari East, Mumbai, Maharashtra 400060")
MAPS = ("https://www.google.com/maps/search/?api=1&query=Dr+Tejas+Pradhan's+Dental+Clinic"
        "+Kokan+Nagar+Jogeshwari+East+Mumbai")
WA = "https://wa.me/918369187806?text=Hello%2C%20I%20would%20like%20to%20book%20an%20appointment."
e = html.escape

# ---------------------------------------------------------------- photos
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
CAPTIONS = {
    "front": f"Entrance of {CLINIC} on Kokan Nagar Road, Jogeshwari East",
    "reception": f"Reception and waiting area at {CLINIC}",
    "treatment-room": f"Treatment room with dental chair at {CLINIC}",
    "equipment": f"Dental equipment at {CLINIC}",
    "doctor": "Dr. Tejas Pradhan, dentist in Jogeshwari East, Mumbai",
    "team": f"The team at {CLINIC}",
    "ppe": "Dr. Tejas Pradhan in protective gear at the clinic",
}


def load_images():
    d = OUT / "images"
    if not d.is_dir():
        return []
    custom = {}
    cf = d / "captions.txt"
    if cf.exists():
        for line in cf.read_text(encoding="utf-8").splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                custom[k.strip().rsplit(".", 1)[0]] = v.strip()
    res = []
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in IMG_EXT:
            continue
        base = re.sub(r"-\d+$", "", f.stem)
        res.append({"url": f"images/{quote(f.name)}", "stem": f.stem, "base": base,
                    "caption": custom.get(f.stem) or CAPTIONS.get(base) or f"Photo of {CLINIC}, Jogeshwari East"})
    return res


IMAGES = load_images()
doctor_img = next((i for i in IMAGES if i["base"] == "doctor"), None)
hero_img = next((i for b in ("front", "reception", "treatment-room") for i in IMAGES if i["base"] == b), None)
CLINIC_IMAGES = [i for i in IMAGES if not i["base"].startswith(("guide-", "ortho-"))]
gallery = [i for i in CLINIC_IMAGES if i is not doctor_img and i is not hero_img]


def img_tag(i, lazy=True, cls=""):
    lz = 'loading="lazy" ' if lazy else ""
    cl = f' class="{cls}"' if cls else ""
    return f'<img src="{i["url"]}" alt="{e(i["caption"])}" {lz}decoding="async"{cl}>'


# ---------------------------------------------------------------- icons (24x24, stroke)
TOOTH = ("M7 3C4.8 3 3 4.8 3 7.2c0 2 .8 3.4 1.3 5 .6 2 .7 4.3 1.2 6 .3 1 1 1.8 1.8 1.8 1.3 0 1.4-2.2 2-4 "
         ".3-1 .8-1.5 1.7-1.5s1.4.5 1.7 1.5c.6 1.8.7 4 2 4 .8 0 1.5-.8 1.8-1.8.5-1.7.6-4 1.2-6 .5-1.6 1.3-3 "
         "1.3-5C21 4.8 19.2 3 17 3c-1.7 0-2.6.8-5 .8S8.7 3 7 3z")
ICONS = {
    "root-canal": f'<path d="{TOOTH}"/><path d="M10 12v5M14 12v5"/>',
    "clear-aligners": '<path d="M3 15c0-5 4-9 9-9s9 4 9 9v2H3z"/><path d="M6.5 15c0-3 2.4-5.5 5.5-5.5s5.5 2.5 5.5 5.5"/>',
    "braces": '<rect x="3" y="7" width="5" height="10" rx="1.5"/><rect x="9.5" y="7" width="5" height="10" rx="1.5"/>'
              '<rect x="16" y="7" width="5" height="10" rx="1.5"/><path d="M2 12h20"/>',
    "dental-implants": '<path d="M6 3h12v5H6z"/><path d="M9 8v11l3 2.5 3-2.5V8"/><path d="M9 11.5h6M9 14.5h6M9 17.5h6"/>',
    "implant-overdenture": '<path d="M3 6c0-2 4-3 9-3s9 1 9 3v3c0 1.5-1 2.5-2 2.5H5c-1 0-2-1-2-2.5z"/><path d="M7 11.5V21M12 11.5V21M17 11.5V21"/>',
    "all-on-4-implants": '<path d="M3 5c0-1.5 4-2.500 9-2.500s9 1 9 2.500v3H3z"/><path d="M6 8v12M10 8v12M14 8v12M18 8v12"/>',
    "tooth-extraction": f'<path d="{TOOTH}"/><path d="M12 12V6M9.5 8.5 12 6l2.5 2.5"/>',
    "scaling-cleaning": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15v5M16.5 17.5h5"/>',
    "crowns-bridges": '<path d="M4 18 3 8l5 4 4-7 4 7 5-4-1 10z"/><path d="M4 21h16"/>',
    "dentures": '<path d="M3 8c0-3 4-5 9-5s9 2 9 5v2c0 2-1 3-2 3H5c-1 0-2-1-2-3z"/><path d="M8 13v4M12 13v5M16 13v4"/>',
    "teeth-whitening": f'<path d="{TOOTH}"/><path d="M19 1v4M17 3h4"/>',
    "fillings": f'<path d="{TOOTH}"/><circle cx="12" cy="8.5" r="1.8" fill="currentColor"/>',
    "childrens-dentistry": '<circle cx="12" cy="12" r="9"/><path d="M8.5 14c1 1.5 2.2 2.2 3.5 2.2s2.5-.7 3.5-2.2"/>'
                           '<circle cx="9" cy="10" r=".8" fill="currentColor"/><circle cx="15" cy="10" r=".8" fill="currentColor"/>',
}
MENU_ICONS = {
    "home": '<path d="M3 11l9-8 9 8M5 10v10h5v-6h4v6h5V10"/>',
    "tooth": f'<path d="{TOOTH}"/>',
    "about": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    "photos": '<path d="M3 5h18v14H3z"/><path d="M3 16l5-5 4 4 3-3 6 6"/><circle cx="16" cy="9" r="1"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "pin": '<path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "guide": '<path d="M5 4h11l3 3v13H5z"/><path d="M9 11h6M9 15h6"/>',
    "faq": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7M12 17h.01"/>',
}


def svg(inner, size=24, sw=1.6):
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')


def icon(slug, size=26):
    return svg(ICONS[slug], size)


FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
           "stroke='%230b2236' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='"
           + TOOTH + "'/%3E%3C/svg%3E")

# ---------------------------------------------------------------- shared CSS
CSS = """
:root{--ink:#1d1a17;--navy:#0b2236;--navy2:#143550;--sand:#e8e0d6;--cream:#faf7f2;--taupe:#b79f8c;--taupe-d:#8a705a;--muted:#6b645c;--line:#e3dbd0;--wa:#1faa59}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:17px;line-height:1.7;color:var(--ink);background:var(--cream);padding-bottom:62px}
a{color:var(--navy2)}img{max-width:100%;display:block}
h1,h2,h3.sf,.num,.nm{font-family:ui-serif,Georgia,"Iowan Old Style","Palatino Linotype",Palatino,"Times New Roman",serif;font-weight:400}
h2{font-size:1.55rem;line-height:1.25;letter-spacing:.05em;text-transform:uppercase;margin:6px 0 18px}
h3{font-size:1.02rem;line-height:1.4;margin:22px 0 4px}
.kick{font-size:.76rem;letter-spacing:.24em;text-transform:uppercase;color:var(--taupe-d);margin:0}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}.narrow{max-width:780px}
.muted{color:var(--muted);font-size:.93rem}
/* top bar + menu */
.top{position:sticky;top:0;z-index:70;background:#fff;border-bottom:1px solid var(--line);height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 16px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--navy);font-family:ui-serif,Georgia,serif;font-size:1.02rem;line-height:1.15;letter-spacing:.02em}
.brand .mk{flex:none;width:38px;height:38px;background:var(--navy);color:#fff;display:grid;place-items:center}
.burger{cursor:pointer;width:44px;height:44px;display:grid;place-content:center;gap:6px}.burger i{display:block;width:26px;height:2px;background:var(--ink)}
.mnc{position:absolute;opacity:0;pointer-events:none}
.menu{display:none;position:fixed;inset:0;z-index:60;background:#fff;overflow:auto;padding-bottom:40px}
.mnc:checked~.menu{display:block}
.menu .cl{background:var(--sand);height:76px;display:grid;place-items:center;cursor:pointer;font-size:1.6rem;line-height:1}
.menu ul{list-style:none;margin:26px 22px;padding:0}
.menu li a{display:flex;align-items:center;gap:20px;padding:10px 14px;text-decoration:none;color:var(--ink);text-transform:uppercase;letter-spacing:.08em;font-size:1rem}
.menu li a .bx{flex:none;width:76px;height:46px;border:1px solid var(--line);display:grid;place-items:center;background:#fff;color:#444}
.menu li a.on{background:var(--navy);color:#fff}.menu li a.on .bx{background:var(--sand);color:var(--navy)}
.menu .mc{margin:0 22px;padding:16px;background:#f6f1ea;border:1px solid var(--line);text-align:center;font-size:.95rem}
/* hero */
.hero{position:relative;background:var(--navy);color:#fff;overflow:hidden;display:flex;align-items:flex-end;min-height:min(80vh,620px)}
.hero .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,34,54,.35) 0%,rgba(11,34,54,.78) 100%);z-index:1}
.hero.plain:before{background:radial-gradient(circle at 85% 15%,rgba(183,159,140,.28),transparent 55%),linear-gradient(135deg,#0b2236,#143550)}
.hero .wm{position:absolute;right:-40px;top:20px;width:340px;height:340px;opacity:.07;color:#fff;z-index:1}
.hero .wrap{position:relative;z-index:2;padding-top:60px;padding-bottom:44px;width:100%}
.hero h1{font-size:2.15rem;line-height:1.15;margin:10px 0 14px;letter-spacing:.005em}
.hero p{margin:0 0 8px;max-width:620px;opacity:.95}
.hero.sm{min-height:0}.hero.sm .wrap{padding-top:34px;padding-bottom:32px}.hero.sm h1{font-size:1.9rem}
.crumb{font-size:.86rem;opacity:.85;margin-bottom:6px}.crumb a{color:#fff}
.cta{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.btn{display:inline-block;text-decoration:none;padding:13px 24px;font-weight:600;letter-spacing:.04em;font-size:.92rem;background:var(--taupe);color:#1d1a17;border:1px solid var(--taupe)}
.btn.o{background:transparent;color:#fff;border-color:rgba(255,255,255,.6)}.btn.wa{background:var(--wa);border-color:var(--wa);color:#fff}
/* stats */
.stats{background:var(--navy);color:#fff}.stats .wrap{display:grid;grid-template-columns:1fr 1fr;gap:26px 14px;padding-top:34px;padding-bottom:34px}
.stats .num{font-size:2.3rem;line-height:1;color:#fff}.stats span{display:block;margin-top:8px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;opacity:.8;line-height:1.4}
/* sections */
.sec{padding:52px 0}.sec.alt{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.about{display:grid;gap:26px}.about .dr{aspect-ratio:4/5;background:var(--sand);max-width:340px;overflow:hidden}.about .dr img{width:100%;height:100%;object-fit:cover}
.tl{border-top:1px solid var(--line)}
.tl a{display:grid;grid-template-columns:44px 1fr 22px;gap:16px;align-items:center;padding:18px 2px;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}
.tl .ic{color:var(--taupe-d)}.tl .nm{font-size:1.22rem;color:var(--navy);line-height:1.25}.tl small{display:block;color:var(--muted);font-size:.9rem;line-height:1.45;margin-top:2px}
.tl .ar{color:var(--taupe-d);font-size:1.3rem}.tl a:hover .nm{text-decoration:underline}
.ap{display:grid;gap:26px}.ap .num{font-size:2.6rem;color:var(--taupe);line-height:1}.ap h3{margin:6px 0 6px;font-size:1.05rem;letter-spacing:.06em;text-transform:uppercase}
.gal{display:grid;grid-template-columns:1fr 1fr;gap:12px}.gal figure{margin:0}.gal img{width:100%;aspect-ratio:4/3;object-fit:cover;background:var(--sand)}
.gal figcaption{font-size:.82rem;color:var(--muted);padding-top:6px;line-height:1.35}
table{border-collapse:collapse;width:100%}td{padding:10px 2px;border-bottom:1px solid var(--line);vertical-align:top}
.two{display:grid;gap:26px}
.cards{display:grid;gap:18px}@media(min-width:760px){.cards{grid-template-columns:1fr 1fr}}
.card{background:#fff;border:1px solid var(--line)}.card .ph svg,.card .ph img{width:100%;height:auto;display:block}.card .cb{padding:16px 18px}.card .cb ul{margin:8px 0}
.dv summary{cursor:pointer;color:var(--navy2);font-weight:600;padding:6px 0}.dv .vid{margin-top:8px}
.cmpw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:12px 0 8px}.cmp{border-collapse:collapse;min-width:820px;width:100%;font-size:.9rem;line-height:1.45}
.cmp th,.cmp td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top;background:#fff}.cmp th{background:var(--navy);color:#fff;font-weight:400}.cmp td:first-child{font-weight:600;background:var(--cream);position:sticky;left:0}
.note{background:#fff7e6;border:1px solid #ecd9a8;padding:12px 14px;margin:16px 0;font-size:.95rem}
.scf label{display:block;margin:14px 0;font-weight:600}.scf input[type=text],.scf input:not([type]),.scf input[name=phone]{display:block;width:100%;font:inherit;padding:12px;border:1px solid var(--line);background:#fff;margin-top:6px}
.scf input[type=file]{display:block;margin-top:6px;font:inherit;width:100%}.scf .ck{font-weight:400;font-size:.92rem}.scf .ck input{margin-right:8px}.scf button{border:0;cursor:pointer;font:inherit;margin-top:8px}
.prev{display:flex;gap:8px;flex-wrap:wrap}.prev img{width:30%;max-width:140px;aspect-ratio:1;object-fit:cover;border:1px solid var(--line)}
.res{margin-top:28px;border-top:2px solid var(--navy);padding-top:8px}.warn{background:#fdecec;border:1px solid #e59a9a;padding:12px 14px;margin:12px 0}.err{color:#b3261e}
.prev.one img{width:100%;max-width:420px;aspect-ratio:auto}
.ba{position:relative;overflow:hidden;border:1px solid var(--line);background:#000}.ba img{width:100%;display:block}.ba .af{position:absolute;inset:0}.ba .af img{width:100%;height:100%;object-fit:cover}
.ba input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:ew-resize;z-index:3}.ba .hd{position:absolute;top:0;bottom:0;width:2px;margin-left:-1px;background:#fff;box-shadow:0 0 4px rgba(0,0,0,.6);z-index:2;pointer-events:none}.ba .hd:after{content:'\25C0\00a0\25B6';position:absolute;top:50%;left:50%;width:44px;height:44px;margin:-22px 0 0 -22px;border:3px solid #fff;border-radius:50%;color:#fff;font-size:11px;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.2);box-shadow:0 0 6px rgba(0,0,0,.5)}.ba .tg{position:absolute;top:8px;background:rgba(11,34,54,.8);color:#fff;font-size:.8rem;padding:2px 8px}.ba .l{left:8px}.ba .r{right:8px}
.pg{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0}.pg figure{margin:0;background:#fff;border:1px solid var(--line)}.pg svg{width:100%;height:auto;display:block}
.pg figcaption{padding:8px 10px;font-size:.84rem;line-height:1.4}.pg figure:first-child{grid-column:1/-1}.pg figure:first-child svg{max-width:340px;margin:0 auto;display:block}
.camb{border:0;cursor:pointer;font:inherit;width:100%;margin-top:14px;padding:14px}
.cam{position:fixed;inset:0;background:#000;z-index:300;display:flex;flex-direction:column;color:#fff;overflow:auto}
.cam[hidden],.cam [hidden],.cam.pv .cambar{display:none!important}
.camtop{display:flex;justify-content:flex-end;padding:8px 12px}.camtop button,#camflip{background:none;border:0;color:#fff;font-size:1.6rem;cursor:pointer;padding:6px 10px}
.camstage{position:relative;margin:0 auto;width:min(100%,calc(58vh * var(--ar,0.75)));aspect-ratio:var(--ar,0.75);background:#111;overflow:hidden}
.camstage video,.camstage canvas{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.camstage .pill{position:absolute;left:50%;top:6%;transform:translateX(-50%);background:rgba(0,0,0,.75);padding:6px 14px;border-radius:20px;font-size:.9rem;white-space:nowrap;max-width:92%;overflow:hidden;text-overflow:ellipsis}
.camstage .count{position:absolute;right:6%;bottom:4%;font-size:3.2rem;font-weight:700;text-shadow:0 2px 6px #000}
.camtxt{padding:10px 18px 0}.camtxt h3{margin:4px 0;font-size:1.25rem}.camtxt p{margin:4px 0 8px;opacity:.85;font-size:.92rem}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chips span{font-size:.78rem;padding:4px 9px;border-radius:14px;background:#333;color:#bbb}.chips span.on{background:#14532d;color:#bbf7d0}
.chips span.on:before{content:"✓ "}
.cambar{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:14px 18px}.cambar #camflip{justify-self:end}
.shot{width:78px;height:78px;border-radius:50%;border:0;background:none;padding:0;cursor:pointer}.shot svg{width:100%;height:100%;transform:rotate(-90deg)}
.shot .bg{fill:#666;stroke:#ddd;stroke-width:5}.shot .pr{fill:none;stroke:#4ade80;stroke-width:6;stroke-linecap:round;stroke-dasharray:213.6;stroke-dashoffset:213.6}
.camprev{padding:10px 18px}.camprev img{width:100%;max-width:520px;display:block;margin:0 auto 12px}.camprev .btn{border:0;cursor:pointer;font:inherit}
.ok{color:#1f7a4d;font-weight:600}
.seg{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.seg button{font:inherit;font-size:.88rem;padding:8px 12px;border:1px solid var(--navy);background:#fff;color:var(--navy);cursor:pointer}.seg button.on{background:var(--navy);color:#fff}.seg.sm button{font-size:.82rem;padding:6px 10px}
.bg{display:grid;grid-template-columns:1fr 1fr;gap:8px}.bg figure{margin:0;cursor:pointer;border:1px solid var(--line);background:#fff}.bg img{width:100%;display:block}.bg figcaption{font-size:.82rem;padding:4px 8px;font-weight:600}
.ctl{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;margin:12px 0}.ctl label{font-size:.88rem;font-weight:600;display:flex;flex-direction:column;gap:4px}.ctl select{font:inherit;padding:8px;border:1px solid var(--line);background:#fff}
.ctl .ck2{flex-direction:row;align-items:center;font-weight:400}.btn.o2{background:#fff;color:var(--navy);border:1px solid var(--navy);cursor:pointer;font:inherit;padding:9px 14px}.wn{color:#b3261e;font-weight:600}
.chart{margin:16px 0}.chart img{width:100%;height:auto;border:1px solid var(--line)}.chart figcaption{margin-top:6px}
.vid{position:relative;aspect-ratio:16/9;background:#000;margin:6px 0 10px}.vid iframe{position:absolute;inset:0;width:100%;height:100%;margin:0}
iframe{width:100%;height:300px;border:0;background:var(--sand)}
ul.b,ol.b{padding-left:20px}ul.b li,ol.b li{margin:7px 0}
.faq h3{border-top:1px solid var(--line);padding-top:16px;margin-top:16px}.faq h3:first-of-type{border:0;margin-top:0;padding-top:0}
.contact{background:var(--navy);color:#fff}.contact a{color:#fff}.contact h2{color:#fff}.contact .kick{color:var(--taupe)}
footer{background:#07151f;color:#aebdc9;font-size:.86rem;padding:22px 0}footer a{color:#fff}
/* bottom bar */
.bar{position:fixed;left:0;right:0;bottom:0;z-index:50;display:grid;grid-template-columns:1fr 1fr 1fr;height:58px}
.bar a{display:flex;align-items:center;justify-content:center;gap:8px;text-decoration:none;font-weight:600;font-size:.93rem;background:var(--navy);color:#fff;border-left:1px solid rgba(255,255,255,.12)}
.bar a:first-child{border:0}.bar a.dir{background:var(--taupe);color:#1d1a17}
@media(min-width:760px){
 body{padding-bottom:0}.bar{display:none}
 .hero h1{font-size:3.2rem}.hero.sm h1{font-size:2.5rem}.hero .wrap{padding-bottom:64px}
 .stats .wrap{grid-template-columns:repeat(4,1fr)}.sec{padding:76px 0}
 .about.has-dr{grid-template-columns:300px 1fr;gap:48px;align-items:start}
 .tl{display:grid;grid-template-columns:1fr 1fr;column-gap:48px}
 .ap{grid-template-columns:repeat(3,1fr);gap:40px}.gal{grid-template-columns:repeat(3,1fr)}.two{grid-template-columns:1fr 1.2fr;gap:44px}
 h2{font-size:1.9rem}
}
"""

HEAD_COMMON = ('<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
               '<meta name="theme-color" content="#0b2236">\n'
               f'<link rel="icon" href="{FAVICON}">\n')

SCRIPT = ("<script>document.querySelectorAll('.menu a').forEach(function(a){a.addEventListener('click',"
          "function(){document.getElementById('mn').checked=false})})</script>")


def menu_items(home_page, has_gallery):
    p = "" if home_page else "index.html"
    items = [("home", "Home", f"{p}#top" if home_page else "index.html"),
             ("tooth", "Treatments", f"{p}#services"),
             ("about", "About", f"{p}#about"),
             ("list", "Our approach", f"{p}#approach")]
    if has_gallery:
        items.append(("photos", "Gallery", f"{p}#clinic"))
    items.append(("guide", "Patient guides", f"{p}#guides"))
    items += [("clock", "Timings", f"{p}#timings"), ("pin", "Location", f"{p}#location"),
              ("faq", "FAQ", f"{p}#faq")]
    return items


def topbar(home_page=False):
    lis = ""
    for i, (ic, label, href) in enumerate(menu_items(home_page, bool(gallery))):
        on = ' class="on"' if (i == 0 and home_page) else ""
        lis += f'<li><a href="{href}"{on}><span class="bx">{svg(MENU_ICONS[ic], 22)}</span>{label}</a></li>'
    mark = svg(f'<path d="{TOOTH}"/>', 22, 1.7)
    return (f'<header class="top" id="top"><a class="brand" href="index.html"><span class="mk">{mark}</span>'
            f'<span>{e(CLINIC)}</span></a>'
            f'<input type="checkbox" id="mn" class="mnc" aria-label="Menu"><label for="mn" class="burger" aria-label="Open menu"><i></i><i></i><i></i></label>'
            f'<nav class="menu"><label for="mn" class="cl" aria-label="Close menu">×</label><ul>{lis}</ul>'
            f'<div class="mc">Call or WhatsApp<br><b>{PHONE}</b><br>{PHONE2}</div></nav></header>')


def bottom_bar():
    return ('<div class="bar"><a href="https://wa.me/918369187806">WhatsApp</a>'
            '<a href="tel:+918369187806">Call</a>'
            f'<a class="dir" href="{MAPS}">Directions</a></div>')


def footer():
    return (f'<footer><div class="wrap">© {e(CLINIC)}, Jogeshwari East, Mumbai · Dr. Tejas Pradhan, '
            f'Maharashtra State Dental Council Reg. No. A-20222.<br>General information only; treatment is decided '
            f'after an examination.</div></footer>')


def one_liner(p):
    return p["intro"].split(". ")[0].rstrip(".") + "."


SHORT = {
    "root-canal": "Save a painful or infected tooth instead of extracting it.",
    "clear-aligners": "Nearly invisible, removable trays to straighten teeth.",
    "braces": "Brackets and wires to straighten teeth and correct the bite.",
    "dental-implants": "A titanium post that replaces a missing tooth root.",
    "implant-overdenture": "A removable denture that snaps onto implants and stays firm.",
    "all-on-4-implants": "A fixed full arch of teeth on four implants.",
    "tooth-extraction": "Routine and wisdom tooth removal under local anaesthesia.",
    "scaling-cleaning": "Remove tartar, plaque and stains that brushing cannot.",
    "crowns-bridges": "Caps and bridges that protect or replace teeth.",
    "dentures": "Removable replacements for missing teeth.",
    "teeth-whitening": "Lighten the natural colour of your teeth, supervised by a dentist.",
    "fillings": "Tooth-coloured fillings for cavities and small chips.",
    "childrens-dentistry": "Check-ups, fillings and preventive care for children.",
}


def tlist(skip=None):
    return '<div class="tl">' + "".join(
        f'<a href="{p["slug"]}.html">{icon(p["slug"])}<div><span class="nm">{e(p["name"])}</span>'
        f'<small>{e(SHORT.get(p["slug"], one_liner(p)))}</small></div><span class="ar">→</span></a>'
        for p in PAGES if p["slug"] != skip) + "</div>"


# ---------------------------------------------------------------- homepage content
HOME_FAQS = [
    ("Where is Dr Tejas Pradhan's Dental Clinic?",
     "Shop No. A-19, Aareshwar Society, opposite Dheeraj Darshan, Kokan Nagar Road, near Kokan Hospital, Jogeshwari East, Mumbai 400060."),
    ("What are the clinic timings?", "Monday to Saturday, 11 am to 2:30 pm and 5:30 pm to 9 pm. Closed on Sunday."),
    ("Do I need an appointment?", "Appointments are recommended. Call or WhatsApp +91 83691 87806 or +91 91675 11565."),
    ("Who is the dentist?", "Dr. Tejas Pradhan, registered with the Maharashtra State Dental Council, Reg. No. A-20222."),
    ("Do you do root canal treatment in Jogeshwari East?",
     "Yes. Root canal treatment is done at the clinic with digital RVG X-rays. The number of sittings depends on the tooth."),
    ("Do you offer braces or clear aligners?", "Yes. The clinic offers metal braces and clear aligners for teens and adults."),
    ("Do you treat children?", "Yes. Check-ups, fillings and preventive care for children."),
    ("Can I get a wisdom tooth removed here?",
     "Yes. Most wisdom tooth extractions are done in the clinic under local anaesthesia after an X-ray."),
    ("Is the clinic accessible, and how can I pay?",
     "The entrance is wheelchair accessible and parking is available. Cash, UPI and card/NFC payments are accepted."),
]
SERVICES_LD = ["Root canal treatment", "Tooth extraction and wisdom tooth removal", "Scaling and polishing",
               "Tooth-coloured fillings", "Teeth whitening", "Crowns and bridges", "Dentures", "Dental implants",
               "Braces and clear aligners", "Children's dentistry"]
WATERMARK = (f'<svg class="wm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width=".6" '
             f'aria-hidden="true"><path d="{TOOTH}"/></svg>')


def home():
    dentist = {
        "@context": "https://schema.org", "@type": "Dentist", "@id": f"{BASE}/#clinic",
        "name": CLINIC, "url": f"{BASE}/", "telephone": "+91-83691-87806",
        "contactPoint": [{"@type": "ContactPoint", "telephone": "+91-91675-11565",
                          "contactType": "appointments", "availableLanguage": ["en", "hi", "mr"]}],
        "priceRange": "₹₹",
        "address": {"@type": "PostalAddress",
                    "streetAddress": "Shop No. A-19, Aareshwar Society, Opp. Dheeraj Darshan, Kokan Nagar Road, Near Kokan Hospital",
                    "addressLocality": "Jogeshwari East, Mumbai", "addressRegion": "Maharashtra",
                    "postalCode": "400060", "addressCountry": "IN"},
        "areaServed": ["Jogeshwari East", "Kokan Nagar", "Poonam Nagar", "Andheri East"],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
             "opens": "11:00", "closes": "14:30"},
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
             "opens": "17:30", "closes": "21:00"}],
        "founder": {"@type": "Person", "name": "Dr. Tejas Pradhan", "jobTitle": "Dentist"},
        "availableService": [{"@type": "MedicalProcedure", "name": n} for n in SERVICES_LD],
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": "Wheelchair-accessible entrance", "value": True},
            {"@type": "LocationFeatureSpecification", "name": "Parking", "value": True},
            {"@type": "LocationFeatureSpecification", "name": "Digital RVG X-ray", "value": True}],
        "sameAs": [],
    }
    if CLINIC_IMAGES:
        dentist["image"] = [f'{BASE}/{i["url"]}' for i in CLINIC_IMAGES]
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                          for q, a in HOME_FAQS]}
    og_img = f'<meta property="og:image" content="{BASE}/{hero_img["url"]}">\n' if hero_img else ""

    if hero_img:
        hero_open, hero_bg = '<section class="hero">', img_tag(hero_img, lazy=False, cls="bg")
    else:
        hero_open, hero_bg = '<section class="hero plain">', WATERMARK
    dr_block = f'<div class="dr">{img_tag(doctor_img)}</div>' if doctor_img else ""
    gal = ""
    if gallery:
        gal = ('<section class="sec alt" id="clinic"><div class="wrap"><p class="kick">The clinic</p><h2>Inside the clinic</h2>'
               '<div class="gal">' + "".join(
                   f'<figure>{img_tag(i)}<figcaption>{e(i["caption"])}</figcaption></figure>' for i in gallery)
               + "</div></div></section>")
    faqs = "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in HOME_FAQS)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON}<title>{e(CLINIC)} | Dentist in Jogeshwari East, Mumbai</title>
<meta name="description" content="{e(CLINIC)}, Kokan Nagar Road, near Kokan Hospital, Jogeshwari East, Mumbai 400060. Root canal, extraction, scaling, crowns, dentures, implants, braces and aligners.">
<link rel="canonical" href="{BASE}/">
<meta property="og:title" content="{e(CLINIC)}, Jogeshwari East">
<meta property="og:description" content="Family dental clinic on Kokan Nagar Road, Jogeshwari East, Mumbai.">
<meta property="og:type" content="website">
{og_img}<script type="application/ld+json">{json.dumps(dentist, ensure_ascii=False, indent=1)}</script>
<script type="application/ld+json">{json.dumps(faq, ensure_ascii=False, indent=1)}</script>
<style>{CSS}</style>
</head>
<body>
{topbar(True)}
{hero_open}
  {hero_bg}
  <div class="wrap">
    <p class="kick" style="color:#d9c8b8">Family dental clinic · Jogeshwari East, Mumbai</p>
    <h1>{e(CLINIC)}</h1>
    <p>Check-ups, root canals, implants, braces and aligners on Kokan Nagar Road, near Kokan Hospital. Clear explanations and costs before any treatment starts.</p>
    <div class="cta">
      <a class="btn" href="{WA}">Book an appointment</a>
      <a class="btn o" href="tel:+918369187806">Call {PHONE}</a>
    </div>
  </div>
</section>

<div class="stats"><div class="wrap">
  <div><div class="num">{RATING} ★</div><span>Google rating · {REVIEWS} reviews</span></div>
  <div><div class="num">6 days</div><span>Open Monday to Saturday</span></div>
  <div><div class="num">{len(PAGES)}</div><span>Treatments offered</span></div>
  <div><div class="num">RVG</div><span>Digital X-ray at the clinic</span></div>
</div></div>

<section class="sec" id="about"><div class="wrap">
  <div class="about{' has-dr' if doctor_img else ''}">
    {dr_block}
    <div>
      <p class="kick">About the clinic</p>
      <h2>Careful dental care for the whole family</h2>
      <p>{e(CLINIC)} is a family dental practice in Jogeshwari East, Mumbai, led by Dr. Tejas Pradhan (Maharashtra State Dental Council Reg. No. A-20222). Families from Kokan Nagar, Poonam Nagar and Andheri East come here for check-ups, root canals, extractions, crowns, dentures, implants and orthodontic treatment.</p>
      <p>The clinic uses digital RVG X-rays and sterilises every instrument before each patient. Treatment plans and costs are explained before any work begins.</p>
    </div>
  </div>
</div></section>

<section class="sec alt" id="services"><div class="wrap">
  <p class="kick">Treatments</p><h2>What we treat</h2>
  {tlist()}
</div></section>

<section class="sec" id="approach"><div class="wrap">
  <p class="kick">Our approach</p><h2>How every visit works</h2>
  <div class="ap">
    <div><div class="num">01</div><h3>Examine first</h3><p>Every treatment starts with an examination and, where needed, a digital RVG X-ray, so the plan is based on what we see.</p></div>
    <div><div class="num">02</div><h3>Explain clearly</h3><p>Treatment plans and costs are explained before any work begins, so there are no surprises.</p></div>
    <div><div class="num">03</div><h3>Treat safely</h3><p>Every instrument is sterilised before each patient, and treatment is done under local anaesthesia where needed.</p></div>
  </div>
</div></section>

{gal}
<section class="sec alt" id="guides"><div class="wrap">
  <p class="kick">Patient guides</p><h2>Guides and aftercare</h2>
  {guides_list()}
</div></section>

<section class="sec" id="timings"><div class="wrap narrow">
  <p class="kick">Timings</p><h2>Clinic timings</h2>
  <table>
    <tr><td>Monday – Saturday</td><td>11:00 am – 2:30 pm<br>5:30 pm – 9:00 pm</td></tr>
    <tr><td>Sunday</td><td>Closed</td></tr>
  </table>
  <p class="muted">Appointments recommended. Call or WhatsApp {PHONE} or {PHONE2}.</p>
</div></section>

<section class="sec alt" id="location"><div class="wrap two">
  <div>
    <p class="kick">Location</p><h2>Find the clinic</h2>
    <p>{e(ADDR)}</p>
    <p><a href="{MAPS}">Open in Google Maps</a></p>
    <p class="muted">Wheelchair-accessible entrance · Parking available · Cash, UPI and card/NFC accepted</p>
  </div>
  <iframe loading="lazy" title="Map to {e(CLINIC)}"
    src="https://www.google.com/maps?q=Dr+Tejas+Pradhan's+Dental+Clinic,+Kokan+Nagar,+Jogeshwari+East,+Mumbai&amp;output=embed"></iframe>
</div></section>

<section class="sec" id="faq"><div class="wrap narrow faq">
  <p class="kick">Questions</p><h2>Frequently asked questions</h2>
  {faqs}
</div></section>

<section class="sec contact" id="contact"><div class="wrap">
  <p class="kick">Contact</p><h2>Book your visit</h2>
  <p>Call or WhatsApp, and we will confirm your appointment.</p>
  <p><a href="tel:+918369187806">{PHONE}</a> · <a href="tel:+919167511565">{PHONE2}</a></p>
  <div class="cta"><a class="btn" href="{WA}">WhatsApp us</a><a class="btn o" href="{MAPS}">Directions</a></div>
</div></section>
{footer()}
{bottom_bar()}
{SCRIPT}
</body>
</html>
"""


# ---------------------------------------------------------------- educational videos (YouTube, checked embeddable)
VIDEOS = {
    "root-canal": ("vW1q2IT-FJA", "Root canal treatment step by step (animation)", "LA Endodontics, Dr Gabreal Shamtoub DDS"),
    "clear-aligners": ("3zC43XlEplw", "What are clear aligners?", "Healthy Habit Dental Care"),
    "braces": ("PWSqEdyizl8", "How do braces work?", "Peekaboo Kidz (The Dr. Binocs Show)"),
    "dental-implants": ("YdIlM0j0dpE", "Dental implants: step-by-step procedure (animation)", "Dr Jignesh Mehta"),
    "tooth-extraction": ("xe-ZVqSGvSE", "Wisdom tooth removal explained: causes, procedure, recovery", "Doctor O'Donovan"),
    "scaling-cleaning": ("r1-od_bc6z8", "What is dental scaling or teeth cleaning?", "Brace Dental Clinic"),
    "crowns-bridges": ("R7XvHJnoxdY", "Tooth crowns: step by step (animation)", "amatterofteeth"),
    "dentures": ("8srCshjp0ww", "How dentures are made", "Insider Science"),
    "teeth-whitening": ("5VVtzd0guas", "How tooth whitening works", "American Dental Association (ADA)"),
    "fillings": ("ie4GQzqyW98", "Cavity filling animation", "DentalVision3D Animation"),
    "implant-overdenture": ("uC01wG-Vvno", "What is an overdenture? What is a snap-in denture?", "Very Nice Smile Dental"),
    "all-on-4-implants": ("IW4VFtb7OHU", "All-on-4 procedure animation", "Shor Dental"),
    "childrens-dentistry": ("9HxUqnYWTk8", "What to expect at your child's first dental visit", "DeltaDentalAZ"),
}


def video_section(slug):
    v = VIDEOS.get(slug)
    if not v:
        return ""
    vid, title, who = v
    return (f'<h2 style="margin-top:36px">Watch: how it works</h2>'
            f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{e(title)}" loading="lazy" '
            f'allow="accelerometer; encrypted-media; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" '
            f'allowfullscreen></iframe></div>'
            f'<p class="muted">{e(title)}, by {e(who)}. <a href="https://www.youtube.com/watch?v={vid}" rel="noopener">Watch on YouTube</a>. '
            f'This is a general educational video and was not made by this clinic. Your own treatment may differ.</p>')


# ---------------------------------------------------------------- treatment pages
def page(p):
    url = f'{BASE}/{p["slug"]}.html'
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in p["faqs"]]}
    page_ld = {"@context": "https://schema.org", "@type": "MedicalWebPage", "url": url, "name": p["title"],
               "inLanguage": "en-IN", "about": {"@type": "MedicalProcedure", "name": p["name"]},
               "provider": {"@id": f"{BASE}/#clinic"},
               "audience": {"@type": "PeopleAudience",
                            "geographicArea": {"@type": "Place", "name": "Jogeshwari East, Mumbai"}},
               "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                   {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
                   {"@type": "ListItem", "position": 2, "name": p["name"], "item": url}]}}
    desc = p["intro"][:155].rsplit(" ", 1)[0] + "…"
    signs = "".join(f"<li>{e(s)}</li>" for s in p["signs"])
    steps = "".join(f"<li>{e(s)}</li>" for s in p["steps"])
    faqs = "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in p["faqs"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON}<title>{e(p["title"])} | {e(CLINIC)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<script type="application/ld+json">{json.dumps(page_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
{topbar(False)}
<section class="hero plain sm">
  {WATERMARK}
  <div class="wrap">
    <div class="crumb"><a href="index.html">Home</a> › {e(p["name"])}</div>
    <p class="kick" style="color:#d9c8b8">Treatment</p>
    <h1>{e(p["title"])}</h1>
    <p>{e(CLINIC)}, Kokan Nagar Road, Jogeshwari East</p>
    <div class="cta"><a class="btn" href="{WA}">Book an appointment</a><a class="btn o" href="tel:+918369187806">Call {PHONE}</a></div>
  </div>
</section>
<section class="sec"><div class="wrap narrow">
<h2>About {e(p["name"].lower())}</h2><p>{e(p["intro"])}</p>
<h2 style="margin-top:36px">{e(p["signs_title"])}</h2><ul class="b">{signs}</ul>
<h2 style="margin-top:36px">What to expect</h2><ol class="b">{steps}</ol>
{video_section(p["slug"])}
{related_block(p["slug"])}
</div></section>
<section class="sec alt"><div class="wrap narrow faq">
<h2>{e(p["name"])}: questions</h2>{faqs}
</div></section>
<section class="sec"><div class="wrap narrow">
<h2>Visit the clinic</h2>
<p>{e(ADDR)}</p>
<p>Monday to Saturday, 11 am – 2:30 pm and 5:30 pm – 9 pm. Closed Sunday. Appointments recommended: call or WhatsApp {PHONE} or {PHONE2}.</p>
<p>Dr. Tejas Pradhan, Maharashtra State Dental Council Reg. No. A-20222. <a href="{MAPS}">Open in Google Maps</a></p>
<p class="muted">This page gives general information. Your treatment is decided after an examination at the clinic.</p>
</div></section>
<section class="sec alt"><div class="wrap"><p class="kick">More</p><h2>Other treatments</h2>{tlist(p["slug"])}</div></section>
{footer()}
{bottom_bar()}
{SCRIPT}
</body>
</html>
"""


# ---------------------------------------------------------------- patient guides (extra pages)
def vid_block(v, heading=None, open_=True):
    vid, title, who = v
    h = f'<h2 style="margin-top:36px">{e(heading)}</h2>' if heading else ""
    return (f'{h}<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{e(title)}" loading="lazy" '
            f'allow="accelerometer; encrypted-media; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" '
            f'allowfullscreen></iframe></div>'
            f'<p class="muted">{e(title)}, by {e(who)}. <a href="https://www.youtube.com/watch?v={vid}" rel="noopener">Watch on YouTube</a>. '
            f'General educational video by a third party, not made by this clinic. Your own treatment may differ.</p>')


def guide_page(slug, title, h1, kick, desc, body, faqs=None):
    url = f"{BASE}/{slug}.html"
    ld = {"@context": "https://schema.org", "@type": "MedicalWebPage", "url": url, "name": title,
          "inLanguage": "en-IN", "provider": {"@id": f"{BASE}/#clinic"},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
              {"@type": "ListItem", "position": 2, "name": h1, "item": url}]}}
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    faq_html = ""
    if faqs:
        fld = {"@context": "https://schema.org", "@type": "FAQPage",
               "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
        ld_html += f'<script type="application/ld+json">{json.dumps(fld, ensure_ascii=False)}</script>'
        qa = "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faqs)
        faq_html = f'<section class="sec alt"><div class="wrap narrow faq"><h2>Questions</h2>{qa}</div></section>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON}<title>{e(title)} | {e(CLINIC)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{ld_html}
<style>{CSS}</style>
</head>
<body>
{topbar(False)}
<section class="hero plain sm">
  {WATERMARK}
  <div class="wrap">
    <div class="crumb"><a href="index.html">Home</a> › {e(h1)}</div>
    <p class="kick" style="color:#d9c8b8">{e(kick)}</p>
    <h1>{e(title)}</h1>
    <p>{e(CLINIC)}, Kokan Nagar Road, Jogeshwari East</p>
    <div class="cta"><a class="btn" href="{WA}">Book an appointment</a><a class="btn o" href="tel:+918369187806">Call {PHONE}</a></div>
  </div>
</section>
<section class="sec"><div class="wrap narrow">
{body}
</div></section>
{faq_html}
<section class="sec"><div class="wrap narrow">
<h2>Visit the clinic</h2>
<p>{e(ADDR)}</p>
<p>Monday to Saturday, 11 am – 2:30 pm and 5:30 pm – 9 pm. Closed Sunday. Call or WhatsApp {PHONE} or {PHONE2}.</p>
<p class="muted">General information only. Follow the instructions your own dentist gives you, and treatment is decided after an examination.</p>
</div></section>
<section class="sec alt"><div class="wrap"><p class="kick">More</p><h2>Treatments</h2>{tlist()}</div></section>
{footer()}
{bottom_bar()}
{SCRIPT}
</body>
</html>
"""


def ul(items):
    return '<ul class="b">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


def ol(items):
    return '<ol class="b">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ol>"


def chart_img(stem, alt):
    i = next((x for x in IMAGES if x["stem"] == stem), None)
    if not i:
        return ""
    return f'<figure class="chart"><a href="{i["url"]}"><img src="{i["url"]}" alt="{e(alt)}" loading="lazy" decoding="async"></a><figcaption class="muted">Tap the chart to open it full size. You can save it or share it on WhatsApp.</figcaption></figure>'


# ---- post-extraction care
EXTRACTION_FAQS = [
    ("How long should I bite on the gauze after tooth extraction?", "Bite firmly on the gauze for 30 to 45 minutes. If bleeding continues, place a fresh folded gauze and bite again for another 30 minutes."),
    ("When can I eat after a tooth extraction?", "Wait until the numbness wears off, then eat soft, cool or lukewarm food for 24 to 48 hours. Avoid hard, hot and spicy food."),
    ("What is a dry socket?", "A dry socket happens when the blood clot is lost from the socket, usually 2 to 4 days after extraction. It causes severe pain that medicines do not relieve. Contact your dentist if this happens."),
    ("When can I brush my teeth after extraction?", "Brush the rest of your teeth as usual from the same evening, but keep the brush away from the extraction site for the first day. Rinse gently with warm salt water from the next day."),
]


def extraction_page():
    body = (
        '<h2>Post-extraction instructions</h2>'
        '<p>Follow these steps for a smooth and speedy recovery after a tooth extraction or wisdom tooth removal. '
        'The chart below is in English and Marathi.</p>'
        + chart_img("guide-post-extraction", "Post extraction instructions chart in English and Marathi: bite on gauze, avoid rinsing, avoid hot food, avoid smoking and alcohol, take medicines, rest")
        + '<h2 style="margin-top:36px">What to do</h2>'
        + ol(["Bite firmly on the gauze for 30 to 45 minutes to stop bleeding.",
              "Do not spit, rinse your mouth or use a straw for 24 hours. This can dislodge the clot and restart bleeding.",
              "Eat soft, cool or lukewarm food for 24 to 48 hours. Avoid hard, spicy and hot food.",
              "Do not smoke or drink alcohol for at least 48 to 72 hours. It delays healing and can cause complications.",
              "Take your medicines on time as your dentist advised. Do not stop or skip them.",
              "Rest, avoid heavy physical activity for 24 to 48 hours, and keep your head slightly raised when sleeping.",
              "For swelling, hold a cold pack on the outside of the cheek, 10 minutes on and 10 minutes off, during the first 24 hours.",
              "From the next day, rinse gently with warm salt water after meals."])
        + '<h2 style="margin-top:36px">Normal healing</h2>'
        + ul(["Mild pain and swelling for 2 to 3 days", "Slight oozing of blood in the first 24 hours", "Bruising of the cheek or jaw may occur"])
        + '<h2 style="margin-top:36px">Contact your dentist if you have</h2>'
        + ul(["Heavy or continuous bleeding", "Severe pain that medicines do not relieve", "Swelling that increases after 2 to 3 days", "Fever, pus, a bad taste or any other unusual symptom"])
        + f'<p>Call or WhatsApp <b>{PHONE}</b> or {PHONE2}.</p>'
        + vid_block(("4mEEl2r-BHg", "Post-operative care after tooth extraction and dental implant surgery", "Vraj Group Of Dental Clinics"), "Watch: aftercare explained")
        + '<p>Related: <a href="tooth-extraction.html">Tooth extraction and wisdom teeth</a> · <a href="post-implant-care.html">Post-implant surgery care</a></p>')
    return guide_page("post-extraction-care", "Post-Extraction Care: Instructions and Chart", "Post-extraction care", "Patient guide",
                      "What to do after a tooth extraction: bite on gauze, avoid rinsing and straws for 24 hours, soft cool food, no smoking, medicines, normal healing and when to call the dentist.",
                      body, EXTRACTION_FAQS)


# ---- post-implant care
IMPLANT_FAQS = [
    ("What can I eat after dental implant surgery?", "Soft, cool or lukewarm food such as curd rice, dal, khichdi, banana and smoothies without a straw. Chew on the other side and avoid hard, hot or spicy food for the first 1 to 2 weeks, or as your dentist advises."),
    ("Is swelling normal after implant surgery?", "Yes. Mild swelling and soreness usually peak around day 2 or 3 and then settle. Cold packs in the first 24 to 48 hours help. Swelling that keeps increasing after day 3 needs a dentist's review."),
    ("When can I smoke after implant surgery?", "Smoking delays healing and raises the risk of implant failure. Avoid it completely during healing, and ideally stop for good."),
    ("When will the stitches be removed?", "Usually after about 7 to 10 days, at a follow-up visit. Your dentist will tell you the exact day."),
]


def implant_page():
    body = (
        '<h2>Post-implant surgery instructions</h2>'
        '<p>The first days after implant surgery decide how smoothly the implant heals. The chart below is in English and Marathi.</p>'
        + chart_img("guide-post-implant", "Post implant surgery care chart in English and Marathi")
        + '<h2 style="margin-top:36px">What to do</h2>'
        + ol(["Bite firmly on the gauze for 30 to 45 minutes. A little oozing of blood on day 1 is normal.",
              "Use a cold pack on the cheek, 10 minutes on and 10 minutes off, for the first 24 to 48 hours.",
              "Do not spit, rinse or use a straw for the first 24 hours.",
              "Eat soft, cool food and chew on the other side. Avoid hard, hot and spicy food for 1 to 2 weeks, or as advised.",
              "Do not smoke or drink alcohol. Smoking delays healing and can make the implant fail.",
              "Take antibiotics and painkillers exactly as prescribed, and finish the course.",
              "From day 2, rinse gently with warm salt water or the mouthwash prescribed, after meals. Brush your other teeth as usual and keep the surgical area gentle.",
              "Rest for 2 to 3 days, avoid heavy exercise for about a week, and sleep with your head raised.",
              "Do not pull your lip or cheek to look at the site, and do not press on it with your tongue or finger.",
              "Come for your follow-up visit and stitch removal as advised, usually after 7 to 10 days."])
        + '<h2 style="margin-top:36px">Normal healing</h2>'
        + ul(["Mild pain and swelling for 2 to 3 days", "Slight bleeding or oozing in the first 24 hours", "Bruising of the face or neck in some patients"])
        + '<h2 style="margin-top:36px">Contact your dentist if you have</h2>'
        + ul(["Bleeding that does not stop with firm pressure", "Severe pain not relieved by medicines", "Swelling that increases after day 3", "Fever, pus or a bad taste", "An implant or cover screw that feels loose", "Numbness that does not go away"])
        + f'<p>Call or WhatsApp <b>{PHONE}</b> or {PHONE2}.</p>'
        + vid_block(("7ZxzBWV2bt8", "Dental implants: aftercare advice", "Bupa Dental Care"), "Watch: implant aftercare")
        + '<p>Related: <a href="dental-implants.html">Dental implants</a> · <a href="implant-overdenture.html">Implant overdenture</a> · <a href="all-on-4-implants.html">All-on-4 implants</a></p>')
    return guide_page("post-implant-care", "Post-Implant Surgery Care: Instructions, Chart and Video", "Post-implant care", "Patient guide",
                      "Aftercare for dental implant surgery: gauze, cold pack, soft food, no smoking, medicines, cleaning, normal healing and when to call your dentist. Chart in English and Marathi.",
                      body, IMPLANT_FAQS)


# ---- braces comparison
def braces_svg(kind):
    teeth = ""
    op = ".55" if kind == "lingual" else "1"
    for k in range(6):
        x = 10 + k * 47
        teeth += f'<rect x="{x}" y="30" width="40" height="62" rx="15" fill="#fbf8f3" stroke="#cfc4b6" stroke-width="1.5" opacity="{op}"/>'
    br = ""
    for k in range(6):
        cx = 30 + k * 47
        if kind == "metal":
            br += (f'<circle cx="{cx}" cy="61" r="9" fill="none" stroke="#3b6ea5" stroke-width="2.5"/>'
                   f'<rect x="{cx-7}" y="54" width="14" height="14" rx="2" fill="#aab2ba" stroke="#6b7580"/>')
        elif kind == "ceramic":
            br += f'<rect x="{cx-7}" y="54" width="14" height="14" rx="2" fill="#f1eadc" stroke="#cdbfa8"/>'
        elif kind == "self-ligating":
            br += (f'<rect x="{cx-8}" y="53" width="16" height="16" rx="2" fill="#aab2ba" stroke="#6b7580"/>'
                   f'<rect x="{cx-4}" y="58" width="8" height="6" rx="1" fill="#e9edf0"/>')
        elif kind == "lingual":
            br += f'<rect x="{cx-7}" y="54" width="14" height="14" rx="2" fill="none" stroke="#6b7580" stroke-dasharray="3 2"/>'
    wire = ""
    if kind in ("metal", "self-ligating"):
        wire = '<path d="M12 61H288" stroke="#6b7580" stroke-width="2"/>'
    elif kind == "ceramic":
        wire = '<path d="M12 61H288" stroke="#d6cfc2" stroke-width="2"/>'
    elif kind == "lingual":
        wire = '<path d="M12 61H288" stroke="#6b7580" stroke-width="1.5" stroke-dasharray="3 2"/>'
    over = ""
    if kind == "aligner":
        over = '<rect x="4" y="24" width="292" height="74" rx="30" fill="#7fa8d1" fill-opacity=".18" stroke="#7fa8d1" stroke-width="2"/>'
    lab = {"lingual": "braces sit behind the teeth", "aligner": "clear removable tray"}.get(kind, "")
    t = f'<text x="150" y="112" text-anchor="middle" font-size="10" fill="#6b645c" font-family="system-ui,sans-serif">{lab}</text>' if lab else ""
    return (f'<svg viewBox="0 0 300 120" role="img" aria-label="Illustration of {kind.replace("-", " ")}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="300" height="120" fill="#f1ece4"/>{teeth}{wire}{br}{over}{t}</svg>')


BRACE_TYPES = [
    ("metal", "Metal braces",
     ["Stainless-steel brackets joined by a wire, held with small coloured or clear elastic ties.",
      "Look: most visible, though coloured ties make them fun for children.",
      "Handles almost every case, including complex bites.",
      "Usually the lowest cost of the options."],
     ("PWSqEdyizl8", "How do braces work?", "Peekaboo Kidz (The Dr. Binocs Show)")),
    ("ceramic", "Ceramic (clear) braces",
     ["Tooth-coloured or clear brackets with a tooth-coloured wire.",
      "Look: much less noticeable than metal, up close they are still visible.",
      "Brackets are a little larger and more brittle, and elastic ties can stain if oral hygiene is poor.",
      "Costs more than metal braces."],
     ("8Wo3bqgWgSM", "Clear braces vs. metal braces: what type works best?", "Premier Orthodontics")),
    ("self-ligating", "Self-ligating braces",
     ["Brackets with a built-in clip or door, so no elastic ties are needed.",
      "Can be metal or ceramic. Easier to keep clean, and appointments are often shorter.",
      "Research has not shown a clear difference in treatment time compared with conventional braces.",
      "Costs more than conventional braces."],
     ("tUe3y-mG6O4", "Damon braces vs. regular braces: what's the difference?", "Dr. Jamilian Orthodontic Clinic")),
    ("lingual", "Lingual braces",
     ["Brackets fixed to the back (tongue side) of the teeth, so they are hidden from view.",
      "Can feel bulky at first, affect speech briefly and irritate the tongue.",
      "Harder to clean, appointments take longer and fewer orthodontists offer them.",
      "Usually the highest cost."],
     ("e-UNMUY8z40", "Lingual braces: pros, cons, process and cost", "Bhatia Dentopulse (Dr. Srishti Bhatia)")),
    ("aligner", "Clear aligners",
     ["A series of clear, removable plastic trays, changed every 1 to 2 weeks.",
      "Worn about 20 to 22 hours a day. Remove them to eat, drink and brush, so there are no food restrictions.",
      "Best for mild to moderate crowding and gaps. Some complex movements need braces instead.",
      "Cost is usually higher than metal braces and depends on the case."],
     ("3zC43XlEplw", "What are clear aligners?", "Healthy Habit Dental Care")),
]
BRACE_ROWS = [
    ("How visible", ["Most visible", "Less visible", "Visible (metal) or less (ceramic)", "Hidden behind teeth", "Almost invisible"]),
    ("Comfort", ["Cheek irritation at first, wax helps", "Similar to metal, brackets slightly larger", "Often a little gentler on adjustment", "Tongue irritation and speech change at first", "Pressure after each new tray"]),
    ("Cleaning", ["Brush and floss around brackets", "Same, and avoid staining foods", "Easier, no elastic ties to trap plaque", "Hardest to clean", "Easiest: trays come out"]),
    ("Food rules", ["Avoid sticky and hard foods", "Avoid sticky, hard and staining foods", "Avoid sticky and hard foods", "Avoid sticky and hard foods", "None while trays are out; brush before refitting"]),
    ("Complex cases", ["Suitable", "Suitable", "Suitable", "Suitable in expert hands", "Mild to moderate cases"]),
    ("Relative cost", ["Lowest", "Higher", "Higher", "Highest", "Higher, varies by case"]),
    ("Works best when", ["You want a dependable, economical option", "You want a discreet look and will keep teeth very clean", "You want shorter visits and easier cleaning", "Appearance matters most and you accept the extra effort", "You will wear the trays all day, every day"]),
]
BRACES_FAQS = [
    ("Which type of braces is best?", "There is no single best type. The right choice depends on your bite, age, how visible you want the braces to be, how well you can clean your teeth and your budget. The dentist advises after an examination."),
    ("Are self-ligating braces faster?", "Self-ligating braces are often marketed as faster, but studies have not shown a clear difference in treatment time. Their advantages are easier cleaning and shorter appointments."),
    ("Do lingual braces hurt your tongue?", "They can irritate the tongue and affect speech for the first few weeks. Most people adapt."),
    ("Can clear aligners fix every problem?", "No. Aligners work well for mild to moderate crowding, spacing and some bite problems. Complex cases may need braces."),
    ("How much do braces cost in Mumbai?", "The cost depends on the type of braces and the case. You get an estimate after the examination and X-rays, before treatment starts."),
]


def braces_page():
    cards, rows_head = "", "".join(f"<th>{e(n)}</th>" for _, n, _, _ in BRACE_TYPES)
    for kind, name, pts, vid in BRACE_TYPES:
        ph = next((i for i in IMAGES if i["base"] == f"ortho-{kind}"), None)
        visual = img_tag(ph) if ph else braces_svg(kind)
        note = "Example case" if ph else "Illustration"
        cards += (f'<div class="card"><div class="ph">{visual}</div><div class="cb"><p class="kick">{note}</p>'
                  f'<h3 class="sf" style="margin-top:4px">{e(name)}</h3>{ul(pts)}'
                  f'<details class="dv"><summary>Watch a video</summary>{vid_block(vid)}</details></div></div>')
    rows = ""
    for label, vals in BRACE_ROWS:
        rows += f"<tr><td>{e(label)}</td>" + "".join(f"<td>{e(v)}</td>" for v in vals) + "</tr>"
    body = (
        '<h2>Braces and aligners compared</h2>'
        '<p>Metal, ceramic, self-ligating and lingual braces, and clear aligners all straighten teeth, but they differ in how they look, feel and are cared for. '
        'Here they are side by side. Your dentist will recommend one after examining your teeth and bite.</p>'
        '</div><div class="wrap"><div class="cards">' + cards + '</div></div><div class="wrap narrow">'
        '<h2 style="margin-top:36px">Comparison table</h2><p class="muted">Swipe sideways to see all columns. Cost is shown only as relative; exact cost is given after examination.</p>'
        f'<div class="cmpw"><table class="cmp"><thead><tr><th></th>{rows_head}</tr></thead><tbody>{rows}</tbody></table></div>'
        + vid_block(("iGuP5ZWOHdI", "Braces or Invisalign? Which is better (metal, ceramic, lingual and aligners compared)", "Teeth Talk Girl"), "Watch: all the options compared")
        + '<p>Related: <a href="braces.html">Braces</a> · <a href="clear-aligners.html">Clear aligners</a> · <a href="brushing-technique.html">Brushing with braces</a></p>')
    return guide_page("braces-comparison", "Types of Braces Compared: Metal, Ceramic, Self-Ligating, Lingual and Aligners",
                      "Braces compared", "Orthodontics",
                      "Compare metal, ceramic, self-ligating and lingual braces and clear aligners: looks, comfort, cleaning, food rules, suitability and relative cost, with videos.",
                      body, BRACES_FAQS)


# ---- brushing
BRUSH_FAQS = [
    ("How long should I brush my teeth?", "Brush for two minutes, twice a day, with a fluoride toothpaste. Spend about 30 seconds on each quarter of the mouth."),
    ("Should I rinse after brushing?", "Spit out the extra toothpaste but do not rinse with water, so the fluoride keeps working on your teeth."),
    ("Is a hard toothbrush better?", "No. Use a soft brush. Hard bristles and heavy pressure can wear the enamel and make gums recede."),
    ("How often should I change my toothbrush?", "Every 3 months, or sooner if the bristles are splayed."),
    ("How do I brush with braces?", "Brush after every meal, angle the brush above and below the brackets, and use an interdental brush for the spaces under the wire."),
]


def brushing_svg():
    return ('<svg viewBox="0 0 300 150" role="img" aria-label="Toothbrush held at 45 degrees to the gum line" xmlns="http://www.w3.org/2000/svg">'
            '<rect width="300" height="150" fill="#f1ece4"/>'
            '<path d="M40 120V55c0-22 16-38 36-38s36 16 36 38v65z" fill="#fbf8f3" stroke="#cfc4b6" stroke-width="2"/>'
            '<path d="M20 118c40-14 100-14 140 0v30H20z" fill="#e6a9a0"/>'
            '<g transform="rotate(-45 150 100)"><rect x="150" y="96" width="120" height="9" rx="4" fill="#143550"/>'
            '<rect x="108" y="88" width="46" height="9" rx="2" fill="#7fa8d1"/></g>'
            '<path d="M70 105l-14 22" stroke="#6b645c" stroke-width="1.5" stroke-dasharray="3 2"/>'
            '<text x="200" y="40" font-size="11" fill="#1d1a17" font-family="system-ui,sans-serif">Bristles at 45°</text>'
            '<text x="200" y="56" font-size="11" fill="#1d1a17" font-family="system-ui,sans-serif">towards the gum line</text></svg>')


def brushing_page():
    body = (
        '<h2>Brushing technique</h2>'
        '<p>Most people brush for long enough but miss the area where teeth meet the gums. The Modified Bass technique is the method dentists most often recommend because it cleans just under the gum edge, where plaque causes gum disease.</p>'
        f'<div class="card" style="margin:18px 0"><div class="ph">{brushing_svg()}</div></div>'
        '<h2 style="margin-top:36px">Step by step</h2>'
        + ol(["Use a soft toothbrush and a pea-sized amount of fluoride toothpaste.",
              "Place the bristles at a 45-degree angle, pointing towards the gum line.",
              "Move the brush in very small, gentle back-and-forth vibrations, covering 2 to 3 teeth at a time, about 10 strokes each.",
              "Work around the outside surfaces of all the teeth, top and bottom.",
              "Repeat on the inside surfaces. For the inner side of the front teeth, tilt the brush upright and use the tip with short up-and-down strokes.",
              "Brush the chewing surfaces with a light back-and-forth scrub.",
              "Gently brush the tongue to remove bacteria that cause bad breath.",
              "Spit out the extra toothpaste and do not rinse with water."])
        + '<h2 style="margin-top:36px">Good habits</h2>'
        + ul(["Brush twice a day for two minutes, and always before bed.", "Do not press hard. Light pressure cleans as well and protects the gums.",
              "Clean between the teeth once a day with floss or interdental brushes, because a brush cannot reach there.",
              "Change your brush every 3 months.", "Wait about 30 minutes after acidic food or drinks before brushing."])
        + '<h2 style="margin-top:36px">If you have braces, implants or dentures</h2>'
        + ul(["Braces: brush after every meal, angle the brush above and below the brackets, and use an interdental brush under the wire.",
              "Implants and All-on-4 teeth: use a soft brush, and clean under the bridge with interdental brushes or a water flosser.",
              "Overdentures and dentures: remove them, brush them with a denture brush and soap, and leave them out at night."])
        + '<h2 style="margin-top:36px">Children</h2>'
        + '<p>Parents should help children brush until about age 7 or 8. Use a smear of fluoride toothpaste for under 3 years and a pea-sized amount after that.</p>'
        + vid_block(("VdjmGxq-X7M", "The best way to brush your teeth: Modified Bass technique", "Dentalk!"), "Watch: Modified Bass technique")
        + '<p>Related: <a href="scaling-cleaning.html">Scaling and cleaning</a> · <a href="braces-comparison.html">Braces compared</a> · <a href="childrens-dentistry.html">Children\'s dentistry</a></p>')
    return guide_page("brushing-technique", "How to Brush Your Teeth Properly: Modified Bass Technique", "Brushing technique", "Patient guide",
                      "Step-by-step brushing technique (Modified Bass): 45-degree angle, small gentle strokes, two minutes twice a day, tips for braces, implants and children, with video.",
                      body, BRUSH_FAQS)


# ---- photo guide illustrations (no real faces)
def _face(kind):
    skin, dark = "#e9c3a3", "#3b2a22"
    teeth = ('<path d="M76 128 Q100 150 124 128 Q100 134 76 128Z" fill="#fff"/>'
             '<path d="M84 130v5M92 132v6M100 133v6M108 132v6M116 130v5" stroke="#d8d0c4" stroke-width="1"/>')
    smile = ('<path d="M70 125 Q100 158 130 125 Q100 132 70 125Z" fill="#7a2f34"/>' + teeth +
             '<path d="M70 125 Q100 120 130 125" stroke="#b8545b" stroke-width="3" fill="none"/>'
             '<path d="M70 125 Q100 160 130 125" stroke="#b8545b" stroke-width="3" fill="none"/>')
    closed = '<path d="M76 130 Q100 142 124 130" stroke="#b8545b" stroke-width="4" fill="none" stroke-linecap="round"/>'
    mouth = closed if kind == "closed" else smile
    head = (f'<ellipse cx="100" cy="100" rx="52" ry="66" fill="{skin}"/>'
            f'<path d="M48 88 Q50 30 100 32 Q150 30 152 88 Q140 50 100 52 Q60 50 48 88Z" fill="{dark}"/>'
            f'<ellipse cx="80" cy="92" rx="6" ry="4" fill="{dark}"/><ellipse cx="120" cy="92" rx="6" ry="4" fill="{dark}"/>'
            f'<path d="M100 96 L94 114 Q100 118 106 114" stroke="#c49a7c" stroke-width="2" fill="none"/>{mouth}')
    if kind == "good":
        g = (head + '<path d="M100 20V190" stroke="#1f7a4d" stroke-width="1.5" stroke-dasharray="4 3"/>'
             '<path d="M30 130H170" stroke="#1f7a4d" stroke-width="1.5" stroke-dasharray="4 3"/>'
             '<rect x="6" y="176" width="112" height="16" fill="#fff" opacity=".85"/><text x="10" y="188" font-size="10" fill="#1f7a4d">camera at mouth level</text>'
             '<rect x="108" y="6" width="88" height="16" fill="#fff" opacity=".85"/><text x="112" y="18" font-size="10" fill="#1f7a4d">face straight on</text>')
        bg = "#eaf5ee"
    elif kind == "close":
        g = f'<g transform="translate(100 100) scale(2.1) translate(-100 -128)">{head}</g>'
        bg = "#eaf5ee"
    elif kind == "tilt":
        g = f'<g transform="rotate(-18 100 100) translate(10 0) scale(.92 1)">{head}</g>'
        bg = "#fdecec"
    elif kind == "closed":
        g = head
        bg = "#fdecec"
    else:
        g = (f'<g transform="translate(100 105) scale(.45) translate(-100 -100)">{head}</g>'
             '<rect width="200" height="200" fill="#000" opacity=".55"/><rect width="200" height="200" fill="#fff" opacity=".1" filter="url(#bl)"/>')
        bg = "#fdecec"
    return (f'<svg viewBox="0 0 200 200" role="img" xmlns="http://www.w3.org/2000/svg"><defs><filter id="bl"><feGaussianBlur stdDeviation="2"/></filter></defs>'
            f'<rect width="200" height="200" fill="{bg}"/><g{" filter=\"url(#bl)\"" if kind == "dark" else ""}>{g}</g></svg>')


def photo_guide():
    cards = [("close", True, "Best: close-up smile", "Nose to chin fills the photo, phone 20 to 30 cm away, straight on. Big smile so the upper teeth show. Do not zoom; move closer."),
             ("good", True, "Also fine: whole face", "Face straight on, phone at mouth level. The AI zooms in on your smile automatically."),
             ("tilt", False, "Avoid: tilted or side angle", "Head turned or tilted makes the teeth look uneven."),
             ("closed", False, "Avoid: teeth hidden", "Lips covering the teeth: the AI cannot see them."),
             ("dark", False, "Avoid: dark, far or blurry", "Too far away, at night or shaky. Stand facing a window in daylight.")]
    h = '<div class="pg">'
    for k, ok, t, d in cards:
        mark = '<span class="ok">✓</span>' if ok else '<span class="wn">✗</span>'
        h += f'<figure>{_face(k)}<figcaption><b>{mark} {t}</b><br>{d}</figcaption></figure>'
    h += '</div>'
    steps = ["Ask someone to take the photo, or use the back camera with a timer. A selfie at arm's length is fine too.",
             "Stand facing a window in daylight. Turn off flash, beauty mode, portrait mode and filters.",
             "Hold the phone straight, at the height of your mouth, not above or below.",
             "Look straight into the camera, relax, then give a big natural smile showing your upper teeth.",
             "Check the photo is sharp and your teeth are clearly visible before uploading."]
    return ('<h2 style="margin-top:28px">How to take the photo</h2>'
            '<p class="muted">Drawings for illustration. A good photo gives a much more accurate result.</p>' + h +
            '<ol class="b">' + "".join(f"<li>{e(s)}</li>" for s in steps) + '</ol>')


# ---- AI smile check
SMILE_API = "https://arxhbdyciylznmlamvri.supabase.co/functions/v1/smile-check"
SMILE_JS = r"""
(function(){
var API="__API__",NAMES=__NAMES__,WA="__WA__";
var f=document.getElementById('sc'),btn=document.getElementById('scb'),msg=document.getElementById('scm'),out=document.getElementById('sco'),inp=document.getElementById('scf'),prev=document.getElementById('scp');
function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}
function shrink(file){return new Promise(function(res,rej){var r=new FileReader();r.onerror=rej;r.onload=function(){var im=new Image();im.onerror=rej;im.onload=function(){var m=1024,w=im.width,h=im.height,k=Math.min(1,m/Math.max(w,h));var c=document.createElement('canvas');c.width=Math.round(w*k);c.height=Math.round(h*k);c.getContext('2d').drawImage(im,0,0,c.width,c.height);res(c.toDataURL('image/jpeg',0.8))};im.src=r.result};r.readAsDataURL(file)})}
inp.addEventListener('change',function(){prev.innerHTML='';var n=Math.min(inp.files.length,3);for(var i=0;i<n;i++){var u=URL.createObjectURL(inp.files[i]);prev.innerHTML+='<img src="'+u+'" alt="Selected photo '+(i+1)+'">'}if(inp.files.length>3){msg.textContent='Only the first 3 photos will be used.'}else{msg.textContent=''}});
f.addEventListener('submit',function(ev){ev.preventDefault();out.innerHTML='';msg.className='muted';
if(!inp.files.length){msg.textContent='Please add at least one photo.';return}
btn.disabled=true;btn.textContent='Checking, please wait...';msg.textContent='This takes about 10 to 20 seconds.';
var files=Array.prototype.slice.call(inp.files,0,3);
Promise.all(files.map(shrink)).then(function(imgs){
return fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:f.name.value,phone:f.phone.value,consent:f.consent.checked,website:f.website.value,images:imgs})})
}).then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})}).then(function(x){
btn.disabled=false;btn.textContent='Check my smile';
if(!x.ok||!x.j.result){msg.className='muted err';msg.textContent=(x.j&&x.j.error)||'Something went wrong. Please try again.';return}
msg.textContent='';show(x.j.result)}).catch(function(e){btn.disabled=false;btn.textContent='Check my smile';msg.className='muted err';msg.textContent='Could not complete the check ('+((e&&e.message)||e)+'). Please open this page in Chrome and try again, or WhatsApp the clinic.'})});
function show(r){var h='<div class="res"><h2>Your tentative result</h2>';
if(!r.photo_usable){h+='<p>'+esc(r.photo_note||'The photos were not clear enough to check.')+'</p><p>Please retake them in good light, with your teeth showing and the camera steady.</p>'}
else{if(r.urgency==='see_dentist_soon'){h+='<div class="warn"><b>Please see a dentist soon.</b> Something in your photos may need prompt attention.</div>'}
if(r.photo_note){h+='<p class="muted">'+esc(r.photo_note)+'</p>'}
if(r.observations.length){h+='<h3>What the AI noticed</h3><ul class="b">'+r.observations.map(function(o){return'<li>'+esc(o)+'</li>'}).join('')+'</ul>'}
if(r.possible_treatments.length){h+='<h3>Treatments you may want to ask about</h3><ul class="b">'+r.possible_treatments.map(function(t){return'<li><a href="'+t.slug+'.html">'+esc(NAMES[t.slug]||t.slug)+'</a>: '+esc(t.why)+'</li>'}).join('')+'</ul>'}
if(r.questions_to_ask_dentist.length){h+='<h3>Questions to ask the dentist</h3><ul class="b">'+r.questions_to_ask_dentist.map(function(o){return'<li>'+esc(o)+'</li>'}).join('')+'</ul>'}}
h+='<p class="muted"><b>This is not a diagnosis.</b> A photo cannot show cavities between teeth, bone or infection. Only an examination and X-ray can confirm what you need. Your photos have also been shared with Dr. Tejas Pradhan for review.</p>';
h+='<div class="cta"><a class="btn" href="'+WA+'">Book an exam on WhatsApp</a></div></div>';out.innerHTML=h;out.scrollIntoView({behavior:'smooth'})}
})();
"""


def smile_page():
    names = {p["slug"]: p["name"] for p in PAGES}
    js = (SMILE_JS.replace("__API__", SMILE_API).replace("__NAMES__", json.dumps(names))
          .replace("__WA__", "https://wa.me/918369187806?text=" + quote("Hello, I used the AI smile check on your website and would like to book an exam.")))
    body = (
        '<h2>Free AI smile check</h2>'
        '<p>Upload 1 to 3 clear photos of your teeth and get a quick, tentative overview and the treatments you may want to ask about. '
        'Dr. Tejas Pradhan can then review your photos, and you can book an exam if you wish.</p>'
        '<div class="note"><b>Please note:</b> this is an AI screening, not a diagnosis. A photo cannot show cavities between teeth, bone loss or infection. '
        'If you have severe pain, swelling or fever, do not wait: call the clinic.</div>'
        + photo_guide() +
        '<form id="sc" class="scf" autocomplete="on">'
        '<label>Your name<input name="name" required maxlength="80" autocomplete="name"></label>'
        '<label>Mobile number<input name="phone" required inputmode="numeric" maxlength="14" autocomplete="tel" placeholder="10-digit number"></label>'
        '<label>Photos of your teeth (1 to 3)<input id="scf" type="file" accept="image/*" multiple required></label>'
        '<div id="scp" class="prev"></div>'
        '<p class="muted">Tips: good daylight, smile with teeth showing, one photo from the front, one of the upper teeth and one of the lower teeth if possible.</p>'
        '<input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">'
        '<label class="ck"><input type="checkbox" name="consent" required> I agree that my photos and details are processed by an AI service (Google Gemini) and stored securely so that Dr. Tejas Pradhan can review them and contact me. '
        'I can ask the clinic to delete them at any time.</label>'
        '<button id="scb" class="btn" type="submit">Check my smile</button>'
        '<p id="scm" class="muted" role="status"></p></form>'
        '<div id="sco"></div>'
        f'<script>{js}</script>')
    faqs = [("Is the AI smile check free?", "Yes, it is free to use. There are daily limits, so if it is busy please try again tomorrow or WhatsApp the clinic."),
            ("Is the AI result a diagnosis?", "No. It is a tentative overview from photos. Only an examination and X-ray can confirm what treatment you need."),
            ("Who sees my photos?", "Your photos are processed by an AI service to produce the result and are stored securely for Dr. Tejas Pradhan to review. They are not shown publicly."),
            ("Can I get my photos deleted?", "Yes. Call or WhatsApp the clinic and ask for your photos and details to be deleted.")]
    return guide_page("smile-check", "Free AI Smile Check: Upload Photos of Your Teeth", "AI smile check", "AI tool",
                      "Upload photos of your teeth and get a tentative AI overview and the treatments to ask about. Not a diagnosis; reviewed by Dr. Tejas Pradhan.",
                      body, faqs)


# ---- AI digital smile design
DSD_API = "https://arxhbdyciylznmlamvri.supabase.co/functions/v1/smile-design"
DSD_JS = r"""
(function(){
var API="__API__",WA="__WA__",CLINIC="__CLINIC__",PHONE="__PHONE__";
var f=document.getElementById('ds'),btn=document.getElementById('dsb'),msg=document.getElementById('dsm'),out=document.getElementById('dso'),inp=document.getElementById('dsf'),prev=document.getElementById('dsp');
var ORDER=["UR4","UR3","UR2","UR1","UL1","UL2","UL3","UL4"],NUM={1:"Central incisor",2:"Lateral incisor",3:"Canine",4:"First premolar"};
var RATIOS={golden:0.618,red70:0.70,red75:0.75,red80:0.80};
// tooth-form library (visagism): [mesial corner, distal corner, incisal convexity] for centrals and laterals, neck narrowing, canine tip roundness, lateral-width tweak
var FORMS={oval:{n:'Oval (soft, rounded)',c:[0.16,0.32,0.035],l:[0.28,0.5,0.05],neck:0.04,tip:0.09,dr:0},
 triangular:{n:'Triangular (dynamic, youthful)',c:[0.07,0.2,0.012],l:[0.14,0.36,0.02],neck:0.13,tip:0.05,dr:-0.03},
 rectangular:{n:'Rectangular (strong, long)',c:[0.05,0.12,0],l:[0.1,0.24,0.01],neck:0.03,tip:0.04,dr:0},
 square:{n:'Square (calm, broad)',c:[0.05,0.1,0],l:[0.08,0.18,0],neck:0.01,tip:0.1,dr:0.06}};
var SHADES={a2:{c:[236,222,198],yr:0.15,lift:0.03},a1:{c:[241,233,216],yr:0.45,lift:0.07},b1:{c:[246,242,232],yr:0.7,lift:0.11},bl:{c:[251,250,246],yr:0.95,lift:0.17}};
var S={eyes:'off',clin:false,face:true,form:'oval',wh:0.78,a:null,after:null,img:null,W:0,H:0,ratio:'red70',shade:'a1',view:'mockup',outline:true,brace:'metal',cache:{}};
var beforeURL=null;
function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}
function avg(a){a=a.filter(function(v){return v!=null&&isFinite(v)});return a.length?a.reduce(function(p,q){return p+q},0)/a.length:null}
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function shrink(file){return new Promise(function(res,rej){var r=new FileReader();r.onerror=rej;r.onload=function(){var im=new Image();im.onerror=rej;im.onload=function(){var m=1280,w=im.width,h=im.height,k=Math.min(1,m/Math.max(w,h));var c=document.createElement('canvas');c.width=Math.round(w*k);c.height=Math.round(h*k);c.getContext('2d').drawImage(im,0,0,c.width,c.height);res(c.toDataURL('image/jpeg',0.88))};im.src=r.result};r.readAsDataURL(file)})}
if(inp)inp.addEventListener('change',function(){prev.innerHTML='';if(inp.files[0]){prev.innerHTML='<img src="'+URL.createObjectURL(inp.files[0])+'" alt="Selected smile photo">'}});
function loadFile(file){return new Promise(function(res,rej){var u=URL.createObjectURL(file),im=new Image();im.onload=function(){res(im)};im.onerror=rej;im.src=u})}
function toURL(im,sx,sy,sw,sh,maxW,q){var k=Math.min(maxW/sw,3);var c=document.createElement('canvas');c.width=Math.round(sw*k);c.height=Math.round(sh*k);var g=c.getContext('2d');g.imageSmoothingQuality='high';g.drawImage(im,sx,sy,sw,sh,0,0,c.width,c.height);return c.toDataURL('image/jpeg',q||0.88)}
function post(body){return fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})})}
/* ---------- guided camera (MediaPipe face landmarks) ---------- */
var CAM={stream:null,lm:null,raf:0,hold:0,lastT:0,lastNose:null,facing:'user',captured:null,ok:{},res:null,loading:false};
var MPV='https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14';
var HOLD=3000;
var CHECKS=[['zone','Smile in the zone'],['dist','Distance'],['straight','Head straight'],['smile','Teeth showing'],['light','Good light'],['steady','Hold still']];
function el(id){return document.getElementById(id)}
function camOpen(){
 if(!el('cam')){var d=document.createElement('div');d.id='cam';d.className='cam';
  d.innerHTML='<div class="camtop"><button type="button" id="camx" aria-label="Close camera">✕</button></div>'+
  '<div class="camstage" id="camstage"><video id="camv" playsinline muted autoplay></video><canvas id="camo"></canvas><div class="pill" id="campill">Starting camera…</div><div class="count" id="camcount"></div></div>'+
  '<div class="camtxt"><h3 id="camh">Smile inside the teeth zone</h3><p id="camp">Hold the phone at mouth level, 20 to 30 cm away. Fit your smile into the box with the tooth outlines.</p><div class="chips" id="camchips"></div></div>'+
  '<div class="cambar"><span></span><button type="button" id="camshot" class="shot" aria-label="Take photo"><svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="34" class="bg"/><circle cx="40" cy="40" r="34" class="pr" id="camring"/></svg></button><button type="button" id="camflip" aria-label="Switch camera">⟲</button></div>'+
  '<div class="camprev" id="camprev" hidden><img id="camimg" alt="Captured smile photo"><div class="cta"><button type="button" class="btn" id="camuse">Use this photo</button><button type="button" class="btn o2" id="camretake">Retake</button></div></div>';
  document.body.appendChild(d);
  el('camx').onclick=camClose;el('camshot').onclick=function(){camCapture(false)};
  el('camflip').onclick=function(){CAM.facing=CAM.facing=='user'?'environment':'user';camStart()};
  el('camretake').onclick=function(){el('camprev').hidden=true;el('cam').classList.remove('pv');el('camstage').hidden=false;camStart()};
  el('camuse').onclick=camUse}
 el('cam').hidden=false;el('camprev').hidden=true;el('cam').classList.remove('pv');el('camstage').hidden=false;document.body.style.overflow='hidden';
 el('camchips').innerHTML=CHECKS.map(function(c){return'<span id="ck_'+c[0]+'">'+c[1]+'</span>'}).join('');
 camStart();camLoadModel()}
function camClose(){camStop();el('cam').hidden=true;document.body.style.overflow=''}
function camStop(){cancelAnimationFrame(CAM.raf);if(CAM.stream){CAM.stream.getTracks().forEach(function(t){t.stop()});CAM.stream=null}}
function camStart(){camStop();var v=el('camv');el('campill').textContent='Starting camera…';
 if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){el('campill').textContent='Camera not available. Open this page in Chrome, or upload a photo instead.';return}
 navigator.mediaDevices.getUserMedia({video:{facingMode:CAM.facing,width:{ideal:1920},height:{ideal:1920}},audio:false}).then(function(s){CAM.stream=s;v.srcObject=s;
  v.style.transform=CAM.facing=='user'?'scaleX(-1)':'none';
  v.onloadedmetadata=function(){v.play();var ar=v.videoWidth/v.videoHeight;el('camstage').style.setProperty('--ar',ar);var o=el('camo');o.width=v.videoWidth;o.height=v.videoHeight;CAM.hold=0;CAM.raf=requestAnimationFrame(camLoop)}
 }).catch(function(e){el('campill').textContent='Camera blocked ('+(e.name||e)+'). Allow camera access, or upload a photo instead.'})}
function camLoadModel(){if(CAM.lm||CAM.loading)return;CAM.loading=true;
 import(MPV+'/vision_bundle.mjs').then(function(m){return m.FilesetResolver.forVisionTasks(MPV+'/wasm').then(function(fs){
  function mk(dl){return m.FaceLandmarker.createFromOptions(fs,{baseOptions:{modelAssetPath:'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',delegate:dl},runningMode:'VIDEO',numFaces:1,outputFaceBlendshapes:true})}
  return mk('GPU').catch(function(){return mk('CPU')})})}).then(function(lm){CAM.lm=lm;CAM.loading=false}).catch(function(){CAM.loading=false;CAM.lm=null;el('campill').textContent='Auto-check unavailable. Line up your smile and tap the button.'})}
function geom(W,H){var mn=Math.min(W,H),rx=mn*0.34,ry=rx*1.32,cx=W/2,cy=H*0.44;if(cy-ry<H*0.04)cy=ry+H*0.04;
 var zw=rx*0.95,zh=zw*0.46,zx=cx,zy=cy+ry*0.55;return{cx:cx,cy:cy,rx:rx,ry:ry,zx:zx,zy:zy,zw:zw,zh:zh}}
function drawGuide(g,W,H,G,allOk,mouth){g.clearRect(0,0,W,H);
 g.save();g.fillStyle='rgba(0,0,0,.45)';g.fillRect(0,0,W,H);g.globalCompositeOperation='destination-out';g.beginPath();g.ellipse(G.cx,G.cy,G.rx,G.ry,0,0,Math.PI*2);g.fill();g.restore();
 var col=allOk?'#4ade80':'rgba(255,255,255,.9)',lw=Math.max(3,W/220);
 g.lineWidth=lw;g.strokeStyle=col;g.beginPath();g.ellipse(G.cx,G.cy,G.rx,G.ry,0,0,Math.PI*2);g.stroke();
 // teeth zone with ideal 8-tooth template (RED 70%)
 var x0=G.zx-G.zw/2,y0=G.zy-G.zh/2,r=G.zh*0.35;g.setLineDash([lw*3,lw*2]);g.strokeStyle=allOk?'#4ade80':'#facc15';
 g.beginPath();g.moveTo(x0+r,y0);g.lineTo(x0+G.zw-r,y0);g.quadraticCurveTo(x0+G.zw,y0,x0+G.zw,y0+r);g.lineTo(x0+G.zw,y0+G.zh-r);g.quadraticCurveTo(x0+G.zw,y0+G.zh,x0+G.zw-r,y0+G.zh);g.lineTo(x0+r,y0+G.zh);g.quadraticCurveTo(x0,y0+G.zh,x0,y0+G.zh-r);g.lineTo(x0,y0+r);g.quadraticCurveTo(x0,y0,x0+r,y0);g.stroke();g.setLineDash([]);
 var q=0.7,half=G.zw*0.47,wc=half/(1+q+q*q+q*q*q*0.9),ws=[wc,wc*q,wc*q*q,wc*q*q*q*0.9],top=G.zy-G.zh*0.38,hc=wc/0.72;
 g.strokeStyle='rgba(255,255,255,.75)';g.lineWidth=Math.max(1.5,lw*0.55);
 [-1,1].forEach(function(s){var x=0;ws.forEach(function(w,i){var a=G.zx+s*x,b=G.zx+s*(x+w),h=hc*[1,0.86,0.94,0.8][i],tp=top+[0,0.06,0,0.1][i]*hc,ar=1-0.06*i*i;var bt=tp+h*ar;
  g.beginPath();g.moveTo(a,tp+h*0.15);g.quadraticCurveTo((a+b)/2,tp-h*0.04,b,tp+h*0.15);g.lineTo(b,bt-h*0.12);g.quadraticCurveTo(b,bt,(a+b)/2,bt);g.quadraticCurveTo(a,bt,a,bt-h*0.12);g.closePath();g.stroke();x+=w})});
 g.beginPath();g.moveTo(G.zx,G.cy-G.ry);g.lineTo(G.zx,G.zy+G.zh/2);g.strokeStyle='rgba(255,255,255,.35)';g.setLineDash([lw*2,lw*2]);g.stroke();g.setLineDash([]);
 if(mouth){g.fillStyle=allOk?'#4ade80':'#f87171';[mouth.l,mouth.r].forEach(function(p){g.beginPath();g.arc(p[0],p[1],lw*1.6,0,Math.PI*2);g.fill()})}}
function lumaOf(v,box){var c=CAM.tmp||(CAM.tmp=document.createElement('canvas'));c.width=24;c.height=24;var g=c.getContext('2d',{willReadFrequently:true});
 g.drawImage(v,box[0],box[1],Math.max(1,box[2]),Math.max(1,box[3]),0,0,24,24);var d=g.getImageData(0,0,24,24).data,s=0;for(var i=0;i<d.length;i+=4)s+=0.299*d[i]+0.587*d[i+1]+0.114*d[i+2];return s/(d.length/4)}
function camLoop(t){var v=el('camv'),o=el('camo');if(!v||!CAM.stream)return;var W=o.width,H=o.height,g=o.getContext('2d'),G=geom(W,H),dt=CAM.lastT?t-CAM.lastT:16;CAM.lastT=t;
 var ok={},msg='',mouth=null,mir=CAM.facing=='user';
 if(CAM.lm&&v.readyState>=2){var r=null;try{r=CAM.lm.detectForVideo(v,t)}catch(e){}
  if(r&&r.faceLandmarks&&r.faceLandmarks.length){var L=r.faceLandmarks[0];CAM.res=r;
   function P(i){var p=L[i];return[(mir?1-p.x:p.x)*W,p.y*H]}
   var ml=P(61),mr=P(291),mc=[(ml[0]+mr[0])/2,(ml[1]+mr[1])/2],mw=Math.hypot(mr[0]-ml[0],mr[1]-ml[1]);mouth={l:ml,r:mr};
   var nose=P(1),ck1=P(234),ck2=P(454),e1=P(33),e2=P(263),fh=P(10),ch=P(152),ul=P(13),ll=P(14);
   var dl=Math.abs(nose[0]-ck1[0]),dr=Math.abs(ck2[0]-nose[0]),yaw=(dl-dr)/(dl+dr+1e-6);
   var roll=Math.atan2(e2[1]-e1[1],e2[0]-e1[0])*180/Math.PI;if(roll>90)roll-=180;if(roll<-90)roll+=180;
   var pitch=(nose[1]-fh[1])/(ch[1]-fh[1]+1e-6);
   var bs={};((r.faceBlendshapes&&r.faceBlendshapes[0]&&r.faceBlendshapes[0].categories)||[]).forEach(function(c){bs[c.categoryName]=c.score});
   var smile=((bs.mouthSmileLeft||0)+(bs.mouthSmileRight||0))/2,gap=(ll[1]-ul[1])/(mw+1e-6);
   var ratio=mw/(G.zw*0.86);
   ok.zone=Math.abs(mc[0]-G.zx)<G.zw*0.18&&Math.abs(mc[1]-G.zy)<G.zh*0.55;
   ok.dist=ratio>0.82&&ratio<1.2;
   ok.straight=Math.abs(yaw)<0.12&&Math.abs(roll)<5&&pitch>0.44&&pitch<0.66;
   ok.smile=smile>0.35&&gap>0.05&&gap<0.45;
   var bx=Math.min(ck1[0],ck2[0]),by=fh[1],bw=Math.abs(ck2[0]-ck1[0]),bh=ch[1]-fh[1];if(mir)bx=W-bx-bw;
   var lu=lumaOf(v,[bx,by,bw,bh]);ok.light=lu>70&&lu<215;
   var mv=CAM.lastNose?Math.hypot(nose[0]-CAM.lastNose[0],nose[1]-CAM.lastNose[1])/W:1;CAM.lastNose=nose;CAM.mv=(CAM.mv==null?mv:CAM.mv*0.7+mv*0.3);ok.steady=CAM.mv<0.004;
   if(!ok.zone)msg=mc[1]<G.zy-G.zh*0.55?'Move the phone up a little':mc[1]>G.zy+G.zh*0.55?'Move the phone down a little':(mc[0]<G.zx?'Move slightly to your left':'Move slightly to your right');
   else if(!ok.dist)msg=ratio<0.82?'Move closer':'Move back a little';
   else if(!ok.straight)msg=Math.abs(yaw)>=0.12?(yaw>0?'Turn your head slightly right':'Turn your head slightly left'):Math.abs(roll)>=5?'Keep your head level':(pitch<=0.44?'Lower your chin slightly':'Raise your chin slightly');
   else if(!ok.smile)msg=gap>=0.45?'Close your mouth a little, keep smiling':'Big smile, show your upper teeth';
   else if(!ok.light)msg=lu<=70?'Too dark. Face a window or turn on a light':'Too bright. Move away from direct light';
   else if(!ok.steady)msg='Hold still…';
  }else{msg='Bring your face into the oval';CAM.lastNose=null}
 }else if(!CAM.lm){msg=CAM.loading?'Loading face guide…':'Line up your smile and tap the button'}
 var all=CHECKS.every(function(c){return ok[c[0]]});
 CHECKS.forEach(function(c){var s=el('ck_'+c[0]);if(s)s.className=ok[c[0]]?'on':''});
 CAM.hold=all?CAM.hold+dt:0;var left=Math.ceil((HOLD-CAM.hold)/1000);
 el('campill').textContent=all?'Perfect – hold still':msg;el('camh').textContent=all?'Perfect – hold still':(msg||'Smile inside the teeth zone');
 el('camcount').textContent=all&&left>0?left:'';
 var ring=el('camring');if(ring){var L2=2*Math.PI*34;ring.style.strokeDasharray=L2;ring.style.strokeDashoffset=L2*(1-Math.min(1,CAM.hold/HOLD))}
 drawGuide(g,W,H,G,all,mouth);
 if(all&&CAM.hold>=HOLD){camCapture(true);return}
 CAM.raf=requestAnimationFrame(camLoop)}
var FULL=null,FACEB=null;
var LIP_IN=[78,191,80,81,82,13,312,311,310,415,308,324,318,402,317,14,87,178,88,95],LIP_LO=[78,95,88,178,87,14,317,402,318,324,308],LIPS=null;
var MODEL='https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',IMLM=null;
function cropFromL(L,W,H){function P(i){return[L[i].x*W,L[i].y*H]}
 var ml=P(61),mr=P(291),mw=Math.hypot(mr[0]-ml[0],mr[1]-ml[1]),cx=(ml[0]+mr[0])/2,cy=(ml[1]+mr[1])/2;
 var cw=Math.min(W,mw*1.6),ch=Math.min(H,cw*0.62),sx=clamp(cx-cw/2,0,W-cw),sy=clamp(cy-ch*0.5,0,H-ch);
 var mx=(P(168)[0]+P(1)[0]+P(152)[0])/3,fm=Math.round((mx-sx)/cw*1000);if(fm<0||fm>1000)fm=null;
 function q(i){return[Math.round((L[i].y*H-sy)/ch*1000),Math.round((L[i].x*W-sx)/cw*1000)]}
 var e1=P(33),e2=P(263),ipl=Math.atan2(e2[1]-e1[1],e2[0]-e1[0]);if(ipl>Math.PI/2)ipl-=Math.PI;if(ipl<-Math.PI/2)ipl+=Math.PI;
 return{eyes:[e1[0],e1[1],e2[0],e2[1]],crop:[sx,sy,cw,ch],fm:fm,lips:{inner:LIP_IN.map(q),lower:LIP_LO.map(q),ipl:ipl,comm:[q(61),q(291)],upper:[78,191,80,81,82,13,312,311,310,415,308].map(q)}}}
function imgLandmarks(im){return (IMLM?Promise.resolve(IMLM):import(MPV+'/vision_bundle.mjs').then(function(m){return m.FilesetResolver.forVisionTasks(MPV+'/wasm').then(function(fs){return m.FaceLandmarker.createFromOptions(fs,{baseOptions:{modelAssetPath:MODEL,delegate:'CPU'},runningMode:'IMAGE',numFaces:1})})}).then(function(l){IMLM=l;return l})).then(function(l){var r=l.detect(im);return r&&r.faceLandmarks&&r.faceLandmarks.length?r.faceLandmarks[0]:null}).catch(function(){return null})}
function camCapture(auto){var v=el('camv');if(!v||!v.videoWidth)return;var W=v.videoWidth,H=v.videoHeight,c=document.createElement('canvas');c.width=W;c.height=H;c.getContext('2d').drawImage(v,0,0,W,H);
 var crop=null,fm=null,r=CAM.res;
 if(r&&r.faceLandmarks&&r.faceLandmarks.length){var L=r.faceLandmarks[0];function P(i){return[L[i].x*W,L[i].y*H]}
  var cr=cropFromL(L,W,H);crop=cr.crop;var lips=cr.lips,eyes=cr.eyes;fm=cr.fm;}
 camStop();CAM.captured={canvas:c,crop:crop,fm:fm,lips:lips,eyes:eyes};
 el('camimg').src=toURL(c,0,0,W,H,900,0.88);
 el('camstage').hidden=true;el('camprev').hidden=false;el('cam').classList.add('pv');el('camh').textContent=auto?'Photo taken automatically':'Photo taken';el('camp').textContent='Check that your teeth are sharp and clearly visible.'}
function camUse(){camClose();setTimeout(function(){var b=el('dsb');if(b)b.scrollIntoView({behavior:'smooth',block:'center'})},50);var c=CAM.captured;if(!c)return;prev.innerHTML='<img src="'+toURL(c.canvas,0,0,c.canvas.width,c.canvas.height,700,0.85)+'" alt="Your photo">';
 if(inp)inp.value='';msg.className='muted';msg.textContent='Photo ready. Tap "Design my smile".'}

var cb=document.getElementById('dscam');if(cb)cb.addEventListener('click',camOpen);
if(inp)inp.addEventListener('change',function(){CAM.captured=null});
if(f)f.addEventListener('submit',function(ev){ev.preventDefault();out.innerHTML='';msg.className='muted';
if(!CAM.captured&&!inp.files.length){msg.textContent='Please take a photo with the guided camera or upload one.';return}
btn.disabled=true;btn.textContent='Finding your smile...';msg.textContent='Step 1 of 2: locating your teeth.';beforeURL=null;
var fm=null,p0;LIPS=null;FULL=null;FACEB=null;
if(CAM.captured){var c=CAM.captured;fm=c.fm;LIPS=c.lips||null;if(c.crop)FULL={img:c.canvas,crop:c.crop,eyes:c.eyes};beforeURL=c.crop?toURL(c.canvas,c.crop[0],c.crop[1],c.crop[2],c.crop[3],1200,0.9):toURL(c.canvas,0,0,c.canvas.width,c.canvas.height,1280,0.88);p0=Promise.resolve()}
else{var full;p0=loadFile(inp.files[0]).then(function(im){full=im;return imgLandmarks(im)}).then(function(L){var im=full,W=im.naturalWidth,H=im.naturalHeight,k=Math.min(1,1280/Math.max(W,H));
 if(L){var cr=cropFromL(L,W,H);fm=cr.fm;LIPS=cr.lips;FULL={img:full,crop:cr.crop,eyes:cr.eyes};beforeURL=toURL(full,cr.crop[0],cr.crop[1],cr.crop[2],cr.crop[3],1200,0.9);return {j:null}}
 return post({mode:'locate',image:toURL(im,0,0,W,H,Math.round(W*k),0.85)})}).then(function(x){if(beforeURL)return;
 var W=full.naturalWidth,H=full.naturalHeight;
 if(x.j&&x.j.ok&&x.j.mouth_box&&x.j.face_ok!==false){var b=x.j.mouth_box,y0=b[0]*H/1000,x0=b[1]*W/1000,y1=b[2]*H/1000,x1=b[3]*W/1000,mw=x1-x0,mh=y1-y0;
  if(mw>10&&mh>5){var cw=Math.min(W,mw*1.8),ch=Math.min(H,cw*0.75),cx=(x0+x1)/2,cy=(y0+y1)/2-mh*0.05;var sx=clamp(cx-cw/2,0,W-cw),sy=clamp(cy-ch/2,0,H-ch);
   if(x.j.facial_midline_x!=null){fm=Math.round(((x.j.facial_midline_x*W/1000)-sx)/cw*1000);if(fm<0||fm>1000)fm=null}
   beforeURL=toURL(full,sx,sy,cw,ch,1200,0.9);FULL={img:full,crop:[sx,sy,cw,ch]}}}
 if(!beforeURL){var k=Math.min(1,1280/Math.max(W,H));beforeURL=toURL(full,0,0,W,H,Math.round(W*k),0.88)}})}
p0.then(function(){
 btn.textContent='Designing your smile...';msg.textContent='Step 2 of 2: measuring your teeth. This takes 15 to 40 seconds.';
 return post({name:f.name.value,phone:f.phone.value,consent:f.consent.checked,website:f.website.value,image:beforeURL,facial_midline_x:fm})
}).then(function(x){
btn.disabled=false;btn.textContent='Design my smile';
if(!x.ok||!x.j.analysis){msg.className='muted err';msg.textContent=(x.j&&x.j.error)||'Something went wrong. Please try again.';return}
msg.textContent='';show(x.j.analysis,x.j.after)}).catch(function(e){btn.disabled=false;btn.textContent='Design my smile';msg.className='muted err';msg.textContent='Could not complete the design ('+((e&&e.message)||e)+'). Please open this page in Chrome and try again, or WhatsApp the clinic.'})});

/* ---------- geometry ---------- */
function teethPx(){var a=S.a,T={};for(var id in a.teeth){var b=a.teeth[id].box;T[id]={y0:b[0]*S.H/1000,x0:b[1]*S.W/1000,y1:b[2]*S.H/1000,x1:b[3]*S.W/1000}}return T}
function design(){
 var a=S.a,T=teethPx(),r=clamp(RATIOS[S.ratio]+(FORMS[S.form].dr||0),0.55,0.86);
 var cen=[T.UR1,T.UL1].filter(Boolean);if(!cen.length)return null;
 var cwNow=avg(cen.map(function(t){return t.x1-t.x0})),mm=cwNow/8.5;
 var mid=a.facial_midline_x!=null?a.facial_midline_x*S.W/1000:(a.dental_midline_x!=null?a.dental_midline_x*S.W/1000:(T.UR1&&T.UL1?(T.UR1.x1+T.UL1.x0)/2:avg(cen.map(function(t){return (t.x0+t.x1)/2}))));
 function span(side){var k=T[side<0?'UR3':'UL3'],l=T[side<0?'UR2':'UL2'];
  if(k)return side<0?mid-k.x0:k.x1-mid;
  if(l)return (side<0?mid-l.x0:l.x1-mid)*(1+r+r*r)/(1+r);
  return cwNow*(1+r+r*r)}
 var half=avg([span(-1),span(1)]);
 var wc=clamp(half/(1+r+r*r),0.88*cwNow,1.15*cwNow),wl=wc*r,wk=wl*r,wp=wk*r*1.05;
 var incC=avg(cen.map(function(t){return t.y1})),gumNow=avg(cen.map(function(t){return t.y0}));
 var lipC=a.lower_lip_y_at_center!=null?a.lower_lip_y_at_center*S.H/1000:null,lipK=a.lower_lip_y_at_canines!=null?a.lower_lip_y_at_canines*S.H/1000:null,lowF=null;
 if(a._lower){var LP=a._lower.map(function(q){return[q[1]*S.W/1000,q[0]*S.H/1000]}).sort(function(p,q){return p[0]-q[0]});
  lowF=function(x){if(x<=LP[0][0])return LP[0][1];for(var i=1;i<LP.length;i++)if(x<=LP[i][0]){var u=(x-LP[i-1][0])/((LP[i][0]-LP[i-1][0])||1);return LP[i-1][1]+u*(LP[i][1]-LP[i-1][1])}return LP[LP.length-1][1]};
  lipC=lowF(mid);lipK=avg([lowF(mid-half*0.9),lowF(mid+half*0.9)])}
 var rise=(lipC!=null&&lipK!=null)?clamp((lipC-lipK)*0.85,0.6*mm,4*mm):1.2*mm;
 if(lipC!=null){var gap=clamp(lipC-incC,0.4*mm,2*mm);incC=clamp(lipC-gap,incC-1*mm,incC+1.5*mm)}
 function inc(dx){var u=dx/half;return incC-rise*u*u}
 var hcIdeal=wc/S.wh,gumC=Math.min(inc(wc/2)-hcIdeal,gumNow+1.5*mm);
 var list=[],widths=[wc,wl,wk,wp],gumOff=[0,0.75*mm,0,0.5*mm],incOff=[0,0.8*mm,0,1.6*mm],types=['c','l','k','p'];
 [-1,1].forEach(function(s){var x=0;for(var i=0;i<4;i++){var xm=mid+s*x,xd=mid+s*(x+widths[i]),cx=x+widths[i]/2;
   var id=(s<0?'UR':'UL')+(i+1);list.push({id:id,type:types[i],xm:xm,xd:xd,top:gumC+gumOff[i]+(i==3?0.3*mm:0),bot:inc(cx)-incOff[i],w:widths[i],shade:[1,0.97,0.94,0.9][i]});x+=widths[i]}});
 return {T:T,list:list,mid:mid,mm:mm,wc:wc,wl:wl,wk:wk,wp:wp,half:half,hc:inc(wc/2)-gumC,gumC:gumC,incC:incC,rise:rise,inc:inc,cwNow:cwNow};
}
function mouthPath(g,D){var a=S.a,p=a.mouth_polygon;
 g.beginPath();
 if(p&&p.length>=6){p.forEach(function(q,i){var x=q[1]*S.W/1000,y=q[0]*S.H/1000;if(i)g.lineTo(x,y);else g.moveTo(x,y)});g.closePath();return}
 var xs=[],ys=[];for(var k in D.T){var t=D.T[k];xs.push(t.x0,t.x1);ys.push(t.y0,t.y1)}
 var x0=Math.min.apply(0,xs),x1=Math.max.apply(0,xs),y0=Math.min.apply(0,ys)-2*D.mm,y1=Math.max.apply(0,ys)+3*D.mm,cx=(x0+x1)/2,rx=(x1-x0)/2+D.mm,ry=(y1-y0)/2;
 g.ellipse(cx,(y0+y1)/2,rx,ry,0,0,Math.PI*2)}
function toothPath(g,t){var xm=t.xm,xd=t.xd,s=xd>xm?1:-1,w=Math.abs(xd-xm),top=t.top,bot=t.bot,h=bot-top,zen=xm+(xd-xm)*0.58;
 function X(u){return xm+s*u*w}
 var F=FORMS[S.form]||FORMS.oval,nk=F.neck,hh=Math.min(h,w*(t.type=='c'?1.3:1.45)),cz=bot-hh*(nk>0.08?0.38:0.55);
 var ang={c:0.025,l:0.055,k:0.09,p:0.07}[t.type]||0;g.save();g.translate((xm+xd)/2,bot);g.rotate(s*ang);g.translate(-(xm+xd)/2,-bot);
 g.beginPath();g.moveTo(X(0.02+nk),top+0.04*h);
 g.bezierCurveTo(X(0.2),top,X(0.45),top,zen,top);g.bezierCurveTo(X(0.75),top,X(0.96-nk),top+0.02*h,X(0.98-nk),top+0.06*h);
 if(t.type=='k'||t.type=='p'){var tip=t.type=='k'?0.44:0.5,ds=t.type=='k'?0.26:0.2,tr=F.tip;
  g.bezierCurveTo(X(1),top+(cz-top)*0.5,X(1.01),cz,X(0.99),bot-ds*hh);
  g.bezierCurveTo(X(0.9),bot-ds*hh*0.7,X(tip+tr*1.6),bot-0.02*hh,X(tip+tr*0.5),bot-0.004*hh);
  g.quadraticCurveTo(X(tip),bot+0.012*hh,X(tip-tr*0.5),bot-0.004*hh);
  g.bezierCurveTo(X(tip-tr*1.6),bot-0.02*hh,X(0.1),bot-(ds-0.08)*hh*0.7,X(0.01),bot-(ds-0.08)*hh);
  g.bezierCurveTo(X(-0.01),cz,X(0),top+(cz-top)*0.5,X(0.02+nk),top+0.04*h)}
 else{var fp=t.type=='c'?F.c:F.l,rm=fp[0],rd=fp[1],e=fp[2]*w;
  // gently convex sides (narrower at the neck), rounded incisal angles: mesial tighter, distal rounder
  g.bezierCurveTo(X(0.99),top+(cz-top)*0.45,X(1.025),cz,X(1),bot-rd*w);
  g.bezierCurveTo(X(1),bot-rd*w*0.45,X(1-rd*0.45),bot+e*0.3,X(1-rd),bot+e*0.45);
  var sp=1-rd-rm;g.bezierCurveTo(X(1-rd-sp*0.33),bot+e,X(rm+sp*0.33),bot+e,X(rm),bot+e*0.3);
  g.bezierCurveTo(X(rm*0.45),bot+e*0.1,X(0),bot-rm*w*0.45,X(0),bot-rm*w);
  g.bezierCurveTo(X(-0.025),cz,X(0.01),top+(cz-top)*0.45,X(0.02+nk),top+0.04*h)}
 g.closePath();g.restore()}

/* ---------- pixel work ---------- */
function baseCanvas(){var c=document.createElement('canvas');c.width=S.W;c.height=S.H;var g=c.getContext('2d');g.drawImage(S.img,0,0);return [c,g]}
function whiten(c,g,D){var sh=SHADES[S.shade];
 var m=document.createElement('canvas');m.width=S.W;m.height=S.H;var mg=m.getContext('2d');
 mg.save();mouthPath(mg,D);mg.clip();mg.fillStyle='#fff';for(var k in D.T){var t=D.T[k];mg.fillRect(t.x0-D.mm,t.y0-D.mm,t.x1-t.x0+2*D.mm,t.y1-t.y0+2*D.mm)}mg.restore();
 var m2=document.createElement('canvas');m2.width=S.W;m2.height=S.H;var g2=m2.getContext('2d');g2.filter='blur('+Math.max(2,D.mm*0.6)+'px)';g2.drawImage(m,0,0);
 var md=g2.getImageData(0,0,S.W,S.H).data,im=g.getImageData(0,0,S.W,S.H),d=im.data;
 for(var i=0;i<d.length;i+=4){var mw=md[i+3]/255;if(mw<0.02)continue;var r=d[i],gg=d[i+1],b=d[i+2];
  var mx=Math.max(r,gg,b),mn=Math.min(r,gg,b),lum=(0.299*r+0.587*gg+0.114*b)/255,sat=mx?(mx-mn)/mx:0,red=(r-gg)/255;
  var w=mw*clamp((0.2-red)/0.1,0,1)*clamp((lum-0.28)/0.17,0,1)*clamp((0.62-sat)/0.15,0,1);if(w<=0)continue;
  var y=(r+gg)/2;b=b+sh.yr*w*(y-b);r=r-sh.yr*w*0.25*(r-gg>0?r-gg:0);
  d[i]=clamp(r+sh.lift*w*(255-r),0,255);d[i+1]=clamp(gg+sh.lift*w*(255-gg),0,255);d[i+2]=clamp(b+sh.lift*w*(255-b),0,255)}
 g.putImageData(im,0,0)}
function sampleGum(D){var c=document.createElement('canvas');c.width=S.W;c.height=S.H;var g=c.getContext('2d');g.drawImage(S.img,0,0);
 var t=D.T.UR1||D.T.UL1,x=Math.round((t.x0+t.x1)/2),y=Math.round(t.y0-0.8*D.mm);if(y<1)y=1;
 var p=g.getImageData(clamp(x-3,0,S.W-7),clamp(y-2,0,S.H-5),7,5).data,r=0,gg=0,b=0,n=0;for(var i=0;i<p.length;i+=4){r+=p[i];gg+=p[i+1];b+=p[i+2];n++}
 r/=n;gg/=n;b/=n;if(r-gg<25){r=200;gg=110;b=115}return [r,gg,b]}
function rgb(c,k,a){return 'rgba('+Math.round(clamp(c[0]*k,0,255))+','+Math.round(clamp(c[1]*k,0,255))+','+Math.round(clamp(c[2]*k,0,255))+','+(a==null?1:a)+')'}
function sampleTooth(g,D){var r=0,gg=0,b=0,n=0;['UR1','UL1'].forEach(function(id){var t=D.T[id];if(!t)return;var w=t.x1-t.x0,h=t.y1-t.y0,p=g.getImageData(Math.round(t.x0+w*0.3),Math.round(t.y0+h*0.35),Math.max(1,Math.round(w*0.4)),Math.max(1,Math.round(h*0.3))).data;for(var i=0;i<p.length;i+=4){r+=p[i];gg+=p[i+1];b+=p[i+2];n++}});return n?[r/n,gg/n,b/n]:null}
function sampleOral(g,D){var xs=[],ys=[];for(var k in D.T){var t=D.T[k];xs.push(t.x0,t.x1);ys.push(t.y0,t.y1)}
 var x0=Math.max(0,Math.round(Math.min.apply(0,xs))),x1=Math.min(S.W,Math.round(Math.max.apply(0,xs))),y0=Math.max(0,Math.round(Math.min.apply(0,ys))),y1=Math.min(S.H,Math.round(Math.max.apply(0,ys)+2*D.mm));
 if(x1-x0<4||y1-y0<4)return[50,28,30];var p=g.getImageData(x0,y0,x1-x0,y1-y0).data,a=[];for(var i=0;i<p.length;i+=16)a.push([p[i]+p[i+1]+p[i+2],p[i],p[i+1],p[i+2]]);
 a.sort(function(u,v){return u[0]-v[0]});var n=Math.max(1,Math.round(a.length*0.06)),r=0,gg=0,b=0;for(var j=0;j<n;j++){r+=a[j][1];gg+=a[j][2];b+=a[j][3]}
 return[clamp(r/n,25,90),clamp(gg/n,12,60),clamp(b/n,14,60)]}
function srcFor(id,D){var T=D.T,o=T[id],m=false;if(!o){o=T[(id[1]=='R'?'UL':'UR')+id[2]];m=!!o}if(!o)return null;
 var w=o.x1-o.x0,h=o.y1-o.y0;return{x:o.x0+w*0.18,y:o.y0+h*0.2,w:w*0.64,h:h*0.55,flip:m}}
function lipMask(D,blur){var m=document.createElement('canvas');m.width=S.W;m.height=S.H;var g=m.getContext('2d');g.filter='blur('+blur+'px)';g.fillStyle='#fff';mouthPath(g,D);g.fill();return m}
function mockup(c,g,D){var sh=SHADES[S.shade],st=sampleTooth(g,D),base=sh.c,mm=D.mm;
 // tone-match: brighten the patient's own (already whitened) tooth colour so the new teeth sit in the photo's light
 if(st){var gain={a2:1.04,a1:1.1,b1:1.16,bl:1.22}[S.shade]||1.1,y=(st[0]+st[1])/2;base=[st[0]*gain,st[1]*gain,(st[2]+sh.yr*0.6*(y-st[2]))*gain].map(function(v){return clamp(v,0,250)});
  var Lb=(base[0]+base[1]+base[2])/3;if(Lb<150){var f=150/Lb;base=base.map(function(v){return clamp(v*f,0,250)})}}
 var orig=document.createElement('canvas');orig.width=S.W;orig.height=S.H;orig.getContext('2d').drawImage(c,0,0);
 var oral=sampleOral(orig.getContext('2d'),D);
 var Ly=document.createElement('canvas');Ly.width=S.W;Ly.height=S.H;var lg=Ly.getContext('2d');
 // natural mode: teeth run up under the upper lip; never shorter than the current edge by more than the design asks
 var L2=D.list.map(function(t){var x0=Math.min(t.xm,t.xd),x1=Math.max(t.xm,t.xd),ot=null;for(var k in D.T){var o=D.T[k];if(o.x1>x0&&o.x0<x1)ot=ot==null?o.y0:Math.min(ot,o.y0)}
  var n={};for(var q in t)n[q]=t[q];n.top=Math.min(t.top,(ot==null?t.top:ot))-3*mm;return n});
 // 1. dark mouth background behind the new teeth (replaces the old teeth), darker toward the corners
 var bx0=Math.min.apply(0,L2.map(function(t){return Math.min(t.xm,t.xd)}))-1.5*mm,bx1=Math.max.apply(0,L2.map(function(t){return Math.max(t.xm,t.xd)}))+1.5*mm;
 var by0=Math.min.apply(0,L2.map(function(t){return t.top})),by1=Math.max.apply(0,L2.map(function(t){return t.bot}))+0.6*mm;
 for(var k in D.T){var o=D.T[k];bx0=Math.min(bx0,o.x0-mm);bx1=Math.max(bx1,o.x1+mm)}
 lg.save();lg.filter='blur('+Math.max(1,mm*0.5)+'px)';var bg=lg.createLinearGradient(bx0,0,bx1,0);
 bg.addColorStop(0,rgb(oral,0.92));bg.addColorStop(0.25,rgb(oral,1));bg.addColorStop(0.75,rgb(oral,1));bg.addColorStop(1,rgb(oral,0.92));lg.fillStyle=bg;lg.fillRect(bx0,by0,bx1-bx0,by1-by0);lg.fillStyle=rgb(oral,1);for(var k in D.T){var o=D.T[k];lg.fillRect(o.x0-0.8*mm,o.y0-mm,o.x1-o.x0+1.6*mm,o.y1-o.y0+1.8*mm)}lg.restore();
 // 2. teeth: back to front, textured from the patient's own enamel
 L2.slice().sort(function(p,q){return p.w-q.w}).forEach(function(t){var dx=Math.min(t.xm,t.xd),dw=Math.abs(t.xd-t.xm),dy=t.top,dh=t.bot-t.top,s=t.xd>t.xm?1:-1;
  lg.save();toothPath(lg,t);lg.clip();
  var vg=lg.createLinearGradient(0,dy,0,t.bot);vg.addColorStop(0,rgb(base,0.9));vg.addColorStop(0.6,rgb(base,1));vg.addColorStop(1,rgb(base,0.96));lg.fillStyle=vg;lg.fillRect(dx,dy,dw,dh);
  var sr=srcFor(t.id,D);
  if(sr){lg.save();lg.globalAlpha=0.85;if(sr.flip){lg.translate(dx+dw,0);lg.scale(-1,1);lg.drawImage(orig,sr.x,sr.y,sr.w,sr.h,0,dy,dw,dh)}else lg.drawImage(orig,sr.x,sr.y,sr.w,sr.h,dx,dy,dw,dh);lg.restore();
   lg.globalCompositeOperation='color';lg.globalAlpha=0.3;lg.fillStyle=rgb(base);lg.fillRect(dx,dy,dw,dh);lg.globalCompositeOperation='source-over';lg.globalAlpha=1}
  // cervical warmth and incisal translucency
  var hz=t.bot-Math.min(dh,dw*1.35),cg=lg.createLinearGradient(0,hz,0,t.bot);
  cg.addColorStop(0,'rgba(190,150,105,.1)');cg.addColorStop(0.35,'rgba(190,150,105,0)');cg.addColorStop(0.82,'rgba(140,150,170,0)');cg.addColorStop(1,'rgba(120,130,155,'+(t.type=='c'||t.type=='l'?0.38:0.18)+')');lg.fillStyle=cg;lg.fillRect(dx,dy,dw,dh);
  // curvature: edges roll away; distal side darker on canines and premolars (they turn away from camera)
  var mi=s>0?dx:dx+dw,di=s>0?dx+dw:dx,hg=lg.createLinearGradient(mi,0,di,0),dd=t.type=='c'?0.16:t.type=='l'?0.22:t.type=='k'?0.3:0.34;
  hg.addColorStop(0,'rgba(60,40,35,.24)');hg.addColorStop(0.16,'rgba(60,40,35,0)');hg.addColorStop(t.type=='k'||t.type=='p'?0.5:0.8,'rgba(60,40,35,0)');hg.addColorStop(1,'rgba(60,40,35,'+dd+')');lg.fillStyle=hg;lg.fillRect(dx,dy,dw,dh);
  var hx=dx+dw*(s>0?0.4:0.6),rg=lg.createRadialGradient(hx,t.bot-dh*0.45,1,hx,t.bot-dh*0.45,dw*0.5);rg.addColorStop(0,'rgba(255,255,255,'+(t.type=='c'?0.16:0.1)+')');rg.addColorStop(1,'rgba(255,255,255,0)');lg.fillStyle=rg;lg.fillRect(dx,dy,dw,dh);
  if(t.shade<1){lg.fillStyle='rgba(30,15,15,'+(1-t.shade)+')';lg.fillRect(dx,dy,dw,dh)}
  lg.restore();
  lg.save();lg.filter='blur('+Math.max(0.6,mm*0.07)+'px)';toothPath(lg,t);lg.lineWidth=Math.max(1,mm*0.12);lg.strokeStyle='rgba(80,50,45,.35)';lg.stroke();lg.restore()});
 // 3. upper-lip shadow on the teeth, then keep only what is inside the lips (soft edge)
 lg.save();lg.globalCompositeOperation='source-atop';lg.filter='blur('+Math.max(1,mm*0.7)+'px)';mouthPath(lg,D);lg.lineWidth=mm*1.3;lg.strokeStyle='rgba(40,18,18,.38)';lg.stroke();lg.restore();
 lg.globalCompositeOperation='destination-in';lg.drawImage(lipMask(D,Math.max(0.8,mm*0.3)),0,0);lg.globalCompositeOperation='source-over';
 // 4. match the photo's grain so the teeth don't look painted
 var id=lg.getImageData(0,0,S.W,S.H),d=id.data,amp=12;for(var i=0;i<d.length;i+=4){if(d[i+3]<8)continue;var n=(Math.random()-0.5)*amp;d[i]=clamp(d[i]+n,0,255);d[i+1]=clamp(d[i+1]+n,0,255);d[i+2]=clamp(d[i+2]+n,0,255)}lg.putImageData(id,0,0);
 g.drawImage(Ly,0,0)}
function lines(g,D,opt){var lw=Math.max(1.5,S.W/450);g.lineWidth=lw;g.font='600 '+Math.round(S.W/42)+'px system-ui,sans-serif';g.textAlign='center';
 if(opt.boxes){ORDER.forEach(function(id){var t=D.T[id];if(!t)return;g.strokeStyle='rgba(255,214,0,.95)';g.strokeRect(t.x0,t.y0,t.x1-t.x0,t.y1-t.y0);g.fillStyle='rgba(255,214,0,.95)';g.fillText(id.slice(2),(t.x0+t.x1)/2,t.y0-lw*2)})}
 var a=S.a;
 if(opt.mid){if(a.facial_midline_x!=null){var fx=a.facial_midline_x*S.W/1000;g.strokeStyle='rgba(0,200,255,.95)';g.setLineDash([lw*4,lw*3]);g.beginPath();g.moveTo(fx,0);g.lineTo(fx,S.H);g.stroke();g.setLineDash([])}
  if(a.dental_midline_x!=null&&opt.boxes){var dx=a.dental_midline_x*S.W/1000;g.strokeStyle='rgba(255,60,60,.95)';g.beginPath();g.moveTo(dx,D.gumC-4*D.mm);g.lineTo(dx,D.incC+4*D.mm);g.stroke()}}
 if(opt.lip&&a.lower_lip_y_at_center!=null&&a.lower_lip_y_at_canines!=null){var yc=a.lower_lip_y_at_center*S.H/1000,ys=a.lower_lip_y_at_canines*S.H/1000;g.strokeStyle='rgba(120,255,120,.95)';g.beginPath();g.moveTo(D.mid-D.half,ys);g.quadraticCurveTo(D.mid,2*yc-ys,D.mid+D.half,ys);g.stroke()}
 if(opt.design){g.setLineDash([]);D.list.forEach(function(t){toothPath(g,t);g.strokeStyle='rgba(255,255,255,.95)';g.lineWidth=lw*1.1;g.stroke()});
  g.strokeStyle='rgba(255,170,60,.9)';g.setLineDash([lw*3,lw*2]);g.beginPath();for(var x=D.mid-D.half;x<=D.mid+D.half;x+=3){var y=D.inc(Math.abs(x-D.mid));if(x==D.mid-D.half)g.moveTo(x,y);else g.lineTo(x,y)}g.stroke();
  g.beginPath();g.moveTo(D.mid-D.half,D.gumC);g.lineTo(D.mid+D.half,D.gumC);g.stroke();g.setLineDash([]);
  g.fillStyle='#fff';g.strokeStyle='rgba(0,0,0,.6)';g.lineWidth=lw*1.5;g.font='600 '+Math.round(Math.max(10,D.mm*1.6))+'px system-ui,sans-serif';
  D.list.forEach(function(t){if(t.type=='p')return;var x=(t.xm+t.xd)/2,y=t.bot+2.6*D.mm,s=(8.5*t.w/D.cwNow).toFixed(1);g.strokeText(s,x,y);g.fillText(s,x,y)})}}
function poly(g,pts,close){g.beginPath();pts.forEach(function(p,i){var x=p[1]*S.W/1000,y=p[0]*S.H/1000;if(i)g.lineTo(x,y);else g.moveTo(x,y)});if(close)g.closePath()}
function dsdLines(g,D){var a=S.a,lw=Math.max(1.5,S.W/420),mm=D.mm,ang=a._ipl||0,cs=Math.cos(ang),sn=Math.sin(ang),fs=Math.round(Math.max(11,mm*1.45));
 g.save();g.fillStyle='rgba(0,0,0,.18)';g.fillRect(0,0,S.W,S.H);g.restore();
 function line(x,y,dx,dy,col,dash,w){g.save();g.strokeStyle=col;g.lineWidth=w||lw;if(dash)g.setLineDash(dash);g.beginPath();g.moveTo(x-dx*S.W*2,y-dy*S.W*2);g.lineTo(x+dx*S.W*2,y+dy*S.W*2);g.stroke();g.restore()}
 function tag(txt,x,y,col){g.save();g.font='700 '+fs+'px system-ui,sans-serif';var w=g.measureText(txt).width+fs*0.6;g.fillStyle='rgba(0,0,0,.6)';g.fillRect(x,y-fs*0.95,w,fs*1.3);g.fillStyle=col;g.fillText(txt,x+fs*0.3,y);g.restore()}
 var cy=(D.gumC+D.incC)/2;
 // 1. facial cross: midline perpendicular to the eye line, horizontal reference parallel to it
 line(D.mid,cy,-sn,cs,'rgba(0,210,255,.95)',[lw*5,lw*3]);
 line(D.mid,D.gumC-5*mm,cs,sn,'rgba(255,230,0,.9)',[lw*5,lw*3]);
 // 2. commissure line
 if(a._comm){var c1=a._comm[0],c2=a._comm[1];g.save();g.strokeStyle='rgba(255,90,200,.95)';g.lineWidth=lw;g.beginPath();g.moveTo(c1[1]*S.W/1000,c1[0]*S.H/1000);g.lineTo(c2[1]*S.W/1000,c2[0]*S.H/1000);g.stroke();g.restore()}
 // 3. lip lines
 if(a._upper){g.save();g.strokeStyle='rgba(255,150,150,.95)';g.lineWidth=lw;poly(g,a._upper);g.stroke();g.restore()}
 if(a._lower){g.save();g.strokeStyle='rgba(120,255,120,.95)';g.lineWidth=lw;poly(g,a._lower);g.stroke();g.restore()}
 else if(a.lower_lip_y_at_center!=null&&a.lower_lip_y_at_canines!=null){var yc=a.lower_lip_y_at_center*S.H/1000,ys=a.lower_lip_y_at_canines*S.H/1000;g.save();g.strokeStyle='rgba(120,255,120,.95)';g.lineWidth=lw;g.beginPath();g.moveTo(D.mid-D.half,ys);g.quadraticCurveTo(D.mid,2*yc-ys,D.mid+D.half,ys);g.stroke();g.restore()}
 // 4. tooth outlines
 D.list.forEach(function(t){toothPath(g,t);g.strokeStyle='rgba(255,255,255,.95)';g.lineWidth=lw*1.1;g.stroke()});
 var Ls=D.list.slice().sort(function(p,q){return Math.min(p.xm,p.xd)-Math.min(q.xm,q.xd)});
 // 5. gingival zenith line, contact-point line, incisal line (smile arc)
 g.save();g.lineWidth=lw;g.strokeStyle='rgba(255,140,40,.95)';g.beginPath();Ls.forEach(function(t,i){var x=t.xm+(t.xd-t.xm)*0.58,y=t.top;if(i)g.lineTo(x,y);else g.moveTo(x,y)});g.stroke();
 Ls.forEach(function(t){var x=t.xm+(t.xd-t.xm)*0.58;g.fillStyle='rgba(255,140,40,1)';g.beginPath();g.arc(x,t.top,lw*1.8,0,7);g.fill()});
 g.strokeStyle='rgba(190,120,255,.95)';g.setLineDash([lw*2,lw*2]);g.beginPath();var first=true;
 for(var i=0;i<Ls.length-1;i++){var p=Ls[i],q=Ls[i+1],x=Math.max(p.xm,p.xd),hc=D.hc,y=Math.min(p.bot,q.bot)-hc*(p.type=='c'&&q.type=='c'?0.25:(p.type=='l'||q.type=='l')&&(p.type=='c'||q.type=='c')?0.33:0.45);if(first){g.moveTo(x,y);first=false}else g.lineTo(x,y)}
 g.stroke();g.setLineDash([lw*4,lw*2]);g.strokeStyle='rgba(255,215,120,.95)';g.beginPath();for(var x2=D.mid-D.half;x2<=D.mid+D.half;x2+=3){var y2=D.inc(Math.abs(x2-D.mid));if(x2==D.mid-D.half)g.moveTo(x2,y2);else g.lineTo(x2,y2)}g.stroke();g.restore();
 // 6. proportions: W/H on centrals, width % on the others
 g.save();g.textAlign='center';g.font='700 '+fs+'px system-ui,sans-serif';g.lineWidth=lw*1.6;g.strokeStyle='rgba(0,0,0,.7)';g.fillStyle='#fff';
 D.list.forEach(function(t){var x=(t.xm+t.xd)/2,y=t.bot+fs*1.25,txt;
  if(t.type=='c')txt=Math.round(t.w/D.hc*100)+'%';else if(t.type=='p')return;else{var prev=t.type=='l'?D.wc:D.wl;txt=Math.round(t.w/prev*100)+'%'}
  g.strokeText(txt,x,y);g.fillText(txt,x,y)});g.restore();
 // 7. 10 mm ruler
 var rx=S.W*0.04,ry=S.H*0.94;g.save();g.strokeStyle='#fff';g.lineWidth=lw*1.4;g.beginPath();g.moveTo(rx,ry);g.lineTo(rx+10*mm,ry);for(var j=0;j<=10;j++){var tx=rx+j*mm,th=j%5?fs*0.25:fs*0.5;g.moveTo(tx,ry);g.lineTo(tx,ry-th)}g.stroke();g.restore();tag('10 mm',rx+10*mm+fs*0.4,ry,'#fff');
 // legend
 var lg=[['Face midline','rgba(0,210,255,1)'],[a._ipl!=null?'Eye-line reference':'Horizontal reference','rgba(255,230,0,1)'],['Gum zeniths','rgba(255,140,40,1)'],['Contact points','rgba(190,120,255,1)'],['Edge curve','rgba(255,215,120,1)'],['Lower lip','rgba(120,255,120,1)']];
 if(a._upper)lg.push(['Upper lip','rgba(255,150,150,1)']);if(a._comm)lg.push(['Mouth corners','rgba(255,90,200,1)']);
 lg.forEach(function(l,i){tag(l[0],S.W*0.02,S.H*0.05+i*fs*1.45,l[1])})}
function cleanDesign(g,D){var lw=Math.max(1.4,S.W/600),mm=D.mm,Ls=D.list.slice().sort(function(p,q){return Math.min(p.xm,p.xd)-Math.min(q.xm,q.xd)});
 function smooth(pts){g.beginPath();g.moveTo(pts[0][0],pts[0][1]);for(var i=1;i<pts.length-1;i++){var mx=(pts[i][0]+pts[i+1][0])/2,my=(pts[i][1]+pts[i+1][1])/2;g.quadraticCurveTo(pts[i][0],pts[i][1],mx,my)}var l=pts[pts.length-1];g.lineTo(l[0],l[1])}
 g.save();g.shadowColor='rgba(0,0,0,.55)';g.shadowBlur=lw*2;g.strokeStyle='rgba(255,255,255,.95)';g.lineWidth=lw;g.lineJoin='round';
 // gingival curve through the zeniths and incisal curve, extended past the last teeth
 var zp=Ls.map(function(t){return[t.xm+(t.xd-t.xm)*0.58,t.top]}),ext=D.half*0.12;
 zp.unshift([zp[0][0]-ext,zp[0][1]+(zp[0][1]-zp[1][1])*0.6]);zp.push([zp[zp.length-1][0]+ext,zp[zp.length-1][1]+(zp[zp.length-1][1]-zp[zp.length-2][1])*0.6]);smooth(zp);g.stroke();
 g.beginPath();for(var x=D.mid-D.half*1.12;x<=D.mid+D.half*1.12;x+=2){var y=D.inc(Math.min(Math.abs(x-D.mid),D.half*1.12));if(x<=D.mid-D.half*1.12+1)g.moveTo(x,y);else g.lineTo(x,y)}g.stroke();
 D.list.forEach(function(t){toothPath(g,t);g.stroke()});g.restore();
 // midline and incisal reference: fine gold dotted lines
 g.save();g.strokeStyle='rgba(232,196,106,.95)';g.lineWidth=Math.max(1,lw*0.7);g.setLineDash([lw*1.2,lw*1.6]);
 var a=S.a,ang=a._ipl||0;g.beginPath();g.moveTo(D.mid+Math.sin(ang)*S.H,-S.H*0+0);g.moveTo(D.mid-Math.sin(ang)*(D.incC),0);g.lineTo(D.mid+Math.sin(ang)*(S.H-D.incC),S.H);g.stroke();
 g.beginPath();g.moveTo(0,D.incC-Math.tan(ang)*D.mid);g.lineTo(S.W,D.incC+Math.tan(ang)*(S.W-D.mid));g.stroke();g.restore()}
// "Clinical photo" style: mimics a retracted photo with a black contrastor behind the upper teeth
function clinical(c,D){var a=S.a,mm=D.mm,W=S.W,H=S.H,g=c.getContext('2d');
 var m=document.createElement('canvas');m.width=W;m.height=H;var mg=m.getContext('2d');mg.filter='blur('+Math.max(1,mm*0.25)+'px)';mg.fillStyle='#fff';mouthPath(mg,D);mg.fill();
 var md=mg.getImageData(0,0,W,H).data,im=g.getImageData(0,0,W,H),d=im.data,rs=0,gs=0,bs=0,n=0;
 var lim=new Float32Array(W);for(var x=0;x<W;x++){var dx=Math.min(Math.abs(x-D.mid),D.half*1.15);lim[x]=D.inc(dx)+0.5*mm}
 for(var y=0;y<H;y++)for(var x2=0;x2<W;x2++){var i=(y*W+x2)*4,mk=md[i+3]/255;if(mk<0.02)continue;
  var r=d[i],gg=d[i+1],b=d[i+2],mx=Math.max(r,gg,b),mn=Math.min(r,gg,b),lum=(0.299*r+0.587*gg+0.114*b)/255,sat=mx?(mx-mn)/mx:0,red=(r-gg)/255;
  var keep;
  if(y>lim[x2])keep=0; // contrastor hides the lower arch
  else{var tooth=clamp((0.2-red)/0.1,0,1)*clamp((lum-0.3)/0.15,0,1)*clamp((0.6-sat)/0.15,0,1),gum=clamp((red-0.12)/0.1,0,1)*clamp((lum-0.22)/0.12,0,1);keep=clamp(Math.max(tooth,gum)*1.4,0,1);
   if(tooth>0.6){rs+=r;gs+=gg;bs+=b;n++}}
  var k=1-mk*(1-keep);d[i]=r*k;d[i+1]=gg*k;d[i+2]=b*k}
 // white balance on the teeth + gentle contrast, like a flash photo
 var fr=1,fg=1,fb=1;if(n>50){var ar=rs/n,ag=gs/n,ab=bs/n,L=(ar+ag+ab)/3,tl=clamp(L*1.12,150,235);fr=clamp(tl*1.02/ar,0.85,1.35);fg=clamp(tl*0.99/ag,0.85,1.35);fb=clamp(tl*0.94/ab,0.85,1.35)}
 for(var j=0;j<d.length;j+=4){d[j]=clamp((d[j]*fr-128)*1.08+128,0,255);d[j+1]=clamp((d[j+1]*fg-128)*1.08+128,0,255);d[j+2]=clamp((d[j+2]*fb-128)*1.08+128,0,255)}
 g.putImageData(im,0,0);
 // crop to the smile, 16:9
 var p=a.mouth_polygon,xs=[],ys=[];if(p&&p.length){p.forEach(function(q){xs.push(q[1]*W/1000);ys.push(q[0]*H/1000)})}else{for(var k2 in D.T){var t=D.T[k2];xs.push(t.x0,t.x1);ys.push(t.y0,t.y1)}}
 var x0=Math.min.apply(0,xs)-2*mm,x1=Math.max.apply(0,xs)+2*mm,y0=Math.min.apply(0,ys)-5*mm,y1=Math.max.apply(0,ys)+3*mm,cw=x1-x0,ch=Math.max(y1-y0,cw*9/16),cy=(y0+y1)/2;
 x0=clamp(x0,0,W-1);cw=Math.min(cw,W-x0);var sy=clamp(cy-ch/2,0,H-1);ch=Math.min(ch,H-sy);
 var o=document.createElement('canvas'),k3=Math.min(3,1400/cw);o.width=Math.round(cw*k3);o.height=Math.round(ch*k3);var og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(c,x0,sy,cw,ch,0,0,o.width,o.height);o._t=[x0,sy,k3];return o}
function render(view){var k=view+'|'+S.ratio+'|'+S.shade+'|'+S.outline+'|'+S.brace+'|'+S.form+'|'+S.wh+'|'+(S.face&&FULL?1:0)+'|'+(S.clin?1:0)+'|'+S.eyes;if(S.cache[k])return S.cache[k];
 var D=design(),cg=baseCanvas(),c=cg[0],g=cg[1];
 if(!D)return beforeURL;
 if(S.clin&&(view=='design'||view=='dsd'||view=='analysis')){var o=clinical(c,D),og=o.getContext('2d'),t=o._t;og.setTransform(t[2],0,0,t[2],-t[0]*t[2],-t[1]*t[2]);og.lineWidth=1;
  if(view=='design')cleanDesign(og,D);else if(view=='dsd')dsdLines(og,D);else lines(og,D,{boxes:1,mid:1,lip:1});var u0=o.toDataURL('image/jpeg',0.9);S.cache[k]=u0;return u0}
 if(view=='analysis')lines(g,D,{boxes:1,mid:1,lip:1});
 else if(view=='white')whiten(c,g,D);
 else if(view=='design'){cleanDesign(g,D)}
 else if(view=='dsd'){dsdLines(g,D)}
 else if(view=='mockup'){whiten(c,g,D);mockup(c,g,D);if(S.outline)lines(g,D,{mid:1})}
 else if(view=='braces'){braces(c,g,D,S.brace)}
 var u=(S.clin?clinical(c,D):faceWrap(c)).toDataURL('image/jpeg',0.9);S.cache[k]=u;return u}
function faceWrap(c){if(!S.face||!FULL||!FULL.crop)return c;var I=FULL.img,W=I.naturalWidth||I.width,H=I.naturalHeight||I.height,k=Math.min(1,1400/Math.max(W,H)),cr=FULL.crop;
 var o=document.createElement('canvas');o.width=Math.round(W*k);o.height=Math.round(H*k);var og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(I,0,0,o.width,o.height);og.drawImage(c,0,0,c.width,c.height,cr[0]*k,cr[1]*k,cr[2]*k,cr[3]*k);maskEyes(o,k);return o}
function maskEyes(o,k){var e=FULL&&FULL.eyes;if(S.eyes=='off'||!e)return;var g=o.getContext('2d'),x1=e[0]*k,y1=e[1]*k,x2=e[2]*k,y2=e[3]*k,d=Math.hypot(x2-x1,y2-y1),a=Math.atan2(y2-y1,x2-x1),cx=(x1+x2)/2,cy=(y1+y2)/2,w=d*1.55,h=d*0.42;
 g.save();g.translate(cx,cy);g.rotate(a);g.beginPath();rrect(g,-w/2,-h*0.55,w,h,h*0.18);
 if(S.eyes=='bar'){g.fillStyle='#111';g.fill()}
 else{g.clip();g.rotate(-a);g.translate(-cx,-cy);var t=document.createElement('canvas');t.width=o.width;t.height=o.height;t.getContext('2d').drawImage(o,0,0);g.filter='blur('+Math.max(8,d*0.12)+'px)';g.drawImage(t,0,0);g.filter='none';g.drawImage(t,0,0,0,0);var t2=g.globalAlpha;g.globalAlpha=0.5;g.filter='blur('+Math.max(12,d*0.2)+'px)';g.drawImage(t,0,0);g.filter='none';g.globalAlpha=t2}
 g.restore()}
function beforeShown(){if(S.clin){var D0=design();if(D0){if(!S.cache.cb)S.cache.cb=clinical(baseCanvas()[0],D0).toDataURL('image/jpeg',0.9);return S.cache.cb}}if(!S.face||!FULL)return beforeURL;if(!FACEB||FACEB.k!=S.eyes)FACEB={k:S.eyes,u:faceWrap(baseCanvas()[0]).toDataURL('image/jpeg',0.9)};return FACEB.u}

/* ---------- reel maker: animated before/after video (9:16) ---------- */
function loadImg(u){return new Promise(function(res,rej){var i=new Image();i.onload=function(){res(i)};i.onerror=rej;i.src=u})}
function reelMime(){var c=['video/mp4;codecs=avc1.42E01E','video/mp4','video/webm;codecs=vp9','video/webm'];for(var i=0;i<c.length;i++)if(window.MediaRecorder&&MediaRecorder.isTypeSupported(c[i]))return c[i];return ''}
function makeReel(bu,au,tpl,label,cb,prog){Promise.all([loadImg(bu),loadImg(au)]).then(function(im){var B=im[0],A=im[1];
 var W=1080,H=1920,cv=document.createElement('canvas');cv.width=W;cv.height=H;var g=cv.getContext('2d');
 var px=60,py=330,pw=W-120,ph=1240,k=Math.min(pw/B.width,ph/B.height),iw=B.width*k,ih=B.height*k,ix=px+(pw-iw)/2,iy=py+(ph-ih)/2;
 var DUR=tpl=='split'?6000:9000;
 function txt(t,x,y,sz,col,al,wt){g.font=(wt||'700')+' '+sz+'px system-ui,sans-serif';g.fillStyle=col;g.textAlign=al||'center';g.fillText(t,x,y)}
 function frame(t){var u=t/DUR;g.fillStyle='#0b2236';g.fillRect(0,0,W,H);
  txt('SMILE DESIGN',W/2,150,64,'#ffffff');txt(label,W/2,225,40,'#d8c3a5','center','500');
  g.save();g.beginPath();g.rect(ix,iy,iw,ih);g.clip();
  if(tpl=='toggle'){var on=(u>0.22&&u<0.55)||u>0.78,sw=Math.min(1,Math.max(0,u<0.55?(u-0.22)/0.04:(u-0.78)/0.04));if(u>=0.55&&u<0.78)sw=Math.max(0,1-(u-0.55)/0.04);
   g.drawImage(B,ix,iy,iw,ih);g.globalAlpha=sw;g.drawImage(A,ix,iy,iw,ih);g.globalAlpha=1;
   if(sw>0&&sw<1){g.fillStyle='rgba(255,255,255,'+(0.5*(1-Math.abs(sw*2-1)))+')';g.fillRect(ix,iy,iw,ih)}
   g.restore();var tx=ix+50,ty=iy+50,tw=190,th=96;g.save();g.shadowColor='rgba(255,255,255,'+(0.4+0.5*sw)+')';g.shadowBlur=30;rrect(g,tx,ty,tw,th,th/2);g.fillStyle=sw>0.5?'#ffffff':'rgba(255,255,255,.35)';g.fill();g.restore();
   g.beginPath();g.arc(tx+th/2+(tw-th)*sw,ty+th/2,th/2-8,0,7);g.fillStyle=sw>0.5?'#e9eef2':'#ffffff';g.fill();
   txt(sw>0.5?'AFTER':'BEFORE',ix+iw-40,iy+ih-40,48,'#ffffff','right')}
  else if(tpl=='swipe'){var p=u<0.15?0:u<0.5?(u-0.15)/0.35:u<0.62?1:u<0.85?1-(u-0.62)/0.23*0.5:0.5,ease=p<0.5?2*p*p:1-Math.pow(-2*p+2,2)/2,sx=ix+iw*ease;
   g.drawImage(B,ix,iy,iw,ih);g.beginPath();g.rect(ix,iy,sx-ix,ih);g.save();g.clip();g.drawImage(A,ix,iy,iw,ih);g.restore();g.restore();
   g.fillStyle='#fff';g.fillRect(sx-3,iy,6,ih);g.beginPath();g.arc(sx,iy+ih/2,56,0,7);g.lineWidth=8;g.strokeStyle='#fff';g.stroke();txt('◀ ▶',sx,iy+ih/2+14,36,'#fff');
   txt('AFTER',ix+40,iy+ih-40,44,'#ffffff','left');txt('BEFORE',ix+iw-40,iy+ih-40,44,'#ffffff','right')}
  else{g.restore();var hh=(ph-30)/2,k2=Math.min(pw/B.width,hh/B.height),w2=B.width*k2,h2=B.height*k2,x2=px+(pw-w2)/2,fa=Math.min(1,u*3),fb=Math.min(1,Math.max(0,(u-0.25)*3));
   g.globalAlpha=fa;g.drawImage(B,x2,py,w2,h2);g.globalAlpha=fb;g.drawImage(A,x2,py+hh+30,w2,h2);g.globalAlpha=1;txt('BEFORE',x2+30,py+70,44,'#fff','left');if(fb>0)txt('AFTER',x2+30,py+hh+100,44,'#fff','left')}
  g.restore&&0;
  txt(CLINIC,W/2,H-250,46,'#ffffff');txt(PHONE+'  ·  Jogeshwari East, Mumbai',W/2,H-185,34,'#d8c3a5','center','500');
  txt('Computer simulation for illustration. Results vary.',W/2,H-110,28,'rgba(255,255,255,.6)','center','400')}
 if(prog=='snap'){cb([0.1,0.3,0.5,0.9].map(function(f){frame(f*DUR);return cv.toDataURL('image/jpeg',0.7)}));return}
 var mime=reelMime();if(!mime||!cv.captureStream){cb(null,'Video recording is not supported in this browser. Please use Chrome.');return}
 var st=cv.captureStream(30),rec=new MediaRecorder(st,{mimeType:mime,videoBitsPerSecond:6000000}),ch=[];rec.ondataavailable=function(e){if(e.data&&e.data.size)ch.push(e.data)};
 rec.onstop=function(){cb(new Blob(ch,{type:mime.split(';')[0]}))};
 frame(0);rec.start(250);var t0=performance.now();
 (function loop(){var t=performance.now()-t0;frame(Math.min(t,DUR));prog&&prog(Math.min(1,t/DUR));if(t<DUR+150)requestAnimationFrame(loop);else rec.stop()})()}).catch(function(e){cb(null,'Could not prepare the images ('+e+').')})}
function reelUI(){var box=document.getElementById('reel');if(!box)return;
 box.innerHTML='<h3>Make a before/after reel</h3><p class="muted">A 9:16 video for Instagram Reels, WhatsApp status or Google. Uses the view selected above.</p><div class="ctl"><label>Style<select id="rtp"><option value="toggle">Toggle switch</option><option value="swipe">Swipe reveal</option><option value="split">Before above, after below</option></select></label><button type="button" class="btn" id="rgo">Create video</button></div><p class="muted" id="rmsg"></p><div id="rout"></div>';
 document.getElementById('rgo').addEventListener('click',function(){var b=this,msg=document.getElementById('rmsg'),out=document.getElementById('rout'),v=S.view=='analysis'||S.view=='dsd'?'mockup':S.view;
  var au=v=='ai'?S.after:render(v),bu=beforeShown(),lbl=v=='braces'?BR[S.brace].n+' braces preview':v=='white'?'Teeth whitening preview':v=='design'?'Smile design plan':'Smile makeover preview';
  b.disabled=true;out.innerHTML='';msg.className='muted';msg.textContent='Recording the video… 0%';
  makeReel(bu,au,document.getElementById('rtp').value,lbl,function(blob,err){b.disabled=false;if(!blob){msg.className='muted err';msg.textContent=err;return}
   var ext=blob.type.indexOf('mp4')>=0?'mp4':'webm',url=URL.createObjectURL(blob),name='smile-reel.'+ext;msg.textContent='Video ready ('+ext.toUpperCase()+').'+(ext=='webm'?' If Instagram does not accept it, send it to yourself on WhatsApp first, or update Chrome.':'');
   out.innerHTML='<video src="'+url+'" controls playsinline loop style="width:100%;max-width:320px;display:block;margin:8px 0"></video><div class="cta"><a class="btn" href="'+url+'" download="'+name+'">Download video</a> <button type="button" class="btn o2" id="rsh">Share</button></div><p class="muted">Only post a patient’s face with their written consent.</p>';
   var sh=document.getElementById('rsh'),f=new File([blob],name,{type:blob.type});if(!(navigator.canShare&&navigator.canShare({files:[f]})))sh.style.display='none';
   sh.addEventListener('click',function(){navigator.share({files:[f],title:'Smile design'}).catch(function(){})})},function(p){msg.textContent='Recording the video… '+Math.round(p*100)+'%'})})}
/* ---------- braces preview ---------- */
var BR={metal:{n:'Metal',t:'Most visible. Strong and reliable for every case. Lowest cost.'},
 ceramic:{n:'Ceramic',t:'Tooth-coloured brackets, much less noticeable. Costs more; ties can stain.'},
 self:{n:'Self-ligating',t:'Built-in clip instead of elastic ties. Easier cleaning, shorter visits. Costs more.'},
 lingual:{n:'Lingual',t:'Fixed behind the teeth, so nothing shows from the front. Harder to clean, highest cost.'},
 aligner:{n:'Aligners',t:'Clear removable trays, almost invisible. Wear 20–22 hours a day. Best for mild to moderate cases.'}};
function toothColour(g,t){var x=Math.round((t.x0+t.x1)/2),y=Math.round(t.y0+(t.y1-t.y0)*0.55);var p=g.getImageData(clamp(x-2,0,S.W-5),clamp(y-2,0,S.H-5),5,5).data,r=0,gg=0,b=0,n=0;for(var i=0;i<p.length;i+=4){r+=p[i];gg+=p[i+1];b+=p[i+2];n++}return[r/n,gg/n,b/n]}
function rrect(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.lineTo(x+w-r,y);g.quadraticCurveTo(x+w,y,x+w,y+r);g.lineTo(x+w,y+h-r);g.quadraticCurveTo(x+w,y+h,x+w-r,y+h);g.lineTo(x+r,y+h);g.quadraticCurveTo(x,y+h,x,y+h-r);g.lineTo(x,y+r);g.quadraticCurveTo(x,y,x+r,y);g.closePath()}
function braces(c,g,D,kind){var T=D.T,mm=D.mm,ids=ORDER.filter(function(id){return T[id]});if(ids.length<3)return;
 g.save();mouthPath(g,D);g.clip();
 if(kind=='lingual'){g.restore();return}
 if(kind=='aligner'){
  var pad=0.5*mm,sid=ids.slice().sort(function(a,b){return T[a].x0-T[b].x0});
  function tray(){g.beginPath();var f=T[sid[0]];g.moveTo(f.x0-pad*0.6,f.y0+pad);sid.forEach(function(id){var t=T[id],w=t.x1-t.x0;g.lineTo(t.x0+w*0.1,t.y0-pad*0.8);g.quadraticCurveTo(t.x0+w*0.5,t.y0-pad*1.6,t.x1-w*0.1,t.y0-pad*0.8)});var l2=T[sid[sid.length-1]];g.lineTo(l2.x1+pad*0.6,l2.y0+pad);
   for(var i=sid.length-1;i>=0;i--){var t=T[sid[i]],w=t.x1-t.x0,r=Math.min(w*0.3,(t.y1-t.y0)*0.3),xa=i==sid.length-1?t.x1+pad*0.6:t.x1,xb=i==0?t.x0-pad*0.6:t.x0,yb=t.y1+pad;
    g.lineTo(xa,yb-r);g.quadraticCurveTo(xa,yb,xa-r,yb);g.lineTo(xb+r,yb);g.quadraticCurveTo(xb,yb,xb,yb-r)}
   g.closePath()}
  var y0=Math.min.apply(0,ids.map(function(id){return T[id].y0})),y1=Math.max.apply(0,ids.map(function(id){return T[id].y1}));
  g.save();tray();g.clip();
  var lg=g.createLinearGradient(0,y0-pad,0,y1+pad);lg.addColorStop(0,'rgba(255,255,255,.45)');lg.addColorStop(0.3,'rgba(235,245,255,.2)');lg.addColorStop(0.75,'rgba(230,242,255,.22)');lg.addColorStop(1,'rgba(255,255,255,.55)');g.fillStyle=lg;g.fillRect(0,0,S.W,S.H);
  // glossy reflection band across the arch, and a shine on each tooth
  g.save();g.filter='blur('+Math.max(1,mm*0.35)+'px)';g.strokeStyle='rgba(255,255,255,.65)';g.lineWidth=mm*0.7;g.beginPath();sid.forEach(function(id,i){var t=T[id],x=(t.x0+t.x1)/2,y=t.y0+(t.y1-t.y0)*0.32;if(i)g.lineTo(x,y);else g.moveTo(x,y)});g.stroke();g.restore();
  sid.forEach(function(id){var t=T[id],w=t.x1-t.x0,h=t.y1-t.y0,hl=g.createLinearGradient(t.x0,0,t.x1,0);hl.addColorStop(0.15,'rgba(255,255,255,0)');hl.addColorStop(0.27,'rgba(255,255,255,.38)');hl.addColorStop(0.36,'rgba(255,255,255,0)');g.fillStyle=hl;g.fillRect(t.x0,t.y0+h*0.15,w,h*0.6);
   g.strokeStyle='rgba(255,255,255,.55)';g.lineWidth=Math.max(1,mm*0.15);g.beginPath();g.moveTo(t.x1,t.y0);g.lineTo(t.x1,t.y1-h*0.2);g.stroke()});
  g.restore();
  g.save();g.shadowColor='rgba(0,0,0,.4)';g.shadowBlur=mm*0.4;tray();g.lineWidth=Math.max(1.4,mm*0.25);g.strokeStyle='rgba(255,255,255,.92)';g.stroke();g.restore();
  // attachments (tooth-coloured bumps)
  ['UR3','UL3','UR4','UL4','UR2','UL2'].forEach(function(id){var t=T[id];if(!t)return;var col=toothColour(g,t),w=Math.min((t.x1-t.x0)*0.5,3*mm),h=w*0.6,x=(t.x0+t.x1)/2-w/2,y=t.y0+(t.y1-t.y0)*0.45;
   g.save();g.shadowColor='rgba(60,40,30,.45)';g.shadowBlur=mm*0.35;g.shadowOffsetY=mm*0.12;rrect(g,x,y,w,h,h*0.35);var ag=g.createLinearGradient(0,y,0,y+h);ag.addColorStop(0,rgb(col,1.15,1));ag.addColorStop(1,rgb(col,0.92,1));g.fillStyle=ag;g.fill();g.restore();
   g.fillStyle='rgba(255,255,255,.7)';g.fillRect(x+w*0.15,y+h*0.15,w*0.5,h*0.18)});
  g.restore();return}
 var pts=ids.map(function(id){var t=T[id],w=t.x1-t.x0,h=t.y1-t.y0,bw=clamp(w*0.58,2.6*mm,(id[2]=='3'?4.2:3.8)*mm),bh=bw*(id[2]=='4'?0.8:0.88);bw=Math.min(bw,w*0.8);return{id:id,t:t,cx:(t.x0+t.x1)/2,cy:t.y1-Math.min(h*0.48,4.4*mm),bw:bw,bh:bh}});
 // smooth the bracket line (brackets sit along an even arch, like a real bonding)
 for(var i=1;i<pts.length-1;i++)pts[i].cy=(pts[i-1].cy+2*pts[i].cy+pts[i+1].cy)/4;
 var MET=kind!='ceramic';
 function wire(){var ww=Math.max(1.6,0.5*mm);g.save();g.lineCap='round';g.lineJoin='round';
  g.beginPath();g.moveTo(pts[0].cx-pts[0].bw*1.4,pts[0].cy+mm*0.25);for(var i=0;i<pts.length-1;i++){var p=pts[i],q=pts[i+1];g.quadraticCurveTo(p.cx,p.cy,(p.cx+q.cx)/2,(p.cy+q.cy)/2)}var l=pts[pts.length-1];g.quadraticCurveTo(l.cx,l.cy,l.cx+l.bw*1.4,l.cy+mm*0.25);
  g.shadowColor='rgba(0,0,0,.45)';g.shadowBlur=mm*0.3;g.shadowOffsetY=mm*0.15;g.strokeStyle='#5f676e';g.lineWidth=ww;g.stroke();g.shadowColor='transparent';
  g.strokeStyle='#c9d0d6';g.lineWidth=ww*0.6;g.stroke();g.translate(0,-ww*0.18);g.strokeStyle='rgba(255,255,255,.95)';g.lineWidth=ww*0.22;g.stroke();g.restore()}
 function bracket(p){var x=p.cx-p.bw/2,y=p.cy-p.bh/2,w=p.bw,h=p.bh,col=MET?null:toothColour(g,p.t);
  // shadow + base pad
  g.save();g.shadowColor='rgba(40,25,20,.5)';g.shadowBlur=mm*0.5;g.shadowOffsetY=mm*0.2;rrect(g,x,y,w,h,h*0.18);
  var bg=g.createLinearGradient(x,y,x+w,y+h);if(MET){bg.addColorStop(0,'#e9edf0');bg.addColorStop(0.5,'#8d979f');bg.addColorStop(1,'#59626a')}else{bg.addColorStop(0,rgb(col,1.1,1));bg.addColorStop(1,rgb(col,0.88,1))}g.fillStyle=bg;g.fill();g.restore();
  // four tie wings
  var ww=w*0.36,wh=h*0.36,cs=[[x+w*0.06,y+h*0.05],[x+w*0.58,y+h*0.05],[x+w*0.06,y+h*0.59],[x+w*0.58,y+h*0.59]];
  cs.forEach(function(q){rrect(g,q[0],q[1],ww,wh,wh*0.3);var wg=g.createLinearGradient(q[0],q[1],q[0],q[1]+wh);
   if(MET){wg.addColorStop(0,'#ffffff');wg.addColorStop(0.35,'#d6dde2');wg.addColorStop(1,'#7b858d')}else{wg.addColorStop(0,'rgba(255,255,255,.95)');wg.addColorStop(1,rgb(col,0.95,1))}
   g.fillStyle=wg;g.fill();g.lineWidth=Math.max(0.8,mm*0.06);g.strokeStyle=MET?'rgba(45,50,55,.8)':'rgba(150,140,130,.6)';g.stroke();
   g.fillStyle='rgba(255,255,255,'+(MET?0.9:0.7)+')';g.fillRect(q[0]+ww*0.15,q[1]+wh*0.12,ww*0.4,wh*0.18)});
  // slot
  g.fillStyle=MET?'rgba(35,40,45,.85)':'rgba(120,110,100,.5)';g.fillRect(x+w*0.02,p.cy-h*0.07,w*0.96,h*0.14)}
 pts.forEach(bracket);wire();
 pts.forEach(function(p){var x=p.cx-p.bw/2,y=p.cy-p.bh/2,w=p.bw,h=p.bh;
  if(kind=='metal'){g.save();g.beginPath();g.ellipse(p.cx,p.cy,w*0.4,h*0.4,0,0,Math.PI*2);g.lineWidth=Math.max(1.4,h*0.17);g.strokeStyle='rgba(150,158,166,.9)';g.stroke();g.lineWidth=Math.max(0.6,h*0.05);g.strokeStyle='rgba(255,255,255,.7)';g.stroke();g.restore()}
  else if(kind=='ceramic'){g.save();g.beginPath();g.ellipse(p.cx,p.cy,w*0.4,h*0.4,0,0,Math.PI*2);g.lineWidth=Math.max(1,h*0.15);g.strokeStyle='rgba(248,246,240,.85)';g.stroke();g.restore()}
  else if(kind=='self'){g.save();rrect(g,x+w*0.12,y+h*0.2,w*0.76,h*0.6,h*0.12);var dg=g.createLinearGradient(0,y,0,y+h);dg.addColorStop(0,'#ffffff');dg.addColorStop(0.5,'#c3ccd3');dg.addColorStop(1,'#78828a');g.fillStyle=dg;g.fill();g.strokeStyle='rgba(40,45,50,.75)';g.lineWidth=Math.max(0.8,mm*0.07);g.stroke();g.fillStyle='rgba(255,255,255,.85)';g.fillRect(x+w*0.2,y+h*0.26,w*0.5,h*0.1);g.restore()}});
 g.restore()}
function mouthBox(D){var xs=[],ys=[];for(var k in D.T){var t=D.T[k];xs.push(t.x0,t.x1);ys.push(t.y0,t.y1)}var x0=Math.min.apply(0,xs),x1=Math.max.apply(0,xs),y0=Math.min.apply(0,ys),y1=Math.max.apply(0,ys),w=x1-x0,h=y1-y0;
 x0=clamp(x0-w*0.18,0,S.W);x1=clamp(x1+w*0.18,0,S.W);y0=clamp(y0-h*0.6,0,S.H);y1=clamp(y1+h*0.9,0,S.H);return[x0,y0,x1-x0,y1-y0]}
function cropURL(u,D,cb){var im=new Image();im.onload=function(){var b=mouthBox(D),c=document.createElement('canvas');c.width=Math.round(b[2]);c.height=Math.round(b[3]);c.getContext('2d').drawImage(im,b[0],b[1],b[2],b[3],0,0,c.width,c.height);cb(c.toDataURL('image/jpeg',0.9))};im.src=u}

/* ---------- report ---------- */
function metrics(D){var T=D.T,mm=D.mm,R=[];
 function wmm(t){return t?8.5*(t.x1-t.x0)/D.cwNow:null}function hmm(t){return t?8.5*(t.y1-t.y0)/D.cwNow:null}
 var cwh=avg([T.UR1&&(T.UR1.x1-T.UR1.x0)/(T.UR1.y1-T.UR1.y0),T.UL1&&(T.UL1.x1-T.UL1.x0)/(T.UL1.y1-T.UL1.y0)]);
 function rat(a,b){return a&&b?(a.x1-a.x0)/(b.x1-b.x0):null}
 var lc=avg([rat(T.UR2,T.UR1),rat(T.UL2,T.UL1)]),kl=avg([rat(T.UR3,T.UR2),rat(T.UL3,T.UL2)]);
 var sym=T.UR1&&T.UL1?Math.min(T.UR1.x1-T.UR1.x0,T.UL1.x1-T.UL1.x0)/Math.max(T.UR1.x1-T.UR1.x0,T.UL1.x1-T.UL1.x0):null;
 var a=S.a,ms=a.facial_midline_x!=null&&a.dental_midline_x!=null?Math.abs(a.facial_midline_x-a.dental_midline_x)*S.W/1000/mm:null;
 var tilt=T.UR3&&T.UL3?Math.abs((Math.atan2(T.UL3.y1-T.UR3.y1,((T.UL3.x0+T.UL3.x1)-(T.UR3.x0+T.UR3.x1))/2)-(a._ipl||0)*(S.H/S.W>0?1:1))*180/Math.PI):null;
 var arc=T.UR3&&T.UL3&&(T.UR1||T.UL1)?(avg([T.UR1&&T.UR1.y1,T.UL1&&T.UL1.y1])-avg([T.UR3.y1,T.UL3.y1]))/mm:null;
 var gum=T.UR1&&T.UL1?Math.abs(T.UR1.y0-T.UL1.y0)/mm:null;
 var lenC=avg([hmm(T.UR1),hmm(T.UL1)]);
 function p(v){return v==null?null:Math.round(v*100)+'%'}function m(v){return v==null?null:v.toFixed(1)+' mm'}
 R.push(['Central incisor width ÷ height',p(cwh),'75–80%',cwh!=null&&cwh>=0.72&&cwh<=0.84]);
 R.push(['Central incisor length (est.)',m(lenC),'10.5–11 mm',lenC!=null&&lenC>=9.8&&lenC<=11.8]);
 R.push(['Lateral ÷ central (front view)',p(lc),'62–75%',lc!=null&&lc>=0.6&&lc<=0.78]);
 R.push(['Canine ÷ lateral (front view)',p(kl),'62–80%',kl!=null&&kl>=0.6&&kl<=0.82]);
 R.push(['Central incisors match',p(sym),'95–100%',sym!=null&&sym>=0.93]);
 R.push(['Midline shift',m(ms),'under 1.5 mm',ms!=null&&ms<1.5]);
 R.push([a._ipl!=null?'Tilt of the smile vs eye line':'Tilt of the smile (canine to canine)',tilt==null?null:tilt.toFixed(1)+'°','under 2°',tilt!=null&&tilt<2]);
 R.push(['Smile arc (centrals lower than canines)',m(arc),'0.5–2 mm',arc!=null&&arc>=0.4&&arc<=2.5]);
 R.push(['Gum line of the two centrals',m(gum),'level (under 0.5 mm)',gum!=null&&gum<0.6]);
 return R}
function toothTable(D){var rows='';[1,2,3].forEach(function(n){var r=D.T['UR'+n],l=D.T['UL'+n],cur=avg([r&&8.5*(r.x1-r.x0)/D.cwNow,l&&8.5*(l.x1-l.x0)/D.cwNow]);
 var des=8.5*[D.wc,D.wl,D.wk][n-1]/D.cwNow;rows+='<tr><td>'+NUM[n]+'</td><td>'+(cur==null?'–':cur.toFixed(1)+' mm')+'</td><td>'+des.toFixed(1)+' mm</td></tr>'});return rows}

/* ---------- UI ---------- */
function show(a,after){if(LIPS&&a){a.mouth_polygon=LIPS.inner;a._lower=LIPS.lower;a._ipl=LIPS.ipl;a._comm=LIPS.comm;a._upper=LIPS.upper}S.a=a;S.after=after;S.cache={};var h='<div class="res"><h2>Your smile design</h2>';
 if(!a.photo_ok){h+='<p>'+esc(a.photo_note||'The photo was not clear enough.')+'</p><p>Please retake a front-facing photo with a natural full smile, upper teeth clearly visible, in good daylight, phone at mouth level.</p></div>';out.innerHTML=h;return}
 var im=new Image();im.onload=function(){S.img=im;S.W=im.width;S.H=im.height;build()};im.src=beforeURL}
function build(){var a=S.a,D=design();
 var views=[['mockup','Smile mock-up'],['braces','Braces preview'],['dsd','DSD lines'],['design','Ideal design'],['white','Whitening only'],['analysis','Analysis']];if(S.after)views.unshift(['ai','AI photo']);
 if(S.after&&S.view=='mockup')S.view='ai';
 var h='<div class="res"><h2>Your smile design</h2><div class="seg" id="vw">'+views.map(function(v){return'<button type="button" data-v="'+v[0]+'"'+(v[0]==S.view?' class="on"':'')+'>'+v[1]+'</button>'}).join('')+'</div>';
 h+='<div class="seg sm" id="bt" style="display:none">'+Object.keys(BR).map(function(k){return'<button type="button" data-b="'+k+'"'+(k==S.brace?' class="on"':'')+'>'+BR[k].n+'</button>'}).join('')+'</div>';
 h+='<div id="cmp"></div><p class="muted" id="cap"></p><div id="bx"></div>';
 h+='<div class="ctl"><label>Proportion<select id="rt"><option value="red70">Natural (RED 70%)</option><option value="red75">Soft (RED 75%)</option><option value="red80">Wide (RED 80%)</option><option value="golden">Golden proportion (62%)</option></select></label>';
 h+='<label>Tooth shape<select id="fm">'+Object.keys(FORMS).map(function(k){return'<option value="'+k+'">'+FORMS[k].n+'</option>'}).join('')+'</select></label>';
 h+='<label>Central width : length<select id="wh"><option value="0.75">75% (longer)</option><option value="0.78">78% (classic)</option><option value="0.8">80%</option><option value="0.85">85% (shorter)</option></select></label>';
 h+='<label>Shade<select id="sh"><option value="a2">Natural (A2)</option><option value="a1">Bright natural (A1)</option><option value="b1">White (B1)</option><option value="bl">Extra white (bleach)</option></select></label>';
 h+='<label>Hide eyes (privacy)<select id="ey"><option value="off">Show</option><option value="bar">Black bar</option><option value="blur">Blur</option></select></label>';
 h+='<label class="ck2"><input type="checkbox" id="cl"> Clinical photo style (black background)</label><label class="ck2"><input type="checkbox" id="fc"'+(S.face?' checked':'')+'> Show full face</label><label class="ck2"><input type="checkbox" id="ol"'+(S.outline?' checked':'')+'> Show midline</label><button type="button" class="btn o2" id="dl">Download image</button></div>';
 h+='<p class="muted"><b>Simulation only.</b> These pictures are drawn by the computer from your photo to explain ideal proportions. They are not a promise of results. Your plan depends on your teeth, gums and bite, and is decided after an examination.</p>';
 h+='<div id="reel" class="note" style="background:#fff"></div>';
 h+='<h3>Your measurements</h3><div class="cmpw"><table class="cmp" style="min-width:0"><thead><tr><th>Measure</th><th>Yours</th><th>Ideal</th><th></th></tr></thead><tbody>'+metrics(D).map(function(r){return'<tr><td>'+r[0]+'</td><td>'+(r[1]==null?'–':r[1])+'</td><td>'+r[2]+'</td><td>'+(r[1]==null?'':(r[3]?'<span class="ok">Within range</span>':'<span class="wn">Outside range</span>'))+'</td></tr>'}).join('')+'</tbody></table></div>';
 h+='<h3>Tooth widths: now and in the design</h3><div class="cmpw"><table class="cmp" style="min-width:0"><thead><tr><th>Tooth</th><th>Yours (est.)</th><th>Design</th></tr></thead><tbody id="tt">'+toothTable(D)+'</tbody></table></div>';
 h+='<p class="muted">Millimetres are estimated from your photo by assuming an average central incisor width of 8.5 mm, so treat them as approximate.</p>';
 if(a.findings&&a.findings.length){h+='<h3>What the AI noticed</h3><ul class="b">'+a.findings.map(function(o){return'<li>'+esc(o)+'</li>'}).join('')+'</ul>'}
 h+='<p>Options that can achieve a design like this include <a href="teeth-whitening.html">whitening</a>, <a href="fillings.html">tooth-coloured bonding</a>, veneers, <a href="crowns-bridges.html">crowns</a> and <a href="clear-aligners.html">aligners</a>. Dr. Tejas Pradhan has received your photo and can discuss what suits you.</p>';
 h+='<div class="cta"><a class="btn" href="'+WA+'">Book a smile design consultation</a></div></div>';
 out.innerHTML=h;
 document.getElementById('rt').value=S.ratio;document.getElementById('fm').value=S.form;document.getElementById('wh').value=String(S.wh);
 document.getElementById('fm').addEventListener('change',function(){S.form=this.value;document.getElementById('tt').innerHTML=toothTable(design());paint()});
 document.getElementById('wh').addEventListener('change',function(){S.wh=parseFloat(this.value);paint()});document.getElementById('sh').value=S.shade;
 document.getElementById('vw').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;S.view=b.getAttribute('data-v');[].forEach.call(this.children,function(x){x.className=x==b?'on':''});paint()});
 document.getElementById('bt').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;S.brace=b.getAttribute('data-b');[].forEach.call(this.children,function(x){x.className=x==b?'on':''});paint()});
 document.getElementById('rt').addEventListener('change',function(){S.ratio=this.value;document.getElementById('tt').innerHTML=toothTable(design());paint()});
 document.getElementById('sh').addEventListener('change',function(){S.shade=this.value;paint()});
 document.getElementById('ol').addEventListener('change',function(){S.outline=this.checked;paint()});
 document.getElementById('fc').addEventListener('change',function(){S.face=this.checked;paint()});
 document.getElementById('cl').addEventListener('change',function(){S.clin=this.checked;paint()});
 document.getElementById('ey').value=S.eyes;document.getElementById('ey').addEventListener('change',function(){S.eyes=this.value;paint()});if(!FULL||!FULL.eyes)document.getElementById('ey').parentNode.style.display='none';if(!FULL)document.getElementById('fc').parentNode.style.display='none';
 document.getElementById('dl').addEventListener('click',function(){var a2=document.createElement('a');a2.href=S.view=='ai'?S.after:render(S.view);a2.download='smile-design-'+S.view+'.jpg';document.body.appendChild(a2);a2.click();a2.remove()});
 paint();reelUI();out.scrollIntoView({behavior:'smooth'})}
var CAP={dsd:'DSD lines: the classic smile-design template on your photo. Blue: face midline. Yellow: horizontal reference parallel to your eyes. Orange dots: gum zeniths. Purple: contact points. Gold: biting-edge curve, which should follow the green lower lip. Percentages: central width ÷ length, and each tooth’s width compared with the tooth in front of it.',mockup:'Smile mock-up: your photo with ideal-proportion teeth drawn in, plus whitening. Drag the slider to compare with your current smile.',design:'Ideal design: the planned tooth outlines drawn on your own photo, with the gum curve and biting-edge curve, the face midline and the biting-edge reference (gold dotted). Drag the slider to compare.',white:'Whitening only: your own teeth at the chosen shade, without changing their shape.',analysis:'Analysis: yellow boxes mark your 8 front teeth (1 central, 2 lateral, 3 canine, 4 premolar). Blue: face midline. Red: teeth midline. Green: lower lip line that the tooth edges should follow.',ai:'AI photo: a realistic AI-generated preview of your smile after treatment.',braces:'Braces preview: how each type of braces or aligners would look on your current teeth (upper teeth shown). Pick a type above and drag the slider.'};
function paint(){var cmp=document.getElementById('cmp');if(!cmp)return;var u=S.view=='ai'?S.after:render(S.view);
 document.getElementById('cap').textContent=CAP[S.view]||'';document.getElementById('bt').style.display=S.view=='braces'?'flex':'none';
 var bx=document.getElementById('bx');bx.innerHTML='';
 if(S.view=='braces'){var D=design(),cur=S.brace;bx.innerHTML='<div class="note"><b>'+BR[cur].n+':</b> '+BR[cur].t+'</div><h3>All options on your smile</h3><div class="bg" id="bg"></div><p><a href="braces-comparison.html">Compare braces and aligners in detail</a></p>';
  var grid=document.getElementById('bg'),fc=S.face,cl0=S.clin;S.face=false;S.clin=false;Object.keys(BR).forEach(function(k){S.brace=k;var uu=render('braces');var fig=document.createElement('figure');fig.innerHTML='<img alt="'+BR[k].n+' preview"><figcaption>'+BR[k].n+'</figcaption>';grid.appendChild(fig);cropURL(uu,D,function(cu){fig.querySelector('img').src=cu});fig.addEventListener('click',function(){S.brace=k;[].forEach.call(document.getElementById('bt').children,function(x){x.className=x.getAttribute('data-b')==k?'on':''});paint()})});S.face=fc;S.clin=cl0;S.brace=cur;u=render('braces')}
 if(S.view=='analysis'){cmp.innerHTML='<div class="ba"><img src="'+u+'" alt="'+esc(S.view)+' view"></div>';return}
 cmp.innerHTML='<div class="ba"><img src="'+beforeShown()+'" alt="Before"><div class="af"><img src="'+u+'" alt="After simulation"></div><span class="tg l">Before</span><span class="tg r">'+(S.view=='braces'?BR[S.brace].n:(S.view=='white'?'Whitened':'Design'))+'</span><div class="hd"></div><input type="range" min="0" max="100" value="50" aria-label="Compare before and after"></div>';
 var ba=cmp.querySelector('.ba'),rg=ba.querySelector('input'),af=ba.querySelector('.af');var hd=ba.querySelector('.hd');function up(){af.style.clipPath='inset(0 0 0 '+rg.value+'%)';hd.style.left=rg.value+'%'}rg.addEventListener('input',up);up()}
window.__camGuide=function(c,ok){var g=c.getContext('2d'),G=geom(c.width,c.height);drawGuide(g,c.width,c.height,G,ok,null)};
window.__dsdTest=function(a,after,url,lips){beforeURL=url;LIPS=lips||null;show(a,after)};window.__render=function(v){return render(v)};window.__set=function(k,v){S[k]=v};window.__reel=function(b,a,t,cb){makeReel(b,a,t,'Smile makeover preview',cb,'snap')};window.__full=function(im,cr,ey){FULL={img:im,crop:cr,eyes:ey};FACEB=null};
})();
"""


def dsd_page():
    js = (DSD_JS.replace("__API__", DSD_API).replace("__CLINIC__", CLINIC.replace('"', "")).replace("__PHONE__", PHONE)
          .replace("__WA__", "https://wa.me/918369187806?text=" + quote("Hello, I tried the AI smile design on your website and would like a smile design consultation.")))
    ideal = [("Central incisor", "8.5–9 mm", "10.5–11 mm", "75–80%"), ("Lateral incisor", "6.5 mm", "9–9.5 mm", "70–75%"),
             ("Canine", "7.5 mm", "10 mm", "75–80%"), ("First premolar", "7 mm", "8–8.5 mm", "80–85%")]
    trs = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in ideal)
    body = (
        '<h2>AI digital smile design</h2>'
        '<p>Upload one front-facing smile photo. The AI marks your 8 upper front teeth, compares their proportions with ideal smile dimensions, '
        'and draws an ideal-proportion design and smile mock-up on your own photo. You can change the proportion and shade, compare before and after, and download the result.</p>'
        '<div class="note"><b>Please note:</b> the "after" picture is an AI simulation for ideas only. It is not a diagnosis or a guarantee. '
        'The real plan is made after an examination, X-rays and a discussion of options like whitening, bonding, veneers, crowns or aligners.</div>'
        + photo_guide() +
        '<form id="ds" class="scf" autocomplete="on">'
        '<label>Your name<input name="name" required maxlength="80" autocomplete="name"></label>'
        '<label>Mobile number<input name="phone" required inputmode="numeric" maxlength="14" autocomplete="tel" placeholder="10-digit number"></label>'
        '<button type="button" class="btn camb" id="dscam">📷 Open guided camera (recommended)</button>'
        '<p class="muted" style="margin:6px 0 0">The camera checks your position, smile and light, then takes the photo automatically.</p>'
        '<label>Or upload a smile photo<input id="dsf" type="file" accept="image/*"></label>'
        '<div id="dsp" class="prev one"></div>'
        '<p class="muted">For best results: face the camera straight, phone at mouth level, natural full smile showing your upper teeth, good daylight, no filter.</p>'
        '<input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">'
        '<label class="ck"><input type="checkbox" name="consent" required> I agree that my photo and details are processed by an AI service (Google Gemini) and stored securely so that Dr. Tejas Pradhan can review them and contact me. '
        'I understand the "after" image is a simulation. I can ask the clinic to delete my data at any time.</label>'
        '<button id="dsb" class="btn" type="submit">Design my smile</button>'
        '<p id="dsm" class="muted" role="status"></p></form>'
        '<div id="dso"></div>'
        '<h2 style="margin-top:40px">Ideal dimensions of the upper front teeth</h2>'
        '<p>Average crown sizes the design aims for. Every face is different, so the dentist adjusts these to your smile.</p>'
        f'<div class="cmpw"><table class="cmp" style="min-width:0"><thead><tr><th>Tooth</th><th>Width</th><th>Height</th><th>Width ÷ height</th></tr></thead><tbody>{trs}</tbody></table></div>'
        + ul(["The two central incisors match in size and shape and are the most prominent teeth.",
              "Seen from the front, each tooth looks narrower than the one before it: laterals about 62–75% of the centrals, canines about 62–80% of the laterals.",
              "The teeth midline lines up with the middle of the face.",
              "The edges of the upper teeth follow a gentle curve parallel to the lower lip (the smile arc).",
              "The gum line is even: centrals and canines level, laterals slightly lower.",
              "A natural shade, not an artificial bright white."])
        + '<p>Related: <a href="smile-check.html">Free AI smile check</a> · <a href="teeth-whitening.html">Teeth whitening</a> · <a href="braces-comparison.html">Braces compared</a></p>'
        f'<script>{js}</script>')
    faqs = [("What is digital smile design?", "Digital smile design (DSD) uses photos and measurements of your face and teeth to plan a smile makeover, so you can preview the result before treatment."),
            ("Is the AI after picture what I will actually get?", "No. It is an AI simulation for ideas only. Your real result depends on your teeth, gums, bite and the treatment chosen after an examination."),
            ("What are the ideal dimensions of front teeth?", "On average, an upper central incisor is about 8.5–9 mm wide and 10.5–11 mm long, a width-to-height ratio of about 75–80%. Laterals are about 6.5 mm wide and canines about 7.5 mm."),
            ("Which treatments can change my smile?", "Depending on your teeth: whitening, tooth-coloured bonding, veneers, crowns, aligners or braces, and sometimes gum contouring. The dentist advises after examining you.")]
    return guide_page("smile-design", "AI Digital Smile Design: See Your Smile Before and After", "AI smile design", "AI tool",
                      "Upload a smile photo: AI marks your 8 front teeth, compares them with ideal dimensions and shows a simulated before and after. Not a guarantee of results.",
                      body, faqs)


GUIDES = [
    ("smile-design", "AI digital smile design", "See a simulated before and after of your smile, with ideal tooth proportions.", dsd_page),
    ("smile-check", "Free AI smile check", "Upload photos of your teeth for a tentative AI overview.", smile_page),
    ("braces-comparison", "Braces and aligners compared", "Metal, ceramic, self-ligating, lingual and clear aligners side by side.", braces_page),
    ("post-extraction-care", "Post-extraction care", "Instructions and chart for after a tooth extraction.", extraction_page),
    ("post-implant-care", "Post-implant surgery care", "Chart, instructions and video for after implant surgery.", implant_page),
    ("brushing-technique", "Brushing technique", "How to brush properly, with a video.", brushing_page),
]


def guides_list():
    ic = '<path d="M5 4h11l3 3v13H5z"/><path d="M9 11h6M9 15h6"/>'
    return '<div class="tl">' + "".join(
        f'<a href="{s}.html">{svg(ic)}<div><span class="nm">{e(n)}</span><small>{e(d)}</small></div><span class="ar">→</span></a>'
        for s, n, d, _ in GUIDES) + "</div>"


RELATED = {
    "tooth-extraction": ["post-extraction-care"],
    "dental-implants": ["post-implant-care", "implant-overdenture", "all-on-4-implants"],
    "implant-overdenture": ["post-implant-care", "dental-implants", "dentures"],
    "all-on-4-implants": ["post-implant-care", "dental-implants"],
    "dentures": ["implant-overdenture"],
    "braces": ["braces-comparison", "brushing-technique"],
    "clear-aligners": ["braces-comparison"],
    "scaling-cleaning": ["brushing-technique"],
    "childrens-dentistry": ["brushing-technique"],
}


def related_block(slug):
    names = {s: n for s, n, _, _ in GUIDES}
    names.update({p["slug"]: p["name"] for p in PAGES})
    r = RELATED.get(slug)
    if not r:
        return ""
    return ('<h2 style="margin-top:36px">Related</h2><ul class="b">'
            + "".join(f'<li><a href="{s}.html">{e(names[s])}</a></li>' for s in r) + "</ul>")


# ---------------------------------------------------------------- write everything
(OUT / "index.html").write_text(home(), encoding="utf-8")
for p in PAGES:
    (OUT / f'{p["slug"]}.html').write_text(page(p), encoding="utf-8")

for slug, _n, _d, fn in GUIDES:
    (OUT / f"{slug}.html").write_text(fn(), encoding="utf-8")

urls = [f"{BASE}/"] + [f'{BASE}/{p["slug"]}.html' for p in PAGES] + [f'{BASE}/{g[0]}.html' for g in GUIDES]
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")

llms = [f"# {CLINIC}", "",
        f"> Dental clinic in Jogeshwari East, Mumbai, led by Dr. Tejas Pradhan (Reg. No. A-20222). {ADDR}. "
        f"Mon–Sat 11:00–14:30 and 17:30–21:00, closed Sunday. Phone/WhatsApp {PHONE} or {PHONE2}.", "",
        "## Treatments", ""]
llms += [f'- [{p["name"]}]({BASE}/{p["slug"]}.html): {one_liner(p)}' for p in PAGES]
llms += ["", "## Patient guides", ""] + [f"- [{n}]({BASE}/{sl}.html): {d}" for sl, n, d, _ in GUIDES]
(OUT / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")

print(f"{len(PAGES) + 1} pages, {sum(len(p['faqs']) for p in PAGES) + len(HOME_FAQS)} FAQs, {len(IMAGES)} photos")
