@echo off
echo ========================================
echo Markdown to Word Paste Helper V1.0 Build Script
echo ========================================

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release" rmdir /s /q "release"

echo Building, please wait...

pyinstaller --noconfirm --onefile --windowed --name "MarkdownWordPasteHelper_V1.0" ^
    --icon="src/resources/icon.ico" ^
    --add-data "src/resources/icon.ico;resources" ^
    --hidden-import "markdown.extensions.extra" ^
    --hidden-import "markdown.extensions.codehilite" ^
    --hidden-import "markdown.extensions.toc" ^
    --hidden-import "markdown.extensions.sane_lists" ^
    --hidden-import "markdown.extensions.nl2br" ^
    "src/main.py"

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b %errorlevel%
)

REM Create release directory and move exe
mkdir release
move "dist\MarkdownWordPasteHelper_V1.0.exe" "release\"

echo.
echo ========================================
echo Build successful! EXE is in release folder.
echo ========================================
pause