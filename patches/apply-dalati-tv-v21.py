from pathlib import Path
root = Path("source/CleanYourTV-Independent")
java = root / "app/src/main/java/ae/cleanyourtv/independent/MainActivity.java"
s = java.read_text(encoding="utf-8")
s=s.replace('refCard(info,"☁  الطقس","26°","عجمان","سماء صافية","weather",1);','refCard(info,"الطقس","26°","عجمان","سماء صافية","weather",0.92f);')
s=s.replace('refCard(info,"۞  حديث اليوم","مَنْ كان يؤمن بالله واليوم الآخر فليقل خيراً أو ليصمت","رواه البخاري ومسلم","","adhkar",1);','refCard(info,"حديث اليوم","مَنْ كان يؤمن بالله واليوم الآخر فليقل خيراً أو ليصمت","رواه البخاري ومسلم","","adhkar",1.22f);')
s=s.replace('refCard(info,"⚽  برشلونة × فياريال","المباراة القادمة","جارٍ تحميل الموعد","","barcelona",1);','refCard(info,"برشلونة","المباراة القادمة","جارٍ تحميل الموعد","","barcelona",1.02f);')
s=s.replace('refCard(info,"۞  الصلاة القادمة","العشاء","--:--","--:--:--","prayer",1.15f);','refCard(info,"الصلاة القادمة","العشاء","--:--","--:--:--","prayer",1.58f);')
s=s.replace('root.addView(info,new LinearLayout.LayoutParams(-1,dp(132)));','root.addView(info,new LinearLayout.LayoutParams(-1,dp(190)));')
s=s.replace('weatherValue=(TextView)weather.getChildAt(1); weatherExtra=(TextView)weather.getChildAt(3);','weatherValue=(TextView)weather.getChildAt(2); weatherExtra=(TextView)weather.getChildAt(3);')
s=s.replace('barcelonaSummary=(TextView)barca.getChildAt(2);','barcelonaSummary=(TextView)barca.getChildAt(3);')
s=s.replace('''        prayerMainView=(TextView)prayer.getChildAt(1); prayerSummary=(TextView)prayer.getChildAt(2);''','''        // Live prayer references are retained by refCard().''')
a=s.index("    private LinearLayout refCard(")
b=s.index("\n\n    private LinearLayout cinematicCard(",a)
method = r'''    private LinearLayout refCard(LinearLayout row,String title,String main,String sub,String foot,String section,float weight) {
        LinearLayout c=new LinearLayout(this); c.setOrientation(LinearLayout.VERTICAL); c.setGravity(Gravity.CENTER);
        c.setLayoutDirection(View.LAYOUT_DIRECTION_RTL); c.setPadding(dp(12),dp(9),dp(12),dp(9));
        c.setBackground(cardSurface(false)); c.setFocusable(true); c.setFocusableInTouchMode(true); c.setId(View.generateViewId());
        c.setOnFocusChangeListener((v,f)->c.setBackground(cardSurface(f))); c.setOnClickListener(v->openSection(section));
        TextView emblem=text(cardEmblem(section),section.equals("barcelona")?34:27,gold,true); emblem.setGravity(Gravity.CENTER);
        c.addView(emblem,new LinearLayout.LayoutParams(-1,dp(38)));
        TextView h=text(title,16,Color.WHITE,true); h.setGravity(Gravity.CENTER); c.addView(h,new LinearLayout.LayoutParams(-1,dp(27)));
        TextView m=text(main,section.equals("adhkar")?17:(section.equals("weather")?36:24),section.equals("prayer")?gold:Color.WHITE,true);
        m.setGravity(Gravity.CENTER); m.setMaxLines(section.equals("adhkar")?3:2); m.setLineSpacing(dp(2),1f);
        c.addView(m,new LinearLayout.LayoutParams(-1,0,1));
        TextView subView=text(sub,section.equals("adhkar")?13:15,Color.WHITE,false); subView.setGravity(Gravity.CENTER); subView.setMaxLines(3);
        c.addView(subView,new LinearLayout.LayoutParams(-1,dp(32)));
        if(foot!=null&&!foot.isEmpty()){TextView f=text(foot,13,section.equals("adhkar")?gold:Color.WHITE,true);f.setGravity(Gravity.CENTER);c.addView(f,new LinearLayout.LayoutParams(-1,dp(22)));}
        if("prayer".equals(section)){
            TextView ring=text("--:--:--",16,Color.WHITE,true);ring.setGravity(Gravity.CENTER);
            android.graphics.drawable.GradientDrawable oval=new android.graphics.drawable.GradientDrawable();
            oval.setShape(android.graphics.drawable.GradientDrawable.OVAL);oval.setColor(Color.argb(110,4,16,34));oval.setStroke(dp(4),gold);
            ring.setBackground(oval);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(dp(96),dp(96));rp.gravity=Gravity.CENTER;rp.topMargin=dp(4);c.addView(ring,rp);
            mainCountdownView=ring;prayerMainView=m;prayerSummary=subView;
        }
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-1,weight);lp.setMargins(dp(6),dp(4),dp(6),dp(4));row.addView(c,lp);return c;
    }
    private String cardEmblem(String section){
        switch(section){case "weather":return "☾  ☁";case "adhkar":return "۞  ﷽";case "barcelona":return "🏆";case "prayer":return "۞";default:return "✦";}
    }
    private android.graphics.drawable.Drawable cardSurface(boolean focused){
        android.graphics.drawable.GradientDrawable g=new android.graphics.drawable.GradientDrawable(
            android.graphics.drawable.GradientDrawable.Orientation.TOP_BOTTOM,
            new int[]{Color.argb(232,5,18,39),Color.argb(210,10,28,49),Color.argb(242,5,15,30)});
        g.setCornerRadius(dp(28));g.setStroke(focused?dp(3):dp(2),focused?Color.WHITE:gold);return g;
    }
'''
s=s[:a]+method+s[b:]
s=s.replace("versionCode 20","versionCode 21").replace("versionName '0.20.0-preview'","versionName '0.21.0-preview'")
java.write_text(s,encoding="utf-8")
