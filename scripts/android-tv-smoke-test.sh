#!/usr/bin/env bash
set -euo pipefail

APK="$GITHUB_WORKSPACE/dalati-tv-smoke.apk"
ADB="$ANDROID_HOME/platform-tools/adb"

echo "Workspace: $GITHUB_WORKSPACE"
echo "APK path: $APK"
test -s "$APK"
sha256sum "$APK"

"$ADB" start-server
"$ADB" wait-for-device
echo "ADB devices:"
"$ADB" devices -l

ready=0
for i in $(seq 1 120); do
  state="$("$ADB" get-state 2>/dev/null || true)"
  if [ "$state" = "device" ] && "$ADB" shell service check package 2>/dev/null | grep -q found; then
    ready=1
    break
  fi
  "$ADB" reconnect offline >/dev/null 2>&1 || true
  sleep 2
done

if [ "$ready" -ne 1 ]; then
  echo "Android package manager did not become ready."
  "$ADB" devices -l || true
  "$ADB" logcat -d -t 250 || true
  exit 1
fi

installed=0
for i in $(seq 1 4); do
  if "$ADB" install -r "$APK"; then
    installed=1
    break
  fi
  echo "Install attempt $i failed; waiting for package manager."
  sleep 5
done
test "$installed" -eq 1

"$ADB" shell am start -W -n ae.cleanyourtv.independent/.MainActivity
sleep 15
PID="$("$ADB" shell pidof ae.cleanyourtv.independent | tr -d '\r')"
test -n "$PID"
echo "Dalati TV process: $PID"

"$ADB" exec-out screencap -p > "$GITHUB_WORKSPACE/dalati-home-emulator.png"
test -s "$GITHUB_WORKSPACE/dalati-home-emulator.png"
file "$GITHUB_WORKSPACE/dalati-home-emulator.png"
