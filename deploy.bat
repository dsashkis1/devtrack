@echo off
chcp 65001 > nul
title DevTrack — Deploy אוטומטי

echo.
echo ╔══════════════════════════════════════════════╗
echo ║       DevTrack — Deploy ל-GitHub + Render    ║
echo ╚══════════════════════════════════════════════╝
echo.

:: ── שלב 1: בדיקת Git ──
git --version > nul 2>&1
if errorlevel 1 (
    echo [!] Git לא מותקן — מוריד ומתקין...
    echo     https://git-scm.com/download/win
    echo.
    echo     לאחר ההתקנה — הרץ את הסקריפט מחדש
    pause
    start https://git-scm.com/download/win
    exit /b
)
echo [✓] Git נמצא

:: ── שלב 2: בדיקת GitHub CLI ──
gh --version > nul 2>&1
if errorlevel 1 (
    echo [!] GitHub CLI לא מותקן — מוריד...
    winget install GitHub.cli > nul 2>&1
    if errorlevel 1 (
        echo     winget נכשל — פתיחה ידנית
        start https://cli.github.com/
        echo.
        echo     התקן GitHub CLI ואז הרץ מחדש
        pause
        exit /b
    )
    :: רענון PATH
    call refreshenv > nul 2>&1
    gh --version > nul 2>&1
    if errorlevel 1 (
        echo [!] נדרש להפעיל מחדש את CMD לאחר ההתקנה
        pause
        exit /b
    )
)
echo [✓] GitHub CLI נמצא

:: ── שלב 3: GitHub Login ──
gh auth status > nul 2>&1
if errorlevel 1 (
    echo.
    echo [→] התחברות ל-GitHub ^(יפתח דפדפן^)...
    gh auth login --web --git-protocol https
    if errorlevel 1 (
        echo [!] כניסה נכשלה
        pause
        exit /b
    )
)
echo [✓] GitHub מחובר

:: ── שלב 4: יצירת Repository ──
echo.
echo [→] יוצר repository "devtrack" ב-GitHub...
cd /d "%~dp0"

:: אתחול git
if not exist ".git" (
    git init
    git add .
    git commit -m "DevTrack initial commit"
)

:: יצירת repo ב-GitHub
gh repo view devtrack > nul 2>&1
if errorlevel 1 (
    gh repo create devtrack --public --source=. --remote=origin --push
    if errorlevel 1 (
        echo [!] יצירת repository נכשלה
        pause
        exit /b
    )
) else (
    git remote remove origin > nul 2>&1
    gh repo view devtrack --json sshUrl -q .sshUrl > nul 2>&1
    for /f "tokens=*" %%i in ('gh repo view devtrack --json url -q .url') do set REPO_URL=%%i
    git remote add origin %REPO_URL%.git
    git push -u origin main 2> nul || git push -u origin master
)

echo [✓] קוד ב-GitHub!

:: ── שלב 5: Render Deploy ──
echo.
echo ╔══════════════════════════════════════════════╗
echo ║   עכשיו — פתיחת Render.com לאישור אחרון    ║
echo ╚══════════════════════════════════════════════╝
echo.

:: קבלת שם GitHub username
for /f "tokens=*" %%i in ('gh api user --jq .login') do set GH_USER=%%i
echo     שם משתמש: %GH_USER%
echo     repository: devtrack
echo.

echo [→] פותח Render.com...
echo     1. לחץ "New +" → "Web Service"
echo     2. בחר: %GH_USER%/devtrack
echo     3. הגדרות יתמלאו אוטומטית מ-render.yaml
echo     4. לחץ "Create Web Service"
echo.
echo     זה הדבר היחיד שצריך לעשות ידנית!
echo.

start https://dashboard.render.com/new/web

echo.
echo ═══════════════════════════════════════════════
echo  לאחר ה-deploy תקבל URL כמו:
echo  https://devtrack-xxxx.onrender.com
echo.
echo  שמור את ה-URL הזה!
echo ═══════════════════════════════════════════════
echo.
pause
