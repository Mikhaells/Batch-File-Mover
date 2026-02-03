# Batch File Mover

Utility Python yang memproses dan memindahkan file dari folder sumber ke struktur folder tujuan yang terorganisir berdasarkan kode di nama file. Dirancang khusus untuk TVRI KEPRI (Stasiun Televisi Republik Indonesia - Kepulauan Riau).

## 📋 Deskripsi Proyek

**Batch File Mover** adalah aplikasi command-line Python yang:
- Memindai folder sumber untuk menemukan file baru
- Memvalidasi file sebelum diproses (ukuran, stabilitas, readability)
- Mengekstrak kode dari nama file untuk pengelompokan
- Memindahkan file ke struktur folder tujuan yang terorganisir berdasarkan:
  - Kode Bahan Pustaka (Konten Lokal/Nasional)
  - Kode Kegiatan (Jenis Program TV)
  - Tanggal (Tahun/Bulan/Hari)

## 🎯 Fitur Utama

✅ **Pemindahan File Otomatis**
- Memproses file dari folder sumber ke folder tujuan
- Copy & delete verification untuk memastikan integritas data
- Support untuk dry-run mode (tanpa benar-benar mengubah file)

✅ **Validasi File**
- Cek ukuran minimum (default 5 MB)
- Verifikasi stabilitas ukuran file
- Cek readability (file dapat dibaca)
- Cek deletability (file tidak dikunci)

✅ **Parsing Filename Cerdas**
- Format: `BAHANPUSTAKA_KEGIATAN_JUDUL.ext`
- Contoh: `KL_KHI_PeluncuranProgram.mp4` → KONTEN LOKAL / KEPRI HARI INI
- Ekstensif validasi format nama file

✅ **Organisasi Folder Otomatis**
- Struktur: `<dest>/<BAHANPUSTAKA>/<KEGIATAN>/YYYY/MONTH/DD/<filename>`
- Menggunakan tanggal modifikasi file sebagai acuan
- Auto-create folder struktur

✅ **Logging Lengkap**
- File log dengan timestamp
- Encoding UTF-8 untuk karakter Indonesia
- Informasi detail tentang setiap operasi

✅ **Error Handling Robust**
- Graceful handling per file
- Logging error detail
- Lanjut proses meskipun satu file gagal

## 🛠️ Teknologi

- **Bahasa**: Python 3.8+
- **Dependencies**: 
  - `json` - Membaca mapping file
  - `logging` - Logging operasi
  - `shutil` - Copy file
  - `argparse` - Command-line arguments
  - `datetime` - Pemrosesan tanggal
  - `time` - Cek stabilitas file

## 📁 Struktur Proyek

```
BatchFileMover/
├── BatchFileMover.py                  # Script utama
├── run.bat                            # Batch script untuk autorun
├── bahanpustaka_map.json              # Mapping kode bahan pustaka
├── kegiatan_map.json                  # Mapping kode kegiatan
├── batch_file_mover.log               # Log file (auto-generated)
└── README.md                          # Dokumentasi ini
```

## 📊 Mapping Kode

### Bahan Pustaka (bahanpustaka_map.json)

| Kode | Deskripsi |
|------|-----------|
| `KL` | KONTEN LOKAL |
| `KN` | KONTEN NASIONAL |

### Kegiatan (kegiatan_map.json)

| Kode | Deskripsi | Program TV |
|------|-----------|-----------|
| `KHI` | KEPRI HARI INI | Program berita lokal |
| `KM` | KEPRI MENYAPA | Program interaktif |
| `NB` | NGAJI BARENG | Program agama islam |
| `MAI` | MIMBAR AGAMA ISLAM | Ceramah agama islam |
| `MAB` | MIMBAR AGAMA BUDDHA | Ceramah agama buddha |
| `MAH` | MIMBAR AGAMA HINDU | Ceramah agama hindu |
| `MAK` | MIMBAR AGAMA KATOLIK | Ceramah agama katolik |
| `MAP` | MIMBAR AGAMA PROTESTAN | Ceramah agama protestan |
| `AA` | ARENA ANAK | Program anak-anak |
| `KS` | KEPRI SEPEKAN | Program mingguan |
| `RM` | RUMAH MUSIK | Program musik |
| `HPK` | HALO PEMIRSA KEPRI | Program talk show |
| `TP` | TAPPING | Program dokumenter |

## 🚀 Instalasi & Setup

### Prasyarat

- **OS**: Windows (untuk run.bat), atau Linux/macOS (untuk manual execution)
- **Python**: 3.8 atau lebih tinggi
- **Network Share**: Akses ke server network (jika menggunakan network drive)

### Langkah Instalasi

1. **Clone atau download project**
   ```bash
   git clone <repository-url>
   cd BatchFileMover
   ```

2. **Buat virtual environment (opsional tapi disarankan)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # atau manual:
   pip install python-dateutil
   ```

4. **Konfigurasi mapping files**
   - Edit `bahanpustaka_map.json` sesuai kebutuhan
   - Edit `kegiatan_map.json` sesuai kebutuhan

5. **Konfigurasi run.bat (jika menggunakan Windows)**
   - Ubah variabel `SERVER`, `USERNAME`, `PASSWORD`
   - Ubah `DRIVE_LETTER` jika tidak Z:

## 📝 Cara Penggunaan

### Basic Usage

```bash
python BatchFileMover.py
```

Dengan konfigurasi default:
- Source folder: `C:\TestWatch`
- Destination folder: `Z:`
- Minimum file size: 5 MB

### Advanced Usage dengan Arguments

```bash
# Custom source dan destination
python BatchFileMover.py --source "D:\Input" --dest "E:\Output"

# Ubah ukuran minimum
python BatchFileMover.py --min-mb 10

# Dry-run mode (preview tanpa execute)
python BatchFileMover.py --dry-run

# Custom mapping files
python BatchFileMover.py --kegiatan-map custom_kegiatan.json --bahan-map custom_bahan.json

# Kombinasi
python BatchFileMover.py -s "D:\Input" -d "E:\Output" --min-mb 3 --dry-run
```

### Arguments yang Tersedia

| Argument | Short | Default | Deskripsi |
|----------|-------|---------|-----------|
| `--source` | `-s` | `C:\TestWatch` | Folder sumber |
| `--dest` | `-d` | `Z:` | Folder tujuan base |
| `--kegiatan-map` | - | `kegiatan_map.json` | File mapping kegiatan |
| `--bahan-map` | - | `bahanpustaka_map.json` | File mapping bahan pustaka |
| `--min-mb` | - | `5` | Ukuran minimum file dalam MB |
| `--dry-run` | - | `False` | Preview tanpa execute |

### Menggunakan run.bat (Windows)

```batch
run.bat
```

Script ini akan:
1. Membersihkan koneksi drive yang ada
2. Test konektivitas ke server network
3. Mount network drive dengan credentials
4. Menjalankan `BatchFileMover.py`

**Konfigurasi run.bat:**
```batch
set SERVER=192.168.1.100              # IP/hostname server
set DRIVE_LETTER=Z:                   # Drive letter untuk mount
set USERNAME=tvri_user                # Username network
set PASSWORD=password123              # Password network
```

## 📂 Format Struktur Folder Output

```
Z:/
└── KONTEN LOKAL/
    ├── KEPRI HARI INI/
    │   └── 2024/
    │       ├── January/
    │       │   ├── 01/
    │       │   │   ├── KL_KHI_PeluncuranProgram.mp4
    │       │   │   └── KL_KHI_BreakingNews.mp4
    │       │   └── 02/
    │       ├── February/
    │       │   └── ...
    ├── KEPRI MENYAPA/
    │   └── 2024/
    │       └── ...
└── KONTEN NASIONAL/
    ├── NGAJI BARENG/
    │   └── 2024/
    │       └── ...
    └── ...
```

## 🔄 Alur Kerja

```
┌─────────────────────────────┐
│  Mulai Process File         │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Parse Filename             │
│  (BAHANPUSTAKA_KEGIATAN_*)  │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Validasi:                  │
│  - Format nama              │
│  - Kode mapping exist       │
│  - Ukuran minimum           │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Cek Status File:           │
│  - Readable                 │
│  - Deletable                │
│  - Stable size              │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Copy File ke Destination   │
│  (auto-create folders)      │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Verify Copy (size check)   │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Delete Source File         │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Log Success                │
└─────────────────────────────┘
```

## 📋 Contoh Operasi

### Contoh 1: File Valid
```
File: KL_KHI_BreakingNews.mp4 (25 MB, 2024-01-15)
├── Parse: KL, KHI, BreakingNews.mp4
├── Map: KONTEN LOKAL / KEPRI HARI INI
├── Destination: Z:/KONTEN LOKAL/KEPRI HARI INI/2024/January/15/
├── Copy: ✓ Success
├── Verify: ✓ Size match
├── Delete: ✓ Source deleted
└── Result: MOVED ✓
```

### Contoh 2: File Format Invalid
```
File: InvalidName.mp4
├── Parse: ✗ Format tidak valid
├── Reason: Kurang dari 3 bagian (underscore separator)
└── Result: SKIPPED (tidak dipindahkan)
```

### Contoh 3: Kode Tidak Ditemukan
```
File: XX_YY_SomeFile.mp4 (15 MB)
├── Parse: XX, YY, SomeFile.mp4
├── Lookup bahanpustaka: XX ✗ tidak ada
├── Reason: Kode tidak ada di bahanpustaka_map.json
└── Result: SKIPPED
```

### Contoh 4: Ukuran Terlalu Kecil
```
File: KL_KHI_SmallFile.mp4 (2 MB, min 5 MB)
├── Parse: ✓ Valid
├── Validasi: ✓ Semua kode ada
├── Size check: 2 MB < 5 MB ✗
└── Result: SKIPPED
```

## 🔧 Konfigurasi Lanjutan

### Mengubah Mapping Kode

Edit `kegiatan_map.json`:
```json
{
  "KHI": "KEPRI HARI INI",
  "KM": "KEPRI MENYAPA",
  "CUSTOM_CODE": "CUSTOM FOLDER NAME"
}
```

Edit `bahanpustaka_map.json`:
```json
{
  "KL": "KONTEN LOKAL",
  "KN": "KONTEN NASIONAL",
  "KD": "KONTEN DOKUMENTER"
}
```

### Mengubah Source Folder

```python
# Dalam code atau via argument:
python BatchFileMover.py -s "D:\NewSourceFolder" -d "E:\NewDestFolder"
```

### Mengubah Size Minimum

```bash
# 10 MB minimum
python BatchFileMover.py --min-mb 10

# 1 MB minimum (untuk testing)
python BatchFileMover.py --min-mb 1
```

## 📊 Logging & Monitoring

### File Log

Log disimpan di `batch_file_mover.log`:

```
2024-01-15 10:30:45,123 - INFO - Mapping loaded from kegiatan_map.json: 13 entries
2024-01-15 10:30:45,234 - INFO - Mapping loaded from bahanpustaka_map.json: 2 entries
2024-01-15 10:30:46,100 - INFO - Found 5 files in C:\TestWatch. Starting processing...
2024-01-15 10:30:46,200 - INFO - Copying C:\TestWatch\KL_KHI_File.mp4 -> Z:\KONTEN LOKAL\KEPRI HARI INI\2024\January\15\File.mp4
2024-01-15 10:30:47,500 - INFO - Copy verified
2024-01-15 10:30:48,100 - INFO - Moved: KL_KHI_File.mp4 -> Z:\KONTEN LOKAL\KEPRI HARI INI\2024\January\15\File.mp4
2024-01-15 10:30:52,000 - INFO - Finished. Moved: 3, Skipped: 2, Errors: 0
```

### Membaca Log

```bash
# View last 50 lines
tail -50 batch_file_mover.log

# Search untuk errors
grep ERROR batch_file_mover.log

# Real-time monitoring
tail -f batch_file_mover.log
```

## ⚠️ Error Handling & Troubleshooting

### File Tidak Terbaca
```
WARNING: File not readable, skipping
```
**Solusi**: Pastikan file tidak sedang digunakan aplikasi lain. Tunggu beberapa saat.

### File Tidak Bisa Dihapus
```
ERROR: File not deletable, remove destination
```
**Solusi**: File mungkin terkunci. Check apakah digunakan oleh proses lain:
```powershell
Get-Process | Where-Object {$_.Handles -gt 100} | Select-Object Name
```

### Koneksi Network Gagal (run.bat)
```
ERROR: Cannot ping SERVER
```
**Solusi**: 
- Check IP/hostname server
- Test ping manual: `ping SERVER_IP`
- Verifikasi credentials network share

### Mapping File Tidak Ditemukan
```
WARNING: Could not load mapping kegiatan_map.json
```
**Solusi**: Pastikan file JSON ada di folder yang sama dengan script

### Size Mismatch After Copy
```
ERROR: Copy size mismatch, removing destination
```
**Solusi**: 
- Check disk space tujuan
- Verifikasi network connection stabil
- Coba lagi file tersebut

## 🔐 Security Considerations

- **Credentials**: Jangan commit `run.bat` dengan credentials real ke repository. Gunakan environment variables.
- **Log Files**: Log file berisi path dan nama file. Pastikan akses dibatasi jika sensitif.
- **Network Share**: Gunakan VPN atau secure connection jika melalui internet.

### Best Practice

```batch
:: Gunakan environment variables daripada hardcoded
set SERVER=%NETWORK_SERVER%
set USERNAME=%NETWORK_USER%
set PASSWORD=%NETWORK_PASS%

:: Atau gunakan Windows Credential Manager
cmdkey /add:SERVER /user:USERNAME /pass:PASSWORD
net use Z: \\SERVER\Produksi
```

## 📈 Performance Tips

1. **Batch Processing**: Script memproses semua file dalam satu run. Cocok untuk scheduled task.
2. **Minimum Size**: Naikkan `--min-mb` untuk skip file kecil yang tidak perlu
3. **Network Share**: Untuk network share, pastikan bandwidth cukup
4. **Disk Space**: Pastikan destination memiliki space cukup (file di-copy dulu, baru delete)

### Resource Usage
- CPU: Low (single-threaded)
- Memory: ~50-100 MB
- Disk I/O: Tergantung ukuran file

## 🔄 Scheduling (Windows Task Scheduler)

Untuk menjalankan otomatis setiap hari:

1. **Buka Task Scheduler**
2. **Create Basic Task**
3. **Set Trigger**: Daily, 08:00 AM
4. **Set Action**: Start program `C:\Code\AutoFile-Organizer\run.bat`
5. **Set Condition**: Run whether user is logged in or not

```powershell
# Atau via PowerShell:
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
$action = New-ScheduledTaskAction -Execute "C:\Code\AutoFile-Organizer\run.bat"
Register-ScheduledTask -TaskName "BatchFileMover" -Trigger $trigger -Action $action
```

## 📝 Development & Customization

### Menambah Validasi Baru

Edit function `process_file()` di `BatchFileMover.py`:

```python
# Tambah cek custom
if some_condition:
    logger.warning(f"Custom validation failed: {file_name}")
    return False
```

### Mengubah Format Destination

Edit struktur path di `process_file()`:

```python
# Current
final_dest = os.path.join(dest_base, bahanpustaka_folder, kegiatan_folder, year, month, day)

# Custom (misal: tanpa hari)
final_dest = os.path.join(dest_base, bahanpustaka_folder, kegiatan_folder, year, month)
```

### Menambah Prefix ke Filename

```python
# Di bagian copy file
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
new_filename = f"{timestamp}_{new_file_name}"
```

## 🐛 Known Limitations

- Single-threaded: Proses file satu per satu (cocok untuk batch processing)
- Windows-focused: File locking check menggunakan Windows rename trick
- UTF-8 dependencies: Filename dengan karakter spesial bisa bermasalah
- Network path: Slower untuk network shares dengan latency tinggi

## 📞 Support & Issues

### Common Issues

**Q: File tidak terbaca ukurannya?**
A: Gunakan `--min-mb 0` untuk skip size check, atau pastikan file tidak sedang digunakan.

**Q: Folder tujuan tidak ada?**
A: Script auto-create folder. Pastikan memiliki write permission ke destination.

**Q: Log file terus membesar?**
A: Rotate log secara manual atau setup log rotation in Python:
```python
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('batch_file_mover.log', maxBytes=10*1024*1024, backupCount=5)
```

**Q: Dry-run mode tidak delete file?**
A: Itu normal. Dry-run hanya preview, tidak ada aksi nyata.

## 📄 Lisensi

Internal project untuk TVRI KEPRI.

## 👨‍💻 Author & Contributors

Developed for TVRI Kepulauan Riau Digital Library System.

---

**Terakhir diperbarui**: Februari 2026
**Version**: 1.0.0
