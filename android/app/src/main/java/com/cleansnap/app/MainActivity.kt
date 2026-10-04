package com.cleansnap.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.cleansnap.app.cleaner.MediaMetadata
import com.cleansnap.app.cleaner.MetadataExtractor
import com.cleansnap.app.cleaner.PhotoCleaner
import com.cleansnap.app.cleaner.VideoCleaner
import com.cleansnap.app.ui.theme.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

data class MediaItem(
    val uri: Uri,
    val name: String,
    val size: Long,
    val isPhoto: Boolean,
    val metadata: MediaMetadata,
    val status: String = "Ready" // "Ready", "Cleaning", "Cleaned", "Error"
)

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val initialUris = handleIncomingShareIntents(intent)

        setContent {
            CleanSnapTheme {
                MainScreen(initialUris = initialUris)
            }
        }
    }

    private fun handleIncomingShareIntents(intent: Intent): List<Uri> {
        val uris = mutableListOf<Uri>()
        when (intent.action) {
            Intent.ACTION_SEND -> {
                (intent.getParcelableExtra<Uri>(Intent.EXTRA_STREAM))?.let { uris.add(it) }
            }
            Intent.ACTION_SEND_MULTIPLE -> {
                intent.getParcelableArrayListExtra<Uri>(Intent.EXTRA_STREAM)?.let {
                    uris.addAll(it)
                }
            }
        }
        return uris
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(initialUris: List<Uri> = emptyList()) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    var mediaList by remember { mutableStateOf(listOf<MediaItem>()) }
    var isProcessing by remember { mutableStateOf(false) }
    var progress by remember { mutableFloatStateOf(0f) }
    var selectedItemForInspect by remember { mutableStateOf<MediaItem?>(null) }
    var showCompletionDialog by remember { mutableStateOf(false) }

    fun addUris(uris: List<Uri>) {
        scope.launch(Dispatchers.IO) {
            val newItems = uris.mapNotNull { uri ->
                val (name, size, isPhoto) = queryUriDetails(context, uri)
                val meta = if (isPhoto) {
                    MetadataExtractor.extractPhotoMetadata(context, uri)
                } else {
                    MetadataExtractor.extractVideoMetadata(context, uri)
                }
                MediaItem(uri, name, size, isPhoto, meta)
            }
            withContext(Dispatchers.Main) {
                mediaList = mediaList + newItems
            }
        }
    }

    LaunchedEffect(initialUris) {
        if (initialUris.isNotEmpty()) {
            addUris(initialUris)
        }
    }

    val pickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.PickMultipleVisualMedia()
    ) { uris ->
        if (uris.isNotEmpty()) {
            addUris(uris)
        }
    }

    Scaffold(
        containerColor = DarkBackground,
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            "✨ CleanSnap",
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary,
                            fontSize = 20.sp
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(Color(0xFF064E3B))
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text(
                                stringResource(R.string.offline_badge),
                                color = AccentGreen,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = DarkBackground
                ),
                actions = {
                    if (mediaList.isNotEmpty() && !isProcessing) {
                        IconButton(onClick = { mediaList = emptyList() }) {
                            Icon(
                                Icons.Default.DeleteOutline,
                                contentDescription = stringResource(R.string.clear_queue),
                                tint = TextSecondary
                            )
                        }
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp)
        ) {
            // 1. Pick Area Card
            PickAreaCard(
                onPickClicked = {
                    pickerLauncher.launch(
                        PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageAndVideo)
                    )
                }
            )

            Spacer(modifier = Modifier.height(12.dp))

            // 2. Summary stats banner if items present
            if (mediaList.isNotEmpty()) {
                val photos = mediaList.count { it.isPhoto }
                val videos = mediaList.count { !it.isPhoto }
                val gpsLeaks = mediaList.count { it.metadata.gps != null }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(DarkSurfaceCard)
                        .padding(horizontal = 12.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = stringResource(R.string.queued_stats, mediaList.size, photos, videos),
                        fontSize = 12.sp,
                        color = TextSecondary
                    )
                    if (gpsLeaks > 0) {
                        Text(
                            text = stringResource(R.string.gps_alert, gpsLeaks),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = WarningAmber
                        )
                    }
                }
                Spacer(modifier = Modifier.height(10.dp))
            }

            // 3. Media List
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                itemsIndexed(mediaList) { _, item ->
                    MediaCard(
                        item = item,
                        onInspect = { selectedItemForInspect = item }
                    )
                }
            }

            // 4. Progress Bar
            if (isProcessing) {
                Spacer(modifier = Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = { progress },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp)
                        .clip(RoundedCornerShape(4.dp)),
                    color = AccentGreen,
                    trackColor = DarkSurfaceCard
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // 5. Clean Action Button
            Button(
                onClick = {
                    if (mediaList.isEmpty() || isProcessing) return@Button
                    isProcessing = true
                    progress = 0f
                    scope.launch(Dispatchers.IO) {
                        val total = mediaList.size
                        val updatedList = mediaList.toMutableList()

                        for (i in 0 until total) {
                            val it = updatedList[i]
                            updatedList[i] = it.copy(status = "Cleaning...")
                            withContext(Dispatchers.Main) {
                                mediaList = updatedList.toList()
                                progress = (i.toFloat() / total)
                            }

                            val result = if (it.isPhoto) {
                                PhotoCleaner.cleanPhoto(context, it.uri, it.name)
                            } else {
                                VideoCleaner.cleanVideo(context, it.uri, it.name)
                            }

                            val newStatus = if (result.isSuccess) "Cleaned" else "Error"
                            updatedList[i] = it.copy(status = newStatus)
                            withContext(Dispatchers.Main) {
                                mediaList = updatedList.toList()
                                progress = ((i + 1).toFloat() / total)
                            }
                        }

                        withContext(Dispatchers.Main) {
                            isProcessing = false
                            showCompletionDialog = true
                        }
                    }
                },
                enabled = mediaList.isNotEmpty() && !isProcessing,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryBlue,
                    disabledContainerColor = DarkSurfaceCard
                )
            ) {
                Text(
                    if (isProcessing) stringResource(R.string.btn_clean_processing) else stringResource(R.string.btn_clean_idle),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
        }
    }

    // Metadata Inspector Bottom Sheet
    selectedItemForInspect?.let { item ->
        ModalBottomSheet(
            onDismissRequest = { selectedItemForInspect = null },
            containerColor = DarkSurfaceCard
        ) {
            InspectBottomSheetContent(item = item) {
                selectedItemForInspect = null
            }
        }
    }

    // Completion Dialog
    if (showCompletionDialog) {
        val successCount = mediaList.count { it.status == "Cleaned" }
        AlertDialog(
            onDismissRequest = { showCompletionDialog = false },
            title = {
                Text(stringResource(R.string.completion_title), fontWeight = FontWeight.Bold, color = AccentGreen)
            },
            text = {
                Text(
                    stringResource(R.string.completion_body, successCount),
                    color = TextPrimary
                )
            },
            confirmButton = {
                TextButton(onClick = { showCompletionDialog = false }) {
                    Text(stringResource(R.string.btn_done), color = AccentGreen, fontWeight = FontWeight.Bold)
                }
            },
            containerColor = DarkSurface
        )
    }
}

@Composable
fun PickAreaCard(onPickClicked: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onPickClicked() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = DarkSurface)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("✨ 📥 ✨", fontSize = 32.sp)
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                stringResource(R.string.pick_title),
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp,
                color = TextPrimary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                stringResource(R.string.pick_subtitle),
                fontSize = 12.sp,
                color = TextSecondary
            )
            Spacer(modifier = Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                listOf("JPG", "PNG", "HEIC", "MP4", "MOV").forEach { fmt ->
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .background(DarkSurfaceCard)
                            .padding(horizontal = 8.dp, vertical = 3.dp)
                    ) {
                        Text(fmt, fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = TextSecondary)
                    }
                }
            }
        }
    }
}

@Composable
fun MediaCard(item: MediaItem, onInspect: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = DarkSurface)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                if (item.isPhoto) "📸" else "🎬",
                fontSize = 24.sp
            )
            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    item.name,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 14.sp,
                    color = TextPrimary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(2.dp))

                val hasGps = item.metadata.gps != null
                val subtitleColor = if (hasGps) WarningAmber else if (!item.metadata.hasMetadata) AccentGreen else PrimaryBlue
                Text(
                    item.metadata.summary,
                    fontSize = 11.sp,
                    color = subtitleColor,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }

            Spacer(modifier = Modifier.width(8.dp))

            if (item.status == "Cleaned") {
                Text(stringResource(R.string.status_cleaned), color = AccentGreen, fontWeight = FontWeight.Bold, fontSize = 12.sp)
            } else if (item.status == "Error") {
                Text(stringResource(R.string.status_error), color = DangerRed, fontWeight = FontWeight.Bold, fontSize = 12.sp)
            } else {
                OutlinedButton(
                    onClick = onInspect,
                    modifier = Modifier.height(32.dp),
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(stringResource(R.string.btn_inspect), fontSize = 11.sp, color = TextPrimary)
                }
            }
        }
    }
}

@Composable
fun InspectBottomSheetContent(item: MediaItem, onClose: () -> Unit) {
    val context = LocalContext.current
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(20.dp)
    ) {
        Text(stringResource(R.string.dialog_inspect_title), fontWeight = FontWeight.Bold, fontSize = 18.sp, color = TextPrimary)
        Spacer(modifier = Modifier.height(4.dp))
        Text(item.name, fontSize = 13.sp, color = TextSecondary)
        Spacer(modifier = Modifier.height(16.dp))

        // GPS warning card if detected
        item.metadata.gps?.let { gps ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(10.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF78350F))
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(stringResource(R.string.warning_gps), fontWeight = FontWeight.Bold, color = WarningAmber, fontSize = 13.sp)
                    Spacer(modifier = Modifier.height(2.dp))
                    Text("${gps.latitude}° N, ${gps.longitude}° E", color = Color.White, fontSize = 12.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(
                        onClick = {
                            val mapIntent = Intent(Intent.ACTION_VIEW, Uri.parse(gps.mapsUrl))
                            context.startActivity(mapIntent)
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = WarningAmber),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text(stringResource(R.string.btn_view_maps), color = Color.Black, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                    }
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
        }

        // Camera Details
        item.metadata.cameraModel?.let { model ->
            DetailRow(stringResource(R.string.label_device), model)
        }
        item.metadata.dateTime?.let { date ->
            DetailRow(stringResource(R.string.label_datetime), date)
        }

        // Raw Tags
        if (item.metadata.rawTags.isNotEmpty()) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(stringResource(R.string.label_raw_tags, item.metadata.rawTags.size), fontWeight = FontWeight.Bold, fontSize = 12.sp, color = TextPrimary)
            Spacer(modifier = Modifier.height(4.dp))
            item.metadata.rawTags.forEach { (k, v) ->
                DetailRow(k, v)
            }
        } else {
            Text(stringResource(R.string.label_clean), color = AccentGreen, fontSize = 13.sp)
        }

        Spacer(modifier = Modifier.height(20.dp))
    }
}

@Composable
fun DetailRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 3.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = TextSecondary, fontSize = 12.sp)
        Text(value, color = TextPrimary, fontSize = 12.sp, fontWeight = FontWeight.Medium)
    }
}

fun queryUriDetails(context: android.content.Context, uri: Uri): Triple<String, Long, Boolean> {
    var name = "Unknown"
    var size = 0L
    context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
        val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
        val sizeIndex = cursor.getColumnIndex(OpenableColumns.SIZE)
        if (cursor.moveToFirst()) {
            if (nameIndex != -1) name = cursor.getString(nameIndex) ?: "Unknown"
            if (sizeIndex != -1) size = cursor.getLong(sizeIndex)
        }
    }
    val mime = context.contentResolver.getType(uri) ?: ""
    val isPhoto = mime.startsWith("image/") || name.endsWith(".jpg", ignoreCase = true) || name.endsWith(".jpeg", ignoreCase = true) || name.endsWith(".png", ignoreCase = true) || name.endsWith(".webp", ignoreCase = true) || name.endsWith(".heic", ignoreCase = true)
    return Triple(name, size, isPhoto)
}
