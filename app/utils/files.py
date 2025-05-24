import logging
from pathlib import Path

CACHE_DIR = '.photoviewer'
IMAGE_EXTENSIONS = ['.jpeg', '.jpg', '.webp', '.png', '.heic']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.webm', '.mkv']


def get_dirs_hierarchy(current_dir: Path, logger: logging.Logger = logging.getLogger(), skip_dirs: set[str] = set([CACHE_DIR])):
    current_dirs_structure = []
    logger.info(f"Getting dirs from root: {current_dir}")
    for item in current_dir.iterdir():
        if item.is_dir():
            if skip_dirs and (item.name in skip_dirs):
                continue
            current_dirs_structure.append({item.name: get_dirs_hierarchy(item, logger=logger, skip_dirs=skip_dirs)})
    return current_dirs_structure


def get_files_list(root: Path, current_dir: Path, extensions: set[str] = IMAGE_EXTENSIONS, logger: logging.Logger = logging.getLogger(), skip_dirs: set[str] = set([CACHE_DIR]), recursive: bool = False):
    logger.info(f"Getting files from root: {current_dir}")
    assert current_dir.is_dir()
    results_files = []
    for input_file in current_dir.iterdir():
        if input_file.is_dir() and recursive:
            if skip_dirs and (input_file.name in skip_dirs):
                logger.info(f"Skip dir: {input_file}")
                continue
            results_files += get_files_list(root, input_file, extensions, logger, skip_dirs=skip_dirs)
        else:
            if input_file.suffix.lower() in extensions:
                input_file_rel_path = input_file.relative_to(root)
                results_files.append(input_file_rel_path)
    return results_files


# if __name__ == '__main__':
#     import json
#     structure = get_dirs_hierarchy(Path("/home/oleg_kudashev/data/pap_haircuts/test_data/hair_live"))
#     with open('test.json', 'w') as f:
#         json.dump(structure, f, indent=2)
