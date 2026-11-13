from pathlib import Path
root = Path("source/CleanYourTV-Independent")
java = root / "app/src/main/java/ae/cleanyourtv/independent/MainActivity.java"
s = java.read_text(encoding="utf-8")
p = Path("patches/v21-native-cards-snippet.py")
exec(compile(p.read_text(encoding="utf-8"), str(p), "exec"))
java.write_text(s, encoding="utf-8")
