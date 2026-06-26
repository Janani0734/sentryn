from sentence_transformers import SentenceTransformer

# Load model once at startup
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def embed_text(text):
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()
