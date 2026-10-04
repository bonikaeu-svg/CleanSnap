import os
import webbrowser
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt
from cleaner.metadata_extractor import extract_metadata, is_photo


class MetadataDialog(QDialog):
    """Detailed metadata inspection dialog showing privacy-sensitive tags."""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(f"Metadata Inspector — {os.path.basename(file_path)}")
        self.setMinimumSize(680, 520)
        self.resize(750, 560)

        # Extract live metadata
        self.meta = extract_metadata(file_path)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(18, 18, 18, 18)

        # File Overview Card
        header_card = QFrame()
        header_card.setObjectName("HeaderCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(12, 10, 12, 10)
        h_layout.setSpacing(4)

        name_label = QLabel(f"<b>{os.path.basename(file_path)}</b>")
        name_label.setStyleSheet("font-size: 15px; color: #F8FAFC;")
        h_layout.addWidget(name_label)

        size_kb = os.path.getsize(file_path) / 1024.0
        size_str = f"{size_kb / 1024.0:.2f} MB" if size_kb > 1024 else f"{size_kb:.1f} KB"
        type_str = "Photo" if is_photo(file_path) else "Video"

        sub_label = QLabel(f"Type: {type_str} • Size: {size_str} • Path: {file_path}")
        sub_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        sub_label.setWordWrap(True)
        h_layout.addWidget(sub_label)

        layout.addWidget(header_card)

        # Tab Widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #334155; border-radius: 8px; background: #1E293B; }
            QTabBar::tab { background: #0F172A; color: #94A3B8; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background: #1E293B; color: #60A5FA; font-weight: 600; }
        """)

        # Tab 1: Privacy Findings
        tabs.addTab(self._build_privacy_tab(), "🛡️ Privacy Summary")

        # Tab 2: All Raw Tags
        tabs.addTab(self._build_raw_tags_tab(), "📋 All Metadata Tags")

        layout.addWidget(tabs)

        # Bottom Button Row
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        btn_folder = QPushButton("Show in Folder")
        btn_folder.setObjectName("SecondaryButton")
        btn_folder.clicked.connect(self._open_in_folder)
        bottom_row.addWidget(btn_folder)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        bottom_row.addWidget(btn_close)

        layout.addLayout(bottom_row)

    def _build_privacy_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        if not self.meta.get("has_metadata"):
            lbl = QLabel("✅ No sensitive metadata detected in this file.")
            lbl.setStyleSheet("color: #10B981; font-size: 14px; font-weight: 600; padding: 20px;")
            layout.addWidget(lbl)
            layout.addStretch()
            return widget

        # GPS Card
        gps = self.meta.get("gps", {})
        if gps.get("decimal"):
            gps_card = QFrame()
            gps_card.setStyleSheet("background-color: #451A03; border: 1px solid #D97706; border-radius: 8px; padding: 10px;")
            gps_layout = QVBoxLayout(gps_card)
            gps_layout.setSpacing(6)

            title_row = QHBoxLayout()
            gps_title = QLabel("📍 <b>Exact GPS Coordinates Detected!</b>")
            gps_title.setStyleSheet("color: #FDE68A; font-size: 13px;")
            title_row.addWidget(gps_title)
            title_row.addStretch()

            btn_maps = QPushButton("View on Google Maps")
            btn_maps.setStyleSheet("background-color: #D97706; color: #FFFFFF; font-weight: 600; padding: 4px 10px; border-radius: 6px;")
            btn_maps.clicked.connect(lambda: webbrowser.open(gps["maps_url"]))
            title_row.addWidget(btn_maps)

            gps_layout.addLayout(title_row)

            coords_lbl = QLabel(f"Location: {gps.get('display', '')} ({gps['decimal'][0]}, {gps['decimal'][1]})")
            coords_lbl.setStyleSheet("color: #FEF3C7; font-size: 12px;")
            gps_layout.addWidget(coords_lbl)

            layout.addWidget(gps_card)

        # Device & Camera Card
        dev = self.meta.get("device", {})
        cam = self.meta.get("camera", {})
        if dev or cam:
            dev_card = QFrame()
            dev_card.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 10px;")
            dev_layout = QVBoxLayout(dev_card)
            dev_layout.setSpacing(4)

            dev_title = QLabel("📷 <b>Device & Camera Hardware</b>")
            dev_title.setStyleSheet("color: #60A5FA; font-size: 13px;")
            dev_layout.addWidget(dev_title)

            for k, v in {**dev, **cam}.items():
                row_lbl = QLabel(f"• <b>{k}:</b> {v}")
                row_lbl.setStyleSheet("color: #E2E8F0; font-size: 12px;")
                dev_layout.addWidget(row_lbl)

            layout.addWidget(dev_card)

        # Timestamps Card
        dt = self.meta.get("datetime", {})
        if dt:
            dt_card = QFrame()
            dt_card.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 10px;")
            dt_layout = QVBoxLayout(dt_card)
            dt_layout.setSpacing(4)

            dt_title = QLabel("📅 <b>Original Capture Timestamps</b>")
            dt_title.setStyleSheet("color: #60A5FA; font-size: 13px;")
            dt_layout.addWidget(dt_title)

            for k, v in dt.items():
                row_lbl = QLabel(f"• <b>{k}:</b> {v}")
                row_lbl.setStyleSheet("color: #E2E8F0; font-size: 12px;")
                dt_layout.addWidget(row_lbl)

            layout.addWidget(dt_card)

        # Video container tags
        video_tags = self.meta.get("tags", {})
        if video_tags:
            v_card = QFrame()
            v_card.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 10px;")
            v_layout = QVBoxLayout(v_card)
            v_layout.setSpacing(4)

            v_title = QLabel("🎥 <b>Video Container Metadata Tags</b>")
            v_title.setStyleSheet("color: #60A5FA; font-size: 13px;")
            v_layout.addWidget(v_title)

            for k, v in video_tags.items():
                row_lbl = QLabel(f"• <b>{k}:</b> {v}")
                row_lbl.setStyleSheet("color: #E2E8F0; font-size: 12px;")
                v_layout.addWidget(row_lbl)

            layout.addWidget(v_card)

        layout.addStretch()
        return widget

    def _build_raw_tags_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter tags...")
        self.search_input.textChanged.connect(self._filter_raw_tags)
        layout.addWidget(self.search_input)

        # Table
        self.tags_table = QTableWidget()
        self.tags_table.setColumnCount(2)
        self.tags_table.setHorizontalHeaderLabels(["Tag / Property", "Value"])
        self.tags_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tags_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tags_table.verticalHeader().setVisible(False)
        self.tags_table.setAlternatingRowColors(True)

        raw_tags = self.meta.get("raw_tags", {})
        self.tags_table.setRowCount(len(raw_tags))

        for row, (k, v) in enumerate(sorted(raw_tags.items())):
            item_k = QTableWidgetItem(str(k))
            item_v = QTableWidgetItem(str(v))
            self.tags_table.setItem(row, 0, item_k)
            self.tags_table.setItem(row, 1, item_v)

        layout.addWidget(self.tags_table)
        return widget

    def _filter_raw_tags(self, text: str):
        query = text.lower()
        for row in range(self.tags_table.rowCount()):
            k_item = self.tags_table.item(row, 0)
            v_item = self.tags_table.item(row, 1)
            k_text = k_item.text().lower() if k_item else ""
            v_text = v_item.text().lower() if v_item else ""
            match = query in k_text or query in v_text
            self.tags_table.setRowHidden(row, not match)

    def _open_in_folder(self):
        folder = os.path.dirname(os.path.abspath(self.file_path))
        if os.name == "nt":
            os.system(f'explorer /select,"{os.path.abspath(self.file_path)}"')
        else:
            webbrowser.open(folder)
