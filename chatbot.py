#!/usr/bin/env python3
# LOAD CONFIG - needs config.py
import config as cfg

#import needed libraries
#from langchain.document_loaders import PyPDFLoader 
#from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings 
from langchain.vectorstores import Cassandra 
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
import time
import datetime
import logging

# configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#establish Astra connection
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# set parameters for ASTRA DB
ASTRA_DB_TOKEN_BASED_USERNAME=cfg.config_astra_db_token_id
ASTRA_DB_TOKEN_BASED_PASSWORD=cfg.config_astra_db_token_password
ASTRA_DB_KEYSPACE=cfg.config_astra_db_keyspace
ASTRA_DB_TABLE_NAME=cfg.config_astra_db_vector_tablename
ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH=cfg.config_astra_db_secure_connect_bundle_path

# create a session for AstraDB
cloud_config = {
   'secure_connect_bundle': ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH
}
auth_provider = PlainTextAuthProvider(ASTRA_DB_TOKEN_BASED_USERNAME, ASTRA_DB_TOKEN_BASED_PASSWORD)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()


#set parameters for openAI
import os
os.environ['OPENAI_API_KEY'] = cfg.config_open_ai_secret







# define the llm model+embedding and vector store to be used
llm = OpenAI(temperature=0)
embedding_function = OpenAIEmbeddings()
vectordb = Cassandra(
	embedding=embedding_function,
	session=session,
	keyspace=ASTRA_DB_KEYSPACE,
	table_name=ASTRA_DB_TABLE_NAME
)

'''
# similarity search:
# matched_docs is a list with the found documents from the similarity search
matched_docs = vectordb.similarity_search(prompt)
# for each of the found documents, print the content
for i, d in enumerate(matched_docs):
    print(f"\n## Document {i}\n")
    print(d.page_content)
'''

# define the retrieval chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0.8), vectordb.as_retriever(), memory=memory)


# run it as an shell based chat bot
while True:
	# wait for user input
	user_input = input("You: ")
	result = qa({"question": user_input}) ##result contains history, question and answer
	print("Answer:")
	print(result["answer"])


