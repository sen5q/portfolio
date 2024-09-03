::職場から直接ファイルの持ち出しはできないため記憶を頼りに書きましたが、
::自宅のWin10からは動作確認できなかったのでもしかしたらどこか間違っているかもしれません

@echo off
setlocal

::今日の日付
for /f "tokens=2 delims=="%%a in ('wmic os get localdatetime /value') do set datetime=%%a
set year1=%datetime:~0,4%
set month1=%datetime:~4,2%
set day1=%datetime:~6,2%

::今日の曜日
for /f "tokens=2 delims==" %%i in ('wmic path win32_localtime get dayofweek/value') do set dayofweek=%%i
setlocal enabledelayedexpansion
set dowlist1=日月火水木金土
set dow1=!dowlist1:~%dayofweek%,1!

::今日のパス
set filePath1=C:\abc\abc\abc¥%year1%%month1%%day1%(%dow1%)¥abc\abc\abc\sheet.xlsx"
start %filePath1%