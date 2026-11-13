from pathlib import Path
import re

root = Path("source/CleanYourTV-Independent")
java = root / "app/src/main/java/ae/cleanyourtv/independent/MainActivity.java"
gradle = root / "app/build.gradle"

s = java.read_text(encoding="utf-8")
# Retain the known-good v18 parser and screensaver stability changes.
old = r'Pattern.compile("(?i)NextPrayer\\s*:\\s*(fajr|zuhr|dhuhr|asr|maghrib|isha)\\s+(\\d{1,2}:\\d{2}:\\d{2})")'
new = r'Pattern.compile("(?i)Next\\s*prayer\\s*:\\s*(fajr|zuhr|dhuhr|asr|maghrib|isha)\\s+(\\d{1,2}:\\d{2}:\\d{2})")'
if old in s: s = s.replace(old, new, 1)

# Keep the TV display awake while the app's own idle timer manages its screensaver.
for before, after in [
    ("        super.onCreate(state);\\n", "        super.onCreate(state);\\n        getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);\\n"),
    ("        root.setOrientation(LinearLayout.VERTICAL);\\n", "        root.setOrientation(LinearLayout.VERTICAL);\\n        root.setKeepScreenOn(true);\\n"),
    ('        LinearLayout page = new LinearLayout(this); page.setOrientation(LinearLayout.VERTICAL);', '        LinearLayout page = new LinearLayout(this); page.setKeepScreenOn(true); page.setOrientation(LinearLayout.VERTICAL);')
]:
    if before in s: s = s.replace(before, after, 1)

# Correct the fixed-app tiles: resolve the real launcher activity by package OR localized app label,
# then load the activity icon. This also handles Shahid when its installed package differs.
start = s.index("    private void appTile(")
end = s.index("    private void navTile(", start)
replacement = r'''    private ResolveInfo findAppInfo(String packageName, String label) {
        PackageManager pm=getPackageManager();
        Intent leanback=new Intent(Intent.ACTION_MAIN); leanback.addCategory("android.intent.category.LEANBACK_LAUNCHER");
        Intent launcher=new Intent(Intent.ACTION_MAIN); launcher.addCategory(Intent.CATEGORY_LAUNCHER);
        for (Intent query : new Intent[]{leanback,launcher}) {
            for (ResolveInfo ri : pm.queryIntentActivities(query,0)) {
                if (ri.activityInfo == null) continue;
                String pkg=ri.activityInfo.packageName;
                String appLabel=ri.loadLabel(pm).toString();
                if (packageName.equals(pkg) || appLabel.equalsIgnoreCase(label)
                    || ("شاهد".equals(label) && (appLabel.contains("شاهد") || pkg.toLowerCase(Locale.ROOT).contains("shahid")))) return ri;
            }
        }
        return null;
    }

    private void appTile(LinearLayout row, String fallbackIcon, String label, String packageName, boolean selected) {
        LinearLayout tile=new LinearLayout(this); tile.setOrientation(LinearLayout.VERTICAL); tile.setGravity(Gravity.CENTER);
        tile.setPadding(8,7,8,7); tile.setFocusable(true); tile.setFocusableInTouchMode(true); tile.setId(View.generateViewId());
        tile.setBackground(roundBackground(selected?Color.argb(222,65,53,30):Color.argb(190,18,31,48),selected?gold:Color.rgb(105,128,151),selected?3:1));
        tile.setOnFocusChangeListener((v,hasFocus) -> tile.setBackground(roundBackground(
            hasFocus?Color.argb(220,20,34,52):Color.argb(190,18,31,48), hasFocus?gold:Color.rgb(105,128,151), hasFocus?4:1)));
        tile.setOnClickListener(v -> {
            if ("apps".equals(packageName)) { openSection("apps"); return; }
            Intent launch = findLaunchIntent(packageName, label);
            if (launch != null) { try { startActivity(launch); } catch(Exception e) { Toast.makeText(this,"تعذر تشغيل "+label,Toast.LENGTH_LONG).show(); } }
            else Toast.makeText(this, "التطبيق غير مثبت أو لا يوفّر واجهة تشغيل للتلفزيون: " + label, Toast.LENGTH_LONG).show();
        });
        boolean iconAdded=false;
        if (!"apps".equals(packageName)) {
            try {
                ResolveInfo info=findAppInfo(packageName,label);
                Drawable appIcon=info!=null ? info.loadIcon(getPackageManager()) : getPackageManager().getApplicationIcon(packageName);
                ImageView image=new ImageView(this); image.setImageDrawable(appIcon);
                image.setScaleType(ImageView.ScaleType.FIT_CENTER); image.setAdjustViewBounds(true);
                tile.addView(image,new LinearLayout.LayoutParams(124,124)); iconAdded=true;
            } catch (Exception ignored) { }
        }
        if (!iconAdded) {
            TextView i=text(fallbackIcon,34,selected?gold:Color.WHITE,true); i.setGravity(Gravity.CENTER);
            tile.addView(i,new LinearLayout.LayoutParams(-1,100));
        }
        tile.setContentDescription(label);
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-1,1); p.setMargins(5,4,5,4); row.addView(tile,p);
    }

'''
s = s[:start] + replacement + s[end:]

# Give the two placeholder destinations working interfaces/actions.
needle = '        TextView heading=text(title,32,gold,true); heading.setPadding(0,0,0,24); page.addView(heading);'
insert = '''        if (section.equals("settings")) { renderSettings(page, title); setContentView(page); resetIdleTimer(); return; }
        if (section.equals("files")) { renderFiles(page, title); setContentView(page); resetIdleTimer(); return; }
''' + needle
if needle not in s: raise SystemExit("Generic section render point missing")
s = s.replace(needle, insert, 1)

marker = "    private Intent findLaunchIntent(String packageName, String label) {"
methods = r'''    private void renderSettings(LinearLayout page, String title) {
        TextView heading=text(title,32,gold,true); page.addView(heading);
        TextView intro=text("إعدادات واجهة Dalati TV",20,Color.WHITE,true); intro.setPadding(0,8,0,18); page.addView(intro);
        int delay=getPreferences(MODE_PRIVATE).getInt("screensaver_delay_minutes",3);
        TextView delayLabel=text("مدة الخمول قبل تشغيل شاشة التوقف: "+delay+" دقائق",20,Color.WHITE,false); delayLabel.setPadding(0,12,0,12); page.addView(delayLabel);
        LinearLayout choices=new LinearLayout(this); choices.setOrientation(LinearLayout.HORIZONTAL); choices.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
        for (int minutes : new int[]{1,3,5,10}) {
            TextView choice=text(minutes+" دقائق",18,Color.WHITE,true); choice.setGravity(Gravity.CENTER);
            choice.setFocusable(true); choice.setPadding(18,14,18,14); choice.setBackground(roundBackground(panel,gold,1));
            choice.setOnClickListener(v->{getPreferences(MODE_PRIVATE).edit().putInt("screensaver_delay_minutes",minutes).apply(); delayLabel.setText("مدة الخمول قبل تشغيل شاشة التوقف: "+minutes+" دقائق"); resetIdleTimer();});
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,64,1); cp.setMargins(5,5,5,5); choices.addView(choice,cp);
        }
        page.addView(choices);
        TextView refresh=text("تحديث الطقس ومواقيت الصلاة الآن",19,gold,true); refresh.setFocusable(true); refresh.setPadding(8,18,8,18);
        refresh.setOnClickListener(v->{loadWeather(); readOfficialPrayerPage(); Toast.makeText(this,"بدأ تحديث البيانات",Toast.LENGTH_SHORT).show();}); page.addView(refresh);
        TextView city=text("الموقع الحالي: عجمان، الإمارات العربية المتحدة",18,Color.WHITE,false); city.setPadding(0,18,0,8); page.addView(city);
        TextView back=text("اضغط زر الرجوع للعودة إلى القائمة الرئيسية",16,gold,false); page.addView(back);
    }

    private void renderFiles(LinearLayout page, String title) {
        TextView heading=text(title,32,gold,true); page.addView(heading);
        TextView info=text("افتح مستعرض الملفات في التلفزيون لاختيار الملفات أو تصفح وحدات التخزين المتاحة.",20,Color.WHITE,false); info.setPadding(0,14,0,22); page.addView(info);
        TextView open=text("فتح مدير الملفات",22,Color.WHITE,true); open.setGravity(Gravity.CENTER); open.setFocusable(true); open.setPadding(20,18,20,18); open.setBackground(roundBackground(panel,gold,2));
        open.setOnClickListener(v->launchFileBrowser()); page.addView(open,new LinearLayout.LayoutParams(-1,76));
        TextView back=text("اضغط زر الرجوع للعودة إلى القائمة الرئيسية",16,gold,false); back.setPadding(0,20,0,0); page.addView(back);
    }

    private void launchFileBrowser() {
        Intent[] intents=new Intent[]{
            new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("*/*").addCategory(Intent.CATEGORY_OPENABLE),
            new Intent(Intent.ACTION_GET_CONTENT).setType("*/*").addCategory(Intent.CATEGORY_OPENABLE)
        };
        for (Intent intent : intents) {
            try { startActivity(intent); return; } catch (Exception ignored) { }
        }
        PackageManager pm=getPackageManager();
        Intent query=new Intent(Intent.ACTION_MAIN); query.addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER);
        for (ResolveInfo ri:pm.queryIntentActivities(query,0)) {
            if (ri.activityInfo==null) continue;
            String label=ri.loadLabel(pm).toString().toLowerCase(Locale.ROOT);
            String pkg=ri.activityInfo.packageName.toLowerCase(Locale.ROOT);
            if (label.contains("file") || label.contains("ملف") || label.contains("مدير") || pkg.contains("filemanager") || pkg.contains("file.manager")) {
                Intent launch=new Intent(Intent.ACTION_MAIN); launch.addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER);
                launch.setClassName(ri.activityInfo.packageName,ri.activityInfo.name); launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                try { startActivity(launch); return; } catch(Exception ignored) { }
            }
        }
        Toast.makeText(this,"لا يوجد مدير ملفات أو مستعرض ملفات متاح على التلفزيون.",Toast.LENGTH_LONG).show();
    }

'''
if marker not in s: raise SystemExit("Launch intent marker missing")
s = s.replace(marker, methods + marker, 1)
s = s.replace('handler.postDelayed(idleScreensaver, 3 * 60 * 1000);', 'handler.postDelayed(idleScreensaver, getPreferences(MODE_PRIVATE).getInt("screensaver_delay_minutes",3) * 60 * 1000L);', 1)
# Fix obsolete call from the archived source that otherwise fails compilation.
s = s.replace("loadWeather(); loadOfficialPrayerData();", "loadWeather();", 1)
java.write_text(s, encoding="utf-8")

g = gradle.read_text(encoding="utf-8")
if "versionCode 17" in g:
    g = g.replace("versionCode 17", "versionCode 19", 1)
    g = g.replace("versionName '0.17.0-preview'", "versionName '0.19.0-preview'", 1)
elif "versionCode 18" in g:
    g = g.replace("versionCode 18", "versionCode 19", 1)
    g = g.replace("versionName '0.18.0-preview'", "versionName '0.19.0-preview'", 1)
else:
    raise SystemExit("Expected prior app version metadata not found.")
gradle.write_text(g, encoding="utf-8")
print("Applied Dalati TV v19: dynamic app icons/label resolution, Shahid fallback, functional settings, file browser action, configurable idle timeout.")
