#!/data/data/com.termux/files/usr/bin/bash
# Copy a photo into the website's images folder under the right name.
# Run inside ~/clinic:   bash _build/addphoto.sh reception          (uses your newest camera photo)
#                        bash _build/addphoto.sh doctor ~/storage/downloads/me.jpg
# Names: front, reception, treatment-room, equipment, doctor, team  (add -2, -3 for more of the same)
set -e
NAME=$1; SRC=$2
[ -z "$NAME" ] && { echo "Usage: bash _build/addphoto.sh <name> [photo file]"; exit 1; }
if [ -z "$SRC" ]; then
  SRC=$(ls -t ~/storage/dcim/Camera/*.jpg ~/storage/dcim/Camera/*.jpeg 2>/dev/null | head -1)
fi
[ -f "$SRC" ] || { echo "No photo found. Run termux-setup-storage once, or give the file path."; exit 1; }
mkdir -p images
cp "$SRC" "images/$NAME.jpg"
echo "Added: $SRC -> images/$NAME.jpg"
ls -la images
