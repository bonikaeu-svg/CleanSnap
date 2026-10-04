package com.cleansnap.app.cleaner

import android.content.ContentValues
import android.content.Context
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaMetadataRetriever
import android.media.MediaMuxer
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import java.io.File
import java.io.FileInputStream
import java.nio.ByteBuffer

object VideoCleaner {

    fun cleanVideo(
        context: Context,
        sourceUri: Uri,
        originalName: String
    ): Result<Uri> {
        val tempFile = File.createTempFile("cleaned_vid_", ".mp4", context.cacheDir)
        var extractor: MediaExtractor? = null
        var muxer: MediaMuxer? = null

        return try {
            extractor = MediaExtractor()
            context.contentResolver.openFileDescriptor(sourceUri, "r")?.use { pfd ->
                extractor.setDataSource(pfd.fileDescriptor)
            } ?: return Result.failure(Exception("Cannot open video file descriptor"))

            muxer = MediaMuxer(tempFile.absolutePath, MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4)

            val trackCount = extractor.trackCount
            val trackMap = mutableMapOf<Int, Int>()

            for (i in 0 until trackCount) {
                val format = extractor.getTrackFormat(i)
                val mime = format.getString(android.media.MediaFormat.KEY_MIME) ?: ""
                if (mime.startsWith("video/") || mime.startsWith("audio/")) {
                    val muxerTrackIndex = muxer.addTrack(format)
                    trackMap[i] = muxerTrackIndex
                    extractor.selectTrack(i)
                }
            }

            // Copy video rotation metadata if present so video displays right-side up
            val retriever = MediaMetadataRetriever()
            try {
                retriever.setDataSource(context, sourceUri)
                val rotation = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_ROTATION)
                rotation?.toIntOrNull()?.let { muxer.setOrientationHint(it) }
            } catch (_: Exception) {} finally {
                try { retriever.release() } catch (_: Exception) {}
            }

            muxer.start()

            val bufferSize = 1024 * 1024 // 1 MB buffer
            val buffer = ByteBuffer.allocate(bufferSize)
            val bufferInfo = MediaCodec.BufferInfo()

            while (true) {
                val sampleTrackIndex = extractor.sampleTrackIndex
                if (sampleTrackIndex < 0) break

                val muxerTrack = trackMap[sampleTrackIndex]
                if (muxerTrack != null) {
                    bufferInfo.offset = 0
                    bufferInfo.size = extractor.readSampleData(buffer, 0)
                    if (bufferInfo.size < 0) break

                    bufferInfo.presentationTimeUs = extractor.sampleTime
                    bufferInfo.flags = extractor.sampleFlags
                    muxer.writeSampleData(muxerTrack, buffer, bufferInfo)
                }
                extractor.advance()
            }

            muxer.stop()
            muxer.release()
            muxer = null

            extractor.release()
            extractor = null

            // Save to MediaStore (Movies/Cleaned_Media)
            val cleanName = if (originalName.contains(".")) {
                val dotIndex = originalName.lastIndexOf('.')
                "${originalName.substring(0, dotIndex)}_cleaned.${originalName.substring(dotIndex + 1)}"
            } else {
                "${originalName}_cleaned.mp4"
            }

            val contentValues = ContentValues().apply {
                put(MediaStore.Video.Media.DISPLAY_NAME, cleanName)
                put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    put(MediaStore.Video.Media.RELATIVE_PATH, "${Environment.DIRECTORY_MOVIES}/Cleaned_Media")
                    put(MediaStore.Video.Media.IS_PENDING, 1)
                }
            }

            val targetUri = context.contentResolver.insert(
                MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                contentValues
            ) ?: return Result.failure(Exception("Failed to insert video into MediaStore"))

            context.contentResolver.openOutputStream(targetUri)?.use { out ->
                FileInputStream(tempFile).use { `in` ->
                    `in`.copyTo(out)
                }
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                contentValues.clear()
                contentValues.put(MediaStore.Video.Media.IS_PENDING, 0)
                context.contentResolver.update(targetUri, contentValues, null, null)
            }

            tempFile.delete()
            Result.success(targetUri)
        } catch (e: Exception) {
            tempFile.delete()
            Result.failure(e)
        } finally {
            try { extractor?.release() } catch (_: Exception) {}
            try { muxer?.release() } catch (_: Exception) {}
        }
    }
}
