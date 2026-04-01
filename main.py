import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QLabel, QFrame, QPushButton)
from PySide6.QtCore import Qt, QPoint, QSize, Slot, QTimer, QEvent
from PySide6.QtGui import QMouseEvent, QKeyEvent, QIcon

import os

#翻訳側で使用
import asyncio
from googletrans import Translator
import re

# 定数宣言（パラメータ）
TRANSPARENT_VALUE = 0.4     #非アクティブ状態のときの透明度（0.0～1.0）
TRANSPARENT_TIME = 10000    #非アクティブ状態になってから透明化するまでの時間（ミリ秒）
CONFIRM_TEXT_TIME = 1000    #テキスト入力が完了したとみなすまでの時間（ミリ秒）
FADE_TIME = 40              #フェードアウトのアニメーションの更新間隔（ミリ秒）
FADE_STEP = 0.01            #フェードアウトのアニメーションで透明度を減少させる量（0.0～1.0）

class MutualTranslator(QWidget):
    def __init__(self):
        super().__init__()
        # self.translator = Translator()

        # クラス内変数宣言
        self.old_pos = None
        self.current_opacity = 1.0       # 現在の透明度管理用

        #アイコンの設定
        icon_path = "myicon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # --- タイマーの設定 ---
        self.input_timer = QTimer(self)
        self.input_timer.setSingleShot(True)  # 1回だけ実行する設定
        self.input_timer.timeout.connect(self.handle_translate) # タイムアップで発火

        # --- 非アクティブタイマー ---
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.make_transparent)

        # フェードアウト用のアニメーションタイマー
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.animate_fade_out)

        # --- コピーメッセージ消去タイマー ---
        self.copy_messege_delete_timer = QTimer(self)
        self.copy_messege_delete_timer.setSingleShot(True)
        self.copy_messege_delete_timer.timeout.connect(self.delete_copy_messege)

        self.init_ui()

    def init_ui(self):
        # 1. ウィンドウ設定: 枠なし、常に最前面
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # メインのコンテナ（背景や角丸をCSSで制御するため）
        self.container = QFrame(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: #ffffff;
                border: 2px solid #4A90E2;
                border-radius: 10px;
            }
            QLabel { color: #333; font-size: 12px; }
            QTextEdit { 
                border: 1px solid #ddd; 
                border-radius: 4px; 
                background: #fafafa;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self.container)
        
        # タイトル兼ドラッグハンドル
        self.title_label = QLabel("● 相互翻訳ツール（ドラッグして移動）")
        self.title_label.setStyleSheet("font-weight: bold; color: #4A90E2; padding-bottom: 5px;")
        layout.addWidget(self.title_label)        
        
        # 入力エリア
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("日本語または英語を入力...")
        self.input_edit.setFixedHeight(40) # 入力欄は固定、出力で可変させる
        self.input_edit.textChanged.connect(self.reset_input_timer)
        self.input_edit.textChanged.connect(self.inputting_status)
        layout.addWidget(self.input_edit)

        # ボタン
        copy_button_layout = QHBoxLayout()
        self.copy_button = QPushButton("コピー")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        copy_button_layout.addWidget(self.copy_button)

        self.clear_button = QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_text)
        copy_button_layout.addWidget(self.clear_button)

        layout.addLayout(copy_button_layout)

        # 区切り線
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #eee;")
        layout.addWidget(line)

        # 出力エリア
        self.output_label = QLabel("翻訳結果はここに表示されます...")
        self.output_label.setWordWrap(True)
        self.output_label.setMinimumHeight(40)
        self.output_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.output_label)

        # ステータスエリア
        self.status_label = QLabel("...")
        self.status_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.status_label)

        # 全体のレイアウト適用
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        self.setMinimumWidth(300)
        self.adjust_window_size()

        self.reset_transparent()#ウィンドウを完全に不透明にし、透明化タイマースタート

    @Slot( str )
    async def translate_text(self, input_text:str)->str:
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF61-\uFF9F]')
        
        if japanese_pattern.search(input_text):
            src_lang = "ja"
            dest_lang = "en"
        else:
            src_lang = "en"
            dest_lang = "ja"
        

        async with Translator() as translator:
            output = await translator.translate(input_text,src=src_lang,dest=dest_lang)
            text = output.text
            # print(f"src_lang ={src_lang} dest_lang = {dest_lang} result:{text}")
            self.result_status(src_lang, dest_lang)
            return text

    @Slot()
    def handle_translate(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            self.output_label.setText("...")
            self.status_label.setText("...")
            self.adjust_window_size()
            return

        try:
            self.status_label.setText("翻訳中...")
            output_text = asyncio.run(self.translate_text(text))
            self.output_label.setText(output_text)            
        except Exception as e:
            self.output_label.setText(f"Error: {e}")

        # 翻訳後にサイズを再計算
        self.adjust_window_size()

    @Slot()  
    def inputting_status(self):
        text = self.input_edit.toPlainText().strip()
        if text:
            self.status_label.setText("入力中...")

    @Slot( str, str )
    def result_status(self, src_lang:str, dest_lang:str):
        self.copy_messege_delete_timer.stop()
        self.status_label.setText(f"{src_lang} -> {dest_lang}")

    @Slot()
    def copy_to_clipboard(self):
        text = self.output_label.text()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        self.status_label.setText("コピーしました!")
        self.copy_messege_delete_timer.start(2000)#上のテキストを削除するタイマ

    @Slot()
    def delete_copy_messege(self):
        self.status_label.setText("...")

    @Slot()
    def reset_inactivity_timer(self):
        pass
    @Slot()
    def make_transparent(self):
        self.current_opacity = 1.0       # 現在の透明度管理用
        self.fade_timer.start(FADE_TIME)

    @Slot()
    def reset_transparent(self):#ウィンドウを完全に不透明に戻す
        self.setWindowOpacity(1.0)  #透明度０
        # self.inactivity_timer.stop()#透明化開始タイマーストップ
        self.fade_timer.stop()#フェードアニメーションタイマーストップ
        self.inactivity_timer.start(TRANSPARENT_TIME)
                

    @Slot()
    def animate_fade_out(self):
        self.current_opacity -= FADE_STEP
        self.setWindowOpacity(self.current_opacity)
        if self.current_opacity <= TRANSPARENT_VALUE:
            self.fade_timer.stop()

    @Slot()
    def clear_text(self):
        self.input_edit.clear()
        self.input_edit.setFocus()

    # 内容に合わせて高さを自動調整
    def adjust_window_size(self):
        self.adjustSize()

    # マウスドラッグによる移動
    def mousePressEvent(self, event:QMouseEvent):
        self.reset_transparent()#ウィンドウを完全に不透明にし、透明化タイマースタート

        if event.button() == Qt.MouseButton.LeftButton:
            # クリック時の座標を保持
            self.old_pos = event.globalPosition().toPoint()
        
        # super().mousePressEvent(event)

    def mouseMoveEvent(self, event:QMouseEvent):
        self.reset_transparent()#ウィンドウを完全に不透明にし、透明化タイマースタート
        if self.old_pos is not None:
            # 移動量を計算してウィンドウを動かす
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event:QMouseEvent):
        self.old_pos = None

    def keyPressEvent(self, event:QKeyEvent):
        # Escキーで終了
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    # ウィンドウの状態変化を検知
    def changeEvent(self, event:QEvent):
        if event.type() == QEvent.Type.ActivationChange:
            if self.isActiveWindow():
                # print("ウィンドウがアクティブになりました")
                self.input_edit.setFocus()
            else:
                # print("ウィンドウが非アクティブになりました")
                pass
        super().changeEvent(event)

    # 入力監視
    def reset_input_timer(self):
        # 文字が入力されるたびに呼ばれる
        # タイマーを1000ミリ秒（1秒）でリスタート
        # 1秒以内に次の入力があれば、前のタイマーは破棄されます
        self.input_timer.start(CONFIRM_TEXT_TIME)
        self.reset_transparent()#ウィンドウを完全に不透明にし、透明化タイマースタート


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MutualTranslator()
    window.show()
    sys.exit(app.exec())