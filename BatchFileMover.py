import os
import shutil
import json
import logging
import argparse
from datetime import datetime
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_file_mover.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_mapping(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            logger.info(f"Mapping loaded from {path}: {len(mapping)} entries")
            return mapping
    except Exception as e:
        logger.warning(f"Could not load mapping {path}: {e}")
        return {}
 
def is_file_deletable(file_path):
    try:
        temp_name = file_path + '.delete_test'
        os.rename(file_path, temp_name)
        os.rename(temp_name, file_path)
        return True
    except Exception:
        return False


def is_file_readable(file_path):
    try:
        with open(file_path, 'rb') as f:
            f.read(1024)
        return True
    except Exception:
        return False


def is_file_stable(file_path, check_interval=2):
    try:
        size1 = os.path.getsize(file_path)
        time.sleep(check_interval)
        size2 = os.path.getsize(file_path)
        change_percent = abs(size2 - size1) / max(size1, 1) * 100
        return change_percent < 1.0
    except Exception:
        return False


def safe_copy_file(src_path, dst_path, dry_run=False):
    try:
        logger.info(f"Copying {src_path} -> {dst_path}")
        if dry_run:
            return True
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        if os.path.exists(dst_path):
            if os.path.getsize(src_path) == os.path.getsize(dst_path):
                logger.info("Copy verified")
                return True
            else:
                logger.error("Copy size mismatch, removing destination")
                os.remove(dst_path)
                return False
        return False
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        return False


def safe_delete_file(path, dry_run=False):
    try:
        if dry_run:
            logger.info(f"(Dry-run) Would delete: {path}")
            return True
        if not os.path.exists(path):
            return True
        if is_file_deletable(path):
            os.remove(path)
            return True
        else:
            logger.error(f"File not deletable: {path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False


def parse_filename(file_name):
    parts = file_name.split('_')
    if len(parts) < 3:
        return None
    if '.' not in parts[-1]:
        return None
    bahanpustaka_code = parts[0].upper()
    kegiatan_code = parts[1].upper()
    new_file_name = '_'.join(parts[2:])
    return bahanpustaka_code, kegiatan_code, new_file_name


def process_file(file_path, dest_base, bahanpustaka_map, kegiatan_map, min_size_bytes, dry_run=False):
    file_name = os.path.basename(file_path)

    # Ignore temp files and directories
    if file_name.lower().endswith('.tmp') or os.path.isdir(file_path):
        logger.info(f"Ignoring temporary or directory: {file_name}")
        return False

    parts = parse_filename(file_name)
    if parts is None:
        logger.warning(f"Invalid filename format, skipping: {file_name}")
        # Do not move invalid files; just skip processing
        return False

    bahanpustaka_code, kegiatan_code, new_file_name = parts

    # Skip files whose codes are not present in the mapping JSONs
    if bahanpustaka_code not in bahanpustaka_map:
        logger.warning(f"Skipping {file_name}: bahan pustaka code '{bahanpustaka_code}' not found in mapping")
        return False
    if kegiatan_code not in kegiatan_map:
        logger.warning(f"Skipping {file_name}: kegiatan code '{kegiatan_code}' not found in mapping")
        return False

    # Size check
    try:
        size = os.path.getsize(file_path)
        if size < min_size_bytes:
            logger.info(f"Skipping small file {file_name} ({size} bytes)")
            return False
    except Exception as e:
        logger.error(f"Could not get size for {file_name}: {e}")
        return False

    # Readability/stability checks
    if not is_file_readable(file_path) or not is_file_deletable(file_path) or not is_file_stable(file_path):
        logger.warning(f"File not ready yet, skipping: {file_name}")
        return False

    # Destination folder based on modification time
    try:
        mtime = os.path.getmtime(file_path)
        file_dt = datetime.fromtimestamp(mtime)
    except Exception:
        file_dt = datetime.now()

    year = str(file_dt.year)
    month = file_dt.strftime('%B')
    day = file_dt.strftime('%d')

    bahanpustaka_folder = bahanpustaka_map.get(bahanpustaka_code, bahanpustaka_code)
    kegiatan_folder = kegiatan_map.get(kegiatan_code, kegiatan_code)

    final_dest = os.path.join(dest_base, bahanpustaka_folder, kegiatan_folder, year, month, day)
    os.makedirs(final_dest, exist_ok=True)
    dst_path = os.path.join(final_dest, new_file_name)

    if safe_copy_file(file_path, dst_path, dry_run=dry_run):
        if safe_delete_file(file_path, dry_run=dry_run):
            logger.info(f"Moved: {file_name} -> {dst_path}")
            return True
        else:
            logger.error(f"Copy succeeded but delete failed for {file_name}")
            return False

    return False


def main():
    parser = argparse.ArgumentParser(description='Batch File Mover - process folder once and move files')
    parser.add_argument('--source', '-s', default=r'C:\TestWatch', help='Source folder to scan')
    parser.add_argument('--dest', '-d', default=r'Z:', help='Destination base folder')
    parser.add_argument('--kegiatan-map', default='kegiatan_map.json')
    parser.add_argument('--bahan-map', default='bahanpustaka_map.json')
    parser.add_argument('--min-mb', type=int, default=5, help='Minimum file size in MB to process')
    parser.add_argument('--dry-run', action='store_true', help='Do not actually copy/delete files')

    args = parser.parse_args()

    source = args.source
    dest = args.dest
    kegiatan_map_path = args.kegiatan_map
    bahan_map_path = args.bahan_map

    # create_sample_mapping_files(kegiatan_map_path, bahan_map_path)

    kegiatan_map = load_mapping(kegiatan_map_path)
    bahan_map = load_mapping(bahan_map_path)

    min_size_bytes = args.min_mb * 1024 * 1024

    if not os.path.exists(source):
        logger.error(f"Source folder does not exist: {source}")
        return

    files = [os.path.join(source, f) for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]

    logger.info(f"Found {len(files)} files in {source}. Starting processing...")

    moved = 0
    skipped = 0
    errors = 0

    for f in files:
        try:
            ok = process_file(f, dest, bahan_map, kegiatan_map, min_size_bytes, dry_run=args.dry_run)
            if ok:
                moved += 1
            else:
                skipped += 1
        except Exception as e:
            logger.error(f"Error processing {f}: {e}")
            errors += 1

    logger.info(f"Finished. Moved: {moved}, Skipped: {skipped}, Errors: {errors}")


if __name__ == '__main__':
    main()
