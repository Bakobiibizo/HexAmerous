import os
import glob
from embeddings import create_embedding


def run_embed_project(file_path):
    # Get all .py files in the project folder
    project_folder = file_path
    output_folder = 'docs/index/project'
    project_files = glob.glob(os.path.join(project_folder, '*.py'))

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    print("Converting files to Markdown")

    count = 0
    # Convert each .py file to a Markdown
    for python_file in project_files: # replace python_files with project_files
        count += 1
        # Read the file content
        with open(python_file, 'r') as f:
            file_content = f.read()

        # Create a Markdown version of the code with syntax highlighting
        code_md = f"```python\n{file_content}\n```\n"

        # Set output file path
        output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(python_file))[0] + '.md')

        # Write the Markdown file
        with open(output_file, 'w') as f:
            f.write(code_md)

        print("File saved")
        print("Embedding created")
        create_embedding(output_file)

    if count == len(project_files):
        print("All files converted to Markdown. Generating embeddings")

        return result
    else:
        print("Error converting files to Markdown")
        return Exception("Error converting files to Markdown")