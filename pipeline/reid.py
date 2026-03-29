import torch
import torchreid
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering

class PersonReID:
    def __init__(self, model_name='osnet_ain_x1_0', use_gpu=False):
        """Initialize the ReID model from torchreid."""
        self.device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        self.model = torchreid.models.build_model(
            name=model_name,
            num_classes=1000,
            pretrained=True
        )
        self.model.eval()
        self.model = self.model.to(self.device)
        
        self.transform = transforms.Compose([
            transforms.Resize((256, 128)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def extract_features(self, img_path):
        """Extract a high-dimensional feature vector for a person crop."""
        image = Image.open(img_path).convert('RGB')
        image = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model(image)
            
        return features.cpu().numpy().flatten()

    def cluster_embeddings(self, embeddings, threshold=0.6):
        """Cluster feature vectors into unique identities based on cosine similarity."""
        if not embeddings:
            return []
            
        embeddings = np.array(embeddings)
        # Cosine similarity matrix
        sim_matrix = cosine_similarity(embeddings)
        # Distance matrix (1 - similarity)
        dist_matrix = 1 - sim_matrix
        
        # Identity clustering (Agglomerative)
        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric='precomputed',
            linkage='average',
            distance_threshold=threshold
        ).fit(dist_matrix)
        
        return clustering.labels_

    def merge_identities(self, scene_level_ids, alpha, beta, audio_similarity=None):
        """Score-level fusion logic for Re-Identification."""
        # This will be used in the fusion module
        pass
