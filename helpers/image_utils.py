"""
helpers/image_utils.py — Image saving and display helpers.

Ported from hereiz-AI-terminal-assistant helpers.
Cross-platform: pathlib.Path + matplotlib.
"""
import shutil
import matplotlib.pyplot as plt
from pathlib import Path


def save_imgs(img_paths: list[str], dest_dir: str) -> list[str]:
    """
    Copy a list of image files to dest_dir.
    Returns the list of destination paths as strings.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    for src in img_paths:
        src_path = Path(src)
        if src_path.exists():
            dst = dest / src_path.name
            shutil.copy2(src_path, dst)
            saved.append(str(dst))
        else:
            print(f"[image_utils] Warning: image not found: {src}")
    return saved


def show_images_side_by_side(imgs_dir: str) -> None:
    """Display all PNG/JPG images in a directory side by side using matplotlib."""
    dir_path = Path(imgs_dir)
    imgs = sorted(list(dir_path.glob("*.png")) + list(dir_path.glob("*.jpg")))
    if not imgs:
        print("[image_utils] No images to display.")
        return

    n = len(imgs)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]

    for ax, img_path in zip(axes, imgs):
        ax.imshow(plt.imread(str(img_path)))
        ax.set_title(img_path.name, fontsize=9)
        ax.axis("off")

    plt.tight_layout()
    plt.show()
