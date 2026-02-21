import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QDialog, QListWidget, QListWidgetItem,
    QScrollArea, QLineEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor


class FolderSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите папку zapret-discord-youtube")
        self.setFixedSize(520, 180)
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: #e2e8f0; border-radius: 12px; }
            QLabel { color: #cbd5e1; }
            QLineEdit { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 6px; padding: 6px; }
            QPushButton { background: #334155; color: #e2e8f0; border: none; border-radius: 8px; padding: 8px 16px; }
            QPushButton:hover { background: #475569; }
            QPushButton#ok { background: #3b82f6; }
            QPushButton#ok:hover { background: #60a5fa; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Укажите путь к папке zapret-discord-youtube")
        title.setFont(QFont("Segoe UI", 12, weight=QFont.Weight.Bold))
        layout.addWidget(title)

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("C:/path/to/zapret-discord-youtube")
        path_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)

        layout.addLayout(path_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ok_btn = QPushButton("Продолжить")
        ok_btn.setObjectName("ok")
        ok_btn.setFixedWidth(140)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку zapret", self.path_edit.text() or os.path.expanduser("~")
        )
        if folder:
            self.path_edit.setText(folder)


class ZapretMainWindow(QMainWindow):
    def __init__(self, zapret_folder):
        super().__init__()
        self.zapret_folder = zapret_folder
        self.is_running = False
        self.selected_strategy = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Zapret")
        self.setFixedSize(820, 720)

        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QLabel { color: #cbd5e1; }
            QPushButton {
                color: white; border: none; border-radius: 10px;
                padding: 10px 24px; font-size: 14px; font-weight: 600;
            }
            QPushButton:hover { filter: brightness(1.15); }
            QPushButton#startBtn { background-color: #22c55e; }
            QPushButton#startBtn:disabled { background-color: #86efac; color: #14532d; opacity: 0.85; }
            QPushButton#stopBtn { background-color: #ef4444; }
            QPushButton#stopBtn:disabled { background-color: #fca5a5; color: #7f1d1d; opacity: 0.7; }
            QListWidget {
                background-color: #1e293b; color: #cbd5e1;
                border: 1px solid #334155; border-radius: 12px;
                font-size: 13px; outline: none;
            }
            QListWidget::item { padding: 10px 16px; border-bottom: 1px solid #334155; }
            QListWidget::item:selected { background-color: #3b82f6; color: white; }
            QScrollBar:vertical { border: none; background: #111827; width: 10px; margin: 0; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #475569; min-height: 40px; border-radius: 5px; }
            QTextEdit {
                background-color: #111827; color: #a5f3fc;
                border: 1px solid #334155; border-radius: 12px;
                font-family: Consolas, monospace; font-size: 12px; padding: 8px;
            }
            QFrame { background-color: #1e293b; border: 1px solid #334155; border-radius: 14px; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 20, 24, 20)

        top_row = QHBoxLayout()
        self.status_label = QLabel("⚡ НЕ ПОДКЛЮЧЕНО")
        self.status_label.setFont(QFont("Segoe UI", 14, weight=QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #94a3b8;")
        top_row.addWidget(self.status_label)
        top_row.addStretch()
        main_layout.addLayout(top_row)

        main_layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)
        btn_layout.addStretch()

        self.start_btn = QPushButton("▶ Запустить")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedWidth(180)
        self.start_btn.clicked.connect(self.toggle_connection)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ Остановить")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedWidth(180)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.toggle_connection)
        btn_layout.addWidget(self.stop_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        main_layout.addSpacing(24)

        title = QLabel("Выбор стратегии")
        title.setFont(QFont("Segoe UI", 16, weight=QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        main_layout.addSpacing(8)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(260)
        scroll_area.setMaximumWidth(360)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        list_widget = QListWidget()
        list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        strategies = [
            "general",
            "general (ALT)",
            "general (ALT2)",
            "general (ALT3)",
            "general (ALT4)",
            "general (ALT5)",
            "general (ALT6)",
            "general (ALT7)",
            "general (ALT8)",
            "general (ALT9)",
            "general (ALT10)",
            "general (ALT11)",
            "general (FAKE TLS AUTO)",
            "general (FAKE TLS AUTO ALT)",
            "general (FAKE TLS AUTO ALT2)",
            "general (FAKE TLS AUTO ALT3)",
            "general (SIMPLE FAKE)",
            "general (SIMPLE FAKE ALT)",
            "general (SIMPLE FAKE ALT2)"
        ]

        for i, name in enumerate(strategies, 1):
            item = QListWidgetItem(f"{i}. {name}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            list_widget.addItem(item)

        list_widget.itemClicked.connect(self.on_strategy_clicked)
        scroll_area.setWidget(list_widget)
        main_layout.addWidget(scroll_area, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addSpacing(80)
        main_layout.addStretch(1)

        log_frame = QFrame()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(16, 16, 16, 16)
        log_layout.setSpacing(8)

        log_title = QLabel("Логи")
        log_title.setFont(QFont("Segoe UI", 13, weight=QFont.Weight.Bold))
        log_layout.addWidget(log_title)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(220)
        self.log.textChanged.connect(lambda: self.log.verticalScrollBar().setValue(
            self.log.verticalScrollBar().maximum()
        ))
        log_layout.addWidget(self.log)

        self.log.append(f"Папка zapret: {self.zapret_folder}")

        log_frame.setLayout(log_layout)
        main_layout.addWidget(log_frame)

        central.setLayout(main_layout)

    def on_strategy_clicked(self, item):
        self.selected_strategy = item.data(Qt.ItemDataRole.UserRole) or item.text().split(". ", 1)[-1]
        self.status_label.setText(f"⚡ ВЫБРАНО: {self.selected_strategy}")
        self.status_label.setStyleSheet("color: #93c5fd;")

    def toggle_connection(self):
        if not self.is_running:
            if not self.selected_strategy:
                self.log.append("→ Стратегия не выбрана")
                return

            self.is_running = True
            self.start_btn.setText("Запущено")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText(f"ПОДКЛЮЧЕНО: {self.selected_strategy}")
            self.status_label.setStyleSheet("color: #86efac;")
            self.log.append(f"[ЗАПУСК] {self.selected_strategy} — статус изменён")

        else:
            self.is_running = False
            self.start_btn.setText("▶ Запустить")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("⚡ НЕ ПОДКЛЮЧЕНО")
            self.status_label.setStyleSheet("color: #94a3b8;")
            self.log.append("[ОСТАНОВКА] Всё завершено")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(203, 213, 225))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 41, 59))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(17, 24, 39))
    palette.setColor(QPalette.ColorRole.Text, QColor(203, 213, 225))
    palette.setColor(QPalette.ColorRole.Button, QColor(30, 41, 59))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(226, 232, 240))
    app.setPalette(palette)

    folder_dialog = FolderSelectDialog()
    if folder_dialog.exec() == QDialog.DialogCode.Accepted:
        selected_path = folder_dialog.path_edit.text().strip()
        if not selected_path or not os.path.isdir(selected_path):
            QMessageBox.critical(None, "Ошибка", "Укажите правильный путь к папке!")
            sys.exit(1)
        w = ZapretMainWindow(selected_path)
        w.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()