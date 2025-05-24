from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pathlib import Path
from ..core.config import Config
from ..utils.files import get_dirs_hierarchy, get_files_list

router = APIRouter()

def get_preview(photo_path: str, request: Request, size: int):
    metadata: dict = request.app.state.metadata
    cfg = request.app.state.cfg
    if photo_path not in metadata:
        raise HTTPException(status_code=400, detail="Invalid photo path")

    preview_path = metadata.get(photo_path, {}).get('preview', {}).get(str(size))
    if preview_path is None:
        raise HTTPException(status_code=400, detail=f"Can't find preview with size: {size}")

    path = cfg.cache_root / preview_path
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(str(path))

@router.get("/preview_small/{photo_path:path}")
def get_small_preview(photo_path: str, request: Request):
    return get_preview(photo_path, request, 512)

@router.get("/preview_large/{photo_path:path}")
def get_small_preview(photo_path: str, request: Request):
    return get_preview(photo_path, request, 1024)

@router.get("/metadata/{photo_path:path}")
def get_small_preview(photo_path: str, request: Request):
    metadata: dict = request.app.state.metadata
    if photo_path not in metadata:
        raise HTTPException(status_code=400, detail="Invalid photo path")
    return metadata[photo_path]

@router.get("/structure")
def get_structure(request: Request):
    return get_dirs_hierarchy(request.app.state.cfg.input_root)

@router.get("/list_dir/{photos_dir:path}")
def get_photos_list(photos_dir: str, request: Request):
    cfg: Config = request.app.state.cfg
    return get_files_list(cfg.input_root, cfg.input_root / Path(photos_dir))

@router.get("/list")
def get_photos_list(request: Request):
    metadata: dict = request.app.state.metadata
    return sorted(metadata.keys())
