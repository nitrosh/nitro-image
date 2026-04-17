"""BatchImage: apply one pipeline to many files matched by a glob.

The save pattern can include {name} which is replaced with the source
file's stem. Pass parallel=True to process files concurrently on a
thread pool (great for I/O-bound workloads).
"""

from __future__ import annotations

import shutil

from nitro_img import BatchImage

from _sample import SAMPLES, banner, out, photo


def main() -> None:
    banner("11 - Batch")

    # Seed a batch dir with a few sample photos so the glob has something to match.
    batch_src = SAMPLES / "batch"
    batch_src.mkdir(parents=True, exist_ok=True)
    for name in ("sunrise.jpg", "noon.jpg", "sunset.jpg"):
        dest = batch_src / name
        if not dest.exists():
            shutil.copy(photo(), dest)

    pattern = str(batch_src / "*.jpg")
    outdir = out("11_batch")

    # Sequential
    results = (
        BatchImage(pattern)
        .resize(600)
        .webp(quality=80)
        .save(str(outdir / "{name}.webp"))
    )
    print(f"Sequential: wrote {len(results)} files to {outdir}")

    # Parallel — same API, just add parallel=True.
    results = (
        BatchImage(pattern)
        .resize(400)
        .sepia()
        .jpeg(quality=82)
        .save(str(outdir / "{name}_sepia.jpg"), parallel=True, max_workers=4)
    )
    print(f"Parallel:   wrote {len(results)} sepia variants")


if __name__ == "__main__":
    main()
