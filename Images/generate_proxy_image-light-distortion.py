"""
generate_proxy_images.py
Creates transformed versions of a sample of images for image->image robustness testing.
Ground truth mapping: proxy_<original_filename> -> original_filename
"""

import os
import random
from PIL import Image, ImageEnhance

# ---------------- CONFIG ----------------
SOURCE_DIR = r"C:\Users\HP\Downloads\flickr30k_images"
OUTPUT_DIR = r"C:\Users\HP\Downloads\flickr30k_proxy_images"
NUM_IMAGES = 200  # no of images to create proxies for
SEED = 42
# -----------------------------------------

random.seed(SEED)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def apply_random_transform(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")

    # Rotation
    angle = random.uniform(-15, 15)
    img = img.rotate(angle, expand=False, fillcolor=(255, 255, 255))

    # Crop (zoom)
    w, h = img.size
    crop_pct = random.uniform(0.80, 0.95)
    new_w, new_h = int(w * crop_pct), int(h * crop_pct)
    left = random.randint(0, w - new_w)
    top = random.randint(0, h - new_h)
    img = img.crop((left, top, left + new_w, top + new_h))
    img = img.resize((w, h))

    # Brightness
    brightness_factor = random.uniform(0.7, 1.3)
    img = ImageEnhance.Brightness(img).enhance(brightness_factor)

    # Contrast
    contrast_factor = random.uniform(0.85, 1.15)
    img = ImageEnhance.Contrast(img).enhance(contrast_factor)

    return img


def main():
    all_files = [
        f for f in os.listdir(SOURCE_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    print(f"Found {len(all_files)} source images.")

    sample = random.sample(all_files, min(NUM_IMAGES, len(all_files)))

    mapping = []
    for i, fname in enumerate(sample, start=1):
        src_path = os.path.join(SOURCE_DIR, fname)
        try:
            img = Image.open(src_path)
            proxy_img = apply_random_transform(img)

            proxy_name = f"proxy_{fname}"
            out_path = os.path.join(OUTPUT_DIR, proxy_name)
            proxy_img.save(out_path, quality=90)

            mapping.append((proxy_name, fname))
        except Exception as e:
            print(f"Skipped {fname}: {e}")

        if i % 50 == 0:
            print(f"Processed {i}/{len(sample)}")

    # Save mapping file: proxy_filename -> ground_truth_original_filename
    mapping_path = os.path.join(OUTPUT_DIR, "proxy_ground_truth.csv")
    with open(mapping_path, "w", encoding="utf-8") as f:
        f.write("proxy_filename,ground_truth_filename\n")
        for proxy_name, orig_name in mapping:
            f.write(f"{proxy_name},{orig_name}\n")

    print(f"\nDone. {len(mapping)} proxy images saved to {OUTPUT_DIR}")
    print(f"Ground truth mapping saved to {mapping_path}")


if __name__ == "__main__":
    main()