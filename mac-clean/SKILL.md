---
name: mac-clean
description: "Use when a Mac is low on disk space or the user asks to clean up or free storage ('my Mac is full', 'free up space', 'disk almost full', 'limpar o computador', 'sem espaço'), when a build or download fails with 'No space left on device', or when the user wants to find apps and files they no longer use. Works with the Mole cleaner (mo)."
---

# Mac storage cleanup (with Mole)

## Overview

[Mole](https://github.com/tw93/Mole) (`mo`) is a command-line Mac cleaner. Its `mo clean` is the first step, but on a developer Mac it often frees only a few hundred MB: the large space usually sits in places it reports but does not delete, such as Docker, project build folders, developer SDKs, app data and apps nobody opens.

This skill runs Mole first and stops if that was enough. Otherwise it finds the rest and sorts it into three groups:
- **SAFE:** cleaned without asking.
- **ASK FIRST:** offered to the user in one question.
- **USER DATA:** reported only, never deleted.

Space is measured on `/System/Volumes/Data`, the real data volume; `df -h /` shows the small system volume.

## Rules

- Run `mo` through `/bin/bash -c '… </dev/null'`. In zsh, calling it directly can lose the output, and lines starting with `===` fail with `(eval):1: == not found`.
- Delete with `rm -rf` and literal, quoted paths, all in one command. Do not use loops or globs: they are hard to review and some agent harnesses block them. Read-only cache folders need `chmod -R u+w <path>` first.
- A project changed in the last 7 days is active: do not delete its build folders, because rebuilding is slow.
- Never delete named Docker volumes (`*_postgres_data`, `*_mysql_data`, …): they are databases.
- Apps are removed only after the user picks them.

## Steps

1. **Mole first.**
   ```bash
   /bin/bash -c 'cd ~ && mo clean </dev/null 2>&1 | sed "s/\x1b\[[0-9;]*[A-Za-z]//g" | tail -20'
   df -h /System/Volumes/Data | tail -1
   ```
   **If 30 GB or more is free now, stop** and report the result.

2. **Diagnose** (read-only). Pass the user's projects folder if it is not `~/Projects`:
   ```bash
   bash scripts/scan.sh ~/Projects
   /bin/bash -c 'cd ~ && mo purge --dry-run </dev/null 2>&1 | sed "s/\x1b\[[0-9;]*[A-Za-z]//g" | tail -30'
   ```
   `mo purge` only scans the folders listed in `~/.config/mole/purge_paths`. If the projects folder is missing there, add it (one path per line) so later purges find old build folders.

3. **SAFE: clean without asking.** Clean every item the scan listed with a relevant size:
   - the CoreDevice deltas;
   - Xcode DerivedData and iOS DeviceSupport;
   - the large app caches in `~/Library/Caches`;
   - installers in Downloads for apps already in `/Applications`;
   - temporary folders of finished agent jobs.

   Then clear the package-manager caches (if the user uses nvm, load it before `npm`):
   ```bash
   /bin/bash -c 'npm cache clean --force; pnpm store prune; python3 -m pip cache purge; brew cleanup --prune=all'
   ```

4. **Docker** (only when it is running). This is usually the biggest win, often 3 to 10 GB:
   ```bash
   docker builder prune -a -f
   docker image prune -a -f --filter "until=168h"
   docker volume prune -f
   ```
   `docker volume prune -f` removes only anonymous volumes. Never add `-a`, and never run `docker system prune --volumes`. The Docker disk image shrinks over a minute or two, so measure again afterwards.

5. **ASK FIRST.** Ask once, as a multiple-choice question, with each item's size:
   - Gradle caches;
   - the Android emulator, when there are no virtual devices;
   - build folders and dependency folders of projects untouched for more than 7 days;
   - the Claude desktop VM bundle.

   If a named Docker volume holds only dependencies (`*_node_modules`, `*_venv`), it can be offered here too.

6. **Unused apps.** Use the scan's "apps by last use" list:
   - Offer apps that were never opened, and apps unused for weeks, in the same multiple-choice style.
   - Leave out apps used from the command line, such as Xcode, which shows `(null)` but is used by builds.

   For each app the user picks:
   - Find its bundle id: `mdls -raw -name kMDItemCFBundleIdentifier "/Applications/<App>.app"`.
   - Search for its leftovers in `~/Library/{Application Support,Containers,Group Containers,Application Scripts,Preferences,HTTPStorages,Caches}`. Deleting those works without a password.
   - The `.app` itself often fails with "Permission denied" (installed by an admin or from the App Store). Give the user one ready-to-run `sudo rm -rf "/Applications/<App1>.app" "/Applications/<App2>.app"` command, or ask them to drag the apps to the Trash. Tell them to type it on a single line: a pasted command that wraps runs as two commands.
   - Apps with system extensions or drivers (antivirus, VPNs, virtual audio devices):
     - Look for their own uninstaller (`find /Library/Application\ Support -iname "*uninstall*"`) and open it.
     - Audio drivers in `/Library/Audio/Plug-Ins/HAL/` go with `sudo rm -rf` followed by `sudo killall coreaudiod`.
     - A system extension marked "waiting to uninstall on reboot" in `systemextensionsctl list` disappears at the next restart.

   Game leftovers live in `~/Games`, in `~/Applications` (Wine/CrossOver shortcuts), and in folders of uninstalled games in `~/Library/Application Support`. Ask before deleting saves.

7. **USER DATA.** Messaging apps, photo libraries, Downloads, video-editor projects and apps in daily use are reported and never deleted. Recommend how to shrink them (table below).

8. **Report** in the user's language and in plain terms:
   - free space before and after;
   - what was cleaned;
   - what is left for the user to decide or to run with their password.

## Keeping the disk from filling up again

| Cause | Recommendation |
|---|---|
| Docker grows without limit | Docker Desktop > Settings > Resources > Disk usage limit: 48–64 GB |
| Messaging apps keep all media | Clear large videos in the app's storage settings; turn off auto-download of video |
| Photos and iCloud Drive | Turn on "Optimize Mac Storage" for both |
| Old project builds | Keep the projects folder in Mole's purge paths and run `mo purge` monthly |
| System caches | Run `sudo mo clean` now and then (needs the password) |

## Common mistakes

- Taking "Mole found almost nothing" to mean the disk is clean. Most of the space sits in Docker, projects and app data.
- Deleting the build folder of an active project.
- Using `docker volume prune -a` and wiping local databases.
- Measuring with `df -h /` instead of `/System/Volumes/Data`.
