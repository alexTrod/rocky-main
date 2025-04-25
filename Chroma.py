from chromadb.utils import embedding_functions
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import os

class ChromaHandler:
    def __init__(self, collection_name: str = "my_collection", model_name: str = "all-MiniLM-L6-v2"):
        self.chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_DB_PERSISTENT_STORAGE'))
        self.collection_name = collection_name
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name, embedding_function=self.embedding_function)
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)


    def add_document(self, documents, ids):
        self.collection.upsert(
            documents = documents,
            # metadatas = metadatas,
            ids = ids
        )

    def query_text_document(self, text, number = 1):
        response = self.collection.query(
            query_texts=[text],
            n_results=number
        )

        return response

    def query_document_embedding(self, embedding, number = 1):
        response = self.collection.query(
            query_embeddings=embedding,
            n_results=number
        )

        return response

    
    def query_documents_by_text(self, query: str, n_results: int = 1):
        """
        Computes an embedding for the query text using "all-MiniLM-L6-v2" and searches the collection.
        
        :param query: The text query.
        :param n_results: The number of results to return.
        :return: A dictionary containing the query results.
        """
        return self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
    
    def delete_document(self, doc_id: str):
        """
        Deletes a document from the collection by its ID.
        
        :param doc_id: The identifier of the document to delete.
        """
        self.collection.delete(ids=[doc_id])


