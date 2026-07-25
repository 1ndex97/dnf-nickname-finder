from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QApplication,
    QProgressBar,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.config import ConfigManager
from app.core.exporter import export_csv, export_txt
from app.services.nickname_service import NicknameService
from app.gui.realtime_worker import RealtimeSearchWorker
from app.models.nickname import NicknameCandidate
from app.models.server import SERVERS

LOGGER = logging.getLogger(__name__)

DARK_STYLE = """
QWidget { background: #111827; color: #e5e7eb; font-size: 14px; }
QLineEdit, QComboBox, QSpinBox, QTableWidget { background: #1f2937; border: 1px solid #374151; border-radius: 6px; padding: 6px; }
QPushButton { background: #2563eb; border: 0; border-radius: 8px; padding: 8px 12px; font-weight: 600; }
QPushButton:hover { background: #1d4ed8; }
QPushButton:disabled { background: #4b5563; }
QProgressBar { border: 1px solid #374151; border-radius: 6px; text-align: center; }
QProgressBar::chunk { background: #10b981; border-radius: 6px; }
"""


class MainWindow(QMainWindow):
    def __init__(self, config_manager: ConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.config = config_manager.load()
        self.nickname_service = NicknameService()
        self.candidates: list[NicknameCandidate] = []
        self.checked_results: list[NicknameCandidate] = []
        self.available_results: list[NicknameCandidate] = []
        self.worker: RealtimeSearchWorker | None = None
        self.thread: QThread | None = None
        self.setWindowTitle("DNF Nickname Finder")
        self.resize(980, 680)
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        api_row = QHBoxLayout()
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("Neople API key")
        save_key = QPushButton("Save API Key")
        save_key.clicked.connect(self._save_api_key)
        api_row.addWidget(QLabel("API Key"))
        api_row.addWidget(self.api_key, 1)
        api_row.addWidget(save_key)
        layout.addLayout(api_row)
        controls = QHBoxLayout()
        self.server = QComboBox()
        self.server.addItem("All servers", "all")
        for srv in SERVERS:
            self.server.addItem(srv.name, srv.id)
        self.limit = QSpinBox()
        self.limit.setRange(1, 200)
        self.limit.setValue(100)
        generate = QPushButton("Generate")
        generate.clicked.connect(self.generate)
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_search)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_search)
        self.resume_btn = QPushButton("Resume")
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self.resume_search)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_search)
        for widget in (
            QLabel("Server"),
            self.server,
            QLabel("Results"),
            self.limit,
            generate,
            self.start_btn,
            self.pause_btn,
            self.resume_btn,
            self.stop_btn,
        ):
            controls.addWidget(widget)
        layout.addLayout(controls)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.stats_label = QLabel(
            "Generated: 0 | Checked: 0 | Available: 0 | Errors: 0 | Idle"
        )
        layout.addWidget(self.stats_label)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Nickname", "Server", "Pronunciation", "Rarity", "Score", "Copy"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table, 1)
        exports = QHBoxLayout()
        txt = QPushButton("Export TXT")
        txt.clicked.connect(lambda: self.export("txt"))
        csv = QPushButton("Export CSV")
        csv.clicked.connect(lambda: self.export("csv"))
        exports.addStretch(1)
        exports.addWidget(txt)
        exports.addWidget(csv)
        layout.addLayout(exports)
        self.setCentralWidget(root)

    def _load_settings(self) -> None:
        self.api_key.setText(self.config_manager.get_api_key())
        self.limit.setValue(self.config.result_limit)
        index = self.server.findData(self.config.selected_server)
        self.server.setCurrentIndex(max(index, 0))

    def _save_api_key(self) -> None:
        self.config_manager.set_api_key(self.api_key.text())
        QMessageBox.information(
            self, "Saved", "API key saved to the OS credential store."
        )

    def generate(self) -> None:
        self.candidates = self.nickname_service.top_candidates(self.limit.value())
        self._render(self.candidates)
        self._persist_ui()

    def start_search(self) -> None:
        servers = (
            [s.id for s in SERVERS]
            if self.server.currentData() == "all"
            else [self.server.currentData()]
        )
        self.available_results = []
        self._render(self.available_results)
        self.progress.setRange(0, 0)
        self._set_search_buttons(running=True, paused=False)
        self.thread = QThread(self)
        self.worker = RealtimeSearchWorker(
            self.api_key.text(), self.config.rate_limit_per_second, servers
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.available.connect(self._on_available)
        self.worker.stats.connect(self._on_stats)
        self.worker.status.connect(self._on_status)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self._on_search_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self._persist_ui()

    def pause_search(self) -> None:
        if self.worker:
            self.worker.pause()
            self._set_search_buttons(running=True, paused=True)

    def resume_search(self) -> None:
        if self.worker:
            self.worker.resume()
            self._set_search_buttons(running=True, paused=False)

    def stop_search(self) -> None:
        if self.worker:
            self.worker.stop()

    def _on_available(self, item: NicknameCandidate) -> None:
        self.available_results.append(item)
        self.candidates = self.available_results
        self._append_available_row(item)

    def _on_stats(
        self, generated: int, checked: int, available: int, errors: int
    ) -> None:
        self.stats_label.setText(
            f"Generated: {generated} | Checked: {checked} | Available: {available} | Errors: {errors} | Running"
        )

    def _on_status(self, status: str) -> None:
        text = self.stats_label.text().rsplit(" | ", 1)[0]
        self.stats_label.setText(f"{text} | {status}")

    def _on_search_finished(self) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self._set_search_buttons(running=False, paused=False)

    def _on_failed(self, message: str) -> None:
        LOGGER.exception("Realtime search failed: %s", message)
        QMessageBox.critical(self, "Realtime search failed", message)
        self._set_search_buttons(running=False, paused=False)

    def _render(self, rows: list[NicknameCandidate]) -> None:
        self.table.setRowCount(0)
        for item in rows:
            self._append_available_row(item)

    def _append_available_row(self, item: NicknameCandidate) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            item.nickname,
            item.server or "-",
            f"{item.pronunciation_score:.2f}",
            f"{item.rarity_score:.2f}",
            f"{item.total_score:.2f}",
        ]
        for column, value in enumerate(values):
            cell = QTableWidgetItem(value)
            cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, column, cell)
        copy = QPushButton("Copy")
        copy.clicked.connect(
            lambda _checked=False, nickname=item.nickname: self._copy_nickname(nickname)
        )
        self.table.setCellWidget(row, 5, copy)

    def _copy_nickname(self, nickname: str) -> None:
        QApplication.clipboard().setText(nickname)
        self.statusBar().showMessage(f"Copied {nickname}", 2500)

    def _set_search_buttons(self, running: bool, paused: bool) -> None:
        self.start_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running and not paused)
        self.resume_btn.setEnabled(running and paused)
        self.stop_btn.setEnabled(running)

    def export(self, kind: str) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export {kind.upper()}",
            str(Path.home() / f"dnf_nicknames.{kind}"),
            f"*.{kind}",
        )
        if not path:
            return
        (
            export_csv(Path(path), self.candidates)
            if kind == "csv"
            else export_txt(Path(path), self.candidates)
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        self.stop_search()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3_000)
        super().closeEvent(event)

    def _persist_ui(self) -> None:
        self.config.selected_server = self.server.currentData()
        self.config.result_limit = self.limit.value()
        self.config_manager.save(self.config)
