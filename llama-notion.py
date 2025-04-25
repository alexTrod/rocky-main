from llama_index.core import SummaryIndex
from llama_index.readers.notion import NotionPageReader
from llama_index.core import Settings, StorageContext, VectorStoreIndex

import os
import logging
import sys

from Chroma import ChromaHandler
from dotenv import load_dotenv

print('Starting script')
#config
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
load_dotenv()
integration_token = os.getenv("NOTION_API_KEY", "secret_Xh3OQ4ASf9ZZEXldj0Hxgw8RHXC1MJOwVWz80fO6Xfl")

print('Intialize the chroma db client')
chroma_db = ChromaHandler('rocky')


#list all pages
print('list all pages') # NOT WORKING
reader = NotionPageReader(integration_token=integration_token)
databases = reader.list_databases()


# getting page ids content
print('getting content')
page_ids = ["8362fdc042d14b939c8bd56c7b7aae12"] # P & C
documents = NotionPageReader(integration_token=integration_token).load_data(
    page_ids=page_ids
)

print('create index')
index = VectorStoreIndex(documents, storage_context=chroma_db.storage_context)
# index = VectorStoreIndex.from_documents(
#     documents,
#     chunk_size=1024,  
#     chunk_overlap=20,
#     show_progress=True,
# )

 
# debugging
query_engine = index.as_query_engine()
response = query_engine.query("What is up with the cost ? ")
print(response)
