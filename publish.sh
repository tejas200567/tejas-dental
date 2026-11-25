#!/data/data/com.termux/files/usr/bin/bash
# Publish the clinic website to GitHub Pages from Termux.
# Usage: bash publish.sh   (run inside the folder holding index.html and robots.txt)
set -e
REPO=tejas-dental

command -v git >/dev/null || pkg install -y git
command -v gh  >/dev/null || pkg install -y gh
gh auth status >/dev/null 2>&1 || gh auth login

USER=$(gh api user --jq .login)
URL="https://$USER.github.io/$REPO"

# Put the real address into the page
sed -i "s#https://SITE_URL#$URL#g" *.html *.txt *.xml

git init -q 2>/dev/null || true
git checkout -q -B main
git add -A
git -c user.name="$USER" -c user.email="$USER@users.noreply.github.com" commit -qm "Clinic website" || true

if ! gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --source=. --push
else
  git push -u origin main
fi

gh api "repos/$USER/$REPO/pages" -X POST -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 \
  || echo "(Pages already enabled)"

echo
echo "Live in 1-2 minutes at: $URL/"
