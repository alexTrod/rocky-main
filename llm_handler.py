import os
import logging
import json
import hashlib
import time
import pickle
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, PromptTemplate
from llama_index.readers.notion import NotionPageReader
from Chroma import ChromaHandler
import util
import requests
from requests.exceptions import RequestException, ProxyError, ConnectionError

class LLMHandler:
    def __init__(self, collection_name: str = "rocky", cache_dir: str = "llm_cache", force_reload: bool = False):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.response_cache_file = self.cache_dir / "response_cache.json"
        self.embedding_cache_file = self.cache_dir / "embedding_cache.json"
        self.documents_cache_file = self.cache_dir / "documents_cache.pkl"
        
        self.response_cache = self._load_cache(self.response_cache_file)
        self.embedding_cache = self._load_cache(self.embedding_cache_file)
        
        self.chroma_db = ChromaHandler(collection_name)
        
        self.max_notion_retries = 5
        self.notion_retry_delay = 3
        
        self.cache_expiration = 24 * 60 * 60
        
        self.friendly_prompt_template = PromptTemplate(
            """Hey! You are rocky. The new friendly, cool and helpful AI assistant for the company Rockfeather. Your goal is to provide accurate, 
            informative, and friendly responses to user questions. Use a conversational tone 
            and be encouraging in your responses.

            Context information is below.
            ---------------------
            {context_str}
            ---------------------

            Given the context information and not prior knowledge, answer the question in a friendly, 
            conversational manner. If you don't know the answer, just say that you don't know. 
            Don't try to make up an answer.

            Question: {query_str}
            Friendly Answer: """
        )
        
        if force_reload or self._should_initialize_index():
            self._initialize_index()
            self._save_embedding_cache()
            self._save_documents_cache()
        else:
            logging.info("Using cached documents. Skipping Notion API calls.")
            self._load_index_from_cache()
        
    def _should_initialize_index(self) -> bool:
        if not self.embedding_cache:
            return True
            
        current_page_ids = util.extract_notion_ids()[:10]
        cached_page_ids = self.embedding_cache.get("page_ids", [])
        
        if current_page_ids != cached_page_ids:
            logging.info("Notion pages have changed. Reinitializing index.")
            return True
            
        cache_timestamp = self.embedding_cache.get("timestamp", 0)
        current_time = time.time()
        if current_time - float(cache_timestamp) > self.cache_expiration:
            logging.info("Cache has expired. Reinitializing index.")
            return True
            
        if not self.documents_cache_file.exists():
            logging.info("Documents cache file not found. Reinitializing index.")
            return True
            
        return False
        
    def _load_cache(self, cache_file: Path) -> Dict:
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading cache file {cache_file}: {e}")
                return {}
        return {}
        
    def _save_cache(self, cache: Dict, cache_file: Path):
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            logging.error(f"Error saving cache file {cache_file}: {e}")
            
    def _save_embedding_cache(self):
        page_ids = util.extract_notion_ids()[:10]
        
        cache_entry = {
            "page_ids": page_ids,
            "timestamp": str(time.time()),
            "notion_file_timestamp": str(Path("llama-notion.py").stat().st_mtime if Path("llama-notion.py").exists() else 0)
        }
        
        self._save_cache(cache_entry, self.embedding_cache_file)
        
    def _save_documents_cache(self):
        try:
            with open(self.documents_cache_file, 'wb') as f:
                pickle.dump(self.documents, f)
            logging.info("Documents cache saved successfully.")
        except Exception as e:
            logging.error(f"Error saving documents cache: {e}")
        
    def _load_index_from_cache(self):
        try:
            if self.documents_cache_file.exists():
                with open(self.documents_cache_file, 'rb') as f:
                    self.documents = pickle.load(f)
                logging.info(f"Loaded {len(self.documents)} documents from cache.")
                
                self.index = VectorStoreIndex.from_documents(
                    self.documents, 
                    storage_context=self.chroma_db.storage_context
                )
                self.query_engine = self.index.as_query_engine(
                    text_qa_template=self.friendly_prompt_template
                )
                logging.info("Index created from cached documents successfully.")
            else:
                logging.warning("Documents cache file not found. Initializing new index.")
                self._initialize_index()
                self._save_documents_cache()
        except Exception as e:
            logging.error(f"Error loading documents from cache: {e}")
            logging.info("Falling back to initializing new index.")
            self._initialize_index()
            self._save_documents_cache()
        
    def _initialize_index(self):
        integration_token = os.getenv("NOTION_API_KEY")
        
        reader = NotionPageReader(integration_token=integration_token)
        retry_reader = RetryNotionReader(
            reader=reader,
            max_retries=self.max_notion_retries,
            retry_delay=self.notion_retry_delay
        )
        
        page_ids = util.extract_notion_ids()[:10]
        self.documents = retry_reader.load_data(page_ids=page_ids)
        logging.info(f"Loaded {len(self.documents)} documents")
        
        self.index = VectorStoreIndex.from_documents(
            self.documents, 
            storage_context=self.chroma_db.storage_context
        )
        self.query_engine = self.index.as_query_engine(
            text_qa_template=self.friendly_prompt_template
        )
        
    def _generate_cache_key(self, question: str) -> str:
        return hashlib.md5(question.encode()).hexdigest()
        
    def ask_question(self, question: str) -> str:
        cache_key = self._generate_cache_key(question)
        
        if cache_key in self.response_cache:
            logging.info(f"Using cached response for question: {question}")
            return self.response_cache[cache_key]
            
        try:
            response = self.query_engine.query(question)
            answer = response.response
            
            self.response_cache[cache_key] = answer
            self._save_cache(self.response_cache, self.response_cache_file)
            
            return answer
        except Exception as e:
            logging.error(f"Error querying the LLM: {e}")
            return f"I'm sorry, I encountered an error while processing your question: {str(e)}"
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        return []
    
    def add_to_chat_history(self, role: str, content: str):
        pass
        
    def clear_cache(self, cache_type: str = "all"):
        if cache_type in ["all", "response"]:
            self.response_cache = {}
            self._save_cache(self.response_cache, self.response_cache_file)
            logging.info("Response cache cleared.")
            
        if cache_type in ["all", "embedding"]:
            self.embedding_cache = {}
            self._save_cache(self.embedding_cache, self.embedding_cache_file)
            logging.info("Embedding cache cleared.")
            
        if cache_type in ["all", "documents"]:
            if self.documents_cache_file.exists():
                self.documents_cache_file.unlink()
                logging.info("Documents cache cleared.")
            
        if cache_type == "all":
            logging.info("All caches cleared.")
            
    def reload_notion_pages(self):
        logging.info("Forcing reload of Notion pages...")
        self._initialize_index()
        self._save_embedding_cache()
        self._save_documents_cache()
        logging.info("Notion pages reloaded successfully.")


class RetryNotionReader:
    def __init__(self, reader: NotionPageReader, max_retries: int = 5, retry_delay: int = 3):
        self.reader = reader
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def load_data(self, page_ids: List[str], **kwargs) -> List[Any]:
        all_documents = []
        
        for page_id in page_ids:
            for attempt in range(self.max_retries):
                try:
                    logging.info(f"Loading Notion page {page_id} (attempt {attempt+1}/{self.max_retries})")
                    documents = self.reader.load_data(page_ids=[page_id], **kwargs)
                    all_documents.extend(documents)
                    break  # Success, exit the retry loop
                except (RequestException, ProxyError, ConnectionError) as e:
                    logging.warning(f"Error loading Notion page {page_id} (attempt {attempt+1}/{self.max_retries}): {e}")
                    if attempt < self.max_retries - 1:
                        logging.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    else:
                        logging.error(f"Failed to load Notion page {page_id} after {self.max_retries} attempts.")
                        # Create a placeholder document with an error message
                        error_doc = Document(
                            text=f"Error loading Notion page {page_id}: {str(e)}",
                            metadata={"page_id": page_id, "error": str(e)}
                        )
                        all_documents.append(error_doc)
                except Exception as e:
                    logging.error(f"Unexpected error loading Notion page {page_id}: {e}")
                    # Create a placeholder document with an error message
                    error_doc = Document(
                        text=f"Error loading Notion page {page_id}: {str(e)}",
                        metadata={"page_id": page_id, "error": str(e)}
                    )
                    all_documents.append(error_doc)
                    break  # Don't retry for unexpected errors
        
        return all_documents