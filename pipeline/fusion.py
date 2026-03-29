import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering

class FusionEngine:
    def __init__(self, alpha=0.7, beta=0.3):
        """Initialize the fusion engine with weights for visual and audio components."""
        self.alpha = alpha
        self.beta = beta

    def set_weights(self, alpha, beta):
        """Update alpha and beta during runtime (UI-configurable)."""
        # Normalize if necessary
        denominator = alpha + beta
        if denominator == 0:
            self.alpha, self.beta = 0.5, 0.5
        else:
            self.alpha = alpha / denominator
            self.beta = beta / denominator

    def compute_fused_similarity(self, visual_sim_matrix, audio_sim_matrix):
        """Fused Score = α * VisualSim + β * AudioSim."""
        fused_matrix = self.alpha * visual_sim_matrix + self.beta * audio_sim_matrix
        return fused_matrix

    def align_audio_visual(self, person_appearances, speaker_segments):
        """Map person tracks to speaker tracks based on temporal overlap."""
        aligned_data = []
        
        for person in person_appearances:
            # Person track format: {person_id: 1, start: 0, end: 120, frames: [], scene_id: 2}
            person_start, person_end = person['start'], person['end']
            
            # Find speakers during this time range
            potential_speakers = []
            for speaker in speaker_segments:
                # Speaker track format: {speaker: 'SPEAKER_00', start: 0, end: 5.0, embedding: []}
                # Check for overlap
                overlap_start = max(person_start, speaker['start'])
                overlap_end = min(person_end, speaker['end'])
                
                if overlap_start < overlap_end:
                    # Found an overlapping speaker
                    overlap_duration = overlap_end - overlap_start
                    potential_speakers.append({
                        "id": speaker['speaker'],
                        "duration": overlap_duration,
                        "embedding": speaker['embedding']
                    })
            
            # Map to the speaker with the longest overlap
            if potential_speakers:
                best_speaker = max(potential_speakers, key=lambda x: x['duration'])
                person['audio_embedding'] = best_speaker['embedding']
                person['matched_speaker'] = best_speaker['id']
            else:
                person['audio_embedding'] = None
                person['matched_speaker'] = None
                
            aligned_data.append(person)
            
        return aligned_data

    def cluster_identities(self, aligned_data, threshold=0.55):
        """Final clustering based on fused similarities for all segments."""
        if not aligned_data:
            return []
            
        n = len(aligned_data)
        
        # Calculate Visual Similarity (ReID embeddings)
        visual_embeddings = np.array([p['visual_embedding'] for p in aligned_data])
        visual_sim_matrix = cosine_similarity(visual_embeddings)
        
        # Calculate Audio Similarity (Speaker embeddings)
        # Handle cases where audio embedding is missing (person was silent)
        audio_sim_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                emb_i = aligned_data[i].get('audio_embedding')
                emb_j = aligned_data[j].get('audio_embedding')
                
                if emb_i is not None and emb_j is not None:
                    # Both segments have audio
                    sim = cosine_similarity(emb_i.reshape(1, -1), emb_j.reshape(1, -1))[0,0]
                    audio_sim_matrix[i,j] = sim
                else:
                    # One or both segments lack audio, fall back to visual only
                    # We compensate by setting audio similarity to the visual similarity
                    # effectively giving visual similarity 100% weight in this case.
                    audio_sim_matrix[i,j] = visual_sim_matrix[i,j]
        
        # Fused Similarity
        fused_matrix = self.compute_fused_similarity(visual_sim_matrix, audio_sim_matrix)
        dist_matrix = 1 - fused_matrix
        
        # Identity Clustering
        # Clip distance matrix to [0, 1] for safety
        dist_matrix = np.clip(dist_matrix, 0, 1)
        
        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric='precomputed',
            linkage='average',
            distance_threshold=threshold
        ).fit(dist_matrix)
        
        # Assign final global identity ID
        for i, label in enumerate(clustering.labels_):
            aligned_data[i]['global_identity_id'] = int(label)
            
        return aligned_data
