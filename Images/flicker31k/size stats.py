with open('captions.txt', 'r', encoding='utf-8') as f:
    data = f.readlines()

freq = {}

for d in data[1:]:
    image_id = d.split(',')[0]
    freq[image_id] = freq.get(image_id, 0) + 1

print(f"No of unique ids: {len(freq)}")

cnt = 10
for key, val in sorted(freq.items(), key=lambda x: x[1]):
    if cnt == 0:
        break
    print(key, val)
    cnt -= 1



import os

# Put your folder path here
folder_path = "./Images"

# Get all PNG file paths, limited to the first 100
png_files = [
    os.path.join(folder_path, f)
    for f in os.listdir(folder_path)
    if f.lower().endswith(".jpg")
]

if png_files:
    # Get the file size for each PNG
    sizes = [os.path.getsize(file) for file in png_files]

    # Calculate average
    avg_bytes = sum(sizes) / len(sizes)
    avg_mb = avg_bytes / (1024 * 1024)

    print(f"Found {len(png_files)} PNG images.")
    print(f"Average size: {avg_mb:.2f} MB ({avg_bytes:.2f} bytes)")
else:
    print("No PNG images found in the directory.")