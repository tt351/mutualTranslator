## 概要
日本語と英語を相互に翻訳するアプリ  
常に最前面に表示します。  
非アクティブにしておくと透過します。  
escで閉じます。  
![ウィンドウ画像](/img/window.png)  

## 制作背景
変数名を決めたりエラー文の翻訳にgoogle翻訳を使っていますが、ブラウザのタブに埋もれたり、日本語と英語の切り替えボタンをよく押したり、画面の切り替えが頻発してましたので、このようなアプリを制作しました。  
常に最前面表示なので埋もれず、非アクティブなら透過するので邪魔になりにくいです。
## 開発環境
Windows11  
vs code  
python3.13.2
## モジュールのインストール
仮想環境内  
python -m pip install -r requirements.txt

## ツール
PySide6...GUIアプリをpythonで開発するライブラリ（商用利用可）  
https://doc.qt.io/qtforpython-6/gettingstarted.html#getting-started  

googletrans...非公式ですがgoogle翻訳が使用できるライブラリ（常に適切に動作するかは保証しませんが、手軽に無料で実装できます）  
https://pypi.org/project/googletrans/  

## バイブコーディング
今回GeminiやgithubCopilotを使用し、ツールの選定からコーディング、軽微な修正までやっていただき、1日で出来ました。便利ですね。  

## 課題
入力文字が英語なのに日本語判定となるバグがあるため判別プロセスを修正予定。