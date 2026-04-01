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
## 仮想環境の作り方・モジュールのインストール
### vscode  
拡張機能Python Environmentsをインストールする  
サイドバー（アクティビティバー）のPython内からENVIRONMENT MANAGERSから環境の作成をする  
プロジェクトの環境として設定する  
->仮想環境ができました

プロジェクトの依存関係をインストール 依存関係ファイルで見つかったパッケージをインストールします を選択
requirements.txtをチェック、OK  
->モジュールがインストールできました

### 通常
仮想環境を作成
python -m venv .venv

仮想環境への切り替え
.venv\Scripts\activate.bat

コマンドプロンプト先頭に下記が表示されたら切り替え完了
(.venv)

依存関係ファイルのパッケージをインストール
python -m pip install -r requirements.txt

### （requirements.txtの作成コマンド）
pip freeze > requirements.txt

## exeファイル化
pyinstaller --noconsole --onefile --icon=myicon.ico --name=相互翻訳ツール main.py

## ツール
PySide6...GUIアプリをpythonで開発するライブラリ（商用利用可）  
https://doc.qt.io/qtforpython-6/gettingstarted.html#getting-started  

googletrans...非公式ですがgoogle翻訳が使用できるライブラリ（常に適切に動作するかは保証しませんが、手軽に無料で実装できます）  
https://pypi.org/project/googletrans/  

## バイブコーディング
今回GeminiやgithubCopilotを使用し、ツールの選定からコーディング、軽微な修正までやっていただきました。便利ですね。  
