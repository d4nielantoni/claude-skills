#!/bin/bash
# Read-only disk-space report for macOS. Deletes nothing.
# Usage: bash scan.sh [projects-dir]      (default projects dir: ~/Projects)
# Groups findings as SAFE / ASK FIRST / USER DATA so the agent knows what it may clean.

H="$HOME"
PROJ="${1:-$H/Projects}"
sz() { [ -e "$1" ] && du -sh "$1" 2>/dev/null | awk '{print $1}' || echo "-"; }
row() { [ -e "$1" ] && printf "  %-8s %s\n" "$(sz "$1")" "${2:-$1}"; }
top() { du -xhd1 "$1" 2>/dev/null | sort -rh | sed -n "2,$(( ${2:-8} + 1 ))p" | sed 's/^/  /'; }

echo "== SPACE =="
df -h /System/Volumes/Data | awk 'NR==2{print "  Free: "$4"  (used "$5")"}'
echo "  Trash: $(sz "$H/.Trash")"

echo
echo "== SAFE (caches that rebuild themselves) =="
row "$H/Library/Containers/com.apple.CoreDevice.CoreDeviceService/Data/Library/Caches/AppInstallationBinaryDeltas" "iPhone app-install deltas (CoreDevice)"
row "$H/Library/Developer/Xcode/DerivedData" "Xcode DerivedData"
row "$H/Library/Developer/Xcode/iOS DeviceSupport" "Xcode iOS DeviceSupport"
row "$H/.npm/_cacache" "npm cache"
row "$H/Library/Caches/pip" "pip cache"
row "$H/Library/Caches/pnpm" "pnpm cache"
row "$H/Library/Caches/Homebrew" "Homebrew downloads"
echo "  Largest folders in ~/Library/Caches:"
top "$H/Library/Caches" 6
echo "  Installers in Downloads (.dmg / .pkg):"
find "$H/Downloads" -maxdepth 2 -type f \( -iname "*.dmg" -o -iname "*.pkg" -o -iname "*.pkg.zip" -o -iname "*.mpkg" \) 2>/dev/null \
  | while read -r f; do row "$f"; done

echo
echo "== DOCKER =="
if docker info >/dev/null 2>&1; then
  docker system df 2>/dev/null | sed 's/^/  /'
  row "$H/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw" "Docker disk image"
else
  echo "  Docker is not running (start Docker Desktop to measure or prune)."
fi

echo
echo "== ASK FIRST (rebuildable, but costs time or bandwidth) =="
row "$H/.gradle/caches" "Gradle caches (next Android build re-downloads)"
row "$H/Library/Android/sdk/emulator" "Android emulator"
[ -d "$H/Library/Android/sdk" ] && echo "    Android virtual devices: $(ls "$H/.android/avd" 2>/dev/null | grep -c '\.ini$') (0 = emulator unused)"
row "$H/Library/Application Support/Claude/vm_bundles" "Claude desktop VM (re-downloads when agent mode is used)"
if [ -d "$PROJ" ]; then
  echo "  Build folders over 100 MB in $PROJ (project last changed):"
  find "$PROJ" -maxdepth 5 -type d \( -name node_modules -o -name build -o -name Pods -o -name .venv -o -name venv -o -name dist -o -name target -o -name .next \) -prune -print 2>/dev/null \
    | while read -r d; do s=$(du -sk "$d" 2>/dev/null | awk '{print $1}'); [ "${s:-0}" -gt 100000 ] && printf "  %-8s %s  (changed %s)\n" "$(sz "$d")" "$d" "$(stat -f '%Sm' -t '%Y-%m-%d' "$(dirname "$d")")"; done | sort -rh
else
  echo "  Projects folder $PROJ not found (pass it as the first argument)."
fi

echo
echo "== USER DATA (never delete without an explicit request; report only) =="
echo "  Largest app data (Application Support / Containers / Group Containers):"
{ du -xhd1 "$H/Library/Application Support" "$H/Library/Containers" "$H/Library/Group Containers" 2>/dev/null \
  | grep -v -E "/(Application Support|Containers|Group Containers)$"; } | sort -rh | head -12 | sed 's/^/  /'
row "$H/Pictures" "Pictures"
row "$H/Movies" "Movies"
row "$H/Downloads" "Downloads"

echo
echo "== APPS BY LAST USE (over 100 MB; (null) = never opened from Finder/Dock) =="
for a in /Applications/*.app; do
  [ -L "$a" ] && continue
  printf "%s\t%s\t%s\n" "$(mdls -raw -name kMDItemLastUsedDate "$a" 2>/dev/null | cut -c1-10)" "$(du -sk "$a" 2>/dev/null | cut -f1)" "$(basename "$a")"
done | sort | awk -F'\t' '$2>100000 {printf "  %-10s %6.0fM  %s\n", $1, $2/1024, $3}'

echo
echo "== LARGEST FILES (over 500 MB) =="
find "$H" -xdev -type f -size +500M -not -path "*/com.docker.docker/*" -not -path "*/vm_bundles/*" 2>/dev/null \
  -exec ls -lh {} \; | awk '{s=$5; $1=$2=$3=$4=$5=$6=$7=$8=""; print "  " s "  " substr($0,9)}' | sort -rh | head -15
echo "  (iCloud files that are not downloaded show their full size here but use no local space.)"
