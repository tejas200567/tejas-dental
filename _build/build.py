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


GUIDES = [
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
