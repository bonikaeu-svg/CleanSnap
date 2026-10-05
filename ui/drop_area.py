import os
from typing import List
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragLeaveEvent

from cleaner.metadata_extractor import is_supported
from cleaner.i18n import get_text


def scan_paths(paths: List[str]) -> List[str]:
    """Recursively discover all supported photos and videos from given paths."""
    found_files = []
    seen = set()

    for p in paths:
        if os.path.isfile(p):
            if is_supported(p) and p not in seen:
                seen.add(p)
                found_files.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    full_p = os.path.join(root, f)
                    if is_supported(full_p) and full_p not in seen:
                        seen.add(full_p)
                        found_files.append(full_p)
    return found_files


class DropArea(QFrame):
    """Interactive drag & drop landing area with file and folder pickers."""

    files_added = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropArea")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        self.icon_label = QLabel("✨ 📥 ✨")
        self.icon_label.setObjectName("DropIcon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Title
        self.title_label = QLabel(get_text("drop_title"))
        self.title_label.setObjectName("DropTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel(get_text("drop_sub"))
        self.subtitle_label.setObjectName("DropSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle_label)

        # Format pills
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(6)
        pills_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        formats = ["JPG", "PNG", "HEIC / iPhone", "WebP", "MP4", "MOV", "MKV"]
        for fmt in formats:
            pill = QLabel(fmt)
            pill.setStyleSheet(
                "background-color: #1E293B; color: #CBD5E1; border: 1px solid #334155; "
                "border-radius: 6px; padding: 4px 10px; font-size: 13px; font-weight: 700;"
            )
            pills_layout.addWidget(pill)
        layout.addLayout(pills_layout)

        # Action Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_add_files = QPushButton(get_text("btn_add_files"))
        self.btn_add_files.setObjectName("SecondaryButton")
        self.btn_add_files.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_files.clicked.connect(self.browse_files)
        btn_row.addWidget(self.btn_add_files)

        self.btn_add_folder = QPushButton(get_text("btn_add_folder"))
        self.btn_add_folder.setObjectName("SecondaryButton")
        self.btn_add_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_folder.clicked.connect(self.browse_folder)
        btn_row.addWidget(self.btn_add_folder)

        layout.addLayout(btn_row)

    def update_texts(self):
        self.title_label.setText(get_text("drop_title"))
        self.subtitle_label.setText(get_text("drop_sub"))
        self.btn_add_files.setText(get_text("btn_add_files"))
        self.btn_add_folder.setText(get_text("btn_add_folder"))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

        urls = event.mimeData().urls()
        raw_paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        valid_files = scan_paths(raw_paths)

        if valid_files:
            self.files_added.emit(valid_files)
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        # Clicking anywhere in the drop area opens the file browser
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked directly on frame rather than button
            child = self.childAt(event.pos())
            if child in (self, self.icon_label, self.title_label, self.subtitle_label):
                self.browse_files()

    def browse_files(self):
        file_filter = (
            "Media Files (*.jpg *.jpeg *.png *.webp *.tiff *.tif *.heic *.heif *.mp4 *.mov *.mkv *.avi *.webm *.flv *.wmv);;"
            "Photos (*.jpg *.jpeg *.png *.webp *.tiff *.tif *.heic *.heif *.bmp *.gif);;"
            "Videos (*.mp4 *.mov *.mkv *.avi *.webm *.flv *.wmv *.3gp);;"
            "All Files (*.*)"
        )
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Photos or Videos to Clean",
            "",
            file_filter
        )
        if paths:
            valid_files = scan_paths(paths)
            if valid_files:
                self.files_added.emit(valid_files)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Photos / Videos"
        )
        if folder:
            valid_files = scan_paths([folder])
            if valid_files:
                self.files_added.emit(valid_files)
