from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
sentences = [
    "Cars are flying",
    "Automobiles are driving",
    "The cat is on the mat" ]

embeddings = model.encode(sentences)

sim_1_2 = np.dot(embeddings[0], embeddings[1])
sim_1_3 = np.dot(embeddings[0], embeddings[2])
sim_2_3 = np.dot(embeddings[1], embeddings[2])

print(f"Similarity between sentence 1 and 2: {sim_1_2:.4f}")
print(f"Similarity between sentence 1 and 3: {sim_1_3:.4f}")
print(f"Similarity between sentence 2 and 3: {sim_2_3:.4f}")