import chromadb
from chromadb.utils import embedding_functions
import os


class ChromaHandler:
    def __init__(self, collection_name: str = "my_collection"):
        """
        Initializes the ChromaHandler with a persistence directory, collection name, and the embedding modal.
        
        :param persist_directory: Directory to persist the Chroma DB.
        :param collection_name: The name of the collection.
        :param embedding_modal: The embedding modal used for the chroma handler. More info available at https://docs.trychroma.com/docs/embeddings/embedding-functions.
        """
        self.persist_directory = os.getenv('CHROMA_DB_PERSISTENT_STORAGE')
        self.collection_name = collection_name
        self.embedding_model = embedding_functions.DefaultEmbeddingFunction()
        self._setup_chroma()
    
    def _setup_chroma(self):
        """
        Internal method to create a Chroma client and initialize a collection.
        If the collection already exists, it retrieves it; otherwise, it creates a new one.
        """
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(name=self.collection_name)
    
    def add_document(self, doc_id: str, document: str, embedding: list):
        """
        Adds a document to the collection along with its provided embedding.
        
        :param doc_id: A unique identifier for the document.
        :param document: The text content of the document.
        :param embedding: The embedding vector associated with the document.
        """
        self.collection.add(
            ids=[doc_id],
            documents=[document],
            embeddings=[embedding]
        )
    
    def add_document_with_embedding(self, doc_id: str, document: str):
        """
        Computes an embedding for the given document using the "all-MiniLM-L6-v2" model,
        and then adds the document along with its embedding to the collection.
        
        :param doc_id: A unique identifier for the document.
        :param document: The text content of the document.
        """
        # Compute the embedding for the document text
        embedding = self.embedding_model.encode(document).tolist()
        self.add_document(doc_id, document, embedding)
    
    def query_documents(self, query: str, n_results: int = 5):
        """
        Queries the collection for documents similar to the query embedding.
        
        :param query_embedding: The embedding vector for the query.
        :param n_results: The number of results to return.
        :return: A dictionary containing the query results.
        """

        query_embedding = self.embedding_model.encode(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    
    def query_documents_by_text(self, query: str, n_results: int = 5):
        """
        Computes an embedding for the query text using "all-MiniLM-L6-v2" and searches the collection.
        
        :param query: The text query.
        :param n_results: The number of results to return.
        :return: A dictionary containing the query results.
        """
        query_embedding = self.embedding_model.encode(query).tolist()
        return self.query_documents(query_embedding, n_results)
    
    def delete_document(self, doc_id: str):
        """
        Deletes a document from the collection by its ID.
        
        :param doc_id: The identifier of the document to delete.
        """
        self.collection.delete(ids=[doc_id])


chroma_handler = ChromaHandler('internal_spy')
print("Completed")
