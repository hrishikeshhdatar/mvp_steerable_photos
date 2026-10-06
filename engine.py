import os
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel

MODEL_NAME = "google/siglip-so400m-patch14-384"

class SteeringVectorEngine:
    def __init__(self, data_dir="data"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.data_dir = data_dir
        self.embeddings_path = os.path.join(data_dir, "embeddings.pt")
        
        # Load SigLIP model and processor
        self.processor = AutoProcessor.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME).to(self.device)
        self.model.eval()

        self.image_paths = []
        self.image_embeddings = None
        self.metadata = []

    def _unwrap_tensor(self, emb, attr_name="image_embeds"):
        """Extract raw PyTorch Tensor if model output is inside a dataclass/container."""
        if hasattr(emb, attr_name):
            return getattr(emb, attr_name)
        elif hasattr(emb, "pooler_output"):
            return emb.pooler_output
        elif isinstance(emb, (tuple, list)):
            return emb[0]
        return emb

    def load_or_build_index(self, image_folder="data/images"):
        """Precomputes or loads 1152-dimensional SigLIP embeddings for sandbox photos."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if os.path.exists(self.embeddings_path):
            data = torch.load(self.embeddings_path, map_location=self.device)
            self.image_paths = data["paths"]
            self.image_embeddings = data["embeddings"].to(self.device)
            self.metadata = data.get("metadata", [{} for _ in self.image_paths])
            return

        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder, exist_ok=True)
            return

        self.image_paths = [
            os.path.join(image_folder, f) for f in os.listdir(image_folder)
            if f.lower().endswith(valid_exts)
        ]

        if not self.image_paths:
            return

        embeddings_list = []
        self.metadata = []

        for path in self.image_paths:
            try:
                img = Image.open(path).convert("RGB")
                inputs = self.processor(images=img, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    img_emb = self.model.get_image_features(**inputs)
                    img_emb = self._unwrap_tensor(img_emb, attr_name="image_embeds")
                    img_emb = F.normalize(img_emb, p=2, dim=-1)
                    
                embeddings_list.append(img_emb)

                # Metadata extraction (EXIF date checking)
                has_exif = False
                exif_year = None
                try:
                    exif_data = img._getexif()
                    if exif_data and 36867 in exif_data:  # DateTimeOriginal
                        exif_year = int(exif_data[36867].split(":")[0])
                        has_exif = True
                except Exception:
                    pass

                self.metadata.append({"has_exif": has_exif, "year": exif_year})
            except Exception as e:
                print(f"Skipping image {path}: {e}")

        if embeddings_list:
            self.image_embeddings = torch.cat(embeddings_list, dim=0)
            torch.save({
                "paths": self.image_paths,
                "embeddings": self.image_embeddings.cpu(),
                "metadata": self.metadata
            }, self.embeddings_path)

    def encode_text(self, text_prompt: str) -> torch.Tensor:
        """Encodes text query into 1152-dim SigLIP embedding space."""
        inputs = self.processor(
            text=[text_prompt], 
            return_tensors="pt", 
            padding="max_length", 
            max_length=64
        ).to(self.device)
        
        with torch.no_grad():
            text_emb = self.model.get_text_features(**inputs)
            text_emb = self._unwrap_tensor(text_emb, attr_name="text_embeds")
            text_emb = F.normalize(text_emb, p=2, dim=-1)
            
        return text_emb

    def search(self, 
               query_text: str, 
               pos_indices: list[int] = None, 
               neg_indices: list[int] = None, 
               active_year: int = None,
               alpha: float = 0.5, 
               beta: float = 0.4, 
               gamma: float
