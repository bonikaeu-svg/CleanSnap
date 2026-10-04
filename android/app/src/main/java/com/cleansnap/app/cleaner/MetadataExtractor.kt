package com.cleansnap.app.cleaner

import android.content.Context
import android.media.MediaMetadataRetriever
import android.net.Uri
import androidx.exifinterface.media.ExifInterface
import java.io.InputStream

data class GpsData(
    val latitude: Double,
    val longitude: Double,
    val mapsUrl: String
)

data class MediaMetadata(
    val hasMetadata: Boolean,
    val summary: String,
    val cameraMake: String? = null,
    val cameraModel: String? = null,
    val dateTime: String? = null,
    val gps: GpsData? = null,
    val rawTags: Map<String, String> = emptyMap()
)

object MetadataExtractor {

    fun extractPhotoMetadata(context: Context, uri: Uri): MediaMetadata {
        return try {
            context.contentResolver.openInputStream(uri)?.use { stream ->
                val exif = ExifInterface(stream)
                val rawTags = mutableMapOf<String, String>()

                val tagsToCheck = listOf(
                    ExifInterface.TAG_MAKE to "Make",
                    ExifInterface.TAG_MODEL to "Model",
                    ExifInterface.TAG_DATETIME to "DateTime",
                    ExifInterface.TAG_DATETIME_ORIGINAL to "DateTimeOriginal",
                    ExifInterface.TAG_SOFTWARE to "Software",
                    ExifInterface.TAG_LENS_MAKE to "LensMake",
                    ExifInterface.TAG_LENS_MODEL to "LensModel",
                    ExifInterface.TAG_IMAGE_WIDTH to "Width",
                    ExifInterface.TAG_IMAGE_LENGTH to "Height",
                    ExifInterface.TAG_ORIENTATION to "Orientation"
                )

                for ((tag, label) in tagsToCheck) {
                    val value = exif.getAttribute(tag)
                    if (!value.isNullOrBlank()) {
                        rawTags[label] = value
                    }
                }

                // Check GPS
                val latLong = FloatArray(2)
                var gpsData: GpsData? = null
                if (exif.getLatLong(latLong)) {
                    val lat = latLong[0].toDouble()
                    val lon = latLong[1].toDouble()
                    gpsData = GpsData(
                        latitude = lat,
                        longitude = lon,
                        mapsUrl = "https://www.google.com/maps?q=$lat,$lon"
                    )
                    rawTags["GPS Latitude"] = String.format("%.5f", lat)
                    rawTags["GPS Longitude"] = String.format("%.5f", lon)
                }

                val make = exif.getAttribute(ExifInterface.TAG_MAKE)
                val model = exif.getAttribute(ExifInterface.TAG_MODEL)
                val date = exif.getAttribute(ExifInterface.TAG_DATETIME_ORIGINAL)
                    ?: exif.getAttribute(ExifInterface.TAG_DATETIME)

                val summaryParts = mutableListOf<String>()
                if (gpsData != null) summaryParts.add("📍 GPS Location")
                if (!model.isNullOrBlank()) summaryParts.add("📷 $model")
                if (!date.isNullOrBlank()) summaryParts.add("📅 $date")

                val summary = if (summaryParts.isNotEmpty()) {
                    summaryParts.joinToString(" • ")
                } else if (rawTags.isNotEmpty()) {
                    "Metadata present (${rawTags.size} tags)"
                } else {
                    "Clean / No EXIF detected"
                }

                MediaMetadata(
                    hasMetadata = rawTags.isNotEmpty() || gpsData != null,
                    summary = summary,
                    cameraMake = make,
                    cameraModel = model,
                    dateTime = date,
                    gps = gpsData,
                    rawTags = rawTags
                )
            } ?: MediaMetadata(false, "Could not open file")
        } catch (e: Exception) {
            MediaMetadata(false, "Inspection error: ${e.message}")
        }
    }

    fun extractVideoMetadata(context: Context, uri: Uri): MediaMetadata {
        val retriever = MediaMetadataRetriever()
        return try {
            retriever.setDataSource(context, uri)
            val rawTags = mutableMapOf<String, String>()

            val keys = listOf(
                MediaMetadataRetriever.METADATA_KEY_TITLE to "Title",
                MediaMetadataRetriever.METADATA_KEY_ARTIST to "Artist",
                MediaMetadataRetriever.METADATA_KEY_DATE to "Date",
                MediaMetadataRetriever.METADATA_KEY_LOCATION to "Location",
                MediaMetadataRetriever.METADATA_KEY_DURATION to "Duration (ms)",
                MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH to "Width",
                MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT to "Height",
                MediaMetadataRetriever.METADATA_KEY_VIDEO_ROTATION to "Rotation"
            )

            for ((key, label) in keys) {
                val value = retriever.extractMetadata(key)
                if (!value.isNullOrBlank()) {
                    rawTags[label] = value
                }
            }

            val loc = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_LOCATION)
            val title = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_TITLE)
            val date = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DATE)

            val summaryParts = mutableListOf<String>()
            if (!loc.isNullOrBlank()) summaryParts.add("📍 Location Tag")
            if (!title.isNullOrBlank()) summaryParts.add("🎥 $title")
            if (!date.isNullOrBlank()) summaryParts.add("📅 $date")

            val summary = if (summaryParts.isNotEmpty()) {
                summaryParts.joinToString(" • ")
            } else {
                "Clean / Minimal tags"
            }

            MediaMetadata(
                hasMetadata = rawTags.isNotEmpty(),
                summary = summary,
                dateTime = date,
                rawTags = rawTags
            )
        } catch (e: Exception) {
            MediaMetadata(false, "Video inspection error: ${e.message}")
        } finally {
            try {
                retriever.release()
            } catch (_: Exception) {}
        }
    }
}
