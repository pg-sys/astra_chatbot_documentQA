#!/usr/bin/env python3

# for astra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# for llm and langchain
from typing import List, Tuple
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Cassandra 
from langchain.chains import ConversationChain
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

# for logging
import time
import datetime
import logging

# for UI
# have a look at https://nicegui.io/#about
from nicegui import Client, ui
import asyncio

# configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# LOAD CONFIG - needs config.py
import config as cfg

# set parameters for ASTRA DB
ASTRA_DB_TOKEN_BASED_USERNAME=cfg.config_astra_db_token_id
ASTRA_DB_TOKEN_BASED_PASSWORD=cfg.config_astra_db_token_password
ASTRA_DB_KEYSPACE=cfg.config_astra_db_keyspace
ASTRA_DB_TABLE_NAME=cfg.config_astra_db_vector_tablename
ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH=cfg.config_astra_db_secure_connect_bundle_path


#establish Astra connection
cloud_config = {
   'secure_connect_bundle': ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH
}
auth_provider = PlainTextAuthProvider(ASTRA_DB_TOKEN_BASED_USERNAME, ASTRA_DB_TOKEN_BASED_PASSWORD)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()



# This sets your OpenAI API key, change in config file
OPENAI_API_KEY = cfg.config_open_ai_secret  
#set parameters for openAI
import os
os.environ['OPENAI_API_KEY'] = cfg.config_open_ai_secret


#llm = ConversationChain(llm=ChatOpenAI(model_name='gpt-3.5-turbo', openai_api_key=OPENAI_API_KEY))
llm = OpenAI(temperature=0)
embedding_function = OpenAIEmbeddings()
vectordb = Cassandra(
	embedding=embedding_function,
	session=session,
	keyspace=ASTRA_DB_KEYSPACE,
	table_name=ASTRA_DB_TABLE_NAME
)

# define the retrieval chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0.8), vectordb.as_retriever(), memory=memory)

# UI part
messages: List[Tuple[str, str, str]] = []
thinking: bool = False

@ui.refreshable
async def chat_messages() -> None:
    for name, text in messages:
        ui.chat_message(text=text, name=name, sent=name == 'You')
    if thinking:
        ui.spinner(size='3rem').classes('self-center')
    await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', respond=False)


@ui.page('/')
async def main(client: Client):
    async def send() -> None:
        global thinking
        thinking = True
        chat_messages.refresh()
        message = text.value
        messages.append(('You', text.value))
        text.value = ''
        
        response = qa({"question": message})
        messages.append(('Bot', response['answer']))
        thinking = False
        
    anchor_style = r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}'
    ui.add_head_html(f'<style>{anchor_style}</style>')
    await client.connected()

    with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
        await chat_messages()

    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message' if OPENAI_API_KEY != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('Peter's DataStax Bot - powered by [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')

ui.run(title='Chat with GPT-3 (example)')
