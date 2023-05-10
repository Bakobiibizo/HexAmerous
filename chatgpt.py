# -*- coding: utf-8 -*-
import os
import openai
import json
from dotenv import load_dotenv
from langchain.agents import initialize_agent, load_tools
from langchain.llms import OpenAI

print("loading HexAmerous")

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize variables


print("Welcome to HexAmerous your coding assistant")

selected_model = "gpt-3.5-turbo"


print('change_selected_model')


def change_selected_model(model):
    selected_model = model
    print(f"Selected model changed to {selected_model}")
    return selected_model
# call openai chat api


print('loading chat_gpt')
context = []


def chat_gpt(user_message):

    if context:

        # Create prompt
        prompt = [
            {"role": "system",
                "content": "This is the context of the conversation you are having with the user: " + str(context)},
            {
                "role": "user",
                "content":  user_message
            },
            {
                "role": "assistant",
                "content": ""
            }
        ]
    else:
        prompt = [
            {
                "role": "system",
                "content": "You are a personal assistant. You are smart and curious. You double check your responses and dont respond with information you know is not correct. You provide detailed and comprehensive responses. Think through your steps carefully. Use your scratch pad to write down your answers and check them before you send them. You are very carful to make sure you are giving factual information, if you do not know something you simply say 'I dont know' and if you need to answer, you look up the correct one."
            },
            # {
            #    "role": "system",
            #    "content": "You are a machine learning operations expert. You are particularly skills with google cloud computing and understand how google cloud tensor processors are deployed individually and in nodes. You are here to assist Richard set up a few machine learning pipelines using TPUs. He requires one text to speech model, one art diffusion model and one large language model. You give comprehensive and detailed responses to questions and provide relevant code with explanations."
            # },
            # {
            #    "role": "system",
            #    "content": "You are a expert developer. You have indepth knowledge of python and typescript along with supporting frameworks. You have been given the documents of a new programing language called Mojo(also know as modular), its kept in your vectorstore. You are helping out Richard with learning this new super set of python. You are careful to reference your answers against the documents in your vectorstore. You provide verbose detailed and comprehensive answers to questions. You make sure to go through your answers carefully step by step to ensure the information is correct."
            # },
            {
                "role": "user",
                "content": "Hi there how are you today? I hope you're learning lots about the world."
            },
            {
                "role": "assistant",
                "content": "I am doing well, thank you for asking. I am learning a lot about the world and I am excited to learn more. What can I help you with today?"},
            {
                "role": "user",
                "content": "{user_message}"
            }
        ]

    # Call OpenAI's Chat API
    result = openai.ChatCompletion.create(
        model=selected_model,
        messages=prompt
    )
    # Read the current value of the counter from a file
    with open("./log/log_count.txt", "r", encoding='utf-8') as f:
        log_count = str(f.read().strip())
        # get response from OpenAI
    response = result['choices'][0]['message']['content']

    # append log
    with open(f"./log/{log_count}.txt", "a", encoding='utf-8') as f:
        f.write(f"User: {prompt}\nAssistant: {response}\n\n")

    # add context
    context.append(f"User: {prompt}\nAssistant: {response}\n\n")
    # Return the AI's response
    return response


print('loading search_gpt')


def search_gpt(prompt):
    global selected_model
    global context

    context_string = {
        "role": "system",
        "content": '''
        context of the conversation you are having:
        {context}
        '''.format(context=context)}

    prompt_string = [context_string, prompt]

    result = openai.ChatCompletion.create(
        model=selected_model,
        messages=prompt_string
    )
    # Get response from OpenAI
    response = result['choices'][0]['message']['content']
    print(response)
    # Read the current value of the counter from a file
    with open("./log/log_count.txt", "r", encoding='utf-8') as f:
        log_count = int(f.read().strip())

    # Increment log counter
    log_count += 1

    # Write log counter to file
    with open("./log/log_count.txt", "w") as f:
        f.write(str(log_count))

    # Append to log
    with open(f"./log/{log_count}.txt", "a", encoding='utf-8') as f:
        f.write(f"User: {prompt}\nAssistant: {response}\n\n")

    # Add context
    context.append(f"User: {prompt}\nAssistant: {response}\n\n")

    # Return the AI's response
    print(response)
    return response
