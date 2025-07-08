#!/usr/bin/env bash

# Force correct Python version from runtime.txt
echo "Using custom build script"
python --version

cd liquidgold
pip install -r requirements.txt
