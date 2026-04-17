"""Target-size optimization.

.optimize(target_kb=N) runs the pipeline and then binary-searches quality
to find the largest file that still fits under the target. Returns bytes.
"""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("09 - Optimize")
    src = photo()

    # Hit ~100 KB by tuning JPEG quality.
    data = Image(src).resize(1200).jpeg().optimize(target_kb=100)
    path = out("09_optimized_100kb.jpg")
    path.write_bytes(data)
    print(f"{path.name}: {len(data) // 1024} KB (target 100 KB)")

    # Same for WebP. quality range is configurable via min_quality/max_quality.
    data = Image(src).resize(1200).webp().optimize(
        target_kb=50, min_quality=20, max_quality=95,
    )
    path = out("09_optimized_50kb.webp")
    path.write_bytes(data)
    print(f"{path.name}: {len(data) // 1024} KB (target 50 KB)")


if __name__ == "__main__":
    main()
