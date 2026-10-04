import os
import sys
import subprocess
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QProgressBar, QCheckBox,
    QMessageBox, QFrame, QPlainTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QStandardPaths
from PyQt6.QtGui import QIcon

from ui.styles import DARK_THEME_QSS
from ui.drop_area import DropArea
from ui.file_list import FileTableWidget
from cleaner.processor import BatchCleanWorker
from cleaner.i18n import get_text, set_language, CURRENT_LANG


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


class MainWindow(QMainWindow):
    """Main window of the EXIF & Metadata Stripper application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CleanSnap — EXIF & Privacy Metadata Stripper")
        self.resize(1050, 740)
        self.setMinimumSize(880, 620)

        # Set application icon
        icon_path = get_resource_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Apply dark theme
        self.setStyleSheet(DARK_THEME_QSS)

        self.worker: BatchCleanWorker = None

        # Main Widget
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        # 1. Header Card
        root_layout.addWidget(self._build_header())

        # 2. Output Directory Card
        root_layout.addWidget(self._build_output_card())

        # 3. Drop Area
        self.drop_area = DropArea()
        self.drop_area.files_added.connect(self._on_files_added)
        root_layout.addWidget(self.drop_area)

        # 4. File Table Section
        table_container = QFrame()
        table_container.setObjectName("Card")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(10, 10, 10, 10)
        table_layout.setSpacing(8)

        # Table Top Controls
        table_header_row = QHBoxLayout()
        self.lbl_queue_count = QLabel(get_text("queued", count=0))
        self.lbl_queue_count.setStyleSheet("font-weight: 600; font-size: 14px; color: #F1F5F9;")
        table_header_row.addWidget(self.lbl_queue_count)
        table_header_row.addStretch()

        self.btn_clear = QPushButton(get_text("clear_all"))
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.clicked.connect(self._clear_files)
        table_header_row.addWidget(self.btn_clear)

        table_layout.addLayout(table_header_row)

        # Table Widget
        self.file_table = FileTableWidget()
        self.file_table.files_removed.connect(self._update_queue_label)
        table_layout.addWidget(self.file_table)

        # 5. Log & Activity Console
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumHeight(110)
        self.log_edit.setPlaceholderText("Live activity log will appear here...")
        table_layout.addWidget(self.log_edit)

        root_layout.addWidget(table_container)

        # 6. Bottom Controls Bar
        root_layout.addWidget(self._build_bottom_controls())

        self._update_queue_label()

    def _build_header(self) -> QFrame:
        card = QFrame()
        card.setObjectName("HeaderCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)

        vbox = QVBoxLayout()
        vbox.setSpacing(3)

        self.title_label = QLabel(get_text("app_title"))
        self.title_label.setObjectName("AppTitle")
        vbox.addWidget(self.title_label)

        self.subtitle_label = QLabel(get_text("app_subtitle"))
        self.subtitle_label.setObjectName("AppSubtitle")
        vbox.addWidget(self.subtitle_label)

        layout.addLayout(vbox)
        layout.addStretch()

        # Language switch button
        self.btn_lang = QPushButton(get_text("lang_switch"))
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.setStyleSheet(
            "background-color: #1E293B; color: #38BDF8; border: 1px solid #334155; "
            "border-radius: 8px; padding: 6px 12px; font-weight: 700; font-size: 12px;"
        )
        self.btn_lang.clicked.connect(self._toggle_language)
        layout.addWidget(self.btn_lang)

        self.badge_offline = QLabel(get_text("badge_offline"))
        self.badge_offline.setStyleSheet(
            "background-color: #064E3B; color: #34D399; border: 1px solid #059669; "
            "border-radius: 8px; padding: 6px 14px; font-weight: 700; font-size: 12px;"
        )
        layout.addWidget(self.badge_offline)

        return card

    def _toggle_language(self):
        new_lang = "ru" if CURRENT_LANG == "en" else "en"
        set_language(new_lang)
        self._update_all_texts()

    def _update_all_texts(self):
        self.title_label.setText(get_text("app_title"))
        self.subtitle_label.setText(get_text("app_subtitle"))
        self.btn_lang.setText(get_text("lang_switch"))
        self.badge_offline.setText(get_text("badge_offline"))
        self.lbl_output_title.setText(get_text("output_dir"))
        self.btn_browse_out.setText(get_text("browse"))
        self.btn_open_out.setText(get_text("open_folder"))
        self.chk_overwrite.setText(get_text("chk_overwrite"))
        self.chk_color_profile.setText(get_text("chk_color"))
        self.btn_clear.setText(get_text("clear_all"))
        self.btn_clean.setText(get_text("btn_clean"))
        self.btn_cancel.setText(get_text("btn_cancel"))
        self.lbl_status.setText(get_text("ready"))
        self._update_queue_label()
        self.drop_area.update_texts()
        self.file_table.update_headers()

    def _build_output_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        # Row 1: Destination Folder
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.lbl_output_title = QLabel(get_text("output_dir"))
        self.lbl_output_title.setStyleSheet("font-weight: 600; color: #E2E8F0; min-width: 120px;")
        row1.addWidget(self.lbl_output_title)

        pic_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
        if not pic_dir or not os.path.exists(pic_dir):
            pic_dir = os.path.expanduser("~")
        default_output = os.path.join(pic_dir, "Cleaned_Media")

        self.edit_output_dir = QLineEdit(default_output)
        row1.addWidget(self.edit_output_dir)

        self.btn_browse_out = QPushButton(get_text("browse"))
        self.btn_browse_out.clicked.connect(self._browse_output_dir)
        row1.addWidget(self.btn_browse_out)

        self.btn_open_out = QPushButton(get_text("open_folder"))
        self.btn_open_out.setObjectName("SecondaryButton")
        self.btn_open_out.clicked.connect(self._open_output_dir)
        row1.addWidget(self.btn_open_out)

        layout.addLayout(row1)

        # Row 2: Options
        row2 = QHBoxLayout()
        row2.setSpacing(18)

        self.chk_overwrite = QCheckBox(get_text("chk_overwrite"))
        self.chk_overwrite.setToolTip("If unchecked, unique names like photo_clean.jpg will be created safely.")
        row2.addWidget(self.chk_overwrite)

        self.chk_color_profile = QCheckBox(get_text("chk_color"))
        self.chk_color_profile.setToolTip("Keeps display color calibrations (Display-P3, AdobeRGB) while stripping all EXIF/GPS.")
        row2.addWidget(self.chk_color_profile)

        row2.addStretch()
        layout.addLayout(row2)

        return card

    def _build_bottom_controls(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Progress bar + status
        status_row = QHBoxLayout()
        self.lbl_status = QLabel(get_text("ready"))
        self.lbl_status.setStyleSheet("color: #94A3B8; font-weight: 500;")
        status_row.addWidget(self.lbl_status)
        status_row.addStretch()

        self.lbl_progress_num = QLabel("")
        self.lbl_progress_num.setStyleSheet("color: #60A5FA; font-weight: 600;")
        status_row.addWidget(self.lbl_progress_num)

        layout.addLayout(status_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Action Buttons Row
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton(get_text("btn_cancel"))
        self.btn_cancel.setObjectName("CancelButton")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._cancel_batch)
        btn_row.addWidget(self.btn_cancel)

        self.btn_clean = QPushButton(get_text("btn_clean"))
        self.btn_clean.setObjectName("PrimaryButton")
        self.btn_clean.clicked.connect(self._start_batch_clean)
        btn_row.addWidget(self.btn_clean)

        layout.addLayout(btn_row)
        return widget

    def _on_files_added(self, paths: List[str]):
        self.file_table.add_files(paths)
        self._update_queue_label()
        self.log_edit.appendPlainText(f"Added {len(paths)} file(s) to queue.")

    def _clear_files(self):
        self.file_table.clear_all()
        self._update_queue_label()
        self.log_edit.appendPlainText("Queue cleared.")
        self.progress_bar.setValue(0)
        self.lbl_progress_num.setText("")
        self.lbl_status.setText(get_text("ready"))

    def _update_queue_label(self):
        count = len(self.file_table.file_items)
        self.lbl_queue_count.setText(get_text("queued", count=count))
        self.btn_clean.setEnabled(count > 0 and (self.worker is None or not self.worker.isRunning()))

    def _browse_output_dir(self):
        initial = self.edit_output_dir.text()
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory", initial)
        if folder:
            self.edit_output_dir.setText(folder)

    def _open_output_dir(self):
        out_dir = self.edit_output_dir.text().strip()
        if not out_dir:
            return
        os.makedirs(out_dir, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(out_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", out_dir])
        else:
            subprocess.Popen(["xdg-open", out_dir])

    def _start_batch_clean(self):
        if not self.file_table.file_items:
            QMessageBox.warning(self, "No Files", get_text("no_files"))
            return

        out_dir = self.edit_output_dir.text().strip()
        if not out_dir:
            self._browse_output_dir()
            out_dir = self.edit_output_dir.text().strip()
            if not out_dir:
                return

        # UI state
        self.btn_clean.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.btn_cancel.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Starting...")

        # Reset statuses
        for i in range(len(self.file_table.file_items)):
            self.file_table.set_row_status(i, "Pending")

        # Start Worker
        self.worker = BatchCleanWorker(
            file_items=self.file_table.file_items,
            output_dir=out_dir,
            overwrite=self.chk_overwrite.isChecked(),
            keep_color_profile=self.chk_color_profile.isChecked(),
            parent=self
        )
        self.worker.file_started.connect(self._on_worker_file_started)
        self.worker.file_finished.connect(self._on_worker_file_finished)
        self.worker.overall_progress.connect(self._on_worker_progress)
        self.worker.batch_finished.connect(self._on_worker_batch_finished)
        self.worker.log_emitted.connect(self._append_log)
        self.worker.start()

    def _cancel_batch(self):
        if self.worker and self.worker.isRunning():
            self.lbl_status.setText("Cancelling...")
            self.worker.cancel()

    def _on_worker_file_started(self, idx: int, path: str):
        self.file_table.set_row_status(idx, "Cleaning...", "#60A5FA")
        self.lbl_status.setText(f"Cleaning: {os.path.basename(path)}")

    def _on_worker_file_finished(self, idx: int, result: Dict[str, Any]):
        self.file_table.update_file_result(idx, result)

    def _on_worker_progress(self, current: int, total: int):
        pct = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)
        self.lbl_progress_num.setText(f"{current} / {total} ({pct}%)")

    def _on_worker_batch_finished(self, summary: Dict[str, Any]):
        self.btn_cancel.setVisible(False)
        self.btn_clean.setEnabled(True)
        self.btn_clear.setEnabled(True)

        if summary.get("cancelled"):
            self.lbl_status.setText("Batch processing cancelled.")
        else:
            self.lbl_status.setText(
                get_text("status_done", success=summary["success"], errors=summary["errors"])
            )

        # Summary Dialog
        orig_mb = summary["total_orig_bytes"] / (1024 * 1024)
        clean_mb = summary["total_cleaned_bytes"] / (1024 * 1024)

        if CURRENT_LANG == "ru":
            msg = (
                f"<h3 style='color: #10B981; margin: 0;'>🎉 Очистка завершена!</h3><br>"
                f"Все метаданные успешно удалены. Файлы готовы к безопасной отправке.<br><br>"
                f"• <b>Обработано файлов:</b> {summary['success']} из {summary['total']}<br>"
                f"• <b>Ошибок / пропусков:</b> {summary['errors']}<br>"
                f"• <b>Сохранено в:</b> <span style='color: #60A5FA;'>{summary['output_dir']}</span><br>"
                f"• <b>Размер файлов:</b> {clean_mb:.2f} MB (было {orig_mb:.2f} MB)<br><br>"
                f"<i>Все GPS-координаты, серийные номера и даты удалены навсегда.</i>"
            )
            title = "CleanSnap — Успешно завершено"
        else:
            msg = (
                f"<h3 style='color: #10B981; margin: 0;'>🎉 Cleaning Complete!</h3><br>"
                f"Your media is now stripped clean and safe to share online.<br><br>"
                f"• <b>Files Protected:</b> {summary['success']} of {summary['total']}<br>"
                f"• <b>Issues / Errors:</b> {summary['errors']}<br>"
                f"• <b>Saved to:</b> <span style='color: #60A5FA;'>{summary['output_dir']}</span><br>"
                f"• <b>Total Media Size:</b> {clean_mb:.2f} MB (was {orig_mb:.2f} MB)<br><br>"
                f"<i>All GPS coordinates, camera serials, timestamps, and personal tags have been permanently scrubbed.</i>"
            )
            title = "CleanSnap — Completed Successfully"

        reply = QMessageBox.information(
            self,
            title,
            msg,
            QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )
        if reply == QMessageBox.StandardButton.Open:
            self._open_output_dir()

    def _append_log(self, text: str, level: str = "info"):
        self.log_edit.appendPlainText(text)
        sb = self.log_edit.verticalScrollBar()
        sb.setValue(sb.maximum())
