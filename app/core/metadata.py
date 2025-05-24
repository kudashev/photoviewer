from pathlib import Path
import logging
import shutil
import json
from datetime import datetime

METADATA_FILE = Path('metadata.json')

def load_metadata(cache_root: Path):
    metadata_file = cache_root / METADATA_FILE
    if not metadata_file.exists():
        return {}
    with metadata_file.open("r", encoding="utf-8") as f:
        return json.load(f)

def update_dict(current: dict, new: dict) -> dict:
    for key, value in new.items():
        key = str(key)
        if isinstance(value, dict):
            current[key] = update_dict(current.get(key, {}), value)
        else:
            current[key] = value
    return current


def update_metadata(cache_root: Path, new_metadata: dict, logger: logging.Logger):
    metadata_file = cache_root / METADATA_FILE
    metadata_backup_file = None

    try:
        if metadata_file.exists():
            current_time = datetime.now().strftime("_%Y%m%d_%H%M%S")
            metadata_backup_file = cache_root / (METADATA_FILE.stem + current_time + METADATA_FILE.suffix)
            assert not metadata_backup_file.exists()
            shutil.copy(metadata_file, metadata_backup_file)
            logger.info(f"Created metadata backup: {metadata_backup_file}")
            with metadata_file.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            metadata = {}
        metadata = update_dict(metadata, new_metadata)
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, sort_keys=True)
        logger.info(f"Metadata updated: {metadata_file}")
    except Exception as e:
        logger.warning("Something went wrong during metadata update")
        if metadata_backup_file is not None:
            shutil.copy(metadata_backup_file, metadata_file)
            logger.warning(f"Backup metadata restored: {metadata_backup_file} -> {metadata_file}")
        raise e

    if metadata_backup_file is not None:
        logger.info(f"Remove metadata backup: {metadata_backup_file}")
        metadata_backup_file.unlink()