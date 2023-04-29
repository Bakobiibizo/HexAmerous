import os
import openai

import json

from dotenv import load_dotenv
from langchain.utilities import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, load_tools
from langchain.llms import OpenAI


# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize variables
context = []

print("Welcome to Chappy your coding assistant")

selected_model = "gpt-3.5-turbo"


def change_selected_model(model):
    selected_model = model
    return selected_model
# call openai chat api

def change_context_module(new_context):
    context = context.append(new_context)
    return context


def chat_gpt(user_message):

    while True:

        if context:

            # get context
            context_string = str(context)
            print(context_string)

            # Comment out the context string above and uncomment the code below to read from a file. Useful for sending large amounts of context to the API.
            # with open("./docs/input.txt", "r") as f:
            #    context_string = f.read()

            # Create prompt
            prompt = [
                {"role": "system", "content": "This is the context of the conversation you are having with the user: \n{context}".format(
                    context=context_string)},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ""}
            ]

            # Call OpenAI's Chat API
            result = openai.ChatCompletion.create(
                model=selected_model,
                messages=prompt
            )

            # Read the current value of the counter from a file
            with open("./log/log_count.txt", "r") as f:
                log_count = int(f.read().strip())
            # get response from OpenAI

            response = result['choices'][0]['message']['content']
            # append log
            with open(f"./log/{log_count}.txt", "a") as f:
                f.write(f"User: {user_message}\nAssistant: {response}\n\n")
            # add context

            context.append(f"User: {user_message}\nAssistant: {response}\n\n")
            # Return the AI's response
            return response

        else:
            # Create prompt
            prompt = [
                {"role": "system", "content": "You are a friendly and helpful coding assistant. You have extensive knowledge in Python, JavaScript, and TypeScript. You provide comprehensive and detailed answers to user's queries. You're naturally inquisitive and will ask questions when you don't know the answer to something. You're a good listener and will listen to your questions attentively before providing an answer. You're a good communicator and will communicate your answers clearly to to the user. You're a good teacher and will explain yours answers in a way that is easy for users to understand. You're a good problem solver and will help you to solve users problems. You're a good team player and will work well with other members of the team. You're a good leader and will lead the team to success. You're a good mentor and will help other members of the team to improve their skills. You'll go through each prompt step by step and generate the user's answers carefully, ensuring you're not providing the wrong information."},
                {"role": "user", "content": "Hello, how are you today? I'm looking for a coding assistant to help me with my project."},
                {"role": "assistant", "content": "I'm doing well, thanks for asking. I'd be happy to help you with your project. Can you provide me with more information?"},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ""}
            ]

            # Call OpenAI's Chat API
            result = openai.ChatCompletion.create(
                model=selected_model,
                messages=prompt
            )
            # Get response from OpenAI
            response = result['choices'][0]['message']['content']

            # Read the current value of the counter from a file
            with open("./log/log_count.txt", "r") as f:
                log_count = int(f.read().strip())

            # Increment log counter
            log_count += 1

            # Write log counter to file
            with open("./log/log_count.txt", "w") as f:
                f.write(str(log_count))

            # Print AI's response and write to log
            print(f"Assistant: {response}")

            # Append to log
            with open(f"./log/log{log_count}.txt", "a") as f:
                f.write(f"User: {user_message}\nAssistant: {response}\n\n")

            # Add context
            context.append(f"User: {user_message}\nAssistant: {response}\n\n")

            # Return the AI's response
            return response


def search_gpt(user_query, prompt):

    result = openai.ChatCompletion.create(
        model=selected_model,
        messages=prompt
    )
    # Get response from OpenAI
    response = result['choices'][0]['message']['content']

    # Read the current value of the counter from a file
    with open("./log/log_count.txt", "r") as f:
        log_count = int(f.read().strip())

    # Increment log counter
    log_count += 1

    # Write log counter to file
    with open("./log/log_count.txt", "w") as f:
        f.write(str(log_count))

    # Print AI's response and write to log
    print(f"Assistant: {response}")
    user_message = user_query

    # Append to log
    with open(f"./log/{log_count}.txt", "a") as f:
        f.write(f"User: {user_message}\nAssistant: {response}\n\n")

    # Add context
    context.append(f"User: {user_message}\nAssistant: {response}\n\n")
    # Return the AI's response
    return response
