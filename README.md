# astra_chatbot_documentQA
A reusable chatbot based on Astra DB, OpenAI, Python to do Document Q/A on your own data.

Requirements: Have Python3 installed.

You will find the following files in this Git Hub repo:


# 1. prepareEnv.sh
Will install the required pip3 packages.

# 2. config.py
This file is imported by the other python programs.
Here you define the path to your secure connect bundle, passwords, and API keys.

Also you have to assign paths to config_inputdir/config_outputdir.
inputdir is the polling folder for new documents to store as embeddings in Astra DB

# 3. embedddata.py
This program will poll on config_inputdir and store found documents in Astra DB.
It supports PDF and TXT files.
Processed files will be moved to config_outputdir

# 4. chatbot.py
A simple chatbot that runs in shell.

# 5. chatbot_tinkter.py
A simple chatbot that uses Tinkter UI Framework and loads a ui to interact with the user.

# 6. chatbot_nicegui.py
A little bit more sophisticate Web UI. It can be embedded into other apps / notebooks etc.
It is a chatbot that uses NiceGui Framework and a chat messaging style to interact with the user.

# Comments
Start the python programs with 
python3 progname.py


