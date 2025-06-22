import torch
import open_clip
from PIL import Image
import numpy as np

# Utility to get CLIP V2 model and tokenizer
clip_model_name = "ViT-H-14"
clip_pretrained = "laion2b_s32b_b79k"
clip_dim = 1024

def get_clip_model():
    model, _, preprocess = open_clip.create_model_and_transforms(
        clip_model_name, pretrained=clip_pretrained
    )
    tokenizer = open_clip.get_tokenizer(clip_model_name)
    return model, preprocess, tokenizer

def get_image_embedding(image_path, model, preprocess):
    image = Image.open(image_path).convert("RGB")
    image_input = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    return image_features.cpu().numpy()[0]

def get_text_embedding(text, model, tokenizer):
    text_input = tokenizer([text])
    with torch.no_grad():
        text_features = model.encode_text(text_input)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy()[0]

def calculate_similarity(image_path, text):
    model, preprocess, tokenizer = get_clip_model()
    model.eval()
    image_emb = get_image_embedding(image_path, model, preprocess)
    text_emb = get_text_embedding(text, model, tokenizer)
    similarity = float(np.dot(image_emb, text_emb))
    return similarity

if __name__ == "__main__":
    image_path = "tiny.png"
    text = "Теория графов и алгоритм Дейкстры"
    score = calculate_similarity(image_path, text)
    print(f"Cosine similarity: {score:.4f}")