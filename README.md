# DevTrack 🚀

ניהול פרויקטי פיתוח — Flask + SQLite + HTML

---

## הרצה מקומית (Windows)

```bash
pip install -r requirements.txt
python app.py
```
פתח דפדפן: http://localhost:7474

---

## Deploy ל-Render.com (חינמי)

### שלב 1 — GitHub
1. צור חשבון GitHub בחינם: https://github.com
2. צור repository חדש (ריבועי + → New repository)
3. שם: `devtrack`
4. לחץ Create repository

### שלב 2 — העלה קבצים ל-GitHub
דרך הממשק של GitHub (ללא git):
1. לחץ "uploading an existing file"
2. גרור את כל הקבצים מהתיקייה:
   - app.py
   - requirements.txt
   - Procfile
   - render.yaml
   - .gitignore
   - static/index.html  ← חשוב: תיקיית static!
3. לחץ Commit changes

### שלב 3 — Render
1. צור חשבון: https://render.com (חינמי, כניסה עם GitHub)
2. לחץ "New +" → "Web Service"
3. בחר את ה-repository devtrack
4. הגדרות:
   - **Name:** devtrack
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1`
5. לחץ "Create Web Service"
6. המתן ~2 דקות → קבל URL כמו: `https://devtrack-xxxx.onrender.com`

### ⚠️ חשוב — SQLite על Render
Render Free Tier = דיסק זמני.
הנתונים נמחקים כשהשרת נרדם (אחרי 15 דק' חוסר שימוש).

**פתרון לטסט:** מספיק. ייצא JSON לפני שסוגר.
**פתרון לאמיתי:** הוסף Render Disk ($1/חודש) — שנה DB_PATH ב-render.yaml.

---

## מבנה קבצים

```
devtrack/
├── app.py              ← שרת Flask + API
├── requirements.txt    ← תלויות Python
├── Procfile            ← הוראות הפעלה ל-Render
├── render.yaml         ← הגדרות Render
├── .gitignore
└── static/
    └── index.html      ← ממשק המשתמש
```

## API Endpoints

| Method | Path | תיאור |
|--------|------|-------|
| GET | /api/projects | כל הפרויקטים |
| POST | /api/projects | פרויקט חדש |
| PUT | /api/projects/:id | עדכון פרויקט |
| DELETE | /api/projects/:id | מחיקת פרויקט |
| POST | /api/projects/:id/versions | הוספת גרסה |
| POST | /api/run | הרצת .bat (מקומי בלבד) |
| GET | /api/health | בדיקת חיבור |
