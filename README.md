
■環境について　

・以下のダウンロードが必要
chrome 115.0.5790.111
chrome.exe
debug.log

■構築方法
clone後 パッケージをダウンロード
$pip install selenium
$pip install cryptography
$pip install influxdb-client

chrome *1 と
chromeDriver *2
https://sites.google.com/chromium.org/driver/downloads


★一回実行して権限を許可しないとダメ？

browserディレクトリを作成
chromeディレクトリを作成
chrome配下に以下を配置
・バイナリ *1のこと
・chrome.exe

driver\chrome配下に以下を配置
・chromedriver.exe *2
・LICENSE.chromedriver *2


◆使い方
modeによって変わります
■ mode (-m)
'jra-odds','nar-odds','jra-result','nar-result'
■ dev-flag (-d)
デフォルト false, trueの場合指定
