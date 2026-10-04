package com.cleansnap.app.cleaner

import android.content.ContentValues
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import androidx.exifinterface.media.ExifInterface
import java.io.InputStream
import java.io.OutputStream

object PhotoCleaner {

    fun cleanPhoto(
        context: Context,
        sourceUri: Uri,
        originalName: String
    ): Result<Uri> {
        return try {
            // 1. Read EXIF orientation before stripping
            var orientation = ExifInterface.ORIENTATION_NORMAL
            context.contentResolver.openInputStream(sourceUri)?.use { stream ->
                val exif = ExifInterface(stream)
                orientation = exif.getAttributeInt(
                    ExifInterface.TAG_ORIENTATION,
                    ExifInterface.ORIENTATION_NORMAL
                )
            }

            // 2. Decode bitmap
            val bitmap = context.contentResolver.openInputStream(sourceUri)?.use { stream ->
                BitmapFactory.decodeStream(stream)
            } ?: return Result.failure(Exception("Failed to decode image"))

            // 3. Bake orientation rotation into pixels
            val rotatedBitmap = applyOrientation(bitmap, orientation)

            // Determine extension & compress format
            val isPng = originalName.endsWith(".png", ignoreCase = true)
            val isWebp = originalName.endsWith(".webp", ignoreCase = true)
            val cleanName = if (originalName.contains(".")) {
                val dotIndex = originalName.lastIndexOf('.')
                "${originalName.substring(0, dotIndex)}_cleaned.${originalName.substring(dotIndex + 1)}"
            } else {
                "${originalName}_cleaned.jpg"
            }

            val compressFormat = when {
                isPng -> Bitmap.CompressFormat.PNG
                isWebp -> if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    Bitmap.CompressFormat.WEBP_LOSSY
                } else {
                    @Suppress("DEPRECATION")
                    Bitmap.CompressFormat.WEBP
                }
                else -> Bitmap.CompressFormat.JPEG
            }

            // 4. Save to MediaStore (Pictures/Cleaned_Media)
            val contentValues = ContentValues().apply {
                put(MediaStore.Images.Media.DISPLAY_NAME, cleanName)
                put(MediaStore.Images.Media.MIME_TYPE, if (isPng) "image/png" else if (isWebp) "image/webp" else "image/jpeg")
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    put(MediaStore.Images.Media.RELATIVE_PATH, "${Environment.DIRECTORY_PICTURES}/Cleaned_Media")
                    put(MediaStore.Images.Media.IS_PENDING, 1)
                }
            }

            val targetUri = context.contentResolver.insert(
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                contentValues
            ) ?: return Result.failure(Exception("Failed to create MediaStore entry"))

            context.contentResolver.openOutputStream(targetUri)?.use { out ->
                rotatedBitmap.compress(compressFormat, 95, out)
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                contentValues.clear()
                contentValues.put(MediaStore.Images.Media.IS_PENDING, 0)
                context.contentResolver.update(targetUri, contentValues, null, null)
            }

            if (rotatedBitmap != bitmap) {
                rotatedBitmap.recycle()
            }
            bitmap.recycle()

            Result.success(targetUri)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun applyOrientation(bitmap: Bitmap, orientation: Int): Bitmap {
        val matrix = Matrix()
        when (orientation) {
            ExifInterface.ORIENTATION_ROTATE_90 -> matrix.postRotate(90f)
            ExifInterface.ORIENTATION_ROTATE_180 -> matrix.postRotate(180f)
            ExifInterface.ORIENTATION_ROTATE_270 -> matrix.postRotate(270f)
            ExifInterface.ORIENTATION_FLIP_HORIZONTAL -> matrix.postScale(-1f, 1f)
            ExifInterface.ORIENTATION_FLIP_VERTICAL -> matrix.postScale(1f, -1f)
            else -> return bitmap
        }
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }
}
