from app.services.search.pg_embedding_search import search_embeddings as pg_search_embeddings
# from app.services.search.qdrant_embedding_search import search_embeddings as qdrant_search_embeddings

embedding_backend_registry = {
    "text-embedding-3-large": pg_search_embeddings,
    # "qdrant-mistral": qdrant_search_embeddings,
}


async def search_embeddings(*args, embedding_model_name: str = "text-embedding-3-large", **kwargs):
    backend = embedding_backend_registry.get(embedding_model_name)
    if not backend:
        raise ValueError(f"No backend registered for model '{embedding_model_name}'")
    return await backend(*args, embedding_model_name=embedding_model_name, **kwargs)
