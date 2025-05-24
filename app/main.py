from dataclasses import dataclass
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
import json
import uvicorn
from functools import partial
from app.api import photos, tags
from app.core.metadata import load_metadata
from app.core.config import Config
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pyrallis

# TODO: load config from app parameters
# TODO: logging


@asynccontextmanager
async def lifespan(app: FastAPI, cfg: Config):
    app.state.cfg = cfg
    app.state.metadata = load_metadata(cfg.cache_root)
    yield

cfg = Config(
    input_root=Path("/home/oleg_kudashev/data/pap_haircuts/test_data/hair_live"),
    cache_root=Path("/home/oleg_kudashev/data/pap_haircuts/test_data/hair_live/.photoviewer")
)

app = FastAPI(lifespan=partial(lifespan, cfg=cfg))

app.include_router(photos.router, prefix="/photos", tags=["Photos"])
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# @pyrallis.wrap()
# def main(cfg: Config):
#     uvicorn.run(app)
