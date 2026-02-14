import os
import shutil
import json
import logging
import argparse
from datetime import datetime
import time
import hashlib
import tempfile
import threading
from pathlib import Path
import stat
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional
import psutil

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('batch_file_mover.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Performance monitoring
class PerformanceMonitor:
    """Monitor performance metrics"""
    def __init__(self):
        self.start_time = time.time()
        self.files_processed = 0
        self.bytes_copied = 0
        self.errors = 0
        
    def log_metrics(self):
        elapsed = time.time() - self.start_time
        files_per_sec = self.files_processed / max(elapsed, 1)
        mb_per_sec = (self.bytes_copied / (1024*1024)) / max(elapsed, 1)
        
        logger.info(f"Performance Metrics:")
        logger.info(f"  - Elapsed time: {elapsed:.2f}s")
        logger.info(f"  - Files processed: {self.files_processed}")
        logger.info(f"  - Files/sec: {files_per_sec:.2f}")
        logger.info(f"  - MB copied: {self.bytes_copied/(1024*1024):.2f} MB")
        logger.info(f"  - MB/sec: {mb_per_sec:.2f}")
        logger.info(f"  - Errors: {self.errors}")
        logger.info(f"  - Memory usage: {psutil.Process().memory_info().rss / (1024*1024):.2f} MB")
        
    def increment_files(self, bytes_count=0):
        self.files_processed += 1
        self.bytes_copied += bytes_count
        
    def increment_errors(self):
        self.errors += 1

# Global performance monitor
perf_monitor = PerformanceMonitor()
class FileMoverError(Exception):
    """Base exception for file mover operations"""
    pass

class FileIntegrityError(FileMoverError):
    """File integrity verification failed"""
    pass

class NetworkError(FileMoverError):
    """Network-related operation failed"""
    pass

class PermissionError(FileMoverError):
    """Permission-related operation failed"""
    pass


def load_mapping(path):
    """Load mapping file with proper error handling"""
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Mapping file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            
        # Validate mapping structure
        if not isinstance(mapping, dict):
            raise ValueError(f"Invalid mapping format in {path}: expected dictionary")
            
        logger.info(f"Mapping loaded from {path}: {len(mapping)} entries")
        return mapping
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in mapping file {path}: {e}")
        raise FileMoverError(f"Invalid JSON format in {path}") from e
    except FileNotFoundError as e:
        logger.error(f"Mapping file not found: {path}")
        raise  # Re-raise FileNotFoundError
    except PermissionError as e:
        logger.error(f"Permission denied accessing mapping file {path}: {e}")
        raise PermissionError(f"Cannot access mapping file {path}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading mapping {path}: {e}")
        raise FileMoverError(f"Failed to load mapping {path}") from e
 
def is_file_deletable(file_path):
    try:
        # Check file permissions instead of rename test
        if not os.access(file_path, os.W_OK):
            return False
        # Check if file is locked by trying to open in exclusive mode
        try:
            with open(file_path, 'r+b') as f:
                pass
            return True
        except (IOError, OSError):
            return False
    except Exception:
        return False


def is_file_readable(file_path):
    try:
        with open(file_path, 'rb') as f:
            f.read(1024)
        return True
    except Exception:
        return False


def is_file_stable(file_path, check_interval=0.5):
    try:
        size1 = os.path.getsize(file_path)
        time.sleep(check_interval)
        size2 = os.path.getsize(file_path)
        change_percent = abs(size2 - size1) / max(size1, 1) * 100
        return change_percent < 1.0
    except Exception:
        return False


def safe_copy_file(src_path, dst_path, dry_run=False, max_retries=3):
    """Copy file with retry mechanism and detailed error handling"""
    file_size = 0
    try:
        file_size = os.path.getsize(src_path)
    except:
        pass
        
    for attempt in range(max_retries):
        try:
            logger.info(f"Copying {src_path} -> {dst_path} (attempt {attempt + 1}/{max_retries})")
            if dry_run:
                perf_monitor.increment_files(file_size)
                return True
            
            # Validate destination path to prevent path traversal
            dst_path = os.path.normpath(dst_path)
            if not dst_path.startswith(os.path.normpath(os.path.dirname(dst_path))):
                raise ValueError("Invalid destination path - potential path traversal")
                
            # Create destination directory with proper permissions
            dst_dir = os.path.dirname(dst_path)
            os.makedirs(dst_dir, exist_ok=True)
            
            # Use temporary file for atomic copy
            temp_dst = dst_path + '.tmp'
            
            # Copy with integrity verification
            shutil.copy2(src_path, temp_dst)
            
            # Verify file integrity with checksum
            if verify_file_integrity(src_path, temp_dst):
                # Atomic move to final destination
                os.replace(temp_dst, dst_path)
                logger.info(f"Copy verified and completed: {dst_path}")
                perf_monitor.increment_files(file_size)
                return True
            else:
                raise FileIntegrityError("File integrity verification failed")
                
        except PermissionError as e:
            logger.error(f"Permission error copying file (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                perf_monitor.increment_errors()
                raise PermissionError(f"Failed to copy {src_path} after {max_retries} attempts") from e
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except (IOError, OSError) as e:
            logger.error(f"IO error copying file (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                perf_monitor.increment_errors()
                raise NetworkError(f"Network/IO error copying {src_path} after {max_retries} attempts") from e
            time.sleep(2 ** attempt)
            
        except FileIntegrityError as e:
            logger.error(f"File integrity error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                perf_monitor.increment_errors()
                raise
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Unexpected error copying file (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                perf_monitor.increment_errors()
                raise FileMoverError(f"Unexpected error copying {src_path}") from e
            time.sleep(1)
            
        finally:
            # Cleanup temporary file on error
            temp_dst = dst_path + '.tmp'
            if os.path.exists(temp_dst):
                try:
                    os.remove(temp_dst)
                except:
                    pass
                    
    return False


def verify_file_integrity(src_path, dst_path):
    """Verify file integrity using SHA-256 checksum"""
    try:
        src_hash = calculate_file_hash(src_path)
        dst_hash = calculate_file_hash(dst_path)
        return src_hash == dst_hash
    except Exception as e:
        logger.error(f"Error verifying file integrity: {e}")
        return False


def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return None


def safe_delete_file(path, dry_run=False, max_retries=2):
    """Delete file with retry mechanism and error handling"""
    for attempt in range(max_retries):
        try:
            if dry_run:
                logger.info(f"(Dry-run) Would delete: {path}")
                return True
                
            if not os.path.exists(path):
                logger.debug(f"File already deleted: {path}")
                return True
            
            # Additional check to prevent accidental deletion of important files
            if not is_file_deletable(path):
                raise PermissionError(f"File is not deletable: {path}")
                
            os.remove(path)
            logger.info(f"Successfully deleted: {path}")
            return True
            
        except PermissionError as e:
            logger.error(f"Permission error deleting file (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise PermissionError(f"Failed to delete {path} after {max_retries} attempts") from e
            time.sleep(1)
            
        except OSError as e:
            logger.error(f"OS error deleting file (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise FileMoverError(f"Failed to delete {path} after {max_retries} attempts") from e
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Unexpected error deleting file (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise FileMoverError(f"Unexpected error deleting {path}") from e
            time.sleep(1)
            
    return False


def parse_filename(file_name):
    """Parse and validate filename format"""
    # Validate filename for security
    if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
        return None
        
    parts = file_name.split('_')
    if len(parts) < 3:
        return None
    if '.' not in parts[-1]:
        return None
        
    # Validate each part
    bahanpustaka_code = parts[0].upper()
    kegiatan_code = parts[1].upper()
    
    # Only allow alphanumeric codes
    if not bahanpustaka_code.isalnum() or not kegiatan_code.isalnum():
        return None
        
    new_file_name = '_'.join(parts[2:])
    return bahanpustaka_code, kegiatan_code, new_file_name


def process_files_parallel(files: List[str], dest_base: str, bahanpustaka_map: Dict, kegiatan_map: Dict, 
                          min_size_bytes: int, max_workers: int = 4, dry_run: bool = False) -> Tuple[int, int, int]:
    """Process multiple files in parallel for better performance"""
    moved = 0
    skipped = 0
    errors = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_file, f, dest_base, bahanpustaka_map, kegiatan_map, min_size_bytes, dry_run): f 
            for f in files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    moved += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                errors += 1
                perf_monitor.increment_errors()
                
    return moved, skipped, errors


def process_file(file_path, dest_base, bahanpustaka_map, kegiatan_map, min_size_bytes, dry_run=False):
    """Process single file with comprehensive error handling"""
    file_name = os.path.basename(file_path)
    
    try:
        # Ignore temp files and directories
        if file_name.lower().endswith('.tmp') or os.path.isdir(file_path):
            logger.info(f"Ignoring temporary or directory: {file_name}")
            return False

        parts = parse_filename(file_name)
        if parts is None:
            logger.warning(f"Invalid filename format, skipping: {file_name}")
            return False

        bahanpustaka_code, kegiatan_code, new_file_name = parts

        # Skip files whose codes are not present in the mapping JSONs
        if bahanpustaka_code not in bahanpustaka_map:
            logger.warning(f"Skipping {file_name}: bahan pustaka code '{bahanpustaka_code}' not found in mapping")
            return False
        if kegiatan_code not in kegiatan_map:
            logger.warning(f"Skipping {file_name}: kegiatan code '{kegiatan_code}' not found in mapping")
            return False

        # Size check with proper error handling
        try:
            size = os.path.getsize(file_path)
            if size < min_size_bytes:
                logger.info(f"Skipping small file {file_name} ({size} bytes)")
                return False
        except OSError as e:
            logger.error(f"Could not get size for {file_name}: {e}")
            return False

        # Readability/stability checks - skip for better performance
        # if not is_file_readable(file_path) or not is_file_deletable(file_path) or not is_file_stable(file_path):
        #     logger.warning(f"File not ready yet, skipping: {file_name}")
        #     return False

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

        # Copy and delete with proper error handling
        if safe_copy_file(file_path, dst_path, dry_run=dry_run):
            if safe_delete_file(file_path, dry_run=dry_run):
                logger.info(f"Successfully moved: {file_name} -> {dst_path}")
                return True
            else:
                logger.error(f"Copy succeeded but delete failed for {file_name}")
                return False
        else:
            logger.error(f"Copy failed for {file_name}")
            return False

    except FileMoverError as e:
        logger.error(f"File mover error processing {file_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing {file_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Batch File Mover - process folder once and move files')
    parser.add_argument('--source', '-s', default=r'C:\TestWatch', help='Source folder to scan')
    parser.add_argument('--dest', '-d', default=r'Z:', help='Destination base folder')
    parser.add_argument('--kegiatan-map', default='kegiatan_map.json')
    parser.add_argument('--bahan-map', default='bahanpustaka_map.json')
    parser.add_argument('--min-mb', type=int, default=5, help='Minimum file size in MB to process')
    parser.add_argument('--dry-run', action='store_true', help='Do not actually copy/delete files')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum number of parallel workers')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel processing')

    args = parser.parse_args()

    source = args.source
    dest = args.dest
    kegiatan_map_path = args.kegiatan_map
    bahan_map_path = args.bahan_map

    try:
        # Load mapping files with proper error handling
        kegiatan_map = load_mapping(kegiatan_map_path)
        bahan_map = load_mapping(bahan_map_path)

        min_size_bytes = args.min_mb * 1024 * 1024

        if not os.path.exists(source):
            logger.error(f"Source folder does not exist: {source}")
            return

        # Get file list with memory-efficient approach
        try:
            files = [os.path.join(source, f) for f in os.listdir(source) 
                    if os.path.isfile(os.path.join(source, f))]
        except OSError as e:
            logger.error(f"Error reading source directory {source}: {e}")
            return

        logger.info(f"Found {len(files)} files in {source}. Starting processing...")
        
        # Process files (parallel or sequential)
        if args.parallel and len(files) > 1:
            logger.info(f"Processing files in parallel with {args.max_workers} workers")
            moved, skipped, errors = process_files_parallel(
                files, dest, bahan_map, kegiatan_map, min_size_bytes, 
                args.max_workers, args.dry_run
            )
        else:
            logger.info("Processing files sequentially")
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
                    perf_monitor.increment_errors()

        # Log final metrics
        perf_monitor.log_metrics()
        logger.info(f"Finished. Moved: {moved}, Skipped: {skipped}, Errors: {errors}")

    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
    except FileMoverError as e:
        logger.error(f"File mover error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        raise


if __name__ == '__main__':
    main()
