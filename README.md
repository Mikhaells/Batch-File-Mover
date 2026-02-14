# Batch File Mover — TVRI KEPRI

Python utility untuk memindahkan file secara batch dari folder sumber ke struktur folder tujuan yang terorganisir berdasarkan kode pada nama file. Dilengkapi dengan fitur keamanan, monitoring performa, dan error handling yang komprehensif.

## Fitur Utama

### Keamanan & Integritas
- **SHA-256 checksum verification** untuk memastikan file tidak corrupt
- **Atomic file operations** dengan temporary files
- **Path traversal protection** dan filename sanitization
- **Race condition prevention** dengan proper file locking detection

### Performa & Monitoring
- **Parallel processing** dengan ThreadPoolExecutor (opsional)
- **Real-time performance metrics** (files/sec, MB/sec, memory usage)
- **Retry mechanisms** dengan exponential backoff
- **Structured logging** dengan detailed error categorization

### Fungsionalitas
- **Batch processing** untuk memindahkan multiple files sekaligus
- **Configurable file size filtering** (default minimum 5 MB)
- **Flexible mapping system** untuk kode BAHANPUSTAKA dan KEGIATAN
- **Organized folder structure**: `<dest>/<BAHANPUSTAKA>/<KEGIATAN>/YYYY/Month/DD/<filename>`

## Teknologi

- **Python 3.8+** (disarankan)
- **psutil** untuk system monitoring
- **Standard library**: os, shutil, json, logging, threading, hashlib, concurrent.futures

## Instalasi

### Prasyarat
- Windows OS (tested) atau Linux/Mac compatible
- Python 3.8 atau lebih tinggi

### Dependencies
```powershell
# Install required package
pip install -r requirements.txt

# Atau install manual
pip install psutil
```

## Struktur Project

```
AutoFile-Organizer/
├─ BatchFileMover.py          # Main script
├─ requirements.txt           # Python dependencies
├─ kegiatan_map.json          # Mapping kode kegiatan -> nama folder
├─ bahanpustaka_map.json      # Mapping kode bahan pustaka -> nama folder
├─ batch_file_mover.log       # Log operasi (UTF-8)
└─ README.md                  # Dokumentasi ini
```

## Konfigurasi

### Mapping Files
**kegiatan_map.json:**
```json
{
  "KHI": "KEPRI HARI INI",
  "KM":  "KEPRI MENYAPA",
  "NB":  "NGAJI BARENG",
  "MAI": "MIMBAR AGAMA ISLAM",
  "MAH": "MIMBAR AGAMA HINDU",
  "MAK": "MIMBAR AGAMA KATOLIK",
  "MAP": "MIMBAR AGAMA PROTESTAN",
  "AA":  "ARENA ANAK",
  "KS":  "KEPRI SEPEKAN",
  "RM":  "RUMAH MUSIK",
  "HPK": "HALO PEMIRSA KEPRI",
  "TP":  "TAPPING"
}
```

**bahanpustaka_map.json:**
```json
{
  "KL": "KONTEN LOKAL",
  "KN": "KONTEN NASIONAL"
}
```

## Cara Penggunaan

### Basic Usage
```powershell
# Sequential processing (default)
python BatchFileMover.py

# Custom source and destination
python BatchFileMover.py --source "C:\MyFiles" --dest "D:\Processed"
```

### Advanced Options
```powershell
# Parallel processing dengan 8 workers
python BatchFileMover.py --parallel --max-workers 8

# Dry run untuk testing
python BatchFileMover.py --dry-run --parallel

# Custom minimum file size
python BatchFileMover.py --min-mb 10

# Custom mapping files
python BatchFileMover.py --kegiatan-map custom_kegiatan.json --bahan-map custom_bahan.json
```

### Command Line Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--source`, `-s` | `C:\TestWatch` | Source folder to scan |
| `--dest`, `-d` | `Z:` | Destination base folder |
| `--kegiatan-map` | `kegiatan_map.json` | Kegiatan mapping file |
| `--bahan-map` | `bahanpustaka_map.json` | Bahan pustaka mapping file |
| `--min-mb` | `5` | Minimum file size in MB |
| `--dry-run` | `False` | Do not actually copy/delete files |
| `--parallel` | `False` | Enable parallel processing |
| `--max-workers` | `4` | Maximum number of parallel workers |

## Format Nama File

File harus mengikuti format: `BAHANPUSTAKA_KEGIATAN_JUDUL.ekstensi`

### Contoh Valid:
- `KL_KHI_PeluncuranProgram.mp4`
- `KN_RM_SenandungRakyat.flv`
- `KL_NB_UstadzKuliah.avi`

### Contoh Invalid:
- `random_file.mp4` (tidak ada kode)
- `KL_KHI` (tidak ada judul/ekstensi)
- `KL_KHI_` (ekstensi kosong)

## Output & Logging

### Console Output
- Real-time progress information
- Performance metrics
- Error notifications

### Log File (`batch_file_mover.log`)
```
2026-02-13 21:48:41,138 - __main__ - INFO - [BatchFileMover.py:90] - Mapping loaded from kegiatan_map.json: 15 entries
2026-02-13 21:48:41,139 - __main__ - INFO - [BatchFileMover.py:456] - Found 0 files in C:\TestWatch. Starting processing...
2026-02-13 21:48:41,139 - __main__ - INFO - [BatchFileMover.py:42] - Performance Metrics:
2026-02-13 21:48:41,140 - __main__ - INFO - [BatchFileMover.py:43] -   - Elapsed time: 0.01s
2026-02-13 21:48:41,140 - __main__ - INFO - [BatchFileMover.py:44] -   - Files processed: 0
2026-02-13 21:48:41,141 - __main__ - INFO - [BatchFileMover.py:49] -   - Memory usage: 22.83 MB
```

## Error Handling

### Retry Mechanism
- **Network/IO errors**: 3 retries dengan exponential backoff (1s, 2s, 4s)
- **Permission errors**: 3 retries dengan 1s delay
- **File integrity errors**: 3 retries dengan 1s delay

### Error Categories
- `FileMoverError`: Base exception untuk semua file mover errors
- `FileIntegrityError`: Checksum verification failed
- `NetworkError`: Network/IO related failures
- `PermissionError`: Permission related issues

## Performance Tips

### Untuk File Banyak:
```powershell
# Gunakan parallel processing
python BatchFileMover.py --parallel --max-workers 8
```

### Untuk Network Drive:
```powershell
# Kurangi workers untuk menghindari network congestion
python BatchFileMover.py --parallel --max-workers 2
```

### Untuk Testing:
```powershell
# Dry run untuk memverifikasi mapping
python BatchFileMover.py --dry-run
```

## Security Features

- **Path traversal protection**: Mencegah `../` attacks
- **Filename sanitization**: Hanya alphanumeric codes yang diperbolehkan
- **Atomic operations**: Temporary files untuk prevent corruption
- **Integrity verification**: SHA-256 checksum validation

## Migration dari Versi Lama

Jika migrasi dari `PCRecord.py`:
1. File mapping (`kegiatan_map.json`, `bahanpustaka_map.json`) tetap compatible
2. Format nama file tetap sama
3. Tambahkan `requirements.txt` dan install `psutil`
4. Update command line arguments

## Troubleshooting

### Common Issues:
1. **"Mapping file not found"**: Pastikan file JSON ada di folder yang sama
2. **"Permission denied"**: Check file/folder permissions
3. **"Network error"**: Verify network connection untuk destination path
4. **"Invalid filename format"**: Pastikan format `BAHANPUSTAKA_KEGIATAN_JUDUL.ext`

### Debug Mode:
```powershell
# Enable debug logging
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" && python BatchFileMover.py --dry-run
```

## License

Project ini dikembangkan untuk kebutuhan internal TVRI KEPRI.

---

**Version**: 2.0  
**Last Updated**: 2026-02-13  
**Developer**: TVRI KEPRI Digital Team