#!/bin/bash
set -e
python3 -m venv --upgrade-deps .venv
. .venv/bin/activate
pip install poetry
poetry install 
