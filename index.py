import faiss 
import os 
from pathlib import Path
import torchvision.models as models
from torchvision import transforms
import torch.nn as nn
from PIL import Image
import numpy as np

dimension = 512

def generate_image_embedding(image):
    preprocess = transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406],
                            std=[0.229,0.224,0.225]),
    ])
    img = preprocess(image).unsqueeze(0)

    model = models.resnet18(pretrained=True)
    feature_extractor = nn.Sequential(*list(model.children())[:-1])
    feature_extractor.eval()

    emb = feature_extractor(img)
    emb = emb.flatten(1)                  # → shape: (1, 512)
    emb = emb.detach().cpu().numpy().astype('float32') # convert to NumPy float32
    return emb

def save_image_index(xb, image_id=1):
    if Path("my_index.faiss").exists():
        index = faiss.read_index("my_index.faiss")
    else:
        index = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIDMap(index)
    ids = np.array([image_id], dtype=np.int64)
    index.add_with_ids(xb,ids)
    faiss.write_index(index, "my_index.faiss")
    print('success')

image = Image.open(f'Carl_Andre_Equivalent_VIII_1966_120Firebricks.jpg')
# img = read_image(image)
embeding = generate_image_embedding(image)
save_image_index(embeding)