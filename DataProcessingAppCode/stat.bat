@echo off
cd /d D:\Data\PythonApp

"C:\Users\zhao1\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe" -F -w -i DataProcessing.ico ^
--hidden-import=scipy ^
--hidden-import=scipy.optimize ^
--hidden-import=scipy.interpolate ^
--hidden-import=scipy.sparse ^
--hidden-import=scipy.spatial ^
--hidden-import=scipy.stats ^
--hidden-import=openpyxl ^
--hidden-import=pandas ^
--hidden-import=numpy ^
PythonApp.py

echo.
echo ✅ 打包完成！
pause