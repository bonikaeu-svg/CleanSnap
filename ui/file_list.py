import os
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QWidget, QHBoxLayout, QLabel, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from cleaner.metadata_extractor import is_photo, extract_metadata
from cleaner.i18n import get_text
from ui.metadata_dialog import MetadataDialog


class FileTableWidget(QTableWidget):
    """Table widget showing queued files, detected metadata tags, and cleaning status."""

    files_removed = pyqtSignal()
    inspect_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_items: List[Dict[str, Any]] = []

        self.update_headers()

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.setColumnWidth(1, 240)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(38)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.cellDoubleClicked.connect(self._on_double_click)

    def update_headers(self):
        headers = [
            get_text("header_fmt"),
            get_text("header_name"),
            get_text("header_size"),
            get_text("header_gps"),
            get_text("header_status"),
            get_text("header_action")
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def add_files(self, paths: List[str]):
        existing_paths = {item["path"] for item in self.file_items}
        new_items = []

        for p in paths:
            if p not in existing_paths and os.path.exists(p):
                size_b = os.path.getsize(p)
                meta = extract_metadata(p)
                item = {
                    "path": p,
                    "name": os.path.basename(p),
                    "size": size_b,
                    "is_photo": is_photo(p),
                    "meta": meta,
                    "status": "Pending",
                    "result": None
                }
                new_items.append(item)
                existing_paths.add(p)

        if not new_items:
            return

        start_row = len(self.file_items)
        self.file_items.extend(new_items)
        self.setRowCount(len(self.file_items))

        for idx, item in enumerate(new_items, start=start_row):
            self._render_row(idx, item)

    def _render_row(self, row: int, item: Dict[str, Any]):
        # Column 0: Type
        type_str = "📸 Photo" if item["is_photo"] else "🎬 Video"
        type_item = QTableWidgetItem(type_str)
        type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 0, type_item)

        # Column 1: File Name
        name_item = QTableWidgetItem(item["name"])
        name_item.setToolTip(item["path"])
        self.setItem(row, 1, name_item)

        # Column 2: Size
        sz_kb = item["size"] / 1024.0
        sz_str = f"{sz_kb / 1024.0:.2f} MB" if sz_kb > 1024 else f"{sz_kb:.1f} KB"
        size_item = QTableWidgetItem(sz_str)
        size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 2, size_item)

        # Column 3: Detected Metadata
        meta_str = item["meta"].get("summary", "None")
        meta_item = QTableWidgetItem(meta_str)
        if "GPS" in meta_str or "📍" in meta_str:
            meta_item.setForeground(QBrush(QColor("#F59E0B")))  # Warm amber for GPS warning
        elif not item["meta"].get("has_metadata"):
            meta_item.setForeground(QBrush(QColor("#10B981")))  # Emerald for clean
        else:
            meta_item.setForeground(QBrush(QColor("#60A5FA")))  # Sky blue for camera info
        self.setItem(row, 3, meta_item)

        # Column 4: Status
        status_item = QTableWidgetItem(item["status"])
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 4, status_item)

        # Column 5: Action Button
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(4, 2, 4, 2)
        action_layout.setSpacing(4)

        btn_inspect = QPushButton("🔍 Inspect")
        btn_inspect.setStyleSheet("padding: 4px 10px; font-size: 11px; font-weight: 600;")
        btn_inspect.setCursor(Qt.CursorShape.PointingHandCursor)
        file_path = item["path"]
        btn_inspect.clicked.connect(lambda checked, p=file_path: self._inspect_file(p))
        action_layout.addWidget(btn_inspect)

        self.setCellWidget(row, 5, action_widget)

    def set_row_status(self, row: int, status: str, color_hex: Optional[str] = None):
        if 0 <= row < len(self.file_items):
            self.file_items[row]["status"] = status
            status_item = self.item(row, 4)
            if status_item:
                status_item.setText(status)
                if color_hex:
                    status_item.setForeground(QBrush(QColor(color_hex)))

    def update_file_result(self, row: int, result: Dict[str, Any]):
        if 0 <= row < len(self.file_items):
            self.file_items[row]["result"] = result
            if result.get("success"):
                self.set_row_status(row, "🎉 Cleaned", "#10B981")
                # Update metadata col to "Cleaned"
                meta_item = self.item(row, 3)
                if meta_item:
                    meta_item.setText("✓ Metadata Scrubbed")
                    meta_item.setForeground(QBrush(QColor("#10B981")))
            else:
                self.set_row_status(row, "❌ Error", "#EF4444")

    def _inspect_file(self, path: str):
        dlg = MetadataDialog(path, self)
        dlg.exec()

    def _on_double_click(self, row: int, col: int):
        if 0 <= row < len(self.file_items):
            self._inspect_file(self.file_items[row]["path"])

    def _show_context_menu(self, pos):
        selected_rows = sorted(set(idx.row() for idx in self.selectedIndexes()), reverse=True)
        if not selected_rows:
            return

        menu = QMenu(self)
        menu.setStyleSheet("background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155;")

        if len(selected_rows) == 1:
            act_inspect = menu.addAction("🔍 Inspect Metadata")
            act_inspect.triggered.connect(lambda: self._inspect_file(self.file_items[selected_rows[0]]["path"]))

        act_remove = menu.addAction("🗑️ Remove from List")
        act_remove.triggered.connect(lambda: self.remove_rows(selected_rows))

        menu.exec(self.viewport().mapToGlobal(pos))

    def remove_rows(self, rows: List[int]):
        for r in sorted(rows, reverse=True):
            if 0 <= r < len(self.file_items):
                del self.file_items[r]
                self.removeRow(r)
        self.files_removed.emit()

    def clear_all(self):
        self.file_items.clear()
        self.setRowCount(0)
        self.files_removed.emit()
