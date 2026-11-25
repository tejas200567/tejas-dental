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
gallery = [i for i in IMAGES if i is not doctor_img and i is not hero_img]


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
    if IMAGES:
        dentist["image"] = [f'{BASE}/{i["url"]}' for i in IMAGES]
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
      <h2>Neighbourhood dentistry, done carefully</h2>
      <p>{e(CLINIC)} is a neighbourhood dental practice in Jogeshwari East, Mumbai, led by Dr. Tejas Pradhan (Maharashtra State Dental Council Reg. No. A-20222). Families from Kokan Nagar, Poonam Nagar and Andheri East come here for check-ups, root canals, extractions, crowns, dentures, implants and orthodontic treatment.</p>
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


# ---------------------------------------------------------------- write everything
(OUT / "index.html").write_text(home(), encoding="utf-8")
for p in PAGES:
    (OUT / f'{p["slug"]}.html').write_text(page(p), encoding="utf-8")

urls = [f"{BASE}/"] + [f'{BASE}/{p["slug"]}.html' for p in PAGES]
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")

llms = [f"# {CLINIC}", "",
        f"> Dental clinic in Jogeshwari East, Mumbai, led by Dr. Tejas Pradhan (Reg. No. A-20222). {ADDR}. "
        f"Mon–Sat 11:00–14:30 and 17:30–21:00, closed Sunday. Phone/WhatsApp {PHONE} or {PHONE2}.", "",
        "## Treatments", ""]
llms += [f'- [{p["name"]}]({BASE}/{p["slug"]}.html): {one_liner(p)}' for p in PAGES]
(OUT / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")

print(f"{len(PAGES) + 1} pages, {sum(len(p['faqs']) for p in PAGES) + len(HOME_FAQS)} FAQs, {len(IMAGES)} photos")
