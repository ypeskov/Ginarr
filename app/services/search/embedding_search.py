from app.services.search.pg_embedding_search import search_embeddings as pg_search_embeddings

# from app.services.search.qdrant_embedding_search import search_embeddings as qdrant_search_embeddings
from app.services.embedding.registry.models import AvailableEmbeddingModels
from app.services.embedding.registry.stores import AvailableEmbeddingStores
from app.models.MemoryChunk import MemoryChunk

_available_embedding_stores_search_functions = {
    AvailableEmbeddingStores.POSTGRES_EMBEDDING_STORE: pg_search_embeddings,
    # AvailableEmbeddingStores.QDRANT_EMBEDDING_STORE: qdrant_search_embeddings,
}


async def search_embeddings(
    *args,
    embedding_model_name: AvailableEmbeddingModels = AvailableEmbeddingModels.TEXT_EMBEDDING_3_LARGE,
    embedding_store: AvailableEmbeddingStores = AvailableEmbeddingStores.POSTGRES_EMBEDDING_STORE,
    **kwargs,
) -> list[MemoryChunk]:
    search_function = _available_embedding_stores_search_functions.get(embedding_store)
    if not search_function:
        raise ValueError(f"No search function registered for embedding store: {embedding_store}")

    return await search_function(*args, embedding_model_name=embedding_model_name, **kwargs)
