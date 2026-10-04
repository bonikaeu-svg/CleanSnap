# 🚀 Google Play Store Publishing Guide for CleanSnap

This guide walks you through building your **`.aab` (Android App Bundle)** and **`.apk`**, and publishing **CleanSnap** to the Google Play Store.

---

## 📱 1. Open the Project in Android Studio

1. Download and open **[Android Studio](https://developer.android.com/studio)** (official Google IDE).
2. Click **Open** and select the folder:
   `c:\Users\Kiton\Documents\antigravity\kind-bardeen\android`
3. Android Studio will automatically download the Android 15 SDK (API 35) and sync Gradle dependencies.

---

## 🔑 2. Generate a Release Signing Key

Google Play requires your App Bundle to be digitally signed with a keystore key.

### Option A: Using Android Studio (Visual)
1. In Android Studio, click **Build > Generate Signed Bundle / APK...**
2. Choose **Android App Bundle** and click **Next**.
3. Under *Key store path*, click **Create new...**
   - Choose a file location (e.g. `cleansnap-release-key.jks`).
   - Enter a secure password.
   - Enter your name or company under *Certificate*.
4. Click **OK**, select **Release**, and click **Create**.

### Option B: Using Command Line (One-Liner)
Run this command in terminal to create a release keystore:
```powershell
keytool -genkey -v -keystore cleansnap-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias cleansnap -storepass your_password -keypass your_password -dname "CN=CleanSnap, OU=Mobile, O=CleanSnap, L=City, S=State, C=US"
```

---

## 📦 3. Build Your APK and AAB Files

* **For Play Store Upload (`.aab`)**:
  In Android Studio:
  - Click **Build > Build Bundle(s) / APK(s) > Build Bundle(s)**.
  - Or run: `./gradlew bundleRelease`
  - Output file: `app/build/outputs/bundle/release/app-release.aab`

* **For Direct Testing on Your Android Phone (`.apk`)**:
  - Click **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
  - Or run: `./gradlew assembleRelease`
  - Output file: `app/build/outputs/apk/release/app-release.apk`
  - Transfer this `.apk` to your phone via USB or WhatsApp/Telegram and tap to install!

---

## 🌐 4. Google Play Console Submission Steps

1. Go to **[Google Play Console](https://play.google.com/console)** and log in with your developer account.
2. Click **Create App**:
   - App Name: `CleanSnap: EXIF Metadata Remover`
   - Default Language: English
   - App or Game: **App**
   - Free or Paid: **Free** (or Paid if you want to sell it)

3. **Store Listing Details**:
   - **Short description (80 chars)**:
     `Remove EXIF data, GPS location, and camera tags from photos & videos offline.`
   - **Full description**:
     ```text
     CleanSnap protects your privacy by stripping hidden EXIF metadata, GPS coordinates, device serial numbers, and camera settings from photos and videos before you share them online.

     ✨ Features:
     • Photos Supported: JPEG, PNG, WebP, HEIC/HEIF
     • Videos Supported: MP4, MOV, MKV, etc.
     • 100% Lossless Video Scrubbing: Fast native stream copy with zero quality loss.
     • Smart Photo Orientation: Never rotates or flips your pictures sideways.
     • Direct Gallery Share: Tap 'Share' on any photo in your Gallery to clean it instantly.
     ```

   - **Russian Localized Listing (Русский перевод для Google Play)**:
     - **Название приложения**: `CleanSnap: Удаление EXIF и GPS`
     - **Краткое описание (до 80 символов)**: `Удаляйте геопозицию GPS, данные камеры и EXIF-метаданные с фото и видео офлайн.`
     - **Полное описание**:
       ```text
       CleanSnap защищает вашу приватность, удаляя скрытые метаданные EXIF, точные координаты GPS, серийные номера устройств и параметры съемки с ваших фотографий и видеороликов перед отправкой в сеть.

       ✨ Возможности:
       • Поддержка фото: JPEG, PNG, WebP, HEIC/HEIF
       • Поддержка видео: MP4, MOV, MKV и др.
       • 100% Без потери качества видео: Быстрое прямое копирование потоков без перекодирования.
       • Умная ориентация фото: Сохраняет правильный поворот кадров.
       • Отправка прямо из Галереи: Нажмите «Поделиться» на фото/видео -> выберите CleanSnap.
       • 100% Офлайн и Приватно: Никаких облаков, учетных записей и трекеров.
       ```

4. **App Content & Data Safety (Crucial for Fast Approval)**:
   - **Privacy Policy URL**: Host the provided [`PRIVACY_POLICY.md`](./PRIVACY_POLICY.md) on GitHub Pages, Google Sites, or Pastebin, and paste the URL.
   - **Data Safety**:
     - *Does your app collect or share user data?* Select **NO**.
     - *All processing happens on-device with zero analytics?* Select **YES**.
   - **Target Audience**: Select **13+** (or 18+).

5. **Upload the App Bundle**:
   - In the left menu, go to **Production** (or **Closed testing**).
   - Click **Create new release**.
   - Upload your `app-release.aab` file.
   - Click **Review and Release** -> **Start rollout to Production**!

Google usually reviews and approves clean utility apps like CleanSnap in **1 to 3 days**!
