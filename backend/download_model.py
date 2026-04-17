# download_model.py
from transformers import CLIPModel, CLIPProcessor

model_name = "openai/clip-vit-base-patch32"

CLIPModel.from_pretrained(model_name, cache_dir="./models")
CLIPProcessor.from_pretrained(model_name, cache_dir="./models")

print("Models Downloaded")