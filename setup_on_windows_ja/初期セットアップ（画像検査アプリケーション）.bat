@echo off

rem Pythonのバージョンを確認する
echo Pythonのバージョンを確認します。
python --version 2>NUL

rem エラーレベルをチェックして処理を分岐
if errorlevel 1 (
    rem Pythonがインストールされていない場合
    echo ------------------------------------------------------------
    echo Python3.9をインストールしてください。
    echo ------------------------------------------------------------
    pause
    exit
) else (
    rem Pythonがインストールされている場合
    for /f "tokens=2" %%A in ('python --version 2^>^&1') do (
        set "python_version=%%A"
    )
    
    rem バージョンが3.9系かどうかをチェック
    echo %python_version% | findstr /r "^3\.9\..*"
    if %errorlevel% == 0 (
        echo Python3.9がインストールされています。セットアップを開始します。
    ) else (
        echo ------------------------------------------------------------
        echo Pythonのバージョンが違います。Python3.9をインストールしてください。
        echo ------------------------------------------------------------
        pause
        exit
    )
)

rem 展開するZIPファイルを指定
set zipFilePath=visual_inspection-main.zip

rem 展開先フォルダを指定
set destFolderPath=.\

rem 実行するPowerShellのコマンドレットを組み立て
set psCommand=powershell -NoProfile -ExecutionPolicy Unrestricted Expand-Archive -Path %zipFilePath% -DestinationPath %destFolderPath% -Force

rem PowerShellで展開を実行
echo ZIPファイルを展開中...
%psCommand%

rem 展開結果を確認
if %errorlevel% == 0 (
    echo %zipFilePath% ファイルを展開しました。
) else (
    echo ------------------------------------------------------------
    echo %zipFilePath% ファイルの展開に失敗しました。
    echo ------------------------------------------------------------
    pause
    exit
)

cd .\visual_inspection-main

rem Pythonの仮想環境を作成
echo Python仮想環境を作成中...
python -m venv .inspection_app

rem Pythonの仮想環境を起動
call ".\.inspection_app\Scripts\activate.bat"

rem pipをアップグレード
echo pipをアップグレード中...
python -m pip install --upgrade pip

rem ライブラリをインストール
echo Pythonライブラリをインストール中...
pip install -r requirements.txt

echo ------------------------------------------------------------
echo 画像検査アプリケーションの初期セットアップが正常完了しました。
echo ------------------------------------------------------------

pause
exit