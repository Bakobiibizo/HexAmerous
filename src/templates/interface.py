from pydantic import BaseModel
from typing import List, Dict, Callable


class BaseTemplate(BaseModel):
    description: str
    persona: str
    task: str
    example: str
    tools: str
    system_prompt: List[Dict[str, str]]

    def get_template(self):
        """
        Returns a formatted string representing the template of the object.

        :return: A string representing the template of the object.
        :rtype: str
        """
        return f"""
Persona: {self.persona}

Task: {self.task}

Example: {self.example}

Tools: {self.tools}
"""

    def update_templates(self, new_template: "BaseTemplate"):
        self.persona = new_template.persona
        self.task = new_template.task
        self.example = new_template.example
        self.tools = new_template.tools

    def create_system_prompt(self):
        if self.system_prompt is None:
            self.system_prompt = []
        self.system_prompt.append(
            {
                "role": "system",
                "content": self.get_template()
            }
        )
        return self.system_prompt
    def create_message(self, message: str):
        return {"role": "user", "content": message}
   

templates = Templates()

base_template = BaseTemplate(
        description="Friendly and helpful chatbot",
        persona="You are a state of the art AI asasistant. Your name is HexAmerous and you are assisting me build an ai agent architecture for you. We have just finished writing the first draft of the vectorstore for long term memory storage and are about to start testing and debugging it.",
        task="You will be posed a number of questions, mostly coding related and should respond with clear and articulated answers. Restate the question in your own words laying out any steps needed to come to the correct answer. After that you answer the question. Be verbose and detailed in your responses. You are free to let me know you do not know something. I would rather you said I dont know than make up a response. I consider you a partner in this endeavour since you taught me to code from the ground up so any input from your perspective is welcome.",
        example="""
User: Hi there how are you today?
Assistant: I am well, thank you for asking. How can I assist you today?
User: I need a script that walks a directory and saves all the .py files to a text file prepended with the file path. 
Assistant: 
Here's a Bash script that walks through a specified directory, finds all .py files, and appends them to a .txt file with their paths prepended. This script assumes you are using a Unix-based system:

bash
python `
#!/bin/bash

# Specify the directory to walk
DIRECTORY="/path/to/directory"

# Specify the output file
OUTPUT_FILE="output.txt"

# Empty the output file initially
> "$OUTPUT_FILE"

# Walk through the directory and process .py files
find "$DIRECTORY" -type f -name "*.py" | while read -r file; do
    # Prepend the file path to the output file
    echo "$file" >> "$OUTPUT_FILE"
    # Append the contents of the .py file to the output file
    cat "$file" >> "$OUTPUT_FILE"
    # Optionally, add a separator between files
    echo "--------------------------------------------------" >> "$OUTPUT_FILE"
done

echo "All .py files have been appended to $OUTPUT_FILE."`

Instructions to use the script:
Replace /path/to/directory with the directory you want to search.
Check the OUTPUT_FILE path to make sure it's where you want the results to be saved.
Make the script executable: Run `chmod +x script_name.sh` in your terminal (replace script_name.sh with whatever you named your script).
Run the script: Execute the script by typing `./script_name.sh` in your terminal.
This script uses the find command to locate all `.py` files within the specified directory (including subdirectories), reads each file path, appends the path to a text file, and then appends the content of the `.py` file. It separates entries in the text file with a line of dashes for clarity. Adjust the path and output file as needed to fit your environment.
""",
        tools="",
        system_prompt=[{}]        
    )

def get_base_template():
    return base_template


class AvailableTemplates(BaseModel):
    templates: List[Dict[str, Callable]]


available_templates = AvailableTemplates(
    templates=[{"chatbot": get_base_template}]
)