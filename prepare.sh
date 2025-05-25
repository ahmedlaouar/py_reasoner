#!/bin/bash

# Set working directory to the directory containing this script
WORKDIR=$(dirname "$(realpath "$0")")
cd "$WORKDIR"

# Create and activate a virtual environment (recommended)
python3 -m venv myenv
source myenv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r "$WORKDIR/requirements.txt"