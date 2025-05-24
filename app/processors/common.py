import os
import logging
import torch
import json
import shutil
from pathlib import Path
from multiprocessing import Pool


class ProgressCallback:
    def __call__(self, progress: float, logger: logging.Logger, rank: int = 0) -> bool:
        logger.info(f"Progress [{rank}]: {100. * progress:.2f} %")
        return True


class Processor:
    def __init__(self, logger: logging.Logger, progress_callback: ProgressCallback = None):
        self.logger = logger
        self.progress_callback = progress_callback or ProgressCallback()

    def __call__(self, input_root: Path, input_file_rel_path: Path, output_root: Path):
        raise NotImplementedError("This method must be implemented")

    def run(self, input_root: Path, output_root: Path, input_files_all: list[Path], rank: int = 0, num_workers: int = 1, progress_step: int = 100) -> dict:
        input_files = input_files_all[rank::num_workers]
        self.logger.info(f"Start processing input files [{rank} / {num_workers}]: {len(input_files)} / {len(input_files_all)}")
        files_meta = {}
        for i, input_file_rel_path in enumerate(input_files):
            output_dir = output_root / input_file_rel_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            try:
                files_meta[str(input_file_rel_path)] = self.__call__(input_root, input_file_rel_path, output_root)
            except KeyboardInterrupt as e:
                logging.warning(f"Caught KeyboardInterrupt, stopping")
                break
            except Exception as e:
                logging.warning(f"Caught exception: {e}")
            if i % progress_step == 0:
                if not self.progress_callback(i / len(input_files), self.logger, rank=rank):
                    logging.warning(f"Progress interrupting")
                    break
        return files_meta


def _run_processor_task(task):
    processor, worker_id, num_workers, args, kwargs = task
    return processor.run(*args, **kwargs, rank=worker_id, num_workers=num_workers)


def run_parallel(processor: Processor, num_workers: int, *args, **kwargs):
        tasks = [(processor, proc_id, num_workers, args, kwargs) for proc_id in range(num_workers)]
        with Pool(num_workers) as p:
            output = p.map(_run_processor_task, tasks)
        output_merged = output[0]
        for i in range(1, num_workers):
            output_merged.update(output[i])
        return output_merged


def set_num_threads(num_threads: int):
    os.environ["OMP_NUM_THREADS"] = str(num_threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(num_threads)
    os.environ["MKL_NUM_THREADS"] = str(num_threads)
    os.environ["VECLIB_MAXIMUM_THREADS"] = str(num_threads)
    os.environ["NUMEXPR_NUM_THREADS"] = str(num_threads)
    torch.set_num_threads(num_threads)

