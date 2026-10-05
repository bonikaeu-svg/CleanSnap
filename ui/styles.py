"""
Friendly Modern Dark Theme Stylesheet for CleanSnap / EXIF & Metadata Stripper.
Optimized with large, highly legible typography for Windows desktop screens.
"""

DARK_THEME_QSS = """
/* Global Window Style */
QWidget {
    background-color: #0B1120;
    color: #F8FAFC;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
}

/* Header Card */
QFrame#HeaderCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E293B, stop:1 #0F172A);
    border-radius: 14px;
    border: 1px solid #334155;
    padding: 12px 16px;
}

QLabel#AppTitle {
    font-size: 22px;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.3px;
}

QLabel#AppSubtitle {
    font-size: 14px;
    color: #94A3B8;
}

/* Drop Area (Central Window) */
QFrame#DropArea {
    background-color: #111E36;
    border: 2px dashed #3B82F6;
    border-radius: 16px;
    padding: 24px;
}

QFrame#DropArea:hover {
    background-color: #172554;
    border: 2px dashed #60A5FA;
}

QFrame#DropArea[dragActive="true"] {
    background-color: #1E3A8A;
    border: 2px solid #93C5FD;
}

QLabel#DropIcon {
    font-size: 46px;
}

QLabel#DropTitle {
    font-size: 21px;
    font-weight: 800;
    color: #F1F5F9;
}

QLabel#DropSubtitle {
    font-size: 14px;
    color: #94A3B8;
}

/* Cards & Containers */
QFrame#Card {
    background-color: #131F37;
    border-radius: 12px;
    border: 1px solid #233554;
}

/* Buttons */
QPushButton {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #0F172A;
}

QPushButton:disabled {
    background-color: #0F172A;
    color: #475569;
    border-color: #1E293B;
}

/* Friendly Primary Action Button */
QPushButton#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #10B981);
    border: none;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
    padding: 14px 32px;
    border-radius: 10px;
}

QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1D4ED8, stop:1 #059669);
}

QPushButton#PrimaryButton:pressed {
    background: #1E40AF;
}

QPushButton#PrimaryButton:disabled {
    background: #1E293B;
    color: #64748B;
    border: 1px solid #334155;
}

/* Friendly Secondary Button */
QPushButton#SecondaryButton {
    background-color: #1E293B;
    border: 1px solid #3B82F6;
    color: #93C5FD;
    font-size: 14px;
    font-weight: 600;
    padding: 9px 18px;
}

QPushButton#SecondaryButton:hover {
    background-color: #2563EB;
    color: #FFFFFF;
}

/* Destructive / Cancel Button */
QPushButton#CancelButton {
    background-color: #7F1D1D;
    border: 1px solid #DC2626;
    color: #FEE2E2;
    padding: 11px 22px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 14px;
}

QPushButton#CancelButton:hover {
    background-color: #991B1B;
}

/* Input Fields */
QLineEdit {
    background-color: #0B1120;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #F8FAFC;
    font-size: 14px;
    selection-background-color: #2563EB;
}

QLineEdit:focus {
    border: 1px solid #3B82F6;
}

/* Table View */
QTableWidget {
    background-color: #0E172A;
    border: 1px solid #1E293B;
    border-radius: 10px;
    gridline-color: #1E293B;
    selection-background-color: #1E3A8A;
    selection-color: #FFFFFF;
    font-size: 14px;
}

QHeaderView::section {
    background-color: #0B1120;
    color: #94A3B8;
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid #1E293B;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QTableWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #141F36;
}

QTableWidget::item:selected {
    background-color: #1E3A8A;
}

/* Progress Bar */
QProgressBar {
    background-color: #0B1120;
    border: 1px solid #1E293B;
    border-radius: 7px;
    text-align: center;
    color: #F8FAFC;
    font-weight: 600;
    height: 22px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #10B981);
    border-radius: 6px;
}

/* Checkboxes */
QCheckBox {
    spacing: 10px;
    color: #E2E8F0;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 1px solid #475569;
    background-color: #0B1120;
}

QCheckBox::indicator:checked {
    background-color: #10B981;
    border: 1px solid #34D399;
}

QCheckBox::indicator:hover {
    border-color: #60A5FA;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #0B1120;
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 28px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #0B1120;
    height: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 28px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #475569;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Activity Log Console */
QPlainTextEdit {
    background-color: #070D18;
    color: #94A3B8;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 8px;
}

/* Tooltips */
QToolTip {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}
"""
