#!/bin/bash

# Create a new virtual environment in the .venv folder
echo "Creating a new Python virtual environment in the .venv folder."
python -m venv .venv
echo "Done."

# Activate the virtual environment
echo "Activating the virtual environment"
source .venv/bin/activate
echo "Done."

# Upgrade pip
echo "Upgrading pip"
python -m pip install pip --upgrade
echo "Done."

# Install the required packages from requirements.txt
echo "Installing required packages from requirements.txt"
while read requirement; do
    pip install -r requirements.txt
done
echo "Done."

# Install playwright
echo "installing playwright"
playwright install
echo "Done."

# Run your Python script HexAmerous.py
echo "Running your Python script HexAmerous.py"
python HexAmerous.py
