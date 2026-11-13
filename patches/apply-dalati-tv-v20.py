from pathlib import Path
import re

root = Path("source/CleanYourTV-Independent")
java = root / "app/src/main/java/ae/cleanyourtv/independent/MainActivity.java"
s = java.read_text(encoding="utf-8")
s = s.replace("private TextView sectionContent, screensaverPrayerView;", "private TextView sectionContent, screensaverPrayerView, prayerMainView;", 1)

def replace_method(source, signature, next_signature, replacement):
    a = source.index(signature)
    b = source.index(next_signature, a)
    return source[:a] + replacement + "\n\n" + source[b:]

s = replace_method(s, "    private void render() {", "    private LinearLayout cinematicCard(", r'''
    private int dp(float n) { return Math.round(n * getResources().getDisplayMetrics().density); }

    private void render() {
        root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22),dp(10),dp(22),dp(8));
        root.setBackground(new BitmapDrawable(getResources(),BitmapFactory.decodeResource(getResources(),R.drawable.ajman_cinematic)));
        root.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);

        LinearLayout header=new LinearLayout(this); header.setGravity(Gravity.CENTER_VERTICAL); header.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
        TextView brand=text("◉  Dalati TV",25,Color.WHITE,true); brand.setShadowLayer(dp(8),0,0,gold);
        header.addView(brand,new LinearLayout.LayoutParams(0,dp(56),1.1f));
        TextView wifi=text("◉",22,Color.WHITE,true); wifi.setGravity(Gravity.CENTER); header.addView(wifi,new LinearLayout.LayoutParams(dp(34),dp(56)));
        View sep=new View(this); sep.setBackgroundColor(gold); LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(dp(1),dp(38)); sp.setMargins(dp(8),0,dp(8),0); header.addView(sep,sp);
        dateView=text("",14,Color.WHITE,true); dateView.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL); dateView.setMaxLines(2); header.addView(dateView,new LinearLayout.LayoutParams(dp(220),dp(56)));
        View sep2=new View(this); sep2.setBackgroundColor(gold); LinearLayout.LayoutParams sp2=new LinearLayout.LayoutParams(dp(1),dp(38)); sp2.setMargins(dp(10),0,dp(10),0); header.addView(sep2,sp2);
        clockView=text("--:--",42,Color.WHITE,true); clockView.setGravity(Gravity.CENTER); clockView.setShadowLayer(dp(8),0,dp(3),gold); header.addView(clockView,new LinearLayout.LayoutParams(dp(145),dp(56)));
        root.addView(header,new LinearLayout.LayoutParams(-1,dp(58)));

        LinearLayout info=new LinearLayout(this); info.setOrientation(LinearLayout.HORIZONTAL); info.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
        LinearLayout weather=refCard(info,"☁  الطقس","26°","عجمان","سماء صافية","weather",1);
        weatherValue=(TextView)weather.getChildAt(1); weatherExtra=(TextView)weather.getChildAt(3);
        LinearLayout quote=refCard(info,"۞  حديث اليوم","مَنْ كان يؤمن بالله واليوم الآخر فليقل خيراً أو ليصمت","رواه البخاري ومسلم","","adhkar",1);
        LinearLayout barca=refCard(info,"⚽  برشلونة × فياريال","المباراة القادمة","جارٍ تحميل الموعد","","barcelona",1);
        barcelonaSummary=(TextView)barca.getChildAt(2);
        LinearLayout prayer=refCard(info,"۞  الصلاة القادمة","العشاء","--:--","--:--:--","prayer",1.15f);
        prayerMainView=(TextView)prayer.getChildAt(1); prayerSummary=(TextView)prayer.getChildAt(2);
        root.addView(info,new LinearLayout.LayoutParams(-1,dp(132)));

        root.addView(new View(this),new LinearLayout.LayoutParams(1,0,1));
        TextView appsTitle=text("تطبيقاتك المفضلة  ▦",16,Color.WHITE,true); appsTitle.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL);
        root.addView(appsTitle,new LinearLayout.LayoutParams(-1,dp(24)));
        LinearLayout apps=new LinearLayout(this); apps.setId(View.generateViewId()); apps.setOrientation(LinearLayout.HORIZONTAL); apps.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
        appTile(apps,"▶","YouTube","com.google.android.youtube",true);
        appTile(apps,"N","Netflix","com.netflix.ninja",false);
        appTile(apps,"D+","Disney+","com.disney.disneyplus",false);
        appTile(apps,"▶","Prime Video","com.amazon.amazonvideo.livingroom",false);
        appTile(apps,"ش","شاهد","com.mbc.shahid",false);
        appTile(apps,"≋","Spotify","com.spotify.tv.android",false);
        appTile(apps,"▶","Google Play","com.android.vending",false);
        appTile(apps,"▦","كل التطبيقات","apps",false);
        root.addView(apps,new LinearLayout.LayoutParams(-1,dp(104)));

        LinearLayout nav=new LinearLayout(this); nav.setId(View.generateViewId()); nav.setOrientation(LinearLayout.HORIZONTAL); nav.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
        nav.setGravity(Gravity.CENTER_VERTICAL); nav.setPadding(dp(8),0,dp(8),0); nav.setBackground(roundBackground(Color.argb(210,7,20,37),gold,dp(1)));
        navTile(nav,"⚙","الإعدادات","settings"); navTile(nav,"♧","الإشعارات","notifications");
        navTile(nav,"▤","الدليل","guide"); navTile(nav,"⌂","الرئيسية","home");
        navTile(nav,"▣","عرض الشاشة","cast"); navTile(nav,"♫","الموسيقى","music");
        navTile(nav,"▦","التطبيقات","apps"); navTile(nav,"⌕","بحث","search");
        root.addView(nav,new LinearLayout.LayoutParams(-1,dp(48)));
        connectVerticalFocus(info,apps,nav); wireFocusRow(apps);
        dashboard=root; statusView=text("",10,Color.WHITE,false); statusView.setVisibility(View.GONE); setContentView(root);
        root.post(()->{if(apps.getChildCount()>0)apps.getChildAt(0).requestFocus();});

        prayerDataWebView=new android.webkit.WebView(this); prayerDataWebView.setFocusable(false);
        prayerDataWebView.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO); prayerDataWebView.setAlpha(0.01f);
        prayerDataWebView.getSettings().setJavaScriptEnabled(true); prayerDataWebView.getSettings().setDomStorageEnabled(true);
        prayerDataWebView.setWebViewClient(new android.webkit.WebViewClient(){@Override public void onPageFinished(android.webkit.WebView v,String u){readOfficialPrayerPage();}});
        root.addView(prayerDataWebView,new LinearLayout.LayoutParams(1,1)); prayerDataWebView.loadUrl("https://www.awqaf.ae/?lang=en");
        handler.removeCallbacks(prayerReadTicker); handler.postDelayed(prayerReadTicker,5000);
        handler.removeCallbacks(prayerCountdownTicker); handler.post(prayerCountdownTicker);
        loadBarcelona(); loadWeather();
    }

    private LinearLayout refCard(LinearLayout row,String title,String main,String sub,String foot,String section,float weight) {
        LinearLayout c=new LinearLayout(this); c.setOrientation(LinearLayout.VERTICAL); c.setGravity(Gravity.CENTER); c.setPadding(dp(7),dp(6),dp(7),dp(6));
        c.setBackground(roundBackground(Color.argb(190,7,22,43),gold,dp(1))); c.setFocusable(true); c.setFocusableInTouchMode(true); c.setId(View.generateViewId());
        c.setOnFocusChangeListener((v,f)->c.setBackground(roundBackground(f?Color.argb(230,24,39,60):Color.argb(190,7,22,43),f?Color.WHITE:gold,f?dp(3):dp(1))));
        c.setOnClickListener(v->openSection(section));
        TextView h=text(title,15,Color.WHITE,true); h.setGravity(Gravity.CENTER); c.addView(h,new LinearLayout.LayoutParams(-1,dp(25)));
        TextView m=text(main,20,Color.WHITE,true); m.setGravity(Gravity.CENTER); m.setMaxLines(2); c.addView(m,new LinearLayout.LayoutParams(-1,0,1));
        TextView b=text(sub,13,Color.WHITE,false); b.setGravity(Gravity.CENTER); b.setMaxLines(2); c.addView(b,new LinearLayout.LayoutParams(-1,dp(24)));
        if(foot!=null&&!foot.isEmpty()){TextView f=text(foot,11,Color.LTGRAY,false);f.setGravity(Gravity.CENTER);c.addView(f);}
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-1,weight);p.setMargins(dp(5),dp(5),dp(5),dp(5));row.addView(c,p);return c;
    }
''')

s = replace_method(s, "    private void appTile(", "    private void navTile(", r'''
    private void appTile(LinearLayout row,String fallbackIcon,String label,String packageName,boolean selected) {
        LinearLayout tile=new LinearLayout(this);tile.setOrientation(LinearLayout.VERTICAL);tile.setGravity(Gravity.CENTER);tile.setPadding(dp(3),dp(3),dp(3),dp(3));
        tile.setFocusable(true);tile.setFocusableInTouchMode(true);tile.setId(View.generateViewId());
        tile.setBackground(roundBackground(Color.argb(165,5,17,34),gold,dp(1)));
        tile.setOnFocusChangeListener((v,f)->tile.setBackground(roundBackground(f?Color.argb(230,29,39,58):Color.argb(165,5,17,34),f?gold:Color.argb(100,210,220,235),f?dp(3):dp(1))));
        tile.setOnClickListener(v->{if("apps".equals(packageName)){openSection("apps");return;}Intent launch=findLaunchIntent(packageName,label);if(launch!=null){try{startActivity(launch);}catch(Exception e){Toast.makeText(this,"تعذر تشغيل "+label,Toast.LENGTH_SHORT).show();}}else Toast.makeText(this,"التطبيق غير مثبت: "+label,Toast.LENGTH_SHORT).show();});
        ImageView image=new ImageView(this);image.setScaleType(ImageView.ScaleType.FIT_CENTER);boolean found=false;
        if(!"apps".equals(packageName))try{ResolveInfo ri=findAppInfo(packageName,label);if(ri!=null){image.setImageDrawable(ri.loadIcon(getPackageManager()));found=true;}else{image.setImageDrawable(getPackageManager().getApplicationIcon(packageName));found=true;}}catch(Exception ignored){}
        if(found)tile.addView(image,new LinearLayout.LayoutParams(dp(72),dp(72)));
        else{TextView g=text(fallbackIcon,38,Color.WHITE,true);g.setGravity(Gravity.CENTER);tile.addView(g,new LinearLayout.LayoutParams(dp(72),dp(72)));}
        tile.setContentDescription(label);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-1,1);p.setMargins(dp(3),dp(3),dp(3),dp(3));row.addView(tile,p);
    }
''')

s = replace_method(s, "    private void navTile(", "    private void renderSettings(", r'''
    private void navTile(LinearLayout row,String icon,String label,String section) {
        LinearLayout item=new LinearLayout(this);item.setOrientation(LinearLayout.VERTICAL);item.setGravity(Gravity.CENTER);
        item.setFocusable(true);item.setFocusableInTouchMode(true);item.setId(View.generateViewId());item.setContentDescription(label);
        item.setBackground(roundBackground(Color.TRANSPARENT,Color.TRANSPARENT,dp(1)));
        item.setOnFocusChangeListener((v,f)->item.setBackground(roundBackground(f?Color.argb(225,30,45,65):Color.TRANSPARENT,f?gold:Color.TRANSPARENT,f?dp(2):dp(1))));
        item.setOnClickListener(v->dispatchNav(section));
        TextView g=text(icon,25,Color.WHITE,true);g.setGravity(Gravity.CENTER);item.addView(g,new LinearLayout.LayoutParams(-1,dp(38)));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-1,1);p.setMargins(dp(2),0,dp(2),0);row.addView(item,p);
    }

    private void dispatchNav(String s) {
        switch(s){
            case "home":showDashboard();break;
            case "settings":openSection("settings");break;
            case "apps":openSection("apps");break;
            case "cast":try{startActivity(new Intent("android.settings.CAST_SETTINGS"));}catch(Exception e){try{startActivity(new Intent(android.provider.Settings.ACTION_SETTINGS));}catch(Exception ignored){}}break;
            case "music":launchMatchingApp(new String[]{"spotify","music","موسيقى"});break;
            case "notifications":try{startActivity(new Intent("android.settings.NOTIFICATION_SETTINGS"));}catch(Exception e){Toast.makeText(this,"إعدادات الإشعارات غير متاحة",Toast.LENGTH_SHORT).show();}break;
            case "guide":openSection("guide");break;
            case "search":openSection("search");break;
        }
    }

    private void launchMatchingApp(String[] terms) {
        Intent q=new Intent(Intent.ACTION_MAIN);q.addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER);
        for(ResolveInfo ri:getPackageManager().queryIntentActivities(q,0))if(ri.activityInfo!=null){
            String label=ri.loadLabel(getPackageManager()).toString().toLowerCase(Locale.ROOT),pkg=ri.activityInfo.packageName.toLowerCase(Locale.ROOT);
            for(String term:terms)if(label.contains(term)||pkg.contains(term)){Intent i=new Intent(Intent.ACTION_MAIN);i.addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER);i.setClassName(ri.activityInfo.packageName,ri.activityInfo.name);try{startActivity(i);return;}catch(Exception ignored){}}
        }
        Toast.makeText(this,"لم يتم العثور على تطبيق مناسب مثبت",Toast.LENGTH_SHORT).show();
    }
''')

s=s.replace('''        if (section.equals("settings")) { renderSettings(page, title);''','''        if (section.equals("search")) {
            TextView h=text(title,32,gold,true);page.addView(h);
            android.widget.EditText q=new android.widget.EditText(this);q.setSingleLine(true);q.setTextColor(Color.WHITE);q.setHintTextColor(Color.LTGRAY);q.setHint("اسم التطبيق");q.setTextSize(22);q.setBackground(roundBackground(panel,gold,dp(1)));page.addView(q,new LinearLayout.LayoutParams(-1,dp(62)));
            TextView go=text("بحث",20,Color.WHITE,true);go.setGravity(Gravity.CENTER);go.setFocusable(true);go.setBackground(roundBackground(panel,gold,dp(1)));go.setOnClickListener(v->launchMatchingApp(new String[]{q.getText().toString().trim().toLowerCase(Locale.ROOT)}));page.addView(go,new LinearLayout.LayoutParams(dp(170),dp(56)));
            setContentView(page);resetIdleTimer();q.requestFocus();return;
        }
        if (section.equals("settings")) { renderSettings(page, title);''',1)
s=s.replace('case "apps": title="التطبيقات";', 'case "guide": title="دليل البرامج"; body="دليل Dalati TV\\n\\nاختر تطبيق البث من صف التطبيقات لعرض القنوات والبرامج المتاحة فيه."; break;' + chr(10) + '            case "search": title="البحث عن تطبيق"; body="اكتب اسم التطبيق المثبت للعثور عليه."; break;' + chr(10) + '            case "apps": title="التطبيقات";',1)
s=s.replace('''        String value="الصلاة القادمة: "+nextPrayerLabel+"\\\\nالوقت المتبقي  "+countdown;
        if(prayerSummary!=null) prayerSummary.setText(value);''','''        if(prayerMainView!=null) prayerMainView.setText(nextPrayerLabel);
        if(prayerSummary!=null) prayerSummary.setText(countdown);''',1)
s=s.replace('LocalDate now=LocalDate.now(); Locale ar=', 'LocalDate now=LocalDate.now(ZoneId.of("Asia/Dubai")); Locale ar=',1)
s=s.replace('java.time.LocalTime.now());','java.time.LocalTime.now(ZoneId.of("Asia/Dubai")));',1)
# Bump build metadata and retain all existing app functionality.
g= root/"app/build.gradle"
gs=g.read_text(encoding="utf-8").replace("versionCode 19","versionCode 20").replace("versionName '0.19.0-preview'","versionName '0.20.0-preview'")
g.write_text(gs,encoding="utf-8")
java.write_text(s,encoding="utf-8")
print("Dalati TV v20 responsive cinematic dashboard, eight app tiles, compact icon navigation and internal search applied.")
