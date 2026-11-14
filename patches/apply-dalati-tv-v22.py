from pathlib import Path
import re

root = Path("source/CleanYourTV-Independent")
java = root / "app/src/main/java/ae/cleanyourtv/independent/MainActivity.java"
s = java.read_text(encoding="utf-8")

# Give the dashboard information cards enough vertical room for their actual contents.
s = s.replace('root.addView(info,new LinearLayout.LayoutParams(-1,dp(190)));',
              'root.addView(info,new LinearLayout.LayoutParams(-1,dp(220)));', 1)

# Prevent long live fixture and weather strings from being clipped inside fixed-height labels.
s = s.replace('''        TextView subView=text(sub,section.equals("adhkar")?13:15,Color.WHITE,false); subView.setGravity(Gravity.CENTER); subView.setMaxLines(3);
        c.addView(subView,new LinearLayout.LayoutParams(-1,dp(32)));''',
'''        int subSize = section.equals("barcelona") ? 12 : (section.equals("weather") ? 12 : (section.equals("adhkar") ? 13 : 15));
        int subHeight = section.equals("barcelona") ? 44 : (section.equals("weather") ? 42 : 32);
        TextView subView=text(sub,subSize,Color.WHITE,false); subView.setGravity(Gravity.CENTER);
        subView.setMaxLines(section.equals("barcelona") || section.equals("weather") ? 3 : 3);
        subView.setEllipsize(android.text.TextUtils.TruncateAt.END);
        c.addView(subView,new LinearLayout.LayoutParams(-1,dp(subHeight)));''', 1)

# The official AWQAF homepage has English and Arabic page variants. Parse both formats,
# normalize Arabic-Indic digits, and accept either the explicit countdown or official prayer timetable.
a=s.index("    private void readOfficialPrayerPage() {")
b=s.index("\n    private String arabicPrayerName(", a)
method = r'''    private void readOfficialPrayerPage() {
        if (prayerDataWebView == null) return;
        prayerDataWebView.evaluateJavascript("(function(){return document.body ? document.body.innerText : '';})()", value -> {
            try {
                String body = new org.json.JSONArray("[" + value + "]").getString(0);
                body = westernDigits(body).replace('\u00a0', ' ');
                Pattern next = Pattern.compile("(?i)Next\\s*prayer\\s*[:：]?\\s*(fajr|zuhr|dhuhr|asr|maghrib|isha)\\s*(?:in\\s*)?(\\d{1,2}:\\d{2}:\\d{2})");
                Matcher m = next.matcher(body);
                if (m.find()) {
                    nextPrayerLabel = arabicPrayerName(m.group(1));
                    String[] parts = m.group(2).split(":");
                    prayerRemainingSeconds = Integer.parseInt(parts[0])*3600L + Integer.parseInt(parts[1])*60L + Integer.parseInt(parts[2]);
                    android.util.Log.i("DalatiPrayer","Countdown parsed: prayer="+nextPrayerLabel+" seconds="+prayerRemainingSeconds);
                    updatePrayerCard();
                    return;
                }

                Pattern arabicNext = Pattern.compile("الصلاة\\s*القادمة\\s*[:：]?\\s*(الفجر|الظهر|العصر|المغرب|العشاء)\\s*(?:خلال\\s*)?(\\d{1,2}:\\d{2}:\\d{2})?");
                // Some AWQAF page builds render the remaining time as prose rather than HH:MM:SS.
                Pattern englishRemaining = Pattern.compile("(?i)Next\\s*prayer\\s*[:：]?\\s*(Fajr|Zuhr|Dhuhr|Asr|Maghrib|Isha).*?In\\s+(?:(\\d+)\\s+Hours?)?\\s*(?:(\\d+)\\s+Minutes?)?\\s*(?:(\\d+)\\s+Seconds?)?");
                Matcher er = englishRemaining.matcher(body);
                if (er.find() && (er.group(2) != null || er.group(3) != null || er.group(4) != null)) {
                    nextPrayerLabel = arabicPrayerName(er.group(1));
                    prayerRemainingSeconds = (er.group(2)==null?0:Integer.parseInt(er.group(2))*3600L)
                        + (er.group(3)==null?0:Integer.parseInt(er.group(3))*60L)
                        + (er.group(4)==null?0:Integer.parseInt(er.group(4)));
                    updatePrayerCard();
                    return;
                }
                Matcher am = arabicNext.matcher(body);
                if (am.find() && am.group(2) != null) {
                    nextPrayerLabel = am.group(1);
                    String[] parts = am.group(2).split(":");
                    prayerRemainingSeconds = Integer.parseInt(parts[0])*3600L + Integer.parseInt(parts[1])*60L + Integer.parseInt(parts[2]);
                    updatePrayerCard();
                    return;
                }

                String[] englishLabels = {"Fajr","Dhuhr","Asr","Maghrib","Isha"};
                String[] arabicLabels = {"الفجر","الظهر","العصر","المغرب","العشاء"};
                String[] patterns = {
                    "(?i)Fajr\\s*[:：-]?\\s*(\\d{1,2}:\\d{2})\\s*(am|pm)?",
                    "(?i)(?:Zuhr|Dhuhr)\\s*[:：-]?\\s*(\\d{1,2}:\\d{2})\\s*(am|pm)?",
                    "(?i)Asr\\s*[:：-]?\\s*(\\d{1,2}:\\d{2})\\s*(am|pm)?",
                    "(?i)Maghrib\\s*[:：-]?\\s*(\\d{1,2}:\\d{2})\\s*(am|pm)?",
                    "(?i)Isha\\s*[:：-]?\\s*(\\d{1,2}:\\d{2})\\s*(am|pm)?"
                };
                for (int i=0; i<patterns.length; i++) {
                    Matcher pt = Pattern.compile(patterns[i]).matcher(body);
                    if (pt.find()) dailyPrayerTimes[i] = pt.group(1) + (pt.group(2)==null ? "" : " "+pt.group(2).toUpperCase(Locale.ROOT));
                }

                java.time.LocalTime now = java.time.LocalTime.now(ZoneId.of("Asia/Dubai"));
                long best = Long.MAX_VALUE;
                int bestIndex = -1;
                for (int i=0; i<dailyPrayerTimes.length; i++) {
                    String t = dailyPrayerTimes[i];
                    if (t == null || !t.matches("\\d{1,2}:\\d{2}(?:\\s+(?:AM|PM))?")) continue;
                    java.time.format.DateTimeFormatter fmt = t.toUpperCase(Locale.ROOT).contains("AM") || t.toUpperCase(Locale.ROOT).contains("PM")
                        ? java.time.format.DateTimeFormatter.ofPattern("h:mm a", Locale.US)
                        : java.time.format.DateTimeFormatter.ofPattern("H:mm", Locale.US);
                    java.time.LocalTime prayerTime = java.time.LocalTime.parse(t.toUpperCase(Locale.ROOT), fmt);
                    long seconds = java.time.Duration.between(now, prayerTime).getSeconds();
                    if (seconds <= 0) seconds += 24*3600L;
                    if (seconds < best) { best=seconds; bestIndex=i; }
                }
                if (bestIndex >= 0) {
                    nextPrayerLabel = arabicLabels[bestIndex];
                    prayerRemainingSeconds = best;
                    updatePrayerCard();
                } else {
                    android.util.Log.w("DalatiPrayer","No supported prayer countdown or timetable pattern found; bodyLength="+body.length());
                    if (prayerSummary != null && prayerRemainingSeconds < 0)
                        prayerSummary.setText("بانتظار مواقيت الصلاة الرسمية من الهيئة");
                }
            } catch(Exception ignored) {
                android.util.Log.e("DalatiPrayer","Prayer parsing exception",ignored);
                if (prayerSummary != null && prayerRemainingSeconds < 0)
                    prayerSummary.setText("جارٍ تحميل مواقيت الصلاة الرسمية…");
            }
        });
    }
'''
s=s[:a]+method+s[b:]

# Request the official English view explicitly, while parser supports Arabic if the server redirects.
s=s.replace('prayerDataWebView.loadUrl("https://www.awqaf.ae/?lang=en");',
            'prayerDataWebView.loadUrl("https://www.awqaf.gov.ae/?lang=en");', 1)
s=s.replace('''        prayerDataWebView.setWebViewClient(new android.webkit.WebViewClient(){@Override public void onPageFinished(android.webkit.WebView v,String u){readOfficialPrayerPage();}});''',
'''        prayerDataWebView.setWebViewClient(new android.webkit.WebViewClient(){
            @Override public void onPageStarted(android.webkit.WebView v,String u,android.graphics.Bitmap icon){
                android.util.Log.i("DalatiPrayer","AWQAF page started: "+u);
            }
            @Override public void onPageFinished(android.webkit.WebView v,String u){
                android.util.Log.i("DalatiPrayer","AWQAF page finished: "+u);
                readOfficialPrayerPage();
            }
            @Override public void onReceivedError(android.webkit.WebView v, android.webkit.WebResourceRequest req, android.webkit.WebResourceError err){
                if(req.isForMainFrame()) android.util.Log.e("DalatiPrayer","AWQAF load error: "+req.getUrl()+" code="+err.getErrorCode()+" "+err.getDescription());
            }
            @Override public void onReceivedHttpError(android.webkit.WebView v,android.webkit.WebResourceRequest req,android.webkit.WebResourceResponse response){
                if(req.isForMainFrame()) android.util.Log.e("DalatiPrayer","AWQAF HTTP error: "+req.getUrl()+" status="+response.getStatusCode()+" "+response.getReasonPhrase());
            }
            @Override public void onReceivedSslError(android.webkit.WebView v,android.webkit.SslErrorHandler handler,android.net.http.SslError error){
                android.util.Log.e("DalatiPrayer","AWQAF SSL error: "+error);
                handler.cancel();
            }
        });
        prayerDataWebView.setWebChromeClient(new android.webkit.WebChromeClient(){
            @Override public boolean onConsoleMessage(android.webkit.ConsoleMessage message){
                android.util.Log.i("DalatiPrayer","AWQAF JS console: "+message.message()+" line="+message.lineNumber());
                return true;
            }
        });''',1)
s=s.replace('''                body = westernDigits(body).replace('\\u00a0', ' ');
                android.util.Log.i("DalatiPrayer","AWQAF body received length="+body.length());
                if(body.length()>0) android.util.Log.i("DalatiPrayer","AWQAF body sample="+body.substring(0,Math.min(900,body.length())).replace('\\n',' '));''',
'''                body = westernDigits(body).replace('\\u00a0', ' ');
                android.util.Log.i("DalatiPrayer","AWQAF body length="+body.length()+" sample="+body.substring(0,Math.min(700,body.length())).replace('\\n',' '));''',1)
s=s.replace('''            } catch(Exception ignored) {
                if (prayerSummary != null && prayerRemainingSeconds < 0)''',
'''            } catch(Exception ignored) {
                android.util.Log.e("DalatiPrayer","Prayer parse exception",ignored);
                if (prayerSummary != null && prayerRemainingSeconds < 0)''',1)
s=s.replace('''            } catch(Exception e) { runOnUiThread(() -> {
                android.util.Log.e("DalatiWeather","Open-Meteo request failed",e);
                weatherSnapshot = "الطقس في عجمان غير متاح حاليًا";''',
'''            } catch(Exception e) { android.util.Log.e("DalatiWeather","Open-Meteo request failed",e); runOnUiThread(() -> {
                weatherSnapshot = "الطقس في عجمان غير متاح حاليًا";''',1)
s=s.replace('section.equals("weather")?36:24','section.equals("weather")?20:24',1)

java.write_text(s, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
if "versionCode 21" not in g: raise SystemExit("Expected v21 metadata")
g = g.replace("versionCode 21", "versionCode 22", 1).replace("versionName '0.21.0-preview'", "versionName '0.22.0-preview'", 1)
gradle.write_text(g, encoding="utf-8")
print("Applied v22: larger dashboard cards, wrapped fixture/weather text, bilingual AWQAF prayer parsing with official timetable fallback.")
