#!/bin/bash
# Activate the virtual environment
echo "Activating the virtual environment"
source .venv/bin/activate
echo export PATH="$PATH:./.venv/Lib/site-packages" >> ~/.bashrc
echo "Done."

# Run your Python script HexAmerous.py
echo "Running your Python script HexAmerous.py"
python HexAmerous.py
