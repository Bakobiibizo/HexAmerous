# Coding assistant

## Description

I have preloaded a prompt that instructs the model that it's a typescript and python expert. Just given its base state its very good and sending short complete blocks of code. I find writing out a schema and preplanning my code blocks helps me a lot when writing programs. I ask for the specific code block needed, add it to the program, test it, then continue. You can ask the model for assistance with planning out this process. Once you get past a file at the size of about [`HexAmerous.py`](HexAmerous.py) it loses context and cannot provide accurate code any longer. So keep sections compartmentalized and brief if possible.

## Features

- Context window containing all the messages in the chat history.
- Historical log with CRUD operations.
- Vector store for long term memory and document search.
- Embedding creation and storage.
- Mass embeddings of all PDFs, txt or md in a folder.
- Mass website data collection and storage in vector store.
- Upload a project file's py files to the vector store.
- Search for uncompressed and compressed documents in the vector store
- Send those raw documents to the model as context for a prompt.
- Internet search for context on a prompt.

## Requirements

Python 3.8 or higher

## Environment variables

Included is a file `called env-example.env`, change it to `.env` and add the corresponding API keys. This API key is stored locally and securely and the .gitignore is set to ignore that file when pushing to the repo, so you don't have to worry about your API keys being exposed. You can read more about how it works [here](https://pypi.org/project/python-dotenv/).
- OpenAi API key: https://platform.openai.com/account/api-keys
- SerpAPI key: https://serpapi.com/dashboard
- SerperAPI: https://serper.dev/api-key
- Google API key: https://console.cloud.google.com/apis/credentials
- Google CSE ID: https://cse.google.com/cse/all

## Installation

Select `install.sh` or `install.bat` and run it from your terminal or command prompt. Note that on Unix-based systems, you may need to give the script execution permissions by running `chmod +x install.sh` before executing it with `./install.sh`.

## Commands

        Commands:
        !help - Display this help message.
        !save - Save chat history.
        !load - Load chat history.
        !clear - Clear chat history.
        !exit - Exit the application.
        !docslong - Uncompressed search of documents.
        !docs - Compressed search the documents.
        !search - Search the internet for context on a prompt then ask the prompt.
        !searchmem - Search the memory for context on a prompt then ask the prompt.
        !addmem - Add a list of comma delineated website to the database.
        !embed - Upload a file to create embeddings.
        !mass_embed - Upload multiple files to create embeddings. Follow with a space then folder path.
        !addproject - Add a project to the database. Follow with a space then folder path. Note this sends your project file information to the OpenAI API.

## UI

### Send

Sends the prompt in the input box to the model and displays the response in the chat window.

### Clear

Clears the chat window. Which is also the context window of the model. You can save the chat history first with !save or load previous or new context with !load.

### L Input

Opens a chat dialog with a lot more space to work with when entering prompts. Useful for entering in large blocks of code.

### Up File

Upload a file to the vector store. This will create an embedding for the file and store it in the database. You can then search for individual docs with the !docs or !docslong commands. Use those docs for context on a prompt with !searchmem.

### Model Dropdown

Select the model you'd like the query. The default is gpt-3.5-turbo. Note you need to have access to the GPT-4 Beta to use that model. I kept the model selection fairly limited to avoid confusion. You can change the models in the code if you'd like to add more but note for older text complete model's you'll have to adjust the request format.

## Updates

- April 24th: Initial commit, included the basic functionality of the app.
- April 27th: Added vector store, commands and refactored to use [PyQt](https://riverbankcomputing.com/software/pyqt/intro) for the UI. Added Hotkey functionality with pyperclip.
- April 28th: Added memsearch, addproject, addmem. Removed Hotkey. Few bug corrections.
- April 29th: Refactored code base to be more readable, added documentation to code base, updated README, updated requirements, created install scripts and run scripts, QA'd both scripts, added error correction to stop file from constantly closing. Updated .gitignore.

I believe I have gotten this to a good enough state for my purposes, which was to demo out the langchain system. I will be moving on to other projects now. If you have any questions or would like to contribute to the project please feel free to [reach out to me](mailto:richard@bakobi.com)

## Author
Bakobiibizo - richard@bakobi.com
Bakobi Inc. - https://sites.google.com/bakobi.com/bakobi-creative-design/home

## License

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

