#!/usr/bin/env python3
"""Home page (run inside ~/clinic, then bash publish.sh):
- '13 treatments offered' -> '10+ years of practice'
- stats become a moving carousel (auto-scroll, pauses on touch, still for reduced motion)
- hero gets a moving background: your clinic video images/hero.mp4 if present, otherwise a slow
  cross-fading slideshow of the treatment room and the 3D pictures
Safe to run again (e.g. after you add images/hero.mp4)."""
import os, re, subprocess, sys

if not os.path.exists("index.html"):
    sys.exit("Run this inside ~/clinic")
s = open("index.html", encoding="utf-8").read()
orig = s

CSS = """
/*home4*/
.hero3d .h3g{position:relative;z-index:2}
.hbg{position:absolute;inset:0;z-index:0;overflow:hidden}
.hbg i,.hbg video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background-size:cover;background-position:center}
.hbg i{opacity:0;animation:hbgf 30s infinite;will-change:opacity,transform}
.hbg i:nth-child(2){animation-delay:6s}.hbg i:nth-child(3){animation-delay:12s}.hbg i:nth-child(4){animation-delay:18s}.hbg i:nth-child(5){animation-delay:24s}
@keyframes hbgf{0%{opacity:0;transform:scale(1.12)}4%{opacity:1}20%{opacity:1}24%{opacity:0;transform:scale(1)}100%{opacity:0}}
.hero3d .h3g{min-height:0}
@media(min-width:760px){.hero3d .h3g{grid-template-columns:1fr;min-height:560px;align-content:center}.hero3d .h3t{max-width:640px}}
.hbg:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,34,54,.55) 0%,rgba(11,34,54,.72) 50%,rgba(11,34,54,.93) 100%)}
.stats{overflow:hidden}
.stats .wrap.mq{display:block;max-width:none;padding-left:0;padding-right:0}
.mq-t{display:flex;width:max-content;animation:mq 28s linear infinite}
.mq:hover .mq-t,.mq:active .mq-t{animation-play-state:paused}
.mq-t>div{display:flex;align-items:center;gap:14px;padding:0 34px;border-right:1px solid rgba(255,255,255,.12);white-space:nowrap}
.mq-t .mi{flex:0 0 auto;width:50px;height:50px;border-radius:50%;background:rgba(217,200,184,.16);display:grid;place-items:center;color:#d9c8b8}
.mq-t .num{font-size:2rem}
.mq-t span{margin-top:4px}
@keyframes mq{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){.hbg i{animation:none}.hbg i:first-child{opacity:1}.mq-t{animation:none;flex-wrap:wrap;width:auto}}
"""
if "/*home4*/" not in s:
    s = s.replace("</style>", CSS + "</style>", 1)

# --- stats: 10+ years, carousel
IC = {
    "star": '<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/>',
    "years": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "xray": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 9c0-1.7 1.8-2.5 4-2.5s4 .8 4 2.5c0 1.5-.8 2.6-1.2 4-.3 1.2-.4 3-1.2 3-.9 0-.8-2.2-1.6-2.2s-.7 2.2-1.6 2.2c-.8 0-.9-1.8-1.2-3C8.8 11.6 8 10.5 8 9z"/>',
    "team": '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M14.5 14.5c.8-.3 1.6-.5 2.5-.5 2.8 0 4.5 2 4.5 5"/>',
    "chair": '<path d="M5 4h3l2 9h7l2 4H7z"/><path d="M9 17v3M16 17v3"/>',
}
ITEMS = [("star", "4.9 ★", "Google rating · 82 reviews"), ("years", "10+", "Years of practice"),
         ("team", "4", "Visiting specialists"), ("xray", "RVG", "Digital X-ray at the clinic"),
         ("cal", "6 days", "Open Monday to Saturday"), ("chair", "2", "Dental chairs")]


def svg(k):
    return f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{IC[k]}</svg>'


one = "".join(f'<div><span class="mi">{svg(k)}</span><div><div class="num">{n}</div><span>{t}</span></div></div>' for k, n, t in ITEMS)
dup = one.replace('<div><span class="mi">', '<div aria-hidden="true"><span class="mi">')
mq = '<div class="stats"><div class="wrap mq" aria-label="Clinic facts"><div class="mq-t">' + one + dup + '</div></div></div>'
s, n = re.subn(r'<div class="stats"><div class="wrap">.*?</div></div>(?=\s*<section)', lambda m: mq, s, count=1, flags=re.S)
if not n and 'class="wrap mq"' not in s:
    print("stats block not found")
s = s.replace('<div class="num">13</div><span>Treatments offered</span>', '<div class="num">10+</div><span>Years of practice</span>')

# --- hero moving background
slides = [p for p in ("images/treatment-room.jpg", "images/hero-3d.png", "images/card-all-on-4-implants.jpg", "images/card-crowns-bridges.jpg",
                      "images/card-dentures.jpg") if os.path.exists(p)]
if os.path.exists("images/hero.mp4"):
    poster = ' poster="images/treatment-room.jpg"' if os.path.exists("images/treatment-room.jpg") else ""
    bg = f'<div class="hbg" aria-hidden="true"><video autoplay muted loop playsinline preload="metadata"{poster} src="images/hero.mp4"></video></div>'
else:
    bg = '<div class="hbg" aria-hidden="true">' + "".join(f'<i style="background-image:url({p})"></i>' for p in slides) + "</div>"
s = re.sub(r'<div class="hbg" aria-hidden="true">.*?</div>', "", s, count=1, flags=re.S)
s = s.replace('<section class="hero3d">', '<section class="hero3d">' + bg, 1)
s = re.sub(r'\s*<div class="h3i"><img[^>]*></div>', '', s, count=1)

if s != orig:
    open("index.html", "w", encoding="utf-8").write(s)
    print("index.html updated", "(hero video)" if "hero.mp4" in bg else f"(slideshow of {len(slides)} pictures)")
else:
    print("index.html already up to date")
subprocess.run("git add index.html images 2>/dev/null; git commit -qm 'Home: 10+ years, moving stats carousel, moving hero background' || true", shell=True)
print("Done. Now run: bash publish.sh")
