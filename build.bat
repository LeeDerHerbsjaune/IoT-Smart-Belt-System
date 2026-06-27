@echo off
:: Tự động di chuyển đến thư mục chứa chính file .bat này
cd /d "%~dp0"

:: Kiểm tra xem PyInstaller đã được cài chưa, nếu chưa thì tự cài
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller chưa được cài đặt. Đang tiến hành cài đặt...
    pip install pyinstaller
)

:: Tiến hành build app
echo Bắt đầu đóng gói ứng dụng...
pyinstaller --onefile main.py

echo Hoàn thành! Kiểm tra file .exe trong thư mục "dist".
pause