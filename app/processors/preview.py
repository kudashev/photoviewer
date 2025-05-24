import os
import logging
from pathlib import Path
from PIL import Image
import numpy as np
import yaml
import json
import torch
from torchvision.transforms.functional import to_pil_image, to_tensor
from torchvision.transforms.v2.functional import resize
from dataclasses import dataclass, field
import pyrallis

from ..utils.logger import get_logger, setup_logger
from ..core.metadata import update_metadata
from .common import set_num_threads, Processor, run_parallel
from ..utils.files import get_files_list, IMAGE_EXTENSIONS

logger = get_logger('preview')


@dataclass
class PreviewConfig:
    input_root: Path
    output_root: Path
    sizes: list[int] = field(default_factory=lambda: [1024, 512])
    device: str = 'cpu'
    num_threads: int = 1
    num_workers: int = 8
    format: str = 'webp'
    quality: int = 75
    calc_psnr: bool = False
    extensions: set[str] = field(default_factory=lambda: set(IMAGE_EXTENSIONS))
    logging_level: str = 'INFO'


def calc_psnr(img_ref: np.ndarray, img_res: np.ndarray):
    aver_mse = np.mean(np.square(img_ref.astype(np.float32) / 255.0 - img_res.astype(np.float32) / 255.0))
    psnr = -10 * np.log10(max(aver_mse, 1.0e-5))
    return psnr


def calc_mse(img_ref: np.ndarray, img_res: np.ndarray) -> float:
    assert img_ref.dtype == np.uint8 and img_res.dtype == np.uint8
    return np.mean(np.square(img_ref.astype(np.float32) / 255.0 - img_res.astype(np.float32) / 255.0)).item()


class PreviewProcessor(Processor):
    def __init__(self, cfg: PreviewConfig, logger):
        super().__init__(logger)
        self.cfg = cfg

    def __call__(self, input_root: Path, input_file_rel_path: Path, output_root: Path):
        img_pil = Image.open(input_root / input_file_rel_path)

        w, h = img_pil.size
        info = {'preview': {}}
        img = to_tensor(img_pil).to(self.cfg.device)
        for output_size in self.cfg.sizes:
            output_file_rel_path = input_file_rel_path.parent / (input_file_rel_path.stem + f'_pr{output_size}.{self.cfg.format}')
            output_file = output_root / output_file_rel_path
            logger.debug(f"Resize file {input_root / input_file_rel_path} -> {output_file}, size = {output_size}")
            if max(h, w) > output_size:
                scale = output_size / float(max(h, w))
                img_resized = resize(img, (int(h * scale), int(w * scale)))
                img_pil_resized = to_pil_image(img_resized)
            else:
                img_pil_resized = img_pil
            img_pil_resized.save(output_file, self.cfg.format, optimize=True, quality=self.cfg.quality)
            info['preview'][output_size] = str(output_file_rel_path)

            if self.cfg.calc_psnr:
                info.setdefault('preview_mse', {})
                info['preview_mse'][output_size] = calc_mse(np.array(Image.open(output_file)), np.array(img_pil_resized))
        return info


@pyrallis.wrap()
def run(cfg: PreviewConfig):
    set_num_threads(cfg.num_threads)
    setup_logger(logger, rank=0, logging_level=cfg.logging_level)
    processor = PreviewProcessor(cfg, logger)
    logger.info(f"input_root: {cfg.input_root}")
    logger.info(f"output_root: {cfg.output_root}")
    cfg.output_root.mkdir(parents=True, exist_ok=True)
    input_files = get_files_list(cfg.input_root, cfg.input_root, cfg.extensions, logger)

    logger.info(f"Input files num: {len(input_files)}")
    output_metadata = run_parallel(processor, cfg.num_workers, cfg.input_root, cfg.output_root, input_files, progress_step=10)
    if cfg.calc_psnr:
        for output_size in cfg.sizes:
            preview_files_mse = [output_metadata[str(file)]['preview_mse'][output_size] for file in input_files]
            aver_mse = np.mean(preview_files_mse)
            psnr = -10 * np.log10(max(aver_mse, 1.0e-5))
            print(f"PSNR size={output_size}: {psnr:.3f}")

    update_metadata(cfg.output_root, output_metadata, logger)

if __name__ == '__main__':
    run()
