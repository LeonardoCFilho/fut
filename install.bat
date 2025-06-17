@echo off
echo Building fut application...
docker build -t fut-app .

echo Installing fut command...
echo @echo off > "%USERPROFILE%\fut.bat"
echo docker run --rm -it fut-app %%* >> "%USERPROFILE%\fut.bat"

echo Add %USERPROFILE% to your PATH if not already there
echo Installation complete! You can now use: fut ^<args^>