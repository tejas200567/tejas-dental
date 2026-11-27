#!/data/data/com.termux/files/usr/bin/bash
# Build and publish the clinic website to GitHub Pages from Termux.
# Usage: bash publish.sh   (run inside ~/clinic)
set -e
REPO=tejas-dental

command -v git >/dev/null || pkg install -y git
command -v gh  >/dev/null || pkg install -y gh
command -v python >/dev/null || pkg install -y python
gh auth status >/dev/null 2>&1 || gh auth login

USER=$(gh api user --jq .login)
URL="https://$USER.github.io/$REPO"

# Shrink big phone photos (needs ImageMagick: pkg install imagemagick). Skipped if not installed.
if [ -d images ]; then
  if command -v convert >/dev/null; then
    for f in images/*.jpg images/*.jpeg images/*.png; do
      [ -f "$f" ] || continue
      if [ "$(stat -c %s "$f")" -gt 600000 ]; then
        convert "$f" -auto-orient -resize '1600x1600>' -strip -quality 82 "$f"
      fi
    done
  else
    for f in images/*; do
      [ -f "$f" ] && [ "$(stat -c %s "$f")" -gt 2500000 ] && echo "NOTE: $f is large. Run: pkg install imagemagick, then publish again."
    done
  fi
fi

# Build all pages (uses the photos in images/ if present)
python _build/build.py .
[ -f .keep ] && git checkout HEAD -- $(cat .keep) 2>/dev/null

# Put the real address into the pages
sed -i "s#https://SITE_URL#$URL#g" *.html *.txt *.xml

git init -q 2>/dev/null || true
git checkout -q -B main
git add -A
git -c user.name="$USER" -c user.email="$USER@users.noreply.github.com" commit -qm "Update clinic website" || true

if ! gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --source=. --push
else
  git push -u origin main
fi

gh api "repos/$USER/$REPO/pages" -X POST -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 \
  || echo "(Pages already enabled)"

echo
echo "Live in 1-2 minutes at: $URL/"
