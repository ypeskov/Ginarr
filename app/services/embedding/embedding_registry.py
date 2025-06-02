from app.models.OpenAIEmbedding import OpenAIEmbedding

embedding_model_registry = {
    "text-embedding-3-large": OpenAIEmbedding,
    # "mistral": MistralEmbedding,
    # "gemini": GeminiEmbedding,
}
