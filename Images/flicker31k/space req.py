import os
from collections import defaultdict
import re

folder_path = "./Images"

with open('captions.txt', 'r', encoding='utf-8') as f:
    data = f.readlines()

# Pre-compile regex patterns outside the loop for speed
space_pattern = re.compile(r'\s+')
quote_pattern = re.compile(r'[\'"]')

captions = defaultdict(list)

# Process data and populate the dictionary
for d in data[1:]:
    image_id, caption = d.split('.jpg')
    image_id += '.jpg'

    caption = space_pattern.sub(' ', caption).strip()
    caption = quote_pattern.sub('', caption)

    captions[image_id].append(caption)

print(f"No of unique images: {len(captions)}")

total_image_bytes = 0
total_caption_bytes = 0

for image_id, caption_list in captions.items():
    try:
        total_image_bytes += os.path.getsize(os.path.join(folder_path, image_id))
    except FileNotFoundError:
        pass

    total_caption_bytes += sum(len(s.encode('utf-8')) for s in caption_list)

print(f"Image Size: {total_image_bytes} bytes, Caption size: {total_caption_bytes} bytes")
print(f"Image Size: {total_image_bytes/(1024**2):.2f} MB, Caption size: {total_caption_bytes/(1024**2):.2f} MB")
print(f"Average size: {total_image_bytes/(len(captions)*1024**2):.2f} MB")


folder_path = "./Images"
# png_files = [
#     os.path.join(folder_path, f)
#     for f in os.listdir(folder_path)
#     if f.lower().endswith(".jpg")
# ]

# formats = set()

# if png_files:
#     sizes = []
#     for file in png_files:
#         sizes.append(os.path.getsize(file))
#         format = file.split('.')[-1]
#         formats.add(format)

#     # Calculate average
#     avg_bytes = sum(sizes) / len(sizes)
#     avg_mb = avg_bytes / (1024 * 1024)

#     print(f"Found {len(png_files)} PNG images.")
#     print(f"Found {len(formats)} formats.", formats)
#     print(f"Average size: {avg_mb:.2f} MB ({avg_bytes:.2f} bytes)")
# else:
#     print("No PNG images found in the directory.")