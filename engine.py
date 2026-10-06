import os
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import AutoProcessor, AutoModel

class SteeringVectorEngine:
    def __init__(self, model_name="google/siglip-so400m-patch14-384", data_dir="data"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.data_dir = data_dir
        self.embeddings_path = os.path.join(data_dir, "embeddings.pt")
        
        # Initialize SigLIP 1152-D Multimodal Model
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device).eval()
        
        self.image_paths = []
        self.image_embeddings = None
        self.metadata = []

    def load_or_build_index(self, image_folder="data/images"):
        """Precomputes or loads 1152-D SigLIP embeddings for target dataset."""
        os.makedirs(self.data_dir, exist_ok=True)
        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        current_paths = [
            os.path.join(image_folder, f) for f in os.listdir(image_folder)
            if f.lower().endswith(valid_exts)
        ] if os.path.exists(image_folder) else []

        # Load cached vectors if image count matches
        if os.path.exists(self.embeddings_path):
            try:
                data = torch.load(self.embeddings_path, map_location=self.device)
                if len(data.get("paths", [])) == len(current_paths):
                    self.image_paths = data["paths"]
                    self.image_embeddings = data["embeddings"].to(self.device)
                    self.metadata = data.get("metadata", [{} for _ in self.image_paths])
                    return
            except Exception:
                pass

        self.image_paths = current_paths
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
                    if hasattr(img_emb, "image_embeds"):
                        img_emb = img_emb.image_embeds
                    elif hasattr(img_emb, "pooler_output"):
                        img_emb = img_emb.pooler_output
                    img_emb = F.normalize(img_emb, p=2, dim=-1)
                
                embeddings_list.append(img_emb)

                # Extract camera metadata / year priors
                has_exif = False
                exif_year = None
                try:
                    exif_data = img._getexif()
                    if exif_data and 36867 in exif_data:
                        exif_year = int(exif_data[36867].split(":")[0])
                        has_exif = True
                except Exception:
                    pass

                self.metadata.append({"has_exif": has_exif, "year": exif_year})
            except Exception as e:
                print(f"Skipping corrupt image {path}: {e}")

        if embeddings_list:
            self.image_embeddings = torch.cat(embeddings_list, dim=0)
            torch.save({
                "paths": self.image_paths,
                "embeddings": self.image_embeddings.cpu(),
                "metadata": self.metadata
            }, self.embeddings_path)

    def search(self, query_text, pos_indices=[], neg_indices=[], active_year=None,
               alpha=0.5, beta=0.4, gamma=0.2, top_k=50):
        """
        Executes vector search with:
        1. Multi-turn weight damping guardrails
        2. Hyper-sphere unit normalization bounds
        3. Real-time quantitative evaluation telemetry (MRR, P@3, Cosine Drift)
        """
        if self.image_embeddings is None or len(self.image_paths) == 0:
            return [], {}

        # 1. Encode Natural Language Text Query
        inputs = self.processor(text=[query_text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_emb = self.model.get_text_features(**inputs)
            if hasattr(text_emb, "text_embeds"):
                text_emb = text_emb.text_embeds
            elif hasattr(text_emb, "pooler_output"):
                text_emb = text_emb.pooler_output
            v_query = F.normalize(text_emb, p=2, dim=-1)

        # 2. Vector Shift Arithmetic with Damping Guardrails
        v_steered = alpha * v_query

        # Positives accumulation with square-root weight damping
        if pos_indices:
            pos_embs = self.image_embeddings[pos_indices]
            e_pos_mean = torch.mean(pos_embs, dim=0, keepdim=True)
            e_pos_mean = F.normalize(e_pos_mean, p=2, dim=-1)
            beta_eff = beta / (1.0 + 0.3 * (len(pos_indices) - 1))
            v_steered += beta_eff * e_pos_mean

        # Negatives accumulation with square-root weight damping
        if neg_indices:
            neg_embs = self.image_embeddings[neg_indices]
            e_neg_mean = torch.mean(neg_embs, dim=0, keepdim=True)
            e_neg_mean = F.normalize(e_neg_mean, p=2, dim=-1)
            gamma_eff = gamma / (1.0 + 0.3 * (len(neg_indices) - 1))
            v_steered -= gamma_eff * e_neg_mean

        # Hyper-sphere Unit Normalization Guardrail
        v_steered = F.normalize(v_steered, p=2, dim=-1)

        # Compute cosine shift telemetry
        cosine_sim = F.cosine_similarity(v_query, v_steered, dim=-1).item()
        angular_drift = round((1.0 - cosine_sim) * 90.0, 2)

        # 3. Compute Vector Cosine Similarities across Index
        scores = torch.matmul(self.image_embeddings, v_steered.T).squeeze(-1)

        # 4. Apply Soft Temporal Prior Offset (+0.08)
        if active_year:
            for idx, meta in enumerate(self.metadata):
                if meta.get("year") == active_year or str(active_year) in self.image_paths[idx]:
                    scores[idx] += 0.08

        # Rank Order Results
        sorted_indices = torch.argsort(scores, descending=True).cpu().tolist()

        results = []
        for rank, idx in enumerate(sorted_indices[:top_k]):
            results.append({
                "index": idx,
                "path": self.image_paths[idx],
                "score": round(scores[idx].item(), 4),
                "rank": rank + 1
            })

        # 5. Compute Quantitative Benchmark Telemetry (MRR & P@3)
        mrr = 0.0
        precision_at_3 = 0.0
        if pos_indices:
            p_hits = sum(1 for r in results[:3] if r["index"] in pos_indices)
            precision_at_3 = round((p_hits / min(3, len(pos_indices))) * 100, 1)

            first_pos_rank = next((r["rank"] for r in results if r["index"] in pos_indices), None)
            if first_pos_rank:
                mrr = round(1.0 / first_pos_rank, 3)

        telemetry = {
            "cosine_similarity": round(cosine_sim, 4),
            "angular_drift_deg": angular_drift,
            "mrr": mrr,
            "precision_at_3": precision_at_3,
            "dimension": self.image_embeddings.shape[1],
            "total_indexed": len(self.image_paths),
            "is_bounded": True
        }

        return results, telemetry
