from pathlib import Path
import re

root = Path("source/CleanYourTV-Independent")
java = root / "app/src/main/java/ae/cleanyourtv/independent/MainActivity.java"
gradle = root / "app/build.gradle"

s = java.read_text(encoding="utf-8")
old = r'Pattern.compile("(?i)NextPrayer\\s*:\\s*(fajr|zuhr|dhuhr|asr|maghrib|isha)\\s+(\\d{1,2}:\\d{2}:\\d{2})")'
new = r'Pattern.compile("(?i)Next\\s*prayer\\s*:\\s*(fajr|zuhr|dhuhr|asr|maghrib|isha)\\s+(\\d{1,2}:\\d{2}:\\d{2})")'
if old not in s:
    raise SystemExit("Expected prayer countdown parser was not found; refusing to build an unpatched APK.")
s = s.replace(old, new, 1)

old = "        super.onCreate(state);\n"
new = "        super.onCreate(state);\n        getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);\n"
if old not in s:
    raise SystemExit("onCreate insertion point not found.")
s = s.replace(old, new, 1)

old = "        root.setOrientation(LinearLayout.VERTICAL);\n"
new = "        root.setOrientation(LinearLayout.VERTICAL);\n        root.setKeepScreenOn(true);\n"
if old not in s:
    raise SystemExit("Root layout insertion point not found.")
s = s.replace(old, new, 1)

old = '        LinearLayout page = new LinearLayout(this); page.setOrientation(LinearLayout.VERTICAL);'
new = '        LinearLayout page = new LinearLayout(this); page.setKeepScreenOn(true); page.setOrientation(LinearLayout.VERTICAL);'
if old not in s:
    raise SystemExit("Section page insertion point not found.")
s = s.replace(old, new, 1)

# The embedded official-authority WebView is initialized in render(); the old onCreate call
# referenced a method that does not exist in this source archive and prevented compilation.
old_call = "loadWeather(); loadOfficialPrayerData();"
if old_call not in s:
    raise SystemExit("Expected obsolete onCreate call not found.")
s = s.replace(old_call, "loadWeather();", 1)

java.write_text(s, encoding="utf-8")

g = gradle.read_text(encoding="utf-8")
if "versionCode 17" not in g or "versionName '0.17.0-preview'" not in g:
    raise SystemExit("Expected version 17 metadata not found.")
g = g.replace("versionCode 17", "versionCode 18", 1).replace("versionName '0.17.0-preview'", "versionName '0.18.0-preview'", 1)
gradle.write_text(g, encoding="utf-8")

print("Applied verified Dalati TV v18 patches: prayer parser, keep-screen-on, version metadata.")
