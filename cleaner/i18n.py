"""
CleanSnap Internationalization (i18n)
Provides complete bilingual support (English & Russian).
"""

TRANSLATIONS = {
    "en": {
        "app_title": "✨ CleanSnap • EXIF & Privacy Stripper",
        "app_subtitle": "Easily remove GPS coordinates, camera serials, and hidden metadata before sharing photos & videos.",
        "badge_offline": "🛡️ 100% Offline • No Quality Loss",
        "lang_switch": "🇷🇺 RU",
        "output_dir": "Output Directory:",
        "browse": "Browse...",
        "open_folder": "Open Folder",
        "chk_overwrite": "Overwrite files if existing in output folder",
        "chk_color": "Preserve ICC Color Profiles (photos)",
        "drop_title": "Drop Your Photos & Videos Here",
        "drop_sub": "...or click the buttons below to browse files or an entire folder",
        "btn_add_files": "📁 Add Files...",
        "btn_add_folder": "📂 Add Folder...",
        "queued": "Queued Media ({count} files)",
        "clear_all": "Clear All",
        "ready": "Ready",
        "btn_clean": "✨ Clean & Protect All Files",
        "btn_cancel": "Cancel",
        "status_processing": "Scrubbing files: {curr}/{total}...",
        "status_done": "🎉 Completed: {success} cleaned, {errors} errors",
        "header_name": "Name",
        "header_fmt": "Format",
        "header_size": "Size",
        "header_gps": "GPS / Coordinates",
        "header_device": "Camera / Device",
        "header_date": "Date / Time",
        "header_status": "Status",
        "header_action": "Action",
        "view_map": "📍 Maps",
        "no_files": "Please add at least one photo or video to clean.",
        "complete_title": "Batch Processing Finished",
        "complete_msg": "Successfully cleaned: {success}\nFailed / Skipped: {errors}\n\nCleaned files saved to:\n{dest}",
    },
    "ru": {
        "app_title": "✨ CleanSnap • Очистка EXIF и Приватных Данных",
        "app_subtitle": "Удаляйте точные GPS-координаты, серийные номера камер и скрытые теги перед отправкой файлов.",
        "badge_offline": "🛡️ 100% Офлайн • Без потери качества",
        "lang_switch": "🇬🇧 EN",
        "output_dir": "Папка для сохранения:",
        "browse": "Обзор...",
        "open_folder": "Открыть папку",
        "chk_overwrite": "Перезаписывать файлы с одинаковыми именами",
        "chk_color": "Сохранять цветовые профили ICC (для фото)",
        "drop_title": "Перетащите фото и видео сюда",
        "drop_sub": "...или используйте кнопки ниже для выбора файлов или папки целиком",
        "btn_add_files": "📁 Выбрать файлы...",
        "btn_add_folder": "📂 Выбрать папку...",
        "queued": "В очереди ({count} файлов)",
        "clear_all": "Очистить список",
        "ready": "Готово к работе",
        "btn_clean": "✨ Очистить и защитить все файлы",
        "btn_cancel": "Отмена",
        "status_processing": "Очистка файлов: {curr}/{total}...",
        "status_done": "🎉 Завершено: {success} очищено, {errors} ошибок",
        "header_name": "Имя файла",
        "header_fmt": "Формат",
        "header_size": "Размер",
        "header_gps": "Геопозиция (GPS)",
        "header_device": "Устройство / Камера",
        "header_date": "Дата съёмки",
        "header_status": "Статус",
        "header_action": "Действие",
        "view_map": "📍 На карте",
        "no_files": "Пожалуйста, добавьте хотя бы одно фото или видео для очистки.",
        "complete_title": "Очистка завершена",
        "complete_msg": "Успешно очищено: {success}\nОшибок / пропущено: {errors}\n\nФайлы сохранены в:\n{dest}",
    }
}

CURRENT_LANG = "en"

def get_text(key: str, **kwargs) -> str:
    """Retrieve localized string."""
    text = TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def set_language(lang: str):
    global CURRENT_LANG
    if lang in TRANSLATIONS:
        CURRENT_LANG = lang
