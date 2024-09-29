@ECHO OFF
setlocal

:: Step 1: Run sphinx-quickstart
sphinx-quickstart || (
    echo !RED!BOLD FAILED: sphinx-quickstart did not run !RESET!
    exit /b 1
)
echo !GREEN! SUCCESSFUL [1/6]: sphinx-quickstart completed !RESET!

:: Step 2: Move up one directory
cd ..

:: Step 3: Run sphinx-apidoc to generate rst files
sphinx-apidoc -o docs . || (
    echo !RED!BOLD FAILED: Couldn't generate rst files !RESET!
    exit /b 1
)
echo !GREEN! SUCCESSFUL [2/6]: Created rst files !RESET!

:: Step 4: Change directory to 'docs'
cd docs || (
    echo !RED!BOLD FAILED: Couldn't change directory to docs !RESET!
    exit /b 1
)

:: Step 5: Delete lines 8 to 12 and
powershell -Command ^
    "$content = Get-Content 'index.rst';" ^
    "$newContent = $content[0..7] + $content[13..($content.Count - 1)];" ^
    "$newContent | Set-Content 'index.rst';"

:: Check ERRORLEVEL after the PowerShell command
if ERRORLEVEL 1 (
    echo !RED! FAILED: Couldn't delete lines in index.rst !RESET!
    exit /b 1
)
echo !GREEN! SUCCESSFUL [3/6]: Deleted lines in index.rst !RESET!

:: Insert 'modules' into index.rst
powershell -Command ^
    "$content = Get-Content 'index.rst';" ^
    "$newContent = $content[0..11] + '    modules' + $content[12..($content.Count - 1)];" ^
    "$newContent | Set-Content 'index.rst';"

:: Check ERRORLEVEL after the PowerShell command
if ERRORLEVEL 1 (
    echo !RED! FAILED: Couldn't insert 'modules' into index.rst !RESET!
    exit /b 1
)
echo !GREEN! SUCCESSFUL [4/6]: Inserted 'modules' into index.rst !RESET!

:: Step 6: Modify extensions in conf.py
powershell -Command ^
    "(Get-Content 'conf.py') | ForEach-Object { if ($_ -match '^extensions =') { 'extensions = [\"sphinx.ext.todo\", \"sphinx.ext.viewcode\", \"sphinx.ext.autodoc\"]' } else { $_ } } | Set-Content 'conf.py';"

if ERRORLEVEL 1 (
    echo !RED! FAILED: Couldn't modify extensions in config.py !RESET!
    exit /b 1
)
echo !GREEN! SUCCESSFUL [5/6]: Modified extensions in conf.py !RESET!

:: Step 7: Modify theme in conf.py
powershell -Command ^
    "(Get-Content 'conf.py') | ForEach-Object { if ($_ -match '^html_theme =') { 'html_theme = \"sphinx_rtd_theme\"' } else { $_ } } | Set-Content 'conf.py';"

if ERRORLEVEL 1 (
    echo !RED! FAILED: Couldn't modify theme in config.py !RESET!
    exit /b 1
)
echo !GREEN! SUCCESSFUL [6/6]: Modified theme in conf.py !RESET!

endlocal
